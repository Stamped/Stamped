#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, auth, utils
from datetime import datetime

from AMongoCollection import AMongoCollection

from api.AAccountDB import AAccountDB
from api.Account import Account

class MongoAccountCollection(AMongoCollection, AAccountDB):
    
    SCHEMA = {
        '_id': object,
        'first_name': basestring,
        'last_name': basestring,
        'email': basestring,
        'password': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'profile_image': basestring,
        'color_primary': basestring,
        'color_secondary': basestring,
        'bio': basestring,
        'website': basestring,
        'privacy': bool,
        'locale': {
            'language': basestring,
            'time_zone': basestring
        },
        'linked_accounts': {
            'itunes': basestring
        },
        'devices': {
            'ios_device_tokens': list
        },
        'flags': {
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
    
    def __init__(self):
        AMongoCollection.__init__(self, 'users')
        AAccountDB.__init__(self)
    
    ### PUBLIC
    
    def addAccount(self, user):
        ### TEMP: For now, verify that no duplicates can occur
        self._collection.ensure_index('screen_name', unique=True)
        user['password'] = auth.generatePasswordHash(user['password'])
        
        return self._addDocument(user, objId='user_id')
    
    def getAccount(self, userID):
        user = Account(self._getDocumentFromId(userID, objId='user_id'))
        if user.isValid == False:
            print str(user)
            raise KeyError("User not valid")
        return user
    
    def updateAccount(self, user):
        return self._updateDocument(user, objId='user_id')
    
    def removeAccount(self, userID):
        return self._removeDocument(userID)
    
    def flagUser(self, user):
        # TODO
        raise NotImplementedError("TODO")

    def verifyAccountCredentials(self, screen_name, password):
        utils.logs.debug("verifyAccountCredentials: %s:%s" % (screen_name, password))
        try:
            user = self._collection.find_one({'screen_name': screen_name})
            utils.logs.debug("User data: %s" % (user))
            if auth.comparePasswordToHash(password, user['password']):
                return user['_id']
            return None
        except:
            return None

