#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime

from AMongoCollection import AMongoCollection
from api.AUserDB import AUserDB
from api.User import User

class MongoUserCollection(AMongoCollection, AUserDB):
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='users')
        AUserDB.__init__(self)
    
    def _convertToMongo(self, user):
        document = user.exportSparse()
        if 'user_id' in document:
            document['_id'] = self._getObjectIdFromString(document['user_id'])
            del(document['user_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['user_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return User(document, discardExcess=True)
    
    ### PUBLIC
    
    def getUser(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def getUserByScreenName(self, screenName):
        document = self._collection.find_one({"screen_name": screenName})
        return self._convertFromMongo(document)

    def checkScreenNameExists(self, screenName):
        try:
            self.getUserByScreenName(screenName)
            return True
        except:
            return False
    
    def lookupUsers(self, userIDs, screenNames, limit=0):
        queryUserIDs = []
        if isinstance(userIDs, list):
            for userID in userIDs:
                queryUserIDs.append(self._getObjectIdFromString(userID))
        
        queryScreenNames = []
        if isinstance(screenNames, list):
            queryScreenNames = screenNames

        data = self._collection.find({"$or": [
            {"_id": {"$in": queryUserIDs}}, 
            {"screen_name": {"$in": queryScreenNames}}
            ]}).limit(limit)
            
        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result

    def searchUsers(self, query, limit=0):
        ### TODO: Using a simple regex here. Need to rank results at some point...
        query = {"screen_name": {"$regex": '^%s' % query, "$options": "i"}}
        data = self._collection.find(query).limit(limit)

        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result
    
    def flagUser(self, user):
        ### TODO
        raise NotImplementedError
    
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

