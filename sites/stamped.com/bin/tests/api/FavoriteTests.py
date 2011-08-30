#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ######### #
# FAVORITES #
# ######### #

class StampedAPIFavoriteTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.favorite = self.createFavorite(self.tokenB, \
                                            self.entity['entity_id'])

    def tearDown(self):
        self.deleteFavorite(self.tokenB, self.entity['entity_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPIFavoritesShow(StampedAPIFavoriteTest):
    def test_show(self):
        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

    def test_show_nothing(self):
        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

class StampedAPIFavoritesAlreadyComplete(StampedAPIFavoriteTest):
    def test_create_completed(self):
        self.entityB = self.createEntity(self.tokenB)
        self.stampB = self.createStamp(self.tokenB, self.entityB['entity_id'])
        self.favoriteB = self.createFavorite(self.tokenB, self.entityB['entity_id'])

        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['complete'])

        self.deleteFavorite(self.tokenB, self.entityB['entity_id'])
        self.deleteStamp(self.tokenB, self.stampB['stamp_id'])
        self.deleteEntity(self.tokenB, self.entityB['entity_id'])

class StampedAPIFavoritesAlreadyOnList(StampedAPIFavoriteTest):
    def test_already_on_list(self):
        try:
            self.favoriteB = self.createFavorite(self.tokenB, self.entity['entity_id'])
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

class StampedAPIFavoritesViaStamp(StampedAPIFavoriteTest):
    def test_show_via_stamp(self):
        self.deleteFavorite(self.tokenB, self.entity['entity_id'])
        self.favorite = self.createFavorite(self.tokenB, \
                                            self.entity['entity_id'], \
                                            stampId=self.stamp['stamp_id'])

        path = "favorites/show.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    main()

