#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from utils import lazyProperty

from MongoUserStampsCollection import MongoUserStampsCollection
from MongoInboxStampsCollection import MongoInboxStampsCollection
from MongoCreditReceivedCollection import MongoCreditReceivedCollection

from api.ACollectionDB import ACollectionDB

class MongoCollectionCollection(ACollectionDB):
    
    def __init__(self):
        ACollectionDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def user_credit_collection(self):
        return MongoCreditReceivedCollection()

    
    def getInboxStampIds(self, userId):
        return self.inbox_stamps_collection.getInboxStampIds(userId)
    
    def getUserStampIds(self, userId):
        return self.user_stamps_collection.getUserStampIds(userId)
    
    def getUserCreditStampIds(self, userId):
        return self.user_credit_collection.getCredit(userId)

    def getMentions(self, userId):
        raise NotImplementedError
