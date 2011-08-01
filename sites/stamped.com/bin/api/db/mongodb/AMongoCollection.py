#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import bson, copy, os, pymongo, time, utils

from errors import Fail
from utils import AttributeDict, getPythonConfigFile, Singleton
from datetime import datetime
from pymongo.errors import AutoReconnect

class MongoDBConfig(Singleton):
    def __init__(self):
        self.config = AttributeDict()
    
    @property
    def isValid(self):
        return 'mongodb' in self.config and \
               'host' in self.config.mongodb and \
               'port' in self.config.mongodb
    
    def init(self):
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
            utils.log("[Mongo] Warning: invalid configuration file; defaulting to localhost:30000")
            self.config = AttributeDict({
                "mongodb" : {
                    "host" : "localhost", 
                    "port" : 30000, 
                }
            })

class AMongoCollection():
    DB = 'stamped_test'
    
    def __init__(self, collection):
        self._initConfig()
        
        self._user = self._getenv_user()
        self._host = self._getenv_host()
        self._desc = self.__class__.__name__
        self._port = self._getenv_port()
        self._db = self.DB
        
        try:
            self._connection = self._connect()
            self._database   = self._getDatabase()
            self._collection = self._getCollection(collection)
        except:
            utils.log("Error: unable to connect to Mongo")
            raise
    
    def _initConfig(self):
        cfg = MongoDBConfig.getInstance()
        if not cfg.isValid:
            cfg.init()
        assert cfg.isValid
        
        self._config = cfg.config
        
        utils.log("%s) %s:%d" % (self.__class__.__name__, 
                                 self._config.mongodb.host, 
                                 self._config.mongodb.port))
    
    def _getenv_host(self):
        return str(self._config.mongodb.host)
    
    def _getenv_port(self):
        return int(self._config.mongodb.port)
    
    def _getenv_user(self):
        if 'user' in self._config.mongodb:
            return str(self._config.mongodb.user)
        else:
            return 'root'
    
    def _connect(self):
        while True:
            try:
                utils.log("%s) connecting to %s:%d" % (self, self._host, self._port))
                return pymongo.Connection(self._host, self._port, slave_okay=True)
            except AutoReconnect:
                time.sleep(2)
    
    def _getDatabase(self):
        return self._connection[self._db]
    
    def _getCollection(self, collection):
        return self._database[collection]
    
    def _endRequest(self):
        self._connection.end_request()
    
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
        return bson.objectid.ObjectId(string)
    
    def _mongoToObj(self, data, objId='id'):
#         print '_mongoToObj: ', data
        data[objId] = self._getStringFromObjectId(data['_id'])
        del(data['_id'])
        return data
    
    def _objToMongo(self, obj, objId='id'):
        if obj is None:
            return None
        
        if obj.isValid == False:
            # print obj
            raise KeyError("Object not valid")
        
        data = copy.copy(obj.getDataAsDict())
        
        if '_id' in data:
            if isinstance(data['_id'], basestring):
                data['_id'] = self._getObjectIdFromString(data['_id'])
        
        if objId in data:
            data['_id'] = self._getObjectIdFromString(data[objId])
            del(data[objId])
        
        return self._mapDataToSchema(data, self.SCHEMA)
    
    def _objsToMongo(self, objs, objId='id'):
        return map(self._objToMongo, objs, objId)
    
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
    
    def _addDocument(self, document, objId='id'):
        return self._getStringFromObjectId(self._collection.insert(self._objToMongo(document, objId), safe=True))
    
    def _addDocuments(self, documents, objId='id'):
        return self._collection.insert(self._objsToMongo(documents, objId))
    
    def _getDocumentFromId(self, documentId, objId='id'):
        #print 'documentId: ', documentId
        document = self._mongoToObj(self._collection.find_one(self._getObjectIdFromString(documentId)), objId)
        return document
    
    def _getDocumentsFromIds(self, documentIds, objId='id', since=None, before=None, sort=None, limit=20):
        ids = []
        for documentId in documentIds:
            ids.append(self._getObjectIdFromString(documentId))
        params = {'_id': {'$in': ids}}
        if since != None and isinstance(since, datetime) and before != None and isinstance(before, datetime):
            params['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since != None and isinstance(since, datetime):
            params['timestamp.created'] = {'$gte': since}
        elif before != None and isinstance(before, datetime):
            params['timestamp.created'] = {'$lte': before}
        
        if sort != None:
            documents = self._collection.find(params).sort(sort, pymongo.DESCENDING).limit(limit)
        else:
            documents = self._collection.find(params).limit(limit)
            
        result = []
        for document in documents:
            result.append(self._mongoToObj(document, objId))
        return result
    
    def _updateDocument(self, document, objId='id'):
        return self._getStringFromObjectId(self._collection.save(self._objToMongo(document, objId), safe=True))
    
    def _removeDocument(self, keyId):
        # Confused here. Supposed to return None on success, so I guess it's working,
        # but should probably test more.
        if self._collection.remove({'_id': self._getObjectIdFromString(keyId)}):
            return False
        else:
            return True
    
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

