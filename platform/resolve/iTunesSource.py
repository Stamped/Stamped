#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'iTunesSource', 'iTunesArtist', 'iTunesAlbum', 'iTunesTrack', 'iTunesMovie' ]

import Globals
from logs import report

try:
    from libs.iTunes                import globaliTunes
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pformat
    from Resolver                   import *
    from libs.LibUtils              import parseDateString
except:
    report()
    raise

class _iTunesObject(object):
    """
    Abstract superclass (mixin) for iTunes objects.

    _iTunesObjects may be instantiated with either their iTunes data or their id.
    If both are provided, they must match.

    Attributes:

    data - the type specific iTunes data for the object.
    itunes - an instance of iTunes (API wrapper)
    """

    def __init__(self, itunes_id=None, data=None, itunes=None):
        if itunes is None:
            itunes = globaliTunes()
        self.__itunes = itunes
        if data == None:
            self.__data = itunes.method('lookup',id=itunes_id)['results'][0]
        else:
            self.__data = data
            if itunes_id is not None and itunes_id != self.__data['artistId']:
                raise ValueError('data does not match id')

    @property
    def data(self):
        return self.__data

    @property 
    def itunes(self):
        return self.__itunes

    @property 
    def source(self):
        return "itunes"

    def __repr__(self):
        return pformat( self.data )


class iTunesArtist(_iTunesObject, ResolverArtist):
    """
    iTunes artist wrapper
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverArtist.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['artistName']

    @lazyProperty
    def key(self):
        return self.data['artistId']

    @lazyProperty
    def albums(self):
        results = self.itunes.method('lookup',id=self.key,entity='album')['results']
        return [
            {
                'name'  : album['collectionName'],
                'key'   : str(album['collectionId']),
            }
                for album in results if album.pop('collectionType',None) == 'Album' ]

    @lazyProperty
    def tracks(self):
        results = self.itunes.method('lookup',id=self.key,entity='song')['results']
        return [
            {
                'name':track['trackName'],
                'key':track['trackId'],
            }
                for track in results if track.pop('wrapperType',None) == 'track'
        ]

class iTunesAlbum(_iTunesObject, ResolverAlbum):
    """
    iTunes album wrapper
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverAlbum.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['collectionName']

    @lazyProperty
    def key(self):
        return self.data['collectionId']

    @lazyProperty
    def artist(self):
        return {'name' : self.data['artistName'] }

    @lazyProperty
    def tracks(self):
        results = self.itunes.method('lookup', id=self.key, entity='song')['results']
        return [
            {
                'name':track['trackName'],
            }
                for track in results if track.pop('wrapperType',None) == 'track' 
        ]


class iTunesTrack(_iTunesObject, ResolverTrack):
    """
    iTunes track wrapper
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverTrack.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['trackName']

    @lazyProperty
    def key(self):
        return self.data['trackId']

    @lazyProperty
    def artist(self):
        try:
            return {'name' : self.data['artistName'] }
        except:
            return {'name' : ''}

    @lazyProperty
    def album(self):
        try:
            return {'name' : self.data['collectionName'] }
        except Exception:
            return {'name' : ''}

    @lazyProperty
    def length(self):
        return float(self.data['trackTimeMillis']) / 1000

class iTunesMovie(_iTunesObject, ResolverMovie):
    """
    iTunes movie wrapper
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMovie.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['trackName']

    @lazyProperty
    def key(self):
        return self.data['trackId']

    @lazyProperty
    def cast(self):
        #TODO try to improve with scraping
        return []

    @lazyProperty
    def director(self):
        try:
            return {
                'name':self.data['artistName'],
            }
        except KeyError:
            return { 'name':'' }

    @lazyProperty
    def date(self):
        try:
            return parseDateString(self.data['releaseDate'])
        except KeyError:
            return None

    @lazyProperty
    def length(self):
        try:
            return self.data['trackTimeMillis'] / 1000
        except Exception:
            return -1

    @lazyProperty
    def rating(self):
        try:
            return self.data['contentAdvisoryRating']
        except KeyError:
            return None

    @lazyProperty 
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except KeyError:
            return []

    @lazyProperty
    def desc(self):
        try:
            return self.data['longDescription']
        except KeyError:
            return None

class iTunesSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'itunes',
            'mpaa_rating',
            'genre',
            'desc',
            'albums',
            'songs',
        )

    @lazyProperty
    def __itunes(self):
        return globaliTunes()

    def __repopulateAlbums(self, entity, artist, controller):
        new_albums = [
            {
                'album_name'    : album['name'],
                'source'        : self.sourceName,
                'id'            : album['key'],
                'timestamp'     : controller.now,
                'album_mangled' : albumSimplify(album['name']),
            }
                for album in artist.albums
        ]
        entity['albums'] = new_albums

    def __repopulateSongs(self, entity, artist, controller):
        new_songs = [
            {
                'song_name'    : track['name'],
                'source'        : self.sourceName,
                'id'            : track['key'],
                'timestamp'     : controller.now,
                'song_mangled' : trackSimplify(track['name']),
            }
                for track in artist.tracks
        ]
        entity['songs'] = new_songs

    def enrichEntity(self, entity, controller, decorations, timestamps):
        GenericSource.enrichEntity(self, entity, controller, decorations, timestamps)
        itunes_id = entity['itunes_id']
        if itunes_id != None:
            if entity['subcategory'] == 'movie':
                movie = iTunesMovie(itunes_id)
                if movie.rating is not None:
                    entity['mpaa_rating'] = movie.rating
                if len(movie.genres) > 0:
                    entity['genre'] = movie.genres[0]
                if movie.desc is not None:
                    entity['desc'] = movie.desc
            if entity['subcategory'] == 'artist':
                artist = iTunesArtist(itunes_id)
                aid = entity['aid']
                if aid == itunes_id:
                    self.__repopulateAlbums(entity, artist, controller) 
                    self.__repopulateSongs(entity, artist, controller)
        return True

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
        tracks = self.__itunes.method('search',term=query.name, entity='song', attribute='allTrackTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ iTunesTrack( entry['trackId'] ) for entry in result ]
        return source

    
    def albumSource(self, query):
        albums = self.__itunes.method('search',term=query.name, entity='album', attribute='albumTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ iTunesAlbum( entry['collectionId'] ) for entry in result ]
        return source


    def artistSource(self, query):
        artists = self.__itunes.method('search',term=query.name, entity='allArtist', attribute='allArtistTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ iTunesArtist( entry['artistId'] ) for entry in result ]
        return source


    def movieSource(self, query):
        movies = self.__itunes.method('search',term=query.name, entity='movie', attribute='movieTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(movies):
                result = movies[start:start+count]
            elif start < len(movies):
                result = movies[start:]
            else:
                result = []
            return [ iTunesMovie( entry['trackId'] ) for entry in result ]
        return source

if __name__ == '__main__':
    demo(iTunesSource(), 'Katy Perry')
