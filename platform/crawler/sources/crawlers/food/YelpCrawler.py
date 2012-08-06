#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "YelpCrawler" ]

# TODO: crawler cutting out after seemingly indeterminate amount of time; why?
# NOTE: root cause resolved to gevent.Pool deadlock; example workaround in AmazonBestSellerBookFeeds

class YelpCrawler(AExternalEntitySource):
    """ 
        Entity crawler which exhaustively outputs all of the (high quality) 
        Yelp-rated restaurants from Yelp.com.
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "Yelp", self.TYPES, 512)
        self.base = 'http://www.yelp.com'
        
        self.title_re          = re.compile('[0-9]*\. (.*)')
        self.address_re        = re.compile('([^_]*)___*([^_]*)___*([^_]*)_*')
        self.rating_reviews_re = re.compile('([0-9.]*) .*')
        self.start_re          = re.compile('.*start=([0-9]*).*')
        self.category_re       = re.compile('refine_category_.*')
        self.results_per_page  = 40
        
        self.seen = set()
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        pool = Pool(64)
        seed = 'http://www.yelp.com/search?cflt=restaurants&find_desc=&find_loc=New+York%2C+NY&rpp={0}&sortby=rating&start=0'.format(self.results_per_page)
        
        # parse the top-level page containing links to all regions (states for the US)
        self._parseResultsPage(pool, seed, offset=0, base=True)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, url, offset=0, base=False):
        utils.log('[%s] parsing page %s' % (self, url))
        max_offset = 8
        
        if offset < max_offset:
            # optimistically process the next results page before processing this one
            if 'start=' in url:
                start = self.start_re.match(url).groups()[0]
                nexti = int(start) + self.results_per_page
                url2  = url.replace('start=%s' % start, 'start=%d' % nexti)
            else:
                url2  = "%s&start=%d" % (url, self.results_per_page)
            
            pool.spawn(self._parseResultsPage, pool, url2, offset + 1)
        
        try:
            soup = utils.getSoup(url)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, url))
            return
        
        if offset >= max_offset:
            next_pagel = soup.find('a', {'id' : 'pager_page_next'})
            
            if next_pagel is not None:
                href = self.base + next_pagel.get('href')
                pool.spawn(self._parseResultsPage, pool, href, 0)
                time.sleep(0.01)
        
        if base:
            categories = soup.findAll('a', {'id' : self.category_re})
            
            if categories is not None:
                for category in categories:
                    href = self.base + category.get('href')
                    pool.spawn(self._parseResultsPage, pool, href, 0)
                
                # yield so other threads have a chance to start working
                time.sleep(0.01)
        
        separator = '___'
        results   = soup.findAll('div', {'class' : re.compile('businessresult')})
        
        if results is None:
            return
        
        for result in results:
            entity = Entity()
            entity.subcategory = 'restaurant'
            entity.sources.yelp = { }
            
            titlel = result.find('a')
            title  = titlel.getText()
            entity.title = self.title_re.match(title).groups()[0]
            entity.yurl  = self.base + titlel.get('href')
            
            addr   = result.find('address').getText(separator)
            match  = self.address_re.match(addr).groups()
            
            entity.address = "%s, %s" % (match[0], match[1])
            entity.phone = match[2]
            
            rating = result.find('img')
            if rating is not None:
                entity.yrating = float(self.rating_reviews_re.match(rating.get('title')).groups()[0])
            
            reviews = result.find('span', {'class' : 'reviews'})
            if reviews is not None:
                entity.yreviews = int(self.rating_reviews_re.match(reviews.getText()).groups()[0])
            
            key = (entity.title, entity.address)
            if key not in self.seen:
                self.seen.add(key)
                self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('yelp', YelpCrawler)

