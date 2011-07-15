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
        'username': basestring,
#         'email': basestring,
#         'password': basestring,
        'img': basestring,
#         'locale': basestring,
        'timestamp': basestring,
        'website': basestring,
        'bio': basestring,
        'color': {
            'primary_color': basestring,
            'secondary_color': basestring
        },
#         'linked_accounts': {
#             'itunes': basestring
#         },
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
#         print userId
        user = User(self._getDocumentFromId(userId))
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
            data = self._collection.find({"username": {"$in": query}})
        else:
            return None
            
        result = []
        for userData in data:
            result.append(User(userData))
        return result

    def searchUsers(self, searchQuery, searchLimit=20):
        # Using a simple regex here. Need to rank results at some point...
        searchQuery = '^%s' % searchQuery
        result = []
        for user in self._collection.find({"username": {"$regex": searchQuery, "$options": "i"}}).limit(searchLimit):
            result.append(User(self._mongoToObj(user)))
        return result
        
    def flagUser(self, user):
        ### TODO
        print 'TODO'
        
    def checkPrivacy(self, userId):
        privacy = self._collection.find_one({"_id": self._getObjectIdFromString(userId)}, fields={"flags": 1})['flags']['privacy']
        return privacy
            
    
    ### PRIVATE
        
