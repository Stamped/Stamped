#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPIHttpTestCase import *

# ########## #
# FRIENDSHIP #
# ########## #

class StampedAPIFriendshipHttpTest(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenA, self.userB)
    
    def tearDown(self):
        self.deleteFriendship(self.tokenA, self.userB)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIFriendshipsCheck(StampedAPIFriendshipHttpTest):
    def test_check_friendship_success(self):
        path = "friendships/check.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id_a": self.userA['user_id'],
            "user_id_b": self.userB['user_id'],
        }
        result = self.handleGET(path, data)
        self.assertTrue(result['result'])
    
    def test_check_friendship_fail(self):
        path = "friendships/check.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id_a": self.userB['user_id'],
            "user_id_b": self.userA['user_id'],
        }
        result = self.handleGET(path, data)
        self.assertFalse(result['result'])
    
    def test_check_friendship_count(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userA['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(x['num_friends'], 1), 
        ])
    
    def test_check_follower_count(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "user_id": self.userB['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(x['num_followers'], 1), 
        ])

class StampedAPIFriends(StampedAPIFriendshipHttpTest):
    def test_show_friends(self):
        path = "friendships/friends.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), 
                   lambda x: self.assertEqual(len(x['user_ids']), 1))

class StampedAPIFollowers(StampedAPIFriendshipHttpTest):
    def test_show_followers(self):
        path = "friendships/followers.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userB['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), 
                   lambda x: self.assertEqual(len(x['user_ids']), 1))

class StampedAPIInviteFriend(StampedAPIFriendshipHttpTest):
    def test_invite_friend(self):
        path = "friendships/invite.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "email": "sample123@stamped.com"
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

        # Subsequent attempts should fail
        with expected_exception():
            result = self.handlePOST(path, data)
            print result
        
        (userC, tokenC) = self.createAccount('sample123')
        self.deleteAccount(tokenC)

if __name__ == '__main__':
    main()

