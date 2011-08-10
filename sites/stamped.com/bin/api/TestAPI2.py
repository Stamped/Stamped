#!/usr/bin/env python

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

    def createEntity(self, token, data=None):
        path = "entities/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "title": "Good Food",
                "desc": "American food in America", 
                "category": "food",
                "subcategory": "restaurant",
                "address": "123 Main Street, Peoria, IL",
                "coordinates": "40.714623,-74.006605"
            }
        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']
        response = self.handlePOST(path, data)
        self.assertIn('entity', response)
        entity = response['entity']
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


# ####### #
# ACCOUNT #
# ####### #

class StampedAPIAccountTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.privacy = True

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
        url = 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg'
        
        path = "account/update_profile_image.json"
        data = {
            "oauth_token": self.token['access_token'],
            "profile_image": url, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['profile_image'], url)


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
        self.assertTrue(result)

    def test_privacy_screen_name(self):
        path = "users/privacy.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "screen_name": self.userB['screen_name']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result)
    

# ###### #
# ENTITY #
# ###### #

class StampedAPIEntityTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.entity = self.createEntity(self.token)

    def tearDown(self):
        self.deleteEntity(self.token)
        self.deleteAccount(self.token)

# class StampedAPIEntitiesShow(StampedAPIEntityTest):
#     def test_show(self):
#         path = "entities/show.json"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": entity['entity_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['title'], entity['title'])

"""

class StampedAPIEntityTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "Kevin",
            "last_name": "Palms", 
            "email": "kevin@stamped.com", 
            "password": "******",
            "screen_name": "kpalms"
        }
        
        response = self.handlePOST(path, data)
        self.userID = response['user_id']
        self.assertValidKey(self.userID)
    
    def test_create_show_update(self):
        path = "entities/create.json"
        desc = "American food in the West Village"
        data = {
            "authenticated_user_id": self.userID,
            "title": "Little Owl",
            "desc": desc, 
            "category": "Restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(entityID)
        
        path = "entities/show.json"
        data = { "entity_id": entityID }
        
        entity = self.handleGET(path, data)
        self.assertEqual(entity['desc'], desc)
        
        desc2 = "Gastropub in the West Village, NYC"
        path = "entities/update.json"
        data = {
            "authenticated_user_id": self.userID,
            "entity_id": entityID,
            "desc": desc2, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(entity['desc'], desc2)
    
    def test_search(self):
        path = "entities/search.json"
        data = {
            "authenticated_user_id": self.userID,
            "q": "Litt"
        }
        
        entities = self.handleGET(path, data)
        self.assertTrue(len(entities) > 0)
    
    def test_remove(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userID,
            "entity_id": entityID
        }
        
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "account/remove.json"
        data = { "authenticated_user_id": self.userID }
        
        result = self.handlePOST(path, data)
        self.assertTrue(result)

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

