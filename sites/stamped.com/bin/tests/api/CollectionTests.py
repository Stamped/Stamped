#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
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

class StampedAPICollectionsShow(StampedAPICollectionTest):
    def test_inbox(self):
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

    def test_user_screen_name(self):
        path = "collections/user.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "screen_name": self.userA['screen_name']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

    def test_user_user_id(self):
        path = "collections/user.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        self.assertTrue(result[0]['blurb'] == self.stampA['blurb'])

class StampedAPICollectionsQuality(StampedAPICollectionTest):
    def test_show(self):
        self.commentC = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentD = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentE = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentF = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentG = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentH = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentI = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentJ = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        self.commentK = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
        
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "quality": 1
        }
        result = self.handleGET(path, data)
        
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


class StampedAPICollectionsActions(StampedAPICollectionTest):
    def test_like(self):
        path = "stamps/likes/create.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stampA['stamp_id']
        }
        result = self.handlePOST(path, data)

        # User B should have "is_liked=True" 
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        for stamp in result:
            if stamp['stamp_id'] == self.stampA['stamp_id']:
                self.assertTrue(stamp['blurb'] == self.stampA['blurb'])
                self.assertTrue(stamp['is_liked'])

        # User A should not have "is_liked"
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        for stamp in result:
            if stamp['stamp_id'] == self.stampA['stamp_id']:
                self.assertTrue(stamp['blurb'] == self.stampA['blurb'])
                self.assertTrue('is_liked' not in stamp)

    def test_fav(self):
        favorite = self.createFavorite(self.tokenB, self.entityA['entity_id'])

        # User B should have "is_fav=True" 
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        for stamp in result:
            if stamp['stamp_id'] == self.stampA['stamp_id']:
                self.assertTrue(stamp['blurb'] == self.stampA['blurb'])
                self.assertTrue(stamp['is_fav'])

        # User A should not have "is_fav"
        path = "collections/inbox.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3)
        for stamp in result:
            if stamp['stamp_id'] == self.stampA['stamp_id']:
                self.assertTrue(stamp['blurb'] == self.stampA['blurb'])
                self.assertTrue('is_fav' not in stamp)

        self.deleteFavorite(self.tokenB, self.entityA['entity_id'])

if __name__ == '__main__':
    main()

