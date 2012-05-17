#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from GooglePlacesEntityMatcher  import GooglePlacesEntityMatcher
from gevent.pool                import Pool
from match.EntityMatcher        import EntityMatcher
from GooglePlaces               import GooglePlaces
from MongoStampedAPI            import MongoStampedAPI
from optparse                   import OptionParser
from pprint                     import pprint

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
    matcher    = GooglePlacesEntityMatcher()
    matcher2   = EntityMatcher(stampedAPI, options)
    entityDB   = stampedAPI._entityDB
    
    # Note: we could just remove all apple movies...
    rs = entityDB._collection.find({"sources.apple" : { "$exists" : False }, "subcategory" : "movie"}, output=list)
    
    pool = Pool(32)
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = placesDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, matcher, matcher2)
    
    pool.join()

def handle_entity(entity, matcher, matcher2):
    match = matcher.tryMatchEntityWithGooglePlaces(entity, detailed=True)
    
    if match is not None:
        entity = matcher2.mergeDuplicates(entity, [ match ])
        utils.log("Success: %s vs %s" % (entity.title, match.title))
    else:
        utils.log("Failure: %s" % entity.title)
        pprint(entity)

if __name__ == '__main__':
    main()

