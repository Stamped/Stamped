#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, logs, utils
import heapq, math
import libs.worldcities

from collections                import defaultdict
from utils                      import lazyProperty
from pprint                     import pprint
from api_old.Schemas                import *

from db.mongodb.AMongoCollection           import AMongoCollection
from db.mongodb.MongoUserCollection        import MongoUserCollection
from db.mongodb.MongoFriendsCollection     import MongoFriendsCollection
from db.mongodb.MongoFollowersCollection   import MongoFollowersCollection
from db.mongodb.MongoStampCollection       import MongoStampCollection
from db.mongodb.MongoBlockCollection       import MongoBlockCollection

from api_old.AFriendshipDB          import AFriendshipDB

class MongoFriendshipCollection(AFriendshipDB):
    
    def __init__(self):
        self._suggested = set()
    
    ### PUBLIC
    
    @lazyProperty
    def block_collection(self):
        return MongoBlockCollection()
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()
    
    @lazyProperty
    def followers_collection(self):
        return MongoFollowersCollection()
    
    @lazyProperty
    def stamp_collection(self):
        return MongoStampCollection()
    
    @lazyProperty
    def collection_collection(self):
        from db.mongodb.MongoCollectionCollection  import MongoCollectionCollection
        
        return MongoCollectionCollection()
    
    @lazyProperty
    def world_cities(self):
        return libs.worldcities.get_world_cities_kdtree()
    
    def addFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.addFriend(userId=userId, friendId=friendId)
        self.followers_collection.addFollower(userId=friendId, followerId=userId)
        return True
    
    def checkFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Friendship: %s -> %s" % (userId, friendId))
        status = self.friends_collection.checkFriend(userId=userId, \
            friendId=friendId)
        return status
    
    def removeFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.removeFriend(userId=userId, friendId=friendId)
        self.followers_collection.removeFollower(userId=friendId, followerId=userId)
        return True
    
    def getFriends(self, userId, limit=None):
        return self.friends_collection.getFriends(userId, limit)
    
    def getFriendsOfFriends(self, userId, distance=2, inclusive=True):
        if distance <= 0:
            logs.warning('Invalid distance for friends of friends: %s' % distance)
            raise Exception

        friends = {0: set([userId])}
        maxDistance = distance

        def visitUser(userId, distance):
            friendIds = self.friends_collection.getFriends(userId)
            
            if distance not in friends:
                friends[distance] = set()
            
            for friendId in friendIds:
                friends[distance].add(friendId)
                
                if distance < maxDistance:
                    visitUser(friendId, distance + 1)

        visitUser(userId, 1)

        result = set([])

        if distance in friends:
            result = friends[distance]

        if not inclusive:
            prevDistance = distance - 1
            while prevDistance >= 0:
                if prevDistance in friends:
                    result = result.difference(friends[prevDistance])
                prevDistance = prevDistance - 1

        return list(result)
    
    def getFollowers(self, userId, limit=None):
        if limit is None:
            limit = 10000
        
        # TODO: add proper cursor support
        return self.followers_collection.getFollowers(userId, limit)
    
    def countFriends(self, userId):
        return len(self.friends_collection.getFriends(userId))
    
    def countFollowers(self, userId):
        return len(self.followers_collection.getFollowers(userId))
    
    def approveFriendship(self, friendship):
        ### TODO
        raise NotImplementedError
    
    def addBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Block: %s -> %s" % (userId, friendId))
        self.block_collection.addBlock(userId=userId, friendId=friendId)
    
    # One Way (Is User A blocking User B?)
    def checkBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        status = self.block_collection.checkBlock(userId=userId,
            friendId=friendId)
        return status
    
    # Two Way (Is User A blocking User B or blocked by User B?)
    def blockExists(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        statusA = self.block_collection.checkBlock(userId=userId,
            friendId=friendId)
        
        logs.debug("Check Block: %s -> %s" % (friendId, userId))
        statusB = self.block_collection.checkBlock(userId=friendId,
            friendId=userId)
        
        if statusA or statusB:
            return True
        return False
    
    def removeBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Block: %s -> %s" % (userId, friendId))
        return self.block_collection.removeBlock(userId=userId,
            friendId=friendId)
    
    def getBlocks(self, userId):
        return self.block_collection.getBlocks(userId)
    
    def getSuggestedUserIds(self, userId, request):
        raise NotImplementedError

