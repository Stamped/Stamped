#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from api.MongoStampedAPI import MongoStampedAPI
import bson
from tests.AStampedAPIHttpTestCase import *
from libs.Facebook import *
from libs.Twitter import *

CLIENT_ID = DEFAULT_CLIENT_ID
CLIENT_SECRET = CLIENT_SECRETS[CLIENT_ID]

# ####### #
# ACCOUNT #
# ####### #

TWITTER_USER_A0_TOKEN      = "595895658-K0PpPWPSBvEVYN46cZOJIQtljZczyoOSTXd68Bju"
TWITTER_USER_A0_SECRET     = "ncDA2SHT0Tn02LRGJmx2LeoDioH7XsKemYk3ktrEyw"
TWITTER_USER_A0_ID         = "595895658"

TWITTER_USER_B0_TOKEN      = "596530357-ulJmvojQCVwAaPqFwK2Ng1NGa3kMTF254x7NhmhW"
TWITTER_USER_B0_SECRET     = "r8ttIXxl79E9r3CDQJHnzW4K1vj81N11CMbyzEgh7k"


class StampedAPILinkedAccountHttpTest(AStampedAPIHttpTestCase):
    def __init__(self, methodName='runTest'):
        AStampedAPIHttpTestCase.__init__(self, methodName)
        self.fb = globalFacebook()
        self.fb_app_access_token = self.fb.getAppAccessToken()

    def _getOpenGraphActivity(self, fb_token):
        return self.fb.getOpenGraphActivity(fb_token)

    def _createFacebookTestUser(self, name='TestUser'):
        # Create the test user on the Facebook API (see: http://developers.facebook.com/docs/test_users/)


        # Next generate the test user for our app on Facebook
        fb_test_user            = self.fb.createTestUser(name, self.fb_app_access_token, permissions='email,publish_stream,publish_actions')

        fb_user_id              = fb_test_user['id']
        fb_user_token           = fb_test_user['access_token']
        fb_user_login_url       = fb_test_user['login_url']
        fb_user_email           = fb_test_user['email']
        fb_user_password        = fb_test_user['password']

        return fb_user_token, fb_user_id

    def _clearFacebookTestUsers(self):
        return self.fb.clearTestUsers()


    def setUp(self):
        (self.user, self.token) = self.createAccount(name='UserA')

    def tearDown(self):
        self.deleteAccount(self.token)

class StampedAPILinkedAccountAdd(StampedAPILinkedAccountHttpTest):

    def setUp(self):
        StampedAPILinkedAccountHttpTest.setUp(self)
        (self.fb_user_token_a, self.fb_user_id_a)     = self._createFacebookTestUser(name='fbusera')

    def tearDown(self):
        StampedAPILinkedAccountHttpTest.tearDown(self)
        self._clearFacebookTestUsers()

    def test_add_twitter_account(self):
        # add the linked account
        self.addLinkedTwitterAccount(self.token, TWITTER_USER_A0_TOKEN, TWITTER_USER_A0_SECRET)

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['twitter']['service_name'], 'twitter')

        from pprint import pprint
        pprint(linkedAccounts)

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'twitter')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)

    def test_update_twitter_account(self):
        # add the linked account
        self.addLinkedTwitterAccount(self.token, TWITTER_USER_A0_TOKEN, TWITTER_USER_A0_SECRET)

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['twitter']['service_name'], 'twitter')

        from pprint import pprint
        pprint(linkedAccounts)

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'twitter')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)


    def test_add_facebook_account(self):
        # add the linked account
        self.addLinkedFacebookAccount(self.token, self.fb_user_token_a)

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['facebook']['service_name'], 'facebook')

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'facebook')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)


    def test_add_rdio_account(self):
        # add the linked account
        self.addLinkedRdioAccount(self.token, "TOKEN_DUMMY")

        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['rdio']['service_name'], 'rdio')

        # remove the linked account and verify that it has been removed
        self.removeLinkedAccount(self.token, 'rdio')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)

    def test_add_facebook_linked_account_taken(self):
        (self.fUserA, self.fUserAToken)             = self.createFacebookAccount(self.fb_user_token_a, name='fUserA')

        with expected_exception():
            self.addLinkedFacebookAccount(self.token, self.fb_user_token_a)

