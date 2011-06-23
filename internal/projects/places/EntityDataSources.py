#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__sources = { }

def registerSource(name, factory):
    source = __getSource(name)
    
    if source:
        return source['id']
    else:
        sourceID = len(__sources)
        
        __sources[name] = {
            'factory' : factory, 
            'id' : sourceID, 
        }
        
        return sourceID

def getSourceID(name):
    source = __getSource(name)
    
    if source:
        return source['id']
    else:
        return None

def instantiateSource(name):
    source = __getSource(name)
    
    if source:
        return source['factory']()
    else:
        return None

def instantiateAll():
    return (v['factory']() for v in __sources.itervalues())

def __getSource(name):
    name = name.lower().strip()
    
    for k, v in __sources.iteritems():
        if name == k.lower():
            return v
    
    return None

