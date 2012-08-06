#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from abc            import ABCMeta, abstractmethod
from libs.ElasticSearch  import ElasticSearch
from libs.MongoMonitor   import *

# TODO: utilize mappings to convert / strip newly added documents
# TODO: enforce required mappings and type checking of newly added documents

# TODO: fix oplog state caching to work with config mappings / indices
# TODO: how does modifying an existing mapping or index work?

class AElasticMongo(BasicMongoMonitor):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, es, ns, state_ns='local.mongomonitor', **kwargs):
        BasicMongoMonitor.__init__(self, ns=ns, state_ns=state_ns, **kwargs)
        assert isinstance(es, ElasticSearch)
        
        self._es = es
    
    def add(self, ns, documents, count = None, noop = False):
        BasicMongoMonitor.add(self, ns, documents, count, noop)
        indices, doc_type = self._get_indices_and_type(ns)
        
        # lazily convert each document, filtering out docs which convert to None
        documents = (obj for obj in (self._convert(ns, doc) for doc in documents) if obj is not None)
        
        # add each document to elasticsearch
        self._es.add(documents, indices, doc_type, count=count)
    
    def remove(self, ns, id):
        BasicMongoMonitor.add(self, ns, id)
        indices, doc_type = self._get_indices_and_type(ns)
        
        self._es.remove(indices, doc_type, id)
    
    @abstractmethod
    def _get_indices_and_type(self, ns):
        pass
    
    @abstractmethod
    def _convert(self, ns, document):
        pass

class BasicElasticMongo(AElasticMongo):
    
    def __init__(self, *args, **kwargs):
        AElasticMongo.__init__(self, *args, **kwargs)
    
    @abstractmethod
    def _get_indices_and_type(self, ns):
        return ('plays', 'line')
    
    @abstractmethod
    def _convert(self, ns, document):
        return document

