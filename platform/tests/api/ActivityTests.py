#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, pprint
from AStampedAPITestCase import *
from MongoStampedAPI import *
from Schemas import *

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
            if i['body'] in body:
                exists = True 
                break
        self.assertTrue(exists)


class StampedAPIActivityShow(StampedAPIActivityTest):
    def test_show(self):
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 2)

class StampedAPIActivityFriendship(StampedAPIActivityTest):
    def test_show_friendship(self):
        # Default (1 follower)
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 2)
        self._assertFollowSubjects(result, 1)

        # Add friend (2 followers)
        self.createFriendship(self.tokenC, self.userA)
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 2)
        self._assertFollowSubjects(result, 2)

        # Remove friend (1 follower), but activity item remains
        self.deleteFriendship(self.tokenC, self.userA)
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 2)
        self._assertFollowSubjects(result, 2)

    def test_show_friendship_universal(self):
        self.createFriendship(self.tokenC, self.userB)

        # Assert "B following A" exists
        result = self.showFriendsActivity(self.tokenC)
        self.assertEqual(len(result), 2)
        self._assertFollowSubjects(result, 1)
        self._assertBody(result, ['UserB is now following UserA.'])

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

        for token in [self.tokenA, self.tokenB, self.tokenC]:
            self.createLike(token, stamp['stamp_id'])
        
        result = self.showActivity(self.tokenD)
        self.assertTrue(len(result) == 1)
        self._assertBenefit(result)
        
        self.deleteStamp(self.tokenD, stamp['stamp_id'])
        self.deleteEntity(self.tokenD, entity['entity_id'])

    def test_show_likes_universal(self):
        # Create "like"
        result = self.createLike(self.tokenB, self.stampA['stamp_id'])

        # Add friendship
        self.createFriendship(self.tokenC, self.userB)

        # Check activity
        # Assert "B liked A's stamp" exists
        result = self.showFriendsActivity(self.tokenC)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB liked %s.' % self.stampA['entity']['title']])

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

        path = "activity/collection.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "scope" : "me",
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
            "credits": self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        self.async(lambda: self.showActivity(self.tokenB), [
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
            "credits": self.userB['screen_name'],
        }
        stamp = self.createStamp(self.tokenA, entity['entity_id'], stampData)

        self.async(lambda: self.showActivity(self.tokenB), [
            lambda x: self.assertEqual(len(x), 2),
            lambda x:self.assertTrue(x[0]['verb'] == 'restamp'),
        ])

        self.deleteStamp(self.tokenA, stamp['stamp_id'])
        self.deleteEntity(self.tokenA, entity['entity_id'])

class StampedAPIActivityTodos(StampedAPIActivityTest):
    def test_show_todos(self):
        #  We will have User B todo entity A and verify that this appears in User A's activity feed
        self.createTodo(self.tokenB, self.entityA['entity_id'])

        # Assert that the UserE's todo appears in User A's activity feed and that they include the entity and stamp
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB added %s as a to-do.' % self.entityA['title']])
        self.assertEqual(len(result[0]['objects']['entities']), 1)

        # User D friends User A and Todo's his stamped entity, we expect this to show up as a grouped activity item
        self.createFriendship(self.tokenD, self.userA)
        self.createTodo(self.tokenD, self.entityA['entity_id'])

        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB and UserD added %s as a to-do.' % self.entityA['title']])

        self.deleteFriendship(self.tokenD, self.userA)
        self.deleteTodo(self.tokenB, self.entityA['entity_id'])
        self.deleteTodo(self.tokenD, self.entityA['entity_id'])

        # Assert nothing happens to the activity feed when User B and D removes the todo
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB and UserD added %s as a to-do.' % self.entityA['title']])

        # Assert adding a todo from a non-friend on User A's stamp shows up in the aggregate item
        self.createTodo(self.tokenC, self.entityA['entity_id'], self.stampA['stamp_id'])
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB and 2 others added %s as a to-do.' % self.entityA['title']])

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

        # Unfriend UserE from UserF, make sure that the activity item remains
        self.deleteFriendship(self.tokenF, self.userE)
        result = self.showActivity(self.tokenE)
        self.assertEqual(len(result), 2)

        # UserF follows UserE again.  Make sure no new activity item appears
        self.createFriendship(self.tokenF, self.userE)
        result = self.showActivity(self.tokenE)
        self.assertEqual(len(result), 2)

        # Assert that deleting UserF's account also removed the 'follow' activity item from User A's feed
        self.deleteAccount(self.tokenF)
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
        self._assertBody(result, ['UserB listened to Call Your Girlfriend - Single.'])

        # Repeat the same action, make sure it doesn't get added to the activity feed again
        self.handlePOST(path, data)

        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)

        # Test that if User A listens to his own stamped song, it doesn't show up on his feed
        data['oauth_token'] =  self.tokenA['access_token']
        self.handlePOST(path, data)
        result = self.showActivity(self.tokenA)

        self.assertEqual(len(result), 3)

        # Have UserC listen to the album and test that activity notifications are grouped
        data['oauth_token'] =  self.tokenC['access_token']
        self.handlePOST(path, data)
        result = self.showActivity(self.tokenA)
        self.assertEqual(len(result), 3)
        self._assertBody(result, ['UserB and UserC listened to Call Your Girlfriend - Single.',
                                  'UserC and UserB listened to Call Your Girlfriend - Single.'])

        # cleanup
        self.deleteStamp(self.tokenA, stampNew['stamp_id'])
        self.deleteEntity(self.tokenA, entityNew['entity_id'])

