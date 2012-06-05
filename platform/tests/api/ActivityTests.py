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

    def _assertBenefit(self, result):
        benefit = None
        for i in result:
            if 'benefit' in i and i['benefit'] is not None:
                benefit = i['benefit']
        self.assertTrue(benefit is not None)

    def _assertVerbExists(self, result, verb):
        verbs = [i['verb'] for i in result]
        exists = verb in verbs
        self.assertTrue(exists)

    def _assertFollowSubjects(self, result, numSubjects):
        exists = False
        for i in result:
            if i['verb'] == 'follow':
                self.assertTrue(len(i['subjects']) == numSubjects)
                exists = True 
                break
        self.assertTrue(exists)

    def _assertBody(self, result, body):
        exists = False
        for i in result:
            if i['body'] == body:
                exists = True 
                break
        self.assertTrue(exists)


class StampedAPIActivityShow(StampedAPIActivityTest):
    def test_show(self):
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
        ])

    def test_show_coordinates(self):
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "coordinates": "40.745498,-73.977612",
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
        ])


class StampedAPIActivityFriendship(StampedAPIActivityTest):
    def test_show_friendship(self):
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
        }
        
        # Default (1 follower)
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
                   lambda x: self._assertFollowSubjects(x, 1),
        ])

        # Add friend (2 followers)
        self.createFriendship(self.tokenC, self.userA)
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
                   lambda x: self._assertFollowSubjects(x, 2),
        ])

        # Remove friend (1 follower)
        self.deleteFriendship(self.tokenC, self.userA)
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
                   lambda x: self._assertFollowSubjects(x, 1),
        ])

    def test_show_friendship_universal(self):
        self.createFriendship(self.tokenC, self.userB)
        path = "activity/friends.json"
        data = { 
            "oauth_token": self.tokenC['access_token'],
        }

        # Assert "B following A" exists
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 2), 
                   lambda x: self._assertFollowSubjects(x, 1),
                   lambda x: self._assertBody(x, 'UserB is now following UserA.'),
        ])

        self.deleteFriendship(self.tokenC, self.userB)


class StampedAPIActivityLikes(StampedAPIActivityTest):
    def test_show_like_benefit(self):
        entity = self.createEntity(self.tokenD)
        stampData = {
            "oauth_token": self.tokenD['access_token'],
            "entity_id": entity['entity_id'],
            "blurb": "Great spot!",
        }
        stamp = self.createStamp(self.tokenD, entity['entity_id'], stampData)

        path = "stamps/likes/create.json"
        for token in [self.tokenA, self.tokenB, self.tokenC]:
            data = { 
                "oauth_token": token['access_token'],
                "stamp_id": stamp['stamp_id']
            }
            result = self.handlePOST(path, data)
        
        path = "activity/show.json"
        data = { 
            "oauth_token": self.tokenD['access_token'],
        }
        
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertTrue(len(x) == 1),
                   lambda x: self._assertBenefit(x),
        ])
        
        self.deleteStamp(self.tokenD, stamp['stamp_id'])
        self.deleteEntity(self.tokenD, entity['entity_id'])

    def test_show_likes_universal(self):
        # Create "like"
        path = "stamps/likes/create.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "stamp_id": self.stampA['stamp_id'],
        }
        result = self.handlePOST(path, data)

        # Add friendship
        self.createFriendship(self.tokenC, self.userB)

        # Check activity
        path = "activity/friends.json"
        data = { 
            "oauth_token": self.tokenC['access_token'],
        }

        # Assert "B liked A's stamp" exists
        self.async(lambda: self.handleGET(path, data), [ 
                   lambda x: self.assertEqual(len(x), 3), 
                   lambda x: self._assertBody(x, 'UserB liked %s.' % self.stampA['entity']['title']),
        ])

        self.deleteFriendship(self.tokenC, self.userB)

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
                   lambda x: self._assertBenefit(x),
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
                   lambda x: self.assertTrue(x[0]['verb'] == 'restamp'), 
        ])
        
        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

