from Bio import SeqIO
from webui.models import Analysis, CustomGenome, GenomicIsland, Replicon, Genomeproject
from webui.utils.formatter import methodfullnames
from django.conf import settings
import os.path
import textwrap
import pprint

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

class GenbankParser():
    def __init__(self,aid):
        '''
        We're going to try and access the analysis
        then find its genbank file     
        '''
        try:
            self.analysis = Analysis.objects.get(pk=aid)
        except Analysis.DoesNotExist:
            pass
        
        if(self.analysis.atype == Analysis.CUSTOM):
            self.fetchCustomFile(self.analysis.ext_id)
        elif(self.analysis.atype == Analysis.MICROBEDB):
            self.fetchMicrobeDBFile(self.analysis.ext_id)

        if not os.path.isfile(self.fname):
            raise Exception("File does not exist: " + self.fname)
        
        '''
        Parse the file, fetch the GIs, and stash all the 
        information we'll need to make the download files,
        this eventually could be memcached so on subsequent 
        requests the genbank file doesn't need to be reparsed 
        '''
        self.gis = GenomicIsland.objects.filter(aid_id=aid).order_by('start')
        
        gbhandle = SeqIO.parse(self.fname, "genbank")
        records = next(gbhandle)
        # Stash it for later
        self.records = records
        recs_in_islands = Vividict()
        
        for feature in records.features:
                if feature.type == 'gene':
                    gi = self.checkIslandRange(feature.location.start, feature.location.end)
                    if gi:
                        loc = str(feature.location.start) + ".." + str(feature.location.end)
                        recs_in_islands[gi][loc]['strand'] = feature.location.strand
                        recs_in_islands[gi][loc]['dna'] = records.seq[feature.location.start:feature.location.end]
                        recs_in_islands[gi][loc]['start'] =  str(feature.location.start)
                        recs_in_islands[gi][loc]['end'] =  str(feature.location.end)
                                                    
                        if not hasattr(feature, 'qualifiers'):
                            continue 
                        qualifiers = feature.qualifiers
                        if 'gene' in qualifiers:
                            recs_in_islands[gi][loc]['gene'] = qualifiers['gene'][0]
                        if 'locus_tag' in qualifiers:
                            recs_in_islands[gi][loc]['locus'] = qualifiers['locus_tag'][0]
                if feature.type == 'CDS':
                    gi = self.checkIslandRange(feature.location.start, feature.location.end)
                    if gi:
                        loc = str(feature.location.start) + ".." + str(feature.location.end)
                        recs_in_islands[gi][loc]['strand'] = feature.location.strand
                        recs_in_islands[gi][loc]['start'] =  str(feature.location.start)
                        recs_in_islands[gi][loc]['end'] =  str(feature.location.end)

                        if not hasattr(feature, 'qualifiers'):
                            continue 
                        qualifiers = feature.qualifiers
                        if 'translation' in qualifiers:
                            recs_in_islands[gi][loc]['protein'] = qualifiers['translation'][0]
                        if 'protein_id' in qualifiers:
                            recs_in_islands[gi][loc]['protein_id'] = qualifiers['protein_id'][0]
                        if 'product' in qualifiers:
                            recs_in_islands[gi][loc]['product'] = qualifiers['product'][0]
                if feature.type == 'tRNA':
                    gi = self.checkIslandRange(feature.location.start, feature.location.end)
                    if gi:
                        loc = str(feature.location.start) + ".." + str(feature.location.end)
                        recs_in_islands[gi][loc]['strand'] = feature.location.strand
                        recs_in_islands[gi][loc]['start'] =  str(feature.location.start)

                        if not hasattr(feature, 'qualifiers'):
                            continue 
                        qualifiers = feature.qualifiers
                        if 'product' in qualifiers:
                            recs_in_islands[gi][loc]['product'] = qualifiers['product'][0]
                if feature.type == 'ncRNA':
                    gi = self.checkIslandRange(feature.location.start, feature.location.end)
                    if gi:
                        loc = str(feature.location.start) + ".." + str(feature.location.end)
                        recs_in_islands[gi][loc]['strand'] = feature.location.strand
                        recs_in_islands[gi][loc]['start'] =  str(feature.location.start)

                        if not hasattr(feature, 'qualifiers'):
                            continue 
                        qualifiers = feature.qualifiers
                        if 'product' in qualifiers:
                            recs_in_islands[gi][loc]['product'] = qualifiers['product'][0]
     
        '''
        Now we need to save the nucleotide sequence for the whole islands, ugh
        '''
        self.dna = {}
        for island in self.gis:
            self.dna[island.gi] = records.seq[island.start:island.end]
            
        self.islands = recs_in_islands

    def fetchRecords(self):
        return self.islands
    
    def fetchDNA(self):
        return self.dna

    def insertFeature(self, feature, offset=0):
        self.records.features.insert(offset, feature)
        
    def writeGenbank(self, handle):
        SeqIO.write(self.records, handle, "genbank")

    def generateFasta(self, gi = 0, seqtype = 'protein', show_methods = False, methods=['integrated']):
        islands = {}
        
        if gi:
            islands.update(self.islands[long(gi)])
        else:
            for islandid in self.islands:
                islands.update(self.islands[islandid])

        sortedislands = sorted(islands.iteritems(), key= lambda (k,v): int(v['start']))

        fasta = ''
        for coord,values in sortedislands:
            header = '>'
            if(values['protein_id']):
                header += 'ref|' + str(values['protein_id']) + '|'
            if(values['locus']):
                header += 'locus|' + str(values['locus']) + '|'
            if show_methods:
