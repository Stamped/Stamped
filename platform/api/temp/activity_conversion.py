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
import pymongo

api = MongoStampedAPI()
activityDB = AMongoCollection(collection='activity', primary_key='activity_id', overflow=True)

query = {'recipient_id': '4e570489ccc2175fcd000000'}
oldActivity = activityDB._collection.find(query).sort('timestamp.created', pymongo.ASCENDING)

for item in oldActivity:
    print '\n%s\n' % ('='*80)
    pprint(item)
    print
    
    userId          = None
    objects         = {}
    benefit         = None
    source          = None      # Not being used
    body            = None

    sendAlert       = False
    unique          = False
    recipientIds    = []
    group           = False
    groupRange      = None

    mapGenreToVerb = {
        'favorite'      : 'todo',
        'follower'      : 'follow',
        'comment'       : 'comment',
        'restamp'       : 'restamp',
        'like'          : 'like',
        'reply'         : 'reply',
        'mention'       : 'mention',
    }

    genre = item['genre']
    if genre in mapGenreToVerb:
        verb = mapGenreToVerb[genre]
    else:
        print 'UNKNOWN GENRE: %s' % genre
        continue

    created         = item['timestamp']['created']

    link            = item.pop('link', {})
    stampId         = link.pop('linked_stamp_id', None)
    entityId        = link.pop('linked_entity_id', None)
    commentId       = link.pop('linked_comment_id', None)

    if 'user' in item and 'user_id' in item['user']:
        userId = item['user']['user_id']

    objects = {}

    if stampId is not None:
        objects['stamp_ids'] = [ stampId ]

    if commentId is not None:
        objects['comment_ids'] = [ commentId ]

    if entityId is not None:
        objects['entity_ids'] = [ entityId ]
        
    if 'benefit' in item and item['benefit'] is not None:
        benefit = 1

    if 'recipient_id' in item:
        recipientIds = [ item['recipient_id'] ]

    # Other settings
    if verb == 'follow':
        group               = True
        groupRange          = timedelta(days=1)
        unique              = True

    if verb == 'restamp':
        pass

    if verb == 'like':
        group               = True
        groupRange          = timedelta(days=1)

    if verb == 'todo':
        requireRecipient    = True
        group               = True
        groupRange          = timedelta(days=1)

    if verb == 'comment':
        pass 

    if verb == 'reply':
        requireRecipient    = True

    if verb == 'mention':
        requireRecipient    = True

    if verb == 'invite':
        requireRecipient    = True
        unique              = True

    if verb == 'friend':
        # body                = body
        requireRecipient    = True
        unique              = True



    api._activityDB.addActivity(verb           = verb,
                                subject        = userId,
                                objects        = objects,
                                body           = body,
                                recipientIds   = recipientIds,
                                benefit        = benefit,
                                group          = group,
                                groupRange     = groupRange,
                                sendAlert      = sendAlert,
                                unique         = unique,
                                created        = created)












