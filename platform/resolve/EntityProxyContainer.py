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

class EntityProxyContainer(object):
    def __init__(self):
        self.__proxies = []

    def addProxy(self, proxy):
        self.__proxies.append(proxy)
        return self

    def addAllProxies(self, proxies):
        self.__proxies.extend(proxies)
        return self
        
    def buildEntity(self):
        if not self.__proxies:
            raise Exception('No proxies added so far, cannot build entity')
        
        primaryProxy = self.__proxies[0]
        entity = Entity.buildEntity(kind=primaryProxy.kind)
        entity.kind = primaryProxy.kind 
        entity.types = primaryProxy.types

        if entity.isType('book'):
            entity.title = self.__chooseBookTitle()
        else:
            entity.title = self.__proxy.name

        sourceContainer = BasicSourceContainer()
        for proxy in self.__proxies:
            sourceContainer.addSource(EntityProxySource(proxy))

        sourceContainer.enrichEntity(entity, {}, max_iterations=None, timestamp=None)
        
        return entity

    def __chooseBookTitle(self):
        return self.__proxies[0].name

