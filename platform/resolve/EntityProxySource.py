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

        self.__proxy    = proxy
        self.__source   = getSource(proxy.source)
        
        # Enrich all groups, except the source specific fields
        allGroupNames = set([group().groupName for group in allGroups])
        allSourceNames = set([source().sourceName for source in allSources])
        self.__groups = allGroupNames - allSourceNames
        self.__groups.add(proxy.source)
        
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

    def enrichEntity(self, entity, groups, controller, decorations, timestamps):
        for group in groups:
            group.enrichEntityWithEntityProxy(entity, self.__proxy)
        return True

