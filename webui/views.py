from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, Genes, Replicon, Genomeproject, STATUS, STATUS_CHOICES
from django.utils import simplejson
from django.core.urlresolvers import reverse
from islandplot import plot
from giparser import fetcher
from uploadparser import uploader
from metasched import pipeline, graph
from .forms import UploadGenomeForm
import re
import pprint

def index(request):
    return render(request, 'index.html')
#    return HttpResponse("Hello, world. You're at the poll index.")

def showgenomes(request):
    context = {}
    
    params = [STATUS['COMPLETE'], Analysis.MICROBEDB]
    context['analysis'] = Analysis.objects.raw("SELECT Analysis.aid as aid, Analysis.ext_id as ext_id, NameCache.name as name FROM Analysis, NameCache WHERE Analysis.ext_id = NameCache.cid AND Analysis.status = %s AND Analysis.default_analysis = 1 AND Analysis.atype = %s ORDER BY NameCache.name", params)
    
    return render(request, 'selectgenome.html', context)

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

        # Fetch the genome name and such
        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            context['genomename'] = genome.name
        elif(analysis.atype == Analysis.MICROBEDB):
            gpv_id = Replicon.objects.using('microbedb').filter(rep_accnum=analysis.ext_id)[0].gpv_id
            context['genomename'] = Genomeproject.objects.using('microbedb').get(pk=gpv_id).org_name
#            context['genomename'] = 'Something from Microbedb'

        # Fetch the virulence factors
        island_genes = Genes.objects.filter(ext_id=analysis.ext_id).order_by('start').all() 
        vir_dict = dict(Virulence.objects.using('microbedb').filter(protein_accnum__in=
                                                              list(island_genes.values_list('name', flat=True))).values_list('protein_accnum', 'source'))

        context['vir_types'] = {}
        for gene in island_genes:
            if vir_dict.has_key(gene.name):
                context['vir_types'][vir_dict[gene.name]] = True

        # Remember the methods we have available
        context['methods'] = dict.fromkeys(GenomicIsland.objects.filter(aid_id=aid).values_list("prediction_method", flat=True).distinct(), 1)

        CHOICES = dict(STATUS_CHOICES)
        context['status'] = CHOICES[analysis.status]
    
    return render(request, 'results.html', context)

def circularplotjs(request, aid):
    context = {}
    context['plotName'] = 'circular'
    if(request.GET.get('name')):
        context['plotName'] = request.GET.get('name')
    context['container'] = '#circularchart'
    if(request.GET.get('container')):
        context['container'] = request.GET.get('container')

    # Fetch the analysis
    try:
        analysis = Analysis.objects.get(pk=aid)
    except Analysis.DoesNotExist:
        pass

    # Fetch the genome length
    if(analysis.atype == Analysis.CUSTOM):
        genome = CustomGenome.objects.get(pk=analysis.ext_id)
        context['genomesize'] = genome.rep_size
    elif(analysis.atype == Analysis.MICROBEDB):
        context['genomesize'] = Replicon.objects.using('microbedb').filter(rep_accnum=analysis.ext_id)[0].rep_size
#        context['genomesize'] = '6000000'

    # Fill in the GIs
    context['gis'] = GenomicIsland.objects.filter(aid_id=aid).all()
    
    # Fetch the GC plot info
    try:
        context['gc'] = GC.objects.get(pk=analysis.ext_id)
    except GC.DoesNotExist:
        pass
    
    # Fetch the virulence factors
    island_genes = Genes.objects.filter(ext_id=analysis.ext_id).order_by('start').all() 
    vir_dict = dict(Virulence.objects.using('microbedb').filter(protein_accnum__in=
                                                                   list(island_genes.values_list('name', flat=True))).values_list('protein_accnum', 'source'))
    context['genes'] = island_genes
    
    context['vir_factors'] = []
    for gene in island_genes:
        if vir_dict.has_key(gene.name):
            context['vir_factors'].append((gene.start,vir_dict[gene.name],))

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

    context['analysis'] = Analysis.objects.select_related().all()
    
    return render(request, 'status.json', context)

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
