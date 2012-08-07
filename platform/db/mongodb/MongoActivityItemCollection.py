#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, utils, logs, pymongo

from db.mongodb.AMongoCollection import AMongoCollection
from api_old.Schemas import *
from datetime import datetime

class MongoActivityItemCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activityitems', 
                                        primary_key='activity_id', 
                                        obj=Activity, 
                                        overflow=True)

        self._collection.ensure_index('timestamp.modified')
        self._collection.ensure_index([('subjects', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('verb', pymongo.ASCENDING), ('subjects', pymongo.ASCENDING), ('timestamp.modified', pymongo.DESCENDING)])
        self._collection.ensure_index([('verb', pymongo.ASCENDING), ('objects.stamp_ids', pymongo.ASCENDING), ('timestamp.created', pymongo.DESCENDING)])
        self._collection.ensure_index([('verb', pymongo.ASCENDING), ('objects.user_ids', pymongo.ASCENDING), ('timestamp.created', pymongo.DESCENDING)])
        self._collection.ensure_index([('verb', pymongo.ASCENDING), ('objects.entity_ids', pymongo.ASCENDING), ('timestamp.created', pymongo.DESCENDING)])


    
    ### PUBLIC
    
    def addActivityItem(self, activity):
        return self._addObject(activity)

    def addSubjectToActivityItem(self, activityId, subjectId, modified=None):
        if modified is None:
            modified = datetime.utcnow()
        documentId = self._getObjectIdFromString(activityId)
        update = { 
            '$addToSet' : { 'subjects' : subjectId }, 
            '$set'      : { 'timestamp.modified': modified } 
        }
        result = self._collection.update({'_id': documentId}, update)
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
        result = self._collection.update({'_id': documentId}, {'$pull': {'subjects': subjectId}})
        return result

    def removeSubjectFromActivityItems(self, activityIds, subjectId):
        documentIds = map(self._getObjectIdFromString, activityIds)
        self._collection.update({'_id': {'$in': documentIds}}, {'$pull': {'subjects': subjectId}})
        emptyIds = self._collection.find({'_id': {'$in': documentIds}, 'subjects': []}, fields={'_id' : 1})
        return map(lambda x: self._getStringFromObjectId(x['_id']), emptyIds)

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

        # Sources
        source = kwargs.pop('source', None)
        if source is not None:
            query['source'] = source

        # Timestamp
        since = kwargs.pop('since', None)
        if since is not None:
            query['timestamp.created'] = { '$gte' : since }

        if len(query.keys()) == 0:
            raise Exception("No params provided!")

        documents = self._collection.find(query, fields={'_id' : 1})

        result = []
        for document in documents:
            result.append(self._getStringFromObjectId(document['_id']))
        return result

    def getActivityForUsers(self, userIds, **kwargs):
        if len(userIds) == 0:
            return []
        
        query       = { 'subjects' : { '$in' : userIds } }

        verbs       = kwargs.pop('verbs', [])
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        if len(verbs) > 0:
            query['verb'] = { '$in' : verbs }

        if since is not None and before is not None:
            query['timestamp.modified'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.modified'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.modified'] = { '$lte' : before }

        documents = self._collection.find(query).sort('timestamp.modified', pymongo.DESCENDING).limit(limit)

        return map(self._convertFromMongo, documents)