class StampedAPIOpenGraphTest(StampedAPILinkedAccountHttpTest):

    def setUp(self):
        StampedAPILinkedAccountHttpTest.setUp(self)
        (self.fb_user_token_a, self.fb_user_id_a)     = self._createFacebookTestUser(name='fbusera')
        # add the linked account
        self.addLinkedFacebookAccount(self.token, self.fb_user_token_a)

    def tearDown(self):
        StampedAPILinkedAccountHttpTest.tearDown(self)
        self._clearFacebookTestUsers()

    def test_update_facebook_share_settings(self):
        # verify that the linked account was properly added
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 1)
        self.assertEqual(linkedAccounts['facebook']['service_name'], 'facebook')

        # update share settings: enable share stamps on facebook

        path = "account/linked/facebook/settings/update.json"
        data = {
            "oauth_token"   : self.token['access_token'],
            'service_name'   : 'facebook',
            'on'   : 'share_stamps,share_follows,share_todos,share_likes',
            }
        self.handlePOST(path, data)

        # verify that share settings were updated
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_stamps'], True)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_follows'], True)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_todos'], True)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_likes'], True)

        data = {
            "oauth_token"   : self.token['access_token'],
            'service_name'   : 'facebook',
            'off'   : 'share_stamps,share_follows',
            }
        self.handlePOST(path, data)

        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_stamps'], False)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_follows'], False)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_todos'], True)
        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_likes'], True)

        path = "account/linked/facebook/settings/show.json"
        data = {
            "oauth_token"   : self.token['access_token'],
            "service_name"  : 'facebook',
            }
        result = self.handleGET(path, data)

        import pprint
        pprint.pprint(result)



    def test_update_facebook_share_settings_with_no_account(self):
        # verify that the linked account was properly added
        self.removeLinkedAccount(self.token, 'facebook')
        linkedAccounts = self.showLinkedAccounts(self.token)
        self.assertEqual(len(linkedAccounts), 0)

        logs.info('linkedAccounts: %s' % linkedAccounts)

        # update share settings: enable share stamps on facebook

        path = "account/linked/facebook/settings/update.json"
        data = {
            "oauth_token"   : self.token['access_token'],
            'service_name'   : 'facebook',
            'on'   : 'share_stamps,share_follows,share_todos,share_likes',
            }
        with expected_exception():
            self.handlePOST(path, data)


#    def test_update_facebook_share_settings(self):
#        # verify that the linked account was properly added
#        linkedAccounts = self.showLinkedAccounts(self.token)
#        self.assertEqual(len(linkedAccounts), 1)
#        self.assertEqual(linkedAccounts['facebook']['service_name'], 'facebook')
#
#        # update share settings: enable share stamps on facebook
#        path = "account/linked/update_share_settings.json"
#        data = {
#            "oauth_token"       : self.token['access_token'],
#            'service_name'      : 'facebook',
#            'on'                : 'share_stamps',
#            }
#        self.handlePOST(path, data)
#
#        # verify that share settings were updated
#        linkedAccounts = self.showLinkedAccounts(self.token)
#        self.assertEqual(linkedAccounts['facebook']['share_settings']['share_stamps'], True)
#
#        account = self.showAccount(self.token)
#        import pprint
#        pprint.pprint(linkedAccounts)
#
#        print('###')
#        pprint.pprint(account)
#
#        #entity = self.createEntity(self.token)
#        #stamp = self.createStamp(self.token, entity['entity_id'], blurb='ASDF')
#        #self.createTodo(self.token, entity['entity_id'])
#        #self.createLike(self.token, stamp['stamp_id'])
#
#        import time
#        time.sleep(5)
#
#        result = self._getOpenGraphActivity(self.fb_user_token_a)
#        pprint.pprint(result)
#
#
#        self.async(lambda: self.stamp = self.createStamp(self.token, self.entity['entity_id'], blurb='ASDF'), [
#            lambda x: self.assertEqual(len(x), 1),
#            lambda x: self.assertEqual(x[0]['verb'], 'friend_facebook'),
#            lambda x: self.assertEqual(x[0]['subjects'][0]['user_id'], self.fUserB['user_id']),
#            ])





