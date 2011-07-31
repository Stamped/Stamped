#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import utils

def getInstances():
    replSetName = 'stamped-dev-01'
    
    return [
        {
            'name' : 'db0', 
            'roles' : [ 'db', ], 
            'mongodb' : {
                'replSet' : replSetName, 
                'port' : 27017, 
            }, 
            'raid' : {
                'diskSize': 8,
                'numDisks': 4,
            },
        }, 
        {
            'name' : 'db1', 
            'roles' : [ 'db', ], 
            'mongodb' : {
                'replSet' : replSetName, 
                'port' : 27017, 
            }, 
            'raid' : {
                'diskSize': 8,
                'numDisks': 4,
            }, 
        }, 
        {
            'name' : 'dev0', 
            'roles' : [ 'webServer', ], 
            'port' : '5000', 
            
            'replSet' : replSetName, 
        }, 
    ]

