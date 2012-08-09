#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import sys, inspect
from api.Schemas import *
from resolve.AEntityGroups import *

def moveField(source, target=None):
    target = target or source
    def wrapped(self, entity, proxy):
        item = getattr(proxy, source, None)
        if item:
            setattr(entity, target, item)
            return True
    return wrapped


def importEntityMinisFromProxyField(field, entityClass, entityType):
    def wrapper(self, entity, proxy):
        subfieldList = getattr(proxy, field, [])
        results = []
        for subfield in subfieldList:
            try:
                entityMini = entityClass()
                entityMini.title = subfield['name']
                entityMini.types = [entityType]
                if 'key' in subfield:
                    setattr(entityMini.sources, '%s_id' % proxy.source, subfield['key'])
                    setattr(entityMini.sources, '%s_source' % proxy.source, proxy.source)
                if 'url' in subfield:
                    setattr(entityMini.sources, '%s_url' % proxy.source, subfield['url'])
                if 'previewUrl' in subfield:
                    setattr(entityMini.sources, '%s_preview' % proxy.source, subfield['previewUrl'])
                results.append(entityMini)
            except Exception:
                report()
                logs.info('%s import failure: %s for %s' % (field, subfield['name'], proxy.name))
        if results:
            setattr(entity, field, results)
            return True
    return wrapper
        

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
 
    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.amazon_id = proxy.key
        try:
            if entity.isType('book'):
                entity.sources.amazon_underlying = proxy.underlying.key
                return True
        except Exception:
            pass


class StampedTombstoneGroup(BasicFieldGroup):
    def __init__(self):
        BasicFieldGroup.__init__(self, 'tombstone',
            source_path=['sources', 'tombstone_source'], 
            timestamp_path=['sources', 'tombstone_timestamp']
        )
        self.addField(['sources', 'tombstone_id'])

    def eligible(self, entity):
        return True


class StampedNemesesGroup(BasicFieldGroup):
    def __init__(self):
        BasicFieldGroup.__init__(self, 'nemeses',
            source_path=['sources', 'nemesis_source'], 
            timestamp_path=['sources', 'nemesis_timestamp']
        )
        self.addField(['sources', 'nemesis_ids'])

    def eligible(self, entity):
        return True

    def syncFields(self, entity, destination):
        source_ids = entity.sources.nemesis_ids
        if not source_ids:
            return False
        destination_ids = destination.sources.nemesis_ids
        if not destination_ids:
            destination.sources.nemesis_ids = source_ids
            return True
        final_ids = set(source_ids + destination_ids)
        if len(final_ids) > len(destination_ids):
            destination.sources.nemesis_ids = final_ids
            return True


class FactualGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'factual', 
            source_path=['sources', 'factual_source'], 
            timestamp_path=['sources', 'factual_timestamp']
        )
        self.addField(['sources', 'factual_id'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.factual_id = proxy.key


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

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.googleplaces_id = proxy.key
        entity.sources.googleplaces_reference = proxy.key
        ### NOTE: It looks like the proxy.key is actually the reference. Shouldn't this be the id?


class TMDBGroup(AMovieGroup):
    def __init__(self):
        AMovieGroup.__init__(self, 'tmdb',
            source_path=['sources', 'tmdb_source'], 
            timestamp_path=['sources', 'tmdb_timestamp']
        )
        self.addField(['sources', 'tmdb_id'])
        self.addField(['sources', 'tmdb_url'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.tmdb_id = proxy.key


class FandangoGroup(AMovieGroup):
    def __init__(self):
        AMovieGroup.__init__(self, 'fandango',
            source_path=['sources', 'fandango_source'], 
            timestamp_path=['sources', 'fandango_timestamp']
        )
        self.addField(['sources', 'fandango_id'])
        self.addField(['sources', 'fandango_url'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.fandango_id = proxy.key
        if proxy.url:
            entity.sources.fandango_url = proxy.url


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


class NetflixAvailableGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'netflix_available',
            source_path=['sources', 'netflix_available_source'], 
            timestamp_path=['sources', 'netflix_available_timestamp']
        )
        self.addKind('media_item')
        self.addKind('media_collection')
        self.addType('movie')
        self.addType('tv')

        self.addField(['sources', 'netflix_is_instant_available'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.netflix_is_instant_available = proxy.is_instant_available
        return True

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

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.rdio_id = proxy.key
        if hasattr(proxy, 'url'):
            entity.sources.rdio_url = proxy.url

class RdioAvailableGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'rdio_available',
            source_path=['sources', 'rdio_available_source'], 
            timestamp_path=['sources', 'rdio_available_timestamp']
        )
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['sources', 'rdio_available_stream'])
        self.addField(['sources', 'rdio_available_sample'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.rdio_available_stream = proxy.canStream
        entity.sources.rdio_available_sample = proxy.canSample
    

class TheTVDBGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'thetvdb',
            source_path=['sources', 'thetvdb_source'], 
            timestamp_path=['sources', 'thetvdb_timestamp']
        )
        self.addKind('media_collection')
        self.addType('tv')

        self.addField(['sources', 'thetvdb_id'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.thetvdb_id = proxy.key
    

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

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.spotify_id = proxy.key


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

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.itunes_id = proxy.key
        entity.sources.itunes_url = proxy.url

        preview = getattr(proxy, 'preview', None)
        if preview:
            entity.sources.itunes_preview = preview
            return True


class NYTimesGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'nytimes',
            source_path=['sources', 'nytimes_source'], 
            timestamp_path=['sources', 'nytimes_timestamp']
        )
        self.addKind('media_item')
        self.addType('book')
        self.addField(['sources', 'nytimes_id'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.nytimes_id = proxy.key


class UMDGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'umdmusic',
            source_path=['sources', 'umdmusic_source'], 
            timestamp_path=['sources', 'umdmusic_timestamp']
        )
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('track')

        self.addField(['sources', 'umdmusic_id'])

    def enrichEntityWithEntityProxy(self, entity, proxy):
        entity.sources.umdmusic_id = proxy.key


class FormattedAddressGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'formatted_address')
        self.addField(['formatted_address'])

    enrichEntityWithEntityProxy = moveField('address_string', 'formatted_address')

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

    def enrichEntityWithEntityProxy(self, entity, proxy):
        if len(proxy.address) > 0:
            address_components = [
                'street',
                'street_ext',
                'locality',
                'region',
                'postcode',
                'country',
            ]
            for k in address_components:
                if k in proxy.address:
                    setattr(entity, 'address_%s' % k, proxy.address[k])
            return True


class CoordinatesGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'coordinates')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        if proxy.coordinates is not None:
            coordinates = Coordinates()
            coordinates.lat = proxy.coordinates[0]
            coordinates.lng = proxy.coordinates[1]
            entity.coordinates = coordinates
            return True


class PhoneGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'phone')
        self.addNameField()

    enrichEntityWithEntityProxy = moveField('phone')
    

class SiteGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'site')
        self.addNameField()

    enrichEntityWithEntityProxy = moveField('url', 'site')


class GalleryGroup(APlaceGroup):
    def __init__(self):
        APlaceGroup.__init__(self, 'gallery')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        gallery = []
        for image in proxy.gallery:
            img = ImageSchema()
            img.caption = image['caption']
            size = ImageSizeSchema()
            size.url = image['url']
            size.height = image['height']
            size.width = image['width']
            img.sizes = [size]
            gallery.append(img)
        if gallery:
            entity.gallery = gallery
            return True


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

    enrichEntityWithEntityProxy = moveField('release_date')


class MPAARatingGroup(AKindTypeGroup):
    def __init__(self):
        AKindTypeGroup.__init__(self, 'mpaa_rating')
        self.addKind('media_collection')
        self.addType('tv')
        self.addKind('media_item')
        self.addType('movie')
        self.addNameField()

    enrichEntityWithEntityProxy = moveField('mpaa_rating')


class GenresGroup(AKindTypeGroup):
    def __init__(self):
        AKindTypeGroup.__init__(self, 'genres')
        self.addKind('person')
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addKind('software')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        if len(proxy.genres) > 0:
            entity.genres = proxy.genres
            return True


class ArtistsGroup(AKindTypeGroup):
    def __init__(self):
        AKindTypeGroup.__init__(self, 'artists')
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addNameField()

    enrichEntityWithEntityProxy = importEntityMinisFromProxyField(
            'artists', PersonEntityMini, 'artist')


class LengthGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'length')
        self.addKind('media_item')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        if proxy.length > 0:
            entity.length = int(proxy.length)
            return True

        
class AlbumsGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'albums')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_item')
        self.addType('track')
        self.addNameField()

    enrichEntityWithEntityProxy = importEntityMinisFromProxyField(
            'albums', MediaCollectionEntityMini, 'album')


class TracksGroup(AKindTypeGroup):
    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, 'tracks')
        self.addKind('person')
        self.addType('artist')
        self.addKind('media_collection')
        self.addType('album')
        self.addNameField()

    enrichEntityWithEntityProxy = importEntityMinisFromProxyField(
            'tracks', MediaItemEntityMini, 'track')


class DirectorsGroup(AFilmGroup):
    def __init__(self):
        AFilmGroup.__init__(self, 'directors')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        directors = []
        for director in proxy.directors:
            entityMini = PersonEntityMini()
            entityMini.title = director['name']
            directors.append(entityMini)
        if directors:
            entity.directors = directors
            return True


class CastGroup(AFilmGroup):
    def __init__(self):
        AFilmGroup.__init__(self, 'cast')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        cast = []
        for actor in proxy.cast:
            entityMini = PersonEntityMini()
            entityMini.title = actor['name']
            cast.append(entityMini)
        if cast:
            entity.cast = cast
            return True


class DescGroup(BasicFieldGroup):
    def __init__(self):
        BasicFieldGroup.__init__(self, 'desc')
        self.addNameField()

    def eligible(self, entity):
        return True

    enrichEntityWithEntityProxy = moveField('description', 'desc')


class LastPopularGroup(BasicFieldGroup):
    def __init__(self):
        BasicFieldGroup.__init__(self, 'last_popular')
        self.addNameField()
        self.addField(['last_popular_info'])
        self.addField(['total_popularity_measure'])

    def eligible(self, entity):
        return True

    def enrichEntityWithEntityProxy(self, entity, proxy):
        if proxy.last_popular:
            if entity.last_popular is None or proxy.last_popular > entity.last_popular:
                entity.last_popular = proxy.last_popular
            popularity_score = getattr(proxy, 'popularity_score', 0)
            if entity.total_popularity_measure is None or popularity_score > entity.total_popularity_measure:
                entity.total_popularity_measure = popularity_score
            return True



class ImagesGroup(BasicFieldGroup):
    def __init__(self):
        BasicFieldGroup.__init__(self, 'images')
        self.addNameField()

    def eligible(self, entity):
        return True

    def enrichEntityWithEntityProxy(self, entity, proxy):
        images = []
        for image in proxy.images:
            if not image:
                logs.warning('Caught an empty image from the proxy entity %s' % (proxy,))
                continue
            img = ImageSchema()
            size = ImageSizeSchema()
            size.url = image
            img.sizes = [size]
            images.append(img)
        if images:
            entity.images = images
            return True


class ScreenshotsGroup(ASoftwareGroup):
    def __init__(self):
        ASoftwareGroup.__init__(self, 'screenshots')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        screenshots = []
        for screenshot in proxy.screenshots:
            img = ImageSchema()
            size = ImageSizeSchema()
            size.url = screenshot
            img.sizes = [size]
            screenshots.append(img)
        if screenshots:
            entity.screenshots = screenshots
            return True


class AuthorsGroup(AKindTypeGroup):
    def __init__(self):
        AKindTypeGroup.__init__(self, 'authors')
        self.addKind('media_item')
        self.addKind('software')
        self.addType('book')
        self.addType('app')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        authors = []
        for author in proxy.authors:
            entityMini = PersonEntityMini()
            entityMini.title = author['name']
            authors.append(entityMini)
        if authors:
            entity.authors = authors
            return True


class PublishersGroup(AKindTypeGroup):
    def __init__(self):
        AKindTypeGroup.__init__(self, 'publishers')
        self.addKind('media_item')
        self.addKind('software')
        self.addType('book')
        self.addType('app')
        self.addNameField()

    def enrichEntityWithEntityProxy(self, entity, proxy):
        publishers = []
        for publisher in proxy.publishers:
            entityMini = PersonEntityMini()
            entityMini.title = publisher['name']
            publishers.append(entityMini)
        if publishers:
            entity.publishers = publishers
            return True

class ISBNGroup(ABookGroup):
    def __init__(self):
        ABookGroup.__init__(self, 'isbn')
        self.addNameField()

    enrichEntityWithEntityProxy = moveField('isbn')


# TODO(geoff): shouldn't SKU be on most of the products, not just books?
class SKUNumberGroup(ABookGroup):
    def __init__(self):
        ABookGroup.__init__(self, 'sku_number')
        self.addNameField()

    enrichEntityWithEntityProxy = moveField('sku_number')


"""
Add all defined groups to the 'allGroups' list. This is necessary for EntityProxySource to enrich all possible groups.

Note that this only works if no abstract classes exist within this module (EntityGroups.py). All abstract classes should
be defined in AEntityGroups.py.
"""

allGroups = []
allGroupObjects = inspect.getmembers(sys.modules[__name__], lambda x: inspect.isclass(x) and x.__module__ == __name__)
for groupObject in allGroupObjects:
    allGroups.append(groupObject[1])

