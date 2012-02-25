#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [
    'Resolver',

    'ResolverArtist',
    'RdioArtist',
    'SpotifyArtist',
    'iTunesArtist',
    'EntityArtist',

    'ResolverAlbum',
    'RdioAlbum',
    'SpotifyAlbum',
    'iTunesAlbum',
    'EntityAlbum',

    'ResolverTrack',
    'RdioTrack',
    'SpotifyTrack',
    'iTunesTrack',
    'EntityTrack',
]

import Globals
from logs import report

try:
    from libs.Rdio                  import globalRdio
    from libs.Spotify               import globalSpotify
    from libs.iTunes                import globaliTunes
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    from Schemas                    import Entity
    import logs
    import re
    from pprint                     import pprint, pformat
    import sys
    from Entity                     import getSimplifiedTitle
    from gevent.pool                import Pool
    import math
    from abc                        import ABCMeta, abstractmethod, abstractproperty
except:
    report()
    raise

_verbose = False
_very_verbose = False


_general_regex_removals = [
    (r'.*(\(.*\)).*'    , [1]),     # a name ( with parens ) anywhere
    (r'.*(\[.*]).*'     , [1]),     # a name [ with brackets ] anywhere
    (r'.*(\(.*)'        , [1]),     # a name ( bad parathetical
    (r'.*(\[.*)'        , [1]),     # a name [ bad brackets
    (r'.*(\.\.\.).*'    , [1]),     # ellipsis ... anywhere
]

_track_removals = [
    (r'.*(-.* (remix|mix|version|edit|dub)$)'  , [1]),
]

_album_removals = [
    (r'.*((-|,)( the)? remixes.*$)'    , [1]),
    (r'.*(- ep$)'                   , [1]),
    (r'.*( the (\w+ )?remixes$)'     , [1]),
    (r'.*(- remix ep)' , [1]),
    (r'.*(- single$)' , [1]),
]

def _regexRemoval(string, patterns):
    modified = True
    while modified:
        modified = False
        for pattern, groups in patterns:
            while True:
                match = re.match(pattern, string)
                if match is None:
                    break
                else:
                    for group in groups:
                        string2 = string.replace(match.group(group),'')
                        if _very_verbose:
                            print('Replaced %s with %s' % (string, string2))
                        string = string2
                        modified = True
    return string

def _format(string):
    modified = True
    li = [ '\t' , '\n', '\r', '  ' ]
    while modified:
        modified = False
        for ch in li:
            string2 = string.replace(ch,' ')
            if string2 != string:
                modified = True
                string = string2
    return string.strip()

def _simplify(string):
    string = getSimplifiedTitle(string)
    string = _format(string)
    string = _regexRemoval(string, _general_regex_removals)
    return _format(string)

def _trackSimplify(string):
    string = _simplify(string)
    string = _regexRemoval(string, _track_removals)
    return _format(string)

def _albumSimplify(string):
    string = _simplify(string)
    string = _regexRemoval(string, _album_removals)
    return _format(string)


class ResolverObject(object):
    
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def key(self):
        pass

    @abstractproperty
    def source(self):
        pass

    @abstractproperty
    def type(self):
        pass

class _EntityObject(object):

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

class _RdioObject(object):

    def __init__(self, data=None, rdio_id=None, rdio=None, extras=''):
        if rdio is None:
            rdio = globalRdio()
        if data == None:
            if rdio_id is None:
                raise ValueError('data or rdio_id must not be None')
            try:
                data = rdio.method('get',keys=rdio_id,extras=extras)['result'][rdio_id]
            except KeyError:
                raise ValueError('bad rdio_id')
        elif rdio_id is not None:
            if rdio_id != data['key']:
                raise ValueError('rdio_id does not match data["key"]')
        self.__rdio = rdio
        self.__data = data

    @property
    def rdio(self):
        return self.__rdio

    @property
    def data(self):
        return self.__data

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def key(self):
        return self.data['key']

    @property 
    def source(self):
        return "rdio"

    def __repr__(self):
        return pformat( self.data )


