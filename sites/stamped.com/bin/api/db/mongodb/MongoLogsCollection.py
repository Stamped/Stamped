#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, pickle

from AMongoCollection import AMongoCollection

class MongoLogsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='logs')
    
    ### PUBLIC
    
    def addLog(self, logData):
        try:
            if 'form' in logData:
                logData['form'] = pickle.dumps(logData['form'])

            if 'headers' in logData:
                logData['headers'] = pickle.dumps(logData['headers'])

            self._collection.insert_one(logData, log=False)
        except Exception as e:
            print e
            raise

