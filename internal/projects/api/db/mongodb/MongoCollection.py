#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

# from MongoDB import Mongo
from ACollectionDB import ACollectionDB
from MongoUserStamps import MongoUserStamps
from MongoInboxStamps import MongoInboxStamps
from MongoStamp import MongoStamp

class MongoCollection(ACollectionDB):
        
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    DESC = 'Mongo Collections Wrapper'
    
    def __init__(self, setup=False):
        ACollectionDB.__init__(self, self.DESC)
        
        
    ### PUBLIC
    
    def getInboxStampIds(self, userId, limit=None):
        return MongoInboxStamps().getInboxStampIds(userId, limit)
    
    def getInboxStamps(self, userId, limit=None):
        return MongoStamp().getStamps(self.getInboxStampIds(userId, limit))
    
    def getUserStampIds(self, userId):
        return MongoUserStamps().getUserStampIds(userId)
    
    def getUserStamps(self, userId):
        return MongoStamp().getStamps(self.getUserStampIds(userId))
        
        
    
    def getFavoriteStamps(self, userId):
        raise NotImplementedError
    
    def getMentions(self, userId):
        raise NotImplementedError


    ### PRIVATE
    