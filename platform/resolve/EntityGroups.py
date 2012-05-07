#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from BasicFieldGroup        import BasicFieldGroup
except:
    report()
    raise

class AKindTypeGroup(BasicFieldGroup):
    def __init__(self, *args, **kwargs):
        BasicFieldGroup.__init__(self, *args, **kwargs)
        self.__kinds = set( )
        self.__types = set( )
        
    def addKind(self, kind):
        self.__kinds.add(kind)

    def removeKind(self, kind):
        self.__kinds.remove(kind)
        
    def addType(self, t):
        self.__types.add(t)

    def removeType(self, t):
        self.__types.remove(t)

    def getKinds(self):
        return self.__kinds 

    def getTypes(self):
        return self.__types
    
    def eligible(self, entity):
        if len(self.__kinds) == 0 or entity.kind in self.__kinds:
            if len(self.__types) == 0 or len(self.__types.intersection(entity.types.value)) > 0:
                return True
        return False

class APlaceGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('place')

class APersonGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('person')

class AMediaCollectionGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')

class AMediaItemGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')

class ASoftwareGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('software')

class ARestaurantGroup(APlaceGroup):

    def __init__(self, *args, **kwargs):
        APlaceGroup.__init__(self, *args, **kwargs)
        eligible = set( [
            'restaurant',
            'bar', 
            'bakery',
            'cafe', 
            'market',
            'food',
            'night_club',
        ] )
        for v in eligible:
            self.addType(v)

class ABookGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')
        self.addType('book')

class AMovieGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')
        self.addType('movie')

class AFilmGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addType('movie')
        self.addType('tv')

class FactualGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'factual')
        self.addField(['factual_id'])

class FoursquareGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'foursquare')
        self.addField(['foursquare_id'])
        self.addField(['foursquare_url'])

class OpenTableGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'opentable')
        self.addField(['opentable_id'])
        self.addField(['opentable_url'])

class OpenTableNicknameGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'opentable_nickname')
        self.addNameField()

class SinglePlatformGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'singleplatform')
        self.addField(['singleplatform_id'])
        self.addField(['singleplatform_url'])

class GooglePlacesGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'googleplaces')
        self.addField(['googleplaces_id'])

class TMDBGroup(AMovieGroup):

    def __init__(self):
        AMovieGroup.__init__(self, 'tmdb')
        self.addField(['tmdb_id'])
        self.addField(['tmdb_url'])

class FandangoGroup(AMovieGroup):

    def __init__(self):
        AMovieGroup.__init__(self, 'fandango')
        self.addField(['fandango_id'])
        self.addField(['fandango_url'])

class NetflixGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'netflix')
        self.addKind('media_item')
        self.addKind('media_collection')
        self.addType('movie')
        self.addType('tv')

        self.addField(['netflix_id'])
        self.addField(['netflix_url'])
        self.addField(['netflix_is_instant_available'])
        self.addField(['netflix_instant_available_until'])

class RdioGroup(AKindTypeGroup):
    
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'rdio')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['rdio_id'])
        self.addField(['rdio_url'])

class TheTVDBGroup(AKindTypeGroup):
    
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'thetvdb')
        self.addKind('media_item')
        self.addType('album')
        self.addKind('media_collection')
        self.addType('tv')

        self.addField(['thetvdb_id'])
        self.addField(['imdb_id'])

class SpotifyGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'spotify')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['spotify_id'])
        self.addField(['spotify_url'])

class iTunesGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'itunes')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addType('tv')
        self.addKind('media_item')
        self.addType('track')
        self.addType('movie')
        self.addType('book')
        self.addKind('software')
        self.addType('app')

        self.addField(['itunes_id'])
        self.addField(['itunes_url'])

class AddressGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'address')
        fields = [
            ['address_street'],
            ['address_street_ext'],
            ['address_locality'],
            ['address_region'],
            ['address_postcode'],
            ['address_country'],
        ]
        for field in fields:
            self.addField(field)

class CoordinatesGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'coordinates')
        self.addNameField()

class PhoneGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'phone')
        self.addNameField()
    
class SiteGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'site')
        self.addNameField()

