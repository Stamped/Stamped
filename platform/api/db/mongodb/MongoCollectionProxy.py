#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math, os, pymongo, time, utils, logs

from pymongo.errors import AutoReconnect
from errors         import Fail
from datetime       import datetime

class MongoCollectionProxy(object):
    def __init__(self, parent, connection, database, collection):
        try:
            self._parent     = parent
            self._connection = connection
            self._database   = self._connection[database]
            self._collection = self._database[collection]
        except:
            logs.warning("Error: unable to set collection")
            raise
    
    def find(self, spec=None, output=None, limit=None, **kwargs):
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
    
    def command(self, cmd):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._database.command(cmd)
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
        try:
            return self.insert([doc], safe=safe, **kwargs)[0]
        except:
            raise
        
    def save(self, to_save, manipulate=True, safe=False, **kwargs):
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
        
    def update(self, spec, document, upsert=False, manipulate=False,
               safe=False, multi=False, **kwargs):
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
    
    def remove(self, spec_or_id=None, safe=False, **kwargs):
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
    
    def ensure_index(self, key_or_list, **kwargs):
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

