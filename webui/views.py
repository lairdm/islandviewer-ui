from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, NameCache, Genes, Replicon, Genomeproject, GIAnalysisTask, Distance, STATUS, STATUS_CHOICES, VIRULENCE_FACTORS, MODULES
from django.core.urlresolvers import reverse
from islandplot import plot
from giparser import fetcher
from uploadparser import uploader
from uploadparser.submitter import send_picker, send_clone
from metasched import pipeline, graph
from .forms import UploadGenomeForm
from .utils.formatter import *
import json
import re
import os
import pprint
from collections import OrderedDict

def index(request):
    return render(request, 'index.html')
#    return HttpResponse("Hello, world. You're at the poll index.")

def showgenomes(request):
    context = {}
    
    params = [STATUS['COMPLETE'], Analysis.MICROBEDB]
    context['analysis'] = Analysis.objects.raw("SELECT Analysis.aid as aid, Analysis.ext_id as ext_id, NameCache.name as name FROM Analysis, NameCache WHERE Analysis.ext_id = NameCache.cid AND Analysis.status = %s AND Analysis.default_analysis = 1 AND Analysis.atype = %s ORDER BY NameCache.name", params)
    
    return render(request, 'selectgenome.html', context)

def showgenomesjson(request):
    context = {}
    
    params = [STATUS['COMPLETE'], Analysis.MICROBEDB]
    context['analysis'] = Analysis.objects.raw("SELECT Analysis.aid as aid, Analysis.ext_id as ext_id, NameCache.name as name FROM Analysis, NameCache WHERE Analysis.ext_id = NameCache.cid AND Analysis.status = %s AND Analysis.default_analysis = 1 AND Analysis.atype = %s ORDER BY NameCache.name", params)
    
    return render(request, "selectgenome.json", context, content_type='text/javascript')

def results(request, aid):
    # Create the context we're going to add
    # our variables for rending to
    context = {}
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['noanalysis'] = False
    except Analysis.DoesNotExist:
        context['noanalysis'] = True;

    if context['noanalysis'] != True:
        context['aid'] = aid
        context['default_analysis'] = (True if analysis.default_analysis == 1 else False)

        # Fetch the genome name and such
        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            context['genomename'] = genome.name
        elif(analysis.atype == Analysis.MICROBEDB):
#            gpv_id = Replicon.objects.using('microbedb').filter(rep_accnum=analysis.ext_id)[0].gpv_id
#            context['genomename'] = Genomeproject.objects.using('microbedb').get(pk=gpv_id).org_name
            context['genomename'] = NameCache.objects.get(cid=analysis.ext_id).name
#            context['genomename'] = 'Something from Microbedb'

        # Fetch the virulence factors
#        island_genes = Genes.objects.filter(ext_id=analysis.ext_id).order_by('start').all() 
#        vir_list = Virulence.objects.using('microbedb').filter(protein_accnum__in=
#                                                              list(island_genes.values_list('name', flat=True))).values_list('source', flat=True).distinct()
#        context['vir_types'] = {}
#        context['has_vir'] = False
#        for vir in VIRULENCE_FACTORS.keys():
#            if vir in vir_list:
#                context['vir_types'][vir] = True
#                context['has_vir'] = True
#            else:
#                context['vir_types'][vir] = False


        # Remember the methods we have available
#        context['methods'] = dict.fromkeys(GenomicIsland.objects.filter(aid_id=aid).values_list("prediction_method", flat=True).distinct(), 1)

        CHOICES = dict(STATUS_CHOICES)
        context['status'] = CHOICES[analysis.status]
    
        context['showtour'] = True
    
    return render(request, 'results.html', context)

def resultsbyaccnum(request, accnum):

    try:
        analysis = get_object_or_404(Analysis, ext_id=accnum, default_analysis=True, atype=Analysis.MICROBEDB)
        return results(request, analysis.aid)
        
    except Exception as e:
        print e
        return HttpResponse(status = 403)
        
        
