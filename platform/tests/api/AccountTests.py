#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from utils                  import lazyProperty
from framework.FixtureTest  import *
from AStampedAPITestCase    import *
from AStampedAPIHttpTestCase import *
from MongoStampedAPI import MongoStampedAPI

import logs

CLIENT_ID = DEFAULT_CLIENT_ID
CLIENT_SECRET = CLIENT_SECRETS[CLIENT_ID]

# ####### #
# ACCOUNT #
# ####### #


class StampedAPIAccountUpdateTest(AStampedAPITestCase):
    def setUp(self):
        self.account = self.createAccount('TestUser')

    def tearDown(self):
        self.deleteAccount(self.account.user_id)


    @fixtureTest()
    def test_change_name(self):
        TEST_NAME = "Pimpbot 5000"
        form = AccountUpdateForm()
        form.name = TEST_NAME

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.name, TEST_NAME)

    def test_change_screen_name(self):
        TEST_SN = "pimpbot5000test"
        form = AccountUpdateForm()
        form.screen_name = TEST_SN

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.screen_name, TEST_SN)

    def test_change_screen_name_used(self):
        TEST_SN = "pimpbot5000test"
        form = AccountUpdateForm()
        form.screen_name = TEST_SN

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.screen_name, TEST_SN)

        with expected_exception():
            self.createAccount("TestUser2", screen_name = TEST_SN)

    def test_change_screen_name_blacklisted(self):
        TEST_SN = "cock"
        form = AccountUpdateForm()
        form.screen_name = TEST_SN

        with expected_exception():
            self.api.updateAccount(self.account.user_id, form)

    def test_change_phone(self):
        form = AccountUpdateForm()
        form.phone = '212-987-6543'

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.phone, '2129876543')

    def test_change_bio(self):
        BIO = "I've got microchips from Yokohama and I'll be turning out yo mama!"
        form = AccountUpdateForm()
        form.bio = BIO

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.bio, BIO)

    def test_change_website(self):
        WEBSITE = "http://www.stamped.com/"
        form = AccountUpdateForm()
        form.website = WEBSITE

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.website, WEBSITE)

    def test_change_website_invalid(self):
        WEBSITE = "not a website"
        form = AccountUpdateForm()
        form.website = WEBSITE

        with expected_exception():
            self.api.updateAccount(self.account.user_id, form)

    def test_change_location(self):
        LOCATION = 'New York, NY'
        form = AccountUpdateForm()
        form.location = LOCATION

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.location, LOCATION)

    def test_change_color_primary(self):
        form = AccountUpdateForm()
        form.color_primary = 'ff0000'

        self.api.updateAccount(self.account.user_id, form)
        self.account = self.showAccount(self.account.user_id)
        self.assertEqual(self.account.color_primary, 'FF0000')

    def test_change_color_primary_invalid(self):
        COLOR_PRIMARY = 'not a valid color'
        form = AccountUpdateForm()
        with expected_exception():
            form.color_primary = COLOR_PRIMARY

class StampedAPIAccountHttpTest(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(name='devbot') 
        self.privacy = False

    def tearDown(self):
        self.deleteAccount(self.token)

class StampedAPIAccountSettings(StampedAPIAccountHttpTest):
    def test_post(self):
        path = "account/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "name": "Pimpbot 5000",
            }
        result = self.handlePOST(path, data)
        self.assertTrue(result['result'])
        account = self.showAccount(self.token)
        self.assertEqual(account['name'], "Pimpbot 5000")

    def test_post_invalid(self):
        path = "account/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "screen_name": "cock",
            }
        with expected_exception():
            self.handlePOST(path, data)

class StampedAPIAccountUpdateProfileImage(StampedAPIAccountHttpTest):
    def test_update_profile_image(self):
        path = "account/update_profile_image.json"
        data = {
            "oauth_token": self.token['access_token'],
            "temp_image_url": "http://static.stamped.com/users/default.jpg",
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['screen_name'], "devbot")

    def test_update_profile_image_invalid(self):
        path = "account/update_profile_image.json"
        data = {
            "oauth_token": self.token['access_token'],
            "temp_image_url": "not a valid url",
            }
        with expected_exception():
            result = self.handlePOST(path, data)


