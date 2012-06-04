#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import feedparser, gevent, os, re

from datetime       import datetime
from optparse       import OptionParser
from libs.LibUtils  import parseDateString
from api.Schemas    import *

__all__ = [ "Fandango" ]

class Fandango(object):
    """ Fandango RSS feed importer """
    
    def __init__(self, verbose = False):
        self._verbose = verbose
    
    def get_coming_soon_movies(self):
        return self._parse_feed('http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839&a=12170')
    
    def get_opening_this_week_movies(self):
        return self._parse_feed('http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839&a=12169')
    
    def get_top_box_office_movies(self):
        return self._parse_feed('http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839&a=12168')
    
    def _parse_feed(self, feed_url):
        if self._verbose:
            utils.log("[%s] parsing feed %s" % (self, feed_url))
        
        data = feedparser.parse(feed_url)
        
        id_r      = re.compile('.*\/([0-9]*)$')
        title_r   = re.compile('^([0-9][0-9]?). (.*) \$[0-9.M]*')
        genre_re  = re.compile('Genres:(.*)$')
        length_re = re.compile('([0-9]+) *hr. *([0-9]+) min.')
        
        info_res  = [
            re.compile('[A-Za-z]+ ([^|]+) \| Runtime:(.+)$'), 
            re.compile('Opens [A-Za-z]+ ([^|]+) \| Runtime:(.+)$'), 
            re.compile('Opens [A-Za-z]+ ([^|]+) *$'), 
        ]
        
        output    = []
        source    = "fandango"
        ts        = datetime.utcnow()
        
        def _set_entity(entity, key, value):
            setattr(entity, key, value)
            try:
                setattr(entity, "%s_source" % key, source)
            except AttributeError:
                pass
            
            try:
                setattr(entity, "%s_timestamp" % key, ts)
            except AttributeError:
                pass
        
        for entry in data.entries:
            if entry.title == 'More Movies':
                continue
            
            fid_match = id_r.match(entry.id)
            assert fid_match is not None
            fid = fid_match.groups()[0]
            
            title = entry.title
            
            title_match = title_r.match(title)
            fandango_rank = None
            
            if title_match:
                title_match_groups = title_match.groups()
                fandango_rank = title_match_groups[0]
                title = title_match_groups[1]
            
            entity = MediaItemEntity()

            setattr(entity.sources, "fandango_id", fid)
            setattr(entity.sources, "fandango_source", source)
            setattr(entity.sources, "fandango_timestamp", ts)

            setattr(entity, "title", title)
            
            _set_entity(entity, "types", [ "movie", ])
            _set_entity(entity, "desc", entry.summary)
            
            for link in entry.links:
                if 'image' in link.type:
                    # fandango gives us low resolution 69x103 versions of the image, so hackily up the 
                    # resolution before saving the entity :)
                    url  = link.href.replace('69/103', '375/375').replace('69x103', '375x375')
                    size = ImageSizeSchema()
                    size.url = url 
                    image = ImageSchema()
                    image.sizes = [ size ]
                    images = [ image ]
                    
                    _set_entity(entity, "images", images)
                    break
            
            f_url = "%s" % entry.link
            f_url = f_url.replace('%26m%3d', '%3fpid=5348839%26m%3d')
            setattr(entity.sources, "fandango_url", f_url)
            
            # attempt to scrape some extra details from fandango's movie page
            url = "http://www.fandango.com/%s_%s/movieoverview" % \
                   (filter(lambda a: a.isalnum(), entity.title.replace(' ', '')), fid)
            
            try:
                if self._verbose:
                    utils.log(url)
                soup = utils.getSoup(url)
                info = soup.find('div', {'id' : 'info'}).findAll('li')[1].getText()
                
                try:
                    release_date, runtime = None, None
                    
                    for info_re in info_res:
                        match = info_re.match(info)
                        
                        if match is not None:
                            groups = match.groups()
                            release_date = groups[0]
                            if len(groups) == 2:
                                runtime = groups[1]
                            break
                    
                    if release_date is not None:
                        release_date = parseDateString(release_date)
                        _set_entity(entity, "release_date", release_date)
                    
                    if runtime is not None:
                        match = length_re.match(runtime)
                        if match is not None:
                            hours, minutes = match.groups()
                            hours, minutes = int(hours), int(minutes)
                            seconds = 60 * (minutes + 60 * hours)
                            
                            _set_entity(entity, "length", release_date)
                except Exception:
                    utils.printException()
                    pass
                
                try:
                    mpaa_rating = soup.find('div', {'class' : re.compile('rating_icn')}).getText()
                    _set_entity(entity, 'mpaa_rating', rating)
                except Exception:
                    pass
                
                details = soup.findAll('li', {'class' : 'detail_list'})
                
                cast = filter(lambda d: 'Cast:' in d.getText(), details)
                if 1 == len(cast):
                    cast = map(lambda a: a.getText(), cast[0].findAll('a'))
                    cast = map(lambda p: PersonEntityMini().dataImport({ 'title' : p, }), cast)
                    
                    _set_entity(entity, "cast", cast)
                
                director = filter(lambda d: 'Director:' in d.getText(), details)
                if 1 == len(director):
                    directors = map(lambda a: a.getText(), director[0].findAll('a'))
                    directors = map(lambda p: PersonEntityMini().dataImport({ 'title' : p, }), directors)
                    
                    _set_entity(entity, "directors", directors)
                
                genres = filter(lambda d: 'Genres:' in d.getText(), details)
                if 1 == len(genres):
                    genres = genres[0].getText()
                    match  = genre_re.match(genres)
                    
                    if match is not None:
                        genre = match.groups()[0].strip()
                        
                        _set_entity(entity, "genres", [ genre ])
            except Exception:
                utils.printException()
                pass
            
            output.append(entity)
        
        if self._verbose:
            utils.log("[%s] done parsing feed '%s' (%s)" % (self, data.feed.title, url))
        
        return output

def parseCommandLine():
    usage   = "Usage,%prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="optionally print verbose results")
    
    (options, args) = parser.parse_args()
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    fandango = Fandango(verbose = options.verbose)
    results  = fandango.get_top_box_office_movies()
    
    for entity in results:
        from pprint import pprint
        pprint(entity)

if __name__ == '__main__':
    main()

