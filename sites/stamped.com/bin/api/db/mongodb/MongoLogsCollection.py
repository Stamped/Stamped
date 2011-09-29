#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, ast, pymongo

from AMongoCollection import AMongoCollection

class MongoLogsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='logs')
    
    ### PUBLIC
    
    def addLog(self, logData):
        try:
            # print 'LOG DATA: %s' % logData
            if 'form' in logData:
                logData['form'] = str(logData['form'])

            # if 'headers' in logData:
            #     logData['headers'] = str(logData['headers'])#pickle.dumps(logData['headers'])

            self._collection.insert_one(logData, log=False)
        except Exception as e:
            print e
            raise

    def getLogs(self, userId=None, **kwargs):
        limit       = kwargs.pop('limit', 10)
        errors      = kwargs.pop('errors', False)
        path        = kwargs.pop('path', None)
        severity    = kwargs.pop('severity', None)
        logId       = kwargs.pop('log_id', None)

        query = {}
        if userId != None:
            query['user_id'] = userId 
        if errors == True:
            query['result'] = {'$exists': True}
        if path != None:
            query['path'] = path
        if severity != None:
            query[severity] = True

        docs = self._collection.find(query).limit(limit).sort('begin', pymongo.DESCENDING)
        
        logs = []
        for doc in docs:
            if 'form' in doc:
                doc['form'] = ast.literal_eval(doc['form'])
            logs.append(doc)
        
        return logs

