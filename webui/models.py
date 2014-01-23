from __future__ import unicode_literals

from django.db import models

STATUS = {'PENDING':1,'RUNNING':2,'ERROR':3,'COMPLETE':4}
STATUS_CHOICES = [
    (STATUS['PENDING'], 'Pending'),
    (STATUS['RUNNING'], 'Running'),
    (STATUS['ERROR'], 'Error'),
    (STATUS['COMPLETE'], 'Complete'),
]

class CustomGenome(models.Model):
    cid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    cds_num = models.IntegerField(default=0)
    rep_size = models.IntegerField(default=0)
    filename = models.CharField(max_length=60)
    formats = models.CharField(max_length=50)
    submit_date = models.DateTimeField('date submitted')

    class Meta:
        db_table = "CustomGenome"

class NameCache(models.Model):
    cid = models.CharField(max_length=15)
    name = models.CharField(max_length=60)

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
    class Meta:
        db_table = "GIAnalysisTask"

class GenomicIsland(models.Model):
    gi = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Analysis)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    prediction_method = models.CharField(max_length=15)

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
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS['PENDING'])
    genome_name = models.CharField(max_length=40)
    email = models.EmailField()
    aid = models.IntegerField(default=0)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "UploadGenome"

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
    rep_seq = models.TextField(blank=True)
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
    class Meta:
        managed = False
        db_table = 'virulence'
 



