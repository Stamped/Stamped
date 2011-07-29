#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals

from utils import lazyProperty

from MongoUserStamps import MongoUserStamps
from MongoInboxStamps import MongoInboxStamps
from MongoStamp import MongoStamp

from api.ACollectionDB import ACollectionDB

class MongoCollection(ACollectionDB):
    
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self):
        ACollectionDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def inbox_stamp_collection(self):
        return MongoInboxStamps()
    
    @lazyProperty
    def stamp_collection(self):
        return MongoInboxStamps()
    
    def getInboxStampIDs(self, userId, since=None, limit=None):
        return self.inbox_stamp_collection.getInboxStampIds(userId, since, limit)
    
    def getInboxStamps(self, userId, since=None, before=None, limit=None):
        return MongoStamp().getStamps(self.getInboxStampIDs(userId), since=since, before=before, limit=limit, withComments=True)
    
    def getUserStampIDs(self, userId, limit=None):
        return MongoUserStamps().getUserStampIds(userId)
    
    def getUserStamps(self, userId, since=None, before=None, limit=None):
        return MongoStamp().getStamps(self.getUserStampIDs(userId), since=since, before=before, limit=limit, withComments=True)
    
    def getMentions(self, userId, limit=None):
        raise NotImplementedError

