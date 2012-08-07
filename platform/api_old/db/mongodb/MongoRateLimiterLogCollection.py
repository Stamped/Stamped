#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
from datetime import datetime
from db.mongodb.AMongoCollection import AMongoCollection

class MongoRateLimiterLogCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='rllog')

    ### PUBLIC
    def _getUtcDay(self, utctime):
        """ Return the datetime of the start of the utc day
        """
        return datetime(utctime.year, utctime.month, utctime.day)

    def updateLog(self, callMap):
        """ accepts a dict of { <service_name> : <num_calls> }
        """
        today = self._getUtcDay(datetime.utcnow())
        callMap.update({'_id' : today})
        return self._collection.update({'_id': today}, callMap, upsert=True)


    def getLog(self, utctime=datetime.utcnow()):
        return self._collection.find_one({'_id': self._getUtcDay(utctime)})
