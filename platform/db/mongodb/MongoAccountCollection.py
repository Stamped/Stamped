#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs, pymongo

from datetime                   import datetime
from utils                      import lazyProperty
from api_old.Schemas                import *
from errors                     import *
from pymongo.errors             import DuplicateKeyError

from db.mongodb.AMongoCollection           import AMongoCollection
from db.mongodb.MongoAlertAPNSCollection   import MongoAlertAPNSCollection
from db.mongodb.MongoUserLinkedAlertsHistoryCollection import MongoUserLinkedAlertsHistoryCollection
from db.mongodb.MongoGuideCollection        import MongoGuideCollection
from api_old.AAccountDB                 import AAccountDB

from libs.Memcache                              import globalMemcache

class MongoAccountCollection(AMongoCollection, AAccountDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'users', primary_key='user_id', obj=Account, overflow=True)
        AAccountDB.__init__(self)
        
        ### TEMP: For now, verify that no duplicates can occur via index
        self._collection.ensure_index('screen_name_lower', unique=True)
        self._collection.ensure_index('email', unique=True)
        self._collection.ensure_index('name_lower')
        self._collection.ensure_index([('linked.facebook.linked_user_id', pymongo.ASCENDING),
                                        ('_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('linked.twitter.linked_user_id', pymongo.ASCENDING),
                                        ('_id', pymongo.ASCENDING)])
        self._collection.ensure_index('linked.netflix.linked_user_id')

        self._cache = globalMemcache()


    @lazyProperty
    def alert_apns_collection(self):
        return MongoAlertAPNSCollection()

    @lazyProperty
    def user_linked_alerts_history_collection(self):
        return MongoUserLinkedAlertsHistoryCollection()

    @lazyProperty
    def guide_collection(self):
        return MongoGuideCollection()
    
    def _convertToMongo(self, account):
        document = AMongoCollection._convertToMongo(self, account)
        
        if 'screen_name' in document:
            document['screen_name_lower'] = str(document['screen_name']).lower()
        if 'name' in document and document['name'] is not None:
            document['name_lower'] = unicode(document['name']).lower()
        if 'phone' in document and document['phone'] is not None:
            document['phone'] = str(document['phone'])

        return document

    def _upgradeLinkedAccounts(self, document):
        linkedAccounts = document.pop('linked_accounts', None)
        if linkedAccounts is None:
            return document

        if 'linked' not in document:
            document['linked'] = {}
        if 'twitter' in linkedAccounts:
            twitterAcct = {
                'service_name'          : 'twitter',
                'linked_user_id'        : linkedAccounts['twitter'].pop('twitter_id', None),
                'linked_name'           : linkedAccounts['twitter'].pop('twitter_name', None),
                'linked_screen_name'    : linkedAccounts['twitter'].pop('twitter_screen_name', None),
                }
            twitterAcctSparse = {}
            for k,v in twitterAcct.iteritems():
                if v is not None:
                    twitterAcctSparse[k] = v
            document['linked']['twitter'] = twitterAcctSparse

            if linkedAccounts['twitter'].pop('twitter_alerts_sent', False) and twitterAcct['linked_user_id'] is not None:
                self.user_linked_alerts_history_collection.addLinkedAlert(document['user_id'], 'twitter', twitterAcct['linked_user_id'])

        if 'facebook' in linkedAccounts:
            facebookAcct = {
                'service_name'          : 'facebook',
                'linked_user_id'        : linkedAccounts['facebook'].pop('facebook_id', None),
                'linked_name'           : linkedAccounts['facebook'].pop('facebook_name', None),
                'linked_screen_name'    : linkedAccounts['facebook'].pop('facebook_screen_name', None),
                }
            facebookAcctSparse = {}
            for k,v in facebookAcct.iteritems():
                if v is not None:
                    facebookAcctSparse[k] = v
            document['linked']['facebook'] = facebookAcctSparse

            if linkedAccounts['facebook'].pop('facebook_alerts_sent', False) and facebookAcct['linked_user_id'] is not None:
                self.user_linked_alerts_history_collection.addLinkedAlert(document['user_id'], 'facebook', facebookAcct['linked_user_id'])

        if 'netflix' in linkedAccounts:
            netflixAcct = {
                'service_name'          : 'netflix',
                'linked_user_id'        : linkedAccounts['netflix'].pop('netflix_user_id', None),
                'token'                 : linkedAccounts['netflix'].pop('netflix_token', None),
                'secret'                : linkedAccounts['netflix'].pop('netflix_secret', None),
                }
            netflixAcctSparse = {}
            for k,v in netflixAcct.iteritems():
                if v is not None:
                    netflixAcctSparse[k] = v
            document['linked']['netflix'] = netflixAcctSparse

        return document

    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        # TODO: Eventually remove all instances of alerts.ios_alert_fav and alerts.email_alert_fav and replace them
        #  with the their equivalent "_todo" fields  For now, we convert for the sake of backward compatability

        if 'alerts' in document:
            if 'alert_settings' not in document:
                document['alert_settings'] = document['alerts']
            if 'ios_alert_fav' in document['alerts']:
                document['alert_settings']['ios_alert_todo'] = document['alerts']['ios_alert_fav']
                del(document['alerts']['ios_alert_fav'])
            if 'email_alert_fav' in document['alerts']:
                document['alert_settings']['email_alert_todo'] = document['alerts']['email_alert_fav']
                del(document['alerts']['email_alert_fav'])
            del(document['alerts'])

        # Map the old-style alert settings to new-style
        ### TODO: Change how this works once we've deprecated the script above (with 'alerts')
        if 'alert_settings' in document:
            alertMapping = {
                'ios_alert_credit'      : 'alerts_credits_apns',
                'email_alert_credit'    : 'alerts_credits_email',
                'ios_alert_like'        : 'alerts_likes_apns',
                'email_alert_like'      : 'alerts_likes_email',
                'ios_alert_todo'        : 'alerts_todos_apns',
                'email_alert_todo'      : 'alerts_todos_email',
                'ios_alert_mention'     : 'alerts_mentions_apns',
                'email_alert_mention'   : 'alerts_mentions_email',
                'ios_alert_comment'     : 'alerts_comments_apns',
                'email_alert_comment'   : 'alerts_comments_email',
                'ios_alert_reply'       : 'alerts_replies_apns',
                'email_alert_reply'     : 'alerts_replies_email',
                'ios_alert_follow'      : 'alerts_followers_apns',
                'email_alert_follow'    : 'alerts_followers_email',
            }
            alertSettings = {}
            for k, v in document['alert_settings'].iteritems():
                if k in alertMapping:
                    alertSettings[alertMapping[k]] = v
                else:
                    alertSettings[k] = v 
            document['alert_settings'] = alertSettings 

        if 'stats' in document and 'num_faves' in document['stats']:
            document['stats']['num_todos'] = document['stats']['num_faves']
            del(document['stats']['num_faves'])

        if 'auth_service' not in document:
            document['auth_service'] = 'stamped'

        document = self._upgradeLinkedAccounts(document)

        if self._obj is not None:
            return self._obj().dataImport(document, overflow=self._overflow)
        else:
            return document

    def _delCachedUserMini(self, userId):
        key = str("obj::usermini::%s" % userId)
        try:
            del(self._cache[key])
        except KeyError:
            pass

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        """
        Check the account to verify the following things:

        - Proper schema 

        - Verify linked accounts are unique (i.e. not linked to other users as well)

        """
        
        document = self._getMongoDocumentFromId(key)
        
        assert document is not None

        modified = False

        # Check if old schema version
        if 'linked_accounts' in document or 'alert_settings' not in document or 'auth_service' not in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                modified = True
            else:
                raise StampedDataError(msg)

        account = self._convertFromMongo(document)

        # Verify Facebook accounts are unique
        if account.linked is not None and account.linked.facebook is not None:
            facebookId = account.linked.facebook.linked_user_id
            if facebookId is None:
                logs.info("Cleaning up linked.facebook")
                del(account.linked.facebook)
                modified = True
            else:
                if self._collection.find({'linked.facebook.linked_user_id': facebookId, '_id': {'$lt': key}}).count() > 0:
                    msg = "%s: Multiple accounts exist linked to Facebook id '%s'" % (key, facebookId)
                    if repair:
                        logs.info(msg)
                        del(account.linked.facebook)
                        modified = True
                    else:
                        raise StampedFacebookLinkedToMultipleAccountsError(msg)

        # Verify Twitter accounts are unique
        if account.linked is not None and account.linked.twitter is not None:
            twitterId = account.linked.twitter.linked_user_id
            if twitterId is None:
                logs.info("Cleaning up linked.twitter")
                del(account.linked.twitter)
                modified = True
            else:
                if self._collection.find({'linked.twitter.linked_user_id': twitterId, '_id': {'$lt': key}}).count() > 0:
                    msg = "%s: Multiple accounts exist linked to Twitter id '%s'" % (key, twitterId)
                    if repair:
                        logs.info(msg)
                        del(account.linked.twitter)
                        modified = True 
                    else:
                        raise StampedTwitterLinkedToMultipleAccountsError(msg)

        # User stats: number of stamps
        numStamps = self._collection._database['stamps'].find({'user.user_id': str(key)}).count()
        if account.stats.num_stamps is None or account.stats.num_stamps != numStamps:
            msg = "%s: Incorrect number of stamps" % key 
            if repair:
                logs.info(msg)
                account.stats.num_stamps = numStamps
                modified = True 
            else:
                raise StampedDataError(msg)

        # User stats: number of friends
        if api is not None:
            numFriends = api._friendshipDB.countFriends(str(key))
            if account.stats.num_friends is None or account.stats.num_friends != numFriends:
                msg = "%s: Incorrect number of friends" % key 
                if repair:
                    logs.info(msg)
                    account.stats.num_friends = numFriends
                    modified = True 
                else:
                    raise StampedDataError(msg)

        # User stats: number of followers
        if api is not None:
            numFollowers = api._friendshipDB.countFollowers(str(key))
            if account.stats.num_followers is None or account.stats.num_followers != numFollowers:
                msg = "%s: Incorrect number of followers" % key 
                if repair:
                    logs.info(msg)
                    account.stats.num_followers = numFollowers
                    modified = True 
                else:
                    raise StampedDataError(msg)

        # User stats: number of credits
        numCredits = self._collection._database['stamps'].find({'credits.user.user_id': str(key)}).count()
        if account.stats.num_credits is None or account.stats.num_credits != numCredits:
            msg = "%s: Incorrect number of credits" % key 
            if repair:
                logs.info(msg)
                account.stats.num_credits = numCredits
                modified = True 
            else:
                raise StampedDataError(msg)

        if modified and repair:
            self._collection.update({'_id' : key}, self._convertToMongo(account))

        # Check integrity for guide
        # self.guide_collection.checkIntegrity(key, repair=repair, api=api)

        return True
    
    ### PUBLIC
    
    def addAccount(self, user):
        try:
            return self._addObject(user)
        except DuplicateKeyError as e:
            logs.warning("Unable to add account: %s" % e)
            if self._collection.find_one({"email": user.email}) is not None:
                raise StampedDuplicateEmailError("An account already exists with email '%s'" % user.email)
            elif self._collection.find_one({"screen_name_lower": user.screen_name.lower()}) is not None:
                raise StampedDuplicateScreenNameError("An account already exists with screen name '%s'" % user.screen_name)
            else:
                raise StampedDuplicationError("Account information already exists: %s" % e)
    
    def getAccount(self, userId):
        try:
            documentId = self._getObjectIdFromString(userId)
            document = self._getMongoDocumentFromId(documentId, forcePrimary=True)
        except Exception:
            raise StampedAccountNotFoundError("Account not found in database")
        return self._convertFromMongo(document)
    
    def getAccountByScreenName(self, screen_name):
        try:
            screen_name = screen_name.lower()
            document = self._collection.find({ 'screen_name_lower' : screen_name }, forcePrimary=True)
        except Exception:
            raise StampedAccountNotFoundError("Account not found")
        
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
        self._delCachedUserMini(user.user_id)
        document = self._convertToMongo(user)
        document = self._updateMongoDocument(document)
        return self._convertFromMongo(document)
    
    def removeAccount(self, userId):
        self._delCachedUserMini(userId)
        documentId = self._getObjectIdFromString(userId)
        return self._removeMongoDocument(documentId)
    
    def flagUser(self, user):
        # TODO
        raise NotImplementedError("TODO")

    def getAccountByEmail(self, email):
        email = str(email).lower()
        document = self._collection.find_one({"email": email})
        if document is None:
            raise StampedAccountNotFoundError("Unable to find account (%s)" % email)
        return self._convertFromMongo(document)


    def getAccountsByFacebookId(self, facebookId):
        documents = self._collection.find({"linked.facebook.linked_user_id" : facebookId })
        accounts = [self._convertFromMongo(doc) for doc in documents]
        return accounts

    def getAccountsByTwitterId(self, twitterId):
        documents = self._collection.find({"linked.twitter.linked_user_id" : twitterId })
        accounts = [self._convertFromMongo(doc) for doc in documents]
        return accounts

    def getAccountsByNetflixId(self, netflixId):
        documents = self._collection.find({"linked.netflix.linked_user_id" : netflixId })
        accounts = [self._convertFromMongo(doc) for doc in documents]
        return accounts

    def addLinkedAccount(self, userId, linkedAccount):
        # create a dict of all twitter fields and bools indicating if required
        valid_twitter = {
            'service_name'          : True,
            'linked_user_id'        : True,
            'linked_screen_name'    : True,
            'token'                 : True,
            'secret'                : True,
        }

        valid_facebook = {
            'service_name'          : True,
            'linked_user_id'        : True,
            'linked_name'           : True,
            'linked_screen_name'    : False,
            'token'                 : True,
            'token_expiration'      : False,
            'share_settings'        : False,
            'third_party_id'        : False,
        }

        valid_netflix = {
            'service_name'          : True,
            'linked_user_id'        : True,
            'token'                 : True,
            'secret'                : True,
        }

        valid_rdio = {
            'service_name'          : True,
            'token'                 : True,
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
        elif linkedAccount.service_name == 'rdio':
            valid_fields = valid_rdio
        else:
            raise StampedInputError("Attempting to add unknown linked account type: '%s'" % linkedAccount.service_name)

        # Check for all required fields
        missing_fields = []
        valid = True
        for k, v in valid_fields.iteritems():
            if v == True and (k not in linkedDict or linkedDict[k] is None):
                valid = False
                missing_fields.append(k)

        if valid == False:
            raise StampedInputError("Missing required linked account fields for %s: %s" % \
                (linkedAccount.service_name, missing_fields))

        # Construct a new LinkedAccount object which contains only valid fields
        newLinkedAccount = LinkedAccount()

        remove_fields = []
        for k, v in linkedDict.iteritems():
            if k is not None and k not in valid_fields:
                remove_fields.append(k)
        for field in remove_fields:
            del(linkedDict[field])

        newLinkedAccount.dataImport(linkedDict)

        self._collection.update(
            {'_id': self._getObjectIdFromString(userId)},
            {'$set': { 'linked.%s' % newLinkedAccount.service_name : newLinkedAccount.dataExport() } }
        )

        return newLinkedAccount

    def updateLinkedAccount(self, userId, linkedAccount):
        fields = {}
        validFields = ['twitter', 'facebook', 'netflix', 'rdio' ]
        if linkedAccount.service_name not in ['twitter', 'facebook', 'netflix', 'rdio'] :
            raise StampedInputError("Linked account name '%s' is not among the valid field names: %s" % validFields)

        userObjectId = self._getObjectIdFromString(userId)

        self._collection.update(
            {'_id': userObjectId},
            {'$set': { 'linked.%s' % linkedAccount.service_name : linkedAccount.dataExport() } }
        )

        # remove old style linked account if it exists
        self._collection.update(
                {'_id': userObjectId},
                {'$unset': { 'linked_accounts.%s' % linkedAccount.service_name : 1 } }
        )


    def removeLinkedAccount(self, userId, linkedAccount):
        fields = {}
        validFields = ['twitter', 'facebook', 'netflix', 'rdio' ]
        if linkedAccount not in ['twitter', 'facebook', 'netflix', 'rdio'] :
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

