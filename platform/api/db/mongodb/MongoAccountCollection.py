#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs

from datetime   import datetime
from utils      import lazyProperty
from api.Schemas    import *
from errors     import *

from AMongoCollection           import AMongoCollection
from MongoAlertAPNSCollection   import MongoAlertAPNSCollection
from AAccountDB                 import AAccountDB

class MongoAccountCollection(AMongoCollection, AAccountDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'users', primary_key='user_id', obj=Account)
        AAccountDB.__init__(self)
        
        ### TEMP: For now, verify that no duplicates can occur via index
        self._collection.ensure_index('screen_name_lower', unique=True)
        self._collection.ensure_index('email', unique=True)
        self._collection.ensure_index('name_lower')
    
    def _convertToMongo(self, account):
        document = AMongoCollection._convertToMongo(self, account)
        
        if 'screen_name' in document:
           document['screen_name_lower'] = str(document['screen_name']).lower()
        if 'name' in document:
           document['name_lower'] = unicode(document['name']).lower()
        
        return document
    
    ### PUBLIC
    
    @lazyProperty
    def alert_apns_collection(self):
        return MongoAlertAPNSCollection()
    
    def addAccount(self, user):
        return self._addObject(user)
    
    def getAccount(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def getAccounts(self, userIds, limit=0):
        query = []
        if isinstance(userIds, list):
            for userId in userIds:
                query.append(self._getObjectIdFromString(userId))

        data = self._collection.find({"_id": {"$in": query}}).limit(limit)
            
        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result
    
    def updateAccount(self, user):
        ### TODO: Only update certain fields (i.e. remove race conditions if 
        ###     user gets credit while modifying account)
        document = self._convertToMongo(user)
        document = self._updateMongoDocument(document)
        return self._convertFromMongo(document)
    
    def removeAccount(self, userId):
        documentId = self._getObjectIdFromString(userId)
        return self._removeMongoDocument(documentId)
    
    def flagUser(self, user):
        # TODO
        raise NotImplementedError("TODO")

    def getAccountByEmail(self, email):
        email = str(email).lower()
        document = self._collection.find_one({"email": email})
        if document is None:
            raise StampedUnavailableError("Unable to find account (%s)" % email)
        return self._convertFromMongo(document)
    
    def getAccountByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
        if document is None:
            raise StampedUnavailableError("Unable to find account (%s)" % screenName)
        return self._convertFromMongo(document)

    def getAccountsByFacebookId(self, facebookId):
        documents = self._collection.find({"linked_accounts.facebook.facebook_id" : facebookId})
        return [self._convertFromMongo(doc) for doc in documents]

    def updateLinkedAccounts(self, userId, twitter=None, facebook=None, netflix=None):

        ### TODO: Derive valid_twitter/facebook from schema

        valid_twitter = [
            'twitter_id',
            'twitter_screen_name',
            'twitter_token',
            'twitter_alerts_sent',
        ]

        valid_facebook = [
            'facebook_id',
            'facebook_name',
            'facebook_screen_name',
            'facebook_token',
            'facebook_expire',
            'facebook_alerts_sent',
        ]

        valid_netflix = [
            'netflix_user_id',
            'netflix_token',
            'netflix_secret',
        ]
        
        fields = {}

        # Twitter
        if twitter is not None:
            for k, v in twitter.dataExport().iteritems():
                if k in valid_twitter and v is not None:
                    fields['linked_accounts.twitter.%s' % k] = v
            
        # Facebook
        if facebook is not None:
            for k, v in facebook.dataExport().iteritems():
                if k in valid_facebook and v is not None:
                    fields['linked_accounts.facebook.%s' % k] = v

        # Netflix
        if netflix is not None:
            for k, v in netflix.dataExport().iteritems():
                if k in valid_netflix and v is not None:
                    fields['linked_accounts.netflix.%s' % k] = v
            
        if len(fields) > 0:
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)},
                {'$set': fields}
            )

    def removeLinkedAccount(self, userId, linkedAccount):
        fields = {}

        if linkedAccount == 'facebook':
            fields = {
                'linked_accounts.facebook.facebook_id': 1,
                'linked_accounts.facebook.facebook_name': 1,
                'linked_accounts.facebook.facebook_screen_name': 1,
                'linked_accounts.facebook.facebook_token': 1,
                'linked_accounts.facebook.facebook_expire': 1,
            }

        if linkedAccount == 'twitter':
            fields = {
                'linked_accounts.twitter.twitter_id': 1,
                'linked_accounts.twitter.twitter_screen_name': 1,
                'linked_accounts.twitter.twitter_token': 1,
            }

        if linkedAccount == 'netflix':
            fields = {
                'linked_accounts.netflix.netflix_user_id': 1,
                'linked_accounts.netflix.netflix_token': 1,
                'linked_accounts.netflix.netflix_secret': 1,
            }

        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)},
            {'$unset': fields}
        )

    def updatePassword(self, userId, password):
        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)}, 
            {'$set': {'password': password}})

        return True

    def updateUserTimestamp(self, userId, key, value):
        key = 'timestamp.%s' % (key)
        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)}, 
            {'$set': {key: value}})

    def updateAPNSToken(self, userId, token):
        current = self.alert_apns_collection.getToken(token)
        if current == userId:
            # Update user token
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)},
                {'$addToSet': {'devices.ios_device_tokens': token}}
            )
        elif current == None:
            # Add token for user
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)},
                {'$addToSet': {'devices.ios_device_tokens': token}}
            )
            # Add token reference
            self.alert_apns_collection.addToken(token, userId)
        else:
            # Token is assigned to someone else!
            # Remove token reference
            self.alert_apns_collection.removeToken(token)
            # Remove token from old user
            self._collection.update(
                {'_id': self._getObjectIdFromString(current)},
                {'$pull': {'devices.ios_device_tokens': token}}
            )
            # Add token for user
            self._collection.update(
                {'_id': self._getObjectIdFromString(userId)},
                {'$addToSet': {'devices.ios_device_tokens': token}}
            )
            # Add token reference
            self.alert_apns_collection.addToken(token, userId)

    def removeAPNSTokenForUser(self, userId, token):
        current = self.alert_apns_collection.getToken(token)
        if current == userId:
            self.alert_apns_collection.removeToken(token)
        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)},
            {'$pull': {'devices.ios_device_tokens': token}}
        )

    def removeAPNSToken(self, token):
        self.alert_apns_collection.removeToken(token)
        self._collection.update(
            {'devices.ios_device_tokens': token},
            {'$pull': {'devices.ios_device_tokens': token}}
        )

