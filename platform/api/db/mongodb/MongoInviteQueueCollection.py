#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty
from errors import *

from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoInviteQueueCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='invitequeue', primary_key='invite_id', obj=Invite)

        self._collection.ensure_index('created', unique=False)

    ### PUBLIC

    def numInvites(self):
        num = self._collection.find().count()
        return num
    
    
    def getInvites(self, **kwargs):
        limit       = kwargs.pop('limit', 5)
        
        documents = self._collection.find().sort('timestamp.created', \
            pymongo.ASCENDING).limit(limit)

        invite = []

        for document in documents:
            invite.append(self._convertFromMongo(document))

        return invite
    

    def addInvite(self, invite):
        result = self._collection.insert_one(invite.dataExport())
        return result
    

    def addInvites(self, invites):
        objects = []
        for invite in invites:
            objects.append(invite.dataExport())
        result = self._collection.insert(objects)
        return result

        
    def removeInvite(self, inviteId, **kwargs):
        documentId = self._getObjectIdFromString(inviteId)
        result = self._removeMongoDocument(documentId)

