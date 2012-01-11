#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, pprint
from AStampedAPITestCase import *

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
        self.commentA = self.createComment(self.tokenB, self.stampA['stamp_id'], self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stampA['stamp_id'], self.blurbB)
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
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
        ])

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
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
        ])
        
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
        #utils.log(pprint.pformat(result))
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
        ])
        
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
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
                   lambda x: self.assertTrue(x[0]['genre'] == 'restamp'), 
        ])
        
        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

if __name__ == '__main__':
    main()

