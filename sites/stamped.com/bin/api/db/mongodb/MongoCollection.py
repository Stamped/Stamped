#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
import copy

from threading import Lock
from datetime import datetime

# from MongoDB import Mongo
from api.ACollectionDB import ACollectionDB
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
    
    def getInboxStampIDs(self, userId, limit=None):
        return MongoInboxStamps().getInboxStampIds(userId, limit)
    
    def getInboxStamps(self, userId, limit=None, output='object'):
        return MongoStamp().getStamps(self.getInboxStampIDs(userId, limit), output)
    
    def getUserStampIDs(self, userId, limit=None):
        return MongoUserStamps().getUserStampIds(userId)
    
    def getUserStamps(self, userId, limit=None, output='object'):
        return MongoStamp().getStamps(self.getUserStampIDs(userId, limit), output)
    
    def getMentions(self, userId, limit=None):
        raise NotImplementedError


    ### PRIVATE
    