class PriceRangeGroup(ARestaurantGroup):

    def __init__(self):
        ARestaurantGroup.__init__(self, 'price_range')
        self.addNameField()

class CuisineGroup(ARestaurantGroup):

    def __init__(self):
        ARestaurantGroup.__init__(self, 'cuisine')
        self.addNameField()

class AlcoholFlagGroup(ARestaurantGroup):

    def __init__(self):
        ARestaurantGroup.__init__(self, 'alcohol_flag')
        self.addNameField()

class MenuGroup(ARestaurantGroup):

    def __init__(self):
        ARestaurantGroup.__init__(self, 'menu')
        self.addNameField()
        self.addDecoration(['menu'])

class ReleaseDateGroup(AKindTypeGroup):

    def __init__(self):
        AKindTypeGroup.__init__(self, 'release_date')
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addKind('software')
        self.addNameField()

class MPAARatingGroup(AKindTypeGroup):

    def __init__(self):
        AKindTypeGroup.__init__(self, 'mpaa_rating')
        self.addKind('media_collection')
        self.addType('tv')
        self.addKind('media_item')
        self.addType('movie')
        self.addNameField()

class GenresGroup(AKindTypeGroup):

    def __init__(self):
        AKindTypeGroup.__init__(self, 'genres')
        self.addKind('person')
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addKind('software')
        self.addNameField()

class ArtistsGroup(AKindTypeGroup):

    def __init__(self):
        AKindTypeGroup.__init__(self, 'artists')
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addNameField()

class LengthGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'length')
        self.addKind('media_item')
        self.addNameField()
        
class AlbumsGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'albums')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_item')
        self.addType('track')
        self.addNameField()

class TracksGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'tracks')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')

        self.addNameField()

class IMDBGroup(AFilmGroup):

    def __init__(self, *args, **kwargs):
        AFilmGroup.__init__(self, 'imdb')
        self.addField(['imdb_id'])

class AAmazonGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('book')
        self.addType('track')
        self.addKind('software')
        self.addType('video_game')

class AmazonGroup(AAmazonGroup):

    def __init__(self):
        AAmazonGroup.__init__(self, 'amazon')
        self.addField(['amazon_id'])
        self.addField(['amazon_url'])
        self.addField(['amazon_underlying'])
 
class DirectorsGroup(AFilmGroup):

    def __init__(self):
        AFilmGroup.__init__(self, 'directors')
        self.addNameField()

class CastGroup(AFilmGroup):

    def __init__(self):
        AFilmGroup.__init__(self, 'cast')
        self.addNameField()

class DescGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'desc')
        self.addNameField()

    def eligible(self, entity):
        return True

class StampedTombstoneGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'tombstone')
        self.addField(['tombstone_id'])

    def eligible(self, entity):
        return True

class ImagesGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'images')
        self.addNameField()

    def eligible(self, entity):
        return True

class AuthorsGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'authors')
        self.addNameField()

class PublishersGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'publishers')
        self.addNameField()

class ISBNGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'isbn')
        self.addNameField()

class SKUNumberGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'sku_number')
        self.addNameField()

allGroups = [
    FactualGroup,
    SinglePlatformGroup,
    FoursquareGroup,
    GooglePlacesGroup,
    TMDBGroup,
    RdioGroup,
    SpotifyGroup,
    iTunesGroup,
    AmazonGroup,
    FandangoGroup,
    NetflixGroup,
    StampedTombstoneGroup,

    # AmazonLinkGroup,
    # AmazonUnderlyingGroup,
    OpenTableGroup,
    OpenTableNicknameGroup,

    DescGroup,
    ImagesGroup,

    AddressGroup,
    CoordinatesGroup,
    PhoneGroup,
    SiteGroup,
    PriceRangeGroup,
    CuisineGroup,
    MenuGroup,
    ReleaseDateGroup,
    DirectorsGroup,
    CastGroup,
    LengthGroup,
    AlbumsGroup,
    TracksGroup,
    MPAARatingGroup,
    ArtistsGroup,
    GenresGroup,
    AuthorsGroup,
    PublishersGroup,
    ISBNGroup,
    SKUNumberGroup,

    # ShortDescriptionGroup, # Deprecated?
]
