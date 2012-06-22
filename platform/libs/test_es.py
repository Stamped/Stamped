
ES_INDICES  = [
    {
        'name' : 'plays', 
        #'settings'
    }, 
]

ES_MAPPINGS = [
    {
        'type'      : 'line', 
        'indices'   : [ 'plays', ], 
        'mapping'   : {
            'properties' : {
                'title' : {
                    'boost' : 1.0, 
                    'index' : 'analyzed', 
                    'store' : 'yes', 
                    'type'  : 'string', 
                    'term_vector' : 'with_positions_offsets', 
                }, 
                'genre' : {
                    'index' : 'analyzed', 
                    'store' : 'yes', 
                    'type'  : 'string', 
                    'term_vector' : 'with_positions_offsets', 
                }, 
                'speaker' : {
                    'index' : 'analyzed', 
                    'store' : 'yes', 
                    'type'  : 'string', 
                    'term_vector' : 'with_positions_offsets', 
                }, 
                'lines' : {
                    'properties' : {
                        'ref'   : {
                            'index' : 'analyzed', 
                            'store' : 'yes', 
                            'type'  : 'string', 
                        }, 
                        'line'  : {
                            'boost' : 2.0, 
                            'index' : 'analyzed', 
                            'store' : 'yes', 
                            'type'  : 'string', 
                            'term_vector' : 'with_positions_offsets', 
                        }, 
                    }, 
                }, 
            }, 
        }, 
    }, 
]

