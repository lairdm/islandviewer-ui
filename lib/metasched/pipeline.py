'''
Read and parse metascheduler pipeline json files
'''

from django.conf import settings
import json
import os.path
import pprint

class Parser():
    
    def read(self, pipeline):
        '''
        We're going to take the pipeline name, build our file to read
        then slurp it in with json
        '''
        
        pipeline_file = os.path.join(settings.PIPELINE_PATH, pipeline.lower()) + '.config'
        
        json_data = open(pipeline_file)
        data = json.load(json_data)
        json_data.close()
        
        return data