def circularplotjs(request, aid):
    context = {}
    context['plotName'] = 'circular'
    if(request.GET.get('name')):
        context['plotName'] = request.GET.get('name')
    context['varName'] = ''
    if(request.GET.get('varname')):
        context['varName'] = request.GET.get('varname')
    context['container'] = '#circularchart'
    if(request.GET.get('container')):
        context['container'] = request.GET.get('container')
    if(request.GET.get('skipinit')):
        context['skip_initialize'] = True

    # Fetch the analysis
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['aid'] = aid
    except Analysis.DoesNotExist:
        pass

    # Fetch the genome length
    if(analysis.atype == Analysis.CUSTOM):
        genome = CustomGenome.objects.get(pk=analysis.ext_id)
        context['genomesize'] = genome.rep_size
        context['genomename'] = genome.name
        context['ext_id'] = analysis.ext_id
    elif(analysis.atype == Analysis.MICROBEDB):
        (context['genomesize'], gpv_id) = Replicon.objects.using('microbedb').filter(rep_accnum=analysis.ext_id).values_list("rep_size", "gpv_id")[0]
#        context['genomename'] = Genomeproject.objects.using('microbedb').get(pk=gpv_id).org_name
        context['genomename'] = NameCache.objects.get(cid=analysis.ext_id).name
        context['ext_id'] = analysis.ext_id
#        context['genomesize'] = '6000000'

    # Fill in the GIs
    context['gis'] = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
    
    # Fetch the GC plot info
    try:
        context['gc'] = GC.objects.get(pk=analysis.ext_id)
    except GC.DoesNotExist:
        pass
    
    # Fetch the virulence factors
    params = [analysis.ext_id]
    context['vir_factors'] = Genes.objects.raw("SELECT Genes.id, Genes.name, Genes.start, virulence.source, virulence.external_id FROM Genes, virulence WHERE ext_id=%s AND Genes.name = virulence.protein_accnum", params)


    island_genes = Genes.objects.filter(ext_id=analysis.ext_id).order_by('start').all() 
    context['genes'] = island_genes
 #   vir_dict = dict(Virulence.objects.using('microbedb').filter(protein_accnum__in=
 #                                                                  list(island_genes.values_list('name', flat=True))).values_list('protein_accnum', 'source'))
    
#    context['vir_factors'] = []
#    for gene in island_genes:
#        if vir_dict.has_key(gene.name):
#            context['vir_factors'].append((gene.start,vir_dict[gene.name],gene.name,))

#    pprint.pprint(context['vir_factors']) 
    
#    return render(request, "iv4/circularplot.js", context)
    return render(request, "circularplot.js", context, content_type='text/javascript')
    

def tablejson(request, aid):
    context = {}
    try:
        analysis = Analysis.objects.get(pk=aid)
    except Analysis.DoesNotExist:
        context['noanalysis'] = True;

    context['aid'] = aid
    context['cid'] = analysis.ext_id
    
    # Fill in the GIs
    context['gis'] = GenomicIsland.objects.filter(aid_id=aid).all()
    
    return render(request, "table.json", context, content_type='application/json')
    
#    return HttpResponse(js_str, content_type=('application/json'))

