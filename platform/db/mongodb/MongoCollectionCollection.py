#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import heapq

from collections                    import defaultdict
from utils                          import lazyProperty
from libs.LRUCache                       import lru_cache

from db.mongodb.MongoUserStampsCollection      import MongoUserStampsCollection
from db.mongodb.MongoInboxStampsCollection     import MongoInboxStampsCollection
from db.mongodb.MongoCreditReceivedCollection  import MongoCreditReceivedCollection
from db.mongodb.MongoFriendshipCollection      import MongoFriendshipCollection

from api_old.ACollectionDB              import ACollectionDB

class MongoCollectionCollection(ACollectionDB):
    
    def __init__(self, api=None):
        ACollectionDB.__init__(self)
        self.api = api
    
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
    
    @lazyProperty
    def friendship_collection(self):
        return MongoFriendshipCollection(self.api)

    