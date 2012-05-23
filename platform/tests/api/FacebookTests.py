#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *
from libs.Facebook import *

CLIENT_ID = DEFAULT_CLIENT_ID
CLIENT_SECRET = CLIENT_SECRETS[CLIENT_ID]

# ######## #
# FACEBOOK #
# ######## #

class StampedAPIFacebookTest(AStampedAPITestCase):

    def _createFacebookTestAccount(self, name='TestUser'):
        # Create the test user on the Facebook API (see: http://developers.facebook.com/docs/test_users/)
        # First get the App Access Token
        access_token    = self.fb.getAppAccessToken()

        # Next generate the test user for our app on Facebook
        fb_test_user    = self.fb.createTestUser(name, access_token, permissions='email')

        fb_user_id              = fb_test_user['id']
        fb_user_token           = fb_test_user['access_token']
        fb_user_login_url       = fb_test_user['login_url']
        fb_user_email           = fb_test_user['email']
        fb_user_password        = fb_test_user['password']

        return fb_user_token, fb_user_id

    def _deleteFacebookTestAccount(self, fb_user_token, fb_user_id):
        return self.fb.deleteTestUser(fb_user_token, fb_user_id)


    def setUp(self):
        # Create a Facebook test user registered with our app, then use that test user to create a new Stamped account
        self.fb = globalFacebook()
        (self.fb_user_token, self.fb_user_id)   = self._createFacebookTestAccount(name='UserA')
        (self.user, self.token)                 = self.createFacebookAccount(self.fb_user_token, name='UserA')
        self.privacy = False


    def tearDown(self):
        self.deleteAccount(self.token)
        self.assertTrue(self._deleteFacebookTestAccount(self.fb_user_token, self.fb_user_id))

class StampedAPIFacebookCreate(StampedAPIFacebookTest):
    def test_create(self):
        print(self.user)
        self.assertEqual(self.user.linked_accounts.facebook.facebook_id, self.fb_user_id)
        self.assertEqual(self.user.linked_accounts.facebook.facebook_token, self.fb_user_token)

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

