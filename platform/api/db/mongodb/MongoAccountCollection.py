#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs

from datetime                   import datetime
from utils                      import lazyProperty
from api.Schemas                import *
from errors                     import *
from pymongo.errors             import DuplicateKeyError

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
        if 'phone' in document:
            document['phone'] = str(document['phone'])

        return document


    def _upgradeLinkedAccounts(self, document):
        linkedAccounts = document.pop('linked_accounts', None)
        if linkedAccounts is None:
            return

        if 'linked' in document:
            logs.error("Account contains both 'linked' and 'linked_account' fields.  Should only have one")
            return document

        document['linked'] = {}
        if 'twitter' in linkedAccounts:
            twitterAcct = {
                'service_name'      : 'twitter',
                'user_id'           : linkedAccounts['twitter'].pop('twitter_id', None),
                'name'              : linkedAccounts['twitter'].pop('twitter_name', None),
                'screen_name'       : linkedAccounts['twitter'].pop('twitter_screen_name', None),
            }
            twitterAcctSparse = {}
            for k,v in twitterAcct.iteritems():
                if v is not None:
                    twitterAcctSparse[k] = v
            document['linked']['twitter'] = twitterAcctSparse

        if 'facebook' in linkedAccounts:
            facebookAcct = {
                'service_name'      : 'facebook',
                'user_id'           : linkedAccounts['facebook'].pop('facebook_id', None),
                'name'              : linkedAccounts['facebook'].pop('facebook_name', None),
                'screen_name'       : linkedAccounts['facebook'].pop('facebook_screen_name', None),
                }
            facebookAcctSparse = {}
            for k,v in facebookAcct.iteritems():
                if v is not None:
                    facebookAcctSparse[k] = v
            document['linked']['facebook'] = facebookAcctSparse

        if 'netflix' in linkedAccounts:
            netflixAcct = {
                'service_name'      : 'netflix',
                'user_id'           : linkedAccounts['netflix'].pop('netflix_user_id', None),
                'token'             : linkedAccounts['netflix'].pop('netflix_token', None),
                'secret'            : linkedAccounts['netflix'].pop('netflix_secret', None),
                }
            netflixAcctSparse = {}
            for k,v in netflixAcct.iteritems():
                if v is not None:
                    netflixAcctSparse[k] = v
            document['linked']['netflix'] = netflixAcctSparse

    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        # TODO: Eventually remove all instances of alerts.ios_alert_fav and alerts.email_alert_fav and replace them
        #  with the their equivalent "_todo" fields  For now, we convert for the sake of backward compatability

        if 'alerts' in document and 'alert_settings' not in document:
            document['alert_settings'] = document['alerts']
            if 'ios_alert_fav' in document['alerts']:
                document['alert_settings']['ios_alert_todo'] = document['alerts']['ios_alert_fav']
            if 'email_alert_fav' in document['alerts']:
                document['alert_settings']['email_alert_todo'] = document['alerts']['email_alert_fav']
            del(document['alerts'])

        if 'stats' in document and 'num_faves' in document['stats']:
            document['stats']['num_todos'] = document['stats']['num_faves']
            del(document['stats']['num_faves'])

        if 'auth_service' not in document:
            document['auth_service'] = 'stamped'

        self._upgradeLinkedAccounts(document)

        if self._obj is not None:
            return self._obj().dataImport(document, overflow=self._overflow)
        else:
            return document
    
    ### PUBLIC
    
    @lazyProperty
    def alert_apns_collection(self):
        return MongoAlertAPNSCollection()

    @lazyProperty
    def user_linked_alerts_history_collection(self):
        return MongoUserLinkedAlertsHistoryCollection()
    
    def addAccount(self, user):
        try:
            return self._addObject(user)
        except DuplicateKeyError as e:
            logs.warning("Unable to add account: %s" % e)
            if self._collection.find_one({"email": user.email}) is not None:
                raise StampedDuplicationError("An account already exists with email '%s'" % user.email)
            elif self._collection.find_one({"screen_name": user.screen_name.lower()}) is not None:
                raise StampedDuplicationError("An account already exists with screen name '%s'" % user.screen_name)
            else:
                raise StampedDuplicationError("Account information already exists: %s" % e)
    
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
        accounts = [self._convertFromMongo(doc) for doc in documents]
        documents = self._collection.find({"linked.facebook.user_id" : facebookId })
        accounts.extend([self._convertFromMongo(doc) for doc in documents])
        return accounts

    def getAccountsByTwitterId(self, twitterId):
        documents = self._collection.find({"linked_accounts.twitter.twitter_id" : twitterId})
        accounts = [self._convertFromMongo(doc) for doc in documents]
        documents = self._collection.find({"linked.twitter.user_id" : twitterId })
        accounts.extend([self._convertFromMongo(doc) for doc in documents])
        return accounts

    def getAccountsByNetflixId(self, netflixId):
        documents = self._collection.find({"linked_accounts.twitter.netflix_user_id" : netflixId})
        accounts = [self._convertFromMongo(doc) for doc in documents]
        documents = self._collection.find({"linked.netflix.user_id" : netflixId })
        accounts.extend([self._convertFromMongo(doc) for doc in documents])
        return accounts

    def addLinkedAccountAlertHistory(self, userId, serviceName, serviceId):
        return user_linked_alerts_history_collection.addLinkedAlert(userId, serviceName, serviceId)

    def checkLinkedAccountAlertHistory(self, userId, serviceName, serviceId):
        result = user_linked_alerts_history_collection.checkLinkedAlert(userId, serviceName, serviceId)
        if result:
            return result
        # Check for deprecated alerts sent flag and update database if exists
        account = self.getAccount(userId)
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        if 'linked_accounts' in document:
            for k, v in document['linked_accounts'].iteritems():
                if k == 'facebook':
                    self.user_linked_alerts_history_collection.addLinkedAlert(userId, k, v['facebook_id'])
                elif k == 'twitter':
                    self.user_linked_alerts_history_collection.addLinkedAlert(userId, k, v['twitter_id'])
                elif k == 'netflix':
                    self.user_linked_alerts_history_collection.addLinkedAlert(userId, k, v['netflix_user_id'])

    def removeLinkedAccountAlertHistory(self, userId):
        return user_linked_alerts_history_collection.removeLinkedAlerts(userId)

    def addLinkedAccount(self, userId, linkedAccount):

        # Verify that the linked account service does not already exist in the account
        #documents = self._collection.find({'linked_accounts.service_name' : linkedAccount.service_name })
        document = self._collection.find_one({ "linked.service_name" : linkedAccount.service_name })
        logs.info('### documents: %s' % document)
        if document is not None:
            raise StampedDuplicationError("Linked '%s' account already exists for user." % linkedAccount.service_name)
        #documents = self._collection.find({"linked_accounts.facebook.facebook_id" : facebookId})


        # create a dict of all twitter fields and bools for required fields
        valid_twitter = {
            'service_name'      : True,
            'user_id'           : True,
            'screen_name'       : True,
            'token'             : True,
            'secret'            : True,
        }

        valid_facebook = {
            'service_name'      : True,
            'user_id'           : True,
            'name'              : True,
            'screen_name'       : False,
            'token'             : True,
            'token_expire'      : True,
        }

        valid_netflix = {
            'service_name'      : True,
            'user_id'           : True,
            'token'             : True,
            'secret'            : True,
        }
        
        fields = {}
        valid = True
        linkedDict = linkedAccount.dataExport()
        if linkedAccount.service_name == 'twitter':
            valid_fields = valid_twitter
        elif linkedAccount.service_name == 'facebook':
            valid_fields = valid_facebook
        elif linkedAccount.service_name == 'netflix':
            valid_fields = valid_netflix
        else:
            raise StampedInputError("Attempting to add unknown linked account type: '%s'" % linkedAccount.service_name)

        # Check for all required fields
        missing_fields = []
        valid = True
        for k, v in valid_twitter.iteritems():
            if v == True and k not in linkedDict or linkedDict[k] is None:
                valid = False
                missing_fields.append(k)

        if valid == False:
            raise StampedInputError("Missing required linked account fields for %s: %s" % (linkedAccount.service_name, missing_fields))

        # Construct a new LinkedAccount object which contains only valid fields
        newLinkedAccount = LinkedAccount()
        for k, v in linkedDict.iteritems():
            if k in valid_fields and k is not None:
                setattr(newLinkedAccount, k, v)

        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)},
            {'$set': { 'linked.%s' % newLinkedAccount.service_name : newLinkedAccount.dataExport() } }
        )

        return newLinkedAccount

    def removeLinkedAccount(self, userId, linkedAccount):
        fields = {}
        validFields = ['twitter', 'facebook', 'netflix' ]
        if linkedAccount not in ['twitter', 'facebook', 'netflix'] :
            raise StampedInputError("Linked account name '%s' is not among the valid field names: %s" % validFields)

        # update old format accounts
        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)},
            {'$unset': { 'linked_accounts.%s' % linkedAccount : 1 } }
        )

        # update new format accounts
        self._collection.update(
                {'_id': self._getObjectIdFromString(userId)},
                {'$unset': { 'linked.%s' % linkedAccount : 1 } }
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

