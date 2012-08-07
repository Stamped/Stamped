#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool        import Pool
from api_old.MongoStampedAPI    import MongoStampedAPI
from optparse           import OptionParser
from pprint             import pprint
from rdioapi            import Rdio

RDIO_API_PUBLIC_KEY = 'vrhd4yxa4eu99jbysjqzebym'
RDIO_API_SECRET_KEY = 'paYxS8rPVE'

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
    
    parser.add_option("-l", "--limit", default=None, action="store", type="int", 
        help="limit number to convert")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    rdio       = Rdio(RDIO_API_PUBLIC_KEY, RDIO_API_SECRET_KEY, {})
    #pprint(rdio.get(keys='t7609753'))
    
    stampedAPI = MongoStampedAPI()
    entityDB   = stampedAPI._entityDB
    
    rs    = entityDB._collection.find({ "subcategory" : "artist" }) #, output=list)
    pool  = Pool(16)
    count = 0
    
    #utils.log("processing %d entities" % len(rs))
    
    # NOTE: rdio is very sensitive to its 10 QPS threshold; create a wrapper that 
    # automatically enforces QPS throttling
    # http://developer.rdio.com/docs/read/rest/Methods
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, rdio, options)
        
        count += 1
        if options.limit and count >= options.limit:
            break
    
    pool.join()

def handle_entity(entity, entityDB, rdio, options):
    query  = entity.title
    query  = query.encode('utf-8')
    
    result = rdio.search(query=query, types='Artist', never_or=True)
    utils.log(query)
    pprint(result)

if __name__ == '__main__':
    main()

