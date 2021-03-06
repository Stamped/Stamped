#!/usr/bin/env python

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
    from resolve.GenericSource      import GenericSource, multipleSource, listSource, MERGE_TIMEOUT, SEARCH_TIMEOUT
    from utils                      import lazyProperty
    from pprint                     import pformat, pprint
    from gevent.pool                import Pool
    from resolve.Resolver           import *
    from resolve.ResolverObject     import *
    from resolve.TitleUtils         import *
    from search.ScoringUtils        import *
except:
    report()
    raise


def available_in_us(item):
    # Most items have the availability field, but in the case of tracks, sometimes the availability is marked on the
    # album instead...
    try:
        territories = item['availability']['territories']
    except KeyError:
        pass
    try:
        territories = item['album']['availability']['territories']
    except KeyError:
        return True
    return not territories or 'US' in territories


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
        return self.spotify.lookup(self.key, "albumdetail", priority='low', timeout=MERGE_TIMEOUT)['artist']

    @lazyProperty
    def albums(self):
        try:
            album_list = self.full_data.get('albums', [])
        except LookupRequiredError:
            return []
        return [
            {
                'name'  : entry['album']['name'],
                'key'   : entry['album']['href'],
            }
                for entry in album_list
                    if entry['album']['artist'] == self.name and available_in_us(entry['album'])
        ]

    @lazyProperty
    def tracks(self):
        tracks = {}
        
        def lookupTrack(key):
            result = self.spotify.lookup(key, 'trackdetail', priority='low', timeout=MERGE_TIMEOUT)
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
        return self.spotify.lookup(self.key, 'trackdetail', priority='low', timeout=MERGE_TIMEOUT)['album']

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
        return self.spotify.lookup(self.key, priority='low', timeout=MERGE_TIMEOUT)['track']

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
            item = self.__spotify.lookup(key, priority='low', timeout=MERGE_TIMEOUT)
            
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

    def matchSource(self, query):
        if query.kind == 'person' and query.isType('artist'):
            return self.artistSource(query)
        if query.kind == 'media_collection' and query.isType('album'):
            return self.albumSource(query)
        if query.kind == 'media_item' and query.isType('track'):
            return self.trackSource(query)
        return self.emptySource

    def trackSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        tracks = self.__spotify.search('track', q=q, timeout=MERGE_TIMEOUT)['tracks']
        tracks = filter(available_in_us, tracks)
        return listSource(tracks, constructor=lambda x: SpotifyTrack(x['href'], data=x))

    def albumSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        albums = self.__spotify.search('album',q=q, timeout=MERGE_TIMEOUT)['albums']
        albums = filter(available_in_us, albums)
        return listSource(albums, constructor=lambda x: SpotifyAlbum(x['href'], data=x))


    def artistSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        artists = self.__spotify.search('artist', q=q, timeout=MERGE_TIMEOUT)['artists']
        return listSource(artists, constructor=lambda x: SpotifyArtist(x['href'], data=x))

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
            rawResults = self.__spotify.search(typeString, q=queryText, priority='high', timeout=SEARCH_TIMEOUT)[resultsKey]
            target.extend([proxyClass(rawResult['href'], data=rawResult, maxLookupCalls=0)
                for rawResult in rawResults if available_in_us(rawResult)])
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
        for track in tracks:
            applyTrackTitleDataQualityTests(track, queryText)
            adjustTrackRelevanceByQueryMatch(track, queryText)
            augmentTrackDataQualityOnBasicAttributePresence(track)

        albums  = scoreResultsWithBasicDropoffScoring(albums, sourceScore=0.7)
        for album in albums:
            applyAlbumTitleDataQualityTests(album, queryText)
            adjustAlbumRelevanceByQueryMatch(album, queryText)
            augmentAlbumDataQualityOnBasicAttributePresence(album)

        artists = scoreResultsWithBasicDropoffScoring(artists, sourceScore=0.6)
        for artist in artists:
            applyArtistTitleDataQualityTests(artist, queryText)
            adjustArtistRelevanceByQueryMatch(artist, queryText)
            augmentArtistDataQualityOnBasicAttributePresence(artist)

        self.__augmentArtistsAndAlbumsWithTracks(artists, albums, tracks)
        smoothRelevanceScores(tracks), smoothRelevanceScores(albums), smoothRelevanceScores(artists)
        # TODO: Incorporate popularities into ranking? Only worthwhile if we think they're under-weighting them.
        return interleaveResultsByRelevance((tracks, albums, artists))

if __name__ == '__main__':
    demo(SpotifySource(), 'Katy Perry')