class StampedAPIHttpOldLinkedAccountRemove(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(name='UserA')

        self._accountDB = MongoStampedAPI()._accountDB
        testuser = self._accountDB._getMongoDocumentFromId(bson.objectid.ObjectId(self.user['user_id']))

        oldFormatAccountData = {
            "alerts" : {
                "ios_alert_comment" : True,
                "ios_alert_follow" : True,
                "ios_alert_reply" : True,
                "ios_alert_fav" : True,
                "email_alert_credit" : True,
                "email_alert_reply" : True,
                "ios_alert_credit" : True,
                "ios_alert_mention" : True,
                "email_alert_like" : True,
                "email_alert_comment" : True,
                "email_alert_mention" : True,
                "ios_alert_like" : True,
                "email_alert_follow" : True,
                "email_alert_fav" : True
            },
            "bio" : "My life is short-lived :(",
            "color_primary" : "33B6DA",
            "color_secondary" : "006C89",
            "devices" : {
                "ios_device_tokens" : [
                    "df687e03345604f6b02a4c32bc7d5220ddd5f832c270645e06f22cc26f66516a",
                    "1c8cf15acb17f8362322ccff0452417dcd3f6b538193099e0347efb84e8a4a4f",
                    "f90a011543694238bde60ff04790f10f864adb2e04c279d91b3477c03a18ddcd"
                ]
            },
            "email" : "testuser@stamped.com",
            "linked_accounts" : {
                "facebook" : {
                    "facebook_alerts_sent" : True,
                    "facebook_id" : "1234567",
                    "facebook_name" : "Test User",
                    "facebook_alerts_sent" : True,
                },
                "twitter" : {
                    "twitter_alerts_sent" : True,
                    "twitter_id" : "12345678",
                    "twitter_screen_name" : "testusera0",
                    "twitter_alerts_sent" : True,
                },
                "netflix" : {
                    "netflix_token" : "abcdefghijkl_7mon6p9zdWyDB_-9QU4w4jcAn4WZA3HotKLMrG4oBT2CsB_Mum6N24aXCrmqRxnBSrNNuxKkhF8sZE6BtSh0",
                    "netflix_secret" : "abcdefghijkl",
                    "netflix_user_id" : "abcdefghijsQujGoAtBtnwbTBpSjBx00o2PE2ASmO9kgw-"
                },
                },
            "location" : "New York",
            "password" : "S3Flv0fae32460b5aa107be10c7d71885a4e28",
            "phone" : 1234567890,
            "privacy" : False,
            "stats" : {
                "num_unread_news" : 0,
                "num_credits" : 51,
                "num_stamps" : 65,
                "num_stamps_left" : 160,
                "num_faves" : 87,
                "num_likes_given" : 79,
                "num_followers" : 179,
                "num_likes" : 115,
                "num_stamps_total" : 65,
                "num_friends" : 70
            },
        }
        testuser.update(oldFormatAccountData)
        self._accountDB._updateMongoDocument(testuser)
        testAccount = self.showAccount(self.token)
        linkedAccounts = self.showLinkedAccounts(self.token)

        self.assertEqual(linkedAccounts['twitter'], { 'service_name': 'twitter', 'linked_screen_name' : 'testusera0', 'linked_user_id': '12345678'})
        self.assertEqual(linkedAccounts['facebook'], { 'service_name': 'facebook', 'linked_user_id' : '1234567', 'linked_name': 'Test User'})
        self.assertEqual(linkedAccounts['netflix'],
                {
                'service_name' : 'netflix',
                'token' : 'abcdefghijkl_7mon6p9zdWyDB_-9QU4w4jcAn4WZA3HotKLMrG4oBT2CsB_Mum6N24aXCrmqRxnBSrNNuxKkhF8sZE6BtSh0',
                'secret' : 'abcdefghijkl',
                'linked_user_id': 'abcdefghijsQujGoAtBtnwbTBpSjBx00o2PE2ASmO9kgw-',
                }
        )

        self.assertEqual(self._accountDB.checkLinkedAccountAlertHistory(self.user['user_id'], 'facebook', '1234567'), True)
        self.assertEqual(self._accountDB.checkLinkedAccountAlertHistory(self.user['user_id'], 'twitter', '12345678'), True)

    def tearDown(self):
        self.deleteAccount(self.token)
        pass

    def test_upgrade_linked_account(self):
        pass





class StampedAPIFacebookTest(StampedAPILinkedAccountHttpTest):

    def setUp(self):
        # Create a Facebook test user registered with our app, then use that test user to create a new Stamped account
        # Also create a user with standard stamped auth
        self.fb = globalFacebook()
        self.fb_app_access_token                    = self.fb.getAppAccessToken()
        (self.fb_user_token_a, self.fb_user_id_a)   = self._createFacebookTestUser(name='fbusera')
        (self.fb_user_token_b, self.fb_user_id_b)   = self._createFacebookTestUser(name='fbuserb')
        self.fb.createTestUserFriendship(self.fb_user_id_a, self.fb_user_token_a, self.fb_user_id_b, self.fb_user_token_b)
        (self.fUserA, self.fUserAToken)             = self.createFacebookAccount(self.fb_user_token_a, name='fUserA')
        (self.fUserB, self.fUserBToken)             = self.createFacebookAccount(self.fb_user_token_b, name='fUserB')
        (self.sUser, self.sUserToken)               = self.createAccount(name='sUser')

        self.privacy = False


    def tearDown(self):
        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.fUserBToken)
        self.deleteAccount(self.fUserAToken)
        self._clearFacebookTestUsers()
    #        self.assertTrue(self._deleteFacebookTestUser(self.fb_user_token_b, self.fb_user_id_b))
