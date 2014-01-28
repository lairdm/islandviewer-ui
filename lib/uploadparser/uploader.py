import os.path
import subprocess
import pprint
from webui.models import UploadGenome
from django.conf import settings
from Bio import SeqIO
from uploadparser import submitter

class GenomeParser():
        
    def submitUpload(self, file, format_type, name, email_addr, uploader_ip):
        '''
        We're going to accept an uploaded file and
        put it in the uploads directory with an
        autoinc filename then send this to the
        backend for processing
        '''
        
        # Make the filename with the correct format
        genome_format = ''
        if format_type == 'GENBANK':
            genome_format += 'gbk'
        else:
            genome_format += 'embl'

        # Create the output file and write out the upload
        # No, we're going to do the tests in the backend now
        g_name = "Custom Genome"
        if name:
            g_name = name

        try:
            genome_data = file.read()
            ret = submitter.send_job(genome_data, genome_format, g_name, email_addr, uploader_ip)
        except Exception as e:
            if settings.DEBUG:
                debug_error = ''
                for arg in e.args:
                    print "{0}\n".format(arg)
                    debug_error += arg
                    raise Exception("Unknown error" + debug_error)

            raise Exception("Unknown error")

        pprint.pprint(ret)
                
        
        return ret;
    