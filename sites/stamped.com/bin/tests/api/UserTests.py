#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# #### #
# USER #
# #### #

class StampedAPIUserTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.screen_names = ['UserA', 'UserB']

    def tearDown(self):
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIUsersShow(StampedAPIUserTest):
    def test_show_user_id(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['screen_name'], self.userA['screen_name'])

    def test_show_screen_name(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "screen_name": self.userA['screen_name']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['user_id'], self.userA['user_id'])

class StampedAPIUsersLookup(StampedAPIUserTest):
    def test_lookup_user_ids(self):
        path = "users/lookup.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_ids": "%s,%s" % (
                self.userA['user_id'],
                self.userB['user_id']
            )
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)

    def test_lookup_screen_names(self):
        path = "users/lookup.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "screen_names": "%s,%s" % (
                self.userA['screen_name'],
                self.userB['screen_name']
            )
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result) >= 2)

class StampedAPIUsersSearch(StampedAPIUserTest):
    def test_search(self):
        path = "users/search.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": "%s" % self.userA['screen_name'][:3]
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result) >= 1)

class StampedAPIUsersPrivacy(StampedAPIUserTest):
    def test_privacy_user_id(self):
        path = "users/privacy.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result == False)
    
    def test_privacy_screen_name(self):
        path = "users/privacy.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "screen_name": self.userB['screen_name']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result == False)
    
    def test_privacy_not_found(self):
        path = "users/privacy.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "screen_name": 'unknownUserName'
        }
        
        with expected_exception():
            result = self.handleGET(path, data)

class StampedAPIUsersFindContacts(StampedAPIUserTest):
    def test_find_by_email(self):
        path = "users/find/email.json"
        emails = ['%s@stamped.com' % self.userA['screen_name'],
                    '%s@stamped.com' % self.userB['screen_name']]
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": ','.join(emails)
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)
            self.assertIn(user['identifier'], [x.lower() for x in emails])

    def test_find_by_phone(self):
        # Set phone number
        numbers = ['1235551111','1235551112']
        path = "account/settings.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "phone": numbers[0],
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "phone": numbers[1],
        }
        result = self.handlePOST(path, data)

        path = "users/find/phone.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": ','.join(numbers)
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)
            self.assertIn(user['identifier'], numbers)

    def test_find_by_phone_twofer(self):
        # Set phone number
        number = '1235551111'
        path = "account/settings.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "phone": number,
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "phone": number,
        }
        result = self.handlePOST(path, data)

        path = "users/find/phone.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": number
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)
            self.assertTrue(user['identifier'] == number)

    def test_fail_find_by_phone(self):
        # Set phone number
        numbers = ['3335551111','2123343774\u200e']
        path = "account/settings.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "phone": numbers[0],
        }
        result = self.handlePOST(path, data)

        path = "users/find/phone.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": ','.join(numbers)
        }
        result = self.handlePOST(path, data)

        self.assertLength(result, 1)
        user = result[0]
        self.assertIn(user['screen_name'], self.screen_names)
        self.assertIn(user['identifier'], numbers)



class StampedAPIUsersFindTwitter(StampedAPIUserTest):
    def test_find_by_twitter(self):
        ids = ['1235551111','1235551112']
        path = "account/linked_accounts.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "twitter_id": ids[0],
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "twitter_id": ids[1],
        }
        result = self.handlePOST(path, data)

        path = "users/find/twitter.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": ','.join(ids)
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)
            self.assertIn(user['identifier'], ids)


class StampedAPIUsersFindFacebook(StampedAPIUserTest):
    def test_find_by_facebook(self):
        ids = ['1235551111','1235551112']
        path = "account/linked_accounts.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "facebook_id": ids[0],
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "facebook_id": ids[1],
        }
        result = self.handlePOST(path, data)

        path = "users/find/facebook.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": ','.join(ids)
        }
        result = self.handlePOST(path, data)
        self.assertLength(result, 2)
        for user in result:
            self.assertIn(user['screen_name'], self.screen_names)
            self.assertIn(user['identifier'], ids)


class StampedAPISuggested(StampedAPIUserTest):
    def test_suggested(self):
        path = "users/suggested.json"
        data = { 
            "oauth_token": self.tokenA['access_token']
        }
        result = self.handleGET(path, data)
        for user in result:
            self.assertTrue('screen_name' in user)

if __name__ == '__main__':
    main()

