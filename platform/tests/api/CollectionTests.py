#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

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
        self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.stampB = self.createStamp(self.tokenA, self.entityB['entity_id'])
        self.stampC = self.createStamp(self.tokenA, self.entityC['entity_id'], credit=self.userB['screen_name'])

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

class StampedAPICollectionsShow(StampedAPICollectionTest):
    def test_inbox(self):
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "scope" : "inbox",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 3), 
                   lambda x: self.assertTrue(x[0]['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb']), 
        ])
    
    def test_user_user_id(self):
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userA['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 3), 
                   lambda x: self.assertTrue(x[0]['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb']), 
        ])
    
    def test_credit_user_id(self):
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id'],
            "scope" : "credit",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 1), 
                   lambda x: self.assertTrue(x[0]['contents'][-1]['blurb'] == self.stampC['contents'][-1]['blurb']), 
        ])


class StampedAPICollectionsSearch(StampedAPICollectionTest):
    def test_inbox(self):
        path = "stamps/search.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "scope" : "inbox",
            "query" : "america",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 3), 
        ])


class StampedAPICollectionsLikes(StampedAPICollectionTest):
    def test_like(self):
        path = "stamps/likes/create.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stampA['stamp_id']
        }
        result = self.handlePOST(path, data)

        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "scope" : "inbox",
        }
        
        def _validate_result(result):
            self.assertEqual(len(result), 3)
            
            for stamp in result:
                if stamp['stamp_id'] == self.stampA['stamp_id']:
                    self.assertTrue(stamp['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb'])
                    self.assertTrue(stamp['is_liked'])
        
        self.async(lambda: self.handleGET(path, data), _validate_result)
        
        # User A should not have "is_liked"
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "scope" : "inbox",
        }
        
        def _validate_result2(result):
            self.assertEqual(len(result), 3)
            
            for stamp in result:
                if stamp['stamp_id'] == self.stampA['stamp_id']:
                    self.assertTrue(stamp['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb'])
                    self.assertTrue(stamp['is_liked'] == False)
        
        self.async(lambda: self.handleGET(path, data), _validate_result2)
    
class StampedAPICollectionsTodos(StampedAPICollectionTest):
    def test_todo(self):
        todo = self.createTodo(self.tokenB, self.entityA['entity_id'])
        
        # User B should have "is_todo=True"
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "scope" : "inbox",
        }
        
        def _validate_result(result):
            self.assertEqual(len(result), 3)
            
            for stamp in result:
                if stamp['stamp_id'] == self.stampA['stamp_id']:
                    self.assertTrue(stamp['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb'])
                    self.assertTrue(stamp['is_todo'])
        
        self.async(lambda: self.handleGET(path, data), _validate_result)
        
        # User A should not have "is_todo"
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "scope" : "inbox",
        }
        
        def _validate_result2(result):
            self.assertEqual(len(result), 3)
            
            for stamp in result:
                if stamp['stamp_id'] == self.stampA['stamp_id']:
                    self.assertTrue(stamp['contents'][-1]['blurb'] == self.stampA['contents'][-1]['blurb'])
                    self.assertTrue(stamp['is_todo'] == False)
        
        self.async(lambda: self.handleGET(path, data), _validate_result2)
        self.deleteTodo(self.tokenB, self.entityA['entity_id'])

class StampedAPICollectionsFriends(StampedAPICollectionTest):
    def test_friends_of_friends(self):
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "scope" : "fof",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertIsInstance(x, list), 
        ])

class StampedAPICollectionsSuggested(StampedAPICollectionTest):
    def test_suggested_stamps(self):
        path = "stamps/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "scope" : "popular",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertIsInstance(x, list), 
        ])

    def test_suggested_stamps_no_auth(self):
        path = "stamps/collection.json"
        data = { 
            "scope" : "popular",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertIsInstance(x, list), 
        ])

class StampedAPICollectionsConsumption(StampedAPICollectionTest):
    def test_consumption(self):
        path = "collections/consumption.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
        }

        for scope in ['you', 'friends', 'fof', 'everyone']:
            data['scope'] = scope
            self.async(lambda: self.handleGET(path, data), [
                lambda x: self.assertIsInstance(x, list),
                ])


if __name__ == '__main__':
    main()

