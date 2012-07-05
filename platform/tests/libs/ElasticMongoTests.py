#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import math, os

from tests.StampedTestUtils   import *
from libs.MongoMonitor  import *
from libs.ElasticMongo  import *
from pymongo.errors     import AutoReconnect

from pyes.query         import *
from pyes.filters       import *

class ElasticMonitorTests(AStampedTestCase):
    
    def test_basic(self):
        test_ns = 'test.lines'
        conf = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.es.conf')
        es = ElasticSearch(conf, force=True, server='localhost:9200')
        
        # perform initial import
        monitor1 = BasicElasticMongo(es = es, ns = test_ns, force=True)
        monitor1.start()
        monitor1.join(timeout=25)
        
        q = StringQuery("wherefore art thou Romeo", 
                        default_operator="AND", 
                        search_fields=[ "lines.line", ])
        results = es.client.search(q, indices='plays')
        
        utils.log("Results: %d" % len(results))
        result = results[0]
        utils.log(results._results['hits']['hits'][0])
        
        self.assertLength(results, 1)
        self.assertEqual(result.lines[0].ref, u'2.2.35')

if __name__ == '__main__':
    StampedTestRunner().run()

