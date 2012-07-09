#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import sys, inspect
    from resolve.AEntityGroups        import *
except:
    report()
    raise


class FactualGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'factual', 
            source_path=['sources', 'factual_source'], 
            timestamp_path=['sources', 'factual_timestamp']
        )
        self.addField(['sources', 'factual_id'])

class FoursquareGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'foursquare',
            source_path=['sources', 'foursquare_source'], 
            timestamp_path=['sources', 'foursquare_timestamp']
        )
        self.addField(['sources', 'foursquare_id'])
        self.addField(['sources', 'foursquare_url'])

class InstagramGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'instagram',
            source_path=['sources', 'instagram_source'], 
            timestamp_path=['sources', 'instagram_timestamp']
        )
        self.addField(['sources', 'instagram_id'])


class OpenTableGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'opentable',
            source_path=['sources', 'opentable_source'], 
            timestamp_path=['sources', 'opentable_timestamp']
        )
        self.addField(['sources', 'opentable_id'])
        self.addField(['sources', 'opentable_url'])
        self.addField(['sources', 'opentable_nickname'])

class SinglePlatformGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'singleplatform',
            source_path=['sources', 'singleplatform_source'], 
            timestamp_path=['sources', 'singleplatform_timestamp']
        )
        self.addField(['sources', 'singleplatform_id'])
        self.addField(['sources', 'singleplatform_url'])

class GooglePlacesGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'googleplaces',
            source_path=['sources', 'googleplaces_source'], 
            timestamp_path=['sources', 'googleplaces_timestamp']
        )
        self.addField(['sources', 'googleplaces_id'])
        self.addField(['sources', 'googleplaces_reference'])

class TMDBGroup(AMovieGroup):

    def __init__(self):
        AMovieGroup.__init__(self, 'tmdb',
            source_path=['sources', 'tmdb_source'], 
            timestamp_path=['sources', 'tmdb_timestamp']
        )
        self.addField(['sources', 'tmdb_id'])
        self.addField(['sources', 'tmdb_url'])

class FandangoGroup(AMovieGroup):

    def __init__(self):
        AMovieGroup.__init__(self, 'fandango',
            source_path=['sources', 'fandango_source'], 
            timestamp_path=['sources', 'fandango_timestamp']
        )
        self.addField(['sources', 'fandango_id'])
        self.addField(['sources', 'fandango_url'])

        self.addKind('media_item')
        self.addType('movie')

class NetflixGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'netflix',
            source_path=['sources', 'netflix_source'], 
            timestamp_path=['sources', 'netflix_timestamp']
        )
        self.addKind('media_item')
        self.addKind('media_collection')
        self.addType('movie')
        self.addType('tv')

        self.addField(['sources', 'netflix_id'])
        self.addField(['sources', 'netflix_url'])
        self.addField(['sources', 'netflix_is_instant_available'])
        self.addField(['sources', 'netflix_instant_available_until'])

class RdioGroup(AKindTypeGroup):
    
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'rdio',
            source_path=['sources', 'rdio_source'], 
            timestamp_path=['sources', 'rdio_timestamp']
        )
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['sources', 'rdio_id'])
        self.addField(['sources', 'rdio_url'])

class TheTVDBGroup(AKindTypeGroup):
    
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'thetvdb',
            source_path=['sources', 'thetvdb_source'], 
            timestamp_path=['sources', 'thetvdb_timestamp']
        )
        self.addKind('media_collection')
        self.addType('tv')

        self.addField(['sources', 'thetvdb_id'])

class SpotifyGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'spotify',
            source_path=['sources', 'spotify_source'], 
            timestamp_path=['sources', 'spotify_timestamp']
        )
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['sources', 'spotify_id'])
        self.addField(['sources', 'spotify_url'])

class iTunesGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'itunes',
            source_path=['sources', 'itunes_source'], 
            timestamp_path=['sources', 'itunes_timestamp']
        )
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

        self.addField(['sources', 'itunes_id'])
        self.addField(['sources', 'itunes_url'])
        self.addField(['sources', 'itunes_preview'])

class FormattedAddressGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'formatted_address')
        fields = [ ['formatted_address'] ]
        for field in fields:
            self.addField(field)

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

class GalleryGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'gallery')
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
        AFilmGroup.__init__(self, 'imdb',
            source_path=['sources', 'imdb_source'], 
            timestamp_path=['sources', 'imdb_timestamp']
        )
        self.addField(['sources', 'imdb_id'])

class AmazonGroup(AAmazonGroup):

    def __init__(self):
        AAmazonGroup.__init__(self, 'amazon',
            source_path=['sources', 'amazon_source'], 
            timestamp_path=['sources', 'amazon_timestamp']
        )
        self.addField(['sources', 'amazon_id'])
        self.addField(['sources', 'amazon_url'])
        self.addField(['sources', 'amazon_underlying'])
 
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
        BasicFieldGroup.__init__(self, 'tombstone',
            source_path=['sources', 'tombstone_source'], 
            timestamp_path=['sources', 'tombstone_timestamp']
        )
        self.addField(['sources', 'tombstone_id'])

    def eligible(self, entity):
        return True

class ImagesGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'images')
        self.addNameField()

    def eligible(self, entity):
        return True

class ScreenshotsGroup(ASoftwareGroup):

    def __init__(self):
        ASoftwareGroup.__init__(self, 'screenshots')
        self.addNameField()

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


"""
Add all defined groups to the 'allGroups' list. This is necessary for EntityProxySource to enrich all possible groups.

Note that this only works if no abstract classes exist within this module (EntityGroups.py). All abstract classes should
be defined in AEntityGroups.py.
"""

allGroups = []
allGroupObjects = inspect.getmembers(sys.modules[__name__], lambda x: inspect.isclass(x) and x.__module__ == __name__)
for groupObject in allGroupObjects:
    allGroups.append(groupObject[1])

