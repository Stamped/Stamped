#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, re
import unicodedata, utils
import libs.CountryData

from difflib        import SequenceMatcher
from Schemas        import *
from libs.LibUtils  import parseDateString
import datetime


categories = set([
    'food', 
    'music', 
    'film', 
    'book', 
    'other'
])

subcategories = {
    # --------------------------
    #           food
    # --------------------------
    'restaurant'        : 'food', 
    'bar'               : 'food', 
    'bakery'            : 'food', 
    'cafe'              : 'food', 
    'market'            : 'food', 
    'food'              : 'food', 
    'night_club'        : 'food', 
    
    # --------------------------
    #           book
    # --------------------------
    'book'              : 'book', 
    
    # --------------------------
    #           film
    # --------------------------
    'movie'             : 'film', 
    'tv'                : 'film', 
    
    # --------------------------
    #           music
    # --------------------------
    'artist'            : 'music', 
    'song'              : 'music', 
    'album'             : 'music', 
    'track'             : 'music', 
    
    # --------------------------
    #           other
    # --------------------------
    'app'               : 'other', 
    'other'             : 'other', 
    
    # the following subcategories are from google places
    'amusement_park'    : 'other', 
    'aquarium'          : 'other', 
    'art_gallery'       : 'other', 
    'beauty_salon'      : 'other', 
    'book_store'        : 'other', 
    'bowling_alley'     : 'other', 
    'campground'        : 'other', 
    'casino'            : 'other', 
    'clothing_store'    : 'other', 
    'department_store'  : 'other', 
    'establishment'     : 'other', 
    'florist'           : 'other', 
    'gym'               : 'other', 
    'home_goods_store'  : 'other', 
    'jewelry_store'     : 'other', 
    'library'           : 'other', 
    'liquor_store'      : 'other', 
    'lodging'           : 'other', 
    'movie_theater'     : 'other', 
    'museum'            : 'other', 
    'park'              : 'other', 
    'school'            : 'other', 
    'shoe_store'        : 'other', 
    'shopping_mall'     : 'other', 
    'spa'               : 'other', 
    'stadium'           : 'other', 
    'store'             : 'other', 
    'university'        : 'other', 
    'zoo'               : 'other', 
    
    # the following subcategories are from amazon
    'video_game'        : 'other', 
}

kinds = set([
    'place',
    'person',
    'media_collection',
    'media_item',
    'software',
    'other',
])

types = set([
    # PEOPLE
    'artist',

    # MEDIA COLLECTIONS
    'tv',
    'album',

    # MEDIA ITEMS
    'track',
    'movie',
    'book',

    # SOFTWARE
    'app',

    # PLACES
    'restaurant',
    'bar',
    'bakery',
    'cafe',
    'market',
    'food',
    'night_club',
    'amusement_park',
    'aquarium',
    'art_gallery',
    'beauty_salon',
    'book_store',
    'bowling_alley',
    'campground',
    'casino',
    'clothing_store',
    'department_store',
    'establishment',
    'florist',
    'gym',
    'home_goods_store',
    'jewelry_store',
    'library',
    'liquor_store',
    'lodging',
    'movie_theater',
    'museum',
    'park',
    'school',
    'shoe_store',
    'shopping_mall',
    'spa',
    'stadium',
    'store',
    'university',
    'zoo',
])

countries = libs.CountryData.countries

city_state_re = re.compile('.*,\s*([a-zA-Z .-]+)\s*,\s*([a-zA-Z]+).*')
year_re = re.compile(r'([0-9]{4})')

def formatReleaseDate(date):
    try:
        return date.strftime("%h %d, %Y")
    except:
        return None

