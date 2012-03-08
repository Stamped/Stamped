#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from BasicFieldGroup    import BasicFieldGroup
except:
    report()
    raise

class ASubcategoryGroup(BasicFieldGroup):
    def __init__(self, *args, **kwargs):
        BasicFieldGroup.__init__(self, *args, **kwargs)
        self.__eligible = set( )
        
    def addEligible(self, subcategory):
        self.__eligible.add(subcategory)

    def removeEligible(self, subcategory):
        self.__eligible.remove(subcategory)
    
    def eligible(self, entity):
        if 'subcategory' in entity and entity['subcategory'] in self.__eligible:
            return True
        else:
            return False  

class APlaceGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        eligible = set( [
            'restaurant',
            'bar', 
            'bakery',
            'cafe', 
            'market',
            'food',
            'night_club',
            'establishment',
        ] )
        for v in eligible:
            self.addEligible(v)

class ARestaurantGroup(APlaceGroup):

    def __init__(self, *args, **kwargs):
        APlaceGroup.__init__(self, *args, **kwargs)
        self.removeEligible('establishment')

class AMediaGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        eligible = set( [
            'book',
            'movie',
            'tv',
            'song',
            'album',
            'app',
        ] )
        for v in eligible:
            self.addEligible(v)

class ABookGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        self.addEligible('book')

class AMovieGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        self.addEligible('movie')

class AFilmGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        self.addEligible('movie')
        self.addEligible('tv')

class FactualGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'factual')
        self.addField(['factual_id'])

class OpenTableGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'opentable')
        self.addField(['opentable_id'])

class OpenTableNicknameGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'opentable_nickname')
        self.addNameField()

class SinglePlatformGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'singleplatform')
        self.addField(['singleplatform_id'])

class GooglePlacesGroup(APlaceGroup):

    def __init__(self):
        APlaceGroup.__init__(self, 'googleplaces')
        self.addField(['googleplaces_id'])

class TMDBGroup(AMovieGroup):

    def __init__(self):
        AMovieGroup.__init__(self, 'tmdb')
        self.addField(['tmdb_id'])

class RdioGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'rdio')
        self.addField(['rdio_id'])
        self.addEligible('song')
        self.addEligible('artist')
        self.addEligible('album')

class SpotifyGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'spotify')
        self.addField(['spotify_id'])
        self.addEligible('song')
        self.addEligible('artist')
        self.addEligible('album')

class iTunesGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'itunes')
        self.addField(['itunes_id'])
        self.addField(['itunes_url'])
        self.addEligible('song')
        self.addEligible('artist')
        self.addEligible('album')
        self.addEligible('movie')
        self.addEligible('book')

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

class ReleaseDateGroup(AMediaGroup):

    def __init__(self):
        AMediaGroup.__init__(self, 'release_date')
        self.addNameField()

class MPAARatingGroup(AMediaGroup):

    def __init__(self):
        AMediaGroup.__init__(self, 'mpaa_rating')
        self.addNameField()

class GenreGroup(AMediaGroup):

    def __init__(self):
        AMediaGroup.__init__(self, 'genre')
        self.addNameField()
        self.addEligible('artist')

class ArtistDisplayNameGroup(AMediaGroup):

    def __init__(self):
        AMediaGroup.__init__(self, 'artist_display_name')
        self.addNameField()

class TracksGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'tracks')
        self.addNameField()
        self.addEligible('album')

class TrackLengthGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'track_length')
        self.addNameField()
        self.addEligible('song')
        self.addEligible('movie')

class ShortDescriptionGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'short_description')
        self.addNameField()
        self.addEligible('movie')
        self.addEligible('tv')

class AlbumsGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'albums')
        self.addNameField()
        self.addEligible('artist')

class SongsGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'songs')
        self.addNameField()
        self.addEligible('artist')

class AlbumNameGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, 'album_name')
        self.addNameField()
        self.addEligible('song')


class AAmazonGroup(ASubcategoryGroup):

    def __init__(self, *args, **kwargs):
        ASubcategoryGroup.__init__(self, *args, **kwargs)
        self.addEligible('book')
        self.addEligible('song')
        self.addEligible('album')

class AmazonGroup(AAmazonGroup):

    def __init__(self):
        AAmazonGroup.__init__(self, 'amazon')
        self.addField(['amazon_id'])


class AmazonLinkGroup(AAmazonGroup):

    def __init__(self):
        AAmazonGroup.__init__(self, 'amazon_link')
        self.addNameField()

class AmazonUnderlyingGroup(AAmazonGroup):

    def __init__(self):
        AAmazonGroup.__init__(self, 'amazon_underlying')
        self.addNameField()
 
 
class DirectorGroup(AFilmGroup):

    def __init__(self):
        AFilmGroup.__init__(self, 'director')
        self.addNameField()

class CastGroup(AFilmGroup):

    def __init__(self):
        AFilmGroup.__init__(self, 'cast')
        self.addNameField()

class SubtitleGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'subtitle')
        self.addNameField()

    def eligible(self, entity):
        return True

class DescGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'desc')
        self.addNameField()

    def eligible(self, entity):
        return True

class MangledTitleGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'mangled_title')
        self.addNameField()

    def eligible(self, entity):
        return True

class SubcategoryGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'subcategory')
        self.addNameField()
        self.addField(['category'])

    def eligible(self, entity):
        return True

class ImagesGroup(BasicFieldGroup):

    def __init__(self):
        BasicFieldGroup.__init__(self, 'images')
        self.addField(['images','large'])
        self.addField(['images','small'])
        self.addField(['images','tiny'])

    def eligible(self, entity):
        return True


class AuthorGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'author')
        self.addNameField()

class PublisherGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'publisher')
        self.addNameField()

class ISBNGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'isbn')
        self.addNameField()

class NumPagesGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'num_pages')
        self.addNameField()


class SKUNumberGroup(ABookGroup):

    def __init__(self):
        ABookGroup.__init__(self, 'sku_number')
        self.addNameField()


