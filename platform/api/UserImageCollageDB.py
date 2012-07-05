#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, time, utils

from S3ImageDB              import S3ImageDB
from api.HTTPSchemas        import HTTPTimeSlice
from libs.ImageCollages     import *
from MongoStampedAPI        import globalMongoStampedAPI

class UserImageCollageDB(object):
    
    def __init__(self):
        self._db    = S3ImageDB()
        
        self._collages   = {
            'default' : DefaultImageCollage(), 
            'place'   : PlaceImageCollage(), 
            'music'   : MusicImageCollage(), 
            'book'    : BookImageCollage(), 
            'film'    : FilmImageCollage(), 
            'app'     : AppImageCollage(), 
        }
        
        self._categories = self._collages.keys()
        self.api = globalMongoStampedAPI()
    
    def process_user(self, user, categories=None):
        assert user is not None
        
        if categories is None:
            categories = self._categories
        
        retries = 0
        
        while retries < 3:
            try:
                for category in categories:
                    ts = { 'user_id' : user.user_id, 'scope'  : 'user' }
                    
                    if category != 'default':
                        if category == 'app':
                            ts['subcategory'] = 'app'
                        else:
                            ts['category'] = category
                    
                    collage     = self._collages[category]
                    stamp_slice = HTTPTimeSlice().dataImport(ts).exportTimeSlice()
                    stamps      = self.api.getStampCollection(stamp_slice)
                    entities    = map(lambda s: s.entity, stamps)
                    
                    logs.info("creating collage for user '%s' w/ category '%s' and %d entities" % (user.screen_name, category, len(entities)))
                    images = collage.generate_from_user(user, entities)
                    
                    for image in images:
                        filename = "collage-%s-%s-%sx%s.jpg" % (user.screen_name, category, image.size[0], image.size[1])
                        
                        self.save_image(image, filename)
                
                break
            except Exception, e:
                logs.warn("unexpected error processing user %s: %s" % (str(user), e))
                logs.warn(utils.getFormattedException())
                
                retries += 1
                time.sleep(2 ** retries)
    
    def save_image(self, image, filename):
        name = "collages/%s" % filename
        
        self._db.addImage(name, image)

