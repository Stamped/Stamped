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
                self.userA['screen_name'],
                self.userB['screen_name']
            )
        }
        result = self.handlePOST(path, data)
        self.assertTrue(len(result['credit']) == 2)

if __name__ == '__main__':
    main()

