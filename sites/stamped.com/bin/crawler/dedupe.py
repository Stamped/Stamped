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

def main():
    options, args = parseCommandLine()
    
    matcher = EntityMatcher2()
    api = MongoStampedAPI()
    db = api._placesEntityDB
    
    results = []
    last = None
    
    db._collection.ensure_index([("coordinates", GEO2D)])
    numDuplicates = 0
    numEntities = 0
    
    while True:
        if last is None:
            query = None
        else:
            query = {'_id' : { "$gt" : last }}
        
        current = db._collection.find_one(query)
        if current is None:
            break
        
        numEntities += 1
        last = bson.objectid.ObjectId(current['_id'])
        
        entity = Entity(db._mongoToObj(current, 'entity_id'))
        
        earthRadius = 3963.192 # miles
        maxDistance = 5.0 / earthRadius # convert to radians
        
        # TODO: verify lat / lng versus lng / lat
        q = SON({"$near" : [entity.lat, entity.lng]})
        q.update({"$maxDistance" : maxDistance })
        
        docs     = db._collection.find({"coordinates" : q})
        entities = (Entity(db._mongoToObj(doc, 'entity_id')) for doc in docs)
        matches  = list(matcher.genMatchingEntities(entity, entities))
        
        if len(matches) > 0:
            matches.insert(0, entity)
            
            keep = None
            for i in xrange(len(matches)):
                match = matches[i]
                if 'openTable' in match:
                    keep = matches.pop(i)
                    break
            
            if keep is not None:
                keep = matches.pop(0)
            
            numMatches = len(matches)
            if numMatches > 0:
                print "%s) found %d duplicates" % (keep.title, numMatches)
                numDuplicates += numMatches
                
                for i in xrange(numMatches):
                    match = matches[i]
                    print "   %d) removing %s" % (i + 1, match.title)
                    db._removeDocument(match.entity_id)
    
    print "found a total of %d duplicates (processed %d)" % (numDuplicates, numEntities)

if __name__ == '__main__':
    main()

