#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import bson, copy, math, os, pymongo, time, utils, atexit, logs

from pprint import pprint
from errors import Fail
from utils import AttributeDict, getPythonConfigFile, Singleton, lazyProperty
from datetime import datetime
from pymongo.errors import AutoReconnect
from MongoCollectionProxy import MongoCollectionProxy

class MongoDBConfig(Singleton):
    def __init__(self):
        self.config = AttributeDict()
        self._connection = None
        self._init()
        
        def disconnect():
            ### TODO: Add disconnect from MongoDB
            if self._connection is not None:
                self._connection.disconnect()
                self._connection = None
        
        atexit.register(disconnect)
    
    @property
    def isValid(self):
        return 'mongodb' in self.config and \
                  'host' in self.config.mongodb and \
                  'port' in self.config.mongodb
    
    def _init(self):
        ### TODO: Make this more robust!
        try:
            config_path = os.path.abspath(__file__)
            for i in xrange(4):
                config_path = os.path.dirname(config_path)
            config_path = os.path.join(config_path, "conf/stamped.conf")
            self.config = getPythonConfigFile(config_path, jsonPickled=True)
            if not 'mongodb' in self.config:
                raise Exception()
        except:
            try:
                config_path = os.path.abspath(__file__)
                for i in xrange(8):
                    config_path = os.path.dirname(config_path)
                config_path = os.path.join(config_path, "conf/stamped.conf")
                #print config_path
                self.config = getPythonConfigFile(config_path, jsonPickled=True)
                #print self.config
            except:
                raise Fail("Error: invalid configuration file")
                raise
        
        if not 'mongodb' in self.config:
            logs.info("Invalid config file; defaulting to localhost:30000")
            # self.config = AttributeDict({
            #     "mongodb" : {
            #         "host" : "ec2-50-19-194-148.compute-1.amazonaws.com", 
            #         "port" : 27017, 
            #     }
            # })
            self.config = AttributeDict({
               "mongodb" : {
                   "host" : "localhost", 
                   "port" : 27017, 
               }
            })
            # self.config = AttributeDict({
            #    "mongodb" : {
            #        "host" : "localhost", 
            #        "port" : 30000, 
            #    }
            # })
    
    @property
    def host(self):
        return str(self.config.mongodb.host)
    
    @property
    def port(self):
        return int(self.config.mongodb.port)
    
    @property
    def user(self):
        if 'user' in self.config.mongodb:
            return str(self.config.mongodb.user)
        else:
            return 'root'
    
    @property
    def connection(self):
        if self._connection:
            return self._connection
        
        # TODO: have a more consistent approach to handling AutoReconnect!
        logs.debug("Creating connection")
        
        delay = 1
        max_delay = 16
        
        while True:            
            try:
                logs.info("Connecting to MongoDB: %s:%d" % (self.host, self.port))
                self._connection = pymongo.Connection(self.host, self.port, \
                    slave_okay=True)
                return self._connection
            except AutoReconnect as e:
                if delay > max_delay:
                    raise
                
                logs.warning("Retrying to connect to host: %s" % (str(e)))
                logs.warning("Delay: %s" % delay)
                time.sleep(delay)
                delay *= 2
    
    def __str__(self):
        return self.__class__.__name__

