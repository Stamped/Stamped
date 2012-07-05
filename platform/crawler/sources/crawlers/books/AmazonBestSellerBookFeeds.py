#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from gevent.pool   import Pool
from gevent.queue  import Queue
from crawler.AEntitySource import AExternalEntitySource
from Schemas       import Entity

__all__ = [ "AmazonBestSellerBookFeeds" ]

class AmazonBestSellerBookFeeds(AExternalEntitySource):
    """ 
        Entity crawler which extracts all of the Amazon bestseller RSS feeds.
    """
    
    TYPES = set([ 'book' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "AmazonBestSellerBookFeeds", self.TYPES, 512)
        self.base = 'http://www.nytimes.com'
        self.seen = set()
        self.max_depth = 2
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        queue = Queue()
        pool  = Pool(32)
        seed  = 'http://www.amazon.com/best-sellers-books-Amazon/zgbs/books/'
        parsed = set()
        
        queue.put_nowait((seed, 'seed', 0))
        
        while True:
            items = []
            
            while not queue.empty():
                item = queue.get_nowait()
                if item[0] not in parsed:
                    items.append(item)
                    parsed.add(item[0])
            
            if 0 == len(items) and 0 == len(pool):
                break
            
            for item in items:
                pool.spawn(self._parseResultsPage, queue, item[0], item[1], item[2])
            
            time.sleep(0.01)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, queue, url, name, depth):
        #utils.log('[%s] parsing page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        if depth < self.max_depth:
            # extract and parse subcategory pages
            category_ul = soup.find('ul', {'id' : 'zg_browseRoot'})
            
            if category_ul is not None:
                while True:
                    temp_ul = category_ul.find('ul')
                    if temp_ul is None:
                        break
                    else:
                        category_ul = temp_ul
                
                categories = category_ul.findAll('a')
                
                for category in categories:
                    href = category.get('href')
                    name = utils.normalize(category.getText())
                    
                    queue.put_nowait((href, name, depth + 1))
        
        self._globals['books'] = soup
        
        rss_link = soup.find('div', {'id' : 'zg_rssLinks'})
        if rss_link is None:
            return
        
        rss_link = rss_link.findAll('a')[1].get('href')
        if rss_link in self.seen:
            return
        
        self.seen.add(rss_link)
        
        entity = Entity()
        entity.title = rss_link
        entity.subcategory = 'book'
        
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('amazonbestsellerbookfeeds', AmazonBestSellerBookFeeds)

