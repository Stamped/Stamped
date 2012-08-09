#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from utils import lazyProperty

from db.mongodb.MongoStampCollection import MongoStampCollection
from db.mongodb.MongoUserStampsCollection import MongoUserStampsCollection
from db.mongodb.MongoInboxStampsCollection import MongoInboxStampsCollection
from db.mongodb.MongoCreditGiversCollection import MongoCreditGiversCollection
from db.mongodb.MongoCreditReceivedCollection import MongoCreditReceivedCollection

class StampDB(object):

    @lazyProperty
    def __stamp_collection(self):
        return MongoStampCollection()

    @lazyProperty
    def __user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def __inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def __credit_givers_collection(self):
        return MongoCreditGiversCollection()
    
    @lazyProperty
    def __credit_received_collection(self):
        return MongoCreditReceivedCollection()

    @lazyProperty
    def __whitelisted_tastemaker_stamps(self):
        return MongoWhitelistedTastemakerStampIdsCollection()


    def checkIntegrity(self, key, repair=False, api=None):
        return self.__stamp_collection.checkIntegrity(key, repair=repair, api=api)


    def addStamp(self, stamp):
        return self.__stamp_collection.addStamp(stamp)
    
    def getStamp(self, stampId):
        return self.__stamp_collection.getStamp(stampId)
    
    def updateStamp(self, stamp):
        return self.__stamp_collection.updateStamp(stamp)
    
    def removeStamp(self, stampId):
        return self.__stamp_collection.removeStamp(stampId)
    
    def addUserStampReference(self, userId, stampId):
        return self.__user_stamps_collection.addUserStamp(userId, stampId)
    
    def removeUserStampReference(self, userId, stampId):
        return self.__user_stamps_collection.removeUserStamp(userId, stampId)
    
    def removeAllUserStampReferences(self, userId):
        return self.__user_stamps_collection.removeAllUserStamps(userId)
    
    def addInboxStampReference(self, userIds, stampId):
        if not isinstance(userIds, list):
            userIds = [ userIds ]
        return self.__inbox_stamps_collection.addInboxStamps(userIds, stampId)
    
    def removeInboxStampReference(self, userIds, stampId):
        return self.__inbox_stamps_collection.removeInboxStamps(userIds, stampId)
    
    def addInboxStampReferencesForUser(self, userId, stampIds):
        return self.__inbox_stamps_collection.addInboxStampsForUser(userId, stampIds)
    
    def removeInboxStampReferencesForUser(self, userId, stampIds):
        return self.__inbox_stamps_collection.removeInboxStampsForUser(userId, stampIds)
    
    def removeAllInboxStampReferences(self, userId):
        return self.__inbox_stamps_collection.removeAllInboxStamps(userId)
    
    def getStamps(self, stampIds, **kwargs):
        return self.__stamp_collection.getStamps(stampIds, **kwargs)
    
    def getStampCollectionSlice(self, stampIds, timeSlice):
        return self.__stamp_collection.getStampCollectionSlice(stampIds, timeSlice)
    
    def searchStampCollectionSlice(self, stampIds, searchSlice):
        return self.__stamp_collection.searchStampCollectionSlice(stampIds, searchSlice)
    
    def countStamps(self, userId):
        return len(self.__user_stamps_collection.getUserStampIds(userId))
    
    def countStampsForEntity(self, entityId, userIds=None):
        return self.__stamp_collection.countStampsForEntity(entityId, userIds=userIds)
    
    def updateStampStats(self, stampId, stat, value=None, increment=1):
        return self.__stamp_collection.updateStampStats(stampid, stat, value=value, increment=increment)

    def updateStampOGActionId(self, stampId, og_action_id):
        return self.__stamp_collection.updateStampOGActionId(stampId, og_action_id)

    def updateStampEntity(self, stampId, entity):
        return self.__stamp_collection.updateStampEntity(stampId, entity)

    def getStampFromUserEntity(self, userId, entityId):
        return self.__stamp_collection.getStampFromUserEntity(userId, entityId)

    def checkStamp(self, userId, entityId):
        return self.getStampFromUserEntity(userId, entityId) is not None
    
    def getStampsFromUsersForEntity(self, userIds, entityId):
        return self.__stamp_collection.getStampsFromUsersForEntity(userIds, entityId)

    def getStampsForEntity(self, entityId, limit=None):
        return self.__stamp_collection.getStampsForEntity(entityId, limit=limit)

    def getStampIdsForEntity(self, entityId, limit=None):
        return self.__stamp_collection.getStampIdsForEntity(entityid, limit=limit)
    
    def getStampFromUserStampNum(self, userId, stampNum):
        return self.__stamp_collection.getStampFromUserStampNum(userId, stampNum)
    
    def giveCredit(self, creditedUserId, stampId, userId):
        self.__credit_received_collection.addCredit(creditedUserId, stampId)
        self.__credit_givers_collection.addGiver(creditedUserId, userId)
    
    def removeCredit(self, creditedUserId, stampId, userId):
        self.__credit_received_collection.removeCredit(creditedUserId, stampId)
        self.__credit_givers_collection.removeGiver(creditedUserId, userId)

    def checkCredit(self, creditedUserId, stamp):
        credits = self.__credit_received_collection.getCredit(creditedUserId)
        if stamp.stamp_id in credits:
            return True
        return False 
    
    def countCredits(self, userId):
        return self.__credit_received_collection.numCredit(userId)

    def getCreditedStamps(self, userId, entityId, limit=0):
        return self.__stamp_collection.getCreditedStamps(userId, entityId, limit=limit)
    
    def removeStamps(self, stampIds):
        return self.__stamp_collection.removeStamps(stampIds)

    def getWhitelistedTastemakerStampIds(self):
        return self.__whitelisted_tastemaker_stamps.getStampIds()
