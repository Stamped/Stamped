#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import copy

__replSetName = 'stamped-dev-01'

__stack = {
    # db nodes handle storing/retrieving all of our platform's core data via mongodb
    'db' : {
        'count' : 2, 
        
        'template' : {
            'roles' : [ 'db', ], 
            'mongodb' : {
                'replSet' : __replSetName, 
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
            'replSet' : __replSetName, 
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
            'replSet' : __replSetName, 
            'instance_type' : 'c1.xlarge',  
            'placement' : None, 
        }, 
    }, 
    
    # monitor nodes monitor the rest of the stack
    'mon' : {
        'count' : 1, 
        
        'template' : {
            'roles' : [ 'monitor', ], 
            'replSet' : __replSetName, 
        }, 
    }, 
    
    # worker nodes handle stateless, asynchronous tasks
    'work' : {
        'count' : 1, 
        
        'template' : {
            'roles' : [ 'work', 'mem', ], 
        }, 
    }, 
    
    # dedicated memcached nodes
    'mem' : {
        'count' : 0, 
        
        'template' : {
            'roles' : [ 'mem', ], 
        }, 
    }, 
}

__placements = [
    'us-east-1a', 
    'us-east-1b', 
    'us-east-1c', 
]

def getInstance(instance_type):
    v = __stack[instance_type]
    
    return v['template'].copy()

def getInstances():
    ### BUILD CONFIG FILE
    config = []
    
    for nodeType in __stack:
        count = __stack[nodeType]['count'] if 'count' in v else 1
        
        for i in xrange(count):
            instance = getInstance(nodeType)
            instance['name'] = '%s%d' % (nodeType, i)
            
            # automate placement via round-robin of us-east availability zones
            if 'placement' in instance and instance['placement'] is None:
                instance['placement'] = __placements[i % len(__placements)]
            
            config.append(instance)
    
    return config

def getPlacements():
    return __placements

