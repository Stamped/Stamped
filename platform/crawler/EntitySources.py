#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

sources = { }

def registerSource(name, factory):
    source = __getSource(name)
    
    if source:
        return source['id']
    else:
        sourceID = len(sources)
        
        sources[name] = {
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
    return list(v['factory']() for v in sources.itervalues())

def __getSource(name):
    name = name.lower().strip()
    
    for k, v in sources.iteritems():
        if name == k.lower():
            return v
    
    return None

