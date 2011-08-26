#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ####### #
# ACCOUNT #
# ####### #

class StampedAPIAccountTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.privacy = False
    
    def tearDown(self):
        self.deleteAccount(self.token)

class StampedAPIAccountSettings(StampedAPIAccountTest):
    def test_post(self):
        path = "account/settings.json"
        data = {
            "oauth_token": self.token['access_token'],
            "screen_name": "UserA2",
            "privacy": False,
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['privacy'], False)
        self.privacy = result['privacy']

    def test_get(self):
        path = "account/settings.json"
        data = {
            "oauth_token": self.token['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['privacy'], self.privacy)

class StampedAPIAccountUpdateProfile(StampedAPIAccountTest):
    def test_update_profile(self):
        path = "account/update_profile.json"
        data = {
            "oauth_token": self.token['access_token'],
            "bio": "My long biography goes here.",
            "color": "333333,999999"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['color_primary'], '333333')
        self.assertEqual(result['color_secondary'], '999999')

class StampedAPIAccountUpdateProfileImage(StampedAPIAccountTest):
    def test_update_profile_image(self):
        # TODO: this url is temporary!
        url = 'https://si0.twimg.com/profile_images/147088134/'
        url = url + 'twitter_profile_reasonably_small.jpg'
        
        path = "account/update_profile_image.json"
        data = {
            "oauth_token": self.token['access_token'],
            "profile_image": url, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['profile_image'], url)

### TESTS TO ADD:
# Change bio from string to None
# Make sure screen_name change propagates through system
# Check how display name works if weird first name / last name things are sent
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

