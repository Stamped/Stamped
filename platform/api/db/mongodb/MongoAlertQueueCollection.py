#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty

from Schemas import *

from AMongoCollection import AMongoCollection
# from AAlertDB import AAlertDB

class MongoAlertQueueCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='alertqueueold', primary_key='alert_id', obj=Alert)
        # AAlertDB.__init__(self)

        self._collection.ensure_index('created', unique=False)

    ### PUBLIC

    def numAlerts(self):
        num = self._collection.find().count()
        return num
    
    def getAlerts(self, **kwargs):
        limit       = kwargs.pop('limit', 5)
        
        documents = self._collection.find().sort('timestamp.created', \
            pymongo.ASCENDING).limit(limit)

        alert = []

        for document in documents:
            alert.append(self._convertFromMongo(document))

        return alert
    

    def addAlert(self, alert):
        result = self._collection.insert_one(alert.value)
        return result
    

    def addAlerts(self, alerts):
        objects = []
        for alert in alerts:
            objects.append(alert.value)
        result = self._collection.insert(objects)
        return result

        
    def removeAlert(self, alertId, **kwargs):
        documentId = self._getObjectIdFromString(alertId)
        result = self._removeMongoDocument(documentId)

