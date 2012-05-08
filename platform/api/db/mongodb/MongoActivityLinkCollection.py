#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import pymongo

from AMongoCollection import AMongoCollection
from Schemas import *
from datetime import datetime

class MongoActivityLinkCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activitylinks',
                                        primary_key='link_id', 
                                        obj=ActivityLink, 
                                        overflow=True)
    
    ### PUBLIC

    def addActivityLink(self, activityId, userId):
        item                = ActivityLink()
        item.activity_id    = activityId 
        item.user_id        = userId
        item.created        = datetime.utcnow()
        return self._addObject(item)

    def removeActivityLink(self, activityId):
        try:
            self._collection.remove(
                { 'activity_id' : activityId },
            )
            return True
        except Exception as e:
            logs.warning("Cannot remove document: %s" % e)
            raise Exception

    def removeActivityLinks(self, activityIds):
        try:
            self._collection.remove(
                { 'activity_id' : {'$in': activityIds }},
            )
            return True
        except Exception as e:
            logs.warning("Cannot remove documents: %s" % e)
            raise Exception

    def removeActivityLinkForUser(self, activityId, userId):
        try:
            self._collection.remove(
                { 'activity_id' : activityId },
                { 'user_id'     : userId }, 
            )
            return True
        except Exception as e:
            logs.warning("Cannot remove document: %s" % e)
            raise Exception

    def getActivityIdsForUser(self, userId, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        query = { 'user_id' : userId }
        if since is not None and before is not None:
            query['timestamp.created'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.created'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.created'] = { '$lte' : before }

        documents = self._collection.find(query).sort('timestamp.created', pymongo.DESCENDING).limit(limit)

        return [ document['activity_id'] for document in documents ]

    def countActivityIdsForUser(self, userId, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)

        query = { 'user_id' : userId }
        if since is not None and before is not None:
            query['timestamp.created'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.created'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.created'] = { '$lte' : before }

        return self._collection.find(query).count()
        
