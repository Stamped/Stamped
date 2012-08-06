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

__all__ = [ "TimeOutSFCrawler" ]

class TimeOutSFCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "TimeOutSF", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)

        #Include restaurant and bars list separately 
        href = [
            'http://www.timeout.com/san-francisco/search/tag/4256/restaurants-cafes',
            'http://www.timeout.com/san-francisco/search/tag/4298/bars-pubs'
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
        
        results = soup.find('div', { 'class' : 'split-right-column' }).findAll('div', { 'class' : 'clear' })
        
        for result in results:
            
            try:
                name = result.findNext('div').find('h2').find('a').getText().strip()
            except Exception:
                continue

            try:
                street = result.findNext('div').find('address').getText()
                locale = '{0}, {1}'.format('San Francisco', 'CA')
                addr = '{0}, {1}'.format(street, locale)
            except Exception:
                addr = ''
                continue 
            
            if addr == '':
                continue
                
            if name == '':
                continue 
            
            if (name, addr) in self._seen:
                continue
            
            self._seen.add((name, addr))
            entity = Entity()
            if 'Bars' in result.findNext('span').getText():
                entity.subcategory = "bar"
            else:  
                entity.subcategory = "restaurant"
            
            entity.title   = name
            entity.address = addr
            entity.sources.timeout_sf = { }
            
            self._output.put(entity)
        
        # try the next page
        try: 
            href_get = soup.find('div', { 'class' : 'next' }).find('a').get('href')
            next_page = '{0}{1}'.format('http://www.timeout.com', href_get)
        except Exception: 
            next_page = ''
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('timeout_sf', TimeOutSFCrawler)