def uploadform(request):
    context = {}
    
    if request.method == 'GET':
        form = UploadGenomeForm()
    elif request.method == 'POST':
        form = UploadGenomeForm(request.POST, request.FILES)
        if form.is_valid():
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            uploadparser = uploader.GenomeParser()
            try:
                ret = uploadparser.submitUpload(request.FILES['genome_file'], form.cleaned_data['format_type'], form.cleaned_data['genome_name'], form.cleaned_data['email_addr'], ip)
            except (ValueError, Exception) as e:
                context['error'] = "Unknown error"
                if settings.DEBUG:
                    print "Unknown error {0}".format(e)
                    for arg in e.args:
                        context['error'] += "<pre>" + "{0}".format(arg) + "</pre>\n"
            else:
                if settings.DEBUG:
                    print "Successful upload, redirect here to analysis"
                # Will be in aid?
                if ret['code'] == 200:
                    m = re.search("\[(\d+)\]", ret['msg'])
                    if m:
                        aid = m.group(1)
                        if settings.DEBUG:
                            print "Found aid: {0}".format(aid)
                        return HttpResponseRedirect(reverse('webui.views.results', kwargs={'aid': aid}))
                    else:
                        context['error'] = "Error parsing results from the server"
                        if settings.DEBUG:
                            context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                            print "Error str: {0}".format(ret['msg'])
                else:
                    if 'user_error_msg' in ret:
                        context['error'] = ret['user_error_msg']
                    else:
                        # Something really bad happened...
                        context['error'] = "Error submitting genome, we're not even sure what went wrong"

                    if settings.DEBUG:
                        context['error'] += "<pre>Return code: " + str(ret['code']) + "</pre>\n"
                        context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                        print "Error str: {0}".format(ret['msg'])
                    
    return render_to_response(
        'upload.html',
        {'form': form},
        context_instance=RequestContext(request, context)
    )

def uploadredirect(request, upload_id):
    context = {}

    upload = get_object_or_404(UploadGenome, pk=upload_id)
    
    if upload.aid == 0:
        return render(request, 'uploadredirect.html')
    else:
        return HttpResponseRedirect(reverse('webui.views.results', kwargs={'aid': upload.aid}))
    
def runstatus(request):
    context = {}

    context['analysis'] = Analysis.objects.select_related().all()
    
    return render(request, 'status.html', context)

def runstatusjson(request):
    context = {}

    context['sEcho'] = 1
    if(request.GET.get('sEcho')):
        sEcho = request.GET.get('sEcho')
        if not sEcho.isdigit():
            return HttpResponse(status=400)

 #       print "Setting secho to: " + sEcho
        context['sEcho'] = int(sEcho)

    startAt = 0
    if(request.GET.get('iDisplayStart')):
        startAt = request.GET.get('iDisplayStart')
        try:
            int(startAt)
        except ValueError:
            return HttpResponse(status=400)

        startAt = int(startAt)

    toShow = 30
    if(request.GET.get('iDisplayLength')):
        try:
            int(request.GET.get('iDisplayLength'))
        except ValueError:
            return HttpResponse(status=400)

        iDisplayLength = int(request.GET.get('iDisplayLength'))
        if iDisplayLength > 0:
            toShow = iDisplayLength

        toShow = int(toShow)

    endAt = startAt + toShow

    analysis = Analysis.objects.select_related().order_by('-aid').all()

    context['records'] = len(analysis)

    #    context['ranks'] = ranks[startAt:endAt]
    context['analysis'] = analysis[startAt:endAt]
    
    return render(request, 'status.json', context)

def runstatusdetailsjson(request, aid):
    context = {}
    
    analysis = Analysis.objects.select_related().get(pk=aid)
    CHOICES = dict(STATUS_CHOICES)

    context['aid'] = analysis.aid
    
    context['tasks'] = {}
    for method in analysis.tasks.all():
        context['tasks'][method.prediction_method] = CHOICES[method.status]
    
    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

def restartmodule(request, aid):
    context = {}
    
    if(request.GET.get('module') and request.GET.get('module') in MODULES):
        module = request.GET.get('module')
    else:
        return HttpResponse(status=400)

    clone_kwargs = { 'action': 'rerun', 'args': { 'modules': { module: { 'args': {  } } } } }

    clone_ret = send_clone(aid, **clone_kwargs)

    if 'code' in clone_ret and clone_ret['code'] == 200:
        if settings.DEBUG:
            print "Job submitted, new aid: " + clone_ret['data']
        
        context['status'] = 'success'
        context['aid'] = clone_ret['data']                

    else:
        context['status'] = 'failed'
        context['msg'] = clone_ret['msg']

    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

