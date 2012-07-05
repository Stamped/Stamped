#!/usr/bin/env python

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

__all__ = [ "SeattleTimesCrawler" ]

class SeattleTimesCrawler(AExternalEntitySource):
    """ 
        Entity crawler which parses all of the SeattleTimes restaurants.
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "SeattleTimes", self.TYPES, 512)
        self.base = 'http://www.seattletimes.com'
        self.seen = set()
        
        self.page_re = re.compile('.*&page=([0-9]*)')
    
    def getMaxNumEntities(self):
        return 2000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        queue = Queue()
        pool  = Pool(64)
        seed  = 'http://community.seattletimes.nwsource.com/entertainment/i_results.php?search=venue&type=Restaurant&page=1'
        
        pool.spawn(self._parseResultsPage, pool, queue, seed, '1', True)
        
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
            html = utils.getFile(url)
            html = html.replace('{"typeFilterHTML":"', '')[0:-2].replace('\\', '')
            soup = BeautifulSoup(html)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        #self._globals['books'] = soup
        
        results = soup.findAll('div', {'class' : 'ev_result_block'})
        if 0 == len(results):
            return
        
        # extract and parse the rest of the paginated results
        if base:
            num_pages = 16
            page = int(self.page_re.match(url).groups()[0])
            url2 = url[0:url.find('&page=')]
            
            for i in xrange(1, num_pages):
                cur_page = page + i
                cur_url  = "%s&page=%d" % (url2, cur_page)
                name2    = "page %d" % cur_page
                
                queue.put_nowait((self._parseResultsPage, cur_url, name2, i == num_pages - 1))
        
        for result in results:
            link  = result.find('a')
            href  = link.get('href')
            name2 = link.getText().strip()
            
            queue.put_nowait((self._parseRestaurantPage, href, name2, False))
    
    def _parseRestaurantPage(self, pool, queue, url, name, base=False):
        utils.log('[%s] parsing restaurant page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            #utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        content = soup.find('div', { 'id' : 'content'})
        
        if content is None:
            return
        
        entity = Entity()
        entity.title = content.find('h1').getText()
        entity.subcategory = "restaurant"
        entity.seattletimes = {}
        
        details = content.find('div', {'id' : 'edbtext'})
        desc    = details.find('p').getText()
        if desc is not None:
            entity.desc = desc
        
        details = details.findAll('p', {'class' : 'list'})
        address = details[0].renderContents().strip().replace('<br />', '')
        address = re.sub('[ \n\t]+', ' ', address)
        entity.address = address
        
        if len(details) > 1:
            site = details[1].get('href')
            if site is not None:
                entity.site = site
        
        if len(details) > 2:
            hoursOfOperation = details[2].getText()
            if hoursOfOperation is not None:
                entity.hoursOfOperation = hoursOfOperation
        
        key = (entity.title, entity.address)
        if key in self.seen or '(closed)' in entity.title.lower():
            return
        
        self.seen.add(key)
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('seattletimes', SeattleTimesCrawler)

