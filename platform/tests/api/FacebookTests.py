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

    def setUp(self):
        # Create a Facebook test user registered with our app, then use that test user to create a new Stamped account
        # Also create a user with standard stamped auth
        self.fb = globalFacebook()
        self.fb_app_access_token                    = self.fb.getAppAccessToken()
        (self.fb_user_token_a, self.fb_user_id_a)   = self.createFacebookTestUser(name='fbusera')
        (self.fb_user_token_b, self.fb_user_id_b)   = self.createFacebookTestUser(name='fbuserb')
        (self.fUserA, self.fUserTokenA)             = self.createFacebookAccount(self.fb_user_token_a, name='fUserA')
        (self.fUserB, self.fUserTokenB)             = self.createFacebookAccount(self.fb_user_token_b, name='fUserB')
        (self.sUser, self.sUserToken)               = self.createAccount(name='sUser')

        self.fb.createTestUserFriendship(self.fb_user_id_a, self.fb_user_token_a, self.fb_user_id_b, self.fb_user_token_b)

        self.privacy = False


    def tearDown(self):
        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.fUserTokenB)
        self.deleteAccount(self.fUserTokenA)
        self.assertTrue(self.deleteFacebookTestUser(self.fb_user_token_b, self.fb_user_id_b))
        self.assertTrue(self.deleteFacebookTestUser(self.fb_user_token_a, self.fb_user_id_a))

## create two stamped accounts, give them both linked facebook id, and try to create a facebook account
## create one stamped account, link it to facebook account, try to create new stamped facebook account
#

class StampedAPIFacebookCreate(StampedAPIFacebookTest):

    def test_invalid_facebook_token_login(self):
        # attempt login with invalid facebook token
        with expected_exception():
            self.loginWithFacebook("BLAAARRGH!!")

    def test_create_duplicate_facebook_auth_account(self):
        with expected_exception():
            self.createFacebookAccount(self.fb_user_token_a, name='fUser2')

    def test_linked_account_with_used_facebook_id(self):
#        self.addLinkedAccount(
#            self.sUserToken,
#                { 'facebook_id'         : self.fb_user_id,
#                  'facebook_name'       : 'facebook_user',
#                  'facebook_token'      : self.fb_user_token,
#                  }
#        )
        pass

    def test_attempt_linked_account_change_for_facebook_auth_user(self):
        pass



    def test_valid_login(self):
        # login with facebook user account
        result = self.loginWithFacebook(self.fb_user_token_a)

        # verify that the stamped user token and user_id are correct
        self.assertEqual(result['user']['user_id'], self.fUserA['user_id'])


class StampedAPIFacebookFind(StampedAPIFacebookTest):
    def test_find_by_facebook(self):
        path = "users/find/facebook.json"
        data = {
            "oauth_token"   : self.fUserTokenA['access_token'],
            "user_token"    : self.fb_user_token_a,
            }
        result = self.handlePOST(path, data)

        self.assertLength(result, 1)
        self.assertEqual(result[0]['user_id'], self.fUserB['user_id'])

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

