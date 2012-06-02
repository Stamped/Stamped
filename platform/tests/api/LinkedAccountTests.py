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
TWITTER_USER_A0_TOKEN      = "595895658-K0PpPWPSBvEVYN46cZOJIQtljZczyoOSTXd68Bju"
TWITTER_USER_A0_SECRET     = "ncDA2SHT0Tn02LRGJmx2LeoDioH7XsKemYk3ktrEyw"
TWITTER_USER_B0_TOKEN      = "596530357-ulJmvojQCVwAaPqFwK2Ng1NGa3kMTF254x7NhmhW"
TWITTER_USER_B0_SECRET     = "r8ttIXxl79E9r3CDQJHnzW4K1vj81N11CMbyzEgh7k"

class StampedAPILinkedAccountTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(name='UserA')

    def tearDown(self):
        self.deleteAccount(self.token)

class StampedAPILinkeAccountAdd(StampedAPILinkedAccountTest):
    def test_add_twitter_account(self):
        # add the linked account
        data = {
            'service_name'   : 'twitter',
            'user_id'        : 'test_user_a',
            'screen_name'    : 'test_user_a',
            'token'          : TWITTER_USER_A0_TOKEN,  #'test_twitter_token',
            'secret'         : TWITTER_USER_A0_SECRET, #'test_twitter_secret',
        }
        self.addLinkedAccount(self.token, **data)

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['twitter']['service_name'], 'twitter')

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'twitter')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)


class StampedAPILinkeAccountAdd(StampedAPILinkedAccountTest):
    def test_add_twitter_account(self):
        # add the linked account
        data = {
            'service_name'        : 'twitter',
            'user_id'             : 'test_user_a',
            'screen_name'    : 'test_user_a',
            'token'          : TEST_USER_TOKEN,  #'test_twitter_token',
            'secret'         : TEST_USER_SECRET, #'test_twitter_secret',
        }
        self.addLinkedAccount(self.token, **data)

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['twitter']['service_name'], 'twitter')

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'twitter')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

