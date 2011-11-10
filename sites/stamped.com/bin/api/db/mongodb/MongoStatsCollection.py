#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, ast, pymongo

from AMongoCollection import AMongoCollection

class MongoStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='logstats')
    
    ### PUBLIC
    
    def addStat(self, statData):
        try:
            # Only add specific parameters
            stat = {}

            if 'user_id' in statData:
                stat['uid'] = statData['user_id']

            if 'path' in statData:
                stat['uri'] = statData['path']

            if 'method' in statData:
                stat['mtd'] = statData['method']

            if 'form' in statData:
                stat['frm'] = str(statData['form'])

            if 'result' in statData:
                stat['cde'] = statData['result']

            if 'begin' in statData:
                stat['bgn'] = statData['begin']

            if 'finish' in statData:
                stat['end'] = statData['finish']


            self._collection.insert_one(stat, log=False, safe=False)

        except Exception as e:
            print e
            raise


    def getStats(self, **kwargs):
        limit       = kwargs.pop('limit', 10)
        errors      = kwargs.pop('errors', False)
        path        = kwargs.pop('path', None)
        userId      = kwargs.pop('userId', None)

        query = {}

        if userId != None:
            query['uid'] = userId 
        if errors == True:
            query['cde'] = {'$exists': True}
        if path != None:
            query['uri'] = path

        docs = self._collection.find(query).limit(limit).sort('begin', pymongo.DESCENDING)
        
        logs = []
        for doc in docs:
            if 'form' in doc:
                doc['form'] = ast.literal_eval(doc['form'])
            logs.append(doc)
        
        return logs

