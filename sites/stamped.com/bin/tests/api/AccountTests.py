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
            "phone": 1235551234,
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
        bio = "My long biography goes here."
        path = "account/update_profile.json"
        data = {
            "oauth_token": self.token['access_token'],
            "bio": bio
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['bio'], bio)

class StampedAPIAccountCustomizeStamp(StampedAPIAccountTest):
    def test_customize_stamp(self):
        path = "account/customize_stamp.json"
        data = {
            "oauth_token": self.token['access_token'],
            "color_primary": '333333',
            "color_secondary": '999999',
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['color_primary'], '333333')
        self.assertEqual(result['color_secondary'], '999999')

class StampedAPIAccountBlacklistedScreenName(StampedAPIAccountTest):
    def test_blacklist(self):
        with expected_exception():
            (user, token) = self.createAccount('cock')
    
    def test_invalid_characters(self):
        with expected_exception():
            (user, token) = self.createAccount('a b')
        
        with expected_exception():
            (user, token) = self.createAccount('a*b')
        
        with expected_exception():
            (user, token) = self.createAccount('a!')
        
        with expected_exception():
            (user, token) = self.createAccount('a+b')
        
        with expected_exception():
            (user, token) = self.createAccount('a/b')
        
        with expected_exception():
            (user, token) = self.createAccount('@ab')

class StampedAPIAccountCheckAccount(StampedAPIAccountTest):
    def test_check_email_available(self):
        path = "account/check.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": 'testest1234@stamped.com',
        }
        
        with expected_exception():
            result = self.handlePOST(path, data)

    def test_check_screen_name_available(self):
        path = "account/check.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": 'testtest1234',
        }
        
        with expected_exception():
            result = self.handlePOST(path, data)

    def test_check_email_taken(self):
        path = "account/check.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": '%s@stamped.com' % self.user['screen_name'],
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['user_id'], self.user['user_id'])

    def test_check_screen_name_taken(self):
        path = "account/check.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": self.user['screen_name'].lower(),
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['user_id'], self.user['user_id'])

class StampedAPIAccountLinkedAccounts(StampedAPIAccountTest):
    def test_twitter(self):
        path = "account/linked_accounts.json"
        data = {
            "oauth_token": self.token['access_token'],
            "twitter_id": '1234567890',
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def test_facebook(self):
        path = "account/linked_accounts.json"
        data = {
            "oauth_token": self.token['access_token'],
            "facebook_id": '1234567890',
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

class StampedAPIAccountChangePassword(StampedAPIAccountTest):
    def test_change_password(self):
        path = "account/change_password.json"
        data = {
            "oauth_token": self.token['access_token'],
            "old_password": '12345',
            "new_password": '54321',
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": self.user['screen_name'],
            "password": "54321"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['token']['access_token']) == 22)
        self.assertTrue(len(result['token']['refresh_token']) == 43)

class StampedAPIAccountAlertSettings(StampedAPIAccountTest):
    def test_show_settings(self):
        path = "account/alerts/show.json"
        data = {
            "oauth_token": self.token['access_token']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result) == 14)

    def test_update_settings(self):
        path = "account/alerts/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "email_alert_fav": True,
            "email_alert_reply": False
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result) == 14)
        self.assertTrue(result['email_alert_fav'])

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

