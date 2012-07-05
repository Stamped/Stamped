#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool            import Pool
from api.MongoStampedAPI        import MongoStampedAPI
from optparse               import OptionParser
from pprint                 import pprint

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run in noop mode without modifying anything")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    stampedAPI = MongoStampedAPI()
    entityDB   = stampedAPI._entityDB
    
    rs = entityDB._collection.find({ "sources.fandango" : {"$exists" : True }}, output=list)
    
    pool = Pool(16)
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, options)
    
    pool.join()

def handle_entity(entity, entityDB, options):
    if entity.f_url is not None:
        url = entity.f_url
        entity.f_url = url.replace('%26m%3d', '%3fpid=5348839%26m%3d')
        
        print "%s vs %s" % (url, entity.f_url)
        if not options.noop:
            entityDB.updateEntity(entity)
    
    return
    info_re   = re.compile('[A-Za-z]+ ([^|]+) \| Runtime:(.+)$')
    genre_re  = re.compile('Genres:(.*)$')
    length_re = re.compile('([0-9]+) *hr. *([0-9]+) min.')
    
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
    
    #entity.image = entity.image.replace('69/103', '375/375').replace('69x103', '375x375')
    pprint(entity)
    
    if not options.noop:
        entityDB.updateEntity(entity)

if __name__ == '__main__':
    main()

