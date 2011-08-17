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
    _opener = StampedAPIURLOpener()
    client_auth = {
        'client_id': 'stampedtest',
        'client_secret': 'august1ftw'
    }

    def handleGET(self, path, data):
        params = urllib.urlencode(data)
        result = json.load(self._opener.open("%s/%s?%s" % (self._baseurl, path, params)))
        return result
    
    def handlePOST(self, path, data):
        params = urllib.urlencode(data)
        result = json.load(self._opener.open("%s/%s" % (self._baseurl, path), params))
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


# ####### #
# ACCOUNT #
# ####### #

# class StampedAPIAccountTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.user, self.token) = self.createAccount()
#         self.privacy = False

#     def tearDown(self):
#         self.deleteAccount(self.token)

# class StampedAPIAccountSettings(StampedAPIAccountTest):
#     def test_post(self):
#         path = "account/settings.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "screen_name": "kevin",
#             "privacy": False,
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['privacy'], False)
#         self.privacy = result['privacy']

#     def test_get(self):
#         path = "account/settings.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['privacy'], self.privacy)

# class StampedAPIAccountUpdateProfile(StampedAPIAccountTest):
#     def test_update_profile(self):
#         path = "account/update_profile.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "bio": "My long biography goes here.",
#             "color": "333333,999999"
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['color_primary'], '333333')
#         self.assertEqual(result['color_secondary'], '999999')

# class StampedAPIAccountUpdateProfileImage(StampedAPIAccountTest):
#     def test_update_profile_image(self):
#         # TODO: this url is temporary!
#         url = 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg'
        
#         path = "account/update_profile_image.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "profile_image": url, 
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['profile_image'], url)


# #### #
# USER #
# #### #

# class StampedAPIUserTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.screen_names = ['UserA', 'UserB']

#     def tearDown(self):
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPIUsersShow(StampedAPIUserTest):
#     def test_show_user_id(self):
#         path = "users/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userA['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['screen_name'], self.userA['screen_name'])

#     def test_show_screen_name(self):
#         path = "users/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "screen_name": self.userA['screen_name']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['user_id'], self.userA['user_id'])

# class StampedAPIUsersLookup(StampedAPIUserTest):
#     def test_lookup_user_ids(self):
#         path = "users/lookup.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_ids": "%s,%s" % (
#                 self.userA['user_id'],
#                 self.userB['user_id']
#             )
#         }
#         result = self.handleGET(path, data)
#         self.assertLength(result, 2)
#         for user in result:
#             self.assertIn(user['screen_name'], self.screen_names)

#     def test_lookup_screen_names(self):
#         path = "users/lookup.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "screen_names": "%s,%s" % (
#                 self.userA['screen_name'],
#                 self.userB['screen_name']
#             )
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(len(result) >= 2)

# class StampedAPIUsersSearch(StampedAPIUserTest):
#     def test_search(self):
#         path = "users/search.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "q": "%s" % self.userA['screen_name'][:3]
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(len(result) >= 1)

# class StampedAPIUsersPrivacy(StampedAPIUserTest):
#     def test_privacy_user_id(self):
#         path = "users/privacy.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(result == False)

#     def test_privacy_screen_name(self):
#         path = "users/privacy.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "screen_name": self.userB['screen_name']
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(result == False)

#     def test_privacy_not_found(self):
#         path = "users/privacy.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "screen_name": 'unknownUserName'
#         }
#         try:
#             result = self.handleGET(path, data)
#             ret = False
#         except:
#             ret = True
#         self.assertTrue(ret)


# ########## #
# FRIENDSHIP #
# ########## #

# class StampedAPIFriendshipTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenA, self.userB)

#     def tearDown(self):
#         self.deleteFriendship(self.tokenA, self.userB)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPIFriendshipsCheck(StampedAPIFriendshipTest):
#     def test_check_friendship_success(self):
#         path = "friendships/check.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(result)

#     def test_check_friendship_fail(self):
#         path = "friendships/check.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "user_id": self.userA['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertFalse(result)

# class StampedAPIFriends(StampedAPIFriendshipTest):
#     def test_show_friends(self):
#         path = "friendships/friends.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userA['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result['user_ids']), 1)

# class StampedAPIFollowers(StampedAPIFriendshipTest):
#     def test_show_followers(self):
#         path = "friendships/followers.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result['user_ids']), 1)

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

# class StampedAPIBlockTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenA, self.userB)

#         path = "friendships/blocks/create.json"
#         data = {
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         friend = self.handlePOST(path, data)

#         self.assertIn('user_id', friend)
#         self.assertValidKey(friend['user_id'])

#     def tearDown(self):
#         path = "friendships/blocks/remove.json"
#         data = {
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         friend = self.handlePOST(path, data)

