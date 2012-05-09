#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, ast, pymongo

from bson.objectid import ObjectId
from AMongoCollection import AMongoCollection

class MongoLogsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='logs')
    
    ### PUBLIC
    
    def addLog(self, logData):
        try:
            if 'form' in logData:
                ### TODO: Is this storing UTF characters?
                logData['form'] = str(logData['form'])

            return self._collection.insert_one(logData, log=False, safe=False)
        except Exception as e:
            print e
            raise

    def saveLog(self, logData, logId=None):
        try:
            if 'form' in logData:
                logData['form'] = str(logData['form'])

            # if '_id' not in logData and logId:
            #     logData['_id'] = logId

            if '_id' in logData:
                logData.pop('_id')

            self._collection.save(logData, log=False, safe=False)
        except Exception as e:
            print e
            raise


    def getLogs(self, userId=None, **kwargs):
        limit       = kwargs.pop('limit', 10)
        errors      = kwargs.pop('errors', False)
        path        = kwargs.pop('path', None)
        severity    = kwargs.pop('severity', None)
        requestId   = kwargs.pop('requestId', None)
        method      = kwargs.pop('method', None)

        query = {}

        if userId != None:
            query['user_id'] = userId
        if requestId is not None:
            query['request_id'] = requestId
        if errors == True:
            query['result'] = {'$exists': True}
        if path != None:
            query['path'] = path
        if severity != None:
            query[severity] = True
        if method is not None:
            query['method'] = str(method).upper()

        docs = self._collection.find(query).limit(limit).sort('begin', pymongo.DESCENDING)
        
        logs = []
        for doc in docs:
            if 'form' in doc:
                doc['form'] = ast.literal_eval(doc['form'])
            logs.append(doc)
        
        return logs

