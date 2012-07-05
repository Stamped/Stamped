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

__all__ = [ "SFMagCrawler" ]

class SFMagCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "SFMag", self.TYPES, 512)
    
    def getMaxNumEntities(self):
        return 250 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://www.sanfranmag.com/modules/ajax-search/search.php?searchtype=restaurant&searchterms=111,112,113,114,117,121,123,125,126,133,134,131,132,139,141,145,148,153,155,156,157,158,159,160,162,166,169,171,170,172,173,179,184,185,186,187,188,189,191,193,194,196,197,198,203,204,205,206,215,217,218,219,221,223,224,225,227,228,229,230,234,235,237,239&and_searchterms=&neighborhoods=75,76,77,78,79,80,362,81,82,363,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,73,102,103,105,375,74,106,107,108,410,411,412&page=0&keyword='
        
        self._parseResultsPage(pool, seed)
        	
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        
        results = soup.findAll('h3')
        for result in results:
            try:
                name = result.find('span', { 'style' : 'cursor:pointer;' }).getText().strip()
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, name, href))
                return
            
            try:
                address1 = result.findNext('span', { 'class' : 'addresslinecaps' }).getText().strip()
                if '(' in address1:
                    # sf mag does not provide any city, state or zip information, 
                    # so inserting basic universal info manually.
                    addr = '{0}, {1}'.format(address1.split('(')[0].strip(), 'San Francisco, CA')
                else: 
                    addr = '{0}, {1}'.format(address1, 'San Francisco, CA') 
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                return
            
            entity = Entity()
            entity.subcategory = "restaurant"
            entity.title   = name
            entity.address = addr
            entity.sources.sfmag = { }
            
            self._output.put(entity)
        
        #locate total pages and compare against current page num to determine if we should iterate again
        try:
            total_pages = soup.find('span', { 'class' : 'last' }).findPrevious('span').getText().strip()
        except AttributeError:
            # crawling of pages is done
            return
        
        index = href.find('&page=')
        end = href.find('&keyword')
        page = href[index+6:end]
        
        if int(page) <= int(total_pages)-1:
            next_page = href.replace('&page=' + str(page), '&page=' + str(int(page)+1))
            pool.spawn(self._parseResultsPage, pool, next_page)
        else:
            return
        
        time.sleep(0.01)

from crawler import EntitySources
EntitySources.registerSource('sfmag', SFMagCrawler)