#        self.assertTrue(self._deleteFacebookTestUser(self.fb_user_token_a, self.fb_user_id_a))

## create two stamped accounts, give them both linked facebook id, and try to create a facebook account
## create one stamped account, link it to facebook account, try to create new stamped facebook account
#

class StampedAPIFacebookCreate(StampedAPIFacebookTest):

#    def test_invalid_facebook_token_login(self):
#        # attempt login with invalid facebook token
#        with expected_exception():
#            self.loginWithFacebook("BLAAARRGH!!")
#
#    def test_create_duplicate_facebook_auth_account(self):
#        with expected_exception():
#            self.createFacebookAccount(self.fb_user_token_a, name='fUser2')
#
#    def test_linked_account_with_used_facebook_id(self):
#    #        self.addLinkedAccount(
#    #            self.sUserToken,
#    #                { 'facebook_id'         : self.fb_user_id,
#    #                  'facebook_name'       : 'facebook_user',
#    #                  'facebook_token'      : self.fb_user_token,
#    #                  }
#    #        )
#        pass
#
#    def test_attempt_linked_account_change_for_facebook_auth_user(self):
#        pass
#
##    def test_fb_stamp_share(self):
##        self.entity = self.createEntity(self.fUserAToken)
##        self.stamp = self.createStamp(self.fUserAToken, self.entity['entity_id'])
##        path = 'v0/stamps/share/facebook.json'
##        data = {
##            "oauth_token"   : self.fUserAToken['access_token'],
##            "service_name"  : "facebook",
##            "stamp_id"      : self.stamp['stamp_id'],
##        }
##        self.handlePOST(path, data)
##
##        # Get news feed from Facebook to verify the wall post went through
##        result = self.fb.getNewsFeed(self.fb_user_id_a, self.fb_user_token_a)
##
##        import pprint
##        print('#### NEWS FEED RESULTS:')
##        pprint.pprint(result)
#
#
#    def test_valid_login(self):
#        # login with facebook user account
#        result = self.loginWithFacebook(self.fb_user_token_a)
#
#        # verify that the stamped user token and user_id are correct
#        self.assertEqual(result['user']['user_id'], self.fUserA['user_id'])
#
#    def test_find_by_facebook(self):
#        path = "users/find/facebook.json"
#        data = {
#            "oauth_token"   : self.fUserAToken['access_token'],
#        }
#
#        logs.info("self.fb_user_token_a %s" % self.fb_user_token_a)
#
#        self.async(lambda: self.handlePOST(path, data), [
#            lambda x: self.assertEqual(len(x), 1),
#            lambda x: self.assertEqual(x[0]['user_id'], self.fUserB['user_id']),
#            ])

    def test_friend_joined_activity_alert(self):
        self.async(lambda: self.showActivity(self.fUserAToken), [
            lambda x: self.assertEqual(len(x), 2),
            lambda x: self.assertEqual(x[0]['verb'], 'friend_facebook'),
            lambda x: self.assertEqual(x[0]['subjects'][0]['user_id'], self.fUserB['user_id']),
            ])

        result = self.showActivity(self.fUserAToken)
        print (result)

        # Make sure that another activity alert is not sent
        self.deleteAccount(self.fUserBToken)
        (self.fUserB, self.fUserBToken) = self.createFacebookAccount(self.fb_user_token_b, name='fUserB')
        self.async(lambda: self.showActivity(self.fUserAToken), [
            lambda x: self.assertEqual(len(x), 1),
            ])

