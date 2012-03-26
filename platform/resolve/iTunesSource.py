#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'iTunesSource', 'iTunesArtist', 'iTunesAlbum', 'iTunesTrack', 'iTunesMovie', 'iTunesBook', 'iTunesSearchAll' ]

import Globals
from logs import report

try:
    from libs.iTunes                import globaliTunes
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    import logs
    from pprint                     import pformat
    from Resolver                   import *
    from libs.LibUtils              import parseDateString
    from StampedSource              import StampedSource
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
        self.__data = data
        self.__itunes_id = itunes_id

    @lazyProperty
    def data(self):
        if self.__data == None:
            if self.type == 'album' or self.type == 'artist':
                entity_field = 'song'
                if self.type == 'artist':
                    entity_field = 'album,song'
                results = self.itunes.method('lookup', id=self.__itunes_id, entity=entity_field)['results']
                m = {
                    'tracks':[],
                    'albums':[],
                    'artists':[]
                }
                for result in results:
                    k = None
                    if 'wrapperType' in result:
                        t = result['wrapperType']
                        if t == 'track' and result['kind'] == 'song':
                            k = 'tracks'
                        elif t == 'collection' and result['collectionType'] == 'Album':
                            k = 'albums'
                        elif t == 'artist' and result['artistType'] == 'Artist':
                            k = 'artists'
                    if k is not None:
                        m[k].append(result)
                if self.type == 'artist':
                    data = m['artists'][0]
                    data['albums'] = m['albums']
                    data['tracks'] = m['tracks']
                    return data
                else:
                    data = m['albums'][0]
                    data['tracks'] = m['tracks']
                    return data
            else:
                return self.itunes.method('lookup', id=self.__itunes_id)['results'][0]
        else:
            return self.__data

    @property 
    def itunes(self):
        return self.__itunes

    @property 
    def source(self):
        return "itunes"

    @lazyProperty
    def image(self):
        try:
            return self.data['artworkUrl100']
        except:
            return ''

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
    def url(self):
        try:
            return self.data['artistLinkUrl']
        except Exception:
            return None

    @lazyProperty
    def key(self):
        return self.data['artistId']

    @lazyProperty
    def albums(self):
        results = []
        if 'albums' in self.data:
            results = self.data['albums']
        else:
            results = self.itunes.method('lookup',id=self.key,entity='album')['results']
        return [
            {
                'name'  : album['collectionName'],
                'key'   : str(album['collectionId']),
                'data'  : album,
            }
                for album in results if album.pop('collectionType',None) == 'Album' ]

    @lazyProperty
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        results = []
        if 'tracks' in self.data:
            results = self.data['tracks']
        else:
            results = self.itunes.method('lookup',id=self.key,entity='song')['results']
        return [
            {
                'name':track['trackName'],
                'key':track['trackId'],
                'data':track,
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
    def url(self):
        try:
            return self.data['albumViewUrl']
        except Exception:
            return None

    @lazyProperty
    def key(self):
        return self.data['collectionId']

    @lazyProperty
    def artist(self):
        return {'name' : self.data['artistName'] }

    @lazyProperty
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        results = []
        if 'tracks' in self.data:
            results = self.data['tracks']
        else:
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
    def url(self):
        try:
            return self.data['trackViewUrl']
        except Exception:
            return None

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
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except Exception:
            return []

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
    def url(self):
        try:
            return self.data['trackViewUrl']
        except Exception:
            return None

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
    def description(self):
        try:
            return self.data['longDescription']
        except KeyError:
            return ''


class iTunesTVShow(_iTunesObject, ResolverTVShow):
    """
    iTunes tv show wrapper
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverTVShow.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['artistName']

    @lazyProperty
    def url(self):
        try:
            return self.data['artistLinkUrl']
        except Exception:
            return None

    @lazyProperty
    def key(self):
        return self.data['artistId']

    @lazyProperty
    def cast(self):
        #TODO try to improve with scraping
        return []

    @lazyProperty
    def director(self):
        return { 'name':'' }

    @lazyProperty
    def date(self):
        return None

    @lazyProperty
    def seasons(self):
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
    def description(self):
        try:
            return self.data['longDescription']
        except KeyError:
            return ''

    @property
    def subcategory(self):
        return 'tv'

class iTunesBook(_iTunesObject, ResolverBook):

    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverBook.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['trackName']

    @lazyProperty
    def url(self):
        try:
            return self.data['trackViewUrl']
        except Exception:
            return None

    @lazyProperty
    def key(self):
        return self.data['trackId']

    @lazyProperty
    def author(self):
        try:
            return {
                'name':self.data['artistName']
            }
        except Exception:
            return { 'name':'' }

    @lazyProperty
    def publisher(self):
        return {'name':''}

    @property
    def date(self):
        try:
            return parseDateString(self.data['releaseDate'])
        except Exception:
            return None

    @property
    def length(self):
        return -1

    @property
    def isbn(self):
        return None

    @property
    def eisbn(self):
        return None

    @property
    def sku(self):
        return None

class iTunesApp(_iTunesObject, ResolverApp):

    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverApp.__init__(self)

    @lazyProperty
    def name(self):
        return self.data['trackName']

    @lazyProperty
    def url(self):
        try:
            return self.data['sellerUrl']
        except Exception:
            return None

    @lazyProperty
    def key(self):
        return self.data['trackId']

    @lazyProperty
    def publisher(self):
        try:
            return {
                'name':self.data['sellerName']
            }
        except Exception:
            return { 'name':'' }

    @property
    def date(self):
        try:
            return parseDateString(self.data['releaseDate'])
        except Exception:
            return None

    @lazyProperty 
    def genres(self):
        try:
            if 'genres' in self.data:
                return self.data['genres']
            return [ self.data['primaryGenreName'] ]
        except KeyError:
            return []

    @lazyProperty
    def description(self):
        try:
            return self.data['description']
        except KeyError:
            return ''

    @lazyProperty
    def screenshots(self):
        try:
            return self.data['screenshotUrls']
        except:
            return []

    @lazyProperty 
    def image(self):
        try:
            return self.data['artworkUrl512']
        except:
            return ''

class iTunesSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type


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

    @lazyProperty
    def __stamped(self):
        return StampedSource()

    @lazyProperty
    def __resolver(self):
        return Resolver()

    def wrapperFromKey(self, key, type=None):
        return self.wrapperFromId(key)

    def wrapperFromId(self, itunes_id):
        try:
            data = self.__itunes.method('lookup',id=itunes_id)['results'][0]
            if data['wrapperType'] == 'track':
                if data['kind'].find('movie') != -1:
                    return iTunesMovie(data=data)
                elif data['kind'] == 'song':
                    return iTunesTrack(data=data)
            elif data['wrapperType'] == 'collection' and data['collectionType'] == 'Album':
                return iTunesAlbum(data=data)
            elif data['wrapperType'] == 'artist':
                if data['artistType'] == 'TV Show':
                    return iTunesTVShow(data=data)
                return iTunesArtist(data=data)
            elif value['wrapperType'] == 'software':
                return iTunesApp(data=data)
            else:
                pass
        except KeyError:
            pass
        return None

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithWrapper(self, wrapper, entity, controller, decorations, timestamps)
        entity.itunes_id = wrapper.key
        return True

    def enrichEntity(self, entity, controller, decorations, timestamps):
        GenericSource.enrichEntity(self, entity, controller, decorations, timestamps)
        itunes_id = entity['itunes_id']
        if itunes_id != None:
            obj = None
            if entity['subcategory'] == 'movie':
                obj = iTunesMovie(itunes_id)
            elif entity['subcategory'] == 'artist':
                obj = iTunesArtist(itunes_id)
            elif entity['subcategory'] == 'album':
                obj = iTunesAlbum(itunes_id)
            elif entity['subcategory'] == 'song':
                obj = iTunesTrack(itunes_id)
            elif entity['subcategory'] == 'book':
                obj = iTunesBook(itunes_id)
            elif entity['subcategory'] == 'tv':
                obj = iTunesTVShow(itunes_id)
            elif entity['subcategory'] == 'app':
                obj = iTunesApp(itunes_id)
            if obj is not None:
                self.enrichEntityWithWrapper(obj, entity, controller, decorations, timestamps)
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
        elif query.type == 'book':
            return self.bookSource(query)
        elif query.type == 'tv':
            return self.tvSource(query)
        elif query.type == 'app':
            return self.appSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        else:
            return self.emptySource

    def trackSource(self, query):
        tracks = self.__itunes.method('search', term=query.name, entity='song', attribute='allTrackTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ iTunesTrack( data=entry ) for entry in result ]
        return source
    
    def albumSource(self, query):
        albums = self.__itunes.method('search', term=query.name, entity='album', attribute='albumTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ iTunesAlbum( data=entry ) for entry in result ]
        return source

    def artistSource(self, query):
        artists = self.__itunes.method('search', term=query.name, entity='allArtist', attribute='allArtistTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ iTunesArtist( data=entry ) for entry in result ]
        return source

    def movieSource(self, query):
        movies = self.__itunes.method('search', term=query.name, entity='movie', attribute='movieTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(movies):
                result = movies[start:start+count]
            elif start < len(movies):
                result = movies[start:]
            else:
                result = []
            return [ iTunesMovie( data=entry ) for entry in result ]
        return source

    def bookSource(self, query):
        movies = self.__itunes.method('search', term=query.name, entity='ebook', limit=100)['results']
        def source(start, count):
            if start + count <= len(movies):
                result = movies[start:start+count]
            elif start < len(movies):
                result = movies[start:]
            else:
                result = []
            return [ iTunesBook( data=entry ) for entry in result ]
        return source

    def tvSource(self, query):
        shows = self.__itunes.method('search', term=query.name, entity='tvShow', attribute='showTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(shows):
                result = shows[start:start+count]
            elif start < len(shows):
                result = shows[start:]
            else:
                result = []
            return [ iTunesTVShow( data=entry ) for entry in result ]
        return source

    def appSource(self, query):
        apps = self.__itunes.method('search', term=query.name, entity='software', attribute='softwareDeveloper', limit=100)['results']
        def source(start, count):
            if start + count <= len(apps):
                result = apps[start:start+count]
            elif start < len(apps):
                result = apps[start:]
            else:
                result = []
            return [ iTunesTVShow( data=entry ) for entry in result ]
        return source

    def __createWrapper(self, value):
        try:
            if 'wrapperType' in value:
                if value['wrapperType'] == 'track' and value['kind'] == 'song':
                    return iTunesTrack(data=value)
                elif value['wrapperType'] == 'collection' and value['collectionType'] == 'Album':
                    return iTunesAlbum(data=value)
                elif value['wrapperType'] == 'artist' and value['artistType'] == 'Artist':
                    return iTunesArtist(data=value)
                elif value['wrapperType'] == 'track' and value['kind'] == 'feature-movie':
                    return iTunesMovie(data=value)
                elif value['wrapperType'] == 'artist' and value['artistType'] == 'TV Show':
                    return iTunesTVShow(data=value)
                elif value['wrapperType'] == 'software':
                    return iTunesApp(data=value)
            else:
                if value['kind'] == 'ebook':
                    return iTunesBook(data=value)
            raise Exception
        except Exception:
            raise ValueError('Malformed iTunes output')

    def searchAllSource(self, query, timeout=None):
        validTypes = set(['book', 'track', 'album', 'artist', 'movie', 'tv', 'app'])
        if query.types is not None and len(validTypes.intersection(query.types)) == 0:
            return self.emptySource

        def gen():
            try:
                if query.types is None:
                    queries = [
                        'musicArtist', 'song', 'album', 'movie', 'ebook', 'tvShow', 'software'
                    ]
                else:
                    queries = []
                    if 'book' in query.types:
                        queries.append('ebook')
                    if 'track' in query.types:
                        queries.append('song')
                    if 'album' in query.types:
                        queries.append('album')
                    if 'artist' in query.types:
                        queries.append('musicArtist')
                    if 'movie' in query.types:
                        queries.append('movie')
                    if 'tv' in query.types:
                        queries.append('tvShow')
                    if 'app' in query.types:
                        queries.append('software')
                
                if len(queries) == 0:
                    return 
                
                raw_results = []
                def helper(q):
                    raw_results.append(self.__itunes.method(
                        'search',term=query.query_string,entity=q
                    )['results'])
                
                pool = Pool(len(queries))
                for q in queries:
                    pool.spawn(helper, q)
                pool.join(timeout=timeout)
                
                final_results = list(raw_results)
                found = True
                
                while found:
                    found = False
                    for results in final_results:
                        if len(results) > 0:
                            value = results[0]
                            del results[0]
                            try:
                                wrapper = self.__createWrapper(value)
                                if wrapper is not None:
                                    found = True
                                    yield wrapper
                            except ValueError:
                                logs.info('Malformed iTunes output:\n%s' % pformat(value))
            except GeneratorExit:
                pass
        return self.generatorSource( gen(), constructor=iTunesSearchAll )

if __name__ == '__main__':
    demo(iTunesSource(), 'Katy Perry')

