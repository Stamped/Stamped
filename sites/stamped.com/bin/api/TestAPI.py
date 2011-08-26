#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import sys, thread, urllib, json
import os, unittest

CLIENT_ID = "stampedtest"
CLIENT_SECRET = "august1ftw"

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')



class AStampedAPITestCase(unittest.TestCase):

    _baseurl = "http://0.0.0.0:5000/api/v1"
    # _baseurl = "http://localhost:8080/v0"

    _opener = StampedAPIURLOpener()
    client_auth = {
        'client_id': 'stampedtest',
        'client_secret': 'august1ftw'
    }

    def handleGET(self, path, data):
        params = urllib.urlencode(data)
        result = json.load(self._opener.open("%s/%s?%s" % \
            (self._baseurl, path, params)))
        return result
    
    def handlePOST(self, path, data):
        params = urllib.urlencode(data)
        # print params
        result = json.load(self._opener.open("%s/%s" % \
            (self._baseurl, path), params))
        return result

    ### DEFAULT ASSERTIONS
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
        
    def assertIn(self, a, b):
        self.assertTrue((a in b) == True)

    def assertLength(self, a, size):
        self.assertTrue(len(a) == size)
    
    ### CUSTOM ASSERTIONS
    def assertValidKey(self, key, length=24):
        self.assertIsInstance(key, basestring)
        self.assertLength(key, length)

    ### HELPER FUNCTIONS
    def createAccount(self, name='UserA'):
        path = "account/create.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "first_name": name,
            "last_name": "Test", 
            "email": "%s@stamped.com" % name, 
            "password": "12345",
            "screen_name": name
        }
        response = self.handlePOST(path, data)
        self.assertIn('user', response)
        self.assertIn('token', response)
        
        user = response['user']
        token = response['token']

        self.assertValidKey(user['user_id'])
        self.assertValidKey(token['access_token'], 22)
        self.assertValidKey(token['refresh_token'], 43)

        return user, token

    def deleteAccount(self, token):
        path = "account/remove.json"
        data = { "oauth_token": token['access_token'] }
        result = self.handlePOST(path, data)
        self.assertTrue(result)


    def createFriendship(self, token, friend):
        path = "friendships/create.json"
        data = {
            "oauth_token": token['access_token'],
            "user_id": friend['user_id']
        }
        friend = self.handlePOST(path, data)

        self.assertIn('user_id', friend)
        self.assertValidKey(friend['user_id'])

        return friend

    def deleteFriendship(self, token, friend):
        path = "friendships/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "user_id": friend['user_id']
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)


    def createEntity(self, token, data=None):
        path = "entities/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "title": "Kanye West",
                "subtitle": "Hubristic Rapper",
                "desc": "Hip-hop artist", 
                "category": "music",
                "subcategory": "artist",
            }
        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']
        entity = self.handlePOST(path, data)
        self.assertValidKey(entity['entity_id'])

        return entity

    def createPlaceEntity(self, token, data=None):
        path = "entities/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "title": "Good Food",
                "subtitle": "Peoria, IL",
                "desc": "American food in America", 
                "category": "food",
                "subcategory": "restaurant",
                "address": "123 Main Street, Peoria, IL",
                "coordinates": "40.714623,-74.006605"
            }
        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']
        entity = self.handlePOST(path, data)
        self.assertValidKey(entity['entity_id'])

        return entity

    def deleteEntity(self, token, entityId):
        path = "entities/remove.json"
        data = { 
            "oauth_token": token['access_token'],
            "entity_id": entityId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    
    def createStamp(self, token, entityId, data=None):
        path = "stamps/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "entity_id": entityId,
                "blurb": "Best restaurant in America",
            }
        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']
        stamp = self.handlePOST(path, data)
        self.assertValidKey(stamp['stamp_id'])

        return stamp

    def deleteStamp(self, token, stampId):
        path = "stamps/remove.json"
        data = { 
            "oauth_token": token['access_token'],
            "stamp_id": stampId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    
    def createComment(self, token, stampId, blurb="Sample Comment Text"):
        path = "comments/create.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId,
            "blurb": blurb,
        }
        comment = self.handlePOST(path, data)
        self.assertValidKey(comment['comment_id'])

        return comment

    def deleteComment(self, token, commentId):
        path = "comments/remove.json"
        data = { 
            "oauth_token": token['access_token'],
            "comment_id": commentId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    
    def createFavorite(self, token, entityId, stampId=None):
        path = "favorites/create.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId,
        }
        if stampId != None:
            data['stamp_id'] = stampId
        favorite = self.handlePOST(path, data)
        self.assertValidKey(favorite['favorite_id'])

        return favorite

    def deleteFavorite(self, token, entityId):
        path = "favorites/remove.json"
        data = { 
            "oauth_token": token['access_token'],
            "entity_id": entityId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

"""
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
            "screen_name": "kevin",
            "privacy": False,
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
        path = "account/update_profile.json"
        data = {
            "oauth_token": self.token['access_token'],
            "bio": "My long biography goes here.",
            "color": "333333,999999"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['color_primary'], '333333')
        self.assertEqual(result['color_secondary'], '999999')

class StampedAPIAccountUpdateProfileImage(StampedAPIAccountTest):
    def test_update_profile_image(self):
        # TODO: this url is temporary!
        url = 'https://si0.twimg.com/profile_images/147088134/'
        url = url + 'twitter_profile_reasonably_small.jpg'
        
        path = "account/update_profile_image.json"
        data = {
            "oauth_token": self.token['access_token'],
            "profile_image": url, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['profile_image'], url)

# ##### #
# OAUTH #
# ##### #

class StampedAPIOAuthTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')

    def tearDown(self):
        self.deleteAccount(self.tokenA)

class StampedAPIOAuthLogin(StampedAPIOAuthTest):
    def test_login(self):
        path = "oauth2/login.json"
        data = { 
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "screen_name": self.userA['screen_name'],
            "password": "12345"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['access_token']) == 22)
        self.assertTrue(len(result['refresh_token']) == 43)

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


# #### #
# USER #
# #### #

class StampedAPIUserTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.screen_names = ['usera', 'userb']

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
        result = self.handleGET(path, data)
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
        result = self.handleGET(path, data)
        self.assertTrue(len(result) >= 2)

class StampedAPIUsersSearch(StampedAPIUserTest):
    def test_search(self):
        path = "users/search.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "q": "%s" % self.userA['screen_name'][:3]
        }
        result = self.handleGET(path, data)
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
        try:
            result = self.handleGET(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)


# ########## #
# FRIENDSHIP #
# ########## #

class StampedAPIFriendshipTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenA, self.userB)

    def tearDown(self):
        self.deleteFriendship(self.tokenA, self.userB)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIFriendshipsCheck(StampedAPIFriendshipTest):
    def test_check_friendship_success(self):
        path = "friendships/check.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id_a": self.userA['user_id'],
            "user_id_b": self.userB['user_id'],
        }
        result = self.handleGET(path, data)
        self.assertTrue(result)

    def test_check_friendship_fail(self):
        path = "friendships/check.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id_a": self.userB['user_id'],
            "user_id_b": self.userA['user_id'],
        }
        result = self.handleGET(path, data)
        self.assertFalse(result)

    def test_check_friendship_count(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['num_friends'], 1)

    def test_check_follower_count(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userB['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['num_followers'], 1)

class StampedAPIFriends(StampedAPIFriendshipTest):
    def test_show_friends(self):
        path = "friendships/friends.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result['user_ids']), 1)

class StampedAPIFollowers(StampedAPIFriendshipTest):
    def test_show_followers(self):
        path = "friendships/followers.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result['user_ids']), 1)

#     def REWRITE_ME(self):
#         path = "friendships/approve.json"
#         data = {
#             "authenticated_user_id": userA
#         }
#         print 'SKIP: %s' % path
            
            
#         path = "friendships/pending.json"
#         data = {
#             "authenticated_user_id": userA,
#             "user_id": userB
#         }
#         print 'SKIP: %s' % path


# ###### #
# BLOCKS #
# ###### #

class StampedAPIBlockTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenA, self.userB)

        path = "friendships/blocks/create.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        friend = self.handlePOST(path, data)

        self.assertIn('user_id', friend)
        self.assertValidKey(friend['user_id'])

    def tearDown(self):
        path = "friendships/blocks/remove.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        friend = self.handlePOST(path, data)

        self.assertIn('user_id', friend)
        self.assertValidKey(friend['user_id'])

        self.deleteFriendship(self.tokenA, self.userB)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPICheckBlocks(StampedAPIBlockTest):
    def test_check_block(self):
        path = "friendships/blocks/check.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result)

    def test_check_block_fail(self):
        path = "friendships/blocks/check.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertFalse(result)

class StampedAPIBlocking(StampedAPIBlockTest):
    def test_show_blocks(self):
        path = "friendships/blocking.json"
        data = { 
            "oauth_token": self.tokenA['access_token']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result['user_ids']), 1)

# ###### #
# ENTITY #
# ###### #

class StampedAPIEntityTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.entity = self.createEntity(self.token)

    def tearDown(self):
        self.deleteEntity(self.token, self.entity['entity_id'])
        self.deleteAccount(self.token)

class StampedAPIEntitiesShow(StampedAPIEntityTest):
    def test_show(self):
        path = "entities/show.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['title'], self.entity['title'])

class StampedAPIEntitiesUpdate(StampedAPIEntityTest):
    def test_update(self):
        path = "entities/update.json"
        desc = "Gastropub in the West Village, NYC"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            # "category": '',
            "desc": desc,
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc)

class StampedAPIEntitiesUTF8(StampedAPIEntityTest):
    def test_utf8_update(self):
        path = "entities/update.json"
        desc = "๓๙ใ1฿"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            "desc": desc
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc.decode('utf-8'))

class StampedAPIEntitiesSearch(StampedAPIEntityTest):
    def test_search(self):
        path = "entities/search.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "q": self.entity['title'][:3]
        }
        result = self.handleGET(path, data)
        self.assertEqual(result[0]['title'][:3], self.entity['title'][:3])

# ###### #
# PLACE #
# ###### #

class StampedAPIPlaceTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.entity = self.createPlaceEntity(self.token)

    def tearDown(self):
        self.deleteEntity(self.token, self.entity['entity_id'])
        self.deleteAccount(self.token)

class StampedAPIPlacesShow(StampedAPIPlaceTest):
    def test_show(self):
        path = "entities/show.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['title'], self.entity['title'])

class StampedAPIPlacesUpdate(StampedAPIPlaceTest):
    def test_update(self):
        path = "entities/update.json"
        desc = "Gastropub in the West Village, NYC"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            "desc": desc,
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc)

class StampedAPIPlacesUTF8(StampedAPIPlaceTest):
    def test_utf8_update(self):
        path = "entities/update.json"
        desc = "๓๙ใ1฿"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            "desc": desc
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc.decode('utf-8'))

class StampedAPIPlacesSearch(StampedAPIPlaceTest):
    def test_search(self):
        path = "entities/search.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "q": self.entity['title'][:3]
        }
        result = self.handleGET(path, data)
        self.assertEqual(result[0]['title'][:3], self.entity['title'][:3])


# ##### #
# STAMP #
# ##### #

class StampedAPIStampTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampsShow(StampedAPIStampTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])

class StampedAPIStampsUpdate(StampedAPIStampTest):
    def test_show(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)



class StampedAPIStampMentionsTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": self.entity['entity_id'],
            "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name'],
            "credit": self.userB['screen_name']
        }
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], \
            self.stampData)

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampsMentionsShow(StampedAPIStampMentionsTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])
        self.assertEqual(
            result['credit'][0]['screen_name'], 
            self.stampData['credit']
            )
        self.assertTrue(len(result['mentions']) == 1)

class StampedAPIStampsMentionsUpdate(StampedAPIStampMentionsTest):
    def test_no_mentions(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        # self.assertTrue(len(result['mentions']) == 0)
        self.assertTrue('mentions' not in result)

    def test_two_mentions(self):
        path = "stamps/update.json"
        blurb = "Thanks again @%s! --@%s" % \
                (self.userB['screen_name'], self.userA['screen_name'])
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        self.assertTrue(len(result['mentions']) == 2)

class StampedAPIStampsCreditUpdate(StampedAPIStampMentionsTest):
    def test_no_credit(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": None
        }
        result = self.handlePOST(path, data)
        # self.assertTrue(len(result['credit']) == 0)
        self.assertTrue('credit' not in result)

    def test_two_credits(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": "%s,%s" % (
                self.userA['screen_name'],
                self.userB['screen_name']
            )
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['credit']) == 2)


# ########### #
# STAMP PLACE #
# ########### #

class StampedAPIStampPlaceTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createPlaceEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampPlacesShow(StampedAPIStampPlaceTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])

class StampedAPIStampPlacesUpdate(StampedAPIStampPlaceTest):
    def test_show(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)

class StampedAPIStampPlaceMentionsTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createPlaceEntity(self.tokenA)
        self.stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": self.entity['entity_id'],
            "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name'],
            "credit": self.userB['screen_name']
        }
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], \
            self.stampData)

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampPlacesMentionsShow(StampedAPIStampPlaceMentionsTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])
        self.assertEqual(
            result['credit'][0]['screen_name'], 
            self.stampData['credit']
            )
        self.assertTrue(len(result['mentions']) == 1)

class StampedAPIStampPlacesMentionsUpdate(StampedAPIStampPlaceMentionsTest):
    def test_no_mentions(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        self.assertTrue('mentions' not in result)

    def test_two_mentions(self):
        path = "stamps/update.json"
        blurb = "Thanks again @%s! --@%s" % \
                (self.userB['screen_name'], self.userA['screen_name'])
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        self.assertTrue(len(result['mentions']) == 2)

class StampedAPIStampPlacesCreditUpdate(StampedAPIStampPlaceMentionsTest):
    def test_no_credit(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": None
        }
        result = self.handlePOST(path, data)
        self.assertTrue('credit' not in result)

    def test_two_credits(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": "%s,%s" % (
                self.userA['screen_name'],
                self.userB['screen_name']
            )
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['credit']) == 2)


# ######## #
# COMMENTS #
# ######## #

class StampedAPICommentTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.blurbA = "Great place"
        self.blurbB = "Glad you liked it!"
        self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stamp['stamp_id'], \
            self.blurbB)

    def tearDown(self):
        self.deleteComment(self.tokenA, self.commentB['comment_id'])
        self.deleteComment(self.tokenB, self.commentA['comment_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPICommentsShow(StampedAPICommentTest):
    def test_show(self):
        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn(result[0]['blurb'],[self.blurbA, self.blurbB])
        self.assertIn(result[1]['blurb'],[self.blurbA, self.blurbB])

class StampedAPICommentsRemovePermissions(StampedAPICommentTest):
    def test_remove_fail(self):
        path = "comments/remove.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "comment_id": self.commentB['comment_id']
        }
        try:
            result = self.handlePOST(path, data)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

class StampedAPICommentsRemoveStampOwner(StampedAPICommentTest):
    def test_show(self):
        path = "comments/remove.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "comment_id": self.commentA['comment_id']
        }
        result = self.handlePOST(path, data)

        # Add it back or else the test will fail...!
        self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurbA)

class StampedAPICommentsMentions(StampedAPICommentTest):
    def test_mention(self):
        self.blurb = "Nice job @%s!" % self.userA['screen_name']
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_fake_double_mention(self):
        self.blurb = "Nice job @%s! You rock @%s." % \
            (self.userA['screen_name'], self.userA['screen_name'])
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])
        self.assertTrue(len(result[2]['mentions']) == 1)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_double_mention(self):
        self.blurb = "Nice job @%s! You rock @%s." % \
            (self.userA['screen_name'], self.userB['screen_name'])
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])
        self.assertTrue(len(result[2]['mentions']) == 2)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

class StampedAPICommentsReply(StampedAPICommentTest):
    def test_reply(self):
        self.blurb = "@%s thanks!" % self.userA['screen_name']
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_upper(self):
        self.blurb = "@%s thanks!" % str(self.userA['screen_name']).upper()
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_lower(self):
        self.blurb = "@%s thanks!" % str(self.userA['screen_name']).lower()
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn('mentions', result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_empty(self):
        self.blurb = "@ thanks!"
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue('mentions' not in result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_email(self):
        self.blurb = "kevin@stamped.com thanks!"
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue('mentions' not in result[2])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

class StampedAPICommentsText(StampedAPICommentTest):
    def test_utf8(self):
        blurb = '“Iñtërnâtiônàlizætiøn”'
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[2]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_doublequotes(self):
        blurb = '"test"'
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[2]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_quotes(self):
        blurb = '\'test\''
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[2]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_other_characters(self):
        blurb = '"test" & \'%test\''
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[2]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

"""

# ########### #
# COLLECTIONS #
# ########### #

class StampedAPICollectionTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entityA = self.createEntity(self.tokenA)
        self.entityB = self.createEntity(self.tokenA)
        self.entityC = self.createEntity(self.tokenA)
        self.stampA = self.createStamp(self.tokenA, self.entityA['entity_id'])
        self.blurbA = "Great place"
        self.blurbB = "Glad you liked it!"
        self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], \
            self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.stampB = self.createStamp(self.tokenA, self.entityB['entity_id'])
        self.stampC = self.createStamp(self.tokenA, self.entityC['entity_id'])

    def tearDown(self):
        self.deleteComment(self.tokenA, self.commentB['comment_id'])
        self.deleteComment(self.tokenB, self.commentA['comment_id'])
        self.deleteStamp(self.tokenA, self.stampA['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampB['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampC['stamp_id'])
        self.deleteEntity(self.tokenA, self.entityA['entity_id'])
        self.deleteEntity(self.tokenA, self.entityB['entity_id'])
        self.deleteEntity(self.tokenA, self.entityC['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

# class StampedAPICollectionsShow(StampedAPICollectionTest):
#     def test_inbox(self):
#         path = "collections/inbox.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

#     def test_user_screen_name(self):
#         path = "collections/user.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "screen_name": self.userA['screen_name']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

#     def test_user_user_id(self):
#         path = "collections/user.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "user_id": self.userA['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

class StampedAPICollectionsQuality(StampedAPICollectionTest):
    def test_show(self):

        self.commentC = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentD = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentE = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentF = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentG = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentH = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentI = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentJ = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.commentK = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)

        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "quality": 1
        }
        result = self.handleGET(path, data)
        print '\n%s\n' % result
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[-1]['comment_preview']), 11)

        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "quality": 2
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[-1]['comment_preview']), 10)

        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "quality": 3
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[-1]['comment_preview']), 4)

        self.deleteComment(self.tokenA, self.commentC['comment_id'])
        self.deleteComment(self.tokenA, self.commentD['comment_id'])
        self.deleteComment(self.tokenA, self.commentE['comment_id'])
        self.deleteComment(self.tokenA, self.commentF['comment_id'])
        self.deleteComment(self.tokenA, self.commentG['comment_id'])
        self.deleteComment(self.tokenA, self.commentH['comment_id'])
        self.deleteComment(self.tokenA, self.commentI['comment_id'])
        self.deleteComment(self.tokenA, self.commentJ['comment_id'])
        self.deleteComment(self.tokenA, self.commentK['comment_id'])


