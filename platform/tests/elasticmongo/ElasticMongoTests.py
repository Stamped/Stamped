#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import pyes, libs.corpus

from tests.StampedTestUtils   import *
from libs.ElasticMongo  import *

from pyes.query         import *
from pyes.filters       import *

_mongo_host = 'localhost'
_mongo_port = 27017

_pyes_host  = 'localhost'
_pyes_port  = 9200

class AElasticMongoTest(AStampedTestCase):
    
    def setUp(self):
        libs.corpus.export('-cd')
        
        self._pyes_conf = "%s:%d" % (_pyes_host, _pyes_port)
        self._pyes = pyes.ES([ self._pyes_conf ])
    
    def tearDown(self):
        pass

class ElasticMongoTests(AElasticMongoTest):
    
    def test_search(self):
        self._elasticmongo = ElasticMongo(_mongo_host, 
                                          _mongo_port, 
                                          force = True, 
                                          server = self._pyes_conf)
        
        q = StringQuery("wherefore art thou Romeo", 
                        default_operator="AND", 
                        search_fields=[ "lines.line", ])
        results = self._pyes.search(q, indices='plays')
        
        self.assertLength(results['hits']['hits'], 1)
        result  = results['hits']['hits'][0]
        
        self.assertEquals(result['_source']['lines'][0]['ref'], u'2.2.35')

if __name__ == '__main__':
    StampedTestRunner().run()

# need to handle stamp-specific info (e.g., blurbs) separately from entities

"""
indices  = [
    { 'name' : 'entities', }, 
    { 'name' : 'stamps', }, 
]

mappings = [
    {
        'ns'        : ns, 
        'type'      : 'line', 
        'indices'   : [ 'plays', ], 
        'mapping'   : {
            'title' : {
                'boost' : 1.0, 
                'index' : 'analyzed', 
                'store' : 'yes', 
                'type'  : 'string', 
                'term_vector' : 'with_position_offsets', 
            }, 
            'genre' : {
                'index' : 'analyzed', 
                'store' : 'yes', 
                'type'  : 'string', 
                'term_vector' : 'with_position_offsets', 
            }, 
            'speaker' : {
                'index' : 'analyzed', 
                'store' : 'yes', 
                'type'  : 'string', 
                'term_vector' : 'with_position_offsets', 
            }, 
            'lines' : {
                'properties' : {
                    'ref'   : {
                        'index' : 'analyzed', 
                        'store' : 'yes', 
                        'type'  : 'string', 
                    }, 
                    'line'  : {
                        'boost' : 2.0, 
                        'index' : 'analyzed', 
                        'store' : 'yes', 
                        'type'  : 'string', 
                        'term_vector' : 'with_position_offsets', 
                    }, 
                }, 
            }, 
        }, 
    }, 
]

"""

