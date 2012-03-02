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

class AElasticMongoError    (Exception):          pass
class InvalidMappingError   (AElasticMongoError): pass
class InvalidIndexError     (AElasticMongoError): pass

# TODO: utilize mappings to convert / strip newly added documents
# TODO: enforce required mappings and type checking of newly added documents

# TODO: fix oplog state caching to work with config mappings / indices
# TODO: how does modifying an existing mapping or index work?

class AElasticMongoObject(object):
    
    @staticmethod
    def _get_collection(db, ns):
        collection = db
        
        for component in ns.split('.'):
            collection = collection[component]
        
        return collection
    
    def __str__(self):
        return self.__class__.__name__

class AMongoCollectionSink(object):
    
    """
        Abstract base class for handling collection modifications.
    """
    
    __metaclass__ = ABCMeta
    
    def __init__(self, elasticmongo, queue_size = 16):
        self._elasticmongo = elasticmongo
    
    @abstractmethod
    def add(self, ns, documents, count = None, noop = False):
        pass
    
    @abstractmethod
    def remove(self, ns, id):
        pass

class ElasticMongo(AElasticMongoObject, AMongoCollectionSink):
    
    def __init__(self, 
                 mongo_host       = 'localhost', 
                 mongo_port       = 27017, 
                 mongo_conn       = None, 
                 mongo_config_ns  = "local.elasticmongo", 
                 poll_interval_ms = 1000, 
                 force            = False, 
                 **kwargs):
        
        AElasticMongoObject.__init__(self)
        AMongoCollectionSink.__init__(self, self)
        
        utils.log("[%s] %s %s" % (self, pformat(dict(
            mongo_host = mongo_host, 
            mongo_port = mongo_port, 
            mongo_conn = mongo_conn, 
            mongo_config_ns  = mongo_config_ns, 
            poll_interval_ms = poll_interval_ms, 
            force            = force)), pformat(kwargs)))
        
        self._mongo_host          = mongo_host
        self._mongo_port          = mongo_port
        self._mongo_config_ns     = mongo_config_ns
        self._mongo_conn          = mongo_conn
        self._poll_interval       = poll_interval_ms / 1000.0 # convert milliseconds to seconds
        self._force               = force
        
        self._init_mongo_conn()
        self._init_elastic_conn(**kwargs)
    
    def _init_mongo_conn(self):
        if self._mongo_conn:
            self._conn      = self._mongo_conn
        else:
            self._conn      = pymongo.Connection(self._mongo_host, self._mongo_port)
        
        self._oplog         = self._conn.local.oplog.rs
        self._config_sink   = ElasticMongoConfigSink(self)
        self._config_source = MongoCollectionSource(self, 
                                                    self._config_sink, 
                                                    self._mongo_config_ns, 
                                                    inclusive = True, 
                                                    force     = self._force, 
                                                    noop      = True)
        
                                  # let mapping := tuple(indices, type, ns, mapping)
        self._indices       = { } # _id => basestring
        self._mappings      = { } # _id => mapping
        self._sources       = { } # ns  => { 
                                  #    'source' : MongoCollectionSource, 
                                  #    'mappings' : { _id => mapping }, 
                                  # }
    
    def _init_elastic_conn(self, **kwargs):
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
    
    def run(self):
        self._config_source.start()
        self._config_source.join()
    
    def add_indices(self, documents, noop = False):
        """
            Registers indices for each of the given documents with the underlying 
            elasticsearch instance.
        """
        
        for doc in documents:
            self._validate_index(doc)
            
            index    = doc['name']
            settings = doc.get('settings', None)
            
            # TODO: special-case if index already exists (pyes.exceptions.IndexAlreadyExistsException)
            try:
                if not noop:
                    utils.log("[%s] add_index(%s)" % (self, index))
                    self._elasticsearch.create_index(index=index, settings=settings)
                
                self._indices[doc['_id']] = index
            except pyes.exceptions.IndexAlreadyExistsException, e:
                # TODO!
                pass
    
    def add_mappings(self, documents, noop = False):
        """ 
            Registers mappings for each of the given documents with the underlying 
            elasticsearch instance.
        """
        
        for doc in documents:
            self._validate_mapping(doc)
            
            doc_type = doc['type']
            ns       = doc['ns']
            doc_id   = doc['_id']
            indices  = doc.get('indices', None)
            mapping  = doc['mapping']
            
            if isinstance(indices, basestring):
                indices = [ indices ]
            
            if not noop:
                utils.log("[%s] add_mapping(type=%s, indices=%s, %s)" % 
                          (self, doc_type, indices, pformat(mapping)))
                self._elasticsearch.put_mapping(doc_type, mapping, indices)
            
            if indices is None:
                indices = []
            
            payload  = (indices, doc_type, ns, mapping)
            self._mappings[doc_id] = payload
            
            try:
                self._sources[ns]['mappings'][doc_id] = payload
            except KeyError:
                source = MongoCollectionSource(self, self, ns, force = self._force)
                
                self._sources[ns] = {
                    'mappings' : {
                        doc_id : payload, 
                    }, 
                    'source'   : source, 
                }
                
                # note: start source only after inserting source into self._sources
                source.start()
    
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
                            
                            if ns == 'stamped.users':
                                if not 'stats' in doc:
                                    doc['stats'] = {
                                        'num_stamps'    : 0, 
                                        'num_followers' : 0, 
                                    }
                                
                                assert 'num_stamps'     in doc['stats']
                                assert 'num_followers'  in doc['stats']
                            
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
        
        ElasticMongo._validate_dict(doc, False, InvalidMappingError, {
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
            Validates the correctness of an index document.
        """
        
        ElasticMongo._validate_dict(doc, False, InvalidIndexError, {
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
    def _validate_dict(doc, allow_overflow, error, schema):
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

class ElasticMongoConfigSink(AMongoCollectionSink):
    
    def __init__(self, elasticmongo):
        AMongoCollectionSink.__init__(self, elasticmongo)
    
    def add(self, ns, documents, count = None, noop = False):
        section = ns.split('.')[-1]
        
        if section == 'indices':
            self._elasticmongo.add_indices(documents,  noop = noop)
        elif section == 'mappings':
            self._elasticmongo.add_mappings(documents, noop = noop)
        elif section != 'state':
            # print warning
            pass
    
    def remove(self, ns, id):
        section = ns.split('.')[-1]
        
        if section == 'indices':
            self._elasticmongo.remove_index(id)
        elif section == 'mappings':
            self._elasticmongo.remove_mapping(id)
        elif section != 'state':
            # print warning
            pass

class MongoCollectionSource(Greenlet, AElasticMongoObject):
    
    """
        Monitors the given Mongo namespace, notifying an AMongoCollectionSink whenever 
        documents are added, modified, or removed.  Monitoring is done via a tailable 
        oplog cursor, and monitoring state is cached in a separate collection specific 
        to ElasticMongo, thereby enabling efficient incremental monitoring (e.g., if 
        ElasticMongo is killed for any reason, the most recent oplog timestamp will 
        implicitly be used upon restart to efficiently start monitoring from the 
        exact place ElasticMongo left off).
    """
    
    def __init__(self, 
                 elasticmongo, 
                 sink, 
                 ns, 
                 state_ns   = None, 
                 inclusive  = False, 
                 force      = False, 
                 noop       = False):
        
        assert isinstance(elasticmongo, ElasticMongo)
        assert isinstance(sink, AMongoCollectionSink)
        
        Greenlet.__init__(self)
        AElasticMongoObject.__init__(self)
        
        if state_ns is None:
            state_ns = "%s.state" % elasticmongo._mongo_config_ns
        
        self._ns                = ns
        self._sink              = sink
        self._elasticmongo      = elasticmongo
        self._collection        = self._get_collection(elasticmongo._conn, ns)
        self._state_collection  = self._get_collection(elasticmongo._conn, state_ns)
        self._inclusive         = inclusive
        self._force             = force
        self._noop              = noop
        self._stopped           = False
    
    def _run(self):
        state_query = { '_id': self._ns }
        
        if self._force:
            self._state_collection.remove(state_query)
        
        state  = self._state_collection.find_one(state_query)
        oplog  = self._elasticmongo._oplog
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
        
        # TODO: address async issue here..
        
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
            except Exception:
                pass
            
            time.sleep(self._elasticmongo._poll_interval)
    
    def stop(self):
        self._stopped = True
    
    def _initial_export(self, noop = False):
        colls = [ self._collection ]
        
        if self._inclusive:
            conn        = self._elasticmongo._conn
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
    
    @staticmethod
    def _extract_id(id):
        if isinstance(id, basestring) or isinstance(id, int):
            return id
        else:
            return repr(id)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-n', '--ns', type=str, default="local.elasticmongo",
                        help=("db and collection namespace of elasticmongo config "
                              "(with two subcollections, indices and mappings)"))
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="drop existing mongo state collections and force "
                             "a fresh sync from scratch")
    parser.add_argument('-m', '--mongo_host', type=str, default="localhost",
                        help=("hostname or IP address of mongod server"))
    parser.add_argument('-p', '--mongo_port', type=int, default=27017,
                        help="port number of mongod server")
    parser.add_argument('-e', '--es_host', type=str, default="localhost",
                        help=("hostname or IP address of elasticsearch server"))
    parser.add_argument('-P', '--es_port', type=int, default=9200,
                        help=("port number of elasticsearch server"))
    parser.add_argument('-i', '--poll_interval', type=int, default=1000,
                        help=("delay between successive mongo oplog polls (in milliseconds)"))
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

