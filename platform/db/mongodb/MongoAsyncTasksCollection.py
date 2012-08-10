#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, ast, pymongo
import libs.ec2_utils

from bson.objectid import ObjectId
from db.mongodb.AMongoCollection import AMongoCollection
from datetime import datetime

class MongoAsyncTasksCollection(AMongoCollection):
    
    def __init__(self, stack_name=None):
        # Change collection name to stack if on EC2
        collection = 'asynctasks'
        if stack_name is not None:
            collection = "asynctasks_%s" % stack_name
        elif libs.ec2_utils.is_ec2():
            stack_info = libs.ec2_utils.get_stack()
            collection = "asynctasks_%s" % stack_info.instance.stack

        AMongoCollection.__init__(self, collection=collection, logger=True)

    ### PUBLIC
    
    def addTask(self, task):
        document = {}

        if 'taskId' in task:
            document['_id'] = ObjectId(task['taskId'])

        if 'taskGenerated' in task:
            document['generated'] = task['taskGenerated']
        else:
            document['generated'] = datetime.utcnow()

        if 'fn' in task:
            document['fn'] = unicode(task['fn'])

        if 'args' in task:
            document['args'] = unicode(task['args'])

        if 'kwargs' in task:
            document['kwargs'] = unicode(task['kwargs'])

        return self._collection.insert_one(document, log=False, safe=False)

    def removeTask(self, taskId):
        documentId = ObjectId(str(taskId))
        return self._removeMongoDocument(documentId)

