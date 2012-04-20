#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, utils, logs, pymongo

from AMongoCollection import AMongoCollection
from Schemas import *

class MongoActivityItemCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activityitems', 
                                        primary_key='activity_id', 
                                        obj=Activity, 
                                        overflow=True)
    
    ### PUBLIC
    
    def addActivityItem(self, activity):
        return self._addObject(activity)

    def addSubjectToActivityItem(self, activityId, subjectId):
        documentId = self._getObjectIdFromString(activityId)
        result = self._collection.update({'_id': documentId}, {'$addToSet': {'subjects': subjectId}})
        return result

    def setBenefitForActivityItem(self, activityId, benefit):
        documentId = self._getObjectIdFromString(activityId)
        result = self._collection.update({'_id': documentId}, {'$set': {'benefit': benefit}})
        return result
    
    def removeActivityItem(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        result = self._removeMongoDocument(documentId)
        return result
    
    def removeActivityItems(self, activityIds):
        documentIds = map(self._getObjectIdFromString, activityIds)
        result = self._removeMongoDocuments(documentIds)
        return result

    def removeSubjectFromActivityItem(self, activityId, subjectId):
        documentId = self._getObjectIdFromString(activityId)
        result = self._collection.update({'_id': documentId}, {'$pullAll': {'subjects': subjectId}})
        return result

    def removeSubjectFromActivityItems(self, activityIds, subjectId):
        documentIds = map(self._getObjectIdFromString, activityIds)
        self._collection.update({'_id': {'$in': documentIds}}, {'$pullAll': {'subjects': subjectId}})
        emptyIds = self._collection.find({'_id': {'$in': documentIds}, 'subjects': []}, fields={'_id' : 1})
        return map(self._convertFromMongo, emptyIds)

    def getActivityItem(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def getActivityItems(self, activityIds, **kwargs):
        ids = map(self._getObjectIdFromString, activityIds)

        documents = self._getMongoDocumentsFromIds(ids, **kwargs)

        return map(self._convertFromMongo, documents)

    def getActivityIds(self, **kwargs):
        query = {}

        # Subjects
        subjects = kwargs.pop('subjects', [])
        if len(subjects) > 0:
            query['subjects'] = { '$in' : subjects }

        # Verb
        verb = kwargs.pop('verb', None)
        if verb is not None:
            query['verb'] = verb 

        # Objects
        objects = kwargs.pop('objects', {})
        for k, v in objects.iteritems():
            if len(v) > 0:
                query['objects.%s' % k] = { '$in' : v }

        documents = self._collection.find(query, fields={'_id' : 1})

        result = []
        for document in documents:
            result.append(self._getStringFromObjectId(document['_id']))
        return result

    def getActivityForUsers(self, userIds, **kwargs):
        if len(userIds) == 0:
            return []
        
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        query = { 'subjects' : {'$in' : userIds } }

        if since is not None and before is not None:
            query['timestamp.modified'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.modified'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.modified'] = { '$lte' : before }

        documents = self._collection.find(query).sort('timestamp.modified', pymongo.DESCENDING).limit(limit)

        return map(self._convertFromMongo, documents)


