#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from tests.framework.FixtureTest import *
from tests.StampedTestUtils import *
import datetime
from libs.MongoCache import mongoCachedFn
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from api.MongoStampedAPI import globalMongoStampedAPI
from pprint import pprint

ARTIST = 'Carly Rae Jepsen'
ALBUMS = set(['Tug of War'])
TRACKS = {
        'Tug of War' : set(['Bucket', 'Tell Me', 'Heavy Lifting'])
        }

class MergeEntityTest(AStampedTestCase):
    @fixtureTest(generateLocalDbQueries=[('entities', {'title' : ARTIST})])
    def test_resolve_artist(self):
        mongoApi = globalMongoStampedAPI()
        collection = mongoApi._entityDB
        allItems = collection.getEntitiesByQuery(dict())
        for item in allItems:
            if item.isType('artist') and (item.albums or item.tracks):
                del item.albums
                del item.tracks
                mongoApi._mergeEntity(item)
                self.verifyAllLinks(item.entity_id, collection)
                break

    SONG_QUERY = ('entities', {
        '$and' : [{
            'title' : 'Call Me Maybe',
            'types' : 'track',
            'artists.title' : 'Carly Rae Jepsen'
        }]
    })
    @fixtureTest(generateLocalDbQueries=[SONG_QUERY])
    def test_resolve_song(self):
        mongoApi = globalMongoStampedAPI()
        collection = mongoApi._entityDB
        allItems = collection.getEntitiesByQuery(dict())
        merged = None
        for item in allItems:
            if item.isType('track') and item.title == 'Call Me Maybe':
                del item.albums
                del item.artists
                merged = mongoApi._mergeEntity(item)
                break
        else:
            raise Exception('could not find track')
        for artist in merged.artists:
            if artist.title == ARTIST:
                self.verifyAllLinks(artist.entity_id, collection)

    def verifyAllLinks(self, artistId, entityCollection):
        artist = entityCollection.getEntity(artistId)
        assert ALBUMS <= set(album.title for album in artist.albums)
        for albumMini in artist.albums:
            album = entityCollection.getEntity(albumMini.entity_id)
            assert any(albumArtist.entity_id == artist.entity_id for albumArtist in album.artists)
            assert TRACKS.get(album.title, set()) <= set(track.title for track in album.tracks)
        for trackMini in artist.tracks:
            track = entityCollection.getEntity(trackMini.entity_id)
            assert any(trackArtist.entity_id == artist.entity_id for trackArtist in track.artists)


if __name__ == '__main__':
    main()