def logsmodule(request, aid):
    context = {}
    
    if(request.GET.get('module') and (request.GET.get('module') in MODULES or request.GET.get('module') == 'All')):
        module = request.GET.get('module')
    else:
        return HttpResponse(status=400)
    
    # Build the path for the analysis log
    if module == 'All':
        filename = os.path.join(settings.ANALYSIS_PATH, aid, 'analysis.log')
    else:
        filename = os.path.join(settings.ANALYSIS_PATH, aid, module, 'analysis.log')
    
    if settings.DEBUG:
        print filename
        context['filename'] = filename
    if not os.path.isfile(filename):
        return HttpResponse(status=400)

    if(request.GET.get('show')):            
        fsock = open(filename,"r")
    
        response = StreamingHttpResponse(fsock, mimetype='text/plain')
        
        return response
        
    context['status'] = 'success'
    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")
    
def graphanalysis(request, aid):
    context = {}
    context['aid'] = aid
    
    return render(request, 'graphanalysis.html', context)

def graphanalysisjs(request, aid):
    context = {}
    grapher = graph.Grapher()

    # Fetch the pipeline's structure
    pipeline_reader = pipeline.Parser()
    pipeline_data = pipeline_reader.read('islandviewer')

    context['json_str'] = grapher.makeGraph(aid, pipeline_data);
    
    return render(request, 'graphanalysis.js', context, content_type='text/javascript')

def fetchislands(request):
    context = {}
    if request.GET.get('aid'):        
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        context['aid'] = aid
    elif request.GET.get('gi'):
        gi = request.GET.get('gi')
        if not gi.isdigit():
            return HttpResponse(status=400)
#        aidrec = GenomicIsland.objects.get(pk=gi)
        girec = get_object_or_404(GenomicIsland, pk=gi)
        aid = girec.aid_id
        context['gi'] = str(gi)
        context['aid'] = aid
    else:
        return HttpResponse(status=400)
    
    p = fetcher.GenbankParser(aid)
    recs = p.fetchRecords()
    
    islands = {}
    dna = {}
    if 'gi' in context:
        islands.update(recs[long(gi)])
    else:
        print type(recs)
        for islandid in recs:
            islands.update(recs[islandid])
            
    context['islands'] = sorted(islands.iteritems(), key= lambda (k,v): int(v['start']))
    context['fastaseq'] = dna

    return render(request, "islands_by_gi.html", context)

def genesjson(request, gi_id):
    context = {}
    
    girec = get_object_or_404(GenomicIsland, pk=gi_id)
    context['gi'] = gi_id
    context['startbp'] = girec.start
    context['endbp'] = girec.end
    analysis = girec.aid
    context['aid'] = analysis.aid
    context['method'] = girec.prediction_method
    
#    context['genes'] = Genes.objects.filter(pk__in = IslandGenes.objects.filter(gi=gi_id).values_list('gene', flat=True)).order_by('start').all()
    params = [gi_id]
    context['genes'] = Genes.objects.raw("select Genes.* FROM Genes, IslandGenes WHERE IslandGenes.gi = %s AND Genes.id = IslandGenes.gene_id ORDER BY Genes.start", params)

    return render(request, "genes.json", context, content_type='application/json')

