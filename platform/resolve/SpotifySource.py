#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SpotifySource', 'SpotifyArtist', 'SpotifyAlbum', 'SpotifyTrack' ]

import Globals, utils
from logs import report

try:
    import logs
    from libs.Spotify               import globalSpotify
    from copy                       import copy
    from GenericSource              import GenericSource, multipleSource, listSource
    from utils                      import lazyProperty
    from pprint                     import pformat
    from gevent.pool                import Pool
    from Resolver                   import *
    from ResolverObject             import *
    from TitleUtils                 import *
    from search.ScoringUtils        import *
except:
    report()
    raise


class _SpotifyObject(object):
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API proxy)
    """

    def __init__(self, spotify_id, spotify=None, data=None):
        if spotify is None:
            spotify = globalSpotify()
        
        self.__spotify    = spotify
        self.__spotify_id = spotify_id
        # The data we get just from search results.
        self.__basicData = data
        # Data retrieved from a lookup.
        self.__fullData  = None

    @property
    def data(self):
        """
        The data accessor is agnostic between basic data and full lookup data. It prefers full data if it's already
        available; if not, it falls back to basic data; if there is none, it issues the lookup.

        If the field you want is only available in lookup data, use the full_data accessor.
        """
        if self.__fullData:
            return self.__fullData
        if self.__basicData:
            return self.__basicData
        # Lazy property call that issues lookup. This could catch LookupRequiredError but we're not catching it here
        # because if you're creating a capped-lookup-call object without any initial data you're doing it wrong.
        return self.full_data

    @lazyProperty
    def full_data(self):
        if self.__fullData:
            return self.__fullData
        # Sort of hacky -- calls a function implemented by ResolverObject.
        # Note that full_data does not catch the LookupRequiredError, so any users of it need to.
        self.countLookupCall('full data')
        self.__fullData = self.lookup_data()
        return self.__fullData

    def lookup_data(self):
        raise NotImplementedError()

    @property
    def popularity(self):
        if self.__basicData is None:
            return None
        return float(self.__basicData['popularity'])

    @property
    def spotify(self):
        return self.__spotify

    @lazyProperty
    def key(self):
        return self.__spotify_id

    @property 
    def source(self):
        return "spotify"

    @property
    def raw_name(self):
        return self.data['name']

    def __repr__(self):
        # NOTE: availability generally includes *many* ISO country codes which 
        # make sifting through debug printouts painful, so disable them here.
        data = copy(self.data)
        data.pop('availability', None)
        return "<%s %s %s> %s" % (self.source, self.types, self.name, pformat(data))


class SpotifyArtist(_SpotifyObject, ResolverPerson):
    """
    Spotify artist proxy
    """
    def __init__(self, spotify_id, data=None, maxLookupCalls=None):
        _SpotifyObject.__init__(self, spotify_id, data=data)
        ResolverPerson.__init__(self, types=['artist'], maxLookupCalls=maxLookupCalls)
        self._properties.extend(['popularity'])

    def _cleanName(self, rawName):
        return cleanArtistTitle(rawName)

    def lookup_data(self):
        return self.spotify.lookup(self.key, "albumdetail")['artist']

    @lazyProperty
    def albums(self):
        try:
            album_list = self.full_data['albums']
        except LookupRequiredError:
            return []
        return [
            {
                'name'  : entry['album']['name'],
                'key'   : entry['album']['href'],
            }
                for entry in album_list
                    if entry['album']['artist'] == self.name and entry['album']['availability']['territories'].find('US') != -1
        ]

    @lazyProperty
    def tracks(self):
        tracks = {}
        
        def lookupTrack(key):
            result = self.spotify.lookup(key, 'trackdetail')
            track_list = result['album']['tracks']
            
            for track in track_list:
                track_key = track['href']
                
                if track_key not in tracks:
                    data = {
                        'key': track_key,
                        'name': track['name'],
                    }
                    
                    try:
                        # (travis): as of 4/3/12, track length is only sometimes returned by spotify
                        data['length'] = int(track['length']),
                    except KeyError:
                        pass
                    
                    tracks[track_key] = data
        
        size = min(1 + len(self.albums), 20)
        pool = Pool(size)
        
        for album in self.albums:
            key = album['key']
            pool.spawn(lookupTrack, key)
        
        pool.join()
        return list(tracks.values())


class SpotifyAlbum(_SpotifyObject, ResolverMediaCollection):
    """
    Spotify album proxy
    """
    def __init__(self, spotify_id, data=None, maxLookupCalls=None):
        _SpotifyObject.__init__(self, spotify_id, data=data)
        ResolverMediaCollection.__init__(self, types=['album'], maxLookupCalls=maxLookupCalls)
        self._properties.extend(['popularity'])

    def _cleanName(self, rawName):
        return cleanAlbumTitle(rawName)

    def lookup_data(self):
        return self.spotify.lookup(self.key, 'trackdetail')['album']

    @lazyProperty
    def artists(self):
        if 'artist' in self.data and 'artist-id' in self.data:
            return [ {
                'name'  : self.data['artist'],
                'key'   : self.data['artist-id'],
            } ]
        if 'artists' in self.data:
            return [ {
                'name' : artist['name'],
                # Artist href is missing for 'Various Artists' stuff.
                'key'  : artist.get('href', None),
            } for artist in self.data['artists'] ]
        return []

    @lazyProperty
    def tracks(self):
        try:
            track_list = self.full_data['tracks']
        except LookupRequiredError:
            return []
        return [ 
            { 
                'name'  : track['name'], 
                'key'   : track['href'],
            } 
                for track in track_list 
        ]


class SpotifyTrack(_SpotifyObject, ResolverMediaItem):
    """
    Spotify track proxy
    """
    def __init__(self, spotify_id, data=None, maxLookupCalls=None):
        _SpotifyObject.__init__(self, spotify_id, data=data)
        ResolverMediaItem.__init__(self, types=['track'], maxLookupCalls=maxLookupCalls)
        self._properties.extend(['popularity'])

    def _cleanName(self, rawName):
        return cleanTrackTitle(rawName)

    def lookup_data(self):
        return self.spotify.lookup(self.key)['track']

    @lazyProperty
    def artists(self):
        try:
            return [ { 
                'name'  : self.data['artists'][0]['name'],
                # Artist href is missing for 'Various Artists' stuff.
                'key'   : self.data['artists'][0].get('href', None),
            } ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        try:
            return [ { 
                'name'  : self.data['album']['name'],
                'key'   : self.data['album']['href'],
                # TODO: We also have year of release here.
            } ]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        try:
            return float(self.data['length'])
        except Exception:
            return -1

    # TODO: We also have track # information which might be useful for de-duping against Amazon and possibly others.


class SpotifySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class SpotifySource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'spotify',
            groups=[
                'albums',
                'tracks',
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
            ]
        )

    @lazyProperty
    def __spotify(self):
        return globalSpotify()

    @property
    def urlField(self):
        return None

    def entityProxyFromKey(self, key, **kwargs):
        try:
            item = self.__spotify.lookup(key)
            
            if item['info']['type'] == 'artist':
                return SpotifyArtist(key)
            if item['info']['type'] == 'album':
                return SpotifyAlbum(key)
            if item['info']['type'] == 'track':
                return SpotifyTrack(key)
            
            raise KeyError
        except KeyError:
            logs.warning('Unable to find Spotify item for key: %s' % key)
            raise
        
        return None

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.spotify_id = proxy.key
        
        return True

    def matchSource(self, query):
        if query.kind == 'person' and query.isType('artist'):
            return self.artistSource(query)
        if query.kind == 'media_collection' and query.isType('album'):
            return self.albumSource(query)
        if query.kind == 'media_item' and query.isType('track'):
            return self.trackSource(query)
        if query.kind == 'search':
            return self.searchAllSource(query)
        
        return self.emptySource

    def trackSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        tracks = self.__spotify.search('track',q=q)['tracks']
        return listSource(tracks, constructor=lambda x: SpotifyTrack(x['href'], data=x))

    def albumSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        albums = self.__spotify.search('album',q=q)['albums']
        albums = [ entry for entry in albums if entry['availability']['territories'].find('US') != -1 ]
        return listSource(albums, constructor=lambda x: SpotifyAlbum(x['href'], data=x))


    def artistSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        artists = self.__spotify.search('artist',q=q)['artists']
        return listSource(artists, constructor=lambda x: SpotifyArtist(x['href'], data=x))

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.debug('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
            
        q = query.query_string
        return multipleSource(
            [
                lambda : self.artistSource(query_string=q),
                lambda : self.albumSource(query_string=q),
                lambda : self.trackSource(query_string=q),
            ],
            constructor=SpotifySearchAll
        )

    def __augmentArtistsAndAlbumsWithTracks(self, artistSearchResults, albumSearchResults, trackSearchResults):
        """
        Takes three lists of SearchResult objects -- one wrapping SpotifyArtists, one wrapping SpotifyAlbums, one
        wrapping SpotifyTracks. Increases the scores of the albums and tracks based on the artists.
        """
        idsToArtists = {}
        for artistSearchResult in artistSearchResults:
            idsToArtists[artistSearchResult.resolverObject.key] = artistSearchResult

        idsToAlbums = {}
        for albumSearchResult in albumSearchResults:
            album = albumSearchResult.resolverObject
            idsToAlbums[album.key] = albumSearchResult
            if album.artists and album.artists[0]['key'] in idsToArtists:
                artistSearchResult = idsToArtists[album.artists[0]['key']]
                scoreBoost = albumSearchResult.relevance / 3
                artistSearchResult.addRelevanceComponentDebugInfo('Boost from album %s' % album.name, scoreBoost)
                artistSearchResult.relevance += scoreBoost

        for trackSearchResult in trackSearchResults:
            track = trackSearchResult.resolverObject
            if track.artists and track.artists[0]['key'] in idsToArtists:
                artistSearchResult = idsToArtists[track.artists[0]['key']]
                scoreBoost = trackSearchResult.relevance / 5
                artistSearchResult.addRelevanceComponentDebugInfo('Boost from track %s' % track.name, scoreBoost)
                artistSearchResult.relevance += scoreBoost
            if track.albums and track.albums[0]['key'] in idsToAlbums:
                albumSearchResult = idsToAlbums[track.albums[0]['key']]
                scoreBoost = trackSearchResult.relevance / 5
                albumSearchResult.addRelevanceComponentDebugInfo('Boost from track %s' % track.name, scoreBoost)
                albumSearchResult.relevance += scoreBoost


    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=None):
        tracks, albums, artists = [], [], []
        def conductTypeSearch((target, proxyClass, typeString, resultsKey)):
            rawResults = self.__spotify.search(typeString, q=queryText)[resultsKey]
            target.extend([proxyClass(rawResult['href'], data=rawResult, maxLookupCalls=0) for rawResult in rawResults])
        typeSearches = (
            (tracks, SpotifyTrack, 'track', 'tracks'),
            (albums, SpotifyAlbum, 'album', 'albums'),
            (artists, SpotifyArtist, 'artist', 'artists'),
        )
        pool = Pool(len(typeSearches))
        for typeSearch in typeSearches:
            pool.spawn(conductTypeSearch, typeSearch)
        pool.join(timeout=timeout)
        
        if logRawResults:
            logComponents = ['\n\n\nSPOTIFY RAW RESULTS\nSPOTIFY RAW RESULTS\nSPOTIFY RAW RESULTS\n\n\n']
            logComponents.append('\n\nTRACKS TRACKS TRACKS TRACKS TRACKS TRACKS\n\n')
            logComponents.extend(['\n\n%s\n\n' % pformat(proxy.data) for proxy in tracks])
            logComponents.append('\n\nALBUMS ALBUMS ALBUMS ALBUMS ALBUMS ALBUMS\n\n')
            logComponents.extend(['\n\n%s\n\n' % pformat(proxy.data) for proxy in albums])
            logComponents.append('\n\nARTISTS ARTISTS ARTISTS ARTISTS ARTISTS ARTISTS\n\n')
            logComponents.extend(['\n\n%s\n\n' % pformat(proxy.data) for proxy in artists])
            logComponents.append('\n\n\nEND SPOTIFY RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))

        # We start out penalizing albums and artists severely, with the idea that if they show up
        tracks  = scoreResultsWithBasicDropoffScoring(tracks, sourceScore=1.0)
        albums  = scoreResultsWithBasicDropoffScoring(albums, sourceScore=0.7)
        artists = scoreResultsWithBasicDropoffScoring(artists, sourceScore=0.6)
        self.__augmentArtistsAndAlbumsWithTracks(artists, albums, tracks)
        smoothRelevanceScores(tracks), smoothRelevanceScores(albums), smoothRelevanceScores(artists)
        # TODO: Incorporate popularities into ranking? Only worthwhile if we think they're under-weighting them.
        return interleaveResultsByRelevance((tracks, albums, artists))

if __name__ == '__main__':
    demo(SpotifySource(), 'Katy Perry')

