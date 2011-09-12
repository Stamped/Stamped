#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime

from Schemas import *
from AMongoCollection import AMongoCollection
from api.AUserDB import AUserDB

class MongoUserCollection(AMongoCollection, AUserDB):
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='users', primary_key='user_id', obj=User, overflow=True)
        AUserDB.__init__(self)

    ### Note that overflow=True
    def _convertFromMongo(self, document):
        if '_id' in document:
            document['user_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return User(document, overflow=True)
    
    ### PUBLIC
    
    def getUser(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document   = self._getMongoDocumentFromId(documentId)
        
        return self._convertFromMongo(document)
    
    def getUserByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
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
            for screenName in screenNames:
                queryScreenNames.append(str(screenName).lower())

        data = self._collection.find({"$or": [
            {"_id": {"$in": queryUserIDs}}, 
            {"screen_name_lower": {"$in": queryScreenNames}}
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

    def findUsersByEmail(self, emails, limit=0): 
        queryEmails = []
        for email in emails:
            queryEmails.append(str(email).lower())

        ### TODO: Add Index
        data = self._collection.find({"email": {"$in": queryEmails}}).limit(limit)
            
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['email']
            result.append(user)
        return result

    def findUsersByPhone(self, phone, limit=0): 
        queryPhone = []
        for number in phone:
            queryPhone.append(int(number))

        ### TODO: Add Index
        data = self._collection.find({"phone": {"$in": queryPhone}}).limit(limit)
            
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['phone']
            result.append(user)
        return result

    def findUsersByTwitter(self, twitterIds, limit=0): 
        ### TODO: Add Index
        data = self._collection.find(
            {"linked_accounts.twitter.twitter_id": {"$in": twitterIds}}
        ).limit(limit)
            
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['linked_accounts']['twitter']['twitter_id']
            result.append(user)
        return result

