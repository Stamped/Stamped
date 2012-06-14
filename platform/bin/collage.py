#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import colorsys, math, os, sys, urllib2, utils

from api.HTTPSchemas        import HTTPTimeSlice
from api.MongoStampedAPI    import MongoStampedAPI
from libs.ImageCollages     import *

def main(image_urls):
    collage = MusicImageCollage()
    images  = collage.get_images(image_urls)
    
    collage.generate(images)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', action='store', default=None)
    parser.add_argument('-u', '--user', action='store', default=None)
    parser.add_argument('-c', '--category', action='store', default=None)
    parser.add_argument('-l', '--limit', action='store', default=None, type=int)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    if args.db is not None:
        utils.init_db_config(args.db)
    
    api = MongoStampedAPI()
    
    screen_name = "travis"
    user_id = None
    
    if args.user is not None:
        screen_name = args.user
        
        try:
            import bson
            object_id = bson.objectid.ObjectId(args.user)
            screen_name = None
            user_id = args.user
        except:
            pass
    
    user       = api.getUserFromIdOrScreenName({
        'screen_name' : screen_name, 
        'user_id' : user_id
    })
    
    collages   = {
        'basic' : BasicImageCollage(), 
        'music' : MusicImageCollage(), 
        'book'  : BookImageCollage(), 
        'film'  : FilmImageCollage(), 
        'app'   : AppImageCollage(), 
    }
    
    categories = collages.keys()
    
    if args.category is not None:
        assert args.category in categories
        
        categories = [ args.category ]
    
    utils.log()
    
    for category in categories:
        ts = { 'user_id' : user.user_id, 'scope'   : 'user' }
        
        if category != 'basic':
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
        
        utils.log("creating collage for user '%s' w/ category '%s' and %d entities" % 
                  (user.screen_name, category, len(entities)))
        images      = collage.generate_from_user(user, entities)
        
        utils.log()
        
        for image in images:
            filename = "collage-%s-%s-%sx%s.jpg" % (user.screen_name, category, image.size[0], image.size[1])
            utils.log("saving image %s" % filename)
            image.save(filename)

