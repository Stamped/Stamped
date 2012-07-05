#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty

from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection
# from AAlertDB import AAlertDB

class MongoAlertAPNSCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='apnstokens')
        # AAlertDB.__init__(self)

    ### PUBLIC

    def addToken(self, token, userId):
        document = self._collection.insert({
            '_id': token,
            'user_id': userId,
        })

    def getToken(self, token):
        try:
            document = self._collection.find_one({'_id': token})
            return document['user_id']
        except:
            return None

    def removeToken(self, token):
        result = self._removeMongoDocument(token)


