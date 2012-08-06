#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import feedparser, gevent, os, re

from gevent.pool import Pool
from crawler.AEntitySource import AExternalDumpEntitySource
from api.Schemas import BasicEntity

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
        
        id_r      = re.compile('.*\/([0-9]*)$')
        title_r   = re.compile('^([0-9][0-9]?). (.*) \$[0-9.M]*')
        info_re   = re.compile('[A-Za-z]+ ([^|]+) \| Runtime:(.+)$')
        genre_re  = re.compile('Genres:(.*)$')
        length_re = re.compile('([0-9]+) *hr. *([0-9]+) min.')
        
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
            
            entity = BasicEntity()
            entity.subcategory = "movie"
            entity.title = title
            
            entity.desc = entry.summary
            entity.fid = fid
            
            for link in entry.links:
                if 'image' in link.type:
                    # fandango gives us low resolution 69x103 versions of the image, so hackily up the 
                    # resolution before saving the entity :)
                    entity.image = link.href.replace('69/103', '375/375').replace('69x103', '375x375')
                    break
            
            # TODO: test f_url
            entity.f_url = "%s" % entry.link
            entity.f_url = entity.f_url.replace('%26m%3d', '%3fpid=5348839%26m%3d')
            #print "LINK: %s" % entry.link
            #break
            
            # attempt to scrape some extra details from fandango's movie page
            url = "http://www.fandango.com/%s_%s/movieoverview" % \
                   (filter(lambda a: a.isalnum(), entity.title.replace(' ', '')), entity.fid)
            
            try:
                utils.log(url)
                soup = utils.getSoup(url)
                info = soup.find('div', {'id' : 'info'}).findAll('li')[1].getText()
                
                try:
                    open_date, runtime = info_re.match(info).groups()
                    entity.original_release_date = open_date
                    
                    match = length_re.match(runtime)
                    if match is not None:
                        hours, minutes = match.groups()
                        hours, minutes = int(hours), int(minutes)
                        seconds = 60 * (minutes + 60 * hours)
                        
                        entity.track_length = str(seconds)
                except:
                    utils.printException()
                    pass
                
                try:
                    mpaa_rating = soup.find('div', {'class' : re.compile('rating_icn')}).getText()
                    entity.mpaa_rating = mpaa_rating
                except:
                    pass
                
                details = soup.findAll('li', {'class' : 'detail_list'})
                
                cast = filter(lambda d: 'Cast:' in d.getText(), details)
                if 1 == len(cast):
                    cast = map(lambda a: a.getText(), cast[0].findAll('a'))
                    entity.cast = ', '.join(cast)
                
                director = filter(lambda d: 'Director:' in d.getText(), details)
                if 1 == len(director):
                    director = map(lambda a: a.getText(), director[0].findAll('a'))
                    entity.director = ', '.join(director)
                
                genres = filter(lambda d: 'Genres:' in d.getText(), details)
                if 1 == len(genres):
                    genres = genres[0].getText()
                    match  = genre_re.match(genres)
                    
                    if match is not None:
                        entity.genre = match.groups()[0].strip()
            except:
                utils.printException()
                pass
            
            self._output.put(entity)
        
        utils.log("[%s] done parsing feed '%s' (%s)" % (self, data.feed.title, url))

from crawler import EntitySources
EntitySources.registerSource('fandango', FandangoFeed)

