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

__all__ = [ "TimeOutChiCrawler" ]

class TimeOutChiCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "TimeOutChi", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)

        #Include restaurant and bars list separately 
        href = [
            'http://timeoutchicago.com/search/apachesolr_search?source_form=bars&filters=type%3Avenue%20im_vid_291%3A36696',
            'http://timeoutchicago.com/search/apachesolr_search?source_form=restaurants&filters=type%3Avenue%20im_vid_291%3A36695'
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
        
        results = soup.find('div', { 'class' : 'search-results apachesolr_search-results' }).findAll('div', { 'class' : 'search-snippet-item' })
        
        for result in results:
            
            try:
                name = result.find('a').getText().strip()
            except Exception:
                continue

            try:
                street = result.findNext('span', { 'class' : 'street-address' }).getText().strip()
                addr = '{0}, {1}'.format(street, 'Chicago, IL')
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
            if 'Bars' in result.find('span', { 'class' : 'taxonomy' }).getText():
                entity.subcategory = "bar"
            else:  
                entity.subcategory = "restaurant"
            
            entity.title   = name
            entity.address = addr
            entity.sources.timeout_chi = { }
            
            self._output.put(entity)
        
        # try the next page
        try: 
            href_get = soup.find('li', { 'class' : 'pager-next last' }).find('a').get('href')
            next_page = '{0}{1}'.format('http://www.timeoutchicago.com', href_get)
        except Exception: 
            next_page = ''
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('timeout_chi', TimeOutChiCrawler)

