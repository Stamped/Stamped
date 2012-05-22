#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, re
import unicodedata, utils

try:
    from api.Schemas        import *
    from difflib        import SequenceMatcher
    from libs.LibUtils  import parseDateString
    from datetime       import datetime
    from bson.objectid  import ObjectId 
    from collections    import defaultdict
except:
    logs.report()
    raise

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

def getSimplifiedTitle(title):
    title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
    title = title.lower().strip()
    
    return title

def deriveSubcategoriesFromCategory(category):
    result = set()
    
    for k, v in subcategories.iteritems():
        if v == category or (category == 'place' and (v == 'food')):
            result.add(k)
    return result

def deriveKindFromCategory(category):
    result = set()
    
    if category == 'place':
        result.add('place')
    else:
        for k, v in subcategories.iteritems():
            if v == category:
                result.add(deriveKindFromSubcategory(k))
    
    return result

def deriveKindFromSubcategory(subcategory):
    mapping = {
        'artist'            : 'person', 
        
        'album'             : 'media_collection', 
        'tv'                : 'media_collection', 
        
        'book'              : 'media_item', 
        'track'             : 'media_item', 
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
        'point_of_interest' : 'place',

        'other'             : 'other', 
        'video_game'        : 'other', 
    }
    if subcategory in mapping:
        return mapping[subcategory]
    if subcategory == 'song':
        return 'media_item'
    return 'other'

def deriveTypesFromCategory(category):
    result = set()
    
    for k, v in subcategories.iteritems():
        # TODO TODO TODO: this place category handling is not correct; just temporary
        if v == category or (category == 'place' and (v == 'food')):
            result = result.union(deriveTypesFromSubcategories([k]))
    
    return result

def deriveTypesFromSubcategories(subcategories):
    result = set()

    if 'song' in subcategories:
        result.add('track')
    
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

def buildEntity(data=None, kind=None, mini=False):
    if data is not None:
        if 'schema_version' not in data:
            return upgradeEntityData(data)
        kind = data.pop('kind', kind)
    if mini:
        new = getEntityMiniObjectFromKind(kind)
    else:
        new = getEntityObjectFromKind(kind)
    if data is not None:
        return new().dataImport(data, overflow=True)
    return new()

