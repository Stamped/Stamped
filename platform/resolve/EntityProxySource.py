#!/usr/bin/env python
from __future__ import absolute_import

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
        
        
    @property
    def sourceName(self):
        return self.__proxy.source 

    @property 
    def kinds(self):
        return self.__source.kinds

    @property 
    def types(self):
        return self.__source.types

    def getGroups(self, entity=None):
        return self.__source.getGroups(entity)

    def enrichEntity(self, entity, groups, controller, decorations, timestamps):
        for group in groups:
            group.enrichEntityWithEntityProxy(entity, self.__proxy)
        return True

