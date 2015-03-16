from __future__ import unicode_literals

from django.db import models
from django.conf import settings
import pprint
from Bio.Phylo.TreeConstruction import _DistanceMatrix, DistanceTreeConstructor
from Bio import Phylo
import StringIO
import json

STATUS = {'PENDING':1,'RUNNING':2,'ERROR':3,'COMPLETE':4}
STATUS_CHOICES = [
    (STATUS['PENDING'], 'Pending'),
    (STATUS['RUNNING'], 'Running'),
    (STATUS['ERROR'], 'Error'),
    (STATUS['COMPLETE'], 'Complete'),
]

VIRULENCE_FACTORS = {
    'VFDB': 'Virulence factors',
    'ARDB': 'Resistance genes',
    'PAG': 'Pathogen-associated genes'
}

VIRULENCE_FACTOR_CATEGORIES = {
    'VFDB': 'VFDB',
    'Victors': 'VFDB',
    'PATRIC_VF': 'VFDB',
    'ARDB': 'ARDB',
    'CARD': 'ARDB',
    'BLAST': 'BLAST',
    'RGI': 'RGI',
    'PAG': 'PAG' 
}

MODULES = ['Prepare', 'Distance', 'Sigi', 'Dimob', 'Islandpick', 'Virulence', 'Summary']

class CustomGenome(models.Model):
    cid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    cds_num = models.IntegerField(default=0)
    rep_size = models.IntegerField(default=0)
    filename = models.CharField(max_length=60)
    formats = models.CharField(max_length=50)
    contigs = models.IntegerField(default=1)
    genome_status = models.IntegerField()
    submit_date = models.DateTimeField('date submitted')

    class Meta:
        db_table = "CustomGenome"

class NameCache(models.Model):
    cid = models.CharField(max_length=15)
    name = models.CharField(max_length=60)
    cds_num = models.IntegerField(default=0)
    rep_size = models.IntegerField(default=0)

    class Meta:
        db_table = "NameCache"

class Analysis(models.Model):
    CUSTOM = 1
    MICROBEDB = 2
    ATYPE_CHOICES = (
        (CUSTOM, 'Custom'),
        (MICROBEDB, 'MicrobeDB'),
    )
    aid = models.AutoField(primary_key=True)
    atype = models.IntegerField(choices=ATYPE_CHOICES,
                                default=CUSTOM)
    ext_id = models.CharField(max_length=15)
    owner_id = models.IntegerField(default=0)
    default_analysis = models.BooleanField(default=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS['PENDING'])
    workdir = models.CharField(max_length=50)
    microbedb_ver = models.IntegerField(default=0)
    start_date = models.DateTimeField('date started')
    complete_date = models.DateTimeField('date completed')

    # Specialty function to find an analysis with the same 
    # Islandpick settings (comparison genomes, min_gi_size)
    
    @classmethod
    def find_islandpick(cls, ext_id, genomes, min_gi_size):
    
        min_gi_size = int(min_gi_size)
        if settings.DEBUG:
            print "Testing for existing islandpick using, ext_id {}, using: ".format(ext_id)
            print "Looking for min_gi_size: {} and genomes {}".format(min_gi_size, genomes)
            
        analysis = Analysis.objects.filter(ext_id = ext_id)
        
        for a in analysis:
            a_parameters_json = None
            for task in a.tasks.all():
                if task.prediction_method == 'Islandpick':
                    a_parameters_json = task.parameters
                    break
            
            # We found an Islandpick in that analysis
            if a_parameters_json:
                if settings.DEBUG:
                    print "Checking Islandpick in analysis {}".format(a.aid)
                a_parameters = json.loads(a_parameters_json)
                
                if settings.DEBUG:
                    print "Found parameters:"
                    pprint.pprint(a_parameters)
                
                # First check we have the right fields...
                if 'comparison_genomes' not in a_parameters and 'MIN_GI_SIZE' not in a_parameters:
                    if settings.DEBUG:
                        print "Either comparison_genomes or min_gi_size aren't in the db for analysis {}, skipping".format(a.aid)
                    continue

                # Next check the comparison genomes
                if sorted(a_parameters['comparison_genomes'].split(' ')) != sorted(genomes):
                    if settings.DEBUG:
                        print "comparison_genomes for analysis {} don't match, skipping".format(a.aid)
                    continue
                
                # Finally, does the min_gi_size match?
                if int(a_parameters['MIN_GI_SIZE']) != min_gi_size:
                    if settings.DEBUG:
                        print "min_gi_size for analysis {} doesn't match, skipping".format(a.aid)
                    continue
                
                # We made it this far, we must have a match, return this aid
                return a.aid
            
        # We exited the loop without returning, we must not have
        # a match, return None
        return None 

    def find_reference_genome(self):
        
        a_parameters_json = None
        for task in self.tasks.all():
            if task.prediction_method == 'Prepare':
                a_parameters_json = task.parameters
                break
            
        # We found a Prepare task, let's see if it has a ref_accnum
        if a_parameters_json:
            a_parameters = json.loads(a_parameters_json)
            
            if settings.DEBUG:
                print "Found parameters:"
                pprint.pprint(a_parameters)
            
            if 'ref_accnum' in a_parameters:
                return a_parameters['ref_accnum']
            
        return None
    
    @classmethod
    def lookup_genome(cls, accnum):
        
        try:
            float(accnum)
        except ValueError:
            # It's not a custom genome...
            genome = NameCache.objects.get(cid=accnum)
            return genome
        
        # It's a custom genome
        genome = CustomGenome.objects.get(cid=accnum)
        return genome

    @classmethod
    def last_modified(cls, request, aid):
        
        print "Looking up aid {}".format(aid)
        return Analysis.objects.get(aid=aid).complete_date

    class Meta:
        db_table = "Analysis"