class StampedAPIActivityUniversal(StampedAPIActivityTest):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        (self.userD, self.tokenD) = self.createAccount('UserD')

        # User D friends User A
        self.createFriendship(self.tokenD, self.userA)

        # User A friends B, C, D
        self.createFriendship(self.tokenA, self.userB)
        self.createFriendship(self.tokenA, self.userC)
        self.createFriendship(self.tokenA, self.userD)

        # Users B, C, D are mutual friends
        self.createFriendship(self.tokenB, self.userC)
        self.createFriendship(self.tokenB, self.userD)
        self.createFriendship(self.tokenC, self.userB)
        self.createFriendship(self.tokenC, self.userD)
        self.createFriendship(self.tokenD, self.userC)
        self.createFriendship(self.tokenD, self.userB)

        self.entity = self.createEntity(self.tokenC)
        self.stamp = self.createStamp(self.tokenC, self.entity['entity_id'])
        self.createLike(self.tokenB, self.stamp['stamp_id'])

    def tearDown(self):
        self.deleteLike(self.tokenB, self.stamp['stamp_id'])
        self.deleteStamp(self.tokenC, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenC, self.entity['entity_id'])

        self.deleteFriendship(self.tokenD, self.userA)

        self.deleteFriendship(self.tokenA, self.userB)
        self.deleteFriendship(self.tokenA, self.userC)
        self.deleteFriendship(self.tokenA, self.userD)

        self.deleteFriendship(self.tokenB, self.userC)
        self.deleteFriendship(self.tokenB, self.userD)
        self.deleteFriendship(self.tokenC, self.userB)
        self.deleteFriendship(self.tokenC, self.userD)
        self.deleteFriendship(self.tokenD, self.userC)
        self.deleteFriendship(self.tokenD, self.userB)

        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)
        self.deleteAccount(self.tokenD)

    def test_follow_activity(self):
        # There should be 1 personal activity item for User A - User D followed User A:
        results = self.showActivity(self.tokenA)
        self.assertEqual(len(results), 1)
        self._assertBody(results, ['UserD is now following you.'])

    def test_follow_activity_universal(self):
        # For friends activity, User A should see that UserB liked Kanye West and Users B,C,D are mutual friends
        results = self.showFriendsActivity(self.tokenA)
        self.assertEqual(len(results), 4)
        self._assertBody(results, ['UserB liked Kanye West.'])
        self._assertBody(results, ['UserC and UserD are now following UserB.', 'UserD and UserC are now following UserB.'])
        self._assertBody(results, ['UserB and UserD are now following UserC.', 'UserD and UserB are now following UserC.'])
        self._assertBody(results, ['UserC and UserB are now following UserD.', 'UserB and UserC are now following UserD.'])

    def test_follow_activity_overlap(self):
        # Now look at UserD's feeds.  We expect to see that User A, B, and C have added him as a follower in his personal feed
        results = self.showActivity(self.tokenD)
        self.assertEqual(len(results), 1)
        self._assertBody(results, ['UserA and 2 others are now following you.', 'UserB and 2 others are now following you.',
                                                                                'UserC and 2 others are now following you.'])
    def test_follow_activity_overlap_universal(self):
        # We should NOT see anyone following UserD.
        results = self.showFriendsActivity(self.tokenD)
        self.assertEqual(len(results), 3)
        self._assertBody(results, ['UserB liked Kanye West.'])
        self._assertBody(results, ['UserA and UserC are now following UserB.', 'UserC and UserA are now following UserB.'])
        self._assertBody(results, ['UserA and UserB are now following UserC.', 'UserB and UserA are now following UserC.'])

    def test_like_activity(self):
        # Test UserC's personal feed.  We expect to see that UserB has liked his stamp, also a grouped item for followers
        results = self.showActivity(self.tokenC)
