#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import feedparser, gevent, os, re

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from Schemas import Entity

__all__ = [ "FandangoFeed" ]

class FandangoFeed(AExternalDumpEntitySource):
    """
        Fandango RSS feed importer
    """
    
    NAME = "Fandango"
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 128)
        self.seen = set()
    
    def getMaxNumEntities(self):
        return 100 # approximation for now
    
    def _run(self):
        feeds = [
            'http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839&a=12170', 
            'http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839&a=12169', 
            'http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839&a=12168', 
        ]
        
        pool = Pool(128)
        
        for url in feeds:
            pool.spawn(self._parse_feed, pool, url)
        
        pool.join()
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d feeds" % (self, len(feeds)))
    
    def _parse_feed(self, pool, url):
        utils.log("[%s] parsing feed %s" % (self, url))
        
        data = feedparser.parse(url)
        id_r = re.compile('.*\/([0-9]*)$')
        title_r = re.compile('^([0-9][0-9]?). (.*) \$[0-9.M]*')
        
        for entry in data.entries:
            if entry.title == 'More Movies':
                continue
            
            fid_match = id_r.match(entry.id)
            assert fid_match is not None
            fid = fid_match.groups()[0]
            
            if fid in self.seen:
                continue
            
            self.seen.add(fid)
            
            title = entry.title
            
            title_match = title_r.match(title)
            fandango_rank = None
            
            if title_match:
                title_match_groups = title_match.groups()
                fandango_rank = title_match_groups[0]
                title = title_match_groups[1]
            
            entity = Entity()
            entity.subcategory = "movie"
            entity.title = title
            
            entity.desc = entry.summary
            entity.fid = fid
            
            for link in entry.links:
                if 'image' in link.type:
                    entity.image = link.href
                    break
            
            self._output.put(entity)
        
        utils.log("[%s] done parsing feed '%s' (%s)" % (self, data.feed.title, url))

import EntitySources
EntitySources.registerSource('fandango', FandangoFeed)

