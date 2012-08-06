#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from datetime      import datetime, timedelta
from gevent.pool   import Pool
from gevent.queue  import Queue
from crawler.AEntitySource import AExternalEntitySource
from Schemas       import Entity

__all__ = [ "NYTimesBestSellerCrawler" ]

class NYTimesBestSellerCrawler(AExternalEntitySource):
    """ 
        Entity crawler which parses all of the NYTimes best seller books.
    """
    
    TYPES = set([ 'book' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "NYTimesBestSellers", self.TYPES, 512)
        self.base = 'http://www.nytimes.com'
        self.seen = set()
        
        self.details_re = re.compile('.*___by ([^(]*)\. \(([^)]*)\) (.*)')
        self.date_re    = re.compile('.*/(\d\d\d\d)-(\d\d)-(\d\d)/.*')
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        queue = Queue()
        pool  = Pool(64)
        seed  = 'http://www.nytimes.com/best-sellers-books/'
        
        pool.spawn(self._parseResultsPage, pool, queue, seed, 'current', True)
        
        while True:
            items = []
            
            while not queue.empty():
                item = queue.get_nowait()
                items.append(item)
            
            if 0 == len(items) and 0 == len(pool):
                break
            
            for item in items:
                pool.spawn(item[0], pool, queue, item[1], item[2], item[3])
            
            time.sleep(0.01)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseResultsPage(self, pool, queue, url, name, base=False):
        utils.log('[%s] parsing results page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        #self._globals['books'] = soup
        
        # extract and parse more past results
        if base:
            prev = soup.find('div', {'class' : 'stepperDynamicPrevSm'})
            
            if prev:
                prev = prev.find('a')
                href = prev.get('href')
                
                year, month, day = map(int, self.date_re.match(href).groups())
                date  = datetime(year=year, month=month, day=day)
                delta = timedelta(days=7)
                count = 10
                
                for i in xrange(count):
                    repl  = date.date().isoformat()
                    href2 = re.sub('\d\d\d\d-\d\d-\d\d', repl, href)
                    queue.put_nowait((self._parseResultsPage, href2, repl, i == count - 1))
                    
                    date = date - delta
        
        categories = soup.findAll('div', {'class' : re.compile('bookCategory')})
        for category in categories:
            link  = category.find('a')
            href  = link.get('href')
            name2 = "%s (%s)" % (name, link.getText().strip().lower())
            
            queue.put_nowait((self._parseListPage, href, name2, False))
    
    def _parseListPage(self, pool, queue, url, name, base=False):
        utils.log('[%s] parsing list page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        results = soup.findAll('td', {'class' : 'summary'})
        
        for result in results:
            entity = Entity()
            entity.subcategory = "book"
            entity.nytimes = {}
            
            title = result.find('span', {'class' : 'bookName'}).getText().strip().title()
            if title.endswith(','):
                title = title[0:-1]
            
            entity.title = title
            
            details = result.getText(separator='___')
            details_match = self.details_re.match(details)
            
            if details_match:
                details_match    = details_match.groups()
                entity.author    = details_match[0]
                entity.publisher = details_match[1]
                entity.desc      = details_match[2]
            
            key = (entity.title, entity.author)
            if key in self.seen:
                continue
            
            self.seen.add(key)
            self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('nytimesbooks', NYTimesBestSellerCrawler)

