#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs       import report

try:
    from datetime                       import datetime
    from utils                          import lazyProperty

    from Schemas                        import *
    from Entity                         import setFields, isEqual, getSimplifiedTitle

    from AMongoCollection               import AMongoCollection
    from MongoMenuCollection            import MongoMenuCollection
    from AEntityDB                      import AEntityDB
    from difflib                        import SequenceMatcher
    from ADecorationDB                  import ADecorationDB
    from errors                         import StampedUnavailableError
    from logs                           import log
except:
    report()
    raise

subcategoryData = {
    # Subcategory           Category        Kind                        Type
    'restaurant'        : ( 'place',        [ 'place' ],                [ 'restaurant' ] ),
    'bar'               : ( 'place',        [ 'place' ],                [ 'bar' ] ),
    'bakery'            : ( 'place',        [ 'place' ],                [ 'bakery' ] ),
    'cafe'              : ( 'place',        [ 'place' ],                [ 'cafe' ] ),
    'market'            : ( 'place',        [ 'place' ],                [ 'market' ] ),
    'food'              : ( 'place',        [ 'place' ],                [ 'food' ] ),
    'night_club'        : ( 'place',        [ 'place' ],                [ 'night_club' ] ),
    'amusement_park'    : ( 'place',        [ 'place' ],                [ 'amusement_park' ] ),
    'aquarium'          : ( 'place',        [ 'place' ],                [ 'aquarium' ] ),
    'art_gallery'       : ( 'place',        [ 'place' ],                [ 'art_gallery' ] ),
    'beauty_salon'      : ( 'place',        [ 'place' ],                [ 'beauty_salon' ] ),
    'book_store'        : ( 'place',        [ 'place' ],                [ 'book_store' ] ),
    'bowling_alley'     : ( 'place',        [ 'place' ],                [ 'bowling_alley' ] ),
    'campground'        : ( 'place',        [ 'place' ],                [ 'campground' ] ),
    'casino'            : ( 'place',        [ 'place' ],                [ 'casino' ] ),
    'clothing_store'    : ( 'place',        [ 'place' ],                [ 'clothing_store' ] ),
    'department_store'  : ( 'place',        [ 'place' ],                [ 'department_store' ] ),
    'establishment'     : ( 'place',        [ 'place' ],                [ 'establishment' ] ),
    'florist'           : ( 'place',        [ 'place' ],                [ 'florist' ] ),
    'gym'               : ( 'place',        [ 'place' ],                [ 'gym' ] ),
    'home_goods_store'  : ( 'place',        [ 'place' ],                [ 'home_goods_store' ] ),
    'jewelry_store'     : ( 'place',        [ 'place' ],                [ 'jewelry_store' ] ),
    'library'           : ( 'place',        [ 'place' ],                [ 'library' ] ),
    'liquor_store'      : ( 'place',        [ 'place' ],                [ 'liquor_store' ] ),
    'lodging'           : ( 'place',        [ 'place' ],                [ 'lodging' ] ),
    'movie_theater'     : ( 'place',        [ 'place' ],                [ 'movie_theater' ] ),
    'museum'            : ( 'place',        [ 'place' ],                [ 'museum' ] ),
    'park'              : ( 'place',        [ 'place' ],                [ 'park' ] ),
    'school'            : ( 'place',        [ 'place' ],                [ 'school' ] ),
    'shoe_store'        : ( 'place',        [ 'place' ],                [ 'shoe_store' ] ),
    'shopping_mall'     : ( 'place',        [ 'place' ],                [ 'shopping_mall' ] ),
    'spa'               : ( 'place',        [ 'place' ],                [ 'spa' ] ),
    'stadium'           : ( 'place',        [ 'place' ],                [ 'stadium' ] ),
    'store'             : ( 'place',        [ 'place' ],                [ 'store' ] ),
    'university'        : ( 'place',        [ 'place' ],                [ 'university' ] ),
    'zoo'               : ( 'place',        [ 'place' ],                [ 'zoo' ] ),

    # Subcategory           Category        Kind                        Type
    'book'              : ( 'book',         [ 'media_item' ],           [ 'book' ] ),

    # Subcategory           Category        Kind                        Type
    'movie'             : ( 'film',         [ 'media_item' ],           [ 'movie' ] ),
    'tv'                : ( 'film',         [ 'media_collection' ],     [ 'tv' ] ),

    # Subcategory           Category        Kind                        Type
    'artist'            : ( 'music',        [ 'person' ],               [ 'artist' ] ),
    'album'             : ( 'music',        [ 'media_collection' ],     [ 'album' ] ),
    'track'             : ( 'music',        [ 'media_item' ],           [ 'track' ] ),

    # Subcategory           Category        Kind                        Type
    'app'               : ( 'app',          [ 'software' ],             [ 'app' ] ),
    
    # Subcategory           Category        Kind                        Type
    'other'             : ( 'other',        [ 'other' ],                [ 'other' ] ),
    'video_game'        : ( 'other',        [ 'software' ],             [ 'video_game' ] ),
}

