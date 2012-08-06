from __future__ import absolute_import

import Globals
from pprint import pprint
from api import MongoStampedAPI
from resolve.EntityGroups import allGroups
from datetime import datetime

api = MongoStampedAPI.MongoStampedAPI()
entities = api._entityDB.getEntitiesByQuery({'sources.user_generated_id' : {'$exists' : False}, 'sources.tombstone_id' : {'$exists' : False}})
timeCutoff = datetime(2012, 7, 1)
groupObjs = [group() for group in allGroups]
for entity in entities:
    modified = False
    for g in groupObjs:
        if g.getSource(entity) == 'seed' and g.getTimestamp(entity) < timeCutoff:
            g.setSource(entity, None)
            modified = True
    if modified:
        api._entityDB.updateEntity(entity)
