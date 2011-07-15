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
from api.User import User

class MongoAccount(AAccountDB, Mongo):
        
    COLLECTION = 'users'
        
    SCHEMA = {
        '_id': object,
        'first_name': basestring,
        'last_name': basestring,
        'username': basestring,
        'email': basestring,
        'password': basestring,
        'img': basestring,
        'locale': basestring,
        'timestamp': basestring,
        'website': basestring,
        'bio': basestring,
        'color': {
            'primary_color': basestring,
            'secondary_color': basestring
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
        }
    }
    
    def __init__(self, setup=False):
        AAccountDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addAccount(self, user):
        return self._addDocument(user)
    
    def getAccount(self, userID):
        user = User(self._getDocumentFromId(userID))
        if user.isValid == False:
            print str(user)
            raise KeyError("User not valid")
        return user
        
    def updateAccount(self, user):
        return self._updateDocument(user)
        
    def removeAccount(self, userID):
        return self._removeDocument(userID)
        
    def flagUser(self, user):
        ### TODO
        print 'TODO'
            
    
    ### PRIVATE
        
