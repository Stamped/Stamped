#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, pymongo, re, time

from abc            import ABCMeta, abstractmethod
from pprint         import pprint, pformat
from gevent         import Greenlet
from collections    import defaultdict
from pymongo.errors import AutoReconnect

class AMongoMonitorObject(object):
    
    @staticmethod
    def _get_collection(db, ns):
        collection = db
        
        for component in ns.split('.'):
            collection = collection[component]
        
        return collection
    
    @staticmethod
    def _extract_id(doc_or_id):
        if isinstance(doc_or_id, bson.objectid.ObjectId):
            return str(doc_or_id)
        elif isinstance(doc_or_id, basestring) or isinstance(doc_or_id, int):
            return doc_or_id
        elif isinstance(doc_or_id, dict):
            return AMongoMonitorObject._extract_id(doc_or_id['_id'])
        else:
            return repr(doc_or_id)
    
    def __str__(self):
        return self.__class__.__name__

class AMongoCollectionSink(AMongoMonitorObject):
    
    """
        Abstract base class for handling Mongo collection modifications.
    """
    
    __metaclass__ = ABCMeta
    
    def __init__(self, monitor):
        self._monitor = monitor
    
    @abstractmethod
    def add(self, ns, documents, count = None, noop = False):
        pass
    
    @abstractmethod
    def remove(self, ns, id):
        pass

class AMongoMonitor(Greenlet, AMongoCollectionSink):
    
    """
        Abstract base class for monitoring an instance of MongoDB.
    """
    
    __metaclass__ = ABCMeta
    
    def __init__(self, 
                 mongo_host       = 'localhost', 
                 mongo_port       = 27017, 
                 mongo_conn       = None, 
                 poll_interval_ms = 1000, 
                 force            = False, 
                 **kwargs):
        
        Greenlet.__init__(self)
        AMongoCollectionSink.__init__(self, self)
        
        self._mongo_host          = mongo_host
        self._mongo_port          = mongo_port
        self._mongo_conn          = mongo_conn
        self._poll_interval       = poll_interval_ms / 1000.0 # convert milliseconds to seconds
        self._force               = force
        
        self._init_mongo_conn()
    
    def _init_mongo_conn(self):
        if self._mongo_conn:
            self.conn = self._mongo_conn
        else:
            self.conn = pymongo.Connection(self._mongo_host, self._mongo_port)
        
        self.oplog    = self.conn.local.oplog.rs
    
    @abstractmethod
    def _run(self):
        pass
    
    @abstractmethod
    def add(self, ns, documents, count = None, noop = False):
        pass
    
    @abstractmethod
    def remove(self, ns, id):
        pass

