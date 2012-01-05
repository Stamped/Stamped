#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals
import utils
import copy

def getInstances():
    replSetName = 'stamped-dev-01'
    
    stack = {
        # db nodes handle storing/retrieving all of our platform's core data via mongodb
        'db' : {
            'count' : 2, 
            
            'template' : {
                'roles' : [ 'db', ], 
                'mongodb' : {
                    'replSet' : replSetName, 
                    'port' : 27017, 
                }, 
                'raid' : {
                    'diskSize': 8,
                    'numDisks': 4,
                },
                'placement' : None, 
                'instance_type' : 'm2.xlarge', 
            }, 
        }, 
        
        # api nodes run our api web servers
        'api' : {
            'count' : 1, 
            
            'template' : {
                'roles' : [ 'apiServer', ], 
                'port' : '5000', 
                'replSet' : replSetName, 
                'instance_type' : 'c1.xlarge',  
                'placement' : None, 
            }, 
        }, 
        
        # web nodes run our public web servers
        'web' : {
            'count' : 1, 
            
            'template' : {
                'roles' : [ 'webServer', ], 
                'port' : '5000', 
                'replSet' : replSetName, 
                'instance_type' : 'c1.xlarge',  
                'placement' : None, 
            }, 
        }, 
        
        # monitor nodes monitor the rest of the stack
        'mon' : {
            'template' : {
                'roles' : [ 'monitor', ], 
                'replSet' : replSetName, 
            }, 
        }, 
        
        # worker nodes handle stateless, asynchronous tasks
        'work' : {
            'template' : {
                'roles' : [ 'work', ], 
            }, 
        }, 
    }
    
    placements = [
        'us-east-1a', 
        'us-east-1b', 
        'us-east-1c', 
    ]
    
    ### BUILD CONFIG FILE
    config = []
    
    for nodeType in stack:
        v = stack[nodeType]
        template = v['template']
        count    = v['count'] if 'count' in v else 1
        
        for i in xrange(count):
            instance = template.copy()
            instance['name'] = '%s%d' % (nodeType, i)
            
            # automate placement via round-robin of us-east availability zones
            if 'placement' in instance and instance['placement'] is None:
                instance['placement'] = placements[i % len(placements)]
            
            config.append(instance)
    
    return config

