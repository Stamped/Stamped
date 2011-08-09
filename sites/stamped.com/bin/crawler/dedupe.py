#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import bson, sys

from MongoStampedAPI import MongoStampedAPI
from db.mongodb.AMongoCollection import MongoDBConfig
from pymongo import GEO2D
from pymongo.son import SON

from gevent import Greenlet
from gevent.pool import Pool
from optparse import OptionParser
from EntityMatcher2 import EntityMatcher2
from Entity import Entity
from pprint import pprint

#-----------------------------------------------------------

class EntityDeduper(Greenlet):
    def __init__(self, options):
        Greenlet.__init__(self)
        
        self.options = options
        self.matcher = EntityMatcher2()
        self.api = MongoStampedAPI()
        self.db0 = self.api._placesEntityDB
        self.db1 = self.api._entityDB
    
    def _run(self):
        results = []
        last = None
        
        self.db0._collection.ensure_index([("coordinates", GEO2D)])
        self.numDuplicates = 0
        self.numEntities = 0
        pool = Pool(512)
        self.dead_entities = set()
        
        while True:
            if last is None:
                query = None
            else:
                query = {'_id' : { "$gt" : last }}
            
            current = self.db0._collection.find_one(query)
            if current is None:
                break
            
            self.numEntities += 1
            last = bson.objectid.ObjectId(current['_id'])
            #pool.spawn(self._dedupe_one, current)
            self._dedupe_one(current)
        
        pool.join()
        utils.log("found a total of %d duplicates (processed %d)" % (self.numDuplicates, self.numEntities))
    
    def _dedupe_one(self, current):
        if current['_id'] in self.dead_entities:
            # this entity has been asynchronously removed
            return
        
        current1 = self.db1._collection.find_one({ '_id' : current['_id'] })
        if current1 is None:
            # this entity has been asynchronously removed
            return
        
        entity1 = Entity(self.db1._mongoToObj(current1, 'entity_id'))
        entity0 = Entity(self.db0._mongoToObj(current,  'entity_id'))
        
        earthRadius = 3963.192 # miles
        maxDistance = 50.0 / earthRadius # convert to radians
        
        # TODO: verify lat / lng versus lng / lat
        q = SON({"$near" : [entity0.lat, entity0.lng]})
        q.update({"$maxDistance" : maxDistance })
        
        docs     = self.db0._collection.find({"coordinates" : q})
        entities = self._gen_entities(docs)
        matches  = list(self.matcher.genMatchingEntities(entity1, entities))
        
        if entity0.entity_id in self.dead_entities:
            # this entity has been asynchronously removed
            return
        
        if len(matches) > 0:
            matches.insert(0, entity1)
            
            # determine which one of the duplicates to keep
            keep = None
            for i in xrange(len(matches)):
                match = matches[i]
                if 'openTable' in match:
                    keep = matches.pop(i)
                    break
            
            if keep is None:
                keep = matches.pop(0)
            
            matches = filter(lambda m: m.entity_id != keep.entity_id, matches)
            numMatches = len(matches)
            
            for match in matches:
                self.dead_entities.add(match.entity_id)
            
            if numMatches > 0:
                utils.log("%s) found %d duplicate%s" % (keep.title, numMatches, '' if 1 == numMatches else 's'))
                
                self.numDuplicates += numMatches
                
                # look through and delete all duplicates
                for i in xrange(numMatches):
                    match = matches[i]
                    
                    def _addDict(src, dest):
                        for k, v in src.iteritems():
                            if not k in dest:
                                dest[k] = v
                            elif isinstance(v, dict):
                                _addDict(v, dest)
                    
                    # add any fields from this version of the duplicate to the version 
                    # that we're keeping if they don't already exist
                    _addDict(match.getDataAsDict(), keep)
                    
                    utils.log("   %d) removing %s" % (i + 1, match.title))
                    self.db1.removeEntity(match.entity_id)
                    self.db0.removeEntity(match.entity_id)
                
                self.db1.updateEntity(keep)
    
    def _gen_entities(self, docs):
        for doc in docs:
            d = self.db1._collection.find_one({ '_id' : doc['_id'] })
            if d is not None:
                yield Entity(self.db1._mongoToObj(d, 'entity_id'))

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        if ':' in options.db:
            options.host, options.port = options.db.split(':')
            options.port = int(options.port)
        else:
            options.host, options.port = (options.db, 27017)
        
        conf = {
            'mongodb' : {
                'host' : options.host, 
                'port' : options.port, 
            }
        }
        
        cfg = MongoDBConfig.getInstance()
        cfg.config = utils.AttributeDict(conf)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    deduper = EntityDeduper(options)
    deduper.start()
    deduper.join()

if __name__ == '__main__':
    main()

