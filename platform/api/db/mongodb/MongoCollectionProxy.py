#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math, os, pymongo, time, utils, logs

from pymongo.errors import AutoReconnect
from errors         import *
from datetime       import datetime

DEBUG = False

class MongoCollectionProxy(object):
    def __init__(self, parent, connection, database, collection, cap_size=None):
        global DEBUG
        try:
            self._parent     = parent
            self._connection = connection
            self._database   = self._connection[database]
            self._collection = self._database[collection]
            self._debug      = DEBUG
            # if cap_size is specified and the collection does not exist, create it and set a cap
            collection_names = self._database.collection_names()
            if cap_size is not None and collection not in collection_names:
                self._database.create_collection(collection, size=cap_size, capped=True)

        except:
            logs.warning("Error: unable to set collection")
            raise

    def options(self):
        return self._collection.options()
    
    def find(self, spec=None, output=None, limit=None, **kwargs):
        if self._debug:
            print("Mongo 'find' - spec: %s output: %s limit: %s kwargs: %s" % (spec, output, limit, kwargs))
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.find(spec, **kwargs)
                
                if limit is not None:
                    ret = ret.limit(limit)
                
                if output is not None:
                    if output == list:
                        ret = list(ret)
                
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                
                logs.info("Retrying find (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
    
    def command(self, cmd, **kwargs):
        if self._debug:
            print("Mongo 'command' - cmd %s" % cmd)

        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._database.command(cmd, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                
                logs.info("Retrying command (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
    
    def count(self):
        if self._debug:
            print("Mongo 'count'")

        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.count()
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                
                logs.info("Retrying count (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
    
    def find_one(self, spec_or_id=None, **kwargs):
        if self._debug:
            print("Mongo 'find_one' - spec_or_id: %s kwargs: %s" % (spec_or_id, kwargs))

        if spec_or_id is not None and not isinstance(spec_or_id, dict):
            spec_or_id = { "_id": spec_or_id }
        
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.find_one(spec_or_id, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                
                logs.info("Retrying find_one (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
    
    def insert(self, docs, manipulate=True, safe=False, check_keys=True, **kwargs):
        if self._debug:
            print("Mongo 'insert' - manipulate: %s safe: %s check_keys: %s kwargs: %s" %
                       (manipulate, safe, check_keys, kwargs))

        max_batch_size = 64
        max_retries = 7

        storeLog = kwargs.pop('log', True)
        
        def _insert(objects, level):
            num_retries = 0
            count = len(objects)
            ret = []
            
            if count <= 0:
                return
            
            if count > max_batch_size:
                num = int(math.ceil(float(count) / float(max_batch_size)))
                for i in xrange(num):
                    offset = i * max_batch_size
                    sub_objects = objects[offset : offset + max_batch_size]
                    ret += _insert(sub_objects, level)
                return ret
            else:
                while True:
                    try:
                        result = self._collection.insert(objects, manipulate, safe, check_keys, **kwargs)
                        if count == 1:
                            if storeLog:
                                logs.debug("Inserted document (%s) id=%s" % (self._parent.__class__.__name__, result))
                        else:
                            if storeLog:
                                logs.debug("Inserted %d documents (%s)" % (count, self._parent.__class__.__name__))
                        return result
                    except AutoReconnect as e:
                        num_retries += 1
                        if storeLog:
                            logs.warning("Insert document failed (%s) -- %d of %d" % \
                                (self._parent.__class__.__name__, num_retries, max_retries))

                        if num_retries > max_retries:
                            if storeLog:
                                logs.warning("Unable to connect after %d retries (%s)" % \
                                    (max_retries, self._parent.__class__.__name__))
                            raise
                        
                        time.sleep(0.25)
        
        return _insert(docs, 0)
    
    def insert_one(self, doc, safe=False, **kwargs):
        if self._debug:
            print("Mongo 'insert_one' - safe: %s kwargs: %s" % (safe, kwargs))

        try:
            return self.insert([doc], safe=safe, **kwargs)[0]
        except:
            raise
        
    def save(self, to_save, manipulate=True, safe=False, **kwargs):
        if self._debug:
            print("Mongo 'save' - manipulate: %s safe: %s kwargs: %s" % (manipulate, safe, kwargs))

        num_retries = 0
        max_retries = 5

        storeLog = kwargs.pop('log', True)
        
        while True:
            try:
                ret = self._collection.save(to_save, manipulate, safe, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    if storeLog:
                        logs.warning(msg)
                    raise
                if storeLog:
                    logs.info("Retrying delete (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
            except Exception as e:
                import traceback
                logs.warning('Failure updating document:\n%s' % ''.join(traceback.format_exc()))
                raise StampedSaveDocumentError("Unable to update document")


    def update(self, spec, document, upsert=False, manipulate=False,
               safe=False, multi=False, **kwargs):
        if self._debug:
            print("Mongo 'update'")

        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.update(spec, document, upsert, manipulate, safe, multi, **kwargs)
                logs.debug("Updated document (%s)" % (self._parent.__class__.__name__))
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                logs.info("Retrying update (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
            except Exception as e:
                raise StampedUpdateDocumentError("Unable to update document: %s" % e)


    def remove(self, spec_or_id=None, safe=False, **kwargs):
        if self._debug:
            print("Mongo 'remove'")

        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.remove(spec_or_id, safe, **kwargs)
                logs.debug("Removed document (%s) id=%s" % (self._parent.__class__.__name__, spec_or_id))
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                logs.info("Retrying remove (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
            except Exception as e:
                raise StampedRemoveDocumentError("Unable to remove document")
    
    def ensure_index(self, key_or_list, **kwargs):
        if self._debug:
            print("Mongo 'ensure_index'")

        num_retries = 0
        max_retries = 5
        
        # NOTE (travis): this method should never throw an error locally if connected to 
        # a non-master DB node that can't ensure_index because the conn doesn't have 
        # write permissions
        
        while True:
            try:
                ret = self._collection.ensure_index(key_or_list, **kwargs)
                return ret
            except AutoReconnect as e:
                if not utils.is_ec2():
                    return
                
                num_retries += 1
                
                if num_retries > max_retries:
                    msg = "Unable to ensure_index after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    
                    raise
                
                logs.info("Retrying ensure_index (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)
    
    def inline_map_reduce(self, m, r, full_response=False, **kwargs):
        if self._debug:
            print("Mongo 'inline_map_reduce'")

        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.inline_map_reduce(m, r, full_response=False, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect after %d retries (%s)" % \
                        (max_retries, self._parent.__class__.__name__)
                    logs.warning(msg)
                    raise
                logs.info("Retrying inline_map_reduce (%s)" % (self._parent.__class__.__name__))
                time.sleep(0.25)

    
    def __str__(self):
        return self.__class__.__name__