def formatAddress(entity, extendStreet=False, breakLines=False):

    street      = entity.address_street
    street_ext  = entity.address_street_ext
    locality    = entity.address_locality
    region      = entity.address_region
    postcode    = entity.address_postcode
    country     = entity.address_country

    delimiter = '\n' if breakLines else ', '

    if street is not None and locality is not None and country is not None:

        # Expand street 
        if extendStreet == True and street_ext is not None:
            street = '%s %s' % (street, street_ext)

        # Use state if in US
        if country == 'US':
            if region is not None and postcode is not None:
                return '%s%s%s, %s %s' % (street, delimiter, locality, region, postcode)
            elif region is not None:
                return '%s%s%s, %s' % (street, delimiter, locality, postcode)
            elif postcode is not None:
                return '%s%s%s, %s' % (street, delimiter, locality, region)

        # Use country if outside US
        else:
            if country in countries:
                return '%s%s%s, %s' % (street, delimiter, locality, countries[country])
            else:
                return '%s%s%s, %s' % (street, delimiter, locality, country)

    if entity.address is not None:
        return entity.address
        
    if entity.neighborhood is not None:
        return entity.neighborhood

    return None

def formatSubcategory(subcategory):
    if subcategory == 'tv':
        return 'TV'
    return subcategory.replace('_', ' ').title()

def formatFilmLength(seconds):
    try:
        seconds = int(seconds)
        m = (seconds % 3600) / 60
        h = (seconds - (seconds % 3600)) / 3600
        if h > 0:
            return '%s hr %s min' % (h, m)
        else:
            return '%s min' % m
    except Exception:
        return None

def getGenericSubtitle(entity):
    if entity.subcategory is not None:
        return str(entity.subcategory).replace('_', ' ').title()
    return None

def getLocationSubtitle(entity, detailed=False):
    # Return detailed address data if requested
    if detailed:
        
        address = formatAddress(entity)
        if address is not None:
            return address
        
        return getGenericSubtitle(entity)
    
    # Check if address components exist
    if entity.address_country is not None and entity.address_locality is not None:
        if entity.address_country == 'US':
            if entity.address_region is not None:
                return "%s, %s" % (entity.address_locality, entity.address_region)
        else:
            country = entity.address_country
            if entity.address_country in countries:
                country = countries[entity.address_country]
            return "%s, %s" % (entity.address_locality, country)
    
    # Extract city / state with regex as fallback
    if entity.address is not None:
        match = city_state_re.match(entity.address)
        
        if match is not None:
            # city, state
            return "%s, %s" % match.groups()
    
    # Use generic subtitle as last resort
    return getGenericSubtitle(entity)

def setSubtitle(entity):
    entity.subtitle = getGenericSubtitle(entity)

def setFields(entity, detailed=False):
    global city_state_re
    
    try:
        entity.category = subcategories[entity.subcategory]
    except:
        entity.category = 'other'
    
    # Subtitle
    if entity.category == 'food':
        entity.subtitle = getLocationSubtitle(entity, detailed)
    
    elif entity.category == 'book':
        if entity.author is not None:
            entity.subtitle = entity.author
        else:
            setSubtitle(entity)
    
    elif entity.category == 'film':
        if entity.subcategory == 'movie':
            try:
                year = year_re.search(entity.original_release_date).groups()[0]
                entity.subtitle = 'Movie (%s)' % year
            except:
                entity.subtitle = 'Movie'
        elif entity.subcategory == 'tv':
            if entity.network_name is not None:
                entity.subtitle = 'TV Show (%s)' % entity.network_name
            else:
                entity.subtitle = 'TV Show'
    
    elif entity.category == 'music':
        if entity.subcategory == 'artist':
            entity.subtitle = 'Artist'
        elif entity.subcategory == 'album':
            if entity.artist_display_name is not None:
                entity.subtitle = "Album by %s" % entity.artist_display_name
            else:
                entity.subtitle = 'Album'
        elif entity.subcategory == 'song':
            if entity.artist_display_name is not None:
                entity.subtitle = "Song by %s" % entity.artist_display_name
            else:
                entity.subtitle = 'Song'
    
    elif entity.category == 'other':
        if entity.subcategory == 'app' and entity.artist_display_name is not None:
            entity.subtitle = 'App (%s)' % entity.artist_display_name
        elif entity.address is not None or entity.address_country is not None:
            entity.subtitle = getLocationSubtitle(entity, detailed)
        elif entity.subtitle is None:
            setSubtitle(entity)
    
    if entity.subtitle is None or len(entity.subtitle) == 0:
        logs.warning('Invalid subtitle: %s' % entity)
        setSubtitle(entity)
        
        if entity.subtitle is None or len(entity.subtitle) == 0:
            entity.subtitle = "Other"
    
    if entity.type is None:
        entity.type = deriveTypeFromSubcategory(entity.subcategory)

    return entity