class MongoCollectionMonitor(Greenlet, AMongoMonitorObject):
    
    """
        Monitors the given Mongo namespace, notifying an AMongoCollectionSink whenever 
        documents are added, modified, or removed.  Monitoring is done via a tailable 
        oplog cursor, and monitoring state is cached in a separate collection specific 
        to the db monitor, thereby enabling efficient incremental monitoring (e.g., if 
        the monitor is killed for any reason, the most recent oplog timestamp will 
        implicitly be used upon restart to efficiently start monitoring from the 
        exact place we left off).
    """
    
    def __init__(self, 
                 monitor, 
                 ns, 
                 state_ns, 
                 sink       = None, 
                 inclusive  = False, 
                 force      = False, 
                 noop       = False):
        
        Greenlet.__init__(self)
        AMongoMonitorObject.__init__(self)
        
        assert isinstance(monitor, AMongoMonitor)
        
        if sink is None:
            sink = monitor
        else:
            assert isinstance(sink, AMongoCollectionSink)
        
        self._ns                = ns
        self._sink              = sink
        self._monitor           = monitor
        self._collection        = self._get_collection(monitor.conn, ns)
        self._state_collection  = self._get_collection(monitor.conn, state_ns)
        self._inclusive         = inclusive
        self._force             = force
        self._noop              = noop
        self._stopped           = False
    
    def _run(self):
        state_query = { '_id': self._ns }
        
        if self._force:
            self._state_collection.remove(state_query)
        
        state  = self._state_collection.find_one(state_query)
        oplog  = self._monitor.oplog
        cursor = None
        spec   = {}
        
        #utils.log("force: %s, %s" % (self._force, pformat(state)))
        
        if state and 'ts' in state:
            first = oplog.find_one()
            
            if first['ts'].time > state['ts'].time and first['ts'].inc > state['ts'].inc:
                self._initial_export()
            elif self._noop:
                self._initial_export(noop = True)
            else:
                ts = state['ts']
                utils.log("[%s] fast-forwarding sync of collection %s to %s" % (self, self._ns, ts.as_datetime()))
                spec['ts'] = { '$gt': ts }
        else:
            self._initial_export()
        
        # TODO: address potential async issues here..
        
        if not 'ts' in spec:
            try:
                # attempt to start pulling at the last occurrence of the target namespace
                ns = self._ns
                
                if self._inclusive:
                    ns = re.compile('^%s.*')
                
                query = { "ns" : ns }
                last  = list(oplog.find(query).sort("$natural", -1).limit(1))[0]
                
                spec['ts'] = { '$gt': last['ts'] }
            except Exception:
                # fallback to starting at the end of the oplog
                try:
                    last = list(oplog.find().sort("$natural", -1).limit(1))[0]
                    spec['ts'] = { '$gt': last['ts'] }
                except Exception:
                    utils.printException()
                    # fallback to starting at the beginning of the oplog
                    pass
            
            try:
                state_query['ts'] = spec['ts']['$gt']
                self._state_collection.save(state_query)
            except KeyError:
                utils.printException()
                pass
        
        #utils.log("ns = %s; spec = %s" % (self._ns, spec))
        
        # poll the mongo oplog indefinitely
        while not self._stopped:
            try:
                if not cursor or not cursor.alive:
                    cursor = oplog.find(spec, tailable=True).sort("$natural", 1)
                
                docs = defaultdict(list)
                mod  = False
                
                for op in cursor:
                    ns = op['ns']
                    
                    if self._inclusive:
                        if not ns.startswith(self._ns):
                            continue
                    elif ns != self._ns:
                        continue
                    
                    # we're interested in this namespace
                    spec['ts'] = { '$gt': op['ts'] }
                    
                    if op['op'] == 'd':
                        id  = self._extract_id(op['o']['_id'])
                        mod = True
                        
                        self._sink.remove(ns, id)
                    elif op['op'] in ['i', 'u']:
                        docs[ns].append(op['o'])
                
                if len(docs) > 0:
                    mod = True
                    
                    for ns, documents in docs.iteritems():
                        self._sink.add(ns, documents, len(documents))
                
                if mod:
                    state_query['ts'] = spec['ts']['$gt']
                    self._state_collection.save(state_query)
            except AutoReconnect:
                time.sleep(0.5)
                pass
            
            time.sleep(self._monitor._poll_interval)
    
    def stop(self):
        self._stopped = True
    
    def _initial_export(self, noop = False):
        colls = [ self._collection ]
        
        if self._inclusive:
            conn        = self._monitor.conn
            namespaces  = conn.local.system.indexes.find(
                { 'key._id' : { '$exists' : True } }, 
                { 'ns' : 1, '_id' : 0 }
            )
            
            for doc in namespaces:
                ns = doc['ns']
                
                if ns.startswith(self._ns) and ns != self._ns:
                    colls.append(self._get_collection(conn, ns))
        
        for coll in colls:
            ns        = "%s.%s" % (coll.database.name, coll.name)
            state     = "%s.%s" % (self._ns, "state")
            
            if ns != state:
                documents = coll.find()
                count     = documents.count()
                
                if count > 0:
                    docs = "documents" if count != 1 else "document"
                    if not noop:
                        utils.log("[%s] performing initial sync of %s (%d %s)" % (self, ns, count, docs))
                    
                    self._sink.add(ns, documents, count, noop = noop)
                    
                    if not noop:
                        utils.log("[%s] finished initial sync of %s (%d %s)" % (self, ns, count, docs))
                elif not noop:
                    utils.log("[%s] skipping initial sync of empty collection %s" % (self, ns))

class BasicMongoMonitor(AMongoMonitor):
    
    """
        Basic, debugging implementation of AMongoMonitor, which monitors one or more 
        MongoDB namespaces and simply logs all modifications to them via utils.log.
    """
    
    def __init__(self, ns, state_ns='local.mongomonitor', **kwargs):
        AMongoMonitor.__init__(self, **kwargs)
        noop      = kwargs.get('noop', False)
        inclusive = kwargs.get('noop', False)
        force     = kwargs.get('force', False)
        
        if isinstance(ns, basestring):
            self.ns = frozenset([ ns ])
        else:
            self.ns = frozenset(ns)
        
        self._sources = []
        for ns in self.ns:
            self._sources.append(MongoCollectionMonitor(monitor   = self, 
                                                        ns        = ns, 
                                                        state_ns  = state_ns, 
                                                        inclusive = inclusive, 
                                                        force     = force, 
                                                        noop      = noop))
    
    def _run(self):
        for source in self._sources:
            source.start()
        
        for source in self._sources:
            source.join()
    
    def add(self, ns, documents, count = None, noop = False):
        utils.log("[%s] ADD: ns=%s, count=%d, noop=%s" % (self, ns, count, noop))
    
    def remove(self, ns, id):
        utils.log("[%s] REMOVE: ns=%s, id=%s" % (self, ns, id))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-n', '--ns', type=str, default="test",
                        help=("db and collection namespace to monitor)"))
    parser.add_argument('-s', '--state_ns', type=str, default="local.mongomonitor",
                        help=("db and collection namespace to store config"))
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="drop existing mongo state collections and force "
                             "a fresh sync from scratch")
    parser.add_argument('-m', '--mongo_host', type=str, default="localhost",
                        help=("hostname or IP address of mongod server"))
    parser.add_argument('-p', '--mongo_port', type=int, default=27017,
                        help="port number of mongod server")
    parser.add_argument('-i', '--poll_interval', type=int, default=1000,
                        help=("delay between successive mongo oplog polls (in milliseconds)"))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args   = parser.parse_args()
    mm     = BasicMongoMonitor(ns                = args.ns, 
                               state_ns          = args.state_ns, 
                               mongo_host        = args.mongo_host, 
                               mongo_port        = args.mongo_port, 
                               poll_interval_ms  = args.poll_interval, 
                               force             = args.force)
    
    mm.run()

