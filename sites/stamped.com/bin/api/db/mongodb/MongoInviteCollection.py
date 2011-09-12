#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, auth, utils, logs
from datetime import datetime
from Schemas import *

from AMongoCollection import AMongoCollection
# from AAccountDB import AAccountDB

class MongoInviteCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'invites')
        # AAccountDB.__init__(self)
    
    ### PUBLIC

    def inviteUser(self, email, userId):
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
        
        if exists == True:
            msg = "Invite already exists"
            logs.warning(msg)
            raise Exception(msg)

        data = {
            'user_id': userId, 
            'timestamp': datetime.utcnow(),
            'sent': False,
        }
        
        self._collection.update(
            {'_id': email},
            {'$addToSet': {'invited_by': data}},
            upsert=True
        )

        return True

    def getInvites(self, email):
        document = self._collection.find_one({'_id': email})
        if document and 'invited_by' in document \
            and isinstance(document['invited_by'], list):
            return document['invited_by']
        return []

    def getUnsentInvites(self):
        pass

    def sendInvitation(self, email, userId):
        pass

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
