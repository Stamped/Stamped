#!/usr/bin/env python

#SFGate only maintains a list of the top 100 restaurants in the SF area

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "SFGateCrawler" ]

class SFGateCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "SFGate", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://www.sfgate.com/cgi-bin/listings/restaurants/listtop2011?Submit=1'
        
        self._parseResultsPage(pool, seed)
            
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.find('div', { 'class' : 'search_results' }).findAll('div', { 'class' : 'restaurant'})
        
        for result in results:
            
            try:
                name = result.find('h3').find('a').getText().strip()
            except Exception:
                continue

            try:
                street = result.find('br').previousSibling.strip()
                locale = '{0}, {1}'.format(result.find('br').nextSibling.strip(), 'CA')
                addr = '{0}, {1}'.format(street, locale)
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
            entity.sources.sfgate = { }
            
            self._output.put(entity)
        
        # try the next page
        try: 
            href_get = soup.find('li', { 'class' : 'next' }).find('a').get('href')
            next_page = '{0}{1}'.format('http://www.sfgate.com', href_get)
        except Exception: 
            next_page = ''
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('sfgate', SFGateCrawler)

