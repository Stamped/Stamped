#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import heapq

from utils                          import lazyProperty

from MongoUserStampsCollection      import MongoUserStampsCollection
from MongoInboxStampsCollection     import MongoInboxStampsCollection
from MongoCreditReceivedCollection  import MongoCreditReceivedCollection
from MongoFriendshipCollection      import MongoFriendshipCollection

from api.ACollectionDB              import ACollectionDB

class MongoCollectionCollection(ACollectionDB):
    
    def __init__(self):
        ACollectionDB.__init__(self)
    
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
    
    def getFriendsStampIds(self, userId, friendsSlice):
        visited_users   = set()
        stamp_ids       = []
        todo            = []
        
        inclusive       = friendsSlice.inclusive
        max_distance    = friendsSlice.distance
        
        # TODO: possible optimization; inboxstamps contains all stamp_ids for 
        # a given user and all users they follow, so this function could 
        # potentially use inboxstamps to expand the BFS more efficiently
        
        def visit_user(user_id, distance):
            if user_id not in visited_users and distance <= max_distance:
                if inclusive or distance == max_distance:
                    stamp_ids.extend(self.getUserStampIds(user_id))
                
                visited_users.add(user_id)
                heapq.heappush(todo, (distance, user_id))
        
        # seed the algorithm with the initial user id at distance 0
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
                    if not friend_id in todo and not friend_id in visited_users:
                        visit_user(friend_id, distance)
        
        return stamp_ids, len(visited_users)
    
    def getMentions(self, userId):
        raise NotImplementedError

