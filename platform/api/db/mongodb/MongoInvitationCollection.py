#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
from datetime   import datetime
from utils      import lazyProperty
from api.Schemas    import *
import pymongo

from api.db.mongodb.AMongoCollection           import AMongoCollection
from api.db.mongodb.MongoInviteQueueCollection import MongoInviteQueueCollection

class MongoInvitationCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'invitations')
        self._collection.ensure_index([('_id', pymongo.ASCENDING), ('invited_by', pymongo.ASCENDING)])
    
    ### PUBLIC
    
    @lazyProperty
    def invite_queue(self):
        return MongoInviteQueueCollection()

    def checkInviteExists(self, email, userId):
        try:
            document = self._collection.find_one({
                '_id': email, 
                'invited_by': {'$elemMatch': {'user_id': userId}},
                })
            if document['_id'] != email:
                raise
            exists = True
        except:
            exists = False
        
        return exists
    
    def inviteUser(self, email, userId):
        data = {
            'user_id': userId, 
            'timestamp': datetime.utcnow(),
        }
        
        self._collection.update(
            {'_id': email},
            {'$addToSet': {'invited_by': data}},
            upsert=True
        )
        
        # Queue email to be sent
        invite = Invite()
        invite.recipient_email = email
        invite.user_id = userId
        invite.created = datetime.utcnow()
        self.invite_queue.addInvite(invite)
        
        return True
    
    def getInvitations(self, email):
        document = self._collection.find_one({'_id': email})
        if document and 'invited_by' in document \
            and isinstance(document['invited_by'], list):
            return document['invited_by']
        return []

    def join(self, email):
        try:
            self._collection.update(
                { '_id' : email },
                { '$set' : { 'joined' : True }}
            )
        except:
            ### TODO: What happens if the update fails? 
            pass
    
    def remove(self, email):
        try:
            self._collection.remove({'_id': email})
        except:
            pass