#         self.assertIn('user_id', friend)
#         self.assertValidKey(friend['user_id'])

#         self.deleteFriendship(self.tokenA, self.userB)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPICheckBlocks(StampedAPIBlockTest):
#     def test_check_block(self):
#         path = "friendships/blocks/check.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "user_id": self.userB['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertTrue(result)

#     def test_check_block_fail(self):
#         path = "friendships/blocks/check.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "user_id": self.userA['user_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertFalse(result)

# class StampedAPIBlocking(StampedAPIBlockTest):
#     def test_show_blocks(self):
#         path = "friendships/blocking.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result['user_ids']), 1)

# ###### #
# ENTITY #
# ###### #

# class StampedAPIEntityTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.user, self.token) = self.createAccount()
#         self.entity = self.createEntity(self.token)

#     def tearDown(self):
#         self.deleteEntity(self.token, self.entity['entity_id'])
#         self.deleteAccount(self.token)

# class StampedAPIEntitiesShow(StampedAPIEntityTest):
#     def test_show(self):
#         path = "entities/show.json"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['title'], self.entity['title'])

# class StampedAPIEntitiesUpdate(StampedAPIEntityTest):
#     def test_update(self):
#         path = "entities/update.json"
#         desc = "Gastropub in the West Village, NYC"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "desc": desc
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['desc'], desc)

# class StampedAPIEntitiesSearch(StampedAPIEntityTest):
#     def test_search(self):
#         path = "entities/search.json"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "q": self.entity['title'][3:]
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result[0]['title'][:3], self.entity['title'][:3])

# class StampedAPIEntitiesUTF8(StampedAPIEntityTest):
#     def test_utf8_update(self):
#         path = "entities/update.json"
#         desc = "๓๙ใ1฿"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "desc": desc
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['desc'], desc.decode('utf-8'))


# ##### #
# STAMP #
# ##### #

# class StampedAPIStampTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenB, self.userA)
#         self.entity = self.createEntity(self.tokenA)
#         self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])

#     def tearDown(self):
#         self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
#         self.deleteEntity(self.tokenA, self.entity['entity_id'])
#         self.deleteFriendship(self.tokenB, self.userA)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPIStampsShow(StampedAPIStampTest):
#     def test_show(self):
#         path = "stamps/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['blurb'], self.stamp['blurb'])

# class StampedAPIStampsUpdate(StampedAPIStampTest):
#     def test_show(self):
#         path = "stamps/update.json"
#         blurb = "Really, really delicious."
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)



# class StampedAPIStampMentionsTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenB, self.userA)
#         self.entity = self.createEntity(self.tokenA)
#         self.stampData = {
#             "oauth_token": self.tokenA['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name'],
#             "credit": self.userB['screen_name']
#         }
#         self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], self.stampData)

#     def tearDown(self):
#         self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
#         self.deleteEntity(self.tokenA, self.entity['entity_id'])
#         self.deleteFriendship(self.tokenB, self.userA)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPIStampsMentionsShow(StampedAPIStampMentionsTest):
#     def test_show(self):
#         path = "stamps/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['blurb'], self.stamp['blurb'])
#         self.assertEqual(
#             result['credit'][0]['screen_name'], 
#             self.stampData['credit']
#             )
#         self.assertTrue(len(result['mentions']) == 1)

# class StampedAPIStampsMentionsUpdate(StampedAPIStampMentionsTest):
#     def test_no_mentions(self):
#         path = "stamps/update.json"
#         blurb = "Really, really delicious."
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)
#         self.assertTrue(len(result['mentions']) == 0)

#     def test_two_mentions(self):
#         path = "stamps/update.json"
#         blurb = "Thanks again @%s! --@%s" % \
#                 (self.userB['screen_name'], self.userA['screen_name'])
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)
#         self.assertTrue(len(result['mentions']) == 2)

# class StampedAPIStampsCreditUpdate(StampedAPIStampMentionsTest):
#     def test_no_credit(self):
#         path = "stamps/update.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "credit": None
#         }
#         result = self.handlePOST(path, data)
#         self.assertTrue(len(result['credit']) == 0)

#     def test_two_credits(self):
#         path = "stamps/update.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "credit": "%s,%s" % (
#                 self.userA['screen_name'],
#                 self.userB['screen_name']
#             )
#         }
#         result = self.handlePOST(path, data)
#         self.assertTrue(len(result['credit']) == 2)


# ######## #
# COMMENTS #
# ######## #

# class StampedAPICommentTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenB, self.userA)
#         self.entity = self.createEntity(self.tokenA)
#         self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
#         self.blurbA = "Great place"
#         self.blurbB = "Glad you liked it!"
#         self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], self.blurbA)
#         self.commentB = self.createComment(self.tokenA, self.stamp['stamp_id'], self.blurbB)

