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

__all__ = [ "BostonMagCrawler" ]

class BostonMagCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "BostonMag", self.TYPES, 512)
        self._seen = set()
    
    def getMaxNumEntities(self):
        return 1000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://www.bostonmagazine.com/restaurants/find_restaurant/index.html'
        
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
            results = soup.find('span', { 'class' : 'header' }).findNext('div').findAll('a')
        except AttributeError:
            utils.log("[%s] error parsing %s (%s)" % (self, results, href))
        
        root = 'http://www.bostonmagazine.com'
        
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
        
        results = soup.find('div', { 'id' : 'searchResults' }).findAll('td', { 'class' : 'start' })
        
        for result in results:
            
            try:
                name = result.find('a').getText().strip()
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, name, href))
                return
                
            x = 0 
            
            for r in result.findAll('br'):
                x+=1
            
            if x == 3: 
                try:
                    addr = '{0}, {1}'.format(result.find('a').nextSibling.strip(), result.find('br').nextSibling.strip())
                except Exception:
                    utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                    return
                    
            elif x == 4:
                try:
                    addr = '{0}, {1}'.format(result.contents[3].strip(), result.contents[5].strip())
                except Exception:
                    utils.log("[%s] error parsing %s (%s)" % (self, addr, href))
                    return 
                    
            else: 
                addr = ''
            
            if addr == '':
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
            entity.sources.bostonmag = { }
            
            self._output.put(entity)
        
        # try the next page
        next_page_ending = soup.find('div', { 'class' : 'right_align' }).findAll('a')
        next_page = ''
        
        for n in next_page_ending: 
            if 'Next' in str(n):
                next_page = href.replace(href[href.find('?'):], n.get('href'))
            else:
                pass
        
        if next_page != '':
            pool.spawn(self._parseResultsPage, pool, next_page)

from crawler import EntitySources
EntitySources.registerSource('bostonmag', BostonMagCrawler)