class AMongoCollection(object):
    
    def __init__(self, collection, primary_key=None, obj=None, overflow=False):
        self._desc = self.__class__.__name__
        
        self._init_collection('stamped', collection)
        self._primary_key = primary_key
        self._obj = obj
        self._overflow = overflow
    
    def _init_collection(self, db, collection):
        cfg = MongoDBConfig.getInstance()
        self._collection = MongoCollectionProxy(self, cfg.connection, db, \
                                                collection)
        
        logs.info("Connected to MongoDB collection: %s" % collection)
    
    def _validateUpdate(self, result):
        try:
            if result['ok'] == 1 and result['err'] == None:
                return True
        except:
            return False
        return False
    
    def _encodeBSON(self, obj):
        return bson.BSON.encode(obj)
    
    def _getStringFromObjectId(self, objId):
        return str(bson.objectid.ObjectId(objId))
    
    def _getObjectIdFromString(self, string):
        try:
            return bson.objectid.ObjectId(string)
        except:
            logs.warning("Invalid ObjectID (%s)" % string)
            raise
    
    def _convertToMongo(self, obj):
        if obj is None:
            return None
        
        if self._obj is not None:
            assert obj.__class__.__name__ == self._obj.__name__
        
        document = obj.exportSparse()
        
        if self._primary_key:
            if self._primary_key in document:
                document['_id'] = self._getObjectIdFromString(document[self._primary_key])
                del(document[self._primary_key])
        
        return document
    
    def _convertFromMongo(self, document):
        if document is None:
            return None
        
        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        
        if self._obj is not None:
            return self._obj(document, overflow=self._overflow)
        else:
            return document
    
    ### GENERIC CRUD FUNCTIONS
    
    def _addObject(self, obj):
        if self._obj is not None:
            assert obj.__class__.__name__ == self._obj.__name__
        
        document = self._convertToMongo(obj)
        document = self._addMongoDocument(document)
        from pprint import pformat
        #pprint(document)
        logs.warning(pformat(document))
        
        obj      = self._convertFromMongo(document)
        
        if self._obj is not None:
            assert obj.__class__.__name__ == self._obj.__name__
        
        return obj
    
    def _addObjects(self, objs):
        if self._obj is not None:
            for obj in objs:
                assert obj.__class__.__name__ == self._obj.__name__
        
        documents = map(self._convertToMongo, objs)
        documents = self._addMongoDocuments(documents)
        objs      = map(self._convertFromMongo, documents)
        
        if self._obj is not None:
            for obj in objs:
                assert obj.__class__.__name__ == self._obj.__name__
        
        return objs
    
    def _addMongoDocument(self, document):
        try:
            document['_id'] = self._collection.insert_one(document, safe=True)
            return document
        except Exception as e:
            logs.warning("Unable to add document: %s" % e)
            raise
    
    def _addMongoDocuments(self, documents):
        try:
            ids = self._collection.insert(documents)
            assert len(ids) == len(documents)
            
            for i in xrange(len(ids)):
                documents[i]['_id'] = ids[i]
            
            return documents
        except Exception as e:
            logs.warning("Unable to add document: %s" % e)
            raise
    
    def _getMongoDocumentFromId(self, documentId):
        document = self._collection.find_one(documentId)
        if document == None:
            logs.warning("Unable to find document (id = %s)" % documentId)
            raise Exception("Document not found")
        return document
    
    def _updateMongoDocument(self, document):
        document['_id'] = self._collection.save(document, safe=True)
        return document
    
    def _removeMongoDocument(self, documentId):
        # Confused here. Supposed to return None on success, so I guess it's 
        # working, but should probably test more.
        if self._collection.remove({'_id': documentId}):
            return False
        else:
            return True
    
    def _getMongoDocumentsFromIds(self, documentIds, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        sort        = kwargs.pop('sort', None)
        limit       = kwargs.pop('limit', 0)

        params = {'_id': {'$in': documentIds}}
        
        if since != None and before != None:
            params['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since != None:
            params['timestamp.created'] = {'$gte': since}
        elif before != None:
            params['timestamp.created'] = {'$lte': before}
        
        if sort != None:
            documents = self._collection.find(params).sort(sort, \
                pymongo.DESCENDING).limit(limit)
        else:
            documents = self._collection.find(params).limit(limit)
        
        return documents
    
    
    ### RELATIONSHIP MANAGEMENT
    
    def _getOverflowBucket(self, objId):
        overflow = self._collection.find_one({'_id': objId}, \
                                                fields={'overflow': 1})
        
        if overflow == None or 'overflow' not in overflow:
            return objId            
        else:
            # Do something to manage overflow conditions?
            # Grabs the most recent bucket to use and appends that to the id. 
            # This is our new key!
            return '%s%s' % (objId, overflow['overflow'][-1])
    
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
    
    def _getRelationships(self, keyId, limit=None):
        doc = self._collection.find_one({'_id': keyId})
        
        if doc == None:
            return []
        else:
            ids = doc['ref_ids']
            if limit != None and len(ids) > limit:
                return ids[:limit]
            if 'overflow' in doc:
                # Check other buckets
                buckets = []
                for bucket in doc['overflow']:
                    buckets.append('%s%s' % (keyId, bucket))
                    
                for moreDocs in self._collection.find({'_id': {'$in': buckets}}):
                    ids = ids + moreDocs['ref_ids']
                    if limit != None and len(ids) > limit:
                        return ids[:limit]
            return ids
    
    def _getRelationshipsAcrossKeys(self, keyIds, limit=4):
        if not isinstance(keyIds, list) or not isinstance(limit, int):
            raise Fail("Warning: Invalid input")
        if limit > 20:
            limit = 20
            
        limit = limit * -1
        ids = []
        documents = self._collection.find({'_id': {'$in': keyIds}})
        for document in documents:
            if 'overflow' in document:
                # Pull in overflow document
                document = self._collection.find({'_id': document['overflow'][-1]})
            ids += document['ref_ids'][limit:]
        
        return ids

