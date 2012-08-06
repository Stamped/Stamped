#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

__sinks = { }

def registerSink(name, factory):
    database = __getSink(name)
    
    if database:
        return database['id']
    else:
        databaseID = len(__sinks)
        
        __sinks[name] = {
            'factory' : factory, 
            'id' : databaseID, 
        }
        
        return databaseID

def getSink(name):
    database = __getSink(name)
    
    if database:
        return database['id']
    else:
        return None

def instantiateSink(name):
    database = __getSink(name)
    
    if database:
        return database['factory']()
    else:
        return None

def instantiateAll():
    return list(v['factory']() for v in __sinks.itervalues())

def __getSink(name):
    name = name.lower().strip()
    
    for k, v in __sinks.iteritems():
        if name == k.lower():
            return v
    
    return None

