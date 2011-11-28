#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import utils
import copy

def getInstances():
    replSetName = 'stamped-dev-01'
    
    dbCount     = 2
    apiCount    = 2
    webCount    = 2
    monCount    = 1
    
    ### TEMPLATES
    dbInstance = {
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
        'instance_type' : 'm2.xlarge', # PROD
    }
    
    apiInstance = {
        'roles' : [ 'apiServer', ], 
        'port' : '5000', 
        'replSet' : replSetName, 
        'instance_type' : 'c1.xlarge',  # PROD
        'placement' : None, 
    }
    
    webInstance = {
        'roles' : [ 'webServer', ], 
        'port' : '5000', 
        'replSet' : replSetName, 
        'instance_type' : 'c1.xlarge',  # PROD
        'placement' : None, 
    }
    
    monInstance = {
        'roles' : [ 'monitor', ], 
        'replSet' : replSetName, 
    }
    
    placements = [
        'us-east-1a', 
        'us-east-1b', 
        'us-east-1c', 
    ]
    
    ### BUILD CONFIG FILE
    config = []
    
    def _addNode(template, namePrefix, count):
        instance = template.copy()
        instance['name'] = '%s%d' % (namePrefix, count)
        
        if 'placement' in instance and instance['placement'] is None:
            instance['placement'] = placements[i % len(placements)]
        
        config.append(instance)
    
    for i in xrange(dbCount):
        _addNode(dbInstance, 'db', i)
    
    for i in xrange(apiCount):
        _addNode(apiInstance, 'api', i)
    
    for i in xrange(webCount):
        _addNode(webInstance, 'web', i)
    
    for i in xrange(monCount):
        _addNode(monInstance, 'mon', i)
    
    return config

