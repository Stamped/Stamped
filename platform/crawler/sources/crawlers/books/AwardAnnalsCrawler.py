#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from BeautifulSoup import BeautifulSoup
from gevent.pool   import Pool
from gevent.queue  import Queue
from crawler.AEntitySource import AExternalEntitySource
from Schemas       import Entity

__all__ = [ "AwardAnnalsCrawler" ]

class AwardAnnalsCrawler(AExternalEntitySource):
    """ 
        Entity crawler which parses all of the AwardAnnals books.
    """
    
    TYPES = set([ 'book' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "AwardAnnals", self.TYPES, 512)
        self.base = 'http://www.awardannals.com'
        self.seen = set()
        
        self.page_re = re.compile('Page 1 of ([0-9]*)')
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        queue = Queue()
        pool  = Pool(16)
        seed  = 'http://www.awardannals.com/skin/menubar81.html'
        
        pool.spawn(self._parseIndexPage, pool, queue, seed, 'index')
        
        while True:
            items = []
            
            while not queue.empty():
                item = queue.get_nowait()
                items.append(item)
            
            if 0 == len(items) and 0 == len(pool):
                break
            
            for item in items:
                pool.spawn(self._parseResultsPage, pool, queue, item[0], item[1], False)
            
            time.sleep(0.01)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseIndexPage(self, pool, queue, url, name):
        utils.log('[%s] parsing page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        categories = soup.find('div', {'id' : 'bookgenremenu'}).findAll('a')
        for category in categories:
            href = self.base + category.get('href')
            name = category.getText().strip()
            
            pool.spawn(self._parseResultsPage, pool, queue, href, name, base=True)
    
    def _parseResultsPage(self, pool, queue, url, name, base=False):
        utils.log('[%s] parsing page %s (%s)' % (self, name, url))
        
        try:
            html = utils.getFile(url)
            html = html.replace("header>", "div>") 
            soup = BeautifulSoup(html)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        # extract and parse the rest of the paginated results
        if base:
            page = soup.find('nav').find('span').getText()
            num_pages = int(self.page_re.match(page).groups()[0])
            
            for i in xrange(2, num_pages + 1):
                href = '%s&pg=%d' % (url, i)
                
                queue.put_nowait((href, name))
        
        results = soup.findAll('section', {'class' : 'CWListing'})
        
        for result in results:
            entity = Entity()
            entity.subcategory = "book"
            entity.awardAnnals = {}
            
            entity.title  = result.find('h4').find('a').getText().strip()
            entity.author = result.find('p', {'class' : 'creators'}).getText()
            
            key = (entity.title, entity.author)
            if key in self.seen:
                continue
            
            self.seen.add(key)
            self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('awardannals', AwardAnnalsCrawler)

