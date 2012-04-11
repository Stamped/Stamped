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

# album = stampedAPI.getEntity({'search_id': 'T_ITUNES_474912044'})   # Childish Gambino - Camp (Album)
# stampedAPI.getEntity({'search_id': 'T_ITUNES_64387566'}) # Katy Perry (Artist)

# stampedAPI.getEntity({'search_id': 'T_ITUNES_474912080'}) # Song (That Power)
# stampedAPI.getEntity({'search_id': 'T_ITUNES_474912071'}) # Song (Hold You Down)

# entity = stampedAPI.getEntity({'search_id': 'T_GOOGLEPLACES_ClRJAAAAaU4WvIwYeYUN93Pt1uQ11sO4xaGHk3Ksi-vXxsPy10gC6LJMuSoEJF1-CJQX4O30cG37mZZnR6ZcYBpVyOcfqZTmxohcy5R0GekwQTmfBoISEHAtNR9kCBd-49e1jEBHCjYaFG3DsuqJ0U4TiedEPtQAzU1UWJve'}) # Place (Cascabel)

# entity = stampedAPI.getEntity({'entity_id': '4e4c691ddb6bbe2bcd000401'}) # Artist
# stampedAPI._enrichEntity(entity)

# stampedAPI._enrichEntityAsync('4e4c691ddb6bbe2bcd000401')

# print 'SKIP\n\n\n'

# stampedAPI._enrichEntityAsync('4f81e6a446ebe66a0d000000') # Artist (Katy Perry)
# stampedAPI._enrichEntityAsync('4f81e7e646ebe66a2a00000f') # Track (Peacock)
# stampedAPI._enrichEntityAsync('4f81e79246ebe66a27000000') # Album (Teenage Dream)

# e = stampedAPI._entityDB.getEntity('4f7a111ca265375be500002b')
# stampedAPI._enrichEntityAsync('4f7a111ca265375be500002b')

e = stampedAPI._entityDB.getEntity('4f7a111ca265375be500002b')
stampedAPI.mergeEntityAsync(e.value, True)

"""
album = stampedAPI._mergeEntity(album, True)

print '\n\nBEGIN\n%s\n' % ('='*40)
# pprint(e.value)

# if len(e.tracks) > 0:
#     for track in e.tracks:
#         print track

stamped   = StampedSource(stamped_api = stampedAPI)
sources = {
    'amazon':       AmazonSource,
    'factual':      FactualSource,
    'googleplaces': GooglePlacesSource,
    'itunes':       iTunesSource,
    'rdio':         RdioSource,
    'spotify':      SpotifySource,
    'tmdb':         TMDBSource,
}
track_list = []

for stub in album.tracks:
    source      = None
    source_id   = None
    entity_id   = None
    wrapper     = None

    # Enrich track
    if stub.entity_id is not None and not stub.entity_id.startswith('T_'):
        entity_id = stub.entity_id
    else:
        for sourceName in sources:
            try:
                if stub.sources['%s_id' % sourceName] is not None:
                    source = sources[sourceName]()
                    source_id = stub.sources['%s_id' % sourceName]

                    # Attempt to resolve against the Stamped DB (quick)
                    entity_id = stamped.resolve_fast(source, source_id)

                    if entity_id is None:
                        # Attempt to resolve against the Stamped DB (full)
                        wrapper = source.wrapperFromKey(source_id)
                        results = stamped.resolve(wrapper)
                        if len(results) > 0 and results[0][0]['resolved']:
                            entity_id = results[0][1].key
                    break
            except:
                pass

    if entity_id is not None:
        track = stampedAPI.getEntity({'entity_id': entity_id})
    elif source_id is not None and wrapper is not None:
        track = source.buildEntityFromWrapper(wrapper)
    else:
        print 'Unable to enrich track'
        track_list.append(stub)
        continue

    # Update track's album with album entity_id
    collectionUpdated = False
    for collection in track.albums:
        commonSources = set(album.sources.value.keys()).intersection(set(collection.sources.value.keys()))
        for commonSource in commonSources:
            if commonSource[-3:] == '_id' and album.sources[commonSource] == collection.sources[commonSource]:
                collection.entity_id = album.entity_id
                collectionUpdated = True
                break
        if collectionUpdated:
            break
    if not collectionUpdated:
        track.albums.append(album.minimize())

    track = stampedAPI._mergeEntity(track, True)

    # TODO: Enrich artist

    # Add track to album
    track_list.append(track.minimize())


print '\n\n\n%s\n%s\n\n\n' % ('='*40, '='*40)

e.tracks = track_list
e = stampedAPI._mergeEntity(e, True)
print e
"""

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