#                pprint.pprint(values['method'])
                methods_found = self.generateMethods(values['start'], values['end'], methods)
                if methods_found:
                    header += 'prediction_method|' + ",".join(methods_found)
                else:
                    continue
            header += " {0} ({1})".format(values['product'], coord)
            if seqtype == 'protein' and values['protein']:
                fasta += "{0}\n{1}\n".format(header, "\n".join(textwrap.wrap(values['protein'])))
            elif seqtype == 'nuc' and values['dna']:
                dna = str(values['dna'])
                fasta += "{0}\n{1}\n".format(header, "\n".join(textwrap.wrap(dna)))
            
        return fasta
    
    def generateIslandFasta(self, gi, rangestr):
        islands = {}
        
        fasta = ">{0}\n".format(rangestr)
        dna = str(self.dna[long(gi)])
        fasta += "\n".join(textwrap.wrap(dna))
        fasta += "\n"
        
        return fasta

                    
    def checkIslandRange(self,start,end):
        
        for island in self.gis:
            if island.start <= start and end <= island.end:
                return island.gi
            
        return False        
    
    def generateMethods(self, start, end, methods = ['integrated']):
        
        if 'integrated' in methods:
            methods_found = ",".join(self.findMethods(int(start), int(end), ['sigi', 'islandpick', "dimob"]))
            return ['Predicted_by_at_least_one_method(' + methods_found + ")"]
        else:
            return self.findMethods(int(start), int(end), methods)
    
    '''
    Ok, this is a lot of looping, but this shouldn't be called very often...
    To shorten the loop we're going to make an assumption that islands
    are returned in order, so we can stop looping when we pass
    the window
    '''
    def findMethods(self, start, end, methods):
        methods_found = []
        
        for island in self.gis:
            if island.start <= start and end <= island.end and island.prediction_method.lower() in methods:
#            if island.start <= start and end <= island.end:
                methods_found.append(methodfullnames[island.prediction_method.lower()])
            if island.start > end:
                return methods_found
                
        return methods_found
        
    def fetchCustomFile(self,ext_id):
        try:
            customgenome = CustomGenome.objects.get(pk=ext_id)
        except CustomGenome.DoesNotExist:
            pass
        
        try:
            filename = customgenome.filename
            filename = filename.replace(u'{{custom_genomes}}', settings.CUSTOM_GENOMES)
        except Exception as e:
            if settings.DEBUG:
                print "Exception raised with filename {}: {}".format(filename, e)
        
        # Check we actually have a genbank type
        if ".gbk" in customgenome.formats.split():
            self.fname = filename + ".gbk"
        else:
            raise Exception("No genbank file")
        
    def fetchMicrobeDBFile(self,ext_id):
        # We'll have to go out to microbedb here and
        # get the filename
        try:
            replicon = Replicon.objects.using('microbedb').filter(rep_accnum=ext_id)[0]
        except Replicon.DoesNotExist:
            pass
        
        gpv_id = replicon.gpv_id

        self.fname = os.path.join(Genomeproject.objects.using('microbedb').get(pk=gpv_id).gpv_directory, replicon.file_name) + ".gbk"
        
    def findGenes(self,startbp,endbp):
        gbhandle = SeqIO.parse(self.fname, "genbank")
        records = next(gbhandle)
        
        recs_in_island = {}
        
        for f in records.features:
            if f.type == 'gene':
                if startbp >= f.location.start >= endbp and  startbp >= f.location.end >= endbp:
                    loc = f.location.start + "_" + f.location.end
                    recs_in_island[loc]['strand'] = f.location.strand
#                print f.location.start
            elif f.type == 'CDS':
                pass
#                print f.location.strand
#                if f.location
#                print(f.id)
#                print(len(f))
#            print record
            
#        handle.close()
         