class StampedAPIFacebookFind(StampedAPIFacebookTest):

    def test_find_by_facebook(self):
        path = "users/find/facebook.json"
        data = {
            "oauth_token"   : self.fUserAToken['access_token']
        }
        self.async(lambda: self.handleGET(path, data), [
            lambda x: self.assertEqual(len(x), 1),
            lambda x: self.assertEqual(x[0]['user_id'], self.fUserB['user_id']),
            ])

    def test_invite_facebook_collection(self):
        path = "users/invite/facebook/collection.json"
        data = {
            "oauth_token"   : self.fUserAToken['access_token'],
            }
        result = self.handleGET(path, data)

        # TODO: Add actual tests!
        from pprint import pprint
        pprint(result)


class StampedAPITwitterHttpTest(AStampedAPIHttpTestCase):

    def setUp(self):
        self.twitter = globalTwitter()

        # Create a new Stamped user with Twitter auth, also create a standard auth Stamped user
        self.tw_user_a_token            = TWITTER_USER_A0_TOKEN
        self.tw_user_a_secret           = TWITTER_USER_A0_SECRET
        self.tw_user_b_token            = TWITTER_USER_B0_TOKEN
        self.tw_user_b_secret           = TWITTER_USER_B0_SECRET

        self.twitter.createFriendship(self.tw_user_a_token, self.tw_user_a_secret, 'TestUserB0')
        (self.twUserA, self.twUserAToken) = self.createTwitterAccount(self.tw_user_a_token, self.tw_user_a_secret, name='twUserA')
        (self.twUserB, self.twUserBToken) = self.createTwitterAccount(self.tw_user_b_token, self.tw_user_b_secret, name='twUserB')
        (self.sUser, self.sUserToken) = self.createAccount(name='sUser')

    def tearDown(self):
        self.twitter.destroyFriendship(self.tw_user_a_token, self.tw_user_a_secret, 'TestUserB0')

        self.deleteAccount(self.sUserToken)
        self.deleteAccount(self.twUserAToken)
        self.deleteAccount(self.twUserBToken)


## create two stamped accounts, give them both linked twitter id, and try to create a twitter account
## create one stamped account, link it to twitter account, try to create new stamped twitter account
#

class StampedAPITwitterCreate(StampedAPITwitterHttpTest):

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

    def test_friend_joined_activity_alert(self):
        self.async(lambda: self.showActivity(self.twUserAToken), [
            lambda x: self.assertEqual(len(x), 2),
            lambda x: self.assertEqual(x[0]['verb'], 'friend_twitter'),
            lambda x: self.assertEqual(x[0]['subjects'][0]['user_id'], self.twUserB['user_id']),
            ])

        # Test friend joined again... It is important to run this only after the previous tests have passed, as otherwise
        #  the activity item may never get added to begin with
        self.deleteAccount(self.twUserBToken)
        (self.twUserB, self.twUserBToken) = self.createTwitterAccount(self.tw_user_b_token, self.tw_user_b_secret, name='twUserB')
        self.async(lambda: self.showActivity(self.twUserAToken), [
            lambda x: self.assertEqual(len(x), 1),
            ])


class StampedAPITwitterFind(StampedAPITwitterHttpTest):
    def test_find_by_twitter(self):
        path = "users/find/twitter.json"
        data = {
            "oauth_token"   : self.twUserAToken['access_token']
            }
        self.async(lambda: self.handleGET(path, data), [
                lambda x: self.assertEqual(len(x), 1),
                lambda x: self.assertEqual(x[0]['user_id'], self.twUserB['user_id']),
            ])

    def test_invite_twitter_collection(self):
        path = "users/invite/twitter/collection.json"
        data = {
            "oauth_token"   : self.twUserAToken['access_token'],
            }
        result = self.handleGET(path, data)
        from pprint import pprint
        pprint(result)

        ### TESTS TO ADD:
# Change bio from string to None
# Upload image data for avatar
# Test privacy settings

if __name__ == '__main__':
    main()

