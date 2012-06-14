#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *
from MongoStampedAPI import *

import alerts

# ###### #
# ALERTS #
# ###### #

class StampedAPIAlertsTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        (self.userD, self.tokenD) = self.createAccount('UserD')
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
        self.deleteAccount(self.tokenC)
        self.deleteAccount(self.tokenD)


class StampedAPISendAlertsTest(StampedAPIAlertsTest):
    def test_alerts_show(self):
        print('running')
        path = "account/alerts/show.json"
        data = {
            "oauth_token": self.tokenA['access_token']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result) == 14)

    # Activity unread is used for badge count
    def test_activity_unread(self):
        print('running')
        path = "activity/unread.json"
        data = {
            "oauth_token": self.tokenA['access_token']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result['num_unread'] == 2)


if __name__ == '__main__':
    main()