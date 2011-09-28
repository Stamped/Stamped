#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ##### #
# OAUTH #
# ##### #

class StampedAPIOAuthTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')

    def tearDown(self):
        self.deleteAccount(self.tokenA)

class StampedAPIOAuthLogin(StampedAPIOAuthTest):
    def test_login_screen_name(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": self.userA['screen_name'],
            "password": "12345"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['token']['access_token']) == 22)
        self.assertTrue(len(result['token']['refresh_token']) == 43)
        self.assertTrue(result['user']['screen_name'] == self.userA['screen_name'])

    def test_login_email(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": "UserA@stamped.com",
            "password": "12345"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['token']['access_token']) == 22)
        self.assertTrue(len(result['token']['refresh_token']) == 43)
        self.assertTrue(len(result['user']['color_primary']) == 6)

    def test_failed_login_screen_name(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": self.userA['screen_name'],
            "password": "123456"
        }
        try:
            result = self.handlePOST(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

    def test_failed_login_email(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": "UserA@stamped.com",
            "password": "123456"
        }
        try:
            result = self.handlePOST(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

    def test_failed_login_empty_password(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": "UserA@stamped.com",
            "password": ""
        }
        try:
            result = self.handlePOST(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

    def test_failed_login_star_password(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": "UserA@stamped.com",
            "password": "*"
        }
        try:
            result = self.handlePOST(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

    def test_token(self):
        path = "oauth2/token.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": self.tokenA['refresh_token'],
            "grant_type": "refresh_token"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['access_token']) == 22)

if __name__ == '__main__':
    main()

