#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals

from utils import lazyProperty

from MongoUserStampsCollection import MongoUserStampsCollection
from MongoInboxStampsCollection import MongoInboxStampsCollection
from MongoStampCollection import MongoStampCollection

from api.ACollectionDB import ACollectionDB

class MongoCollectionCollection(ACollectionDB):
    
    def __init__(self):
        ACollectionDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def stamp_collection(self):
        return MongoStampCollection()
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    def getInboxStampIDs(self, userId, since=None, limit=None):
        return self.inbox_stamps_collection.getInboxStampIds(userId, since, limit)
    
    def getInboxStamps(self, userId, since=None, before=None, limit=None):
        return self.stamp_collection.getStamps(self.getInboxStampIDs(userId), since=since, before=before, limit=limit, withComments=True)
    
    def getUserStampIDs(self, userId, limit=None):
        return self.user_stamps_collection.getUserStampIds(userId)
    
    def getUserStamps(self, userId, since=None, before=None, limit=None):
        return self.stamp_collection.getStamps(self.getUserStampIDs(userId), since=since, before=before, limit=limit, withComments=True)
    
    def getMentions(self, userId, limit=None):
        raise NotImplementedError

