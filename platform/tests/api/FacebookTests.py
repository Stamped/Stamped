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
        fb_test_user            = self.fb.createTestUser(name, access_token, permissions='email')

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
        # Also create a user with standard stamped auth
        self.fb = globalFacebook()
        (self.fb_user_token_a, self.fb_user_id_a)   = self._createFacebookTestAccount(name='fbusera')
        (self.fb_user_token_b, self.fb_user_id_b)   = self._createFacebookTestAccount(name='fbuserb')
        (self.fUserA, self.fUserTokenA)         = self.createFacebookAccount(self.fb_user_token_a, name='fUserA')
        (self.fUserB, self.fUserTokenB)         = self.createFacebookAccount(self.fb_user_token_b, name='fUserB')
        (self.sUser, self.sUserToken)           = self.createAccount(name='sUser')

        self.fb.createTestUserFriendship(self.fb_user_id_a, self.fb_user_token_a, self.fb_user_id_b, self.fb_user_token_b)

        self.privacy = False


    def tearDown(self):
        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.fUserTokenB)
        self.deleteAccount(self.fUserTokenA)
        self.assertTrue(self._deleteFacebookTestAccount(self.fb_user_token_b, self.fb_user_id_b))
        self.assertTrue(self._deleteFacebookTestAccount(self.fb_user_token_a, self.fb_user_id_a))

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

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

