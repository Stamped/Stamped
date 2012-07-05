#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import json, re, time, utils

from api.MongoStampedAPI    import MongoStampedAPI
from libs.GooglePlaces       import GooglePlaces
from libs.Geocoder           import Geocoder

from gevent.pool        import Pool
from optparse           import OptionParser
from pprint             import pprint

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
    geocoder   = Geocoder()
    entityDB   = stampedAPI._entityDB
    googlePlaces = GooglePlaces()
    
    rs = entityDB._collection.find({"sources.userGenerated.generated_by" : {"$exists" : True}, "coordinates.lat" : {"$exists" : False}, "details.place.address" : {"$exists" : True}, "details.place.address" : {"$nin" : [ None, "", " ", ", " ]}}, output=list)
    
    pool = Pool(16)
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, geocoder, googlePlaces, entityDB, options)
    
    pool.join()
    utils.log("done processing %d entities" % len(rs))

def handle_entity(entity, geocoder, googlePlaces, entityDB, options):
    latLng = geocoder.addressToLatLng(entity.address)
    
    if latLng is None:
        utils.log("error converting address '%s'" % utils.normalize(entity.address))
        return
    
    entity.lat = latLng[0]
    entity.lng = latLng[1]
    
    ret = googlePlaces.addPlaceReport(entity)
    if ret is not None:
        ret = json.loads(ret)
        
        if ret['status'] == 'OK':
            entity.gid = ret['id']
            entity.reference = ret['reference']
    
    if not options.noop:
        entityDB.updateEntity(entity)
    
    utils.log("success: entity '%s'" % entity.title)
    utils.log("%s => %s" % (entity.address, (entity.lat, entity.lng)))

if __name__ == '__main__':
    main()

