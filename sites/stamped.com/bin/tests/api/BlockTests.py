#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

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

if __name__ == '__main__':
    main()

