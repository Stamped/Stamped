#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
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
        self.assertEqual(result['contents'][-1]['blurb'], self.stamp['contents'][-1]['blurb'])

# class StampedAPIStampsUpdate(StampedAPIStampTest):
#     def test_show(self):
#         path = "stamps/update.json"
#         blurb = "Really, really delicious."
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)

class StampedAPIStampsRestamp(StampedAPIStampTest):
    def test_restamp(self):
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], blurb='ASDF')
        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(len(result['contents']), 2)
        self.assertEqual(result['contents'][0]['blurb'], 'ASDF')


class StampedAPIStampsUserDetails(StampedAPIStampTest):
    def test_user_details(self):

        path = "account/customize_stamp.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "color_primary": "123456",
            "color_secondary": "123456",
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['color_primary'], '123456')
        self.assertEqual(result['color_secondary'], '123456')

        path = "stamps/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['user']['color_primary'], '123456')
        self.assertEqual(result['user']['color_secondary'], '123456')

# class StampedAPIStampMentionsTest(AStampedAPITestCase):
#     def setUp(self):
#         (self.userA, self.tokenA) = self.createAccount('UserA')
#         (self.userB, self.tokenB) = self.createAccount('UserB')
#         (self.userC, self.tokenC) = self.createAccount('UserC')
#         self.createFriendship(self.tokenB, self.userA)
#         self.entity = self.createEntity(self.tokenA)
#         self.stampData = {
#             "oauth_token": self.tokenA['access_token'],
#             "entity_id": self.entity['entity_id'],
#             "blurb": "Great spot. Thanks @%s!" % self.userB['screen_name'],
#             "credits": self.userB['screen_name']
#         }
#         self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'], \
#             self.stampData)

#     def tearDown(self):
#         self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
#         self.deleteEntity(self.tokenA, self.entity['entity_id'])
#         self.deleteFriendship(self.tokenB, self.userA)
#         self.deleteAccount(self.tokenA)
#         self.deleteAccount(self.tokenB)
#         self.deleteAccount(self.tokenC)

# class StampedAPIStampsMentionsShow(StampedAPIStampMentionsTest):
#     def test_show(self):
#         path = "stamps/show.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id']
#         }
#         result = self.handleGET(path, data)
#         self.assertEqual(result['contents'][-1]['blurb'], self.stamp['contents'][-1]['blurb'])
#         self.assertEqual(
#             result['credits'][0]['screen_name'], 
#             self.stampData['credits']
#             )
#         self.assertTrue(len(result['mentions']) == 1)

# class StampedAPIStampsMentionsUpdate(StampedAPIStampMentionsTest):
#     def test_no_mentions(self):
#         path = "stamps/update.json"
#         blurb = "Really, really delicious."
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)
#         # self.assertTrue(len(result['mentions']) == 0)
#         self.assertTrue('mentions' not in result)

#     def test_two_mentions(self):
#         path = "stamps/update.json"
#         blurb = "Thanks again @%s! --@%s" % \
#                 (self.userB['screen_name'], self.userA['screen_name'])
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "blurb": blurb
#         }
#         result = self.handlePOST(path, data)
#         self.assertEqual(result['blurb'], blurb)
#         self.assertTrue(len(result['mentions']) == 2)

# class StampedAPIStampsCreditUpdate(StampedAPIStampMentionsTest):
#     def test_no_credit(self):
#         path = "stamps/update.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "credits": None
#         }
#         result = self.handlePOST(path, data)
#         # self.assertTrue(len(result['credits']) == 0)
#         self.assertTrue('credits' not in result)

#     def test_two_credits(self):
#         path = "stamps/update.json"
#         data = { 
#             "oauth_token": self.tokenA['access_token'],
#             "stamp_id": self.stamp['stamp_id'],
#             "credits": "%s,%s" % (
#                 self.userB['screen_name'],
#                 self.userC['screen_name']
#             )
#         }
#         result = self.handlePOST(path, data)
#         self.assertTrue(len(result['credits']) == 2)

