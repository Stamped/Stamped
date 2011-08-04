#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from AEntitySource import AExternalEntitySource
from api.Entity import Entity

__all__ = [ "NYMagCrawler" ]

class NYMagCrawler(AExternalEntitySource):
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "NYMag", self.TYPES, 512)
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = 'http://nymag.com/srch?t=restaurant&No=0&N=265+69'
        
        self._parseResultsPage(pool, seed)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing page %s" % (self, href))
            return
        results = soup.find("table", {"id" : "resultsFound"}).findAll("dl", {"class" : "result"})
        
        try:
            next_page = soup.find("ul", {"class" : re.compile("nextpages|morepages")}).find("li", {"class" : "next"}).find("a").get("href")
            if len(next_page) > 5:
                pool.spawn(self._parseResultsPage, pool, next_page)
        except AttributeError:
            # crawling of pages is done
            #utils.log("Done crawling: %s" % href)
            pass
        
        time.sleep(0.01)
        
        for result in results:
            link = result.find("dt").find("a")
            href = link.get("href")
            name = link.getText()
            
            detail = pool.spawn(self._parseDetailPage, name, href)
    
    def _parseDetailPage(self, name, href):
        try:
            soup = utils.getSoup(href)
        except urllib2.HTTPError:
            utils.log("[%s] error parsing %s (%s)" % (self, name, href))
            return
        
        summ = soup.find('div', {'class' : 'summary-address'})
        
        try:
            addrp = summ.find('p', {'class' : 'adr'})
            
            street_addr = addrp.find('span', {'class' : 'street-address'}).getText().strip()
            locality    = addrp.find('span', {'class' : 'locality'}).getText().strip()
            region      = addrp.find('span', {'class' : 'region'}).getText().strip()
            
            try:
                postal_code = addrp.find('span', {'class' : 'postal-code'}).getText().strip()
            except AttributeError:
                postal_code = ""
            
            addr = "%s, %s, %s %s" % (street_addr, locality, region, postal_code)
        except AttributeError:
            try:
                p = summ.find('p').getText()
                r = re.compile('(.*)nr\. ', re.DOTALL)
                m = r.match(p)
                
                if m is None:
                    r = re.compile('(.*)at[. ]', re.DOTALL)
                    m = r.match(p)
                
                addr = m.groups()[0].replace('\n', ' ').strip()
            except AttributeError:
                utils.log("[%s] error parsing %s (%s)" % (self, name, href))
                return
        
        entity = Entity()
        entity.subcategory = "restaurant"
        entity.title   = name
        entity.address = addr
        entity.sources = {
            'nymag' : { }
        }
        
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('nymag', NYMagCrawler)

