#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import math, os, pymongo, time, utils

from errors import Fail
from datetime import datetime
from pymongo.errors import AutoReconnect

class MongoCollectionProxy(object):
    def __init__(self, parent, connection, database, collection):
        try:
            self._parent     = parent
            self._connection = connection
            self._database   = self._connection[database]
            self._collection = self._database[collection]
        except:
            utils.log("Error: unable to set collection")
            raise
    
    def find(self, spec=None, **kwargs):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.find(spec, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "%s) unable to connect after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                
                utils.log("[%s] retrying query" % (self, ))
                time.sleep(1)
    
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
                    msg = "%s) unable to connect after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                
                utils.log("[%s] retrying command" % (self, ))
                time.sleep(1)
    
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
                    msg = "%s) unable to connect after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                
                utils.log("[%s] retrying count" % (self, ))
                time.sleep(1)
    
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
                    msg = "[%s] unable to connect to host after %d retries (%s)" % (self._parent, max_retries, str(e))
                    utils.log(msg)
                    raise
                
                utils.log("[%s] retrying query" % (self, ))
                time.sleep(1)
    
    def insert(self, docs, manipulate=True, safe=False, check_keys=True, **kwargs):
        max_batch_size = 64
        max_retries = 7
        
        def _insert(objects, level):
            ret = []
            count = len(objects)
            
            if count <= 0:
                return
            
            if count > max_batch_size:
                num = int(math.ceil(float(count) / float(max_batch_size)))
                for i in xrange(num):
                    offset = i * max_batch_size
                    sub_objects = objects[offset : offset + max_batch_size]
                    ret += _insert(sub_objects, level)
            else:
                try:
                    result = self._collection.insert(objects, manipulate, safe, check_keys, **kwargs)
                    utils.log("[%s] successfully inserted %d documents" % (self._parent, count))
                    ret += result
                except AutoReconnect as e:
                    if level > max_retries or count <= 1:
                        utils.log("[%s] unable to connect after %d retries (%s)" % \
                            (self, max_retries, str(e)))
                        raise
                    
                    utils.log("[%s] inserting %d documents failed... trying smaller batch" % (self._parent, count))
                    
                    time.sleep(0.05)
                    mid = count / 2
                    ret += _insert(objects[:mid], level + 1)
                    ret += _insert(objects[mid:], level + 1)
            
            return ret
        
        return _insert(docs, 0)
    
    def insert_one(self, doc, safe=False):
        return self.insert([doc], safe=safe)[0]
        
    def save(self, to_save, manipulate=True, safe=False, **kwargs):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.save(to_save, manipulate, safe, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "%s) unable to connect to host after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                utils.log("[%s] retrying delete" % (self._parent, ))
                time.sleep(1)
        
    def update(self, spec, document, upsert=False, manipulate=False,
               safe=False, multi=False, **kwargs):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.update(spec, document, upsert, manipulate, safe, multi, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "%s) unable to connect to host after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                utils.log("[%s] retrying delete" % (self._parent, ))
                time.sleep(1)
    
    def remove(self, spec_or_id=None, safe=False, **kwargs):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.remove(spec_or_id, safe, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "%s) unable to connect to host after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                utils.log("%s) retrying delete" % (self._parent, ))
                time.sleep(1)
    
    def ensure_index(self, key_or_list, deprecated_unique=None,
                     ttl=300, **kwargs):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                ret = self._collection.ensure_index(key_or_list, deprecated_unique, ttl, **kwargs)
                return ret
            except AutoReconnect as e:
                num_retries += 1
                if num_retries > max_retries:
                    msg = "%s) unable to connect to host after %d retries (%s)" % \
                        (self, max_retries, str(e))
                    utils.log(msg)
                    raise
                utils.log("[%s] retrying delete" % (self._parent, ))
                time.sleep(1)
    
    def __str__(self):
        return self.__class__.__name__

