#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
from HTTPSchemas import *
from Schemas import *
from pprint import pprint
from iTunesSource import iTunesSource
from StampedSource import StampedSource

stampedAPI = MongoStampedAPI()

q = 'auction house'
# q = 'little owl'
q = '21 jump street'
# q = 'stamped'
# q = 'boyfriend'
# q = 'avec'
q = 'kanye west'
q = 'katy perry'
coords = CoordinatesSchema({'lat': 37.781697, 'lng':-122.392146})   # SF
coords = CoordinatesSchema({'lat': 40.742273, 'lng':-74.007549})   # NYC
# coords = None

e = stampedAPI.getEntity({'entity_id': '4eb3001b41ad855d53000ac8'})

print '\n\nBEGIN\n%s\n' % ('='*40)
# pprint(e.value)

# if len(e.tracks) > 0:
#     for track in e.tracks:
#         print track

source    = iTunesSource()
stamped   = StampedSource(stamped_api = stampedAPI)


t = e.tracks[7]
# t.itunes_id = '420843675'
print t
# stampedAPI._enrichEntity(t)
# print t
#print stampedAPI._enrichEntity(e)

source_id = t['itunes_id']

# attempt to resolve against the Stamped DB
# entity_id = stamped.resolve_fast(source, source_id)
entity_id = None

if entity_id is None:
    wrapper = source.wrapperFromKey(source_id)
    results = stamped.resolve(wrapper)

    print 'RESULTS: %s' % results

    if len(results) > 0 and results[0][0]['resolved']:
        # source key was found in the Stamped DB
        entity_id = results[0][1].key
        print 'FOUND IN STAMPED DB: %s' % entity_id
        
        # enrich entity asynchronously
        # tasks.invoke(tasks.APITasks._enrichEntity, args=[entity.entity_id])
    else:
        entity = source.buildEntityFromWrapper(wrapper)
        print '\n\n\nBUILT ENTITY\n%s' % entity
        # stampedAPI._enrichEntity(entity)
        # entity = self._entityDB.addEntity(entity)
        # entity_id = entity.entity_id
        
        # enrich and merge entity asynchronously
        stampedAPI._mergeEntity(entity, True)

        print '\n\n\nENRICHED ENTITY\n%s' % entity
else:
    print 'FAST RESOLVE: %s' % entity_id


# results = stampedAPI.searchEntities(q, coords=coords, category=None)

# for i in range(len(results)):
#     # pprint(results[i][0].value)
#     entity = HTTPEntityAutosuggest().importSchema(results[i][0], results[i][1]).exportSparse()

#     print '%2s. %s' % (i+1, entity['search_id'])
#     print '    title:     %s' % entity['title']
#     print '    subtitle:  %s' % entity['subtitle']
#     print '    category:  %s' % entity['category']
#     if 'distance' in entity:
#         print '    distance:  %s' % entity['distance']

#     # print '%2s. %s %10s %s' % (i+1, results[i].entity_id, results[i].subcategory, results[i].title)

#     # pprint(entity)
#     print 

# if len(results) > 0:
#     pprint(results[0][0].value)
# else:
#     print'\n\nNO RESULTS\n\n'