#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import pymongo
import bson
import copy

from AEntityDB import AEntityDB
from threading import Lock
from datetime import datetime

class Mongo():
    USER    = 'root'
    PASS    = None
    CONN    = 'ec2-50-19-194-148.compute-1.amazonaws.com'
    PORT    = 27017
    DB      = 'stamped_test'
    DESC    = 'MongoDB:%s' % (DB)
    
    def __init__(self, collection, mapping=None, setup=False, conn=CONN, port=PORT, db=DB):
        self.user = self.USER
        self._desc = self.DESC
        self._lock = Lock()
        self._mapping = mapping
        self._conn = conn
        self._port = port
        self._db = db
#         if setup:
#             self._setup()
        self._connection = self._connect()
        self._database = self._getDatabase()
        self._collection = self._getCollection(collection)
    
    def _connect(self):
        return pymongo.Connection(self._conn, self._port)
        
    def _getDatabase(self):
        return self._connection[self._db]
        
    def _getCollection(self, collection):
        return self._database[collection]
        
    def _endRequest(self):
        self._connection.end_request()
        
        
    def _encodeBSON(self, obj):
        return bson.BSON.encode(obj)
        
    def _getStringFromObjectId(self, objId):
        return str(bson.objectid.ObjectId(objId))
        
    def _getObjectIdFromString(self, string):
        return bson.objectid.ObjectId(string)
        
        
    def _mongoToObj(self, data):
        data['id'] = self._getStringFromObjectId(data['_id'])
        del(data['_id'])
        return data
    
    def _objToMongo(self, obj):
        if obj.isValid == False:
            # print obj
            raise KeyError("Object not valid")
        data = copy.copy(obj.getDataAsDict())
        if '_id' in data:
            if isinstance(data['_id'], basestring):
                data['_id'] = self._getObjectIdFromString(data['_id'])
        if 'id' in data:
            data['_id'] = self._getObjectIdFromString(data['id'])
            del(data['id'])
        return self._mapDataToSchema(data, self.SCHEMA)
        
    def _objsToMongo(self, objs):
        return map(self._objToMongo, objs)
        
        
    def _mapDataToSchema(self, data, schema):
        
        def _unionDict(source, schema, dest):
            for k, v in source.iteritems():
                _unionItem(k, v, schema, dest)
            return dest
        
        def _unionItem(k, v, schema, dest):
            if k in schema:
                schemaVal = schema[k]
                
                if isinstance(schemaVal, type):
                    schemaValType = schemaVal
                else:
                    schemaValType = type(schemaVal)
                
                # basic type checking
                if not isinstance(v, schemaValType):
                    isValid = True
                    
                    # basic implicit type conversion s.t. if you pass in, for example, 
                    # "23.4" for longitude as a string, it'll automatically cast to 
                    # the required float format.
                    try:
                        if schemaValType == basestring:
                            v = str(v)
                        elif schemaValType == float:
                            v = float(v)
                        elif schemaValType == int:
                            v = int(v)
                        else:
                            isValid = False
                    except ValueError:
                        isValid = False
                    
                    if not isValid:
                        raise KeyError("Entity error; key '%s' found '%s', expected '%s'" % \
                            (k, str(type(v)), str(schemaVal)))
                
                if isinstance(v, dict):
                    if k not in dest:
                        dest[k] = { }
                    
                    return _unionDict(v, schemaVal, dest[k])
                else:
                    dest[k] = v
                    return dest
            else:
                for k2, v2 in schema.iteritems():
                    if isinstance(v2, dict):
                        if k2 in dest:
                            if not isinstance(dest[k2], dict):
                                raise KeyError(k2)
                            
                            if _unionItem(k, v, v2, dest[k2]):
                                return dest
                        else:
                            temp = { }
                            
                            if _unionItem(k, v, v2, temp):
                                dest[k2] = temp
                                return dest
            return dest
        
        result = {}
        if not _unionDict(data, schema, result):
            raise KeyError("Error: %s" % str(data))

        return result
        
        
    ### RELATIONSHIP MANAGEMENT
        
    def _getOverflowBucket(self, objId):
        overflow = self._collection.find_one({'_id': objId}, fields={'overflow': 1})

        if overflow == None or 'overflow' not in overflow:
            return objId            
        else:
            # Do something to manage overflow conditions?
            # Grabs the most recent bucket to use and appends that to the id. This is our new key!
            return '%s%s' % (objId, overflow['overflow'][-1])
        
        
    ### GENERIC CRUD FUNCTIONS
    
    def _addDocument(self, document):
        return self._getStringFromObjectId(self._collection.insert(self._objToMongo(document)))
    
    def _addDocuments(self, documents):
        return self._collection.insert(self._objsToMongo(documents))
        
    def _getDocumentFromId(self, documentId):
        document = self._mongoToObj(self._collection.find_one(self._getObjectIdFromString(documentId)))
        return document
        
    def _getDocumentsFromIds(self, documentIds):
        ids = []
        for documentId in documentIds:
            ids.append(self._getObjectIdFromString(documentId))
        documents = self._collection.find({'_id': {'$in': ids}})
        result = []
        for document in documents:
            result.append(self._mongoToObj(document))
        return result
        
    def _updateDocument(self, document):
        return self._collection.save(self._objToMongo(document))
        
    def _removeDocument(self, document):
        return self._collection.remove(self._objToMongo(document))
        
    
    ### GENERIC RELATIONSHIP FUNCTIONS
        
    def _createRelationship(self, keyId, refId):
        self._collection.update({'_id': self._getOverflowBucket(keyId)}, 
                                {'$addToSet': {'ref_ids': refId}},
                                upsert=True)
        return True
            
    def _removeRelationship(self, keyId, refId):
        doc = self._collection.find_one({'_id': keyId})
        
        if doc == None:
            return False
            
        elif refId in doc['ref_ids']:
            self._collection.update({'_id': keyId}, 
                                    {'$pull': {'ref_ids': refId}})
            return True
            
        elif 'overflow' in doc:
            # Check other buckets
            buckets = []
            for bucket in doc['overflow']:
                buckets.append('%s%s' % (keyId, bucket))
                
            for moreDocs in self._collection.find({'_id': {'$in': buckets}}):
                if refId in moreDocs['ref_ids']:
                    self._collection.update({'_id': moreDocs['_id']}, 
                                            {'$pull': {'ref_ids': refId}})
                    return True
            return False
            
        else:
            return False
    
    def _checkRelationship(self, keyId, refId):
        doc = self._collection.find_one({'_id': keyId})
        
        if doc == None:
            return False
            
        elif refId in doc['ref_ids']:
            return True
            
        elif 'overflow' in doc:
            # Check other buckets
            buckets = []
            for bucket in doc['overflow']:
                buckets.append('%s%s' % (keyId, bucket))
                
            for moreDocs in self._collection.find({'_id': {'$in': buckets}}):
                if refId in moreDocs['ref_ids']:
                    return True
            return False
            
        else:
            return False
            
    def _getRelationships(self, keyId):
        doc = self._collection.find_one({'_id': keyId})
        
        if doc == None:
            return []
        else:
            ids = doc['ref_ids']
            if 'overflow' in doc:
                # Check other buckets
                buckets = []
                for bucket in doc['overflow']:
                    buckets.append('%s%s' % (keyId, bucket))
                    
                for moreDocs in self._collection.find({'_id': {'$in': buckets}}):
                    ids = ids + moreDocs['ref_ids']
            return ids
            

    