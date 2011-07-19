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
        'image': basestring,
        'bio': basestring,
        'website': basestring,
        'color': {
            'primary': list,
            'secondary': list
        },
        'flags': {
            'privacy': bool,
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'total_stamps': int,
            'total_following': int,
            'total_followers': int,
            'total_todos': int,
            'total_credit_received': int,
            'total_credit_given': int
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
    
#     def addUser(self, user):
#         return self._addDocument(user)
    
    def getUser(self, userId):
        user = User(self._getDocumentFromId(userId, 'user_id'))
        if user.isValid == False:
            raise KeyError("User not valid")
        return user
        
    def lookupUsers(self, userIDs, usernames):
        query = []
        if userIDs:
            for userID in userIDs:
                query.append(self._getObjectIdFromString(userID))
            data = self._collection.find({"_id": {"$in": query}})
        elif usernames:
            for username in usernames:
                query.append(username)
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
        privacy = self._collection.find_one({"_id": self._getObjectIdFromString(userId)}, fields={"flags": 1})['flags']['privacy']
        return privacy
            
    
    ### PRIVATE
        
