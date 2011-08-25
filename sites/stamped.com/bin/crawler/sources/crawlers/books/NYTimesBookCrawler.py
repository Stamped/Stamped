#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from gevent.pool import Pool
from AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "NYTimesBookCrawler" ]

# TODO: crawler cutting out after seemingly indeterminate amount of time; why?

class NYTimesBookCrawler(AExternalEntitySource):
    """ 
        Entity crawler which parses all of the NYTimes bestseller list.
    """
    
    TYPES = set([ 'book' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "NYTimesBook", self.TYPES, 512)
        self.base = 'http://www.nytimes.com'
        self.seen = set()
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        pool = Pool(64)
        seed = ''
        
        # parse the top-level page containing links to all regions (states for the US)
        self._parseResultsPage(pool, seed)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, url):
        utils.log('[%s] parsing page %s' % (self, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, url))
            return

import EntitySources
EntitySources.registerSource('nytimes', NYTimesBookCrawler)