def isEqual(entity1, entity2, prefix=False):
    """
    # note: useful for debugging search dupes
    from pprint import pformat
    utils.log("-" * 40)
    utils.log(pformat(entity1.value))
    utils.log(pformat(entity2.value))
    utils.log("-" * 40)
    """
    
    try:
        is_google_places_special_case = \
            ((entity1.subcategory == 'other' and entity1.googleLocal is not None) or \
             (entity2.subcategory == 'other' and entity2.googleLocal is not None))
        
        if not prefix and entity1.subcategory != entity2.subcategory:
            # if either entity came from google autosuggest, disregard subcategories not matching
            if not is_google_places_special_case:
                return False
        
        # if entity1.simplified_title != entity2.simplified_title:
        #     return False
        elif prefix or is_google_places_special_case:
            return True
        
        if entity1.lat is not None:
            if entity2.lat is None:
                return False
            
            earthRadius = 3959.0 # miles
            
            distance = utils.get_spherical_distance((entity1.lat, entity1.lng), 
                                                    (entity2.lat, entity2.lng))
            
            distance = distance * earthRadius
            
            if distance > 0.8 or distance < 0:
                return False
            
            # TODO: investigate libraries to determine similarity between two 
            # addresses (e.g., converting to some standardized form and then 
            # comparing)
            """
            is_junk = " \t-,".__contains__ # characters for SequenceMatcher to disregard
            
            addr1 = entity1.address.lower()
            addr2 = entity2.address.lower()
            
            def _normalize_addr(addr):
                addr = addr.replace(' street ' ' st ')
                addr = addr.replace(' st. ' ' st ')
                addr = addr.replace(' boulevard ' ' st ')
                addr = addr.replace(' lane ' ' st ')
                addr = addr.replace(' highway ' ' st ')
                addr = addr.replace(' road ' ' st ')
                addr = addr.replace(',' ' ')
                return addr
            
            addr1 = _normalize_addr(addr1)
            addr2 = _normalize_addr(addr2)
            
            ratio = SequenceMatcher(is_junk, addr1, addr2).ratio()
            
            return (ratio >= 0.95)
            """
        
        elif entity2.lat is not None:
            return False
        
        return True
    except:
        return False

def getSimplifiedTitle(title):
    title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
    title = title.lower().strip()
    
    return title

def deriveKindFromSubcategory(subcategory):
    mapping = {
        'artist'            : 'person', 

        'album'             : 'media_collection', 
        'tv'                : 'media_collection', 

        'book'              : 'media_item', 
        'track'             : 'media_item', 
        'song'              : 'media_item', 
        'movie'             : 'media_item', 

        'app'               : 'software', 

        'restaurant'        : 'place', 
        'bar'               : 'place', 
        'bakery'            : 'place', 
        'cafe'              : 'place', 
        'market'            : 'place', 
        'food'              : 'place', 
        'night_club'        : 'place', 
        'amusement_park'    : 'place', 
        'aquarium'          : 'place', 
        'art_gallery'       : 'place', 
        'beauty_salon'      : 'place', 
        'book_store'        : 'place', 
        'bowling_alley'     : 'place', 
        'campground'        : 'place', 
        'casino'            : 'place', 
        'clothing_store'    : 'place', 
        'department_store'  : 'place', 
        'establishment'     : 'place', 
        'florist'           : 'place', 
        'gym'               : 'place', 
        'home_goods_store'  : 'place', 
        'jewelry_store'     : 'place', 
        'library'           : 'place', 
        'liquor_store'      : 'place', 
        'lodging'           : 'place', 
        'movie_theater'     : 'place', 
        'museum'            : 'place', 
        'park'              : 'place', 
        'school'            : 'place', 
        'shoe_store'        : 'place', 
        'shopping_mall'     : 'place', 
        'spa'               : 'place', 
        'stadium'           : 'place', 
        'store'             : 'place', 
        'university'        : 'place', 
        'zoo'               : 'place', 

        'other'             : 'other', 
        'video_game'        : 'other', 
    }
    if subcategory in mapping:
        return mapping[subcategory]
    return 'other'

