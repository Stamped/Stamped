#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, ast, pymongo
import libs.ec2_utils

from bson.objectid import ObjectId
from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoLogsCollection(AMongoCollection):
    
    def __init__(self, stack_name=None):
        # Change collection name to stack if on EC2
        collection = 'logs'
        if stack_name is not None:
            collection = "logs_%s" % stack_name
        elif libs.ec2_utils.is_ec2():
            stack_info = libs.ec2_utils.get_stack()
            collection = "logs_%s" % stack_info.instance.stack

        AMongoCollection.__init__(self, collection=collection, logger=True)

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
        code        = kwargs.pop('code', None)

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
        if code is not None:
            query['result'] = code

        docs = self._collection.find(query).limit(limit).sort('begin', pymongo.DESCENDING)
        
        logs = []
        for doc in docs:
            if 'form' in doc:
                doc['form'] = ast.literal_eval(doc['form'])
            logs.append(doc)
        
        return logs

