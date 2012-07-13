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
    import logs, urllib2, datetime
    from libs.iTunes                import globaliTunes
    from resolve.GenericSource              import GenericSource, listSource
    from utils                      import lazyProperty, basicNestedObjectToString
    from gevent.pool                import Pool
    from pprint                     import pprint, pformat
    from resolve.Resolver                   import *
    from resolve.ResolverObject             import *
    from resolve.TitleUtils                 import *
    from libs.LibUtils              import parseDateString
    from resolve.StampedSource              import StampedSource
    from api.Entity                     import mapCategoryToTypes
    from search.ScoringUtils        import *
    from resolve.Resolver                   import trackSimplify
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

    def _findBestImage(self, url):
        """
        Takes a artworkUrl100 url and returns the highest res url
        """
        size400url = url.replace('100x100', '400x400')
        size200url = url.replace('100x100', '200x200')

        try:
            self.countLookupCall('image')
            urllib2.urlopen(size400url)
            return size400url
        except urllib2.HTTPError:
            pass
        except LookupRequiredError:
            pass

        try:
            self.countLookupCall('image')
            urllib2.urlopen(size200url)
            return size200url
        except urllib2.HTTPError:
            pass
        except LookupRequiredError:
            pass

        return url


    @lazyProperty
    def data(self):
        if self.__data is not None:
            return self.__data

        if not (self.isType('album') or self.isType('artist')):
            # Here and in the later call, we don't bother catching the LookupRequiredError because if you're not passing
            # the data param into an iTunesSource with capped lookup calls you're doing it wrong.
            self.countLookupCall('full data')
            return self.itunes.method('lookup', id=self.__itunes_id)['results'][0]

        entity_field = 'song'
        if self.isType('artist'):
            entity_field = 'album,song'
        # This is pretty heinous -- this method doesn't actually exist on iTunesObject but secretly we know that
        # all iTunesObjects are also ResolverObjects, which defines countLookupCall. Ugh.
        # TODO: Multiple inheritance blows. Maybe instead of making these things explicitly ResolverObject subtypes,
        # we can just have them call functions in their initializers that perform debug checks to (a) make sure they
        # define the right fields and (b) make sure the fields all return the right types. This makes it more onerous
        # to define an implementation that falls back to empty values for a bunch of fields, but the initializer could
        # fill those fields in with static values, or something.
        #    (if not hasattr(self, 'authors') self.authors = [])
        # Instead of being able to say "is ResolverPerson," then, you could instead use types, etc.
        self.countLookupCall('full data')
        results = self.itunes.method('lookup', id=self.__itunes_id, entity=entity_field, limit=1000)['results']
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
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverPerson.__init__(self, types=['artist'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanArtistTitle(rawName)

    @lazyProperty
    def raw_name(self):
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
    def amgId(self):
        return self.data.get('amgArtistId', None)

    @lazyProperty
    def albums(self):
        results = []
        if 'albums' in self.data:
            results = self.data['albums']
        else:
            try:
                self.countLookupCall('albums')
                results = self.itunes.method('lookup', id=self.key, entity='album', limit=1000)['results']
            except LookupRequiredError:
                results = []
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
            try:
                self.countLookupCall('tracks')
                results = self.itunes.method('lookup', id=self.key, entity='song', limit=1000)['results']
            except LookupRequiredError:
                results = []
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
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaCollection.__init__(self, types=['album'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanAlbumTitle(rawName)

    @lazyProperty
    def raw_name(self):
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
        result = [{
                'name':     self.data.get('artistName', None),
                'key':      self.data.get('artistId', None),
                'url':      self.data.get('artistViewUrl', None),
                }]
        if any(value is not None for value in result[0].values()):
            return result
        else:
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
            try:
                self.countLookupCall('tracks')
                results = self.itunes.method('lookup', id=self.key, entity='song', limit=1000)['results']
            except LookupRequiredError:
                results = []
        if results is None:
            return []
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
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['track'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanTrackTitle(rawName)

    @lazyProperty
    def raw_name(self):
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

    @property
    def artistId(self):
        return self.data.get('artistId', None)

    @lazyProperty
    def artists(self):
        result = [{
                'name':     self.data.get('artistName'),
                'key':      self.data.get('artistId'),
                'url':      self.data.get('artistViewUrl'),
                }]
        if any(value is not None for value in result[0].values()):
           return result
        else:
            return []

    @property
    def albumId(self):
        return self.data.get('collectionId', None)

    @lazyProperty
    def albums(self):
        result = [{
            'name':     self.data.get('collectionName'),
            'key':      self.data.get('collectionId'),
            'url':      self.data.get('collectionViewUrl'),
            }]
        if any(value is not None for value in result[0].values()):
            return result
        else:
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
        except KeyError:
            return None


class iTunesMovie(_iTunesObject, ResolverMediaItem):
    """
    iTunes movie proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanMovieTitle(rawName)

    @lazyProperty
    def raw_name(self):
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
        # iTunes movie release dates are LIES. If there's something in a title in parens, we can trust it. Otherwise,
        # throw it out.
        year = getMovieReleaseYearFromTitle(self.raw_name)
        if year is not None:
            return datetime.datetime(year, 1, 1)
        else:
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
        except KeyError:
            return None


class iTunesTVShow(_iTunesObject, ResolverMediaCollection):
    """
    iTunes tv show proxy
    """
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaCollection.__init__(self, types=['tv'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanTvTitle(rawName)

    @lazyProperty
    def raw_name(self):
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
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverMediaItem.__init__(self, types=['book'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanBookTitle(rawName)

    @lazyProperty
    def raw_name(self):
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
    def __init__(self, itunes_id=None, data=None, itunes=None, maxLookupCalls=None):
        _iTunesObject.__init__(self, itunes_id=itunes_id, data=data, itunes=itunes)
        ResolverSoftware.__init__(self, types=['app'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanAppTitle(rawName)

    @lazyProperty
    def raw_name(self):
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

class UnknownITunesTypeError(Exception):
    def __init__(self, details):
        super(UnknownITunesTypeError, self).__init__(self, details)

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
                'software',
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
    def __types_to_itunes_strings(self):
        types_to_itunes_strings = [
            ('track',   'song'), 
            ('album',   'album'), 
            ('artist',  'musicArtist'), 
            ('app',     'software'), 
            ('book',    'ebook'), 
            ('movie',   'movie'), 
            ('tv',      'tvShow'), 
        ]
        return types_to_itunes_strings

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
                        if entity.sources.itunes_url is not None:
                            url = entity.sources.itunes_url
                        else:
                            for (type_, str_) in self.__types_to_itunes_strings:
                                if entity.isType(type_):
                                    url = 'http://itunes.apple.com/us/%s/id%s' % (str_, itunesId)
                        assert url is not None
                        source = urllib2.urlopen(url)
                        if source.code == 200 and source.url != url:
                            newId = source.url.split('?')[0].split('/')[-1].replace('id','')
                            if newId != itunesId:
                                rawData = self.__itunes.method('lookup', id=newId)
                except Exception:
                    pass

            try:
                data = rawData['results'][0]
            except IndexError:
                logs.warning('iTunes lookup failed(%s)' % itunesId)
                raise

            dataWrapperType     = data['wrapperType'] if 'wrapperType' in data else None
            dataKind            = data['kind'] if 'kind' in data else None
            dataCollectionType  = data['collectionType'] if 'collectionType' in data else None
            dataArtistType      = data['artistType'] if 'artistType' in data else None

            return self.__createEntityProxy(data)
            if dataWrapperType == 'track':
                if dataKind is not None and dataKind.find('movie') != -1:
                    return iTunesMovie(data=data)
                elif dataKind == 'song':
                    return iTunesTrack(data=data)
            elif dataWrapperType == 'collection' and dataCollectionType in ['Album', 'Compilation']:
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
        entity.sources.itunes_url = proxy.url

        if hasattr(proxy, 'preview') and proxy.preview is not None:
            entity.sources.itunes_preview = proxy.preview
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

    def __createEntityProxy(self, value, maxLookupCalls=None):
        constructor = None
        if 'wrapperType' in value:
            w = value['wrapperType']

            if w == 'track' and value['kind'] == 'song':
                constructor = iTunesTrack
            elif w == 'collection' and value['collectionType'] in ['Album', 'Compilation']:
                constructor = iTunesAlbum
            elif w == 'artist' and value['artistType'] == 'Artist':
                constructor = iTunesArtist
            elif w == 'track' and value['kind'] == 'feature-movie':
                constructor = iTunesMovie
            elif w == 'artist' and value['artistType'] == 'TV Show':
                constructor = iTunesTVShow
            elif w == 'software':
                constructor = iTunesApp
            else:
                raise UnknownITunesTypeError('Unknown iTunes type: wrapperType=%s, kind=%s, artistType=%s, collectionType=%s' %
                                             (w, value.get('kind', ''), value.get('artistType', ''), value.get('collectionType', '')))
        else:
            if value['kind'] == 'ebook':
                constructor = iTunesBook
            else:
                raise UnknownITunesTypeError('Unknown iTunesType: no wrapperType, kind=%s' % value.get('kind', ''))

        return constructor(data=value, maxLookupCalls=maxLookupCalls)

    def __searchEntityTypeLite(self, entityType, queryText, resultsDict):
        try:
            if isinstance(queryText, unicode):
                queryText = queryText.encode('utf-8')
            resultsDict[entityType] = self.__itunes.method('search', entity=entityType, term=queryText)['results']
        except Exception:
            logs.report()

    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=False):
        if queryCategory not in ('music', 'film', 'app', 'book'):
            raise NotImplementedError()

        supportedProxyTypes = {
            'music': (iTunesArtist, iTunesAlbum, iTunesTrack),
            'film': (iTunesMovie, iTunesTVShow),
            'app': (iTunesApp,),
            'book': (iTunesBook,),
        }[queryCategory]

        types = mapCategoryToTypes(queryCategory)
        iTunesTypes = []
        typesMap = dict(self.__types_to_itunes_strings)
        for entityType in types:
            iTunesTypes.append(typesMap[entityType])

        pool = Pool(len(iTunesTypes))
        rawResults = {}
        for iTunesType in iTunesTypes:
            pool.spawn(self.__searchEntityTypeLite, iTunesType, queryText, rawResults)
        pool.join(timeout=timeout)

        if logRawResults:
            logComponents = ["\n\n\nITUNES RAW RESULTS\nITUNES RAW RESULTS\nITUNES RAW RESULTS\n\n\n"]

        searchResultsByType = {}
        # Convert from JSON objects to entity proxies. Pass through actual parsing errors, but report & drop the result
        # if we just see a type we aren't expecting. (Music search will sometimes return podcasts, for instance.)
        for (iTunesType, rawTypeResults) in rawResults.items():
            processedResults = []
            for rawResult in rawTypeResults:
                try:
                    if logRawResults:
                        logComponents.extend(['\n\n', pformat(rawResult), '\n\n'])
                    proxy = self.__createEntityProxy(rawResult, maxLookupCalls=0)
                    if not any(isinstance(proxy, proxyType) for proxyType in supportedProxyTypes):
                        logs.warning('Dropping iTunes proxy of unsupported type %s for queryCategory %s:\n\n%s\n\n' %
                                     (proxy.__class__.__name__, queryCategory, str(proxy)))
                        continue
                    processedResults.append(self.__createEntityProxy(rawResult, maxLookupCalls=0))
                except UnknownITunesTypeError:
                    logs.report()
                    pass

            if len(processedResults) > 0:
                searchResultsByType[iTunesType] = self.__scoreResults(iTunesType, processedResults, queryText)

        if logRawResults:
            logComponents.append("\n\n\nEND RAW ITUNES RESULTS\n\n\n")
            logs.debug(''.join(logComponents))

        if len(searchResultsByType) == 0:
            # TODO: Throw exception to avoid cache?
            return []
        if len(searchResultsByType) == 1:
            return searchResultsByType.values()[0]
        if queryCategory == 'music':
            # We have to separately request songs, albums, and artists because iTunes does a terrible job blending
            # results between the three. So we need to blend, but it's hard to know how to. We do a little work on the
            # string matching side, but
            self.__augmentAlbumAndArtistResultsWithSongs(searchResultsByType.get('album', []),
                searchResultsByType.get('musicArtist', []),
                searchResultsByType.get('song', []))
        return interleaveResultsByRelevance(searchResultsByType.values())

    def __scoreResults(self, iTunesType, resolverObjects, queryText):
        # We weight down album and artist and rely on the augmentation to bring them back up. This is because otherwise
        # we will always interleave artists with songs -- you'll never get a query where artists don't feature
        # prominently -- and that doesn't make sense.

        # With that said, we weight down albums more than artists, and we boost artists more than albums based on songs,
        # because Amazon carries albums (and weights them up with songs) and not artists.
        iTunesTypesToWeights = {
            'album' : 0.5,
            'musicArtist' : 0.8,
            # Having iTunes book results is good for enrichment, and in case Amazon doesn't return results or something,
            # but we really don't want it having much of an impact on ranking, since iTunes only has
            # ebooks, so any book without ebook version will be at a huge disadvantage
            'ebook': 0.5,
        }

        # TODO: Refactoring is needed here.
        iTunesTypesToScoreAdjustments = {
            'movie' : (applyMovieTitleDataQualityTests, adjustMovieRelevanceByQueryMatch),
            'tvShow' : (applyTvTitleDataQualityTests, adjustTvRelevanceByQueryMatch),
            'musicArtist' : (applyArtistTitleDataQualityTests, adjustArtistRelevanceByQueryMatch),
            'album' : (applyAlbumTitleDataQualityTests, adjustAlbumRelevanceByQueryMatch),
            'song' : (applyTrackTitleDataQualityTests, adjustTrackRelevanceByQueryMatch),
        }

        if iTunesType in iTunesTypesToWeights:
            searchResults = scoreResultsWithBasicDropoffScoring(resolverObjects,
                sourceScore=iTunesTypesToWeights[iTunesType])
        else:
            searchResults = scoreResultsWithBasicDropoffScoring(resolverObjects)

        for adjustmentFn in iTunesTypesToScoreAdjustments.get(iTunesType, ()):
            for searchResult in searchResults:
                adjustmentFn(searchResult, queryText)

        # Artists without amg IDs get scored down.
        if iTunesType == 'musicArtist':
            for artistResult in searchResults:
                if not artistResult.resolverObject.amgId:
                    artistResult.relevance = artistResult.relevance * 0.6

        # TODO(geoff): This is a bit hacky, but because iTunes always has better quality data than
        # amazon, we double the quality here so the title and author from iTunes will always be
        # picked.
        if iTunesType == 'ebook':
            for result in searchResults:
                result.dataQuality *= 2

        return searchResults
        # TODO: POTENTIALLY USE RELEASE DATE.

    def __augmentAlbumAndArtistResultsWithSongs(self, albumSearchResults, artistSearchResults, songSearchResults):
        artistIdsToArtists = {}
        collectionIdsToAlbums = {}
        for albumSearchResult in albumSearchResults:
            # Hey. It never hurts to program defensively.
            if albumSearchResult.resolverObject.key in collectionIdsToAlbums:
                raise Exception("Found duplicates in results straight from iTunes!")
            collectionIdsToAlbums[albumSearchResult.resolverObject.key] = albumSearchResult

        for artistSearchResult in artistSearchResults:
            # Hey. It never hurts to program defensively.
            if artistSearchResult.resolverObject.key in artistIdsToArtists:
                raise Exception("Found duplicates in results straight from iTunes!")
            artistIdsToArtists[artistSearchResult.resolverObject.key] = artistSearchResult

        # Sometimes we see a bunch of variations of the same song show up, and that can unreasonably boost an artist
        # result way to the top when the request is for the song. So we do some simple de-duping to try to avoid
        # counting multiple different recordings of a song all towards the same artist (or album.)
        songsSeenTitlesAndArtistIds = set()
        for songSearchResult in songSearchResults:
            title = trackSimplify(songSearchResult.resolverObject.name)
            albumId = songSearchResult.resolverObject.albumId
            artistId = songSearchResult.resolverObject.artistId

            if (title, artistId) in songsSeenTitlesAndArtistIds:
                continue
            songsSeenTitlesAndArtistIds.add((title, artistId))

            if albumId and albumId in collectionIdsToAlbums:
                albumSearchResult = collectionIdsToAlbums.get(albumId, None)
                # TODO: Revisit this.
                scoreBoost = songSearchResult.relevance / 5
                albumSearchResult.addRelevanceComponentDebugInfo(
                    'boost from song %s' % songSearchResult.resolverObject.name, scoreBoost)
                albumSearchResult.relevance += scoreBoost

            if artistId and artistId in artistIdsToArtists:
                artistSearchResult = artistIdsToArtists.get(artistId, None)
                # TODO: Revisit this.
                scoreBoost = songSearchResult.relevance / 3
                artistSearchResult.addRelevanceComponentDebugInfo(
                    'boost from song %s' % songSearchResult.resolverObject.name, scoreBoost)
                artistSearchResult.relevance += scoreBoost
                    
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
                    queries = [itunes_str for (type_, itunes_str) in self.__types_to_itunes_strings]
                else:
                    queries = []
                    for query_type in query.types:
                        for (type_, itunes_str) in self.__types_to_itunes_strings:
                            if query_type == type_:
                                queries.append(itunes_str)
                
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
        return self.generatorSource(gen(), constructor=iTunesSearchAll)

if __name__ == '__main__':
    demo(iTunesSource(), 'Katy Perry')

