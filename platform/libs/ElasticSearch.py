#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import pyes, sys, time

from abc    import ABCMeta, abstractmethod
from pprint import pformat

class AElasticSearchError   (Exception):           pass
class InvalidMappingError   (AElasticSearchError): pass
class InvalidIndexError     (AElasticSearchError): pass

def deep_comparison(v0, v1):
    if isinstance(v0, (set, frozenset)):
        if not isinstance(v1, (set, frozenset)):
            return False
        if len(frozenset(v0.keys()) - frozenset(v1.keys())) > 0:
            return False
        
        return all(deep_comparison(v0[k], v1[k]) for k in v0)
    elif isinstance(v0, (list, tuple)):
        if not isinstance(v1, (list, tuple)):
            return False
        
        return all(deep_comparison(v0[i], v1[i]) for i in xrange(len(v0)))
    else:
        return v0 == v1

def coerce_iter(v):
    if isinstance(v, basestring):
        return [ v ]
    elif isinstance(v, (list, tuple)):
        return v
    else:
        try:
            iter(v)
            return v
        except TypeError:
            return [ v ]

class ElasticSearch(object):
    
    def __init__(self, config_file, force=False, **kwargs):
        self._config_file = config_file
        self._config = { }
        self._cache  = { }
        self._force  = force
        
        self._init_config()
        self._init_client(**kwargs)
        
        self._sync_config()
    
    @property
    def indices(self):
        try:
            return self._cache['indices']
        except KeyError:
            indices = self._client.get_indices()
            self._cache['indices'] = indices
            return indices
    
    @property
    def mappings(self):
        try:
            return self._cache['mappings']
        except KeyError:
            try:
                mappings = self._client.get_mapping()
            except pyes.exceptions.NotFoundException:
                mappings = { }
            
            self._cache['mappings'] = mappings
            return mappings
    
    @property
    def client(self):
        return self._client
    
    def _init_config(self):
        self._config = self._parse_config_file(self._config_file)
        
        indices  = self._config.get('ES_INDICES',  [])
        mappings = self._config.get('ES_MAPPINGS', [])
        
        for index in indices:
            self._validate_index(index)
        
        for mapping in mappings:
            self._validate_mapping(mapping)
    
    def _sync_config(self):
        indices  = self._config.get('ES_INDICES',  [])
        mappings = self._config.get('ES_MAPPINGS', [])
        
        utils.log()
        utils.log("-" * 80)
        utils.log("[%s] SYNCING CONFIG:" % self)
        utils.log()
        utils.log("Desired indices:  %s" % pformat(indices))
        utils.log("Actual indices:   %s" % pformat(self.indices))
        utils.log()
        utils.log("Desired mappings: %s" % pformat(mappings))
        utils.log("Actual mappings:  %s" % pformat(self.mappings))
        utils.log("-" * 80)
        utils.log()
        
        # sync indices
        # ------------
        missing  = []
        remove   = []
        
        # find all extraneous indices
        for index in self.indices:
            found = False
            
            for index2 in indices:
                if index == index2['name']:
                    found = True
                    break
            
            if not found:
                remove.append(index)
        
        # find all missing indices
        for index in indices:
            name  = index['name']
            found = False
            
            for index2 in self.indices:
                if name == index2:
                    found = True
                    break
            
            if not found:
                missing.append(index)
        
        # remove all extraneous indices
        for index in remove:
            if not self._force:
                utils.log("[%s] remove invalid index '%s'?" % (self, index))
                response = utils.get_input()
                
                if response == 'n': # no
                    continue
                elif response == 'a': # abort
                    sys.exit(1)
            
            self._delete_index(index)
        
        # add all missing indices
        for index in missing:
            name = index['name']
            
            if not self._force:
                utils.log("[%s] add new index '%s'?" % (self, name))
                response = utils.get_input()
                
                if response == 'n': # no
                    continue
                elif response == 'a': # abort
                    sys.exit(1)
            
            self._create_index(name, index.get('settings', None))
        
        # sync mappings
        # -------------
        missing   = []
        remove    = []
        blacklist = frozenset(['boost', 'index'])
        
        def _prune(d):
            if isinstance(d, dict):
                return dict((k, _prune(v)) for k, v in d.iteritems() if k not in blacklist)
            else:
                return d
        
        # find all extraneous mappings
        for index, types in self.mappings.iteritems():
            for doc_type, properties in types.iteritems():
                prefix = 'remove invalid'
                found = False
                
                for mapping2 in mappings:
                    if index in mapping2['indices'] and doc_type == mapping2['type']:
                        if deep_comparison(_prune(mapping2['mapping']), _prune(properties)):
                            found = True
                            break
                        else:
                            prefix = 'remove stale'
                
                if not found:
                    remove.append((index, doc_type, prefix))
        
        # find all missing mappings
        for mapping2 in mappings:
            properties2 = _prune(mapping2['mapping'])
            type2 = mapping2['type']
            
            for index2 in mapping2['indices']:
                prefix = 'add new'
                found  = False
                
                for index, types in self.mappings.iteritems():
                    if index == index2:
                        for doc_type, properties in types.iteritems():
                            if doc_type == mapping2['type']:
                                if deep_comparison(properties2, _prune(properties)):
                                    found = True
                                    break
                                else:
                                    prefix = 'update'
                    
                    if found:
                        break
                
                if not found:
                    missing.append((mapping2, prefix))
        
        # remove all extraneous mappings
        for index, doc_type, prefix in remove:
            if not self._force:
                utils.log("[%s] %s mapping '%s:%s'?" % (self, prefix, index, doc_type))
                response = utils.get_input()
                
                if response == 'n': # no
                    continue
                elif response == 'a': # abort
                    sys.exit(1)
            
            self._delete_mapping(index, doc_type)
        
        # add all missing mappings
        for mapping, prefix in missing:
            doc_type = mapping['type']
            
            for index in mapping['indices']:
                if not self._force:
                    utils.log("[%s] %s mapping '%s:%s'?" % (self, prefix, index, doc_type))
                    response = utils.get_input()
                    
                    if response == 'n': # no
                        continue
                    elif response == 'a': # abort
                        sys.exit(1)
                
                properties = mapping['mapping']
                self._put_mapping(doc_type, properties, [ index ])
        
        self.update()
    
    def _parse_config_file(self, config_file):
        with open(config_file, 'r') as f:
            return self._parse_config(f.read())
    
    def _parse_config(self, config):
        conf = {}
        exec compile(config, '', "exec") in conf
        
        try:
            del conf['__builtins__']
        except KeyError:
            pass
        
        # ignore any global config variables which don't begin with ES_
        return dict(i for i in conf.iteritems() if i[0].startswith('ES_'))
    
    def update(self):
        self._cache = {}
    
    def _init_client(self, **kwargs):
        retries = 5
        
        while True:
            try:
                self._client = pyes.ES(**kwargs)
                self._client.collect_info()
                utils.log("[%s] pyes: %s" % (self, pformat(self._client.info)))
                self.update()
                break
            except Exception:
                retries -= 1
                if retries <= 0:
                    raise
                
                utils.printException()
                time.sleep(1)
    
    def _create_index(self, index, settings=None):
        """
            Registers the given index with the underlying elasticsearch instance.
        """
        
        try:
            utils.log("[%s] create_index(%s)" % (self, index))
            self._client.create_index(index=index, settings=settings)
            self.update()
        except pyes.exceptions.IndexAlreadyExistsException, e:
            pass
    
    def _put_mapping(self, doc_type, mapping, indices):
        """ 
            Registers the given mapping with the underlying elasticsearch instance.
        """
        
        indices = coerce_iter(indices)
        
        utils.log("[%s] put_mapping(type=%s, indices=%s, %s)" % 
                  (self, doc_type, indices, pformat(mapping)))
        self._client.put_mapping(doc_type, mapping, indices)
        self.update()
    
    def _delete_index(self, index):
        """ 
            Removes a single index from the underlying elasticsearch instance.
        """
        
        utils.log("[%s] delete_index(index=%s)" % (self, index))
        self._client.delete_index(index)
        self.update()
    
    def _delete_mapping(self, index, doc_type):
        """ 
            Removes a single mapping from the underlying elasticsearch instance.
        """
        
        utils.log("[%s] delete_mapping(index=%s, type=%s)" % (self, index, doc_type))
        self._client.delete_mapping(index, doc_type)
        self.update()
    
    def _get_mapping(self, index, doc_type):
        try:
            return self.mappings[index][doc_type]
        except KeyError:
            pass
        
        return None
    
    def add(self, documents, indices, doc_type, **kwargs):
        """
            Indexes all of the given documents with elasticsearch.
        """
        
        documents = coerce_iter(documents)
        indices   = coerce_iter(indices)
        
        count     = kwargs.pop('count', None)
        max_batch = kwargs.pop('max_batch', 512)
        inserts   = 0
        cur_batch = 0
        
        try:
            bulk  = (count and count > 1) or (len(documents) > 1)
        except Exception:
            bulk  = True
        
        try:
            kwargs['bulk'] = kwargs.get('bulk', bulk)
            
            for index in indices:
                mapping = self._get_mapping(index, doc_type)
                
                if mapping is None:
                    utils.log("INVALID_MAPPING_ERROR: (index=%s, type=%s)" % (index, doc_type))
                    
                    raise InvalidMappingError("no mapping defined for (index=%s, type=%s)" % 
                                              (index, doc_type))
                
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
                
                for doc in documents:
                    id = str(doc.pop('_id', None))
                    kwargs['id'] = id
                    
                    # validate this document against the predefined mapping
                    _validate_doc(doc, mapping)
                    
                    # index this document with elasticsearch
                    self._client.index(doc, index, doc_type, **kwargs)
                    
                    inserts   += 1
                    cur_batch += 1
                    
                    # flush bulk batch once it gets too big
                    if bulk and cur_batch >= max_batch:
                        utils.log("[%s] flushing bulk indexing job of %d documents (%s:%s) (%d total)" % 
                                  (self, cur_batch, index, doc_type, inserts))
                        self._client.flush_bulk(True)
                        cur_batch = 0
            
            # flush bulk batch
            if bulk and cur_batch >= 0:
                utils.log("[%s] flushing bulk indexing job of %d documents (%s:%s) (%d total)" % 
                          (self, cur_batch, index, doc_type, inserts))
                self._client.flush_bulk(True)
                cur_batch = 0
            else:
                utils.log("[%s] finished bulk indexing job of %d documents (%s:%s)" % 
                          (self, inserts, index, doc_type))
        except:
            utils.printException()
            raise
    
    def remove(self, indices, doc_type, ids):
        """
            Removes a single document from its underlying elasticsearch index.
        """
        
        indices = coerce_iter(indices)
        ids     = coerce_iter(ids)
        bulk    = True
        
        for index in indices:
            for id in ids:
                self._client.delete(index, doc_type, id, bulk=bulk)
        
        if bulk:
            self._client.flush_bulk()
    
    @staticmethod
    def _validate_mapping(doc):
        """
            Validates the correctness of a mapping document.
        """
        
        ElasticSearch._validate_dict(doc, InvalidMappingError, {
            'type'          : {
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
        
        ElasticSearch._validate_dict(doc, InvalidIndexError, {
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
                    msg = "type error; attribute '%s' expected type '%s', found type '%s' in %s" % \
                          (key, _type, type(doc[key]), pformat(doc))
                    raise error(msg)
            elif required:
                raise error("missing required attribute '%s' in %s" % (key, pformat(doc)))
        
        # optionally check for overflow
        if not allow_overflow:
            for key in doc:
                if key != '_id' and key not in schema:
                    raise error("unknown key found '%s' in %s" % (key, pformat(doc)))
    
    def __str__(self):
        return self.__class__.__name__

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
    server = "%s:%s" % (args.es_host, args.es_port)
    es     = ElasticSearch('test_es.py', force=args.force, server=server)

