#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "WashMagCrawler" ]

class WashMagCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "WashMag", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        # hardcoded list of URLs for Washingtonian 'Top' lists (no directly located)
        href = [
            'http://www.washingtonian.com/restaurantreviews/20/index.html',
            'http://www.washingtonian.com/restaurantreviews/10/index.html', 
            'http://www.washingtonian.com/restaurantreviews/19/index.html', 
            'http://www.washingtonian.com/restaurantreviews/17/index.html'
        ]
        
        for l in href:
            pool.spawn(self._parseResultsPage, pool, l)
            
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.find('div', { 'class' : 'searchresults' }).findAll('div', { 'class' : 'fs1-sans' })
        
        for result in results:
            
            if 'Price' in result.getText():
                continue 
                
            if 'Kid' in result.getText():
                continue
                
            if 'Other' in result.getText():
                continue
            
            if 'Wheelchair' in result.getText():
                continue 
                
            if 'Cuisines' in result.getText():
                continue
                
            if 'Rating' in result.getText():
                continue
            
            if 'Latest' in result.getText():
                continue 
            
            try:
                name = result.find('strong').getText().strip()
            except Exception:
                continue

            try:
                addr = '{0} {1}, {2}, {3}'.format(result.find('span').getText(), 
                                                  result.find('span').findNext('span').getText(), 
                                                  result.find('span').findNext('span').findNext('span').getText(), 
                                                  result.find('span').findNext('span').findNext('span').findNext('span').getText())
            except Exception:
                addr = ''
                utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                continue
                        
            if addr == '':
                continue
                
            if name == '':
                continue 
            
            if (name, addr) in self._seen:
                continue
            
            self._seen.add((name, addr))
            
            entity = Entity()
            entity.subcategory = "restaurant"
            entity.title   = name
            entity.address = addr
            entity.sources.washmag = { }
            
            self._output.put(entity)
        
        return 
        
from crawler import EntitySources
EntitySources.registerSource('washmag', WashMagCrawler)

