#!/usr/bin/env python
from __future__ import absolute_import

import Globals
import pymongo, json, codecs, os, sys, bson, utils

from api.MongoStampedAPI    import MongoStampedAPI


def main():

    stampedAPI  = MongoStampedAPI()
    activityDB  = stampedAPI._activityDB

    items = activityDB._collection.find({'link.linked_entity_id': {'$exists': True}, 'link.linked_entity': {'$exists': True}})

    for item in items:
        print item['_id']
        activityDB._collection.update({'_id': item['_id']}, {'$unset': {'link.linked_entity_id': True, 'link.linked_entity': True}})


if __name__ == '__main__':  
    main()

