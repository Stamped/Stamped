#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import gevent, os, re
from Netflix import NetflixClient

from AEntitySource import AExternalServiceEntitySource
from api.Entity import Entity

__all__ = [ "NetflixAPI" ]

NETFLIX_API_KEY    = 'nr5nzej56j3smjra6vtybbvw'
NETFLIX_API_SECRET = 'H5A633JsYk'

class NetflixAPI(AExternalServiceEntitySource):
    """
        Netflix API wrapper
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, 'Netflix', self.TYPES, 128)
        
        self._client = NetflixClient("Stamped", NETFLIX_API_KEY, NETFLIX_API_SECRET, '', False)
    
    def getMaxNumEntities(self):
        return 100 # approximation for now
    
    def _run(self):
        utils.log("[%s] parsing instantly available movies" % (self, ))
        
        index = netflixClient.catalog.getIndex()
        # TODO: use index
        # TODO: use xml parser
        
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing available movies" % (self, ))

import EntitySources
EntitySources.registerSource('netflix', NetflixAPI)