#     def tearDown(self):
#         self.deleteComment(self.tokenA, self.commentB['comment_id'])
#         self.deleteComment(self.tokenB, self.commentA['comment_id'])
#         self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
#         self.deleteEntity(self.tokenA, self.entity['entity_id'])
#         self.deleteFriendship(self.tokenB, self.userA)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

# class StampedAPICommentsShow(StampedAPICommentTest):
#     def test_show(self):
#         path = "comments/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertIn(result[0]['blurb'],[self.blurbA, self.blurbB])
#         self.assertIn(result[1]['blurb'],[self.blurbA, self.blurbB])

# class StampedAPICommentsRemovePermissions(StampedAPICommentTest):
#     def test_remove_fail(self):
#         path = "comments/remove.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "comment_id": self.commentB['comment_id']
#         }
#         try:
#             result = self.handlePOST(path, data)
#             ret = False
#         except:
#             ret = True
#         self.assertTrue(ret)

# class StampedAPICommentsRemoveStampOwner(StampedAPICommentTest):
#     def test_show(self):
#         path = "comments/remove.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "comment_id": self.commentA['comment_id']
#         }
#         result = self.handlePOST(path, data)

#         # Add it back or else the test will fail...!
#         self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], self.blurbA)


# ########### #
# COLLECTIONS #
# ########### #

# class StampedAPICollectionTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         self.createFriendship(self.tokenB, self.userA)
#         self.entity = self.createEntity(self.tokenA)
#         self.stampA = self.createStamp(self.tokenA, self.entity['entity_id'])
#         self.blurbA = "Great place"
#         self.blurbB = "Glad you liked it!"
#         self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], self.blurbA)
#         self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.stampB = self.createStamp(self.tokenA, self.entity['entity_id'])
#         self.stampC = self.createStamp(self.tokenA, self.entity['entity_id'])

#     def tearDown(self):
#         self.deleteComment(self.tokenA, self.commentB['comment_id'])
#         self.deleteComment(self.tokenB, self.commentA['comment_id'])
#         self.deleteStamp(self.tokenA, self.stampA['stamp_id'])
#         self.deleteStamp(self.tokenA, self.stampB['stamp_id'])
#         self.deleteStamp(self.tokenA, self.stampC['stamp_id'])
#         self.deleteEntity(self.tokenA, self.entity['entity_id'])
#         self.deleteFriendship(self.tokenB, self.userA)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)

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

# class StampedAPICollectionsQuality(StampedAPICollectionTest):
#     def test_show(self):

#         self.commentC = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentD = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentE = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentF = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentG = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentH = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentI = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentJ = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
#         self.commentK = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)

#         path = "collections/inbox.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "quality": 1
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertEqual(len(result[-1]['comment_preview']), 11)

#         path = "collections/inbox.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "quality": 2
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertEqual(len(result[-1]['comment_preview']), 10)

#         path = "collections/inbox.json"
#         data = { 
#             "oauth_token": self.tokenB['access_token'],
#             "quality": 3
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(len(result), 3)
#         self.assertEqual(len(result[-1]['comment_preview']), 4)

#         self.deleteComment(self.tokenA, self.commentC['comment_id'])
#         self.deleteComment(self.tokenA, self.commentD['comment_id'])
#         self.deleteComment(self.tokenA, self.commentE['comment_id'])
#         self.deleteComment(self.tokenA, self.commentF['comment_id'])
#         self.deleteComment(self.tokenA, self.commentG['comment_id'])
#         self.deleteComment(self.tokenA, self.commentH['comment_id'])
#         self.deleteComment(self.tokenA, self.commentI['comment_id'])
#         self.deleteComment(self.tokenA, self.commentJ['comment_id'])
#         self.deleteComment(self.tokenA, self.commentK['comment_id'])


# ######## #
# ACTIVITY #
# ######## #

class StampedAPIActivityTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stampA = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.blurbA = "Great place"
        self.blurbB = "Glad you liked it!"
        self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.stampB = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.stampC = self.createStamp(self.tokenA, self.entity['entity_id'])

    def tearDown(self):
        self.deleteComment(self.tokenA, self.commentB['comment_id'])
        self.deleteComment(self.tokenB, self.commentA['comment_id'])
        self.deleteStamp(self.tokenA, self.stampA['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampB['stamp_id'])
        self.deleteStamp(self.tokenA, self.stampC['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPICollectionsShow(StampedAPIActivityTest):
    def test_show(self):
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

class StampedAPICollectionsMentions(StampedAPIActivityTest):
    def test_show_stamp_mention(self):
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": self.entity['entity_id'],
            "blurb": "Thanks @%s!" % self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, self.entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])


"""


class StampedAPStampTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "User",
            "last_name": "A", 
            "email": "usera@stamped.com", 
            "password": "******",
            "screen_name": "UserA"
        }
        
        self.userA = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userA)
        
        data = {
            "first_name": "User",
            "last_name": "B", 
            "email": "userb@stamped.com", 
            "password": "******",
            "screen_name": "UserB"
        }
        
        self.userB = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userB)
        
        path = "entities/create.json"
        data = {
            "authenticated_user_id": userA,
            "title": "Little Owl ",
            "desc": "American food in the West Village", 
            "category": "food",
            "subcategory": "restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        self.entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(self.entityID)
        
    def test_create_show_update(self):
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village.", 
            "image": "image.png"
        }
        stampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(stampID)
        
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userB,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village. Thanks, @UserA.", 
            "image": "image.png",
            "credit": "UserA"
        }
        restampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(restampID)
        
        path = "stamps/update.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID,
            "image": "image2.png"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], stampID)
        
        path = "stamps/show.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['image'], 'image2.png')
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.restampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "account/remove.json"
        data = {"authenticated_user_id": userA}
        resultA = self.handlePOST(path, data)
        self.assertTrue(resultA)
        
        data = {"authenticated_user_id": userB}
        resultB = self.handlePOST(path, data)
        self.assertTrue(resultB)

class StampedAPIFriendshipTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
    
    
    
        TODO
        # TODO
        TODO
        
        
        
        
        
        path = "account/create.json"
        data = {
            "first_name": "Kevin",
            "last_name": "Palms", 
            "email": "kevin@stamped.com", 
            "password": "******",
            "screen_name": "kpalms"
        }
        userA = self.handlePOST(path, data)['user_id']
        data = {
            "first_name": "Robby",
            "last_name": "Stein", 
            "email": "robby@stamped.com", 
            "password": "******",
            "screen_name": "rmstein"
        }
        userB = self.handlePOST(path, data)['user_id']
        if len(userA) == 24 and len(userB) == 24:
            print 'DATA: %s' % path
        else:
            print 'FAIL: %s' % path
            print userID
            raise Exception
            
            
        path = "account/settings.json"
        data = {
            "authenticated_user_id": userA,
            "privacy": False
        }
        result = self.handlePOST(path, data)
        data = {
            "authenticated_user_id": userB,
            "privacy": False
        }
        result = self.handlePOST(path, data)
        if result['privacy'] == False:
            print 'DATA: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
        
        
        path = "friendships/create.json"
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
            
        
        path = "friendships/check.json"
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
            
            
        path = "friendships/friends.json"
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
            
            
        path = "friendships/followers.json"
        data = {
            "authenticated_user_id": userB
        }
        result = self.handleGET(path, data)
        if len(result['user_ids']) == 1:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
            
            
        path = "friendships/approve.json"
        data = {
            "authenticated_user_id": userA
        }
        print 'SKIP: %s' % path
            
            
        path = "friendships/pending.json"
        data = {
            "authenticated_user_id": userA,
            "user_id": userB
        }
        print 'SKIP: %s' % path
        
        
        path = "friendships/remove.json"
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
            
            
        path = "account/remove.json"
        data = { "authenticated_user_id": userA }
        resultA = self.handlePOST(path, data)
        data = { "authenticated_user_id": userB }
        resultB = self.handlePOST(path, data)
        if resultA and resultB:
            print 'DATA: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception

        path = "account/create.json"
        data = {
            "first_name": "User",
            "last_name": "A", 
            "email": "usera@stamped.com", 
            "password": "******",
            "screen_name": "UserA"
        }
        
        self.userA = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userA)
        
        data = {
            "first_name": "User",
            "last_name": "B", 
            "email": "userb@stamped.com", 
            "password": "******",
            "screen_name": "UserB"
        }
        
        self.userB = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userB)
        
        path = "entities/create.json"
        data = {
            "authenticated_user_id": userA,
            "title": "Little Owl ",
            "desc": "American food in the West Village", 
            "category": "food",
            "subcategory": "restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(entityID)
        
    def test_create_show_update(self):
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village.", 
            "image": "image.png"
        }
        stampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(stampID)
        
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userB,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village. Thanks, @UserA.", 
            "image": "image.png",
            "credit": "UserA"
        }
        restampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(restampID)
        
        path = "stamps/update.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID,
            "image": "image2.png"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], stampID)
        
        path = "stamps/show.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['image'], 'image2.png')
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.restampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "account/remove.json"
        data = {"authenticated_user_id": userA}
        resultA = self.handlePOST(path, data)
        self.assertTrue(resultA)
        
        data = {"authenticated_user_id": userB}
        resultB = self.handlePOST(path, data)
        self.assertTrue(resultB)
"""

if __name__ == '__main__':
    unittest.main()

