#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import bson, sys

from MongoStampedAPI import MongoStampedAPI
from db.mongodb.AMongoCollection import MongoDBConfig

from gevent import Greenlet
from gevent.pool import Pool
from optparse import OptionParser
from match.EntityMatcher import EntityMatcher
from pprint import pprint

#-----------------------------------------------------------

class EntityDeduper(Greenlet):
    def __init__(self, options):
        Greenlet.__init__(self)
        
        self.api = MongoStampedAPI()
        self.matcher = EntityMatcher(self.api, options)
    
    def _run(self):
        results = []
        last = None
        
        numEntities = 0
        pool = Pool(2)
        
        utils.log("parsing place duplicates")
        while True:
            if last is None:
                query = None
            else:
                query = {'_id' : { "$gt" : last }}
            
            current = self.matcher._placesDB._collection.find_one(query)
            if current is None:
                break
            
            numEntities += 1
            last = bson.objectid.ObjectId(current['_id'])
            
            pool.spawn(self.matcher.dedupeOne, current, True)
            #self.matcher.dedupeOne(current, True)
        
        pool.join()
        utils.log("done parsing place duplicates")
        
        pool = Pool(64)
        utils.log("parsing non-place duplicates")
        
        last = None
        while True:
            if last is None:
                query = None
            else:
                query = {'_id' : { "$gt" : last }}
            
            current = self.matcher._entityDB._collection.find_one(query)
            if current is None:
                break
            
            numEntities += 1
            last = bson.objectid.ObjectId(current['_id'])
            
            pool.spawn(self.matcher.dedupeOne, current)
            #self.matcher.dedupeOne(current, False)
        
        pool.join()
        utils.log("done parsing non-place duplicates")
        utils.log("found a total of %d duplicates (processed %d)" % (self.matcher.numDuplicates, numEntities))

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, 
        action="store_true", dest="noop", 
        help="just run the dedupper without actually modifying anything")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    deduper = EntityDeduper(options)
    deduper.start()
    deduper.join()

if __name__ == '__main__':
    main()

