#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ###### #
# ENTITY #
# ###### #

class StampedAPIEntityTest(AStampedAPITestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(client_id='iphone8')
        self.entity = self.createEntity(self.token)

    def tearDown(self):
        self.deleteEntity(self.token, self.entity['entity_id'])
        self.deleteAccount(self.token)

class StampedAPIEntitiesShow(StampedAPIEntityTest):
    def test_show(self):
        path = "entities/show.json"
        data = {
            "oauth_token": self.token['access_token'],
            "entity_id": self.entity['entity_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['title'], self.entity['title'])

# class StampedAPIEntitiesUpdate(StampedAPIEntityTest):
#     def test_update(self):
#         path = "entities/update.json"
#         desc = "Gastropub in the West Village, NYC"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "desc": desc,
#         }
#         result = self.handlePOST(path, data)
#         newDesc = None
#         for item in result['metadata']:
#             if 'key' in item and item['key'] == 'desc':
#                 newDesc = item['value']
#         self.assertEqual(newDesc, desc)

# class StampedAPIEntitiesUTF8(StampedAPIEntityTest):
#     def test_utf8_update(self):
#         path = "entities/update.json"
#         desc = "๓๙ใ1฿"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "desc": desc
#         }
#         result = self.handlePOST(path, data)
#         newDesc = None
#         for item in result['metadata']:
#             if 'key' in item and item['key'] == 'desc':
#                 newDesc = item['value']
#         self.assertEqual(newDesc, desc.decode('utf-8'))

class StampedAPIEntitiesSearch(StampedAPIEntityTest):
    def test_search(self):
        path = "entities/search.json"
        data = {
            "oauth_token": self.token['access_token'],
            "q": self.entity['title'], 
        }
        result = self.handleGET(path, data)
        
        self.assertEqual(result['entities'][0]['title'].lower(), self.entity['title'].lower())


class StampedAPIEntitiesAutoSuggest(StampedAPIEntityTest):
    def test_autosuggest_results(self):
        path = "entities/autosuggest.json"
        data = {
            "oauth_token": self.token['access_token'],
            'query'     : 'ghostbusters',
            'category'  : 'film',
            }
        result = self.handleGET(path, data)
        self.assertGreater(len(result), 0)

    def test_autosuggest_noresults(self):
        path = "entities/autosuggest.json"
        data = {
            "oauth_token": self.token['access_token'],
            'query'     : 'asdfoimwerplkj',
            'category'  : 'film',
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)


# ########### #
# OLD VERSION #
# ########### #

# class StampedAPIEntity0Test(AStampedAPITestCase):
#     def setUp(self):
#         (self.user, self.token) = self.createAccount(client_id='stampedtest')
#         self.entity = self.createEntity(self.token)

#     def tearDown(self):
#         self.deleteEntity(self.token, self.entity['entity_id'])
#         self.deleteAccount(self.token)

# class StampedAPIEntities0Show(StampedAPIEntity0Test):
#     def test_show_0(self):
#         path = "entities/show.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['title'], self.entity['title'])

# class StampedAPIEntities0Update(StampedAPIEntity0Test):
#     def test_update_0(self):
#         path = "entities/update.json"
#         desc = "Gastropub in the West Village, NYC"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             # "category": '',
#             "desc": desc,
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['desc'], desc)

# class StampedAPIEntities0UTF8(StampedAPIEntity0Test):
#     def test_utf8_update_0(self):
#         path = "entities/update.json"
#         desc = "๓๙ใ1฿"
#         data = { 
#             "oauth_token": self.token['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "desc": desc
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['desc'], desc.decode('utf-8'))

# class StampedAPIEntities0Search(StampedAPIEntity0Test):
#     def test_search_0(self):
#         path = "entities/search.json"
#         data = {
#             "oauth_token": self.token['access_token'],
#             "q": self.entity['title'], 
#         }
#         result = self.handleGET(path, data)
        
#         self.assertEqual(result[0]['title'].lower(), self.entity['title'].lower())

if __name__ == '__main__':
    main()

