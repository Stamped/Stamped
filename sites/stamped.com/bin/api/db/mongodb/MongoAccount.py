#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from api.AAccountDB import AAccountDB
from api.Account import Account

class MongoAccount(AAccountDB, Mongo):
        
    COLLECTION = 'users'
        
    SCHEMA = {
        '_id': object,
        'first_name': basestring,
        'last_name': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'email': basestring,
        'password': basestring,
        'image': basestring,
        'bio': basestring,
        'website': basestring,
        'color': {
            'primary': list,
            'secondary': list
        },
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
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        }
    }
    
    def __init__(self, setup=False):
        AAccountDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addAccount(self, user):
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
        return True
        
    def flagUser(self, user):
        ### TODO
        print 'TODO'
            
    
    ### PRIVATE
        