def upgradeEntityData(entityData):
    # Just to be explicit..
    old     = entityData
    
    kind    = deriveKindFromSubcategory(old['subcategory'])
    types   = deriveTypesFromSubcategories([old['subcategory']])
    
    if kind == 'other' and ('coordinates' in old or 'address' in old):
        kind = PlaceEntity
    
    new     = getEntityObjectFromKind(kind)()
    
    try:
        seedTimestamp = ObjectId(old['entity_id']).generation_time.replace(tzinfo=None)
    except:
        seedTimestamp = datetime.utcnow()
    
    def setBasicGroup(source, target, oldName, newName=None, oldSuffix=None, newSuffix=None, additionalSuffixes=None, seed=True):
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
                setattr(target, newName, item)
            else:
                setattr(target, '%s_%s' % (newName, newSuffix), item)

            sourceName = 'format'
            if seed:
                sourceName = 'seed'

            if newName != 'tombstone':
                setattr(target, '%s_source' % newName, source.pop('%s_source' % oldName, sourceName))
            setattr(target, '%s_timestamp' % newName, source.pop('%s_timestamp' % oldName, seedTimestamp))

            if additionalSuffixes is not None:
                for s in additionalSuffixes:
                    t = source.pop('%s_%s' % (oldName, s), None)
                    if t is not None:
                        setattr(target, '%s_%s' % (newName, s), t)
    
    def setListGroup(source, target, oldName, newName=None, delimiter=',', wrapper=None, seed=True):
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
            setattr(target, newName, items)

            sourceName = 'format'
            if seed:
                sourceName = 'seed'

            setattr(target, '%s_source' % newName, source.pop('%s_source' % oldName, sourceName))
            setattr(target, '%s_timestamp' % newName, source.pop('%s_timestamp' % oldName, seedTimestamp))
    
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
    book                    = details.pop('book', {})
    netflix                 = sources.pop('netflix', {})
    
    # General
    new.schema_version      = 0
    new.entity_id           = old.pop('entity_id', None)
    new.title               = old.pop('title', None)
    
    # Images
    netflixImages = netflix.pop('images', {})
    oldImages = [
        old.pop('image', None),
        media.pop('artwork_url', None),
        netflixImages.pop('hd', None),
        netflixImages.pop('large', None),
    ]
    for oldImage in oldImages:
        if oldImage is not None:
            image = ImageSchema()
            size  = ImageSizeSchema()
            size.url = oldImage
            image.sizes = [ size ]
            new.images = [ image ]
            break
    if len(new.images) > 0:
        new.images_source = 'seed'
        new.images_timestamp = seedTimestamp
    
    setBasicGroup(old, new, 'desc')
    subcategory = old['subcategory']
    if subcategory == 'song':
        subcategory = 'track'
    new.types += (subcategory,)

    # Sources
    setBasicGroup(sources, new.sources, 'spotify', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new.sources, 'rdio', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new.sources, 'fandango', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources, new.sources, 'stamped', 'tombstone', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources.pop('tmdb', {}), new.sources, 'tmdb', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    setBasicGroup(sources.pop('factual', {}), new.sources, 'factual', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    # TODO: Add factual_crosswalk
    setBasicGroup(sources.pop('singleplatform', {}), new.sources, 'singleplatform', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    
    # Apple / iTunes
    setBasicGroup(sources, new.sources, 'itunes', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    if new.sources.itunes_id is None:
        apple = sources.pop('apple', {})
        setBasicGroup(apple, new.sources, 'aid', 'itunes', newSuffix='id')
        setBasicGroup(apple, new.sources, 'view_url', 'itunes', newSuffix='url')
    
    # Amazon
    setBasicGroup(sources, new.sources, 'amazon', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    if new.sources.amazon_id is None:
        amazon = sources.pop('amazon', {})
        setBasicGroup(amazon, new.sources, 'asin', 'amazon', newSuffix='id')
        setBasicGroup(amazon, new.sources, 'amazon_link', 'amazon', newSuffix='url')
    
    # Netflix
    if netflix:
        setBasicGroup(netflix, new.sources, 'nid', 'netflix', newSuffix='id')
        setBasicGroup(netflix, new.sources, 'nurl', 'netflix', newSuffix='url')

    # OpenTable
    setBasicGroup(sources, new.sources, 'opentable', oldSuffix='id', newSuffix='id', additionalSuffixes=['nickname', 'url'])
    if new.sources.opentable_id is None:
        setBasicGroup(sources.pop('openTable', {}), new.sources, 'rid', 'opentable', newSuffix='id', additionalSuffixes=['url'])
    
    # Google Places
    googleplaces = sources.pop('googlePlaces', {})
    setBasicGroup(googleplaces, new.sources, 'googleplaces', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
    if new.sources.googleplaces_id is None:
        setBasicGroup(googleplaces, new.sources, 'reference', 'googleplaces', newSuffix='id', additionalSuffixes=['url'])
    
    # User Generated
    userGenerated = sources.pop('userGenerated', {}).pop('generated_by', None)
    if userGenerated is not None:
        new.sources.user_generated_id = userGenerated
        if 'created' in timestamp:
            new.sources.user_generated_timestamp = timestamp['created']
        else:
            new.sources.user_generated_timestamp = seedTimestamp
        subtitle = old.pop('subtitle', None)
        if subtitle is not None:
            new.sources.user_generated_subtitle = subtitle
    
    # Contacts
    setBasicGroup(contact, new, 'phone')
    setBasicGroup(contact, new, 'site')
    setBasicGroup(contact, new, 'email')
    setBasicGroup(contact, new, 'fax')
    
    # Places
    if kind == 'place':
        coordinates = old.pop('coordinates', None)
        if coordinates is not None:
            new.coordinates = CoordinatesSchema().dataImport(coordinates)

        addressComponents = ['locality', 'postcode', 'region', 'street', 'street_ext']
        setBasicGroup(place, new, 'address', 'address', oldSuffix='country', newSuffix='country', additionalSuffixes=addressComponents, seed=False)


        setBasicGroup(place, new, 'address', 'formatted_address')
        if 'hours' in place:
            place['hours'] = HoursSchema().dataImport(place['hours'], overflow=True)
        setBasicGroup(place, new, 'hours', seed=False)
        setBasicGroup(restaurant, new, 'menu', seed=False)
        setBasicGroup(restaurant, new, 'price_range', seed=False)
        setBasicGroup(restaurant, new, 'alcohol_flag', seed=False)
        
        setListGroup(restaurant, new, 'cuisine', seed=False)
    
    # Artist
    if kind == 'person':
        songs = artist.pop('songs', [])
        itunesSource = False
        newSongs = []
        for song in songs:
            entityMini = MediaItemEntityMini()
            entityMini.title = song['song_name']
            entityMini.kind = 'media_item'
            entityMini.types = [ 'track' ]
            if 'id' in song and 'source' in song and song['source'] == 'itunes':
                itunesSource = True
                entityMini.sources.itunes_id = song['id']
                entityMini.sources.itunes_source = 'itunes'
                entityMini.sources.itunes_timestamp = song.pop('timestamp', seedTimestamp)
            newSongs.append(entityMini)
        if len(newSongs) > 0:
            new.tracks = newSongs
            sourceName = 'itunes' if itunesSource else 'format'
            new.tracks_source = artist.pop('songs_source', sourceName)
            new.tracks_timestamp = artist.pop('songs_timestamp', seedTimestamp)

        albums = artist.pop('albums', [])
        itunesSource = False
        newAlbums = []
        for item in albums:
            entityMini = MediaCollectionEntityMini()
            entityMini.title = item['album_name']
            if 'id' in item and 'source' in item and item['source'] == 'itunes':
                entityMini.sources.itunes_id = item['id']
                entityMini.sources.itunes_source = 'itunes'
                entityMini.sources.itunes_timestamp = item.pop('timestamp', seedTimestamp)
            newAlbums.append(entityMini)
        if len(newAlbums) > 0:
            new.albums = newAlbums
            sourceName = 'itunes' if itunesSource else 'format'
            new.albums_source = artist.pop('albums_source', sourceName)
            new.albums_timestamp = artist.pop('albums_timestamp', seedTimestamp)

        setListGroup(media, new, 'genre', 'genres', seed=False)
    
    # General Media
    if kind in ['media_collection', 'media_item']:

        setBasicGroup(media, new, 'track_length', 'length')
        setBasicGroup(media, new, 'mpaa_rating', seed=False)
        setBasicGroup(media, new, 'release_date')

        setListGroup(media, new, 'genre', 'genres', seed=False)
        setListGroup(media, new, 'artist_display_name', 'artists', wrapper=PersonEntityMini, seed=False)
        setListGroup(video, new, 'cast', 'cast', wrapper=PersonEntityMini, seed=False)
        setListGroup(video, new, 'director', 'directors', wrapper=PersonEntityMini, seed=False)
        setListGroup(video, new, 'network_name', 'networks', wrapper=PersonEntityMini, seed=False)

        originalReleaseDate = parseDateString(media.pop('original_release_date', None))
        if new.release_date is None and originalReleaseDate is not None:
            new.release_date = originalReleaseDate
            new.release_date_source = 'seed'
            new.release_date_timestamp = seedTimestamp
    
    # Book
    if 'book' in types:
        setBasicGroup(book, new, 'isbn')
        setBasicGroup(book, new, 'sku_number')
        setBasicGroup(book, new, 'num_pages', 'length', seed=False)

        setListGroup(book, new, 'author', 'authors', wrapper=PersonEntityMini, seed=False)
        setListGroup(book, new, 'publishers', 'publisher', wrapper=PersonEntityMini, seed=False)
    
    # Album
    if 'album' in types:
        songs = album.pop('tracks', [])
        newSongs = []
        for song in songs:
            entityMini = MediaItemEntityMini()
            entityMini.title = song
            newSongs.append(entityMini)
        if len(newSongs) > 0:
            new.tracks = newSongs
            new.tracks_source = album.pop('songs_source', 'format')
            new.tracks_timestamp = album.pop('songs_timestamp', seedTimestamp)
    
    # Track
    if 'track' in types:
        albumName = song.pop('album_name', media.pop('album_name', None))
        if albumName is not None:
            entityMini = MediaCollectionEntityMini()
            entityMini.title = albumName
            albumId = song.pop('song_album_id', None)
            if albumId is not None:
                entityMini.sources.itunes_id = albumId 
                entityMini.sources.itunes_source = 'seed'
                entityMini.sources.itunes_timestamp = seedTimestamp
            new.albums = [ entityMini ]
            new.albums_source = song.pop('album_name_source', 'format')
            new.albums_timestamp = song.pop('album_name_timestamp', seedTimestamp)
    
    # Apps
    if 'app' in types:
        setBasicGroup(media, new, 'release_date', seed=False)
        setListGroup(media, new, 'artist_display_name', 'authors', wrapper=PersonEntityMini, seed=False)

        screenshots = media.pop('screenshots', [])
        newScreenshots = []
        for screenshot in screenshots:
            imageSchema = ImageSchema()
            imageSizeSchema = ImageSizeSchema()
            imageSizeSchema.url = screenshot
            imageSchema.sizes = [ imageSizeSchema ]
            newScreenshots.append(imageSchema)
        if len(newScreenshots) > 0:
            new.screenshots = newScreenshots
            new.screenshots_source = media.pop('screenshots_source', 'format')
            new.screenshots_timestamp = media.pop('screenshots_timestamp', seedTimestamp)
    
    return new 

def fast_id_dedupe(entities, seen=None):
    """
        Returns a new list of entities with all obvious, id-based duplicates 
        removed (with lower indexed entities taking precedence over ones 
        appearing later in the input list).
        
        entities        - iterable of entities to dedupe
        seen (optional) - defaultdict(set) is a mapping of id keys to a set 
                          containing unique values seen so far for a given id.
    """
    
    if seen is None:
        seen = defaultdict(set)
    
    output = []
    for entity in entities:

        sources = entity.sources.dataExport()
        keys = [ k for k in sources if k.endswith('_id') ]
        keep = True
        
        # ensure that the same source id doesn't appear twice in the result set
        # (source ids are supposed to be unique)
        for key in keys:
            value = str(getattr(entity.sources, key))
            
            if value in seen[key]:
                keep = False
            else:
                seen[key].add(value)
        
        if keep:
            output.append(entity)
    
    return output

