#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals

try:
    from api.MongoStampedAPI    import globalMongoStampedAPI
    import logs
    import random
    from abc                    import ABCMeta, abstractmethod, abstractproperty
    from pymongo                import json_util
    import json
    from pprint                 import pformat, pprint
    from gevent.pool            import Pool
    from schema import Schema
except:
    raise

def _api():
    return globalMongoStampedAPI()

def _entityDB():
    api = globalMongoStampedAPI()
    return api._entityDB

def _entityCollection():
    return _entityDB()._collection

def outputToCollection(entity_id, result_entities):
    """
    Outputs the given results to the local mongo entity collection.

    This function is intended to be used the 'output' argument of processBatch().
    It is also the default function used if no 'output' function is provided.
    """
    for entity in result_entities:
        _entityDB().updateEntity(entity)

def outputToCollectionAndEnrich(entity_id, result_entities):
    """
    Outputs the given results to the local mongo entity collection.

    This function is intended to be used the 'output' argument of processBatch().
    It is also the default function used if no 'output' function is provided.
    """
    for entity in result_entities:
        _entityDB().updateEntity(entity)
        _api().mergeEntity(entity)

def outputToConsole(entity_id, result_entities):
    """
    Outputs verbose logging of results to stdout.

    This function is intended to be used the 'output' argument of processBatch().
    The output is written in a single write() operation to ensure continuity even when
    being run in parallel.

    The output takes the following format:
    <entity_id based header>
    <original entity>
    <results_header>
    <result 0>
    ...
    <result n-1>
    """
    db = _entityDB()
    original_entity = db.getEntity(entity_id)
    accum = []
    accum.append("ORIGINAL:%s\n" % entity_id)
    accum.append('%s\n' % pformat(original_entity.dataExport()))
    accum.append('RESULTS %d:\n' % len(result_entities))
    for entity in result_entities:
        accum.append('%s\n' % pformat(entity.dataExport()))
    print(''.join(accum))

def _sparsePrint(schema, keys, keypath):
    if len(keys) == 0:
        if isinstance(schema, Schema):
            schema = schema.dataExport()
        print("%s: %s" % (keypath, pformat(schema)))
    else:
        key = keys[0]
        if key == '*':
            for value in schema:
                _sparsePrint(value, keys[1:], keypath)
        else:
            _sparsePrint(getattr(schema, key), keys[1:], keypath)

def createSparseOutputToConsole(keypaths):
    """
    """
    db = _entityDB()
    def sparseOutputToConsole(entity_id, result_entities):
        original_entity = db.getEntity(entity_id)
        print("\nORIGINAL:%s" % entity_id)
        for keypath in keypaths:
            keys = keypath.split('.')
            _sparsePrint(original_entity, keys, keypath)
        print('RESULTS %d' % len(result_entities))
        for entity in result_entities:
            if entity.entity_id != entity_id:
                print('entity_id: %s' % entity.entity_id)
            for keypath in keypaths:
                keys = keypath.split('.')
                _sparsePrint(entity, keys, keypath)
    return sparseOutputToConsole

def createOutputToFile(f):
    """
    Creates an output function that writes JSON to the given file.

    This function is intended to be used as the 'output' argument of processBatch().
    """
    db = _entityDB()
    def outputToFile(entity_id, result_entities):
        for entity in result_entities:
            bson = db._convertToMongo(entity)
            # converts bson to json using pymongo's built in support for handling datetime, ObjectID, etc.
            string = json.dumps(bson, default=json_util.default)
            # delimit objects with newlines to match mongoexport format
            f.write('%s\n' % string)
    return outputToFile

def processBatch(handler, query=None, output=None, offset=0, limit=None, thread_count=None, shuffle=False):
    """

    Applies the given handler to a batch of entities.

    handler - a function that takes a single entity as a parameter and returns a 
        list of updates in the form of entities. If a returned entity does not contain
        an entity_id, it will be assigned one. Otherwise, the entity will be treated
        as the updated version of the entity.

    query - The mongo query used to select the input entities. If no query is provided,
        all entities in the collection will be used.

    output - The output function for the result entities. If no function is provided, the entities
        will be written back to the underlying collection.

    offset - The integer offset into the entity results (defaults to 0).

    limit - The maximum number of entities to be processed (defaults to all query results).

    thread_count - The number of threads to use. If not provided, the implementation will attempt to
        choose an appropriate number, but it will guarantee that the tasks are not executed on the
        calling thread even if 1 thread is used. If set to 1 explicitly, the batch will be run 
        sequentially on the calling thread.

    """
    #if no output function is provided, write back to collection using outputToCollection()
    if output is None:
        output = outputToCollection
    kwargs = {} # additional find() parameters

    # if not shuffling, use built in limit/offset support in query
    if not shuffle:
        kwargs['skip'] = offset
        if limit is not None:
            kwargs['limit'] = limit
    
    # retrieve entity ids for query into a local list
    collection = _entityCollection()
    cursor = collection.find(query, fields=['_id'], **kwargs)
    matches = [ str(m['_id']) for m in cursor]

    # if shuffling, shuffle then apply limit and offset to shuffled matches
    if shuffle:
        random.shuffle(matches)
        if limit is None:
            limit = len(matches)
        matches = matches[offset:limit - offset]

    def handlerWrapper(entity_id):
        """
        Handles each entity_id by creating an entity from it, applying the handler,
        and outputting the results.
        """
        entity = _entityDB().getEntity(entity_id)
        results = handler(entity)
        output(entity_id, results)

    # run sequentially if thread_count explicitly set to 1
    if thread_count == 1:
        for match in matches:
            handlerWrapper(match)
    # otherwise, spawn tasks out in parallel
    else:
        # if thread_count not set, choose appropriate pool size
        if thread_count is None:
            thread_count = min(10, len(matches))
        pool = Pool(thread_count)
        for match in matches:
            pool.spawn(handlerWrapper, match)
        pool.join()





