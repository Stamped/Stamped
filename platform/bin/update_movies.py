#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool            import Pool
from api.MongoStampedAPI        import MongoStampedAPI
from crawler.match.EntityMatcher    import EntityMatcher
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
    matcher    = EntityMatcher(stampedAPI, options)
    entityDB   = stampedAPI._entityDB
    
    rs = entityDB._collection.find({ "sources.apple" : {"$exists" : True }, "subcategory" : "movie"}, output=list)
    pool = Pool(16)
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, matcher, options)
    
    pool.join()

def handle_entity(entity, entityDB, matcher, options):
    date_re = re.compile('([0-9]+) ([0-9]+) ([0-9]+)')
    match   = date_re.match(entity.original_release_date)
    
    if match is not None:
        groups = match.groups()
        entity.original_release_date = groups[0]
    """
    if 1 == len(rs):
        entity2 = entityDB._convertFromMongo(rs[0])
        utils.log("MATCH %s (%s vs %s)" % (entity.title, entity.aid, entity2.nid))
        
        if not options.noop:
            keep, dupes1 = matcher.getBestDuplicate([ entity2, entity ])
            matcher.mergeDuplicates(keep, dupes1)
    else:
        utils.log("NOMATCH %s" % (entity.title, ))
    """

if __name__ == '__main__':
    main()

