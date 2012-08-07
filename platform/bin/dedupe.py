#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, sys

from crawler.match.EntityMatcher import EntityMatcher
from api_old.MongoStampedAPI     import MongoStampedAPI
from gevent              import Greenlet
from gevent.pool         import Pool
from optparse            import OptionParser
from pprint              import pprint

#-----------------------------------------------------------

class EntityDeduper(Greenlet):
    def __init__(self, options):
        Greenlet.__init__(self)
        
        self.api = MongoStampedAPI()
        self.matcher = EntityMatcher(self.api, options)
        self.options = options
    
    def _run(self):
        results = []
        last = None
        
        numEntities = 0
        
        if self.options.place:
            pool = Pool(2)
            
            utils.log("[%s] parsing place duplicates" % (self, ))
            while True:
                if last is None:
                    if self.options.seed:
                        last  = bson.objectid.ObjectId(self.options.seed)
                        query = {'_id' : last}
                    else:
                        query = None
                else:
                    query = {'_id' : { "$gt" : last }}
                
                current = self.matcher._placesDB._collection.find_one(query)
                if current is None:
                    break
                
                numEntities += 1
                last = bson.objectid.ObjectId(current['_id'])
                
                current = self.matcher._placesDB._convertFromMongo(current)
                pool.spawn(self.matcher.dedupeOne, current)
                #self.matcher.dedupeOne(current)
                
                if self.options.seed:
                    break
            
            pool.join()
            utils.log("[%s] done parsing place duplicates" % (self, ))
        
        if self.options.nonplace:
            pool = Pool(8)
            utils.log("[%s] parsing non-place duplicates" % (self, ))
            
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
                
                current = self.matcher._entityDB._convertFromMongo(current)
                pool.spawn(self.matcher.dedupeOne, current)
                #self.matcher.dedupeOne(current)
                
                if self.options.seed:
                    break
            
            pool.join()
         
        numDuplicates = self.matcher.numDuplicates
        utils.log("[%s] found a total of %d duplicate%s (processed %d)" % 
            (self, numDuplicates, '' if 1 == numDuplicates else 's', numEntities))
    
    def __str__(self):
        return self.__class__.__name__

def parseCommandLine():
    usage   = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-s", "--seed", default=None, type="string", 
        action="store", dest="seed", 
        help="seed id to start with")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run the dedupper in noop mode without modifying anything")
    
    parser.add_option("-p", "--place", default=False, action="store_true", 
        help="dedupe only place entities")
    
    parser.add_option("-P", "--nonplace", default=False, action="store_true", 
        help="dedupe only non-place entities")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    (options, args) = parser.parse_args()
    
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    
    if not (options.place or options.nonplace):
        options.place = True
        options.nonplace = True
    
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

