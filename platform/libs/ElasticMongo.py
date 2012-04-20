#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from abc            import ABCMeta, abstractmethod
from ElasticSearch  import ElasticSearch
from MongoMonitor   import *

# TODO: utilize mappings to convert / strip newly added documents
# TODO: enforce required mappings and type checking of newly added documents

# TODO: fix oplog state caching to work with config mappings / indices
# TODO: how does modifying an existing mapping or index work?

class ElasticMongo(BasicMongoMonitor):
    
    def __init__(self, es, ns, state_ns='local.mongomonitor', **kwargs):
        BasicMongoMonitor.__init__(self, ns=ns, state_ns=state_ns, **kwargs)
        assert isinstance(es, ElasticSearch)
        
        self._es = es
    
    def add(self, ns, documents, count = None, noop = False):
        BasicMongoMonitor.add(self, ns, documents, count, noop)
        indices, doc_type = self._get_indices_and_type(ns)
        
        documents = (self._convert(ns, doc) for doc in documents)
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

class BasicElasticMongo(ElasticMongo):
    
    def __init__(self, *args, **kwargs):
        ElasticMongo.__init__(self, *args, **kwargs)
    
    @abstractmethod
    def _get_indices_and_type(self, ns):
        return ('plays', 'line')
    
    @abstractmethod
    def _convert(self, ns, document):
        return document


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

