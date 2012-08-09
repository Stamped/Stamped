#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoAlertAPNSCollection import MongoAlertAPNSCollection
from db.mongodb.MongoUserLinkedAlertsHistoryCollection import MongoUserLinkedAlertsHistoryCollection

class AccountDB(object):

    @lazyProperty
    def _account_collection(self):
        return MongoAccountCollection()

    @lazyProperty
    def _alert_apns_collection(self):
        return MongoAlertAPNSCollection()

    @lazyProperty
    def _user_linked_alerts_history_collection(self):
        return MongoUserLinkedAlertsHistoryCollection()

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        return self._account_collection.checkIntegrity(key, repair=repair, api=api)

    ### ACCOUNT

    def addAccount(self, user):
        return self._account_collection.addAccount(user)
    
    def getAccount(self, user_id):
        return self._account_collection.getAccount(user_id)
    
    def getAccountByScreenName(self, screen_name):
        return self._account_collection.getAccountByScreenName(screen_name)
    
    def getAccounts(self, userIds):
        return self._account_collection.getAccounts(userIds)
    
    def updateAccount(self, user):
        return self._account_collection.updateAccount(user)
    
    def removeAccount(self, userId):
        return self._account_collection.removeAccount(userId)

    def getAccountByEmail(self, email):
        return self._account_collection.getAccountByEmail(email)

    def getAccountsByFacebookId(self, facebookId):
        return self._account_collection.getAccountsByFacebookId(facebookId)

    def getAccountsByTwitterId(self, twitterId):
        return self._account_collection.getAccountsByTwitterId(twitterId)

    def getAccountsByNetflixId(self, netflixId):
        return self._account_collection.getAccountsByNetflixId(netflixId)

    def updatePassword(self, userId, password):
        return self._account_collection.updatePassword(userId, password)

    def updateUserTimestamp(self, userId, key, value):
        return self._account_collection.updateUserTimestamp(userId, key, value)

    ### LINKED ACCOUNTS

    def addLinkedAccount(self, userId, linkedAccount):
        return self._account_collection.addLinkedAccount(userId, linkedAccount)

    def updateLinkedAccount(self, userId, linkedAccount):
        return self._account_collection.updateLinkedAccount(userId, linkedAccount)

    def removeLinkedAccount(self, userId, linkedAccount):
        return self._account_collection.removeLinkedAccount(userId, linkedAccount)

    def addLinkedAccountAlertHistory(self, userId, serviceName, serviceId):
        return self._user_linked_alerts_history_collection.addLinkedAlert(userId, serviceName, serviceId)

    def checkLinkedAccountAlertHistory(self, userId, serviceName, serviceId):
        result = self._user_linked_alerts_history_collection.checkLinkedAlert(userId, serviceName, serviceId)
        if result:
            return True
        return False

    def removeLinkedAccountAlertHistory(self, userId):
        return self._user_linked_alerts_history_collection.removeLinkedAlerts(userId)

    ### APNS TOKENS

    def updateAPNSToken(self, userId, token):
        return self._account_collection.updateAPNSToken(userId, token)

    def removeAPNSTokenForUser(self, userId, token):
        return self._account_collection.removeAPNSTokenForUser(userId, token)

    def removeAPNSToken(self, token):
        return self._account_collection.removeAPNSToken(token)
