#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import pyes, pymongo, re, time

from abc            import ABCMeta, abstractmethod
from pprint         import pprint, pformat
from gevent         import Greenlet
from collections    import defaultdict
from pymongo.errors import AutoReconnect
from MongoMonitor   import *

class AElasticMongoError    (Exception):          pass
class InvalidMappingError   (AElasticMongoError): pass
class InvalidIndexError     (AElasticMongoError): pass

# TODO: utilize mappings to convert / strip newly added documents
# TODO: enforce required mappings and type checking of newly added documents

# TODO: fix oplog state caching to work with config mappings / indices
# TODO: how does modifying an existing mapping or index work?

class ElasticMongo(AMongoMonitorObject):
    
    def __init__(self, **kwargs):
        utils.log("pyes: %s" % str(kwargs))
        retries = 5
        
        while True:
            try:
                self._elasticsearch = pyes.ES(**kwargs)
                info = self._elasticsearch.collect_info()
                utils.log("[%s] pyes: %s" % (self, pformat(info)))
                break
            except Exception:
                retries -= 1
                if retries <= 0:
                    raise
                
                utils.printException()
                time.sleep(1)
    
    def add_indices(self, indices, noop = False):
        """
            Registers each of the given indices with the underlying elasticsearch instance.
        """
        
        for index in indices:
            self._validate_index(index)
            
            name     = index['name']
            settings = index.get('settings', None)
            
            # TODO: special-case if index already exists (pyes.exceptions.IndexAlreadyExistsException)
            try:
                if not noop:
                    utils.log("[%s] add_index(%s)" % (self, name))
                    self._elasticsearch.create_index(index=name, settings=settings)
            except pyes.exceptions.IndexAlreadyExistsException, e:
                # TODO!
                raise
    
    def add_mappings(self, mappings, noop = False):
        """ 
            Registers each of the given mappings with the underlying elasticsearch instance.
        """
        
        for doc in mappings:
            self._validate_mapping(doc)
            
            doc_type = doc['type']
            ns       = doc['ns']
            indices  = doc.get('indices', None)
            mapping  = doc['mapping']
            
            if isinstance(indices, basestring):
                indices = [ indices ]
            
            if not noop:
                utils.log("[%s] add_mapping(type=%s, indices=%s, %s)" % 
                          (self, doc_type, indices, pformat(mapping)))
                self._elasticsearch.put_mapping(doc_type, mapping, indices)
    
    def remove_index(self, id):
        """ 
            Removes a single index from the underlying elasticsearch instance.
        """
        
        try:
            index = self._indices[id]
        except KeyError:
            raise InvalidIndexError(id)
        
        self._elasticsearch.delete_index(index)
        del self._indices[id]
        
        # TODO: should we clear the state cache of affected sources here?
    
    def remove_mapping(self, id):
        """ 
            Removes a single mapping from the underlying elasticsearch instance and stops any 
            outstanding mongo listeners from needlessly continuing to poll changes if no more 
            mappings exist.
        """
        
        try:
            indices, doc_type, ns = self._mappings[id]
        except KeyError:
            raise InvalidMappingError(id)
        
        if ns not in self._sources:
            raise InvalidMappingError(id)
        
        wrapper = self._sources[ns]
        del wrapper['mappings'][id]
        
        if len(wrapper['mappings']) == 0:
            source = wrapper['source']
            source.stop()
            del self._sources[ns]
        
        if indices:
            for index in indices:
                self._elasticsearch.delete_mapping(index, doc_type)
        else:
            self._elasticsearch.delete_mapping(None, doc_type)
        
        del self._mappings[id]
    
    def add(self, ns, documents, count = None, noop = False):
        """
            Indexes all documents in the given namespace with elasticsearch.
        """
        
        try:
            wrapper = self._sources[ns]
        except KeyError:
            utils.log(self._sources)
            raise InvalidMappingError(ns)
        
        if not noop:
            mappings = wrapper['mappings']
            bulk     = count and count > 1
            inserts  = 0
            
            for mapping_id, mapping in mappings.iteritems():
                indices    = mapping[0]
                doc_type   = mapping[1]
                mapping_ns = mapping[2]
                properties = mapping[3]
                
                if ns == mapping_ns:
                    for index in indices:
                        for doc in documents:
                            id = str(doc.pop('_id'))
                            
                            #utils.log("[%s] index(ns=%s, index=%s, type=%s, %s)" % 
                            #          (self, ns, index, doc_type, pformat(doc)))
                            
                            def _validate_doc(d, schema):
                                for k, v in schema.iteritems():
                                    try:
                                        dv = d[k]
                                        
                                        if isinstance(dv, dict):
                                            _validate_doc(dv, v)
                                    except KeyError:
                                        try:
                                            null_value = v['null_value']
                                            d[k] = null_value
                                        except KeyError:
                                            pass
                            
                            # validate doc against mapping properties
                            _validate_doc(doc, properties)
                            
                            self._elasticsearch.index(doc, index, doc_type, id=id, bulk=bulk)
                            inserts += 1
            
            if bulk:
                utils.log("[%s] flushing bulk indexing job of %d '%s' documents" % 
                          (self, inserts, doc_type))
                self._elasticsearch.flush_bulk()
    
    def remove(self, ns, id):
        """
            Removes a single document in the given namespace from any underlying 
            elasticsearch indices.
        """
        
        try:
            wrapper = self._sources[ns]
        except KeyError:
            raise InvalidMappingError(ns)
        
        todo = []
        
        for mapping in wrapper['mappings']:
            doc_type = mapping[1]
            
            for index in mapping[0]:
                todo.append([ index, doc_type, id ])
        
        bulk = len(todo) > 2
        
        for item in todo:
            self._elasticsearch.delete(*item, bulk=bulk)
        
        if bulk:
            self._elasticsearch.flush_bulk()
    
    @staticmethod
    def _validate_mapping(doc):
        """
            Validates the correctness of a mapping document.
        """
        
        ElasticMongo._validate_dict(doc, InvalidMappingError, {
            'type'          : {
                'required'  : True, 
                'type'      : basestring, 
            }, 
            'ns'            : {
                'required'  : True, 
                'type'      : basestring, 
            }, 
            'indices'       : {
                'required'  : False, 
                'type'      : (list, tuple, basestring), 
            }, 
            'mapping'       : {
                'required'  : True, 
                'type'      : dict, 
            }, 
        })
    
    @staticmethod
    def _validate_index(doc):
        """
            Validates the correctness of an indexed document.
        """
        
        ElasticMongo._validate_dict(doc, InvalidIndexError, {
            'name'          : {
                'required'  : True, 
                'type'      : basestring, 
            }, 
            'settings'      : {
                'required'  : False, 
                'type'      : dict, 
            }, 
        })
    
    @staticmethod
    def _validate_dict(doc, error, schema, allow_overflow=False):
        """
            Performs simple existence and type-checking of the source dict against 
            a reference schema dict.
        """
        
        if not isinstance(doc, dict):
            raise error(doc)
        
        for key, value in schema.iteritems():
            required = value.get('required', False)
            _type    = value.get('type', None)
            
            if key in doc:
                if _type is not None and not isinstance(doc[key], _type):
                    raise error(doc)
            elif required:
                raise error(doc)
        
        # optionally check for overflow
        if not allow_overflow:
            for key in doc:
                if key != '_id' and key not in schema:
                    raise error(doc)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-n', '--ns', type=str, default="local.elasticmongo",
                        help=("db and collection namespace of elasticmongo config "
                              "(with two subcollections, indices and mappings)"))
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="force a fresh sync from scratch")
    parser.add_argument('-e', '--es_host', type=str, default="localhost",
                        help=("hostname or IP address of elasticsearch server"))
    parser.add_argument('-P', '--es_port', type=int, default=9200,
                        help=("port number of elasticsearch server"))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args   = parser.parse_args()
    server = '%s:%s' % (args.es_host, args.es_port)
    em     = ElasticMongo(mongo_host        = args.mongo_host, 
                          mongo_port        = args.mongo_port, 
                          mongo_config_ns   = args.ns, 
                          poll_interval_ms  = args.poll_interval, 
                          force             = args.force, 
                          server            = server)
    
    em.run()

