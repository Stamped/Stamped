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
import Entity

from resolve.EntitySource   import EntitySource
from resolve                import FullResolveContainer
from AmazonSource           import AmazonSource
from FactualSource          import FactualSource
from GooglePlacesSource     import GooglePlacesSource
from iTunesSource           import iTunesSource
from RdioSource             import RdioSource
from SpotifySource          import SpotifySource
from TMDBSource             import TMDBSource
from StampedSource          import StampedSource

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

# e = stampedAPI.getEntity({'entity_id': '4eb3001b41ad855d53000ac8'})
# e = stampedAPI.getEntity({'entity_id': '4e4c6e76db6bbe2bcd01ce85'})

e = stampedAPI.getEntity({'search_id': 'T_ITUNES_474912044'})

print '\n\nBEGIN\n%s\n' % ('='*40)
# pprint(e.value)

# if len(e.tracks) > 0:
#     for track in e.tracks:
#         print track

stamped   = StampedSource(stamped_api = stampedAPI)

track_list = []

for stub in e.tracks:
    # stub = e.tracks[7]
    print stub

    sources = {
        'amazon':       AmazonSource,
        'factual':      FactualSource,
        'googleplaces': GooglePlacesSource,
        'itunes':       iTunesSource,
        'rdio':         RdioSource,
        'spotify':      SpotifySource,
        'tmdb':         TMDBSource,
    }
    source      = None
    source_id   = None
    entity_id   = None
    wrapper     = None

    if stub.entity_id is not None and not stub.entity_id.startswith('T_'):
        entity_id = stub.entity_id
    else:
        for sourceName in sources:
            try:
                if stub.sources['%s_id' % sourceName] is not None:
                    source = sources[sourceName]()
                    source_id = stub.sources['%s_id' % sourceName]

                    # attempt to resolve against the Stamped DB
                    entity_id = stamped.resolve_fast(source, source_id)

                    if entity_id is None:
                        wrapper = source.wrapperFromKey(source_id)
                        results = stamped.resolve(wrapper)

                        if len(results) > 0 and results[0][0]['resolved']:
                            # source key was found in the Stamped DB
                            entity_id = results[0][1].key
                    break
            except:
                pass

    if entity_id is not None:
        entity = stampedAPI.getEntity({'entity_id': entity_id})

    elif source_id is not None and wrapper is not None:
        entity = source.buildEntityFromWrapper(wrapper)

    else:
        raise Exception

    entity = stampedAPI._mergeEntity(entity, True)

    newStub = Entity.buildEntity(kind=entity.kind)
    newStub.sources     = entity.sources
    newStub.artists     = entity.artists
    newStub.collections = entity.collections
    newStub.entity_id   = entity.entity_id
    newStub.title       = entity.title 
    newStub.kind        = entity.kind 
    newStub.types       = entity.types
    track_list.append(newStub)

print '\n\n\n%s\n%s\n\n\n' % ('='*40, '='*40)

for track in track_list:
    print track


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