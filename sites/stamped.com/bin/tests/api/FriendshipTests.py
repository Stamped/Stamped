#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

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

if __name__ == '__main__':
    main()

