#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import base64, os, utils, Image, urllib2, mimetools

from AStampedAPITestCase import *
from MongoStampedAPI import MongoStampedAPI
from S3ImageDB import S3ImageDB

# ###### #
# IMAGES #
# ###### #

class AImageTest(AStampedAPITestCase):
    def __init__(self, *args, **kwargs):
        AStampedAPITestCase.__init__(self, *args, **kwargs)
        
        base = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(os.path.join(base, 'data'), 'images')
        self.images  = []
        
        for f in os.listdir(image_dir):
            path  = os.path.join(image_dir, f)
            image = Image.open(path)
            
            self.images.append(image)

# class ImageDBTests(AImageTest):
#     def setUp(self):
#         self.imageDB = S3ImageDB(bucket_name='stamped.com.static.test')
#         self.baseurl = 'http://%s.s3.amazonaws.com' % self.imageDB.bucket_name
    
#     def test_profile_images(self):
#         self.util_test_images("users", self.imageDB.addProfileImage)
    
#     def test_entity_images(self):
#         self.util_test_images("entities", self.imageDB.addEntityImage)
    
#     def test_stamp_images(self):
#         self.util_test_images("stamps", self.imageDB.addStampImage)
    
#     def util_test_images(self, path, func):
#         for index in xrange(len(self.images)):
#             image    = self.images[index]
#             entityId = 'test_id_%d' % index
#             func(entityId, image)
            
#             baseurl = "%s/%s/%s" % (self.baseurl, path, entityId)
#             url = "%s.jpg" % (baseurl, )
            
#             try:
#                 f = utils.getFile(url)
#             except HTTPError:
#                 logs.warn("unable to download '%s'" % url)
#                 raise
            
#             image2 = self.imageDB.getImage(f)
            
#             self.assertEqual(image.size, image2.size)
#             self.assertEqual(image.mode, image2.mode)
    
#     def tearDown(self):
#         keys = self.imageDB.bucket.get_all_keys()
#         for key in keys:
#             key.delete()

class StampedAPIImageTests(AImageTest):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
    
    # def test_profile_images(self):
    #     for image in self.images:
    #         path = "account/update_profile_image.json"
    #         temp = 'temp.jpg'
    #         image.save(temp, optimize=True)
            
    #         f = open(temp, 'r')
    #         data = f.read()
    #         f.close()
            
    #         data = {
    #             "oauth_token": self.token['access_token'],
    #             "profile_image": base64.urlsafe_b64encode(data), 
    #         }
            
    #         result = self.handlePOST(path, data)
    #         self.assertIn('images', result)
    
    def test_profile_images(self):
        from poster.encode import *
        from poster.streaminghttp import register_openers, StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler
        import urllib2



        for image in self.images:
            path = "account/update_profile_image.json"
            temp = 'temp.jpg'
            image.save(temp, optimize=True)
            
            f = open(temp, 'r')
            image = f.read()
            f.close()


            path    = "account/update_profile_image.json"
            url     = "%s/%s" % (self._baseurl, path)

            params = {
                "oauth_token": self.token['access_token'],
                "profile_image": image, 
            }


            # Register the streaming http handlers with urllib2
            # register_openers()

            # handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler]
            # opener = urllib2.build_opener(urllib2.HTTPHandler(), *handlers)
            # urllib2.install_opener(opener)



            datagen, headers = multipart_encode({"profile_image": open(temp, "rb"), "oauth_token": '1234'})
            s = "".join(datagen)
            print 'DATAGEN: %s' % s
            print 'HEADERS: %s' % headers

            # Create the Request object
            request = urllib2.Request(url, datagen, headers)
            request.add_header('Accept-encoding', 'gzip,deflate,sdch')

            request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            request.add_header('Accept-charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')

            # Actually do the request, and get the response
            result = urllib2.urlopen(request)#.read()

            print result



            # params = {}
            # dir = u'/data/'
            # for f in os.listdir(dir):
            #     params[f] = open(dir+f)
            data, headers = multipart_encode(params)
            print 'HEADERS: %s' % headers
            # url = 'https://test/upload.py'
            req = urllib2.Request(url, data, headers)
            result = urllib2.urlopen(req)



            # Start the multipart/form-data encoding of the file "DSC0001.jpg"
            # "image1" is the name of the parameter, which is normally set
            # via the "name" parameter of the HTML <input> tag.

            # headers contains the necessary Content-Type and Content-Length
            # datagen is a generator object that yields the encoded parameters
            # datagen, headers = multipart_encode(data)

            # Create the Request object
            # request = urllib2.Request(url, datagen, headers)
            # Actually do the request, and get the response
            # result = urllib2.urlopen(request).read()
            print result
            
            # result = json.load(self._opener.open(url, params))

            # self.assertIn('images', result)
    
    def tearDown(self):
        self.deleteAccount(self.token)

if __name__ == '__main__':
    main()

