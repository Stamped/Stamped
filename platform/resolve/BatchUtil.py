#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals

try:
    from api.MongoStampedAPI import globalMongoStampedAPI
    import logs
    import random
    from abc        import ABCMeta, abstractmethod, abstractproperty
except:
    raise

def outputToCollection(entity):
    api = globalMongoStampedAPI()
    db = api._entityDB
    collection = db._collection
    collection.updateEntity(entity)

def createOutputToFile(file):
    def outputToFile(entity):
        

def processBatch(handler, query=None, output=None, offset=0, limit=None, threads=None, shuffle=False):
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

    threads - The number of threads to use. If not provided, the implementation will attempt
        choose and appropriate number. If set to 1, the batch will be run sequentially in the
        calling thread.

    """
    kwargs = {}
    if not shuffle:
        kwargs['skip'] = offset
        if limit is not None:
            kwargs['limit'] = limit
    api = globalMongoStampedAPI()
    db = api._entityDB
    collection = db._collection
    matches = list(collection.find(query, fields=['_id'], **kwargs))
    if shuffle:
        random.shuffle(matches)
        if limit is None:
            limit = len(matches)
        matches = matches[offset:limit - offset]
    def handlerWrapper(entity):
        results = handler(entity)
        for result in results:


