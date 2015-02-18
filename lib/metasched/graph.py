'''
Use the pipeline object's data structure and make a d3 dagre
graph of the current state
'''

from webui.models import Analysis, GIAnalysisTask, STATUS_CHOICES
import json
import pprint

class Grapher():
    
    def makeGraph(self, aid, pipeline):
        components = {}
        CHOICES = dict(STATUS_CHOICES)
        tasks = GIAnalysisTask.objects.all().filter(aid=aid)
        
        for task in tasks:
            components[task.prediction_method] = task.status
        
#        pprint.pprint(components)
#        pprint.pprint(pipeline)
        
        nodes = []
        pairs = []
        
        for c in pipeline['components']:
            status = components[c['name']]
            nodes.append({'name': c['name'], 'status': CHOICES[status]})
            if(('on_failure' not in c) and ('on_success' not in c)):
                continue
            if(CHOICES[status] == 'Error'):
                pairs.append({'name': c['name'], 'nexttask': c['on_success'], 'status':'FAILED'})
            elif(CHOICES[status] == 'Complete'):
                pairs.append({'name': c['name'], 'nexttask': c['on_success'], 'status':'SUCCESS'})
            else:
                pairs.append({'name': c['name'], 'nexttask': c['on_success'], 'status':'PENDING'})

        graph_set = {'nodes': nodes, 'edges': pairs}

        json_str = json.dumps(graph_set, sort_keys=True, indent=4)
#        print json_str

        return json_str

    def makeTrueGraph(self, aid, pipeline):
        components = {}
        CHOICES = dict(STATUS_CHOICES)
        tasks = GIAnalysisTask.objects.all().filter(aid=aid)
        
        for task in tasks:
            components[task.prediction_method] = task.status
        
#        pprint.pprint(components)
#        pprint.pprint(pipeline)
        
        nodes = []
        pairs = []
        
        for c in pipeline['components']:
            status = components[c['name']]
            nodes.append({'name': c['name'], 'status': CHOICES[status]})
            if(('on_failure' not in c) and ('on_success' not in c)):
                continue
            if(CHOICES[status] == 'Error'):
                pairs.append({'name': c['name'], 'nexttask': c['on_failure'], 'status':'FAILED'})
            elif(CHOICES[status] == 'Complete'):
                pairs.append({'name': c['name'], 'nexttask': c['on_success'], 'status':'SUCCESS'})
            else:
                pairs.append({'name': c['name'], 'nexttask': c['on_success'], 'status':'PENDING'})

        graph_set = {'nodes': nodes, 'edges': pairs}

        json_str = json.dumps(graph_set, sort_keys=True, indent=4)
#        print json_str

        return json_str
    
