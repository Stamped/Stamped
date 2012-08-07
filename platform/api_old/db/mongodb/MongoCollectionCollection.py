#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import heapq

from collections                    import defaultdict
from utils                          import lazyProperty
from libs.LRUCache                       import lru_cache

from db.mongodb.MongoUserStampsCollection      import MongoUserStampsCollection
from db.mongodb.MongoInboxStampsCollection     import MongoInboxStampsCollection
from db.mongodb.MongoCreditReceivedCollection  import MongoCreditReceivedCollection
from db.mongodb.MongoFriendshipCollection      import MongoFriendshipCollection

from api_old.ACollectionDB              import ACollectionDB

class MongoCollectionCollection(ACollectionDB):
    
    def __init__(self, api=None):
        ACollectionDB.__init__(self)
        self.api = api
    
    ### PUBLIC
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def user_credit_collection(self):
        return MongoCreditReceivedCollection()
    
    @lazyProperty
    def friendship_collection(self):
        return MongoFriendshipCollection(self.api)
    
    def getInboxStampIds(self, userId):
        return self.inbox_stamps_collection.getInboxStampIds(userId)
    
    def getUserStampIds(self, userId):
        return self.user_stamps_collection.getUserStampIds(userId)
    
    def getUserCreditStampIds(self, userId):
        return self.user_credit_collection.getCredit(userId)
    
    def getMentions(self, userId):
        raise NotImplementedError
    
    # TODO: optimize this function; find more efficient alternative to heapq?
    
    def getFofStampIds(self, userId):
        max_distance    = 2
        
        # check if result was cached
        # stampIds        = self._getCachedFriendsStamps(userId, False, max_distance)
        
        # if stampIds is not None:
        #     return stampIds
        
        stampIds        = set()
        visited_users   = set()
        fof             = {}
        todo            = []
        
        def visit_user(user_id, distance):
            if user_id not in visited_users and distance <= max_distance:
                if distance == max_distance:
                    stampIds.update(set(self.getUserStampIds(user_id)))
                visited_users.add(user_id)
                if distance < max_distance:
                    heapq.heappush(todo, (distance, user_id))
        
        # seed the algorithm with the initial user at distance 0
        visit_user(userId, 0)
        
        while True:
            try:
                distance, user_id = heapq.heappop(todo)
            except IndexError:
                break # heap is empty
            
            if distance < max_distance:
                friend_ids  = self.friendship_collection.getFriends(user_id)
                distance    = distance + 1
                
                for friend_id in friend_ids:
                    visit_user(friend_id, distance)
        
        # self._cacheFriendsStamps(userId, False, max_distance, stamp_ids)
        
        return stampIds
    
    def getFriendsStamps(self, userId, friendsSlice):
        inclusive       = friendsSlice.inclusive
        max_distance    = friendsSlice.distance
        
        # check if result was cached
        stamp_ids       = self._getCachedFriendsStamps(userId, inclusive, max_distance)
        
        if stamp_ids is not None:
            return stamp_ids
        
        if max_distance == 0:
            # stamps at distance 0 from the seed user are just the seed user's own stamps
            stamp_ids = self.getUserStampIds(userId)
            return dict(map(lambda k: (k, None), stamp_ids))
        
        stamp_ids       = defaultdict(list)
        visited_users   = set()
        fof             = {}
        todo            = []
        
        def visit_user(user_id, friend_id, distance):
            if user_id in visited_users:
                try:
                    ids = fof[user_id]
                    
                    for stamp_id in ids:
                        stamp_ids[stamp_id].append(friend_id)
                except KeyError:
                    pass
            elif distance <= max_distance:
                if inclusive or distance == max_distance:
                    ids = self.getUserStampIds(user_id)
                    
                    if distance >= 2:
                        fof[user_id] = ids
                        
                        for stamp_id in ids:
                            stamp_ids[stamp_id].append(friend_id)
                    else:
                        for stamp_id in ids:
                            stamp_ids[stamp_id] = [ ]
                
                visited_users.add(user_id)
                if distance < max_distance:
                    heapq.heappush(todo, (distance, user_id))
        
        # seed the algorithm with the initial user at distance 0
        visit_user(userId, None, 0)
        
        while True:
            try:
                distance, user_id = heapq.heappop(todo)
            except IndexError:
                break # heap is empty
            
            if distance < max_distance:
                friend_ids  = self.friendship_collection.getFriends(user_id)
                distance    = distance + 1
                
                for friend_id in friend_ids:
                    visit_user(friend_id, user_id, distance)
        
        self._cacheFriendsStamps(userId, inclusive, max_distance, stamp_ids)
        
        #print list(stamp_ids.iteritems())[:10]
        return stamp_ids
    
    # small local LRU cache backed by memcached
    @lru_cache(maxsize=256)
    def _getCachedFriendsStamps(self, userId, inclusive, distance):
        # TODO: add friendsSlice params if / once they're actually used
        if self.api is not None:
            try:
                key = self._getFoFCacheKey(userId, inclusive, distance)
                
                return self.api._cache[key]
            except:
                pass
    
    def _cacheFriendsStamps(self, userId, inclusive, distance, value):
        if self.api is not None:
            try:
                key = self._getFoFCacheKey(userId, inclusive, distance)
                ttl = 14 * 24 * 60 * 60 # TTL of 2 weeks
                
                return self.api._cache.set(key, value, time=ttl)
            except:
                pass
    
    def _getFoFCacheKey(self, userId, inclusive, distance):
        return "fof(%s,%s,%d)" % (userId, inclusive, distance)

