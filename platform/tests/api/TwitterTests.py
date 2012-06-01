#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *
from libs.Twitter import *

CLIENT_ID = DEFAULT_CLIENT_ID
CLIENT_SECRET = CLIENT_SECRETS[CLIENT_ID]

# ####### #
# TWITTER #
# ####### #

#TODO: Replace these tokens with a test account!!
TEST_USER_TOKEN      = '558345111-gsOAXPBGrvjOaWNmTyCtivPcEoH6yHVh627IynHU'
TEST_USER_SECRET     = 'NpWLdSOrvHrtTpy2SALH4Ty1T5QUWdMZQhAMcW6Jp4'

class StampedAPITwitterTest(AStampedAPITestCase):

    def setUp(self):
        # Create a new Stamped user with Twitter auth, also create a standard auth Stamped user
        self.twitter = globalTwitter()

        self.tw_user_token          = TEST_USER_TOKEN
        self.tw_user_secret         = TEST_USER_SECRET

        (self.twUser, self.twUserToken) = self.createTwitterAccount(self.tw_user_token, self.tw_user_secret, name='twUser')
        (self.sUser, self.sUserToken) = self.createAccount(name='sUser')
        self.privacy = False

    def tearDown(self):
        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.twUserToken)

## create two stamped accounts, give them both linked twitter id, and try to create a twitter account
## create one stamped account, link it to twitter account, try to create new stamped twitter account
#

class StampedAPITwitterCreate(StampedAPITwitterTest):

    def test_invalid_twitter_token_login(self):
        # attempt login with invalid twitter token
        with expected_exception():
            self.loginWithTwitter(self.tw_user_token, "BLAAARRGH!!")

    def test_create_duplicate_twitter_auth_account(self):
        with expected_exception():
            self.createTwitterAccount(self.tw_user_token, self.tw_user_secret, name='twUser2')

    def test_linked_account_with_used_twitter_id(self):
    #        self.addLinkedAccount(
    #            self.sUserToken,
    #                { 'facebook_id'         : self.fb_user_id,
    #                  'facebook_name'       : 'facebook_user',
    #                  'facebook_token'      : self.fb_user_token,
    #                  }
    #        )
        pass

    def test_attempt_linked_account_change_for_twitter_auth_user(self):
        pass



    def test_valid_login(self):
        # login with twitter user account
        result = self.loginWithTwitter(self.tw_user_token, self.tw_user_secret)

        # verify that the stamped user token and user_id are correct
        self.assertEqual(result['user']['user_id'], self.twUser['user_id'])

class StampedAPITwitterFind(StampedAPITwitterTest):
    def test_find_by_twitter(self):
        path = "users/find/twitter.json"
        data = {
            "oauth_token"   : self.twUserToken['access_token'],
            "user_token"    : TEST_USER_TOKEN,
            "user_secret"   : TEST_USER_SECRET,
        }
        result = self.handlePOST(path, data)

        self.assertLength(result, 2)
#        for user in result:
#            self.assertIn(user['screen_name'], self.screen_names)
#            self.assertIn(user['identifier'], ids)
#
#        path = "users/find/twitter.json"
#        data = {
#            "oauth_token": self.tokenC['access_token'],
#            "twitter_key": TWITTER_KEY,
#            "twitter_secret": TWITTER_SECRET,
#            }
#        result = self.handlePOST(path, data)
#        self.assertTrue(len(result) >= 2)
#        for user in result:
#            self.assertIn(user['screen_name'], self.screen_names)
#            self.assertIn(user['identifier'], ids)

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

