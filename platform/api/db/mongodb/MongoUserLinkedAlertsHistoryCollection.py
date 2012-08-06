#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoUserLinkedAlertsHistoryCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userlinkedalertshistory')

    ### PUBLIC

    def addLinkedAlert(self, userId, serviceName, serviceId):
        reference = '%s_%s' % (serviceName, serviceId)
        self._createRelationship(keyId=userId, refId=reference)
        return True

    def checkLinkedAlert(self, userId, serviceName, serviceId):
        reference = '%s_%s' % (serviceName, serviceId)
        return self._checkRelationship(userId, reference)

    def getLinkedAlerts(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)

    def removeLinkedAlerts(self, userId):
        return self._removeAllRelationships(userId)