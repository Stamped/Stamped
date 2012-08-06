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

__all__ = [ "SFWeeklyCrawler" ]

class SFWeeklyCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "SFWeekly", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://www.sfweekly.com/directory/club/'
        
        self._parseResultsPage(pool, seed)
            
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.find('div', { 'name' : 'LocationDirectory' }).findAll('h3')
        
        for result in results:
            
            try:
                name = result.find('a').getText().strip()
            except Exception:
                continue

            try:
                raw_address = result.findNext('span', { 'class' : 'address'}).getText()
                street = raw_address[0:raw_address.find('(')].strip()
                locale = raw_address[raw_address.find(')')+1:raw_address.find('CA')+2].strip()
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
            entity.subcategory = "bar"
            entity.title   = name
            entity.address = addr
            entity.sources.sfweekly = { }
            
            self._output.put(entity)
        
        # try the next page
        try: 
            pagination = soup.find('span', { 'class' : 'Pagination' }).getText()
            if 'Next' in pagination:
                pagination = soup.find('span', { 'class' : 'Pagination' })
                href_get = pagination.find('span', { 'class' : 'PaginationSelected' }).findNext('a').get('href')
                next_page = '{0}{1}'.format('http://www.sfweekly.com', href_get)
            else: 
                next_page = '' 
        except Exception: 
            next_page = ''
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('sfweekly', SFWeeklyCrawler)

