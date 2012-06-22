#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api import Entity
from tests.framework.FixtureTest import *
import datetime
from libs.MongoCache import mongoCachedFn
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from MongoStampedAPI import globalMongoStampedAPI
from pprint import pprint

ARTIST = 'Carly Rae Jepsen'
ALBUMS = set(['Tug of War'])
TRACKS = {
        'Tug of War' : set(['Bucket', 'Tell Me', 'Heavy Lifting'])
        }

class MergeEntityTest(AStampedFixtureTestCase):
    @fixtureTest(generateLocalDbQueries=[('entities', {'title' : ARTIST})])
    def test_resolve_artist(self):
        mongoApi = globalMongoStampedAPI()
        collection = mongoApi._entityDB
        allItems = collection.getEntitiesByQuery(dict())
        for item in allItems:
            if item.isType('artist') and (item.albums or item.tracks):
                del item.albums
                del item.tracks
                item = collection.updateEntity(item)
                merged = mongoApi._mergeEntity(item, set())
                self.verifyAllLinks(merged, collection)
                break

    def verifyAllLinks(self, artist, entityCollection):
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
