from webui.models import Analysis, GenomicIsland, GC, CustomGenome
from islandplot.types import definitions

class Generator():
    def __init__(self,aid):
        '''
        We're going to save our analysis for
        generating the tracks
        '''
        try:
            self.analysis = Analysis.objects.get(pk=aid)
        except Analysis.DoesNotExist:
            pass
        
        self.gis = GenomicIsland.objects.filter(aid_id=aid)
        
        self.gcvalues = GC.objects.get(pk=aid)
    
    def generateCircular(self, name, container):
        js_str = ''
        
        js_str += "var " + name + "layout = {genomesize: "
        if(self.analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=self.analysis.ext_id)
            js_str += genome.rep_size
        elif(self.analysis.atype == Analysis.MICROBEDB):
            js_str += '6000000'
        
        js_str += ", container: " + container + "};\n"
        js_str += "var " + name + "track = new circularTrack(" + name + "layout, " + name + "tracks);\n"
        
        return js_str                                         
                                                
    
    def generateTrack(self, trackName, track_def):
        formatting = definitions[track_def]
        result = {}

        GIs =  self.gis.filter(prediction_method__in = formatting['prediction_method'])

        # Start building the track
        result['trackName'] = trackName
        result['trackType'] = formatting['trackType']
        result['innerRadius'] = formatting['inner_radius']
        result['outerRadius'] = formatting['outer_radius']
        
        items = []
        for GI in GIs.all():
            item = {'id': GI.gi,
                    'start': GI.start,
                    'end': GI.end,
                    'name': GI.gi
                    }
            items.append(item)
            
        result['items'] = items
        
        return result
    
    def generateGCPlot(self, trackName, track_def):
        formatting = definitions[track_def]
        result = {}
        
        result['items'] = [float(x) for x in self.gcvalues.gc.split(',')]
        result['plot_min'] = self.gcvalues.min
        result['plot_max'] = self.gcvalues.max
        result['plot_mean'] = self.gcvalues.mean
            
        # Start building the track
        result['trackName'] = trackName
        result['trackType'] = formatting['trackType']
        result['plot_width'] = formatting['plot_width']
        result['plot_radius'] = formatting['plot_radius']
        
        return result