"""
# ######### #
# FAVORITES #
# ######### #

class StampedAPIFavoriteTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.favorite = self.createFavorite(self.tokenB, self.entity['entity_id'])

    def tearDown(self):
        self.deleteFavorite(self.tokenB, self.entity['entity_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIFavoritesShow(StampedAPIFavoriteTest):
    def test_show(self):
        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

    def test_show_nothing(self):
        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

class StampedAPIFavoritesAlreadyComplete(StampedAPIFavoriteTest):
    def test_create_completed(self):
        self.entityB = self.createEntity(self.tokenB)
        self.stampB = self.createStamp(self.tokenB, self.entityB['entity_id'])
        self.favoriteB = self.createFavorite(self.tokenB, self.entityB['entity_id'])

        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['complete'])

        self.deleteFavorite(self.tokenB, self.entityB['entity_id'])
        self.deleteStamp(self.tokenB, self.stampB['stamp_id'])
        self.deleteEntity(self.tokenB, self.entityB['entity_id'])

class StampedAPIFavoritesAlreadyOnList(StampedAPIFavoriteTest):
    def test_already_on_list(self):
        try:
            self.favoriteB = self.createFavorite(self.tokenB, self.entity['entity_id'])
            ret = False
        except:
            ret = True
        self.assertTrue(ret)



# ######## #
# ACTIVITY #
# ######## #

class StampedAPIActivityTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entityA = self.createEntity(self.tokenA)
        self.stampA = self.createStamp(self.tokenA, self.entityA['entity_id'])
        self.blurbA = "Great place"
        self.blurbB = "Glad you liked it!"
        self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], \
            self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], \
            self.blurbB)
        self.entityB = self.createEntity(self.tokenA)
        self.entityC = self.createEntity(self.tokenA)
        self.stampB = self.createStamp(self.tokenA, self.entityB['entity_id'])
        self.stampC = self.createStamp(self.tokenA, self.entityC['entity_id'])

    def tearDown(self):
        self.deleteComment(self.tokenA, self.commentB['comment_id'])
        self.deleteComment(self.tokenB, self.commentA['comment_id'])
        self.deleteStamp(self.tokenA, self.stampA['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampB['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampC['stamp_id'])
        self.deleteEntity(self.tokenA, self.entityA['entity_id'])
        self.deleteEntity(self.tokenA, self.entityB['entity_id'])
        self.deleteEntity(self.tokenA, self.entityC['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIActivityShow(StampedAPIActivityTest):
    def test_show(self):
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

class StampedAPIActivityMentions(StampedAPIActivityTest):
    def test_show_stamp_mention(self):
        entity = self.createEntity(self.tokenA)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Thanks @%s!" % self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

class StampedAPIActivityCredit(StampedAPIActivityTest):
    def test_show_stamp_credit(self):
        entity = self.createEntity(self.tokenA)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Great spot!",
            "credit": self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

class StampedAPIActivityMentionAndCredit(StampedAPIActivityTest):
    def test_show_stamp_mention_and_credit(self):
        entity = self.createEntity(self.tokenA)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Thanks @%s!" % self.userB['screen_name'],
            "credit": self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['genre'] == 'restamp')

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])


"""
"""
        
        
        path = "friendships/blocks/create.json"
        data = {
            "authenticated_user_id": userA,
            "user_id": userB
        }
        result = self.handlePOST(path, data)    
        if result['user_id'] == userB:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
            
        
        path = "friendships/blocks/check.json"
        data = {
            "authenticated_user_id": userA,
            "user_id": userB
        }
        result = self.handleGET(path, data)
        if result == True:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
            
            
        path = "friendships/blocking.json"
        data = {
            "authenticated_user_id": userA
        }
        result = self.handleGET(path, data)
        if len(result['user_ids']) == 1:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
        
        
        path = "friendships/blocks/remove.json"
        data = {
            "authenticated_user_id": userA,
            "user_id": userB
        }
        result = self.handlePOST(path, data)
        if result == True:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
            
          
"""

if __name__ == '__main__':
    unittest.main()

