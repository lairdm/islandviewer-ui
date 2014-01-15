import os.path
import subprocess
import pprint
from webui.models import UploadCounter
from django.conf import settings
from Bio import SeqIO

class GenomeParser():
        
    def submitUpload(self, file, format_type, name, email_addr, uploader_ip):
        '''
        We're going to accept an uploaded file and
        put it in the uploads directory with an
        autoinc filename then send this to the
        backend for processing
        '''
        
        upload = UploadCounter(ip_addr = uploader_ip)
        upload.save()
        upload_file = os.path.join(settings.GENOME_UPLOAD_PATH, str(upload.id))

        # Make the filename with the correct format
        if format_type == 'GENBANK':
            upload_file += '.gbk'
        else:
            upload_file += '.embl'

        # Create the output file and write out the upload
        with open(upload_file, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        '''
        Do tests on uploaded file here
        '''
        try:
            handle = SeqIO.read(open(upload_file), format_type.lower())
        except ValueError, e:
            self.cleanupFile(upload_file)
            raise e
#            print "upload_file doesn't seem to be a valid " + format_type.lower() + " file"
#            pprint.pprint(e)
        else:
            if(format_type == 'GENBANK'):
                self.checkGenbank(handle)
            else:
                self.checkEmbl(handle)
            print "Parsing..."
        
        g_name = "Custom Genome"
        if name:
            g_name = name
        
        upload_script = settings.GENOME_SUBMISSION_SCRIPT.format(filename=upload_file, genome_name=g_name)
        print "Wanting to run " + upload_script
        
        try:
#            output = 20
#            output = subprocess.check_output(upload_script.split(), stderr=subprocess.STDOUT, universal_newlines=True)
            output = subprocess.check_output(upload_script.split(), universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print "Error submitting: " + str(e.returncode), e.output
            raise Exception("Error submitting analysis")
        else:
            print "Successfully submitted " + output
#            return 20
            return int(output)

        # Get the analysis id here and return it
        
    def checkGenbank(self,handle):
        if not handle.seq:
            raise Exception("No sequence")
        print "Checking"
        
    def checkEmbl(self, handle):
        print "Checking"
        
    def cleanupFile(self, filename):
        os.remove(filename)
        