def genesbybpjson(request):
    context = {}
    
    if not request.method == 'GET':
        return HttpResponse(status = 403)
    
    if request.GET.get('ext_id'):
        ext_id = request.GET.get('ext_id')
    else:
        return HttpResponse(status = 403)

    if request.GET.get('aid'):
        aid = request.GET.get('aid')
    else:
        return HttpResponse(status = 403)
    
    if request.GET.get('start') and request.GET.get('start').isdigit():
        start = request.GET.get('start')
    else:
        return HttpResponse(status = 403)

    if request.GET.get('end') and request.GET.get('end').isdigit():
        end = request.GET.get('end')
    else:
        return HttpResponse(status = 403)
    
    params = [aid, ext_id, start, end]
    context['genes'] = Genes.objects.raw("SELECT DISTINCT g.id, g.start, g.end, g.name, g.gene, g.product, g.locus, GROUP_CONCAT( ig.gi ) AS gi , GROUP_CONCAT( DISTINCT gi.prediction_method ) AS method, GROUP_CONCAT( DISTINCT v.source ) AS virulence FROM Genes AS g LEFT JOIN IslandGenes AS ig ON g.id = ig.gene_id LEFT JOIN GenomicIsland AS gi ON ig.gi = gi.gi AND gi.aid_id = %s LEFT JOIN virulence AS v ON g.name = v.protein_accnum WHERE ext_id = %s AND g.start >=%s AND g.end <=%s GROUP BY g.id", params)

    return render(request, "genesbybp.json", context, content_type='application/json')

def islandpick_select_genomes(request, aid):
    context = {}
    
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['aid'] = analysis.aid

        # Fetch the genome name and such
        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            context['genomename'] = genome.name
        elif(analysis.atype == Analysis.MICROBEDB):
            context['genomename'] = NameCache.objects.get(cid=analysis.ext_id).name

    except:
        pass

    return render(request, "islandpick_select_genomes.html", context)


@csrf_exempt
def islandpick_genomes(request, aid):
    context = {}
    
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['accnum'] = analysis.ext_id
        context['default_analysis'] = (True if analysis.default_analysis == 1 else False)
    except Analysis.DoesNotExist:
        if settings.DEBUG:
            print "Can't fetch analysis"
        return HttpResponse(status = 403)
        
    kwargs = {}

    selected = {}
    try:
        iptask = GIAnalysisTask.objects.get(aid=aid, prediction_method='Islandpick')
        
        parameters = json.loads(iptask.parameters)
        context['parameters'] = parameters

        if 'min_cutoff' in parameters:
            kwargs.update({'min_cutoff': float(parameters['min_cutoff'])})

        if 'max_distance' in parameters:
            kwargs.update({'max_cutoff': float(parameters['max_cutoff'])})

    except Exception as e:
        if settings.DEBUG:
            print e
        return HttpResponse(status = 403)

    try:
        if request.GET.get('min_cutoff'):
            kwargs.update({'min_cutoff': float(request.GET.get('min_cutoff'))})
            
        if request.GET.get('max_cutoff'):
            kwargs.update({'max_cutoff': float(request.GET.get('max_cutoff'))})

        if request.GET.get('max_dist_single_cutoff'):
            kwargs.update({'max_dist_single_cutoff': float(request.GET.get('max_dist_single_cutoff'))})

        if request.GET.get('min_compare_cutoff'):
            kwargs.update({'min_compare_cutoff': float(request.GET.get('min_compare_cutoff'))})

        if request.GET.get('max_compare_cutoff'):
            kwargs.update({'max_compare_cutoff': float(request.GET.get('max_compare_cutoff'))})
        
    except ValueError as e:
        if settings.DEBUG:
            print e
        return HttpResponse(status = 403)

    if 'comparison_genomes' in parameters:
        selected = {x: True for x in parameters['comparison_genomes'].split()}
        kwargs.update({'extra_genomes': selected})
        
    genomes = Distance.find_genomes(analysis.ext_id, **kwargs)

    if request.method == 'GET':

        try:

            # Now get all the names
            ext_ids = [g for g,d in genomes]
            cache_names = NameCache.objects.filter(cid__in=ext_ids).values('cid', 'name')
            cache_names = {x['cid']:x['name'] for x in cache_names}
            cids = [int(x) for x in ext_ids if x.isdigit()]
            custom_names = CustomGenome.objects.filter(cid__in=cids).values('cid', 'name')
            custom_names = {x['cid']:x['name'] for x in custom_names}

