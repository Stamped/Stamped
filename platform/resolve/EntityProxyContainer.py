#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntityProxyContainer' ]

import Globals
from logs import report

try:
    from api import Entity
    from resolve.BasicSourceContainer   import BasicSourceContainer
    from resolve.EntityGroups           import *
    from resolve.EntityProxySource      import EntityProxySource
except:
    report()
    raise

seedPriority = 100

class EntityProxyContainer(BasicSourceContainer):
    """
    """

    def __init__(self, proxy):
        BasicSourceContainer.__init__(self)

        self.__proxy = proxy

        for group in allGroups:
            self.addGroup(group())

        self.addSource(EntityProxySource(self.__proxy))
        
        self.setGlobalPriority('seed', seedPriority)

    def buildEntity(self):
        entity              = Entity.buildEntity(kind=self.__proxy.kind)
        # entity.entity_id    = 'T_%s_%s' % (self.__proxy.source.upper(), self.__proxy.key)
        entity.title        = self.__proxy.name
        entity.kind         = self.__proxy.kind 
        entity.types        = self.__proxy.types
        
        decorations = {}
        
        modified = self.enrichEntity(entity, decorations, max_iterations=None, timestamp=None)
        
        return entity

