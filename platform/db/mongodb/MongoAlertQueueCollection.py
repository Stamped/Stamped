#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty

from api_old.Schemas import *

from db.mongodb.AMongoCollection import AMongoCollection
# from AAlertDB import AAlertDB

class MongoAlertQueueCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='alertqueue', primary_key='alert_id', obj=Alert)
        # AAlertDB.__init__(self)

        self._collection.ensure_index('timestamp.created', unique=False)
        self._collection.ensure_index([('recipient_id',pymongo.ASCENDING), ('timestamp.created',pymongo.ASCENDING)])

    ### PUBLIC

    def numAlerts(self):
        num = self._collection.find().count()
        return num
    
    def getAlerts(self, **kwargs):
        limit       = kwargs.pop('limit', 5)
        
        documents = self._collection.find().sort('timestamp.created', pymongo.ASCENDING).limit(limit)

        alerts = [self._convertFromMongo(doc) for doc in documents]
        return alerts

    def getAlertsForUser(self, userId):
        documents = self._collection.find({'recipient_id' : userId }).sort('timestamp.created', pymongo.ASCENDING)
        alerts = [self._convertFromMongo(doc) for doc in documents]
        return alerts

    def addAlert(self, alert):
        result = self._collection.insert_one(alert.dataExport())
        return result

    def addAlerts(self, alerts):
        objects = []
        for alert in alerts:
            objects.append(alert.dataExport())
        result = self._collection.insert(objects)
        return result

        
    def removeAlert(self, alertId, **kwargs):
        documentId = self._getObjectIdFromString(alertId)
        result = self._removeMongoDocument(documentId)