class MongoEntityCollection(AMongoCollection, AEntityDB, ADecorationDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection=collection, primary_key='entity_id', obj=Entity)
        AEntityDB.__init__(self)

    def _downgradeAccountFromTwoPointOh(data):
        if 'schema_version' not in data:
            return api._entityDB._convertFromMongo(data)

        # Basics
        entity = Entity()
        entity.entity_id = str(data['_id'])
        entity.title = data['title']
        if 'desc' in data:
            entity.desc = data['desc']

        # Timestamp
        timestamp = data.pop('timestamp', {})
        if 'created' in timestamp:
            entity.timestamp.created = timestamp['created']
        if 'modified' in timestamp:
            entity.timestamp.modified = timestamp['modified']

        # Category / Subcategory
        kind = data.pop('kind')
        types = data.pop('types', ['other'])
        subcategory = types[0]
        assert subcategory is not None
        entity.subcategory = subcategory

        # Image
        if 'images' in data and len(data['images']) > 0:
            entity.image = data['images'][0]['sizes'][0]['url']

        # Contact
        if 'site' in data:
            entity.site = data['site']
        if 'phone' in data:
            entity.phone = data['phone']

        # Sources
        sources = data.pop('sources', {})

        if 'user_generated_id' in sources:
            entity.generated_by = sources['user_generated_id']
            entity.user_id = sources['user_generated_id']
        if 'user_generated_subtitle' in sources:
            entity.subtitle = sources['user_generated_subtitle']

        if 'itunes_id' in sources:
            entity.sources.apple.aid = sources['itunes_id']
        if 'itunes_url' in sources:
            entity.sources.apple.view_url = sources['itunes_url']
        if 'itunes_preview' in sources:
            entity.preview_url = sources['itunes_preview']

        if 'amazon_id' in sources:
            entity.asin = sources['amazon_id']
        if 'amazon_url' in sources:
            entity.amazon_link = sources['amazon_url']

        if 'opentable_id' in sources:
            entity.rid = sources['opentable_id']

        if 'fandango_id' in sources:
            entity.fid = sources['fandango_id']
        if 'fandango_url' in sources:
            entity.f_url = sources['fandango_url']

        if 'singleplatform_id' in sources:
            entity.singleplatform_id = sources['singleplatform_id']

        if 'factual_id' in sources:
            entity.factual_id = sources['factual_id']
        if 'factual_crosswalk' in sources:
            entity.factual_crosswalk = sources['factual_crosswalk']

        if 'tmdb_id' in sources:
            entity.tmdb_id = sources['tmdb_id']

        if 'thetvdb_id' in sources:
            entity.thetvdb_id = sources['thetvdb_id']

        if 'googleplaces_id' in sources:
            entity.gid = sources['googleplaces_id']
            entity.googleplaces_id = sources['googleplaces_id']
        if 'googleplaces_reference' in sources:
            entity.reference = sources['googleplaces_reference']
        if 'googleplaces_url' in sources:
            entity.gurl = sources['googleplaces_url']


        # Kind: Place
        if kind == 'place':

            # Coordinates
            coordinates = data.pop('coordinates', {})
            if 'lat' in coordinates and 'lng' in coordinates:
                entity.lat = coordinates['lat']
                entity.lng = coordinates['lng']

            # Address
            if 'formatted_address' in data:
                entity.address = data['formatted_address']

            components = []
            
            if 'address_country' in data:
                schema = AddressComponentSchema()
                schema.types.append('country')
                schema.short_name = data['address_country']
                components.append(schema)
            
            if 'address_locality' in data:
                schema = AddressComponentSchema()
                schema.types.append('locality')
                schema.short_name = data['address_locality']
                components.append(schema)

            if 'address_postcode' in data:
                schema = AddressComponentSchema()
                schema.types.append('postal_code')
                schema.short_name = data['address_postcode']
                components.append(schema)

            if 'address_region' in data:
                schema = AddressComponentSchema()
                schema.types.append('administrative_area_level_1')
                schema.short_name = data['address_region']
                components.append(schema)

            if 'address_street' in data:
                schema = AddressComponentSchema()
                schema.types.append('street_address')
                schema.short_name = data['address_street']
                components.append(schema)

            if len(components) > 0:
                entity.address_components = components

            # Cuisine
            if 'cuisine' in data:
                entity.cuisine = '; '.join(data['cuisine'])

        # Kind: Person
        if kind == 'person':

            # Genres
            if 'genres' in data:
                entity.genre = '; '.join(data['genres'])

            # Tracks
            if 'tracks' in data and len(data['tracks']) > 0:
                entity.songs = map(lambda x: ArtistSongsSchema({'song_name': x['title']}), data['tracks'])
                entity.tracks = map(lambda x: x['title'], data['tracks'])

            # Album
            if 'albums' in data and len(data['albums']) > 0:
                entity.albums = map(lambda x: ArtistAlbumsSchema({'album_name': x['title']}), data['albums'])

        # Kind: Basic Media 
        if kind == 'media_item' or kind == 'media_collection':

            # Release date
            if 'release_date' in data:
                entity.release_date = data['release_date']
                entity.original_release_date = data['release_date'].isoformat()[:10]

            # Genres
            if 'genres' in data:
                entity.genre = '; '.join(data['genres'])
                
            # Artists
            if 'artists' in data and len(data['artists']) > 0:
                entity.artist_display_name = data['artists'][0]['title']
                
            # Authors
            if 'authors' in data and len(data['authors']) > 0:
                entity.author = data['authors'][0]['title']
                
            # Directors
            if 'directors' in data and len(data['directors']) > 0:
                entity.director = data['directors'][0]['title']
                
            # Cast
            if 'cast' in data and len(data['cast']) > 0:
                entity.cast = ', '.join(map(lambda x: x['title'], data['cast']))
                
            # Publishers
            if 'publishers' in data and len(data['publishers']) > 0:
                entity.publisher = data['publishers'][0]['title']
                
            # Networks
            if 'networks' in data and len(data['networks']) > 0:
                entity.network_name = data['networks'][0]['title']

            # Length
            if 'length' in data:
                if subcategory == 'book':
                    entity.num_pages = data['length']
                else:
                    entity.track_length = data['length']

            # MPAA Rating
            if 'mpaa_rating' in data:
                entity.mpaa_rating = data['mpaa_rating']

        # Kind: Media Item
        if kind == 'media_item':

            # Album
            if 'albums' in data and len(data['albums']) > 0:
                entity.album_name = data['albums'][0]['title']

            # ISBN
            if 'isbn' in data:
                entity.isbn = data['isbn']

        # Kind: Media Collection
        if kind == 'media_collection':

            # Tracks
            if 'tracks' in data and len(data['tracks']) > 0:
                entity.songs = map(lambda x: ArtistSongsSchema({'song_name': x['title']}), data['tracks'])
                entity.tracks = map(lambda x: x['title'], data['tracks'])

        # Kind: Software
        if kind == 'software':

            # Genres
            if 'genres' in data:
                entity.genre = '; '.join(data['genres'])

            # Release date
            if 'release_date' in data:
                entity.release_date = data['release_date']
                entity.original_release_date = data['release_date'].isoformat()[:10]

        # Kind: Other
        if kind == 'other':
            pass

        # pprint(entity.value)
        # print '-'*40

        return entity
    
    def _convertFromMongo(self, document):
        document = self._downgradeAccountFromTwoPointOh(document)

        entity = AMongoCollection._convertFromMongo(self, document)
        if entity is not None and entity.titlel is None:
            entity.titlel = getSimplifiedTitle(entity.title)
        
        return entity

    ### PUBLIC
    
    def addEntity(self, entity):
        if entity.titlel is None:
            entity.titlel = getSimplifiedTitle(entity.title)
        
        return self._addObject(entity)
    
    def getEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document   = self._getMongoDocumentFromId(documentId)
        
        return self._convertFromMongo(document)
    
    def getEntities(self, entityIds):
        documentIds = []
        for entityId in entityIds:
            documentIds.append(self._getObjectIdFromString(entityId))
        data = self._getMongoDocumentsFromIds(documentIds)
        
        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result
    
    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        
        return self._convertFromMongo(document)
    
    def removeEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)
    
    def removeCustomEntity(self, entityId, userId):
        try:
            query = {'_id': self._getObjectIdFromString(entityId), \
                        'sources.userGenerated.user_id': userId}
            self._collection.remove(query)
            return True
        except:
            logs.warning("Cannot remove document")
            raise Exception
    
    def addEntities(self, entities):
        for entity in entities:
            if entity.titlel is None:
                entity.titlel = getSimplifiedTitle(entity.title)
        
        return self._addObjects(entities)

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)
        
