#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import atexit, urllib, json, unittest

from StampedTestUtils import *

CLIENT_ID     = "stampedtest"
CLIENT_SECRET = "august1ftw"

_accounts  = []
_test_case = None

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')

class AStampedAPITestCase(AStampedTestCase):
    
    # _baseurl = "http://0.0.0.0:5000/api/v1"
    # _baseurl = "http://localhost:18000/v0"
    _baseurl = "http://localhost:8080/v0"
    # _baseurl = "https://dev.stamped.com/v0"
    
    _opener = StampedAPIURLOpener()
    client_auth = {
        'client_id': 'stampedtest',
        'client_secret': 'august1ftw'
    }
    
    def handleGET(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s?%s" % (self._baseurl, path, params)
        result = json.load(self._opener.open(url))
        
        return result
    
    def handlePOST(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s" % (self._baseurl, path)
        result = json.load(self._opener.open(url, params))
        
        return result
    
    ### CUSTOM ASSERTIONS
    def assertValidKey(self, key, length=24):
        self.assertIsInstance(key, basestring)
        self.assertLength(key, length)
    
    ### HELPER FUNCTIONS
    def createAccount(self, name='UserA'):
        global _test_case, _accounts
        _test_case = self
        
        path = "account/create.json"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "name": name,
            "email": "%s@stamped.com" % name, 
            "password": "12345",
            "screen_name": name
        }
        response = self.handlePOST(path, data)
        self.assertIn('user', response)
        self.assertIn('token', response)
        
        user  = response['user']
        token = response['token']
        
        _accounts.append((user, token))
        
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

def __cleanup():
    global _test_case, _accounts
    
    # attempt to clean up all accounts created in this session
    test = _test_case
    if test is not None:
        print "cleaning up..."
        
        for acct in _accounts:
            try:
                test.deleteAccount(acct[1])
            except:
                pass

def main():
    atexit.register(__cleanup)
    StampedTestRunner().run()

