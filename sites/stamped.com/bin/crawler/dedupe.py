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

from gevent.pool import Pool
from optparse import OptionParser
from EntityMatcher2 import EntityMatcher2
from Entity import Entity
from pprint import pprint

#-----------------------------------------------------------

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")
    
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

def _gen_entities(db1, docs):
    for doc in docs:
        d = db1._collection.find_one({ '_id' : doc['_id'] })
        assert d is not None
        yield Entity(db1._mongoToObj(d, 'entity_id'))

def main():
    options, args = parseCommandLine()
    
    matcher = EntityMatcher2()
    api = MongoStampedAPI()
    
    db0 = api._placesEntityDB
    db1 = api._entityDB
    
    results = []
    last = None
    
    db0._collection.ensure_index([("coordinates", GEO2D)])
    numDuplicates = 0
    numEntities = 0
    
    while True:
        if last is None:
            query = None
        else:
            query = {'_id' : { "$gt" : last }}
        
        current = db0._collection.find_one(query)
        if current is None:
            break
        
        numEntities += 1
        last = bson.objectid.ObjectId(current['_id'])
        
        current1 = db1._collection.find_one({ '_id' : current['_id'] })
        assert current1 is not None
        
        entity1 = Entity(db1._mongoToObj(current1, 'entity_id'))
        entity0 = Entity(db0._mongoToObj(current,  'entity_id'))
        
        earthRadius = 3963.192 # miles
        maxDistance = 5.0 / earthRadius # convert to radians
        
        # TODO: verify lat / lng versus lng / lat
        q = SON({"$near" : [entity0.lat, entity0.lng]})
        q.update({"$maxDistance" : maxDistance })
        
        docs     = db0._collection.find({"coordinates" : q})
        entities = _gen_entities(db1, docs)
        matches  = list(matcher.genMatchingEntities(entity1, entities))
        
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
            
            if numMatches > 0:
                utils.log("%s) found %d duplicate%s" % (keep.title, numMatches, '' if 0 == numMatches else 's'))
                
                numDuplicates += numMatches
                
                for i in xrange(numMatches):
                    match = matches[i]
                    
                    def _addDict(src, dest):
                        for k, v in src.iteritems():
                            if not k in dest:
                                dest[k] = v
                            elif isinstance(v, dict):
                                _addDict(v, dest)
                    
                    _addDict(match.getDataAsDict(), keep)
                    
                    utils.log("   %d) removing %s" % (i + 1, match.title))
                    db0.removeEntity(match.entity_id)
                    db1.removeEntity(match.entity_id)
                
                db1.updateEntity(keep)
    
    utils.log("found a total of %d duplicates (processed %d)" % (numDuplicates, numEntities))

if __name__ == '__main__':
    main()

