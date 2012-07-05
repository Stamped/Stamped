#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntityProxySource' ]

import Globals
from logs import report

try:
    from resolve.AExternalSource        import AExternalSource
    from resolve.EntityGroups           import *
    from resolve.ResolverSources        import *
except:
    report()
    raise

class EntityProxySource(AExternalSource):

    def __init__(self, proxy):
        AExternalSource.__init__(self)

        self.__groups   = set()
        self.__proxy    = proxy
        self.__source   = getSource(proxy.source)
        
        for group in allGroups:
            self.__groups.add(group().groupName)
    
    @property
    def sourceName(self):
        return self.__proxy.source 

    @property 
    def kinds(self):
        return set([
            'place',
            'person',
            'media_collection',
            'media_item',
            'software',
            'search',
        ])

    @property 
    def types(self):
        return set()

    def getGroups(self, entity=None):
        return self.__groups

    def enrichEntity(self, entity, controller, decorations, timestamps):
        self.__source.enrichEntityWithEntityProxy(self.__proxy, entity, controller, decorations, timestamps)
        return True

