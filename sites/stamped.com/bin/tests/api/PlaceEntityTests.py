#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ###### #
# PLACE #
# ###### #

class StampedAPIPlaceTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount()
        self.entity = self.createPlaceEntity(self.token)

    def tearDown(self):
        self.deleteEntity(self.token, self.entity['entity_id'])
        self.deleteAccount(self.token)

class StampedAPIPlacesShow(StampedAPIPlaceTest):
    def test_show(self):
        path = "entities/show.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['title'], self.entity['title'])

class StampedAPIPlacesUpdate(StampedAPIPlaceTest):
    def test_update(self):
        path = "entities/update.json"
        desc = "Gastropub in the West Village, NYC"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            "desc": desc,
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc)

class StampedAPIPlacesUTF8(StampedAPIPlaceTest):
    def test_utf8_update(self):
        path = "entities/update.json"
        desc = "๓๙ใ1฿"
        data = { 
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id'],
            "desc": desc
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['desc'], desc.decode('utf-8'))

class StampedAPIPlacesSearch(StampedAPIPlaceTest):
    def test_search(self):
        path = "entities/search.json"
        data = { 
            "oauth_token": self.token['access_token'],
            "q": self.entity['title'][:3]
        }
        result = self.handleGET(path, data)
        self.assertEqual(result[0]['title'][:3], self.entity['title'][:3])

if __name__ == '__main__':
    main()

