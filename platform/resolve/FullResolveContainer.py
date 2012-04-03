#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FullResolveContainer' ]

import Globals
from logs import report

try:
    from BasicSourceContainer   import BasicSourceContainer

    from EntityGroups           import *

    from SeedSource             import SeedSource
    from FactualSource          import FactualSource
    from GooglePlacesSource     import GooglePlacesSource
    from SinglePlatformSource   import SinglePlatformSource
    from TMDBSource             import TMDBSource
    from FormatSource           import FormatSource
    from RdioSource             import RdioSource
    from SpotifySource          import SpotifySource
    from iTunesSource           import iTunesSource
    from AmazonSource           import AmazonSource
    from StampedSource          import StampedSource
    from pprint                 import pformat
except:
    report()
    raise

seedPriority = 100

class FullResolveContainer(BasicSourceContainer):
    """
    """

    def __init__(self):
        BasicSourceContainer.__init__(self)
        
        groups = [
            FactualGroup(),
            SinglePlatformGroup(),
            GooglePlacesGroup(),
            TMDBGroup(),
            RdioGroup(),
            SpotifyGroup(),
            iTunesGroup(),
            AmazonGroup(),
            FandangoGroup(),
            StampedTombstoneGroup(),

            AmazonLinkGroup(),
            AmazonUnderlyingGroup(),
            OpenTableGroup(),
            OpenTableNicknameGroup(),

            AddressGroup(),
            CoordinatesGroup(),
            PhoneGroup(),
            SiteGroup(),
            PriceRangeGroup(),
            CuisineGroup(),
            MenuGroup(),
            ReleaseDateGroup(),
            DirectorGroup(),
            CastGroup(),
            SubtitleGroup(),
            DescGroup(),
            MangledTitleGroup(),
            TrackLengthGroup(),
            ShortDescriptionGroup(),
            AlbumNameGroup(),
            #AlbumsGroup(),
            #SongsGroup(),
            # TracksGroup(),

            MPAARatingGroup(),
            ArtistDisplayNameGroup(),
            GenreGroup(),

            AuthorGroup(),
            PublisherGroup(),
            ISBNGroup(),
            SKUNumberGroup(),
            NumPagesGroup(),

            SubcategoryGroup(),
            ImagesGroup(),

            AlbumListGroup(),
            TrackListGroup(),
        ]
        for group in groups:
            self.addGroup(group)

        sources = [
            SeedSource(),
            FormatSource(),
            FactualSource(),
            GooglePlacesSource(),
            SinglePlatformSource(),
            AmazonSource(),
            TMDBSource(),
            RdioSource(),
            SpotifySource(),
            iTunesSource(),
            StampedSource(),
        ]
        for source in sources:
            self.addSource(source)
        self.setGlobalPriority('seed',seedPriority)
        self.setGlobalPriority('entity',-1)
        self.setGlobalPriority('itunes',1)

def demo(default_title='Katy Perry'):
    import sys
    import bson

    title = default_title.lower()
    subcategory = None
    index = 0

    print(sys.argv)
    if len(sys.argv) > 1:
        title = sys.argv[1]
    if len(sys.argv) > 2:
        subcategory = sys.argv[2]
    if len(sys.argv) > 3:
        index = int(sys.argv[3])

    _verbose = True
    from MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db = api._entityDB
    query = {'titlel':title}
    if subcategory is not None:
        query['subcategory'] = subcategory
    print("Query: %s" % query)
    cursor = db._collection.find(query)
    if cursor.count() == 0:
        print("Could not find a matching entity for %s" % title)
        return
    result = cursor[index]
    entity = db._convertFromMongo(result)
    print( "Before:\n%s" % pformat( entity.value ) )

    container = FullResolveContainer()

    decorations = {}
    container.enrichEntity( entity, decorations )

    print( "After:\n%s" % pformat( entity.value ) )
    if len(decorations) > 0:
        print( "With decorations:")
        for k,v in decorations.items():
            print( "%s decoration:" % k )
            try:
                print( "%s" % pformat(v.value) )
            except Exception:
                print( "%s" % pformat(v) )

if __name__ == "__main__":
    demo()
