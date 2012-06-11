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
        # example url:  http://thetvdb.com/banners/_cache/posters/211751-2.jpg
        db.addEntityImages(args.image_urls)
    else:
        api  = MongoStampedAPI()
        pool = Pool(32)
        
        def _process_entity(entity):
            modified = False
            
            for image in entity.images:
                image_url   = image.sizes[0].url
                image_url   = db.addWebEntityImage(image_url)
                
                modified    = True
                image.sizes[0].url = image_url
            
            if modified:
                api._entityDB.updateEntity(entity)
        
        # TODO: handle new-style entity images
        docs  = api._entityDB._collection.find({'image' : {'$regex' : r'^.*thetvdb.com.*$'}})
        count = docs.count()
        index = 0
        
        progress_delta = 5
        progress_count = 100 / progress_delta
        
        utils.log("processing %d entity images" % count)
        
        for doc in docs:
            entity = api._entityDB._convertFromMongo(doc)
            
            pool.spawn(_process_entity, entity)
            
            if 0 == (index % (count / progress_count)):
                utils.log("\n\nPROGRESS: %s\n\n" % (utils.getStatusStr(index, count)))
            
            index += 1
        
        pool.join()

