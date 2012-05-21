#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import feedparser, gevent, os, re

from AEntitySource import AExternalDumpEntitySource
from BeautifulSoup import BeautifulSoup
from api.Schemas   import Entity
from pprint        import pprint
from gevent.pool   import Pool

__all__ = [ "AmazonBookFeed" ]

class AmazonBookFeed(AExternalDumpEntitySource):
    """
        Amazon RSS feed importer
    """
    
    TYPES = set([ 'book' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, "Amazon", self.TYPES, 512)
        self.seen = set()
        
        self.title_re   = re.compile('#([0-9])*: (.*)')
        self.id_re      = re.compile('.*_([0-9A-Za-z]*)')
        self.author_re0 = re.compile('by (.*)')
        self.author_re1 = re.compile('(.*) \(Author\)')
    
    def getMaxNumEntities(self):
        return 1000 # approximation for now
    
    def _run(self):
        filename = 'amazon_feeds.txt'
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        feed_file = file(path, 'r')
        feeds = map(lambda t: t[0:-1], feed_file.readlines())
        feed_file.close()
        
        num_feeds = len(feeds)
        utils.log("[%s] parsing %d feeds" % (self, num_feeds))
        
        pool = Pool(128)
        
        for i in xrange(num_feeds):
            url = feeds[i]
            pool.spawn(self._parse_feed, pool, url)
            
            if num_feeds > 100 and (i % (num_feeds / 100)) == 0:
                utils.log("[%s] done parsing %s" % (self, utils.getStatusStr(i, num_feeds)))
        
        pool.join()
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d feeds" % (self, num_feeds))
    
    def _parse_feed(self, pool, url):
        utils.log("[%s] parsing feed %s" % (self, url))
        data = feedparser.parse(url)
        
        for entry in data.entries:
            try:
                entity = Entity()
                entity.subcategory = "book"
                entity.amazon = {}
                
                asin = self.id_re.match(entry.id).groups()[0]
                
                # note: every valid amazon standard identification number is exactly 10 digits long
                if 10 == len(asin):
                    entity.asin = asin
                else:
                    continue
                
                title_match = self.title_re.match(entry.title)
                if title_match:
                    title_match = title_match.groups()
                    entity.title = title_match[1]
                    entity.popularity = title_match[0]
                else:
                    entity.title = entry.title
                
                entity.amazon_link = entry.link
                
                soup = BeautifulSoup(entry.summary)
                img  = soup.find('img')
                if img:
                    entity.image = img.get('src')
                
                author = soup.find('span', {'class' : 'riRssContributor'})
                if author:
                    author_link = author.find('a')
                    
                    if author_link:
                        entity.author = author_link.getText()
                    else:
                        author = author.getText().strip()
                        
                        try:
                            entity.author = self.author_re0.match(author).groups()[0]
                        except AttributeError:
                            try:
                                entity.author = self.author_re1.match(author).groups()[0]
                            except AttributeError:
                                entity.author = author
                                pass
                
                #pprint(entity)
                #self._globals['books'] = entry
                
                if asin in self.seen:
                    continue
                
                self.seen.add(asin)
                self._output.put(entity)
            except:
                utils.printException()
                #print soup.prettify()
        
        #utils.log("[%s] done parsing feed '%s' (%s)" % (self, data.feed.title, url))

import EntitySources
EntitySources.registerSource('amazonbookfeed', AmazonBookFeed)