class GIAnalysisTask(models.Model):
    taskid = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Analysis, related_name='tasks')
    prediction_method = models.CharField(max_length=15)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS['PENDING'])
    parameters = models.CharField(max_length=15)
    start_date = models.DateTimeField('date started')
    complete_date = models.DateTimeField('date completed')

    @classmethod
    def fetch_parameters(cls, aid, method):
            
        try:
            if settings.DEBUG:
                print "Checking method {} in analysis {}".format(method,aid)

            task = GIAnalysisTask.objects.filter(aid=aid, prediction_method=method)
            a_parameters_json = task.parameters
            
            a_parameters = json.loads(a_parameters_json)

            if settings.DEBUG:
                print "Found parameters:"
                pprint.pprint(a_parameters)

        except Exception as e:
            if settings.DEBUG:
                print e
                
            raise e
        
        return a_parameters
        
    class Meta:
        db_table = "GIAnalysisTask"

class GenomicIsland(models.Model):
    gi = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Analysis)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    prediction_method = models.CharField(max_length=15)
    details = models.CharField(max_length=20)

    @classmethod
    def sqltodict(cls, query,param):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(query,param)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        return result

    class Meta:
        db_table = "GenomicIsland"

class GC(models.Model):
    ext_id = models.CharField(primary_key=True,max_length=15)
    min = models.FloatField()
    max = models.FloatField()
    mean = models.FloatField()
    gc = models.TextField()
    
    class Meta:
        db_table = "GC"

class Genes(models.Model):
    ext_id = models.CharField(max_length=15)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    strand = models.IntegerField()
    name = models.CharField(max_length=14)
    gene = models.CharField(max_length=10)
    product = models.CharField(max_length=100)
    locus = models.CharField(max_length=10)
    
    class Meta:
        db_table = "Genes"

class IslandGenes(models.Model):
    gi = models.IntegerField()
    gene = models.ForeignKey(Genes)
    
    class Meta:
        db_table = "IslandGenes"

