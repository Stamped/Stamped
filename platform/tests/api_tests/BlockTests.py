#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from tests.AStampedAPIHttpTestCase import *

# ###### #
# BLOCKS #
# ###### #

class StampedAPIBlockHttpTest(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
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
        self.deleteAccount(self.tokenC)

"""


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


class StampedAPIBlockedStamp(StampedAPIBlockTest):
    def test_give_credit(self):
        path = "friendships/blocking.json"
        data = { 
            "oauth_token": self.tokenA['access_token']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result['user_ids']), 1)

class StampedAPIBlockComments(StampedAPIBlockTest):
    # A comments on B's stamp
    def test_a_comment_b(self):
        entity = self.createEntity(self.tokenB)
        stamp = self.createStamp(self.tokenB, entity['entity_id'])
        
        with expected_exception():
            self.createComment(self.tokenA, stamp['stamp_id'], "test")
        
        self.deleteStamp(self.tokenB, stamp['stamp_id'])
        self.deleteEntity(self.tokenB, entity['entity_id'])
    
    # B comments on A's stamp
    def test_b_comment_a(self):
        entity = self.createEntity(self.tokenA)
        stamp = self.createStamp(self.tokenA, entity['entity_id'])
        
        with expected_exception():
            self.createComment(self.tokenB, stamp['stamp_id'], "test")
        
        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])
    
    # A mentions B in comment
    def test_a_mentions_b_in_comment(self):
        entity = self.createEntity(self.tokenC)
        stamp = self.createStamp(self.tokenC, entity['entity_id'])
        
        blurb = "Thanks @%s" % self.userB['screen_name']
        comment = self.createComment(self.tokenA, stamp['stamp_id'], blurb)
        
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteComment(self.tokenA, comment['comment_id'])
        self.deleteStamp(self.tokenC, stamp['stamp_id'])
        self.deleteEntity(self.tokenC, entity['entity_id'])
        
    # B mentions A in comment
    def test_b_mentions_a_in_comment(self):
        entity = self.createEntity(self.tokenC)
        stamp = self.createStamp(self.tokenC, entity['entity_id'])

        blurb = "Thanks @%s" % self.userA['screen_name']
        comment = self.createComment(self.tokenB, stamp['stamp_id'], blurb)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

        self.deleteComment(self.tokenB, comment['comment_id'])
        self.deleteStamp(self.tokenC, stamp['stamp_id'])
        self.deleteEntity(self.tokenC, entity['entity_id'])
        
    # A comments on C's stamp that B commented on previously
    def test_a_replies_to_b(self):
        entity = self.createEntity(self.tokenC)
        stamp = self.createStamp(self.tokenC, entity['entity_id'])

        blurb = "First comment"
        commentA = self.createComment(self.tokenB, stamp['stamp_id'], blurb)

        blurb = "Second comment"
        commentB = self.createComment(self.tokenA, stamp['stamp_id'], blurb)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteComment(self.tokenA, commentB['comment_id'])
        self.deleteComment(self.tokenB, commentA['comment_id'])
        self.deleteStamp(self.tokenC, stamp['stamp_id'])
        self.deleteEntity(self.tokenC, entity['entity_id'])
        
    # B comments on C's stamp that A commented on previously
    def test_b_replies_to_a(self):
        entity = self.createEntity(self.tokenC)
        stamp = self.createStamp(self.tokenC, entity['entity_id'])

        blurb = "First comment"
        commentA = self.createComment(self.tokenA, stamp['stamp_id'], blurb)

        blurb = "Second comment"
        commentB = self.createComment(self.tokenB, stamp['stamp_id'], blurb)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

        self.deleteComment(self.tokenB, commentB['comment_id'])
        self.deleteComment(self.tokenA, commentA['comment_id'])
        self.deleteStamp(self.tokenC, stamp['stamp_id'])
        self.deleteEntity(self.tokenC, entity['entity_id'])

class StampedAPIBlockFriendships(StampedAPIBlockTest):
    # A friends B
    def test_a_friend_b(self):
        with expected_exception():
            self.createFriendship(self.tokenA, self.userB)

    # B friends A
    def test_b_friend_a(self):
        with expected_exception():
            self.createFriendship(self.tokenB, self.userA)

class StampedAPIBlockStamps(StampedAPIBlockTest):
    # A mentions B in stamp
    def test_a_mentions_b_in_stamp(self):
        entity = self.createEntity(self.tokenB)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name']
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

    # B mentions A in stamp
    def test_b_mentions_a_in_stamp(self):
        entity = self.createEntity(self.tokenB)
        stampData = {
            "oauth_token": self.tokenB['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Great spot. Thanks @%s!" % self.userA['screen_name']
        }
        stamp = self.createStamp(self.tokenB, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

        self.deleteStamp(self.tokenB, stamp['stamp_id'])
        self.deleteEntity(self.tokenB, entity['entity_id'])

    # A gives B credit
    def test_a_gives_b_credit(self):
        entity = self.createEntity(self.tokenB)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
            "credit": self.userB['screen_name']
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

    # B gives A credit
    def test_b_gives_a_credit(self):
        entity = self.createEntity(self.tokenB)
        stampData = {
            "oauth_token": self.tokenB['access_token'],
            "entity_id": entity['entity_id'],
            "credit": self.userA['screen_name']
        }
        stamp = self.createStamp(self.tokenB, entity['entity_id'], stampData)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

        self.deleteStamp(self.tokenB, stamp['stamp_id'])
        self.deleteEntity(self.tokenB, entity['entity_id'])

    # A updates stamp to give credit to B
    def test_a_gives_b_credit_via_update(self):
        entity = self.createEntity(self.tokenA)
        stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": entity['entity_id'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": stamp['stamp_id'],
            "credit": "%s" % self.userB['screen_name'],
        }
        result = self.handlePOST(path, data)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

    # B updates stamp to give credit to A
    def test_b_gives_a_credit_via_update(self):
        entity = self.createEntity(self.tokenB)
        stampData = {
            "oauth_token": self.tokenB['access_token'],
            "entity_id": entity['entity_id'],
        }
        stamp = self.createStamp(self.tokenB, entity['entity_id'], stampData)

        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": stamp['stamp_id'],
            "credit": "%s" % self.userA['screen_name'],
        }
        result = self.handlePOST(path, data)

        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

        self.deleteStamp(self.tokenB, stamp['stamp_id'])
        self.deleteEntity(self.tokenB, entity['entity_id'])

"""

if __name__ == '__main__':
    main()