#        from pprint import pprint
#        pprint([(result['body'], result['activity_id']) for result in results])
        self.assertEqual(len(results), 2)
        self._assertBody(results, ['UserB liked Kanye West.'])

    def test_like_activity_universal(self):
        # Test UserC's friends feed.  We expect that UserB's like is absent.
        results = self.showFriendsActivity(self.tokenC)
        self.assertEqual(len(results), 3)
        self._assertBody(results, ['UserD is now following UserB.'])
        self._assertBody(results, ['UserB is now following UserD.'])
        self._assertBody(results, ['UserD is now following UserA.'])

api = MongoStampedAPI()
class StampedAPIActivityCache(AStampedAPITestCase):
    def setUp(self):
        global api
        self.api = api
        if api._cache._client is None:
            logs.info('WARNING: Not connected to memcached server.')
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        (self.userC, self.tokenC) = self.createAccount('UserC')
        (self.userD, self.tokenD) = self.createAccount('UserD')
        (self.userE, self.tokenE) = self.createAccount('UserE')
        (self.userF, self.tokenF) = self.createAccount('UserF')
        (self.userG, self.tokenG) = self.createAccount('UserG')
        (self.userH, self.tokenH) = self.createAccount('UserH')

        self.createFriendship(self.tokenA, self.userB)

        self.createFriendship(self.tokenB, self.userA)
        self.createFriendship(self.tokenB, self.userC)
        self.createFriendship(self.tokenB, self.userD)
        self.createFriendship(self.tokenB, self.userE)
        self.createFriendship(self.tokenB, self.userF)
        self.createFriendship(self.tokenB, self.userG)
        self.createFriendship(self.tokenB, self.userH)

        self.createFriendship(self.tokenA, self.userB)
        self.createFriendship(self.tokenC, self.userB)
        self.createFriendship(self.tokenD, self.userB)
        self.createFriendship(self.tokenE, self.userB)
        self.createFriendship(self.tokenF, self.userB)
        self.createFriendship(self.tokenG, self.userB)
        self.createFriendship(self.tokenH, self.userB)



    def tearDown(self):
        self.deleteFriendship(self.tokenA, self.userB)

        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteFriendship(self.tokenB, self.userC)
        self.deleteFriendship(self.tokenB, self.userD)
        self.deleteFriendship(self.tokenB, self.userE)
        self.deleteFriendship(self.tokenB, self.userF)
        self.deleteFriendship(self.tokenB, self.userG)
        self.deleteFriendship(self.tokenB, self.userH)

        self.deleteFriendship(self.tokenA, self.userB)
        self.deleteFriendship(self.tokenC, self.userB)
        self.deleteFriendship(self.tokenD, self.userB)
        self.deleteFriendship(self.tokenE, self.userB)
        self.deleteFriendship(self.tokenF, self.userB)
        self.deleteFriendship(self.tokenG, self.userB)
        self.deleteFriendship(self.tokenH, self.userB)

        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)
        self.deleteAccount(self.tokenC)
        self.deleteAccount(self.tokenD)
        self.deleteAccount(self.tokenE)
        self.deleteAccount(self.tokenF)
        self.deleteAccount(self.tokenG)
        self.deleteAccount(self.tokenH)

    def test_offset(self):
        scope = 'friends'
        offset = 0
        limit = 4

        self.api.ACTIVITY_CACHE_BLOCK_SIZE = 50
        self.api.ACTIVITY_CACHE_BUFFER_SIZE = 20

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 4)



        # Test offset
        offset = 1
        limit = 1
        results2 = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0].activity_id, results[1].activity_id)

    def test_limit_greater_than_items_in_cache(self):
        scope = 'friends'
        offset = 0
        limit = 10

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 6)

    def test_limit_larger_than_cache_block(self):
        scope = 'friends'
        offset = 0
        limit = 6

        from pprint import pformat

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 6)
        for r in results:
            logs.info(r.activity_id)

        self.api._activityCache.setCacheBlockSize(2)
        self.api._activityCache.setCacheBlockBufferSize(0)

        results2 = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        for r in results2:
            logs.info(r.activity_id)
        self.assertEqual(len(results2), 6)
        for i,r in enumerate(results2):
            self.assertEqual(r.activity_id, results[i].activity_id)

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

    def test_prev_cache_block_expired(self):
        scope = 'friends'
        offset = 0
        limit = 6

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 6)

        scope = 'friends'
        offset = 5
        limit = 6

        self.api._activityCache.setCacheBlockSize(2)
        self.api._activityCache.setCacheBlockBufferSize(0)

        try:
            api._cache.flush_all()
        except:
            pass
        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 1)

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

    def test_clear_activity_cache(self):
        scope = 'friends'
        offset = 0
        limit = 6

        self.api._activityCache.setCacheBlockSize(5)
        self.api._activityCache.setCacheBlockBufferSize(0)

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 6)

        key = api._activityCache._generateKey(0, authUserId=self.userA['user_id'], scope=scope)
        key2 = api._activityCache._generateKey(5, authUserId=self.userA['user_id'], scope=scope)
        self.assertEqual(key in api._cache, True)
        self.assertEqual(key2 in api._cache, True)
        api._activityCache._clearCacheForKeyParams(authUserId=self.userA['user_id'], scope=scope)
        self.assertEqual(key in api._cache, False)
        self.assertEqual(key2 in api._cache, False)

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)


    def test_cache_clear_on_offset_0(self):
        scope = 'friends'
        offset = 0
        limit = 10

        self.api._activityCache.setCacheBlockSize(5)
        self.api._activityCache.setCacheBlockBufferSize(0)

        results = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results), 6)

        # Create a new activity item that will appear for User A
        (user, token) = self.createAccount('tempUser')
        self.createFriendship(self.tokenB, user)

        # First test that this new item will not be retrieved if we pull from offset != 0
        offset = 5
        results2 = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0].activity_id, results[5].activity_id)

        # Now test that the new item is retrieved when we pull from offset 0
        offset = 0
        results2 = self.api.getActivity(self.userA['user_id'], scope=scope, limit=limit, offset=offset)
        self.assertEqual(len(results2), 7)
        self.assertEqual(results2[1].activity_id, results[0].activity_id)

        self.deleteFriendship(self.tokenB, user)
        self.deleteAccount(token)

        self.api._activityCache.setCacheBlockSize(50)
        self.api._activityCache.setCacheBlockBufferSize(20)

if __name__ == '__main__':
    main()

