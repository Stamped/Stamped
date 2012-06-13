#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, time
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
        books = [ 'Book A', 'Book B', 'Book C', 'Book D' ]
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

        # Build to-dos
        self.createTodo(self.tokenA, self.entities[0]['entity_id'])
        self.createTodo(self.tokenB, self.entities[1]['entity_id'])
        self.createTodo(self.tokenC, self.entities[1]['entity_id'])
        self.createTodo(self.tokenB, self.entities[2]['entity_id'])

        """
        Note: The guide's cache only refreshes once every 24 hours currently, so any actions taken
        immediately after the cache creation won't impact the results. 

        A race condition exists within this test where the created to-do does it's work asynchronously, 
        but calling guide/collection.json can generate the guide cache before the to-do is successful. For 
        the purposes of this unit test we're pausing for an additional second for the to-do to build.
        """
        time.sleep(1)


    def tearDown(self):
        for entity in self.entities:
            self.deleteEntity(self.tokenC, entity['entity_id'])

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

        # import pprint
        # for r in result:
        #     print '\n%s.' % (int(result.index(r)) + 1)
        #     pprint.pprint(r)

        # Verify first result is Book A
        self.assertTrue(result[0]['title'] == 'Book A')

        # Verify first result has 3 stamps and 1 to-do
        self.assertTrue(len(result[0]['previews']['stamps']) == 3)
        self.assertTrue(len(result[0]['previews']['todos']) == 1)

        # Verify second result is Book B
        self.assertTrue(result[1]['title'] == 'Book B')

        # Verify second result has 2 stamps and 2 to-dos
        self.assertTrue(len(result[1]['previews']['stamps']) == 2)
        self.assertTrue(len(result[1]['previews']['todos']) == 2)

        # Verify third result is Book C
        self.assertTrue(result[2]['title'] == 'Book C')

        # Verify third result has 2 stamps and 1 to-do
        self.assertTrue(len(result[2]['previews']['stamps']) == 2)
        self.assertTrue(len(result[2]['previews']['todos']) == 1)

        # Verify fourth restult is Book D
        self.assertTrue(result[3]['title'] == 'Book D')

        # Verify fourth result has 1 stamp and no to-dos
        self.assertTrue(len(result[3]['previews']['stamps']) == 1)
        self.assertTrue('todos' not in result[3]['previews'] or result[3]['previews']['todos'] == None)
        





if __name__ == '__main__':
    main()

