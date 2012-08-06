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

__all__ = [ "ChicagoMagCrawler" ]

class ChicagoMagCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "ChicagoMag", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://www.chicagomag.com/Chicago-Magazine/Dining/Dining-Guide/index.php/cp/1/'
        
        self._parseResultsPage(pool, seed)
            
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.find('td', { 'id' : 'search-results' }).findAll('tr')
        
        for result in results:
            
            try:
                name = result.find('td', { 'class' : 'business-name' }).find('a').getText().strip()
            except Exception:
                continue

            try:
                result.find('td', { 'class' : 'contact' }).find('br').previousSibling.strip()
                result.find('td', { 'class' : 'contact' }).find('br').nextSibling.strip()
                addr = '{0}, {1}'.format(result.find('td', { 'class' : 'contact' }).find('br').previousSibling.strip(), result.find('td', { 'class' : 'contact' }).find('br').nextSibling.strip())
            except Exception:
                addr = ''
                utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                continue
            
            if 'OPENING SOON' in result.find('td', { 'class' : 'categories' }).getText(): 
                continue
            
            if addr == '':
                continue
                
            if name == '':
                continue 
            
            if 'CLOSED' in name:
                continue
            
            if (name, addr) in self._seen:
                continue
            
            self._seen.add((name, addr))
            
            entity = Entity()
            entity.subcategory = "restaurant"
            entity.title   = name
            entity.address = addr
            entity.sources.chicagomag = { }
            
            self._output.put(entity)
        
        # try the next page
        next_page_all= soup.find('div', { 'id' : 'pager' }).findAll('a')
        next_page = ''
        
        for n in next_page_all: 
            if 'Next' in n.getText():
                next_page = n.get('href')
            else:
                pass
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('chicagomag', ChicagoMagCrawler)