class Distance(models.Model):
    rep_accnum1 = models.CharField(max_length=15)
    rep_accnum2 = models.CharField(max_length=15)
    distance = models.FloatField()

    @classmethod
    def find_genomes(cls, accnum, *args, **kwargs):
        #pprint.pprint(kwargs)
        
        if 'min_cutoff' in kwargs:
            min_cutoff = kwargs['min_cutoff']
        else:
            min_cutoff = 0.1

        if 'max_cutoff' in kwargs:
            max_cutoff = kwargs['max_cutoff']
        else:
            max_cutoff = 0.42

        params = [accnum, accnum, min_cutoff, max_cutoff]
        sql = "SELECT id, rep_accnum1, rep_accnum2, distance from Distance WHERE (rep_accnum1 = %s or rep_accnum2 = %s) AND "
        sql_dist = "(distance >= %s AND distance <= %s)"

        if 'extra_genomes' in kwargs:
            rep_list = ','.join("'" + rep + "'" for rep in kwargs['extra_genomes'])
            sql += "(" + sql_dist + " OR (rep_accnum1 IN ({}) OR rep_accnum2 IN ({})))".format(rep_list, rep_list)
        else:
            sql += sql_dist
        
        #sql += ' ORDER BY distance'
        
        dists = Distance.objects.raw(sql, params)
        #dists = Distance.objects.filter(models.Q(rep_accnum1=accnum) | models.Q(rep_accnum2=accnum), distance__gte=min_cutoff, distance__lte=max_cutoff).order_by('distance')
        
        genomes = [(g.rep_accnum1, g.distance) if g.rep_accnum1 != accnum else (g.rep_accnum2, g.distance) for g in dists]

        return genomes
    
    @classmethod
    def distance_matrix(cls, cluster_list):
        print cluster_list
        dists = Distance.objects.filter(rep_accnum1__in=cluster_list, rep_accnum2__in=cluster_list)
        
        distance_pairs = {g.rep_accnum1 + '_' + g.rep_accnum2: g.distance for g in dists.all()}
    
        matrix = []
        for i in range(0,len(cluster_list)):
            matrix_iteration = []
            for j in range(0,i+1):
                if i == j:
                    matrix_iteration.append(0)
                elif cluster_list[i] + '_' + cluster_list[j] in distance_pairs:
                    matrix_iteration.append(distance_pairs[cluster_list[i] + '_' + cluster_list[j]])
                elif cluster_list[j] + '_' + cluster_list[i] in distance_pairs:
                    matrix_iteration.append(distance_pairs[cluster_list[j] + '_' + cluster_list[i]])
                else:
                    raise("Error, can't find pair!")
            matrix.append(matrix_iteration)
            #print matrix_iteration

        cluster_list = [s.encode('ascii', 'ignore') for s in cluster_list]
        matrix_obj = _DistanceMatrix(names=cluster_list, matrix=matrix)
        constructor = DistanceTreeConstructor()
        tree = constructor.nj(matrix_obj)
        tree.ladderize()
        #Phylo.draw_ascii(tree)
        output = StringIO.StringIO()
        Phylo.write(tree, output, 'newick')
        tree_str = output.getvalue()
        #print tree_str
        
        return tree_str
    
    class Meta:
        db_table = "Distance"

class DistanceAttempts(models.Model):
    rep_accnum1 = models.CharField(max_length=15)
    rep_accnum2 = models.CharField(max_length=15)
    status = models.IntegerField()
    run_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DistanceAttempts"
        
class UploadGenome(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=120)
    ip_addr = models.IPAddressField()
    genome_name = models.CharField(max_length=40)
    email = models.EmailField()
    cid = models.IntegerField(default=0)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "UploadGenome"

class Notification(models.Model):
    analysis = models.ForeignKey(Analysis, related_name='notifications')
    email = models.EmailField()
    status = models.IntegerField(default=0)
    
    class Meta:
        db_table = "Notification"

'''
MicrobeDB models
'''
class Analysislist(models.Model):
    table_name = models.CharField(primary_key=True, max_length=30)
    type = models.CharField(max_length=30)
    domain = models.CharField(max_length=13)
    author = models.CharField(max_length=30)
    comments = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'analysislist'

class Cdd(models.Model):
    pid = models.IntegerField()
    cdd_accession = models.IntegerField()
    evalue = models.CharField(max_length=10)
    analysis_id = models.IntegerField()
    query_start = models.IntegerField()
    query_end = models.IntegerField()
    subject_start = models.IntegerField()
    subject_end = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cdd'

class CddAnalysis(models.Model):
    analysis_id = models.IntegerField(primary_key=True)
    refseq_accession = models.CharField(max_length=25)
    gpv_id = models.IntegerField()
    microbedb_version = models.IntegerField()
    cdd_version = models.CharField(max_length=10)
    rpsblast_version = models.CharField(max_length=10)
    startdate = models.IntegerField()
    enddate = models.IntegerField()
    status = models.CharField(max_length=10)
    loading_status = models.CharField(max_length=10)
    class Meta:
        managed = False
        db_table = 'cdd_analysis'

class CddLookup(models.Model):
    accession = models.CharField(primary_key=True, max_length=20)
    external_accession = models.CharField(max_length=25)
    external_db = models.CharField(max_length=25)
    short_name = models.CharField(max_length=50)
    description = models.TextField()
    class Meta:
        managed = False
        db_table = 'cdd_lookup'

class CogAccessionToCategory(models.Model):
    accession = models.CharField(unique=True, max_length=10)
    category = models.CharField(max_length=1)
    class Meta:
        managed = False
        db_table = 'cog_accession_to_category'

