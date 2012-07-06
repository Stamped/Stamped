#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "LATimesCrawler" ]

class LATimesCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "LATimes", self.TYPES, 512)
        self._count = {}
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 15000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://findlocal.latimes.com/categories/restaurants'
        
        for l in self._parseDirectoryPage(pool, seed):
            pool.spawn(self._parseResultsPage, pool, l)
            
        pool.join()
        self._output.put(StopIteration)
    
    def _parseDirectoryPage(self,pool,href):
    
        try: 
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        try: 
            results = soup.find('div', { 'class' : 'module_content clearfix' }).findAll('a')
            
        except AttributeError:
            utils.log("[%s] error parsing %s (%s)" % (self, results, href))
            
        root = 'http://findlocal.latimes.com'
        
        href_list = []
        
        for r in results: 
            link = "{0}{1}".format(root, r.get('href'))
            href_list.append(link)
        
        return href_list
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.find('ul', { 'id' : 'search_pagination' }).findAll('div', { 'class' : 'listing_item' })
        
        for result in results:
            try:
                name = result.find('h2').getText().strip()
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, name, href))
                return
            
            try:
                addr = result.find('span', { 'class' : 'address' }).getText().strip()
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                return
            
            if addr == '':
                continue 
                
            if 'CLOSED' in name:
                continue
            
            if addr in self._seen:
                continue
                
            self._seen.add(addr)
            
            if name in self._count:
                if self._count[name] < 3:
                    self._count[name] = self._count[name] + 1 
                else: 
                    continue
            
            else:   
                self._count[name] = 1 
        
            entity = Entity()
            entity.subcategory = "restaurant"
            entity.title   = name
            entity.address = addr
            entity.sources.latimes = { }
            
            self._output.put(entity)
        
        #try the next page
        
        try:
            next_page = soup.find('a', {'class': 'next_page'}).get("href")
            if next_page != '':
                next_page_url = "{0}{1}".format('http://findlocal.latimes.com', next_page)
                pool.spawn(self._parseResultsPage, pool, next_page_url)
        except AttributeError:
            # crawling of pages is done
            #utils.log("Done crawling: %s" % href)
            pass

from crawler import EntitySources
EntitySources.registerSource('latimes', LATimesCrawler)

