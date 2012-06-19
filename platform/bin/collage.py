#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import colorsys, math, os, pprint, sys, time, urllib2, utils

from S3ImageDB              import S3ImageDB
from api.HTTPSchemas        import HTTPTimeSlice
from api.MongoStampedAPI    import MongoStampedAPI
from libs.ImageCollages     import *

def main(image_urls):
    collage = MusicImageCollage()
    images  = collage.get_images(image_urls)
    
    collage.generate(images)

def save_local_image(image, filename):
    utils.log("saving image %s" % filename)
    image.save(filename)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', action='store', default=None)
    parser.add_argument('-u', '--user', action='store', default=None)
    parser.add_argument('-U', '--users', action='append', default=[])
    parser.add_argument('-c', '--category', action='store', default=None)
    parser.add_argument('-l', '--limit', action='store', default=None, type=int)
    parser.add_argument('-s', '--s3', action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    if args.db is not None:
        utils.init_db_config(args.db)
    
    api = MongoStampedAPI()
    
    collages   = {
        'default' : DefaultImageCollage(), 
        'place'   : PlaceImageCollage(), 
        'music'   : MusicImageCollage(), 
        'book'    : BookImageCollage(), 
        'film'    : FilmImageCollage(), 
        'app'     : AppImageCollage(), 
    }
    
    categories = collages.keys()
    
    if args.category is not None:
        assert args.category in categories
        
        categories = [ args.category ]
    
    save_image = save_local_image
    
    if args.s3:
        db = S3ImageDB()
        
        def save_s3_image(image, filename):
            name = "collages/%s" % filename
            
            db.addImage(name, image)
        
        save_image = save_s3_image
    
    users = [
        {
            'screen_name' : 'travis', 
            'user_id' : None
        }
    ]
    
    if args.user is not None:
        users[0]['screen_name'] = args.user
        
        try:
            import bson
            object_id = bson.objectid.ObjectId(args.user)
            users[0]['screen_name'] = None
            users[0]['user_id']     = args.user
        except:
            pass
    elif len(args.users) > 0:
        users = []
        
        for screen_name in args.users:
            users.append({
                'screen_name' : screen_name, 
                'user_id'     : None
            })
    
    utils.log()
    pad = "-" * 80
    
    for u in users:
        utils.log()
        utils.log(pad)
        utils.log("processing user %s" % pprint.pformat(u))
        utils.log(pad)
        utils.log()
        
        retries = 0
        
        while retries < 3:
            try:
                user = api.getUserFromIdOrScreenName(u)
                
                if user is None:
                    continue
                
                for category in categories:
                    ts = { 'user_id' : user.user_id, 'scope'   : 'user' }
                    
                    if category != 'default':
                        if category == 'app':
                            ts['subcategory'] = 'app'
                        else:
                            ts['category'] = category
                    
                    collage     = collages[category]
                    stamp_slice = HTTPTimeSlice().dataImport(ts).exportTimeSlice()
                    stamps      = api.getStampCollection(stamp_slice)
                    entities    = map(lambda s: s.entity, stamps)
                    
                    if args.limit is not None:
                        entities = entities[:args.limit]
                    
                    utils.log()
                    utils.log(pad)
                    utils.log("creating collage for user '%s' w/ category '%s' and %d entities" % 
                              (user.screen_name, category, len(entities)))
                    utils.log(pad)
                    utils.log()
                    
                    images = collage.generate_from_user(user, entities)
                    
                    utils.log()
                    
                    for image in images:
                        filename = "collage-%s-%s-%sx%s.jpg" % (user.screen_name, category, image.size[0], image.size[1])
                        
                        save_image(image, filename)
            except Exception, e:
                utils.log("unexpected error processing user %s: %s" % (pprint.pformat(u), e))
                utils.printException()
                
                retries += 1
                time.sleep(2 ** retries)
                continue
            
            break

