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
MIKE_TOKEN         = '558345111-gsOAXPBGrvjOaWNmTyCtivPcEoH6yHVh627IynHU'
MIKE_SECRET        = 'NpWLdSOrvHrtTpy2SALH4Ty1T5QUWdMZQhAMcW6Jp4'

TEST_USER_A0_TOKEN      = "595895658-K0PpPWPSBvEVYN46cZOJIQtljZczyoOSTXd68Bju"
TEST_USER_A0_SECRET     = "ncDA2SHT0Tn02LRGJmx2LeoDioH7XsKemYk3ktrEyw"

TEST_USER_B0_TOKEN      = "596530357-ulJmvojQCVwAaPqFwK2Ng1NGa3kMTF254x7NhmhW"
TEST_USER_B0_SECRET     = "r8ttIXxl79E9r3CDQJHnzW4K1vj81N11CMbyzEgh7k"

class StampedAPITwitterTest(AStampedAPITestCase):

    def setUp(self):
        # Create a new Stamped user with Twitter auth, also create a standard auth Stamped user
        self.twitter = globalTwitter()

        self.tw_user_a_token            = TEST_USER_A0_TOKEN
        self.tw_user_a_secret           = TEST_USER_A0_SECRET
        self.tw_user_b_token            = TEST_USER_B0_TOKEN
        self.tw_user_b_secret           = TEST_USER_B0_SECRET

        (self.twUserA, self.twUserAToken) = self.createTwitterAccount(self.tw_user_a_token, self.tw_user_a_secret, name='twUserA')
        (self.twUserB, self.twUserBToken) = self.createTwitterAccount(self.tw_user_b_token, self.tw_user_b_secret, name='twUserB')
        (self.sUser, self.sUserToken) = self.createAccount(name='sUser')

        self.twitter.createFriendship(self.tw_user_a_token, self.tw_user_a_secret, 'TestUserB0')

    def tearDown(self):
        self.twitter.destroyFriendship(self.tw_user_a_token, self.tw_user_a_secret, 'TestUserB0')

        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.twUserAToken)
        self.deleteAccount(self.twUserBToken)


## create two stamped accounts, give them both linked twitter id, and try to create a twitter account
## create one stamped account, link it to twitter account, try to create new stamped twitter account
#

class StampedAPITwitterCreate(StampedAPITwitterTest):

    def test_invalid_twitter_token_login(self):
        # attempt login with invalid twitter token
        with expected_exception():
            self.loginWithTwitter(self.tw_user_a_token, "BLAAARRGH!!")

    def test_create_duplicate_twitter_auth_account(self):
        with expected_exception():
            self.createTwitterAccount(self.tw_user_a_token, self.tw_user_a_secret, name='twUser2')

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
        result = self.loginWithTwitter(self.tw_user_a_token, self.tw_user_a_secret)

        # verify that the stamped user token and user_id are correct
        self.assertEqual(result['user']['user_id'], self.twUserA['user_id'])

class StampedAPITwitterFind(StampedAPITwitterTest):
    def test_find_by_twitter(self):
        path = "users/find/twitter.json"
        data = {
            "oauth_token"   : self.twUserAToken['access_token'],
            "user_token"    : TEST_USER_A0_TOKEN,
            "user_secret"   : TEST_USER_A0_SECRET,
        }
        result = self.handlePOST(path, data)

        self.assertLength(result, 1)
        self.assertEqual(result[0]['user_id'], self.twUserB['user_id'])

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