class CogCategories(models.Model):
    identifier = models.CharField(max_length=1)
    category = models.CharField(max_length=250)
    class Meta:
        managed = False
        db_table = 'cog_categories'

class Gene(models.Model):
    gene_id = models.IntegerField(primary_key=True)
    rpv_id = models.IntegerField()
    version_id = models.IntegerField()
    gpv_id = models.IntegerField()
    gid = models.IntegerField(blank=True, null=True)
    pid = models.IntegerField(blank=True, null=True)
    protein_accnum = models.CharField(max_length=12, blank=True)
    gene_type = models.CharField(max_length=8, blank=True)
    gene_start = models.IntegerField(blank=True, null=True)
    gene_end = models.IntegerField(blank=True, null=True)
    gene_length = models.IntegerField(blank=True, null=True)
    gene_strand = models.CharField(max_length=2, blank=True)
    gene_name = models.TextField(blank=True)
    locus_tag = models.TextField(blank=True)
    gene_product = models.TextField(blank=True)
    gene_seq = models.TextField(blank=True)
    protein_seq = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'gene'

class Genomeproject(models.Model):
    gpv_id = models.IntegerField(primary_key=True)
    gp_id = models.IntegerField(blank=True, null=True)
    version_id = models.IntegerField()
    taxon_id = models.IntegerField(blank=True, null=True)
    org_name = models.TextField(blank=True)
    gram_stain = models.CharField(max_length=7, blank=True)
    genome_gc = models.FloatField(blank=True, null=True)
    patho_status = models.CharField(max_length=11, blank=True)
    disease = models.TextField(blank=True)
    genome_size = models.FloatField(blank=True, null=True)
    pathogenic_in = models.TextField(blank=True)
    temp_range = models.CharField(max_length=17, blank=True)
    habitat = models.CharField(max_length=15, blank=True)
    shape = models.TextField(blank=True)
    arrangement = models.TextField(blank=True)
    endospore = models.CharField(max_length=7, blank=True)
    motility = models.CharField(max_length=7, blank=True)
    salinity = models.TextField(blank=True)
    oxygen_req = models.CharField(max_length=15, blank=True)
    release_date = models.DateField(blank=True, null=True)
    centre = models.TextField(blank=True)
    gpv_directory = models.TextField(blank=True)
    chromosome_num = models.IntegerField(blank=True, null=True)
    plasmid_num = models.IntegerField(blank=True, null=True)
    contig_num = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'genomeproject'

class GenomicIslands(models.Model):
    gi_id = models.IntegerField(primary_key=True)
    rep_accnum = models.CharField(max_length=12, blank=True)
    start = models.IntegerField()
    end = models.IntegerField()
    prediction_method = models.CharField(max_length=16)
    prediction_method_params = models.IntegerField(blank=True, null=True)
    genome_image = models.TextField(blank=True)
    gi_image_map = models.TextField(blank=True)
    curated = models.CharField(max_length=3, blank=True)
    fasta_sequence = models.TextField(blank=True)
    genome_image_islandview = models.TextField(blank=True)
    gi_image_map_islandview = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'genomic_islands'

class GenomicIslandsDup(models.Model):
    gi_id = models.IntegerField(primary_key=True)
    rep_accnum = models.CharField(max_length=12, blank=True)
    start = models.IntegerField()
    end = models.IntegerField()
    prediction_method = models.CharField(max_length=16)
    prediction_method_params = models.IntegerField(blank=True, null=True)
    genome_image = models.TextField(blank=True)
    gi_image_map = models.TextField(blank=True)
    curated = models.CharField(max_length=3, blank=True)
    fasta_sequence = models.TextField(blank=True)
    genome_image_islandview = models.TextField(blank=True)
    gi_image_map_islandview = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'genomic_islands_dup'

class GiPrograms(models.Model):
    gi_program_id = models.IntegerField(primary_key=True)
    rep_accnum = models.CharField(max_length=12)
    program_name = models.CharField(max_length=16)
    min_gi_size = models.IntegerField()
    parameters = models.TextField()
    status = models.CharField(max_length=8)
    class Meta:
        managed = False
        db_table = 'gi_programs'

class Islandpick(models.Model):
    islandpick_id = models.IntegerField(primary_key=True)
    query_rep_accnum = models.CharField(max_length=12)
    reference_rep_accnum = models.TextField()
    alignment_program = models.TextField()
    min_gi_size = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=8)
    curated = models.CharField(max_length=3, blank=True)
    class Meta:
        managed = False
        db_table = 'islandpick'

