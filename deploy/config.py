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
    webCount    = 1
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
    }

    webInstance = {
        'roles' : [ 'webServer', ], 
        'port' : '5000', 
        'replSet' : replSetName, 
    }

    monInstance = {
        'roles' : [ 'monitor', ], 
        'replSet' : replSetName, 
    }

    ### BUILD CONFIG FILE
    config = []

    for i in xrange(dbCount):
        instance = dbInstance.copy()
        instance['name'] = 'db%d' % i
        config.append(instance)

    for i in xrange(webCount):
        instance = webInstance.copy()
        instance['name'] = 'api%d' % i
        config.append(instance)

    for i in xrange(monCount):
        instance = monInstance.copy()
        instance['name'] = 'mon%d' % i
        config.append(instance)

    return config

