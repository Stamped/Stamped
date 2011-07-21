#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from api.AUserDB import AUserDB
from api.User import User
from MongoDB import Mongo

class MongoUser(AUserDB, Mongo):
        
    COLLECTION = 'users'
        
    SCHEMA = {
        '_id': object,
        'first_name': basestring,
        'last_name': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'profile_image': basestring,
        'color_primary': basestring,
        'color_secondary': basestring,
        'bio': basestring,
        'website': basestring,
        'privacy': bool,
        'flags': {
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'num_stamps': int,
            'num_following': int,
            'num_followers': int,
            'num_todos': int,
            'num_credit_received': int,
            'num_credit_given': int
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        }
    }
    
    def __init__(self, setup=False):
        AUserDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def getUser(self, userId):
        user = User(self._getDocumentFromId(userId, 'user_id'))
        if user.isValid == False:
            raise KeyError("User not valid")
        return user
        
    def getUserId(self, screenName):
        user = self._collection.find_one({"screen_name": screenName})
        if 'user_id' in user:
            return user.user_id
        return None
    
    def lookupUsers(self, userIDs, screenNames):
        query = []
        if userIDs:
            for userID in userIDs:
                query.append(self._getObjectIdFromString(userID))
            data = self._collection.find({"_id": {"$in": query}})
        elif screenNames:
            for screenName in screenNames:
                query.append(screenName)
            data = self._collection.find({"screen_name": {"$in": query}})
        else:
            return None
            
        result = []
        for userData in data:
            userData['user_id'] = self._getStringFromObjectId(userData['_id'])
            del(userData['_id'])
            result.append(User(userData))
        return result

    def searchUsers(self, searchQuery, searchLimit=20):
        # Using a simple regex here. Need to rank results at some point...
        searchQuery = '^%s' % searchQuery
        result = []
        for userData in self._collection.find({"screen_name": {"$regex": searchQuery, "$options": "i"}}).limit(searchLimit):
            userData['user_id'] = self._getStringFromObjectId(userData['_id'])
            del(userData['_id'])
            result.append(User(userData))
        return result
        
    def flagUser(self, user):
        ### TODO
        print 'TODO'
        
    def checkPrivacy(self, userId):
        privacy = self._collection.find_one({"_id": self._getObjectIdFromString(userId)}, fields={"privacy": 1})['privacy']
        return privacy
        
    def updateUserStats(self, userId, stat, value=None, increment=1):
        key = 'stats.%s' % (stat)
        if value != None:
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)}, 
                {'$set': {key: value}},
                upsert=True)
        else:
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)}, 
                {'$inc': {key: increment}},
                upsert=True)
        return self._collection.find_one({'_id': self._getObjectIdFromString(userId)})['stats'][stat]
    
    ### PRIVATE
        