class StampedAPIStampsLimits(StampedAPIStampTest):
    def test_show(self):
        path = "users/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "user_id": self.userA['user_id']
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(x['num_stamps_left'], self.userA['num_stamps_left'] - 1), 
        ])
    
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
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(x['num_stamps_left'], 0), 
                   lambda x: self.assertEqual(x['num_stamps'], self.userA['num_stamps_left']), 
        ])
        
        # User should now be over their limit
        with expected_exception():
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
            "credits": self.userB['screen_name']
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
        
        self.assertTrue(len(result['credits']) == 1)
        self.assertEqual(
            result['credits'][0]['user']['screen_name'], 
            self.stampData['credits']
            )
        self.assertEqual(
            result['credits'][0]['stamp_id'], 
            self.stampA['stamp_id']
            )


class StampedAPIStampLikesTest(AStampedAPITestCase):
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

class StampedAPILikesPass(StampedAPIStampLikesTest):
    def test_like(self):
        path = "stamps/likes/create.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result['num_likes'], 1)

        path = "stamps/likes/remove.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result['num_likes'], 0)

    def test_many_likes(self):
        tokens = []
        for i in xrange(6):
            user, token = self.createAccount('User%s' % i)
            tokens.append(token)

            path = "stamps/likes/create.json"
            data = { 
                "oauth_token": token['access_token'],
                "stamp_id": self.stamp['stamp_id']
            }
            result = self.handlePOST(path, data)
            self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])
            self.assertEqual(result['num_likes'], i + 1)

            # Verify likes that exist
            path = "stamps/likes/show.json"
            data = { 
                "oauth_token": self.tokenB['access_token'],
                "stamp_id": self.stamp['stamp_id']
            }
            result = self.handleGET(path, data)
            self.assertEqual(len(result['user_ids']), i + 1)

            # Verify user is within results
            check = False
            for item in result['user_ids']:
                if item == user['user_id']:
                    check = True
            self.assertTrue(check)

        for i in xrange(6):
            token = tokens[i]
            path = "stamps/likes/remove.json"
            data = { 
                "oauth_token": token['access_token'],
                "stamp_id": self.stamp['stamp_id']
            }
            result = self.handlePOST(path, data)

            self.deleteAccount(token)

class StampedAPILikesFail(StampedAPIStampLikesTest):
    def test_remove(self):
        path = "stamps/likes/remove.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        
        with expected_exception():
            result = self.handlePOST(path, data)
    
    def test_like_twice(self):
        path = "stamps/likes/create.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result['num_likes'], 1)
        
        with expected_exception():
            result = self.handlePOST(path, data)
        
        path = "stamps/likes/remove.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result['num_likes'], 0)

    def test_many_likes_from_one_user(self):
        for i in xrange(6):
            path = "stamps/likes/create.json"
            data = { 
                "oauth_token": self.tokenB['access_token'],
                "stamp_id": self.stamp['stamp_id']
            }
            result = self.handlePOST(path, data)
            self.assertEqual(result['stamp_id'], self.stamp['stamp_id'])

            if 'like_threshold_hit' in result:
                self.assertEqual(result['like_threshold_hit'], False)

            path = "stamps/likes/remove.json"
            data = { 
                "oauth_token": self.tokenB['access_token'],
                "stamp_id": self.stamp['stamp_id']
            }
            result = self.handlePOST(path, data)


class StampedAPIEntitiesStampedBy(StampedAPIStampTest):
    def test_stampedby_nogroup(self):
        # User B queries the entity User A created and Stamped
        path = "entities/stamped_by.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            "entity_id": self.entity['entity_id']
        }
        result = self.handleGET(path, data)

        self.assertEqual(result['friends']['count'], 1)
        self.assertEqual(result['friends']['stamps'][0]['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result['friends']['stamps'][0]['user']['screen_name'], 'UserA')
        #self.assertEqual(result[0]['title'].lower(), self.entity['title'].lower())

#        import time
#        time.sleep(100000)


if __name__ == '__main__':
    main()

