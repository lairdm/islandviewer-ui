'''
    Definition of the various track types to
    be displayed in Islandplot
'''

definitions = {
               'Std_Islandpick': {
                                 'trackType': 'track',
                                 'inner_radius': 50,
                                 'outer_radius': 100,
                                 'prediction_method': ['Islandpick']
                                 },
               'Std_GC': {
                          'trackType': 'plot',
                          'bp_per_element': 10000,
                          'plot_width': 50,
                          'plot_radius': 150
                          },
               'Std_Circularplot': {
                                    'container': '#circularchart'
                                    }
               }
