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
    import logs, urllib2
    from libs.iTunes                import globaliTunes
    from GenericSource              import GenericSource, listSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from pprint                     import pformat
    from Resolver                   import *
    from ResolverObject             import *
    from libs.LibUtils              import parseDateString
    from StampedSource              import StampedSource
except Exception:
    report()
    raise

class _iTunesObject(object):
    """
    Abstract superclass (mixin) for iTunes objects.

    _iTunesObjects may be instantiated with either their iTunes data or their id.
    If both are provided, they must match.

    Attributes:

    data - the type specific iTunes data for the object.
    itunes - an instance of iTunes (API entity proxy)
    """
    
    def __init__(self, itunes_id=None, data=None, itunes=None):
        if itunes is None:
            itunes = globaliTunes()
        self.__itunes       = itunes
        self.__data         = data
        self.__itunes_id    = itunes_id
    
    @lazyProperty
    def data(self):
        if self.__data == None:
            if self.isType('album') or self.isType('artist'):
                entity_field = 'song'
                if self.isType('artist'):
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
                if self.isType('artist'):
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
    def images(self):
        try:
            return [ self.data['artworkUrl100'] ]
        except Exception:
            return []
    
    def __repr__(self):
        return pformat( self.data )


class iTunesArtist(_iTunesObject, ResolverPerson):
    """
    iTunes artist proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverPerson.__init__(self, types=['artist'])

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
            results = self.itunes.method('lookup', id=self.key, entity='album')['results']
        return [
            {
                'name'  : album['collectionName'], 
                'key'   : str(album['collectionId']), 
                'data'  : album, 
            }
                for album in results if album.pop('collectionType', None) == 'Album' ]

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
                'name':             track['trackName'],
                'key':              track['trackId'],
                'url':              track['trackViewUrl'],
            }
                for track in results if track.pop('wrapperType', None) == 'track'
        ]
    
    #def __repr__(self):
    #    return "%s, %s" % (pformat(self.tracks), pformat(self.albums))

class iTunesAlbum(_iTunesObject, ResolverMediaCollection):
    """
    iTunes album proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaCollection.__init__(self, types=['album'])

    @lazyProperty
    def name(self):
        suffix = ''
        try:
            if self.data['contentAdvisoryRating'] == 'Clean':
                pass
                # suffix = ' (Clean)'
        except Exception:
            pass
        return '%s%s' % (self.data['collectionName'], suffix)

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
    def artists(self):
        try:
            return [{
                'name':     self.data['artistName'],
                'key':      self.data['artistId'],
                'url':      self.data['artistViewUrl'],
            }]
        except Exception:
            return []

    @lazyProperty
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except Exception:
            return []

    @lazyProperty
    def release_date(self):
        try:
            return parseDateString(self.data['releaseDate'])
        except KeyError:
            return None

    @lazyProperty
    def tracks(self):
        results = []
        if 'tracks' in self.data:
            results = self.data['tracks']
        else:
            results = self.itunes.method('lookup', id=self.key, entity='song')['results']
        return [
            {
                'name':             track['trackName'],
                'key':              track['trackId'],
                'url':              track['trackViewUrl'],
                'track_number':     track['trackNumber'],
            }
                for track in results if track.pop('wrapperType', None) == 'track' 
        ]


class iTunesTrack(_iTunesObject, ResolverMediaItem):
    """
    iTunes track proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['track'])

    @lazyProperty
    def name(self):
        suffix = ''
        try:
            if self.data['contentAdvisoryRating'] == 'Clean':
                pass
                # suffix = ' (Clean)'
        except Exception:
            pass
        return '%s%s' % (self.data['trackName'], suffix)

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
    def artists(self):
        try:
            return [{
                'name':     self.data['artistName'],
                'key':      self.data['artistId'],
                'url':      self.data['artistViewUrl'],
            }]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        try:
            return [{
                'name':     self.data['collectionName'],
                'key':      self.data['collectionId'],
                'url':      self.data['collectionViewUrl'],
            }]
        except Exception:
            return []

    @lazyProperty
    def genres(self):
        try:
            return [ self.data['primaryGenreName'] ]
        except Exception:
            return []

    @lazyProperty
    def release_date(self):
        try:
            return parseDateString(self.data['releaseDate'])
        except KeyError:
            return None

    @lazyProperty
    def length(self):
        return float(self.data['trackTimeMillis']) / 1000

    @lazyProperty
    def preview(self):
        try:
            return self.data['previewUrl']
        except Exception:
            return None


class iTunesMovie(_iTunesObject, ResolverMediaItem):
    """
    iTunes movie proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['movie'])

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
    def directors(self):
        try:
            return [ { 'name' : self.data['artistName'] } ]
        except KeyError:
            return []

    @lazyProperty
    def release_date(self):
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
    def mpaa_rating(self):
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

    @lazyProperty
    def preview(self):
        try:
            return self.data['previewUrl']
        except Exception:
            return None


