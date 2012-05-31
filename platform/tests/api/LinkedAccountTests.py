#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

CLIENT_ID = DEFAULT_CLIENT_ID
CLIENT_SECRET = CLIENT_SECRETS[CLIENT_ID]

# ####### #
# ACCOUNT #
# ####### #

#TODO: Replace these tokens with a test account!!
TEST_USER_TOKEN      = '558345111-gsOAXPBGrvjOaWNmTyCtivPcEoH6yHVh627IynHU'
TEST_USER_SECRET     = 'NpWLdSOrvHrtTpy2SALH4Ty1T5QUWdMZQhAMcW6Jp4'

class StampedAPILinkedAccountTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(name='UserA')

    def tearDown(self):
        self.deleteAccount(self.token)

class StampedAPILinkeAccountAdd(StampedAPILinkedAccountTest):
    def test_add_twitter_account(self):
        data = {
            'service_name'        : 'twitter',
            'user_id'             : 'test_user_a',
            'screen_name'    : 'test_user_a',
            'token'          : TEST_USER_TOKEN,  #'test_twitter_token',
            'secret'         : TEST_USER_SECRET, #'test_twitter_secret',
        }
        import pprint
        self.addLinkedAccount(self.token, **data)
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['twitter']['service_name'], 'twitter')
        self.removeLinkedAccount(self.token, 'twitter')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

