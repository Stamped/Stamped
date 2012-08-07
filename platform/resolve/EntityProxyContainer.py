#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntityProxyContainer' ]

import Globals

from api_old import Entity
from resolve.BasicSourceContainer import BasicSourceContainer
from resolve.EntityProxySource import EntityProxySource

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
            entity.title = self.__chooseBestTitle()

        sourceContainer = BasicSourceContainer()
        for proxy in self.__proxies:
            sourceContainer.addSource(EntityProxySource(proxy))

        sourceContainer.enrichEntity(entity, {})
        
        return entity

    def __chooseBestTitle(self):
        def penaltyChar(c):
            return not (c.isalpha() or c.isspace())
        def titleScore(title):
            return -len(title) - len(filter(penaltyChar, title)) * 2
        return max((proxy.name for proxy in self.__proxies), key=titleScore)

    def __chooseBookTitle(self):
        # If we have a title from iTunes, always use that. iTunes has much much better titles than
        # Amazon.
        for proxy in self.__proxies:
            if proxy.source == 'itunes':
                return proxy.name
        return self.__chooseBestTitle()

