#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'StampedSource' ]

import Globals
from logs import report

try:
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import *
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import Entity
    from datetime                   import datetime
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
        return self.entity['title']

    @lazyProperty
    def key(self):
        return self.entity['entity_id']

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
        return [ {'name':album['album_name']} for album in self.entity['albums'] ]

    @lazyProperty
    def tracks(self):
        return [ {'name':song['song_name']} for song in self.entity['songs'] ]


class EntityAlbum(_EntityObject, ResolverAlbum):
    """
    Entity album wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        return { 'name' : self.entity['artist_display_name'] }

    @lazyProperty
    def tracks(self):
        return [ {'name':entry.value} for entry in self.entity['tracks'] ]


class EntityTrack(_EntityObject, ResolverTrack):
    """
    Entity track wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverTrack.__init__(self)

    @lazyProperty
    def artist(self):
        return {'name':self.entity['artist_display_name']}

    @lazyProperty
    def album(self):
        return {'name':self.entity['album_name']}

    @lazyProperty
    def length(self):
        return float(self.entity['track_length'])



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
        else:
            return self.emptySource

    def trackSource(self, query):
        def query_gen():
            try:
                yield {
                    'title' : query.name,
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
        return self.__querySource(query_gen(), subcategory='song')

    def albumSource(self, query):
        def query_gen():
            try:
                yield {
                    'title' : query.name,
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
        return self.__querySource(query_gen(), subcategory='album')

    def artistSource(self, query):
        def query_gen():
            try:
                yield {
                    'title' : query.name,
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
        return self.__querySource(query_gen(), subcategory='artist')

    def movieSource(self, query):
        def query_gen():
            try:
                yield {
                    'title' : query.name,
                }
                yield {
                    'mangled_title' : movieSimplify( query.name ),
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), subcategory='movie')

    def bookSource(self, query):
        def query_gen():
            try:
                yield {
                    'title' : query.name,
                }
                yield {
                    'mangled_title' : bookSimplify( query.name ),
                }
                yield {
                    'details.book.author' : query.author['name'],
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), subcategory='book')

    def __id_query(self, mongo_query):
        return list(self.__entityDB._collection.find(mongo_query, {'_id':1} ))

    def __querySource(self, query_gen, **kwargs):
        def gen():
            try:
                id_set = set()
                for query in query_gen:
                    for k,v in kwargs.items():
                        query[k] = v
                    matches = self.__id_query(query )
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
        return self.generatorSource(generator, constructor)


if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')
