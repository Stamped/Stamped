#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import math

from tests.StampedTestUtils   import *
from libs.MongoMonitor  import *
from pymongo.errors     import AutoReconnect

class MongoTestMonitor(BasicMongoMonitor):
    
    def __init__(self, *args, **kwargs):
        BasicMongoMonitor.__init__(self, *args, **kwargs)
        
        self.documents = defaultdict(dict)
    
    def add(self, ns, documents, count = None, noop = False):
        BasicMongoMonitor.add(self, ns, documents, count, noop)
        assert ns in self.ns
        
        total = 0
        for document in documents:
            #utils.log("add: %s" % self._extract_id(document))
            self.documents[self._extract_id(document)] = document
            total += 1
        
        if count is not None:
            assert total == count
    
    def remove(self, ns, id):
        BasicMongoMonitor.remove(self, ns, id)
        id = self._extract_id(id)
        
        #utils.log("remove: %s" % id)
        assert ns in self.ns
        assert id in self.documents
        
        del self.documents[id]

def export_documents(coll, documents, drop = False, batch_size = 64):
    """
        Exports documents to mongo in batches.
    """
    
    num_docs    = len(documents)
    num_batches = int(math.ceil(num_docs / float(batch_size)))
    
    # drop the collection before beginning insertion
    if drop:
        coll.drop()
    
    utils.log("exporting %d documents... (%d batches of %d documents)" % 
              (num_docs, num_batches, batch_size))
    
    for i in xrange(num_batches):
        offset  = i * batch_size
        batch   = documents[offset : offset + batch_size]
        
        safe_insert(coll, batch)

def safe_insert(coll, documents, retries = 5, delay = 0.25):
    """
        Retry wrapper around a single mongo bulk insertion.
    """
    
    while True:
        try:
            return coll.insert(documents, safe=True)
        except AutoReconnect as e:
            retries -= 1
            
            if retries <= 0:
                raise
            
            time.sleep(delay)
            delay *= 2

class MongoMonitorTests(AStampedTestCase):
    
    def test_basic(self):
        test_ns = 'test.lines'
        
        # perform initial import
        monitor1 = MongoTestMonitor(ns = test_ns, force=True)
        monitor1.start()
        monitor1.join(timeout=5)
        
        # ensure that the correct number of docs were imported
        total1 = len(monitor1.documents)
        test_coll = monitor1._get_collection(monitor1.conn, test_ns)
        count1 = test_coll.count()
        
        self.assertEqual(total1, count1)
        utils.log("Docs imported: %d vs %d" % (total1, count1))
        
        # perform noop incremental import
        monitor2 = MongoTestMonitor(ns = test_ns)
        monitor2.start()
        monitor2.join(timeout=5)
        
        # ensure that no new docs were imported
        total2 = len(monitor2.documents)
        self.assertEqual(total2, 0)
        
        items = list(test_coll.find(limit = 10))
        num_items1 = len(items)
        
        for item in items:
            del item['_id']
        
        # insert some new documents and pause for the monitors to sync
        export_documents(test_coll, items)
        
        monitor1.join(timeout=5)
        monitor2.join(timeout=5)
        
        # ensure newly inserted documents reached the monitor
        self.assertEqual(len(monitor1.documents), test_coll.count())
        self.assertEqual(len(monitor1.documents), count1 + num_items1)
        self.assertEqual(len(monitor2.documents), num_items1)
        
        items = list(test_coll.find().limit(5).skip(80))
        items = map(lambda i: i['_id'], items)
        num_items2 = len(items)
        
        for item in items:
            test_coll.remove({'_id' : item}, safe=True)
        
        monitor1.join(timeout=5)
        monitor2.join(timeout=5)
        
        self.assertEqual(len(monitor1.documents), test_coll.count())
        self.assertEqual(len(monitor1.documents), count1 + num_items1 - num_items2)
        self.assertEqual(len(monitor2.documents), num_items1 - num_items2)

if __name__ == '__main__':
    StampedTestRunner().run()

