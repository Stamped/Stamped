#!/usr/bin/python

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
        else:
            return self.emptySource

    def trackSource(self, query):
        tracks = list(self.__entityDB._collection.find({
            'subcategory':'song',
            '$or': [
                { 'title':query.name },
                { 'mangled_title':trackSimplify(query.name) },
                { 'details.media.artist_display_title':query.artist['name'] },
                { 'details.song.album.name': query.album['name'] },
            ]
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ self.trackFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) ) ) for entry in result ]
        return source
    
    def albumSource(self, query):
        options = [
            { 'title':query.name },
            { 'mangled_title':albumSimplify(query.name) },
            { 'details.media.artist_display_title':query.artist['name'] },
        ]
        for track in query.tracks:
            options.append( {
                'details.album.tracks': track['name'],
            })
        albums = list(self.__entityDB._collection.find({
            'subcategory':'album',
            '$or': options,
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ self.albumFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) )  ) for entry in result ]
        return source


    def artistSource(self, query):
        options = [
            { 'title':query.name },
            { 'mangled_title':artistSimplify(query.name) },
        ]
        for track in query.tracks:
            options.append( {
                'details.artist.songs': track['name'],
            })
        for album in query.albums:
            options.append( {
                'details.artist.albums': album['name'],
            })
        artists = list(self.__entityDB._collection.find({
            'subcategory':'artist',
            '$or': options,
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ self.artistFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) )  ) for entry in result ]
        return source

    def movieSource(self, query):
        options = [
            { 'title':query.name },
        ]
        artists = list(self.__entityDB._collection.find({
            'subcategory':'movie',
            '$or': options,
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ self.movieFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) )  ) for entry in result ]
        return source

if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')
