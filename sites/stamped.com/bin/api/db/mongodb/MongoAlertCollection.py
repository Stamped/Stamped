#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty

from Schemas import *

from AMongoCollection import AMongoCollection
# from AAlertDB import AAlertDB

class MongoAlertCollection(AMongoCollection):
    
    """
    Alert Types:
    * restamp
    * mention
    * comment
    * reply
    * like
    * favorite
    * invite_sent
    * invite_received
    * follower
    """
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='alerts', primary_key='alert_id', obj=Alert)
        # AAlertDB.__init__(self)

        self._collection.ensure_index('created', pymongo.ASCENDING)

    ### PUBLIC
    
    def getAlerts(self, userId, **kwargs):
        limit       = kwargs.pop('limit', 20)

        params = {'recipient_id': userId}
        
        documents = self._collection.find(params).sort('timestamp.created', \
            pymongo.ASCENDING).limit(limit)

        alert = []
        for document in documents:
            alert.append(self._convertFromMongo(document))

        return alert
    

    def addAlert(self, alert):
        result = self._collection.insert_one(alert.value)

        
    def removeAlert(self, genre, userId, **kwargs):
        stampId     = kwargs.pop('stampId', None)

        if genre in ['like', 'favorite'] and stampId:
            self._collection.remove({
                'user.user_id': userId,
                'link.linked_stamp_id': stampId,
                'genre': genre
            })