class iTunesTVShow(_iTunesObject, ResolverMediaCollection):
    """
    iTunes tv show proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaCollection.__init__(self, types=['tv'])
    
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
    def directors(self):
        try:
            return [ { 'name' : self.data['artistName'] } ]
        except KeyError:
            return []

    @lazyProperty
    def release_date(self):
        return None

    @lazyProperty
    def seasons(self):
        return -1

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

class iTunesBook(_iTunesObject, ResolverMediaItem):

    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['book'])

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
    def authors(self):
        try:
            return [ { 'name' : self.data['artistName'] } ]
        except KeyError:
            return []

    @lazyProperty
    def publishers(self):
        return []

    @property
    def release_date(self):
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
    def sku_number(self):
        return None

class iTunesApp(_iTunesObject, ResolverSoftware):

    def __init__(self, itunes_id=None, data=None, itunes=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverSoftware.__init__(self, types=['app'])

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
    def publishers(self):
        try:
            return [ { 'name' : self.data['sellerName'] } ]
        except KeyError:
            return []

    @property
    def release_date(self):
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
        except Exception:
            return []

    @lazyProperty 
    def images(self):
        try:
            return [ self.data['artworkUrl512'] ]
        except Exception:
            return []

class iTunesSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)


class iTunesSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'itunes',
            groups=[
                'mpaa_rating',
                'genres',
                'desc',
                'artists',
                'albums',
                'tracks',
                'release_date',
                'publishers',
                'authors',
                'images',
                'screenshots',
                'length',
            ],
            kinds=[
                'person',
                'media_collection',
                'media_item',
            ],
            types=[
                'artist',
                'album',
                'track',
                'book',
                'movie',
                'tv',
                'app',
            ]
        )

    @property 
    def __mapper(self):
        mapper = [
            ('track',   'song'), 
            ('album',   'album'), 
            ('artist',  'musicArtist'), 
            ('app',     'software'), 
            ('book',    'ebook'), 
            ('movie',   'movie'), 
            ('tv',      'tvShow'), 
        ]
        return mapper

    @lazyProperty
    def __itunes(self):
        return globaliTunes()

    @lazyProperty
    def __stamped(self):
        return StampedSource()

    @lazyProperty
    def __resolver(self):
        return Resolver()

    def getGroups(self, entity=None):
        groups = GenericSource.getGroups(self, entity)
        if not entity.isType('app') and not entity.isType('movie') and not entity.isType('tv'):
            groups.remove('desc')
        if entity.isType('artist'):
            groups.remove('images')
        return groups

    def entityProxyFromKey(self, itunesId, **kwargs):
        try:
            rawData = self.__itunes.method('lookup',id=itunesId)

            if len(rawData['results']) == 0 or rawData['resultCount'] == 0:
                """
                Hacky method to try and 'enrich' the iTunes ID 

                If the iTunes ID is deprecated, lookup will fail with 0 results. The only
                way to convert to a new id is to attempt to connect to the human-readable 
                endpoint, which then does a 301 redirect to a url that contains the new
                valid id. This section grabs and parses that new id. It's not pretty, but it works.

                Note that iTunes can overwrite the seed priority for itunes_id as a result.
                """
                try:
                    entity = kwargs.pop('entity', None)
                    if entity is not None: 
                        url = None
                        if entity.itunes_url is not None:
                            url = entity.itunes_url
                        else:
                            for t in self.__mapper:
                                if entity.isType(t[0]):
                                    url = 'http://itunes.apple.com/us/%s/id%s' % (t[1], itunesId)
                        assert url is not None
                        source = urllib2.urlopen(url)
                        if source.code == 200 and source.url != url:
                            newId = source.url.split('?')[0].split('/')[-1].replace('id','')
                            if newId != itunesId:
                                rawData = self.__itunes.method('lookup', id=newId)
                except Exception:
                    pass

            data = rawData['results'][0]

            dataWrapperType     = data['wrapperType'] if 'wrapperType' in data else None
            dataKind            = data['kind'] if 'kind' in data else None
            dataCollectionType  = data['collectionType'] if 'collectionType' in data else None
            dataArtistType      = data['artistType'] if 'artistType' in data else None

            if dataWrapperType == 'track':
                if dataKind is not None and dataKind.find('movie') != -1:
                    return iTunesMovie(data=data)
                elif dataKind == 'song':
                    return iTunesTrack(data=data)
            elif dataWrapperType == 'collection' and dataCollectionType == 'Album':
                return iTunesAlbum(data=data)
            elif dataWrapperType == 'artist':
                if dataArtistType == 'TV Show':
                    return iTunesTVShow(data=data)
                return iTunesArtist(data=data)
            elif dataWrapperType == 'software':
                return iTunesApp(data=data)
            elif dataKind == 'ebook':
                return iTunesBook(data=data)
            raise KeyError('Unrecognized data: %s' % data)
        except KeyError:
            logs.warning('iTunes lookup failed (%s)' % itunesId)
            raise
        return None

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.itunes_id = proxy.key
        try:
            if proxy.preview is not None:
                entity.itunes_preview = proxy.preview
        except:
            pass
        return True

    def matchSource(self, query):
        if query.kind == 'person':
            if query.isType('artist'):
                return self.artistSource(query)

        if query.kind == 'media_collection':
            if query.isType('album'):
                return self.albumSource(query)
            if query.isType('tv'):
                return self.tvSource(query)

        if query.kind == 'media_item':
            if query.isType('track'):
                return self.trackSource(query)
            if query.isType('movie'):
                return self.movieSource(query)
            if query.isType('book'):
                return self.bookSource(query)

        if query.kind == 'software':
            if query.isType('app'):
                return self.appSource(query)

        if query.kind == 'search':
            return self.searchAllSource(query)
        return self.emptySource

    def trackSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='song', attribute='allTrackTerm', limit=200)['results']
        return listSource(items, constructor=lambda x: iTunesTrack(data=x))
    
    def albumSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='album', attribute='albumTerm', limit=200)['results']
        return listSource(items, constructor=lambda x: iTunesAlbum(data=x))

    def artistSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='allArtist', attribute='allArtistTerm', limit=100)['results']
        return listSource(items, constructor=lambda x: iTunesArtist(data=x))

    def movieSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='movie', attribute='movieTerm', limit=100)['results']
        return listSource(items, constructor=lambda x: iTunesMovie(data=x))

    def bookSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='ebook', limit=100)['results']
        return listSource(items, constructor=lambda x: iTunesBook(data=x))

    def tvSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='tvShow', attribute='showTerm', limit=100)['results']
        return listSource(items, constructor=lambda x: iTunesTVShow(data=x))

    def appSource(self, query):
        items = self.__itunes.method('search', term=query.name, entity='software', attribute='softwareDeveloper', limit=100)['results']
        return listSource(items, constructor=lambda x: iTunesApp(data=x))

    def __createEntityProxy(self, value):
        try:
            if 'wrapperType' in value:
                w = value['wrapperType']
                 
                if w == 'track' and value['kind'] == 'song':
                    return iTunesTrack(data=value)
                elif w == 'collection' and value['collectionType'] == 'Album':
                    return iTunesAlbum(data=value)
                elif w == 'artist' and value['artistType'] == 'Artist':
                    return iTunesArtist(data=value)
                elif w == 'track' and value['kind'] == 'feature-movie':
                    return iTunesMovie(data=value)
                elif w == 'artist' and value['artistType'] == 'TV Show':
                    return iTunesTVShow(data=value)
                elif w == 'software':
                    return iTunesApp(data=value)
            else:
                if value['kind'] == 'ebook':
                    return iTunesBook(data=value)
            raise Exception
        except Exception:
            raise ValueError('Malformed iTunes output')

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.info('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.info('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.info('Searching %s...' % self.sourceName)

        def gen():
            try:
                if query.types is None:
                    queries = [v[1] for v in self.__mapper]
                else:
                    queries = []
                    for t in query.types:
                        for t2 in self.__mapper:
                            if t == t2[0]:
                                queries.append(t2[1])
                
                if len(queries) == 0:
                    return
                
                raw_results = []
                def helper(q):
                    raw_results.append(self.__itunes.method(
                        'search', term=query.query_string, entity=q
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
                                proxy = self.__createEntityProxy(value)
                                
                                if proxy is not None:
                                    found = True
                                    yield proxy
                            except ValueError:
                                logs.info('Malformed iTunes output:\n%s' % pformat(value))
            except GeneratorExit:
                pass
        return self.generatorSource( gen(), constructor=iTunesSearchAll )

if __name__ == '__main__':
    demo(iTunesSource(), 'Katy Perry')

