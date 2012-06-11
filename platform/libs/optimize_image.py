#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, sys, urllib2, utils

from api.S3ImageDB      import S3ImageDB
from StringIO           import StringIO
from PIL                import Image, ImageFilter
from gevent.pool        import Pool
from MongoStampedAPI    import MongoStampedAPI

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image_urls', nargs='*', action="append")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-d', '--db', action='store')
    
    args = parser.parse_args()
    db   = S3ImageDB()
    
    if args.db is not None:
        utils.init_db_config(args.db)
    
    if args.image_urls is not None:
        args.image_urls = args.image_urls[0]
    
    if args.image_urls is not None and len(args.image_urls) > 0:
        utils.log("HARDCODED")
        db.addEntityImages(args.image_urls)
    else:
        utils.log("USING DB")
        api  = MongoStampedAPI()
        pool = Pool(8)
        
        def _process_entity(entity):
            image_url = entity['image']
            image_url = db.addWebEntityImage(image_url)
            entity['image'] = image_url
            
            api._entityDB.updateEntity(entity)
        
        # TODO: handle new-style entity images
        docs = api._entityDB._collection.find({'image' : {'$regex' : r'^.*thetvdb.com.*$'}})
        utils.log("processing %d entity images" % entities.count())
        
        count = 0
        for doc in docs:
            entity = api._entityDB._convertFromMongo(doc)
            pool.spawn(_process_entity, entity)
            
            count += 1
            if count > 10:
                break
        
        pool.join()

#http://thetvdb.com/banners/_cache/posters/211751-2.jpg

