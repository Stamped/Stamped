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
# from Friendship import Friendship
from MongoUserStamps import MongoUserStamps
from MongoStamp import MongoStamp

class MongoCollection(ACollectionDB):
        
    COLLECTION = 'userstamps'
        
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    DESC = 'Mongo Collections Wrapper'
    
    def __init__(self, setup=False):
        ACollectionDB.__init__(self, self.DESC)
#         Mongo.__init__(self, collection=self.COLLECTION)
        
        
    ### PUBLIC
    
    def getInboxStamps(self, userId):
        raise NotImplementedError
    
    def getUserStampIds(self, userId):
        return MongoUserStamps().getUserStampIds(userId)
    
    def getUserStamps(self, userId):
        return MongoStamp().getStamps(self.getUserStampIds(userId))
    
    def getFavoriteStamps(self, userId):
        raise NotImplementedError
    
    def getMentions(self, userId):
        raise NotImplementedError


    ### PRIVATE
    