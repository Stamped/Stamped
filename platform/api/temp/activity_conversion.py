#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
from api.db.mongodb.AMongoCollection import AMongoCollection
from HTTPSchemas import *
from api.Schemas import *
from datetime import datetime
from pprint import pprint
import Entity

api = MongoStampedAPI()
activityDB = AMongoCollection(collection='activity', primary_key='activity_id', overflow=True)

oldActivity = activityDB._collection.find()
for item in oldActivity:
    print '\n%s\n' % ('='*80)
    pprint(item)
    print
    
    activity = Activity()

    timestamp = BasicTimestamp()
    timestamp.created = item['timestamp']['created']
    activity.timestamp = timestamp

    genre = item.pop('genre', None)
    if genre == 'favorite':
        activity.verb = 'todo'
    elif genre == 'follower':
        activity.verb = 'follow'
    elif genre == 'comment':
        activity.verb = 'comment'
    elif genre == 'restamp':
        activity.verb = 'restamp'
    elif genre == 'like':
        activity.verb = 'like'
    elif genre == 'reply':
        activity.verb = 'reply'
    elif genre == 'mention':
        activity.verb = 'mention'
    else:
        print 'UNKNOWN GENRE: %s' % genre
        continue

    link        = item.pop('link', {})
    # userId      = link.pop('linked_user_id', None)
    stampId     = link.pop('linked_stamp_id', None)
    entityId    = link.pop('linked_entity_id', None)
    commentId   = link.pop('linked_comment_id', None)

    if 'user' in item and 'user_id' in item['user']:
        userId = item['user']['user_id']

    objectIds = ActivityObjectIds()
    objectIdsSet = False

    if userId is not None:
        activity.subjects = [ userId ]

    if stampId is not None:
        objectIds.stamp_ids = [ stampId ]
        objectIdsSet = True

    if commentId is not None:
        objectIds.comment_ids = [ commentId ]
        objectIdsSet = True

    if entityId is not None:
        objectIds.entity_ids = [ entityId ]
        objectIdsSet = True

    if objectIdsSet:
        activity.objects = objectIds

    print activity