class StampedAPIAccountCustomizeStamp(StampedAPIAccountHttpTest):
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

    def test_customize_stamp_invalid(self):
        path = "account/customize_stamp.json"
        data = {
            "oauth_token": self.token['access_token'],
            "color_primary": '333333',
            "color_secondary": '999999',
        }
        with expected_exception():
            del(data['color_primary'])
            result = self.handlePOST(path, data)
        data["color_primary"] = '333333'

        with expected_exception():
            del(data['color_secondary'])
            result = self.handlePOST(path, data)
        data["color_secondary"] = '999999'



class StampedAPIAccountInvalid(StampedAPIAccountHttpTest):
    def test_blacklist(self):
        with expected_exception():
            self.createAccount('cock')
    
    def test_invalid_screen_name(self):
        with expected_exception():
            self.createAccount('a b')
        
        with expected_exception():
            self.createAccount('a*b')
        
        with expected_exception():
            self.createAccount('a!')
        
        with expected_exception():
            self.createAccount('a+b')
        
        with expected_exception():
            self.createAccount('a/b')
        
        with expected_exception():
            self.createAccount('@ab')
    
    def test_invalid_length(self):
        with expected_exception():
            self.createAccount('')
        
        with expected_exception():
            self.createAccount('012345678901234578901234567890')
    
    def test_invalid_emails(self):
        invalid_emails = [
            'abc@stamped.con', 
            'abc@gmail.con', 
            'abc@gmailcom', 
            'abcgmail.com', 
            '@gmail.com', 
            'abc@.com', 
            'abc@@.com', 
            'test@gmail.ghz', 
            'devbot@stamped.con', 
        ]
        
        index = 0
        for email in invalid_emails:
            with expected_exception():
                self.createAccount('testinv_%s' % index, email=email)
            index += 1

class StampedAPIAccountCheckAccount(StampedAPIAccountHttpTest):
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
    
    def test_check_email_invalid(self):
        path = "account/check.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login": '%s@stamped.con' % self.user['screen_name'],
        }
        
        with expected_exception():
            self.handlePOST(path, data)
"""
class StampedAPIAccountLinkedAccounts(StampedAPIAccountTest):
    def test_twitter(self):
        path = "account/linked/twitter/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "twitter_id": '1234567890',
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        path = "account/linked/twitter/remove.json"
        data = {
            "oauth_token": self.token['access_token']
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def test_facebook(self):
        path = "account/linked/facebook/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "facebook_id": '1234567890',
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        path = "account/linked/facebook/remove.json"
        data = {
            "oauth_token": self.token['access_token']
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def test_twitter_followers(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        
        ids = ['11131112','814122']
        path = "account/linked/twitter/update.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "twitter_id": ids[0],
            "twitter_screen_name": 'usera',
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "twitter_id": ids[1],
            "twitter_screen_name": 'userb',
        }
        result = self.handlePOST(path, data)

        # Log in with credentials to post alert to followers
        data = {
            "oauth_token": self.tokenC['access_token'],
            "twitter_id": '0000',
            "twitter_screen_name": 'userc',
            "twitter_key": TWITTER_KEY,
            "twitter_secret": TWITTER_SECRET,
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        # Check activity for userA to verify activity item was created
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 1), 
        ])
        
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)

    def test_facebook_followers(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        
        ids = ['100003002012425','2400157'] # andybons, robbystein
        path = "account/linked/facebook/update.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "facebook_id": ids[0],
            "facebook_name": 'usera',
        }
        result = self.handlePOST(path, data)
        data = {
            "oauth_token": self.tokenB['access_token'],
            "facebook_id": ids[1],
            "facebook_name": 'userb',
        }
        result = self.handlePOST(path, data)

        # Log in with credentials to post alert to followers
        data = {
            "oauth_token": self.tokenC['access_token'],
            "facebook_id": '0000',
            "facebook_name": 'userc',
            "facebook_token": FB_TOKEN,
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        # Check activity for userA to verify activity item was created
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 1), 
        ])

        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)
"""
class StampedAPIAccountChangePassword(StampedAPIAccountHttpTest):
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
        self.token = result['token']

class StampedAPIAccountAlertSettings(StampedAPIAccountHttpTest):
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
            "email_alert_todo": True,
            "email_alert_reply": False
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result) == 14)
        self.assertTrue(result['email_alert_todo'])

    def test_set_token(self):
        path = "account/alerts/ios/update.json"
        data = {
            "oauth_token": self.token['access_token'],
            "token": "%s" % ("0" * 64)
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def test_remove_token(self):
        path = "account/alerts/ios/remove.json"
        data = {
            "oauth_token": self.token['access_token'],
            "token": "%s" % ("0" * 64)
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

