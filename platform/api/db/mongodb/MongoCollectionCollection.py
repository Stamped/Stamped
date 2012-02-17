#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import heapq

from utils                          import lazyProperty
from LRUCache                       import lru_cache

from MongoUserStampsCollection      import MongoUserStampsCollection
from MongoInboxStampsCollection     import MongoInboxStampsCollection
from MongoCreditReceivedCollection  import MongoCreditReceivedCollection
from MongoFriendshipCollection      import MongoFriendshipCollection

from api.ACollectionDB              import ACollectionDB

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
        return MongoFriendshipCollection()
    
    def getInboxStampIds(self, userId):
        return self.inbox_stamps_collection.getInboxStampIds(userId)
    
    def getUserStampIds(self, userId):
        return self.user_stamps_collection.getUserStampIds(userId)
    
    def getUserCreditStampIds(self, userId):
        return self.user_credit_collection.getCredit(userId)
    
    def getMentions(self, userId):
        raise NotImplementedError
    
    # TODO: optimize this function; find more efficient alternative to heapq?
    # TODO: cache results of this function locally and in Memcached
    
    def getFriendsStampIds(self, userId, friendsSlice):
        inclusive       = friendsSlice.inclusive
        max_distance    = friendsSlice.distance
        cache           = (inclusive and max_distance == 2)
        
        if cache:
            stamp_ids   = self._getCachedFriendsStampIds(userId)
            
            if stamp_ids is not None:
                return stamp_ids
        
        visited_users   = set()
        stamp_ids       = []
        todo            = []
        
        if max_distance == 0:
            stamp_ids.update(self.getUserStampIds(userId))
            return stamp_ids
        
        # TODO: possible optimization; inboxstamps contains all stamp_ids for 
        # a given user and all users they follow, so this function could 
        # potentially use inboxstamps to expand the BFS more efficiently
        
        def visit_user_naive(user_id, distance):
            if user_id not in visited_users and distance <= max_distance:
                if inclusive or distance == max_distance:
                    stamp_ids.extend(self.getUserStampIds(user_id))
                
                visited_users.add(user_id)
                
                if distance < max_distance:
                    heapq.heappush(todo, (distance, user_id))
        
        def visit_user_cached(user_id, distance):
            if user_id not in visited_users and distance < max_distance:
                stamp_ids.update(self.getInboxStampIds(user_id))
                
                visited_users.add(user_id)
                
                if distance < max_distance - 1:
                    heapq.heappush(todo, (distance, user_id))
        
        if max_distance <= 2:
            visit_user = visit_user_cached
            stamp_ids  = set()
        else:
            visit_user = visit_user_naive
        
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
        
        if max_distance <= 2:
            stamp_ids = list(stamp_ids)
        
        if cache:
            self._cacheFriendsStampIds(userId, stamp_ids)
        
        return stamp_ids
    
    # small local LRU cache supplemented by the global memcached instance
    @lru_cache(maxsize=256)
    def _getCachedFriendsStampIds(self, userId):
        # TODO: add friendsSlice params if / once they're actually used
        if self.api is not None:
            try:
                key = self._getFoFCacheKey(userId)
                
                return self.api._cache[key]
            except:
                pass
    
    def _cacheFriendsStampIds(self, userId, value):
        if self.api is not None:
            try:
                key = self._getFoFCacheKey(userId)
                ttl = 14 * 24 * 60 * 60 # TTL of 2 weeks
                
                return self.api._cache.set(key, value, time=ttl)
            except:
                pass
    
    def _getFoFCacheKey(self, userId):
        return "fof(%s)" % userId

