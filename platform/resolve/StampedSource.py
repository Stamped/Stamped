#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'StampedSource', 'EntitySearchAll' ]

import Globals
from logs import report

try:
    import logs
    
    from Resolver                   import *
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import Entity
    from datetime                   import datetime
    from bson                       import ObjectId
except:
    report()
    raise


class _EntityObject(object):
    """
    Abstract superclass (mixin) for Entity based objects.

    Creates a deepcopy of the entity, accessible via the 'entity' attribute.
    """

    def __init__(self, entity):
        self.__entity = Entity()
        self.__entity.importData(entity.value)

    @property
    def entity(self):
        return self.__entity

    @lazyProperty
    def name(self):
        try:
            return self.entity['title']
        except Exception:
            return ''

    @lazyProperty
    def key(self):
        try:
            return self.entity['entity_id']
        except Exception:
            return ''

    @property 
    def source(self):
        return "stamped"

    def __repr__(self):
        return pformat( self.entity.value )


class EntityArtist(_EntityObject, ResolverArtist):
    """
    Entity artist wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverArtist.__init__(self)

    @lazyProperty
    def albums(self):
        try:
            return [ {'name' : album['album_name'] } for album in self.entity['albums'] ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        try:
            return [ {'name' : song['song_name'] } for song in self.entity['songs'] ]
        except Exception:
            return []


class EntityAlbum(_EntityObject, ResolverAlbum):
    """
    Entity album wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        try:
            return { 'name' : self.entity['artist_display_name'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def tracks(self):
        try:
            return [ {'name':entry.value} for entry in self.entity['tracks'] ]
        except Exception:
            return []


class EntityTrack(_EntityObject, ResolverTrack):
    """
    Entity track wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverTrack.__init__(self)

    @lazyProperty
    def artist(self):
        if self.entity['artist_display_name'] is not None:
            return {'name':self.entity['artist_display_name']}
        else:
            return {'name':''}

    @lazyProperty
    def album(self):
        if self.entity['album_name'] is not None:
            return {'name':self.entity['album_name']}
        else:
            return {'name':''}

    @lazyProperty
    def length(self):
        try:
            return float(self.entity['track_length'])
        except Exception:
            return -1


class EntityMovie(_EntityObject, ResolverMovie):
    """
    Entity movie wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverMovie.__init__(self)

    @lazyProperty 
    def cast(self):
        cast = self.entity['cast']
        if cast is not None:
            return [
                {
                    'name':entry.strip()
                }
                    for entry in cast.split(',')
            ]
        else:
            return []

    @lazyProperty 
    def director(self):
        name = self.entity['director']
        if name is not None:
            return { 'name': name }
        else:
            name = self.entity['artist_display_name']
            if name is not None:
                return { 'name': name }
        return { 'name':'' }

    @lazyProperty 
    def date(self):
        date = self.entity['release_date']
        if date is not None:
            return date
        else:
            date = self.entity['original_release_date']
            if date is not None:
                parsed_date = parseDateString(date)
                if parsed_date is None:
                    try:
                        year = int(date)
                        date = datetime(year,1,1)
                    except Exception:
                        date = None
                else:
                    date = parsed_date
        return date

    @lazyProperty 
    def length(self):
        value = self.entity['track_length']
        if value is not None:
            return float(value)
        else:
            return -1

    @lazyProperty 
    def rating(self):
        value = self.entity['mpaa_rating']
        if value is not None:
            return value
        else:
            return None


class EntityBook(_EntityObject, ResolverBook):
    """
    Entity book wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverBook.__init__(self)

    @lazyProperty
    def author(self):
        author = self.entity['author']
        if author is None:
            author = ''
        return {'name':author}

    @lazyProperty
    def publisher(self):
        publisher = self.entity['publisher']
        if publisher is None:
            publisher = ''
        return {'name':publisher}

    @lazyProperty
    def date(self):
        try:
            return parseDateString(self.entity['publish_date'])
        except Exception:
            return None

    @lazyProperty
    def length(self):
        try:
            return float(self.entity['num_pages'])
        except Exception:
            return -1

    @lazyProperty
    def isbn(self):
        return self.entity['isbn']

    @lazyProperty
    def eisbn(self):
        return None

class EntityPlace(_EntityObject, ResolverPlace):

    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverPlace.__init__(self)

    @lazyProperty
    def coordinates(self):
        try:
            return (self.entity['lat'], self.entity['lng'])
        except Exception:
            return None

    @lazyProperty
    def address(self):
        m = set(['street','street_ext','locality','region','postcode','country'])
        address = {}
        for k in m:
            actual = 'address_%s' % k
            if actual in self.entity:
                value = self.entity[actual]
                if value is not None and value != '':
                    address[k] = value
        return address


class EntitySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type


class StampedSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'stamped')

    @lazyProperty
    def __entityDB(self):
        import MongoStampedAPI
        api = MongoStampedAPI.MongoStampedAPI()
        return api._entityDB

    def artistFromEntity(self, entity):
        """
        ResolverArtist factory method for entities.

        This method may or may not return a simple EntityArtist or
        it could return a different implementation of ResolverArtist.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityArtist(entity)

    def albumFromEntity(self, entity):
        """
        ResolverAlbum factory method for entities.

        This method may or may not return a simple EntityAlbum or
        it could return a different implementation of ResolverAlbum.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityAlbum(entity)

    def trackFromEntity(self, entity):
        """
        ResolverTrack factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityTrack(entity)

    def movieFromEntity(self, entity):
        """
        ResolverMovie factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityMovie(entity)

    def bookFromEntity(self, entity):
        """
        """
        return EntityBook(entity)

    def placeFromEntity(self, entity):
        return EntityPlace(entity)

    def wrapperFromEntity(self, entity):
        """
        Generic ResolverObject factory method for entities.

        This method will create a type specific ResolverObject
        based on the type of the given entity.
        """
        sub = entity['subcategory']
        if sub == 'song':
            return self.trackFromEntity(entity)
        elif sub == 'album':
            return self.albumFromEntity(entity)
        elif sub == 'artist':
            return self.artistFromEntity(entity)
        elif sub == 'movie':
            return self.movieFromEntity(entity)
        elif sub == 'book':
            return self.bookFromEntity(entity)
        elif sub in set(['restaurant','bar','bakery','cafe','market','food','nightclub']):
            return self.placeFromEntity(entity)
        else:
            raise ValueError('Unrecognized subcategory %s for %s' % (sub, entity['title']))

    def matchSource(self, query):
        if query.type == 'artist':
            return self.artistSource(query)
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        elif query.type == 'movie':
            return self.movieSource(query)
        elif query.type == 'book':
            return self.bookSource(query)
        elif query.type == 'place':
            return self.placeSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        else:
            return self.emptySource

    def trackSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : trackSimplify( query.name ),
                }
                yield {
                    'details.media.artist_display_title' : query.artist['name'],
                }
                yield {
                    'details.song.album.name': query.album['name'],
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='song')

    def albumSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : albumSimplify( query.name ),
                }
                yield {
                    'details.media.artist_display_title' : query.artist['name'],
                } 
                yield {
                    '$or': [
                        { 'details.album.tracks': track['name'] }
                            for track in query.tracks
                    ]
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='album')

    def artistSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : artistSimplify( query.name ),
                }
                yield {
                    '$or': [
                        { 'details.artist.albums': {'$elemMatch':{ 'album_name': album['name'] } } }
                            for album in query.albums
                    ]
                }
                yield {
                    '$or': [
                        { 'details.artist.songs': {'$elemMatch':{ 'song_name': track['name'] } } }
                            for track in query.tracks
                    ]
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='artist')

    def movieSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : movieSimplify( query.name ),
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='movie')

    def bookSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : bookSimplify( query.name ),
                }
                yield {
                    'details.book.author' : query.author['name'],
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='book')

    def placeSource(self, query):
        def query_gen():
            try:
                or_clause = [
                    {'subcategory' : 'bar'},
                    {'subcategory' : 'restaurant'},
                ]
                yield {
                    'titlel' : query.name.lower(),
                    '$or' : or_clause,
                }
                yield {
                    'mangled_title' : bookSimplify( query.name ),
                    '$or' : or_clause,
                }
                yield {
                    'details.book.author' : query.author['name'],
                    '$or' : or_clause,
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query)

    def searchAllSource(self, query, timeout=None, types=None):
        def query_gen():
            try:
                # Exact match
                yield {
                    'titlel' : query.query_string.lower(),
                }

                words = query.query_string.lower().split()
                if len(words) == 1:
                    return

                # Pair prefix
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^%s %s( .*)?$" % (words[i], words[i+1])
                            }
                        }
                            for i in xrange(len(words) - 1)
                    ]
                }

                blacklist = set([
                    'the',
                    'a',
                    'an',
                ])

                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^%s( .*)?$" % (word)
                            }
                        }
                            for word in words if word not in blacklist
                    ]
                }

                # Pair regex
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^(.* )?%s %s( .*)?$" % (words[i], words[i+1])
                            }
                        }
                            for i in xrange(len(words) - 1)
                    ]
                }
                """
                blacklist = set([
                    'and',
                    'or',
                    'in',
                    'the',
                    'a',
                    'an',
                    'of',
                    'on',
                    'movie',
                ])

                # Word regex
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^(.* )?%s( .*)?$" % word
                            }
                        }
                            for word in simplify(query.query_string).split()
                                if word not in blacklist
                    ]
                }
                """
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, constructor_wrapper=EntitySearchAll)

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich(self.sourceName, self.sourceName, entity):
            try:
                query = self.wrapperFromEntity(entity)
                timestamps[self.sourceName] = controller.now
                mins = None
                if query.type == 'artist':
                    mins = {
                        'name':.1,
                        'albums':.1,
                        'tracks':-1,
                        'total':-1,
                    }
                results = self.resolver.resolve(query, self.matchSource(query), mins=mins)
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        entity[self.idField] = best[1].key
                        if self.urlField is not None and best[1].url is not None:
                            entity[self.urlField] = best[1].url
            except ValueError:
                pass
        return True

    def __id_query(self, mongo_query):
        import pymongo
        #print(pformat(mongo_query))
        logs.info(mongo_query)
        return list(self.__entityDB._collection.find(mongo_query, fields=['_id'] ).sort('_id',pymongo.ASCENDING), limit=1000)

    def __querySource(self, query_gen, query_obj, constructor_wrapper=None, **kwargs):
        def gen():
            try:
                id_set = set()
                for query in query_gen:
                    for k,v in kwargs.items():
                        query[k] = v
                    
                    and_list = query.setdefault('$and',[])
                    and_list.append( {
                        '$or' : [
                            {'sources.stamped_id' : { '$exists':False }},
                            {'sources.stamped_id' : None},
                        ]
                    } )
                    if query_obj.source == 'stamped' and query_obj.key != '':
                        query['_id'] = { '$lt' : ObjectId(query_obj.key) }
                    matches = self.__id_query(query )
                    logs.info('Found %d matches for query: %20s' % (len(matches), str(matches)))
                    #print(matches)
                    for match in matches:
                        entity_id = match['_id']
                        if entity_id not in id_set:
                            yield entity_id
                            id_set.add(entity_id)
            except GeneratorExit:
                pass
        generator = gen()
        
        def constructor(entity_id):
            return self.wrapperFromEntity(
                self.__entityDB.getEntity(
                    self.__entityDB._getStringFromObjectId(entity_id)
                )
            )
        
        if constructor_wrapper is not None:
            return self.generatorSource(generator, lambda x: constructor_wrapper(constructor(x)), unique=True, tolerant=True)
        else:
            return self.generatorSource(generator, constructor=constructor, unique=True, tolerant=True)

    @property
    def urlField(self):
        return None

if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')