class StampedAPIActivityTodos(StampedAPIActivityTest):
    def test_show_todos(self):
        #  We will have User B todo entity A and verify that this appears in User A's activity feed
        self.createTodo(self.tokenB, self.entityA['entity_id'])

        path = "activity/show.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            }

        # Assert that the UserE's todo appears in User A's activity feed and that they include the entity and stamp
        self.async(lambda: self.handleGET(path, data), [
            lambda x: self.assertEqual(len(x), 3),
            lambda x: self._assertBody(x, 'UserB added %s as a to-do.' % self.entityA['title']),
            lambda x: self.assertEqual(len(x[0]['objects']['entities']), 1),
            ])

        # User D friends User A and Todo's his stamped entity, we expect this to show up as a grouped activity item
        self.createFriendship(self.tokenD, self.userA)
        self.createTodo(self.tokenD, self.entityA['entity_id'])

        result = self.handleGET(path, data)
        self.assertEqual(len(result), 3),
        self._assertBody(result, 'UserB and UserD added %s as a to-do.' % self.entityA['title'])

        self.deleteFriendship(self.tokenD, self.userA)
        self.deleteTodo(self.tokenB, self.entityA['entity_id'])
        self.deleteTodo(self.tokenD, self.entityA['entity_id'])

        # Assert nothing happens to the activity feed when User B and D removes the todo
        self.async(lambda: self.handleGET(path, data), [
            lambda x: self.assertEqual(len(x), 3),
            lambda x: self._assertBody(x, 'UserB and UserD added %s as a to-do.' % self.entityA['title']),
            ])

        # Assert adding a todo from a non-friend on User A's stamp shows up in the aggregate item
        self.createTodo(self.tokenC, self.entityA['entity_id'], self.stampA['stamp_id'])
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, 'UserB and 2 others added %s as a to-do.' % self.entityA['title'])

        self.deleteTodo(self.tokenC, self.entityA['entity_id'])

    def test_delete_account_show(self):
        (self.userE, self.tokenE) = self.createAccount('UserE')
        (self.userF, self.tokenF) = self.createAccount('UserF')
        self.createFriendship(self.tokenF, self.userE)
        self.createStamp(self.tokenE, self.entityA['entity_id'])
        self.createTodo(self.tokenF, self.entityA['entity_id'])

        # Make sure that the 'follow' and 'todo' activity items appear for UserE
        result = self.showActivity(self.tokenE)
        self.assertEqual(len(result), 2)

        # Unfriend UserE from UserF
        self.deleteFriendship(self.tokenF, self.userE)
        result = self.showActivity(self.tokenE)

        self.assertEqual(len(result), 1)

        self.deleteAccount(self.tokenF)

        # Assert that deleting the account removed the activity item from User A's feed
        result = self.showActivity(self.tokenE)

        self.assertEqual(len(result), 0)

        self.deleteAccount(self.tokenE)


class StampedAPIActivityActionComplete(StampedAPIActivityTest):
    def test_action_complete(self):
        pass
        data = {
            "oauth_token": self.tokenA['access_token'],
            'category' : 'music',
            'subcategory' : 'album',
            'title' : 'Call Your Girlfriend - Single',
            "subtitle": "Album by Erato",
            }
        entityNew = self.createEntity(self.tokenA, data)
        stampNew = self.createStamp(self.tokenA, entityNew['entity_id'])

        path = 'actions/complete.json'
        data = {
            "oauth_token": self.tokenB['access_token'],
            'action' : 'listen',
            'source' : 'rdio',
            'source_id': 'a1213511',
            'stamp_id' : stampNew['stamp_id'],
            }
        self.handlePOST(path, data)

        # Make sure the complete action was added to User A's activity feed
        result = self.showActivity(self.tokenA)
        self._assertVerbExists(result, 'action_listen')
        self.assertEqual(len(result), 3)
        self._assertBody(result, 'UserB listened to Call Your Girlfriend - Single.')

        # Repeat the same action, make sure it doesn't get added to the activity feed again
        path = 'actions/complete.json'
        data = {
            "oauth_token": self.tokenB['access_token'],
            'action' : 'listen',
            'source' : 'rdio',
            'source_id': 'a1213511',
            'stamp_id' : stampNew['stamp_id'],
            }
        self.handlePOST(path, data)

        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)

        # Test that if User A listens to his own stamped song, it doesn't show up on his feed
        # Repeat the same action, make sure it doesn't get added to the activity feed again
        path = 'actions/complete.json'
        data = {
            "oauth_token": self.tokenA['access_token'],
            'action' : 'listen',
            'source' : 'rdio',
            'source_id': 'a1213511',
            'stamp_id' : stampNew['stamp_id'],
            }
        self.handlePOST(path, data)

        result = self.showActivity(self.tokenA)

        self.assertEqual(len(result), 3)
        self._assertBody(result, 'UserB listened to Call Your Girlfriend - Single.')

        # cleanup
        self.deleteStamp(self.tokenA, stampNew['stamp_id'])
        self.deleteEntity(self.tokenA, entityNew['entity_id'])


if __name__ == '__main__':
    main()