def deriveTypesFromSubcategories(subcategories):
    result = set()

    for item in types.intersection(subcategories):
        result.add(item)

    return result 

def deriveSubcategoryFromTypes(types):
    for t in types:
        if t in subcategories.keys():
            return t 
    return 'other'

def deriveCategoryFromTypes(types):
    subcategory = deriveSubcategoryFromTypes(types)
    if subcategory in subcategories:
        return subcategories[subcategory]
    return 'other'

def _getEntityObjectFromKind(kind):
    if kind == 'place':
        return PlaceEntity
    if kind == 'person':
        return PersonEntity
    if kind == 'media_collection':
        return MediaCollectionEntity
    if kind == 'media_item':
        return MediaItemEntity
    if kind == 'software':
        return SoftwareEntity
    return BasicEntity

def buildEntity(data=None, kind=None):
    if data is not None:
        kind = data.pop('kind', kind)
    new = _getEntityObjectFromKind(kind)
    return new(data)

def upgradeEntityData(entityData):
    # Just to be explicit..
    old = entityData

    kind = deriveKindFromSubcategory(old['subcategory'])

    new = _getEntityObjectFromKind(kind)()

    def setBasicGroup(source, target, oldName, newName=None, oldSuffix=None, newSuffix=None, additionalSuffixes=None):
        if newName is None:
            newName = oldName
        if oldSuffix is None:
            item = source.pop(oldName, None)
        else:
            item = source.pop('%s_%s' % (oldName, oldSuffix), None)

        if item is not None:
            # Manual conversions...
            if oldName == 'track_length':
                try:
                    item = int(str(item).split('.')[0])
                except:
                    pass

            if newSuffix is None:
                target[newName] = item 
            else:
                target['%s_%s' % (newName, newSuffix)] = item

            if newName != 'tombstone':
                target['%s_source' % newName] = source.pop('%s_source' % oldName, 'seed')
            target['%s_timestamp' % newName]  = source.pop('%s_timestamp' % oldName, datetime.datetime.utcnow())

            if additionalSuffixes is not None:
                for s in additionalSuffixes:
                    t = source.pop('%s_%s' % (oldName, s), None)
                    if t is not None:
                        target['%s_%s' % (newName, s)] = t 

    def setListGroup(source, target, oldName, newName=None, delimiter=',', wrapper=None):
        if newName is None:
            newName = oldName

        item = source.pop(oldName, None)

        if item is not None:
            items = []
            for i in item.split(delimiter):
                if wrapper is not None:
                    entityMini = wrapper()
                    entityMini.title = i.strip()
                    items.append(entityMini)
                else:
                    items.append(i.strip())
            target[newName] = items 

            target['%s_source' % newName]     = source.pop('%s_source' % oldName, 'seed')
            target['%s_timestamp' % newName]  = source.pop('%s_timestamp' % oldName, datetime.datetime.utcnow())


    sources                 = old.pop('sources', {})
    details                 = old.pop('details', {})
    timestamp               = old.pop('timestamp', {})
    place                   = details.pop('place', {})
    contact                 = details.pop('contact', {})
    restaurant              = details.pop('restaurant', {})
    media                   = details.pop('media', {})
    video                   = details.pop('video', {})
    artist                  = details.pop('artist', {})
    album                   = details.pop('album', {})
    song                    = details.pop('song', {})


    # General
    new.schema_version      = 0
    new.entity_id           = old.pop('entity_id', None)
    new.title               = old.pop('title', None)
    new.title_lower         = old.pop('titlel', None)
    new.image               = old.pop('image', None)
    # TODO: Refactor image
    # TODO: Include old.sources.netflix.images[large/small/etc.]
    setBasicGroup(old, new, 'desc')
    subcategory = old['subcategory']
    if subcategory == 'song':
        subcategory = 'track'
    new.types.append(subcategory)

    # TODO: Add custom subtitle for user-generated


    # Sources
    setBasicGroup(sources, new['sources'], 'spotify', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new['sources'], 'rdio', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new['sources'], 'amazon', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new['sources'], 'fandango', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new['sources'], 'stamped', 'tombstone', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources.pop('tmdb', {}), new['sources'], 'tmdb', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources.pop('factual', {}), new['sources'], 'factual', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    # TODO: Add factual_crosswalk
    setBasicGroup(sources.pop('singleplatform', {}), new['sources'], 'singleplatform', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])

    # Apple / iTunes
    setBasicGroup(sources, new['sources'], 'itunes', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    if new.sources.itunes_id is None:
        setBasicGroup(sources.pop('apple', {}), new['sources'], 'aid', 'itunes', newSuffix='id', additionalSuffixes=['url'])

    # OpenTable
    setBasicGroup(sources, new['sources'], 'opentable', oldSuffix='id', newSuffix='id', additionalSuffixes=['nickname', 'url'])
    if new.sources.opentable_id is None:
        setBasicGroup(sources.pop('openTable', {}), new['sources'], 'rid', 'opentable', newSuffix='id', additionalSuffixes=['url'])

    # Google Places
    googleplaces = sources.pop('googlePlaces', {})
    setBasicGroup(googleplaces, new['sources'], 'googleplaces', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    if new.sources.googleplaces_id is None:
        setBasicGroup(googleplaces, new['sources'], 'reference', 'googleplaces', newSuffix='id', additionalSuffixes=['url'])

    # User Generated
    userGenerated = sources.pop('userGenerated', {}).pop('generated_by', None)
    if userGenerated is not None:
        new.sources.user_generated_id = userGenerated
        if 'created' in timestamp:
            new.sources.user_generated_timestamp = timestamp['created']
        else:
            new.sources.user_generated_timestamp = datetime.datetime.utcnow()


    # Contacts
    setBasicGroup(contact, new.contact, 'phone')
    setBasicGroup(contact, new.contact, 'site')
    setBasicGroup(contact, new.contact, 'email')
    setBasicGroup(contact, new.contact, 'fax')


    # Places
    if newType == 'place':
        coordinates = old.pop('coordinates', None)
        if coordinates is not None:
            new.coordinates = coordinates

        addressComponents = ['locality', 'postcode', 'region', 'street', 'street_ext']
        setBasicGroup(place, new, 'address', 'address', oldSuffix='country', newSuffix='country', additionalSuffixes=addressComponents)

        setBasicGroup(place, new, 'address', 'formatted_address')
        setBasicGroup(place, new, 'hours')
        setBasicGroup(restaurant, new, 'menu')
        setBasicGroup(restaurant, new, 'price_range')
        setBasicGroup(restaurant, new, 'alcohol_flag')
        
        setListGroup(restaurant, new, 'cuisine')


    # Artist
    if newType == 'artist':

        songs = artist.pop('songs', [])
        for song in songs:
            entityMini = MediaItemEntityMini()
            entityMini.title = song['song_name']
            if 'id' in song and 'source' in song and song['source'] == 'itunes':
                entityMini.sources.itunes_id = song['id']
                entityMini.sources.itunes_source = 'itunes'
                entityMini.sources.itunes_timestamp = song.pop('timestamp', datetime.datetime.utcnow())
            new.tracks.append(entityMini)
        if len(songs) > 0:
            new.tracks_source = artist.pop('songs_source', 'seed')
            new.tracks_timestamp = artist.pop('songs_timestamp', datetime.datetime.utcnow())

        albums = artist.pop('albums', [])
        for item in albums:
            entityMini = MediaCollectionEntityMini()
            entityMini.title = item['album_name']
            if 'id' in item and 'source' in item and item['source'] == 'itunes':
                entityMini.sources.itunes_id = item['id']
                entityMini.sources.itunes_source = 'itunes'
                entityMini.sources.itunes_timestamp = item.pop('timestamp', datetime.datetime.utcnow())
            new.albums.append(entityMini)
        if len(albums) > 0:
            new.albums_source = artist.pop('albums_source', 'seed')
            new.albums_timestamp = artist.pop('albums_timestamp', datetime.datetime.utcnow())

        setListGroup(media, new, 'genre', 'genres')


    # General Media
    if newType in ['album', 'tv', 'track', 'movie', 'book']:
        artwork_url = media.pop('artwork_url', None)
        if new.image is None and artwork_url is not None:
            new.image = artwork_url

        setBasicGroup(media, new, 'track_length', 'length')
        setBasicGroup(media, new, 'mpaa_rating')
        setBasicGroup(media, new, 'release_date')

        setListGroup(media, new, 'genre', 'genres')
        setListGroup(media, new, 'artist_display_name', 'artists', wrapper=PersonEntityMini)
        setListGroup(video, new, 'cast', 'cast', wrapper=PersonEntityMini)
        setListGroup(video, new, 'director', 'directors', wrapper=PersonEntityMini)

        originalReleaseDate = parseDateString(media.pop('original_release_date', None))
        if new.release_date is None and originalReleaseDate is not None:
            new.release_date = originalReleaseDate
            new.release_date_source = 'seed'
            new.release_date_timestamp = datetime.datetime.utcnow()


    # Album
    if newType == 'album':
        songs = album.pop('tracks', [])
        for song in songs:
            entityMini = MediaItemEntityMini()
            entityMini.title = song
            new.tracks.append(entityMini)
        if len(songs) > 0:
            new.tracks_source = album.pop('songs_source', 'seed')
            new.tracks_timestamp = album.pop('songs_timestamp', datetime.datetime.utcnow())


    # Track
    if newType == 'track':
        albumName = song.pop('album_name', media.pop('album_name', None))
        print albumName
        if albumName is not None:
            entityMini = MediaCollectionEntityMini()
            entityMini.title = albumName
            albumId = song.pop('song_album_id', None)
            if albumId is not None:
                entityMini.sources.itunes_id = albumId 
                entityMini.sources.itunes_source = 'seed'
                entityMini.sources.itunes_timestamp = datetime.datetime.utcnow()
            new.collections.append(entityMini)
            new.collections_source = song.pop('album_name_source', 'seed')
            new.collections_timestamp = song.pop('album_name_timestamp', datetime.datetime.utcnow())

    # Apps
    if newType == 'app':
        setBasicGroup(media, new, 'release_date')
        setListGroup(media, new, 'authors', 'artist_display_name', wrapper=PersonEntityMini)

        screenshots = media.pop('screenshots', [])
        for screenshot in screenshots:
            imageSchema = ImageSchema()
            imageSchema.image = screenshot 
            imageSchema.source = 'itunes'
            new.screenshots.append(imageSchema)
        if len(screenshots) > 0:
            new.screenshots_source = media.pop('screenshots_source', 'seed')
            new.screenshots_timestamp = media.pop('screenshots_timestamp', datetime.datetime.utcnow())

    return new 