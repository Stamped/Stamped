#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from MongoStampedAPI import MongoStampedAPI
from db.mongodb.AMongoCollection import MongoDBConfig
from optparse import OptionParser
from Entity import Entity
from pprint import pprint
import sys

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

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI()
    #api._entityDB.matchEntities(params.q, limit=10)
    entityDB = api._entityDB
    
    query = '^%s' % args[0]
    
    results = []
    db_results = entityDB._collection.find({"title": {"$regex": query, "$options": "i"}})
    if options.limit is not None and options.limit >= 0:
        db_results = db_results.limit(options.limit)
    
    for entity in db_results:
        e = Entity(entityDB._mongoToObj(entity, 'entity_id'))
        results.append(e)
    
    if len(results) <= 0:
        sys.exit(1)
    
    for entity in results:
        data = { }
        data['title'] = entity.title
        data['category'] = entity.category
        #data['subtitle'] = entity.subtitle
        pprint(data)
    
    print "%d results found" % len(results)

if __name__ == '__main__':
    main()