#            cluster_list = ext_ids
#            cluster_list.insert(0, analysis.ext_id)
#            print len(cluster_list)
#            context['tree'] = Distance.distance_matrix(cluster_list)
                                    
        except Exception as e:
            print str(e)
            pass

        genome_list = OrderedDict()

        # We need the genomes to display in order
        for g,dist in genomes:
            genome_list.update({g: {'dist': "%0.3f" % dist,
                                    'used': (True if g in selected else False),
                                    'picked' : (True if g in selected and 'reselect' not in request.GET else False),
                                    'name': (cache_names[g] if g in cache_names else custom_names[g] if g in custom_names else "Unknown" )
                                    }
                                })

        if request.GET.get('reselect'):
            try:
                # If we're re-selecting the candidates, make the call to the backend
                picker = send_picker(analysis.ext_id, **kwargs)
                
                if 'code' in picker and picker['code'] == 200:
                    for acc in picker['data']:
                        if "picked" in picker['data'][acc] and acc in genome_list:
                            genome_list[acc]["picked"] = 'true'
                    
                context['picker'] = picker
            except Exception as e:
                if settings.DEBUG:
                    print "Exception: " + str(e)
                context['picker'] = {'code': 500}


        context['genomes'] = genome_list
        context['status'] = "OK"            
        
        data = json.dumps(context, indent=4, sort_keys=False)
    
        return HttpResponse(data, content_type="application/json")

    else:
        try:
        
            #print request.GET.get('min_gi_size')
            accnums = []
            min_gi_size = filter(lambda x: x.isdigit(), request.GET.get('min_gi_size') )
            for name in request.POST:
                #print name, request.POST[name]
                if name not in (x[0] for  x in genomes):
                    if settings.DEBUG:
                        print "Error, " + name + " not in genomes set"
                    raise Exception("Error, requested genome isn't in the allowed set")
                accnums.append(name)

            clone_kwargs = { 'args': { 'modules': { 'Islandpick': { 'args': { 'comparison_genomes':  ' '.join(accnums), 'MIN_GI_SIZE': min_gi_size } } } } }

            # Check if we've run these settings before, if so, just redirect to that
            match_aid = Analysis.find_islandpick(analysis.ext_id, accnums, min_gi_size)
            if match_aid:
                context['status'] = 'success'
                context['aid'] = match_aid 
            
            else:
                clone_ret = send_clone(aid, **clone_kwargs)
            
                if 'code' in clone_ret and clone_ret['code'] == 200:
                    if settings.DEBUG:
                        print "Job submitted, new aid: " + clone_ret['data']
                    
                    context['status'] = 'success'
                    context['aid'] = clone_ret['data']                
        
        except Exception as e:
            if settings.DEBUG:
                print "Error in post"
                print str(e)
            return HttpResponse(status = 403)

        data = json.dumps(context, indent=4, sort_keys=False)
    
        return HttpResponse(data, content_type="application/json")
    
def downloadCoordinates(request):
    
    if request.GET.get('aid'):
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = Analysis.objects.get(pk=aid)


        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            filename = genome.name
            filename = ''.join(e for e in filename if e.isalnum())
        elif(analysis.atype == Analysis.MICROBEDB):
            filename = analysis.ext_id
    else:
        return HttpResponse(status=400)
        
    if request.GET.get('format'):
        format = request.GET.get('format')
        if format not in downloadformats:
            return HttpResponse(status=400)
        extension = downloadextensions[format]
    else:
        return HttpResponse(status=400)

    if request.GET.getlist('methods'):
        pprint.pprint(request.GET.getlist('methods'))
        methods = request.GET.getlist('methods')
        pprint.pprint(methods)
    else:
        methods = ['integrated']

    params = [aid]   
    islandset = Genes.objects.raw("SELECT G.id, GI.start AS island_start, GI.end AS island_end, GI.prediction_method, G.ext_id, G.start AS gene_start, G.end AS gene_end, G.strand, G.name, G.gene, G.product, G.locus FROM Genes AS G, IslandGenes AS IG, GenomicIsland AS GI WHERE GI.aid_id = %s AND GI.gi = IG.gi AND G.id = IG.gene_id ORDER BY GI.start, GI.prediction_method", params)
    pprint.pprint(islandset)
    
    response = downloadformats[format](islandset,methods, filename + "." + extension)
    
    return response