class IslandviewerRunDate(models.Model):
    gpv_id = models.IntegerField(primary_key=True)
    run_date = models.DateField()
    class Meta:
        managed = False
        db_table = 'islandviewer_run_date'

class MicrobedbMeta(models.Model):
    meta_id = models.IntegerField(primary_key=True)
    meta_key = models.CharField(unique=True, max_length=255)
    meta_value = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'microbedb_meta'

class OrganismCache(models.Model):
    rep_accnum = models.CharField(max_length=12)
    definition = models.TextField()
    class Meta:
        managed = False
        db_table = 'organism_cache'

class PathogenAssociatedGenes(models.Model):
    gpv_id = models.IntegerField()
    pid = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=11)
    genus_hits = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'pathogen_associated_genes'

class PathogenAssociatedGenesCompared(models.Model):
    gpv_id = models.IntegerField()
    pid = models.IntegerField()
    status = models.CharField(max_length=11)
    genus_hits = models.IntegerField()
    version = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'pathogen_associated_genes_compared'

class PathogenStatus(models.Model):
    gpv_id = models.IntegerField(primary_key=True)
    version_id = models.IntegerField()
    pathogen_status = models.CharField(max_length=11, blank=True)
    curated = models.CharField(max_length=3)
    org_name = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'pathogen_status'

class Reference(models.Model):
    ref_id = models.IntegerField(primary_key=True)
    gp_id = models.IntegerField(blank=True, null=True)
    ref_source = models.CharField(max_length=6)
    ref_value = models.TextField(blank=True)
    ref_url = models.TextField(blank=True)
    ref_comment = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'reference'

class Replicon(models.Model):
    rpv_id = models.IntegerField(primary_key=True)
    gpv_id = models.IntegerField()
    version_id = models.IntegerField()
    rep_accnum = models.CharField(max_length=12, blank=True)
    definition = models.TextField(blank=True)
    rep_type = models.CharField(max_length=10, blank=True)
    rep_ginum = models.TextField(blank=True)
    file_name = models.TextField(blank=True)
    cds_num = models.IntegerField(blank=True, null=True)
    gene_num = models.IntegerField(blank=True, null=True)
    protein_num = models.IntegerField(blank=True, null=True)
    rep_size = models.IntegerField(blank=True, null=True)
    rna_num = models.IntegerField(blank=True, null=True)
    file_types = models.TextField(blank=True)
    distance_calculated = models.CharField(max_length=3, blank=True)
    class Meta:
        managed = False
        db_table = 'replicon'

class RepliconDistance(models.Model):
    rep_accnum1 = models.CharField(max_length=12)
    rep_accnum2 = models.CharField(max_length=12)
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'replicon_distance'

class RepliconDistanceTmp(models.Model):
    rep_accnum1 = models.CharField(max_length=12)
    rep_accnum2 = models.CharField(max_length=12)
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'replicon_distance_tmp'

class Taxonomy(models.Model):
    taxon_id = models.IntegerField(primary_key=True)
    superkingdom = models.TextField(blank=True)
    phylum = models.TextField(blank=True)
    class_field = models.TextField(db_column='class', blank=True) # Field renamed because it was a Python reserved word.
    order = models.TextField(blank=True)
    family = models.TextField(blank=True)
    genus = models.TextField(blank=True)
    species = models.TextField(blank=True)
    other = models.TextField(blank=True)
    synonyms = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'taxonomy'

class Updatelog(models.Model):
    ul_id = models.IntegerField(primary_key=True)
    record_id = models.IntegerField()
    record_fieldname = models.TextField()
    object_name = models.CharField(max_length=13)
    field_name = models.TextField()
    original_value = models.TextField(blank=True)
    new_value = models.TextField()
    curator_name = models.TextField()
    update_date = models.DateField()
    version_id = models.TextField(blank=True)
    update_status = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    ref_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'updatelog'

class Version(models.Model):
    version_id = models.IntegerField(primary_key=True)
    dl_directory = models.TextField(blank=True)
    version_date = models.DateField()
    used_by = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'version'

class Virulence(models.Model):
    protein_accnum = models.CharField(max_length=18,primary_key=True)
    external_id = models.CharField(max_length=18)
    source = models.CharField(max_length=4, blank=True)
    type = models.CharField(max_length=20, blank=False)
    class Meta:
        managed = False
        db_table = 'virulence'
 



