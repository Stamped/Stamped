#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from db.mongodb.AMongoCollection import AMongoCollection
from bson import ObjectId


class MongoFBCallbackTokenCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userfbcallbacktokens')

    ### PUBLIC

    def addUserId(self, userId):
        oid = ObjectId()
        self._collection.insert({'_id': oid, 'user_id' : userId })
        return str(oid)

    def getUserId(self, oid):
        return self._collection.find_one({'_id' : ObjectId(oid)})['user_id']

    def removeUserId(self, oid):
        return self._collection.remove({'_id' : ObjectId(oid)})