#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# GENERIC CLASSES

class StampedAPIGuideTest(AStampedAPITestCase):
    def setUp(self):
        # Build users
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')

        # Build friendships
        self.createFriendship(self.tokenA, self.userB)
        self.createFriendship(self.tokenA, self.userC)
        self.createFriendship(self.tokenB, self.userA)
        self.createFriendship(self.tokenB, self.userC)
        self.createFriendship(self.tokenC, self.userA)
        self.createFriendship(self.tokenC, self.userB)

        # Build five entities
        self.entities = []
        books = [ 'Book A', 'Book B', 'Book C', 'Book D', 'Book E' ]
        for book in books:
            data = {
                "title"         : book,
                "subtitle"      : "by Author",
                "category"      : "book",
                "subcategory"   : "book",
            }
            result = self.createEntity(self.tokenC, data=data)
            self.entities.append(result)

        # Build stamps
        self.stamps = []
        self.stamps.append(self.createStamp(self.tokenA, self.entities[0]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenB, self.entities[0]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenC, self.entities[0]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenA, self.entities[1]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenB, self.entities[1]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenB, self.entities[2]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenC, self.entities[2]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenB, self.entities[3]['entity_id'], blurb='Great book.'))
        self.stamps.append(self.createStamp(self.tokenC, self.entities[4]['entity_id'], blurb='Great book.'))

        # Build to-dos
        self.createTodo(self.tokenA, self.entities[0]['entity_id'])
        self.createTodo(self.tokenB, self.entities[1]['entity_id'])
        self.createTodo(self.tokenC, self.entities[1]['entity_id'])
        self.createTodo(self.tokenB, self.entities[2]['entity_id'])
        self.createTodo(self.tokenC, self.entities[3]['entity_id'])
        self.createTodo(self.tokenB, self.entities[4]['entity_id'])


    def tearDown(self):
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)


class StampedAPIGuideCollection(StampedAPIGuideTest):
    def test_guide_inbox(self):
        path = "guide/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "section": "book",
            "scope" : "inbox",
        }
        
        result = self.handleGET(path, data)

        # Verify first result is Book A
        self.assertTrue(result[0]['title'] == 'Book A')

        # Verify first result has 3 stamps and 1 to-do
        self.assertTrue(len(result[0]['previews']['stamps']) == 3)
        self.assertTrue(len(result[0]['previews']['todos']) == 1)

        # Verify second result is Book B
        self.assertTrue(result[0]['title'] == 'Book B')

        # Verify second result has 2 stamps and 2 to-dos
        self.assertTrue(len(result[0]['previews']['stamps']) == 2)
        self.assertTrue(len(result[0]['previews']['todos']) == 2)


        import pprint
        for r in result:
            pprint.pprint(r)



if __name__ == '__main__':
    main()

