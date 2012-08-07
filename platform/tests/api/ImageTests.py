#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, os, utils, Image, binascii

from tests.AStampedAPIHttpTestCase import *
from api.MongoStampedAPI import MongoStampedAPI
from api.S3ImageDB import S3ImageDB

# ###### #
# IMAGES #
# ###### #

class AImageHttpTest(AStampedAPIHttpTestCase):
    def __init__(self, *args, **kwargs):
        AStampedAPIHttpTestCase.__init__(self, *args, **kwargs)
        
        base = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(os.path.join(base, 'data'), 'images')
        self.images  = []
        
        for f in os.listdir(image_dir):
            path  = os.path.join(image_dir, f)
            image = Image.open(path)
            
            self.images.append(image)

class ImageDBTests(AImageHttpTest):
    def setUp(self):
        self.imageDB = S3ImageDB(bucket_name='stamped.com.static.test')
        self.baseurl = 'http://%s.s3.amazonaws.com' % self.imageDB.bucket_name
    
    def test_profile_images(self):
        self.util_test_images("users", self.imageDB.addResizedProfileImages, True)
    
#    def test_entity_images(self):
#        self.util_test_images("entities", self.imageDB.addEntityImage)
#
#    def test_stamp_images(self):
#        self.util_test_images("stamps", self.imageDB.addStampImage)
    
    def util_test_images(self, path, func, resized=False):
        print self.images
        for index in xrange(len(self.images)):
            image    = self.images[index]
            entityId = 'test_id_%d' % index
            func(entityId, image)

            if resized:
                pass
            else:
                baseurl = "%s/%s/%s" % (self.baseurl, path, entityId)
                url = "%s.jpg" % (baseurl, )

                print('### url: %s' % url)

                try:
                    f = utils.getFile(url)
                except HTTPError:
                    logs.warn("unable to download '%s'" % url)
                    raise

                image2 = utils.getImage(f)

                self.assertEqual(image.size, image2.size)
            # note: we convert all images to JPEG upon upload, which'll 
            # convert RGBA to RGB, so the modes won't necessarily be 
            # equal.
            #self.assertEqual(image.mode, image2.mode)
    
    def tearDown(self):
        keys = self.imageDB.bucket.get_all_keys()
        for key in keys:
            key.delete()

class StampedAPIImageTests(AImageHttpTest):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
    
    def test_profile_images(self):

        for image in self.images:
            path = "account/update_profile_image.json"
            temp = 'temp.jpg'
            image.save(temp, optimize=True)
            
            f = open(temp, 'r')
            image = f.read()
            # Send data ascii-encoded
            #image = binascii.b2a_qp(image)
            f.close()

            path    = "account/update_profile_image.json"

            data = {
                "oauth_token": self.token['access_token']
            }

            files = {
                "profile_image": {
                    "filename": temp,
                    "data": image
                }
            }

            result = self.handleMultiPart(path, data, files)

            self.assertIn('images', result)
    
    def tearDown(self):
        self.deleteAccount(self.token)

if __name__ == '__main__':
    main()