def downloadSequences(request):
    
    if request.GET.get('aid'):
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = Analysis.objects.get(pk=aid)
        p = fetcher.GenbankParser(aid)

        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            filename = genome.name
            filename = ''.join(e for e in filename if e.isalnum())
        elif(analysis.atype == Analysis.MICROBEDB):
            filename = analysis.ext_id
    else:
        return HttpResponse(status=400)
        
    if request.GET.get('format'):
        format = request.GET.get('format')
        if format not in downloadformats:
            return HttpResponse(status=400)
        extension = downloadextensions[format]
    else:
        return HttpResponse(status=400)

    if request.GET.getlist('methods'):
        pprint.pprint(request.GET.getlist('methods'))
        methods = request.GET.getlist('methods')
        pprint.pprint(methods)
    else:
        methods = ['integrated']

    params = [aid] 
    if(format == 'genbank'):
        islandset = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
        #islandset = Genes.objects.raw("SELECT IG.id, GI.start AS island_start, GI.end AS island_end, GI.prediction_method FROM IslandGenes AS IG, GenomicIsland AS GI WHERE GI.aid_id = %s AND GI.gi = IG.gi ORDER BY GI.start, GI.prediction_method", params)
    else:
        islandset = Genes.objects.raw("SELECT G.id, GI.start AS island_start, GI.end AS island_end, GI.prediction_method, G.ext_id, G.start AS gene_start, G.end AS gene_end, G.strand, G.name, G.gene, G.product, G.locus FROM Genes AS G, IslandGenes AS IG, GenomicIsland AS GI WHERE GI.aid_id = %s AND GI.gi = IG.gi AND G.id = IG.gene_id ORDER BY GI.start, GI.prediction_method", params)
        
    response = downloadformats[format](islandset, p, methods, filename + "." + extension)

    return response

    
    
def fetchislandsfasta(request):
    context = {}
    gi = 0
    if request.GET.get('aid'):        
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        aidrec = get_object_or_404(Analysis, pk=aid)
        filename = aidrec.ext_id
    elif request.GET.get('gi'):
        gi = request.GET.get('gi')
        if not gi.isdigit():
            return HttpResponse(status=400)
#        aidrec = GenomicIsland.objects.get(pk=gi)
        girec = get_object_or_404(GenomicIsland, pk=gi)
        aid = girec.aid_id
        gi = str(gi)
        aid = aid
        filename = str(girec.start) + '_' + str(girec.end)
        rangestr = str(girec.start) + '..' + str(girec.end)
    else:
        return HttpResponse(status=400)
    
    seqtype = 'protein'
    if request.GET.get('seq'):
        seqtype = request.GET.get('seq')
        if seqtype not in ('protein', 'nuc', 'island'):
            return HttpResponse(status=400)
    
    p = fetcher.GenbankParser(aid)

    if seqtype == 'island':
        if gi:
            fasta = p.generateIslandFasta(gi, rangestr)
        else:
            return HttpResponse(status=400)
    else:
        fasta = p.generateFasta(gi=gi, seqtype=seqtype)
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = "attachment; filename=\"gi_{0}.txt\"".format(filename)
    response.write(fasta)
    return response
    
def about(request):
    
    return render(request, "about.html")

def download(request):
    
    return render(request, "download.html")
        
def resources(request):
    
    return render(request, "resources.html")

def contactus(request):
    
    return render(request, "contactus.html")

def faq(request):
    
    return render(request, "faq.html")

def acknowledgements(request):
    
    return render(request, "acknowledgements.html")

def islandpick(request):
    
    return render(request, "islandpick.html")
