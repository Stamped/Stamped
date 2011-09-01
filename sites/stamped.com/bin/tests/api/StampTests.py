#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ##### #
# STAMP #
# ##### #

class StampedAPIStampTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampsShow(StampedAPIStampTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])

class StampedAPIStampsUpdate(StampedAPIStampTest):
    def test_show(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)

class StampedAPIStampMentionsTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": self.entity['entity_id'],
            "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name'],
            "credit": self.userB['screen_name']
        }
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], \
            self.stampData)

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)

class StampedAPIStampsMentionsShow(StampedAPIStampMentionsTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['blurb'], self.stamp['blurb'])
        self.assertEqual(
            result['credit'][0]['screen_name'], 
            self.stampData['credit']
            )
        self.assertTrue(len(result['mentions']) == 1)

class StampedAPIStampsMentionsUpdate(StampedAPIStampMentionsTest):
    def test_no_mentions(self):
        path = "stamps/update.json"
        blurb = "Really, really delicious."
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        # self.assertTrue(len(result['mentions']) == 0)
        self.assertTrue('mentions' not in result)

    def test_two_mentions(self):
        path = "stamps/update.json"
        blurb = "Thanks again @%s! --@%s" % \
                (self.userB['screen_name'], self.userA['screen_name'])
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "blurb": blurb
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['blurb'], blurb)
        self.assertTrue(len(result['mentions']) == 2)

class StampedAPIStampsCreditUpdate(StampedAPIStampMentionsTest):
    def test_no_credit(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": None
        }
        result = self.handlePOST(path, data)
        # self.assertTrue(len(result['credit']) == 0)
        self.assertTrue('credit' not in result)

    def test_two_credits(self):
        path = "stamps/update.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id'],
            "credit": "%s,%s" % (
                self.userB['screen_name'],
                self.userC['screen_name']
            )
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['credit']) == 2)

class StampedAPIStampsLimits(StampedAPIStampTest):
    def test_show(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['num_stamps_left'], self.userA['num_stamps_left']-1)

    def test_max_limit(self):
        entity_ids = []
        stamp_ids = []

        # Time to create some stamps!
        num_stamps_left = self.userA['num_stamps_left']
        for i in xrange(num_stamps_left-1):

            data = {
                "oauth_token": self.tokenA['access_token'],
                "title": "Entity %s" % i,
                "subtitle": "Sample item",
                "desc": "Sample item", 
                "category": "music",
                "subcategory": "artist",
            }
            entity = self.createEntity(self.tokenA, data)
            entity_ids.append(entity['entity_id'])
            stamp = self.createStamp(self.tokenA, entity['entity_id'])
            stamp_ids.append(stamp['stamp_id'])

        # Check user to verify that they've used up all their stamps
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['num_stamps_left'], 0)
        self.assertEqual(result['num_stamps'], self.userA['num_stamps_left'])

        # User should now be over their limit
        try:
            data = {
                "oauth_token": self.tokenA['access_token'],
                "title": "Entity 100!",
                "subtitle": "Sample item",
                "desc": "Sample item", 
                "category": "music",
                "subcategory": "artist",
            }
            entity = self.createEntity(self.tokenA, data)
            entity_ids.append(entity['entity_id'])
            stamp = self.createStamp(self.tokenA, entity['entity_id'])
            stamp_ids.append(stamp['stamp_id'])
            result = False
        except:
            result = True
        
        self.assertTrue(result)

        # Delete everything
        for stamp_id in stamp_ids:
            self.deleteStamp(self.tokenA, stamp_id)
        for entity_id in entity_ids:
            self.deleteEntity(self.tokenA, entity_id)

class StampedAPIStampCreditTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenB)
        self.stampA = self.createStamp(self.tokenB, self.entity['entity_id'])
        self.stampData = {
            "oauth_token": self.tokenA['access_token'],
            "entity_id": self.entity['entity_id'],
            "blurb": "Great spot.",
            "credit": self.userB['screen_name']
        }
        self.stampB = self.createStamp(self.tokenA, self.entity['entity_id'], \
            self.stampData)

    def tearDown(self):
        self.deleteStamp(self.tokenA, self.stampB['stamp_id'])
        self.deleteStamp(self.tokenB, self.stampA['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIStampsCreditShow(StampedAPIStampCreditTest):
    def test_show(self):
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stampB['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result['credit']) == 1)
        self.assertEqual(
            result['credit'][0]['screen_name'], 
            self.stampData['credit']
            )
        self.assertEqual(
            result['credit'][0]['stamp_id'], 
            self.stampA['stamp_id']
            )




if __name__ == '__main__':
    main()