class _SpotifyObject(object):

    def __init__(self, spotify_id, spotify=None, extras=''):
        if spotify is None:
            spotify = globalSpotify()
        self.__spotify = spotify
        self.__spotify_id = spotify_id

    @property
    def spotify(self):
        return self.__spotify

    @lazyProperty
    def key(self):
        return self.__spotify_id

    @property 
    def source(self):
        return "spotify"

    def __repr__(self):
        return "<%s %s %s>" % (self.source, self.type, self.name)


class _iTunesObject(object):
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

#
# Artist
#


class ResolverArtist(ResolverObject):

    @abstractproperty
    def albums(self):
        pass

    @abstractproperty
    def tracks(self):
        pass

    @property 
    def type(self):
        return 'artist'

class RdioArtist(_RdioObject, ResolverArtist):
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='albumCount')  
        ResolverArtist.__init__(self)

    @lazyProperty
    def albums(self):
        album_list = self.rdio.method('getAlbumsForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in album_list ]

    @lazyProperty
    def tracks(self):
        track_list = self.rdio.method('getTracksForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in track_list ]


class SpotifyArtist(_SpotifyObject, ResolverArtist):
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverArtist.__init__(self)

    @lazyProperty
    def name(self):
        result = self.spotify.lookup(self.key)
        return result['artist']['name']

    @lazyProperty
    def albums(self):
        result = self.spotify.lookup(self.key, "albumdetail")
        album_list = result['artist']['albums']
        return [
            {
                'name':entry['album']['name'],
                'key':entry['album']['href'],
            }
                for entry in album_list
                    if entry['album']['artist'] == self.name and entry['album']['availability']['territories'].find('US') != -1
        ]

    @lazyProperty
    def tracks(self):
        tracks = {}
        for album in self.albums:
            key = album['key']
            result = self.spotify.lookup(key, 'trackdetail')
            track_list = result['album']['tracks']
            for track in track_list:
                track_key = track['href']
                if track_key not in tracks:
                    tracks[track_key] = {
                        'name': track['name'],
                    }
        return list(tracks.values())


class iTunesArtist(_iTunesObject, ResolverArtist):
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
        return [ {'name':album['collectionName']} for album in results if album.pop('collectionType',None) == 'Album' ]

    @lazyProperty
    def tracks(self):
        results = self.itunes.method('lookup',id=self.key,entity='song')['results']
        return [ {'name':track['trackName']} for track in results if track.pop('wrapperType',None) == 'track' ]


class EntityArtist(_EntityObject, ResolverArtist):

    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverArtist.__init__(self)

    @lazyProperty
    def albums(self):
        return [ {'name':album['album_name']} for album in self.entity['albums'] ]

    @lazyProperty
    def tracks(self):
        return [ {'name':song['song_name']} for song in self.entity['songs'] ]

#
#       #       #       ######  #       # #     #
#      # #      #       #     # #       # ##   ##
#     #   #     #       #     # #       # # # # #
#    #     #    #       ######  #       # #  #  #
#   #########   #       #     # #       # #     #
#  #         #  #       #     # #       # #     #
# #           # ####### ######   #######  #     #
#

class ResolverAlbum(ResolverObject):

    @abstractproperty
    def artist(self):
        pass

    @abstractproperty
    def tracks(self):
        pass

    @property 
    def type(self):
        return 'album'

class RdioAlbum(_RdioObject, ResolverAlbum):
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        return { 'name' : self.data['artist'] }

    @lazyProperty
    def tracks(self):
        keys = ','.join(self.data['trackKeys'])
        track_dict = self.rdio.method('get',keys=keys)['result']
        return [ {'name':entry['name']} for k, entry in track_dict.items() ]


class SpotifyAlbum(_SpotifyObject, ResolverAlbum):
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverAlbum.__init__(self)

    @lazyProperty
    def name(self):
        result = self.spotify.lookup(self.key)
        return result['album']['name']

    @lazyProperty
    def artist(self):
        result = self.spotify.lookup(self.key)
        return { 'name': result['album']['artist'] }

    @lazyProperty
    def tracks(self):
        result = self.spotify.lookup(self.key, 'trackdetail')
        track_list = result['album']['tracks']
        return [
            {
                'name':track['name'],
            }
                for track in track_list
        ]


class iTunesAlbum(_iTunesObject, ResolverAlbum):
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
        return [ {'name':track['trackName']} for track in results if track.pop('wrapperType',None) == 'track' ]


class EntityAlbum(_EntityObject, ResolverAlbum):
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        return { 'name' : self.entity['artist_display_name'] }

    @lazyProperty
    def tracks(self):
        return [ {'name':entry.value} for entry in self.entity['tracks'] ]

#
# Tracks
#

class ResolverTrack(ResolverObject):

    @abstractproperty
    def artist(self):
        pass

    @abstractproperty
    def album(self):
        pass

    @abstractproperty
    def length(self):
        pass

    @property 
    def type(self):
        return 'track'


class RdioTrack(_RdioObject, ResolverTrack):
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverTrack.__init__(self)

    @lazyProperty
    def artist(self):
        return {'name':self.data['artist']}

    @lazyProperty
    def album(self):
        return {'name':self.data['album']}

    @lazyProperty
    def length(self):
        return float(self.data['duration'])


class SpotifyTrack(_SpotifyObject, ResolverTrack):
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverTrack.__init__(self)

    @lazyProperty
    def data(self):
        return self.spotify.lookup(self.key)['track']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def artist(self):
        try:
            return {'name': self.data['artists'][0]['name'] }
        except:
            return {'name':''}

    @lazyProperty
    def album(self):
        return {'name':self.data['album']['name']}

    @lazyProperty
    def length(self):
        return float(self.data['length'])


class iTunesTrack(_iTunesObject, ResolverTrack):
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
        except:
            return {'name' : ''}

    @lazyProperty
    def length(self):
        return float(self.data['trackTimeMillis']) / 1000


class EntityTrack(_EntityObject, ResolverTrack):
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


##
# Main Resolver class
##

class Resolver(object):
    """
    """
    def __init__(self):
        pass

    def artistFromEntity(self, entity):
        return EntityArtist(entity)

    def albumFromEntity(self, entity):
        return EntityAlbum(entity)

    def trackFromEntity(self, entity):
        return EntityTrack(entity)

    def setSimilarity(self, a, b):
        if a == b:
            return 1.0
        elif len(b) == 0 or len(a) == 0:
            return 0
        else:
            inter = a & b
            value = math.log(2+len(inter))/math.log(2+len(a))
            if inter == a:
                value = float(1 + value) / 2
            return value 

    def albumSimplify(self, album):
        return _albumSimplify(album)

    def trackSimplify(self, track):
        return _trackSimplify(track)

    def nameSimilarity(self, a, b):
        if len(a) < len(b):
            b, a = a, b
        if a == b:
            return 1.0
        else:
            a = _simplify(a)
            b = _simplify(b)
            if a == b:
                return .90

            if len(a) < len(b):
                b, a = a, b
            index = a.find(b)
            if index == 0:
                return len(b)*.90 / max(len(a),1)
            elif index != -1:
                if a[index-1] == ' ':
                    return len(b)*.70 / max(len(a),1)
                else:
                    return len(b)*.40 / max(len(a),1)
        return 0.0

    def artistSimilarity(self, q, m):
        return self.nameSimilarity(q, m)

    def albumSimilarity(self, q, m):
        return self.nameSimilarity(q, m)

    def trackSimilarity(self, q, m):
        return self.nameSimilarity(q, m)

    def lengthSimilarity(self, q, m):
        diff = abs(q - m)
        return (1 - (float(diff)/max(q, m)))**2

    def __nameWeight(self, a, b):
        la = len(a)
        lb = len(b)
        if la == 0 or lb == 0:
            return 1
        return 2*float(la+lb)/(math.log(la+1)+math.log(lb+1))

    def __lengthWeight(self, q, m):
        #TODO improve
        return 4

    def __setWeight(self, q, m):
        size = len( q | m )
        if size == 0:
            return 1
        weight = float(size)/math.log(size+1)
        if q & m == q:
            weight *= 1.2
        return weight

    def __albumsWeight(self, query, match):
        return self.__setWeight(self.albumsSet(query), self.albumsSet(match))

    def __tracksWeight(self, query, match):
        return self.__setWeight(self.tracksSet(query), self.tracksSet(match))

    def __resolveArtistBatch(self, query, source, start, count, mins):
        results = []
        entries = source(start, count)

        def checkArtist(query, match, mins):
            if _verbose:
                print("Comparing %s and %s" % (match.name,query.name))
            similarities = {}

            similarities['name'] = self.artistSimilarity(query.name, match.name)

            if similarities['name'] >= mins['name']:

                similarities['albums'] = self.albumsSimilarity(query, match)

                if similarities['albums'] >= mins['albums']:

                    similarities['tracks'] = self.tracksSimilarity(query, match)

                    if similarities['tracks']  > mins['tracks']:

                        weights = {
                            'name': self.__nameWeight(query.name, match.name),
                            'albums': self.__albumsWeight(query, match),
                            'tracks': self.__tracksWeight(query, match),
                        }
                        total = 0
                        weight = 0
                        for k,v in weights.items():
                            weight += v
                            total += v * similarities[k]

                        similarities['total'] = total / weight
                        if _verbose:
                            print( "Weights %s: %s" % (match.name, weights))
                            print( 'Similarities for %s: %s' %(match.name, similarities) )

                        similarities['weights'] = weights
                        if similarities['total'] >= mins['total']:
                            results.append((similarities,match))

        pool = Pool(10)
        for entry in entries:
            pool.spawn(checkArtist, query, entry, mins)
        pool.join()

        return results

    def resolveArtist(self, query, source):
        mins = {
            'total' : -1,
            'name' : -1,
            'albums' : -1,
            'tracks' : -1,
        }
        groups = [1, 4, 10, 25]
        results = []
        index = 0
        for i in groups:
            batch = self.__resolveArtistBatch(query, source, index, i , mins)
            for result in batch:
                result[0]['resolved'] = False
            index += i
            results.extend( batch )

            def finalSort(pair):
                return -pair[0]['total']
            results = sorted(results , key=finalSort)
            if len(results) > 0 and results[0][0]['total'] > .7:
                results[0][0]['resolved'] = True
                break

        return results

    def __resolveAlbumBatch(self, query, source, start, count, options):
        results = []
        entries = source(start, count)

        def checkAlbum(query, match, options):
            mins = options['mins']
            if _verbose:
                print("Comparing %s and %s" % (match.name,query.name))
            similarities = {}

            similarities['name'] = self.albumSimilarity(query.name, match.name)
            if similarities['name'] >= mins['name']:

                similarities['artist'] = self.artistSimilarity(query.artist['name'], match.artist['name'])

                if similarities['artist'] >= mins['artist']:

                    similarities['tracks'] = self.tracksSimilarity(query, match)

                    if similarities['tracks']  > mins['tracks']:
                        weights = {
                            'name': self.__nameWeight(query.name, match.name),
                            'artist': self.__nameWeight(query.artist, match.artist),
                            'tracks': self.__tracksWeight(query, match),
                        }
                        total = 0
                        weight = 0
                        for k,v in weights.items():
                            weight += v
                            total += v * similarities[k]

                        similarities['total'] = total / weight
                        if _verbose:
                            print( "Weights %s: %s" % (match.name, weights))
                            print( 'Similarities for %s: %s' %(match.name, similarities) )

                        similarities['weights'] = weights
                        if similarities['total'] >= mins['total']:
                            results.append((similarities,match))
        pool = Pool(10)
        for entry in entries:
            pool.spawn(checkAlbum, query, entry, options)
        pool.join()

        return results

    def resolveAlbum(self, query, source):
        options = {
            'mins': {
                'name':-1,
                'artist':-1,
                'tracks':-1,
                'total':-1,
            }
        }
        groups = [1, 4, 10, 25]
        results = []
        index = 0
        for i in groups:
            batch = self.__resolveAlbumBatch(query, source, index, i , options)
            for result in batch:
                result[0]['resolved'] = False
            index += i
            results.extend( batch )

            def finalSort(pair):
                return -pair[0]['total']
            results = sorted(results , key=finalSort)
            if len(results) > 0 and results[0][0]['total'] > .7:
                results[0][0]['resolved'] = True
                break

        return results

    def __resolveTrackBatch(self, query, source, start, count, options):
        results = []
        entries = source(start, count)

        def checkTrack(query, match, options):
            mins = options['mins']
            if _verbose:
                print("Comparing %s and %s" % (match.name,query.name))
            similarities = {}

            similarities['name'] = self.trackSimilarity(query.name, match.name)
            print(similarities)
            if similarities['name'] >= mins['name']:

                similarities['artist'] = self.artistSimilarity(query.artist['name'], match.artist['name'])
                print(similarities)

                if similarities['artist'] >= mins['artist']:

                    similarities['album'] = self.albumSimilarity(query.album['name'], match.album['name'])
                    print(similarities)

                    if similarities['album']  > mins['album']:

                        similarities['length'] = self.lengthSimilarity(query.length, match.length)
                        print(similarities)

                        if similarities['length'] > mins['length']:
                            weights = {
                                'name': self.__nameWeight(query.name, match.name),
                                'artist': self.__nameWeight(query.artist, match.artist)*2,
                                'album': self.__nameWeight(query.album, match.album)*.3,
                                'length': self.__lengthWeight(query.length, query.length),
                            }
                            total = 0
                            weight = 0
                            for k,v in weights.items():
                                weight += v
                                total += v * similarities[k]

                            similarities['total'] = total / weight
                            if _verbose:
                                print( "Weights %s: %s" % (match.name, weights))
                                print( 'Similarities for %s: %s' %(match.name, similarities) )

                            similarities['weights'] = weights
                            if similarities['total'] >= mins['total']:
                                results.append((similarities,match))
        pool = Pool(10)
        for entry in entries:
            pool.spawn(checkTrack, query, entry, options)
        pool.join()

        return results

    def resolveTrack(self, query, source):
        if _verbose:
            print("Resolving: %s" % query)
        options = {
            'mins': {
                'name':-1,
                'artist':-1,
                'album':-1,
                'length':-1,
                'total':-1,
            }
        }
        groups = [1,4,25,200]
        results = []
        index = 0
        for i in groups:
            batch = self.__resolveTrackBatch(query, source, index, i , options)
            for result in batch:
                result[0]['resolved'] = False
            index += i
            results.extend( batch )

            def finalSort(pair):
                return -pair[0]['total']
            results = sorted(results , key=finalSort)
            if len(results) > 0 and results[0][0]['total'] > .7:
                results[0][0]['resolved'] = True
                break

        return results

    def tracksSet(self, entity):
        return set( [ self.trackSimplify(track['name']) for track in entity.tracks ] )

    def albumsSet(self, entity):
        return set( [ self.albumSimplify(album['name']) for album in entity.albums ] )

    def albumsSimilarity(self, query, match):
        query_album_set = self.albumsSet(query)
        match_album_set = self.albumsSet(match)

        if _verbose:
            diff = sorted(query_album_set ^ match_album_set)
            print('%s Album difference for %s and %s (%s %s vs %s %s)' % (
                len(diff), match.name , query.name, len(match_album_set), match.source, len(query_album_set), query.source
            ))
            for album in diff:
                source = match.source
                if album in query_album_set:
                    source = query.source
                print( "%s: %s" % (source, album))

        return self.setSimilarity(query_album_set, match_album_set)

    def tracksSimilarity(self, query, match):
        query_track_set = self.tracksSet(query)
        match_track_set = self.tracksSet(match)

        if _verbose:
            diff = sorted(query_track_set ^ match_track_set)
            print('%s Track difference for %s and %s (%s %s vs %s %s)' % (
                len(diff), match.name , query.name, len(match_track_set), match.source, len(query_track_set), query.source
            ))
            for track in diff:
                source = match.source
                if track in query_track_set:
                    source = query.source
                print( "%s: %s" % (source, track))

        return self.setSimilarity(query_track_set, match_track_set)

