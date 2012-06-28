#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs

from datetime   import datetime
from utils      import lazyProperty
from Schemas    import *
from errors     import *

from AMongoCollection           import AMongoCollection
from MongoAlertAPNSCollection   import MongoAlertAPNSCollection
from AAccountDB                 import AAccountDB

class MongoAccountCollection(AMongoCollection, AAccountDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'users', primary_key='user_id', obj=Account, overflow=True)
        AAccountDB.__init__(self)
        
        ### TEMP: For now, verify that no duplicates can occur via index
        self._collection.ensure_index('screen_name_lower', unique=True)
        self._collection.ensure_index('email', unique=True)
        self._collection.ensure_index('name_lower')

    def _downgradeAccountFromTwoPointOh(self, data):
        # Linked Accounts
        linked = data.pop('linked', None)
        if linked is not None:
            linkedAccounts = {}

            facebook = linked.pop('facebook', None)
            if facebook is not None:
                linkedAccounts['facebook'] = {}
                if 'linked_user_id' in facebook:
                    linkedAccounts['facebook']['facebook_id'] = facebook['linked_user_id']
                if 'linked_name' in facebook:
                    linkedAccounts['facebook']['facebook_name'] = facebook['linked_name']
                if 'linked_screen_name' in facebook:
                    linkedAccounts['facebook']['facebook_screen_name'] = facebook['linked_screen_name']
                linkedAccounts['facebook']['facebook_alerts_sent'] = True

            twitter = linked.pop('twitter', None)
            if twitter is not None:
                linkedAccounts['twitter'] = {}
                if 'linked_user_id' in twitter:
                    linkedAccounts['twitter']['twitter_id'] = twitter['linked_user_id']
                if 'linked_screen_name' in twitter:
                    linkedAccounts['twitter']['twitter_screen_name'] = twitter['linked_screen_name']
                linkedAccounts['twitter']['twitter_alerts_sent'] = True

            data['linked_accounts'] = linkedAccounts

        if 'auth_service' in data:
            del(data['auth_service'])

        # Alerts
        alerts = data.pop('alert_settings', None)
        if alerts is not None:
            alertMapping = {
                'alerts_credits_apns'       : 'ios_alert_credit',
                'alerts_credits_email'      : 'email_alert_credit',
                'alerts_likes_apns'         : 'ios_alert_like',
                'alerts_likes_email'        : 'email_alert_like',
                'alerts_todos_apns'         : 'ios_alert_fav',
                'alerts_todos_email'        : 'email_alert_fav',
                'alerts_mentions_apns'      : 'ios_alert_mention',
                'alerts_mentions_email'     : 'email_alert_mention',
                'alerts_comments_apns'      : 'ios_alert_comment',
                'alerts_comments_email'     : 'email_alert_comment',
                'alerts_replies_apns'       : 'ios_alert_reply',
                'alerts_replies_email'      : 'email_alert_reply',
                'alerts_followers_apns'     : 'ios_alert_follow',
                'alerts_followers_email'    : 'email_alert_follow',
            }

            alertSettings = {}
            for k, v in alerts.iteritems():
                if k in alertMapping.values():
                    alertSettings[k] = v 
                elif k in alertMapping:
                    alertSettings[alertMapping[k]] = v
            data['alerts'] = alertSettings 

        # Stats
        stats = data.pop('stats')
        if 'distribution' in stats:
            del(stats['distribution'])
        if 'num_todos' in stats:
            stats['num_faves'] = stats['num_todos']
            del(stats['num_todos'])
        data['stats'] = stats

        return data
    
    def _convertFromMongo(self, document):
        document = self._downgradeAccountFromTwoPointOh(document)
        return AMongoCollection._convertFromMongo(self, document)
    
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

    def updateLinkedAccounts(self, userId, twitter=None, facebook=None):

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
        
        fields = {}

        # Twitter
        if twitter is not None:
            for k, v in twitter.value.iteritems():
                if k in valid_twitter and v is not None:
                    fields['linked_accounts.twitter.%s' % k] = v
            
        # Facebook
        if facebook is not None:
            for k, v in facebook.value.iteritems():
                if k in valid_facebook and v is not None:
                    fields['linked_accounts.facebook.%s' % k] = v
            
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

