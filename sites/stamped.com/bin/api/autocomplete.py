#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import pymongo, sys

from MongoStampedAPI import MongoStampedAPI
from db.mongodb.AMongoCollection import MongoDBConfig
from optparse import OptionParser
from Entity import Entity
from difflib import SequenceMatcher
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
    
    parser.add_option("-v", "--verbose", default=False, 
        action="store_true", 
        help="turn verbosity on")
    
    parser.add_option("-c", "--category", default=None, type="string", 
        action="store", dest="category", 
        help="filters results by a given category")
    
    parser.add_option("-s", "--subcategory", default=None, type="string", 
        action="store", dest="subcategory", 
        help="filters results by a given subcategory")
    
    (options, args) = parser.parse_args()
    
    if len(args) <= 0:
        parser.print_help()
        sys.exit(1)
    
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

subcategory_indices = {
    'restaurant' : 0, 
    'bar' : 0, 
    'book' : 3, 
    'movie' : 2, 
    'artist' : 1, 
    'song' : 8, 
    'album' : 7, 
    'app' : 9, 
    'other' : 10,
}

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI()
    #api._entityDB.matchEntities(params.q, limit=10)
    entityDB = api._entityDB
    #placesDB = api._placesEntityDB
    
    entityDB._collection.ensure_index([("title", pymongo.ASCENDING)])
    
    input_query = args[0].lower()
    query = u"%s" % input_query
    query = query.strip()
    query = query.replace('[', '\[?')
    query = query.replace(']', '\]?')
    query = query.replace('(', '\(')
    query = query.replace(')', '\)')
    query = query.replace('|', '\|')
    query = query.replace(' and ', ' (and|&)? ')
    query = query.replace('.', '\.')
    query = query.replace('&', ' & ')
    query = query.replace('-', '-?')
    query = query.replace(' ', '[ \t-_]?')
    query = query.replace("'", "'?")
    utils.log("query: %s" % query)
    
    results = []
    db_results = entityDB._collection.find({"title": {"$regex": query, "$options": "i"}})
    #if options.limit is not None and options.limit >= 0:
    #    db_results = db_results.limit(options.limit)
    
    for entity in db_results:
        e = Entity(entityDB._mongoToObj(entity, 'entity_id'))
        results.append(e)
    
    if options.category is not None:
        results = filter(lambda e: e.category == options.category, results)
    if options.subcategory is not None:
        results = filter(lambda e: e.subcategory == options.subcategory, results)
    
    if len(results) <= 0:
        sys.exit(1)
    
    is_junk = " \t-".__contains__
    #lambda x: x in " \t-"
    
    for i in xrange(len(results)):
        entity = results[i]
        ratio  = 1.0 - SequenceMatcher(is_junk, input_query, entity.title.lower()).ratio()
        subcategory_index = subcategory_indices[entity.subcategory]
        
        results[i] = (ratio, subcategory_index, entity)
    
    results = sorted(results)
    if options.limit is not None and options.limit >= 0:
        results = results[0:min(len(results), options.limit)]
    
    for result in results:
        ratio, _, entity = result
        if options.verbose:
            pprint(entity.getDataAsDict())
        else:
            data = { }
            data['title'] = utils.normalize(entity.title)
            #data['category'] = entity.category
            data['subcategory'] = utils.normalize(entity.subcategory)
            if 'address' in entity:
                data['addr'] = utils.normalize(entity.address)
            pprint(data)
    
    print "%d results found" % len(results)

if __name__ == '__main__':
    main()

