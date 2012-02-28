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
    from libs.TMDB                  import globalTMDB
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
    from libs.LibUtils              import parseDateString
except:
    report()
    raise

# Debugging and demo flags
_verbose = False
_very_verbose = False

"""
General string formatting, simplification, and mangling methods

removal dicts are used in a modification-based loop to remove certain patterns.
"""


#generally applicable removal patterns
_general_regex_removals = [
    (r'.*(\(.*\)).*'    , [1]),     # a name ( with parens ) anywhere
    (r'.*(\[.*]).*'     , [1]),     # a name [ with brackets ] anywhere
    (r'.*(\(.*)'        , [1]),     # a name ( bad parathetical
    (r'.*(\[.*)'        , [1]),     # a name [ bad brackets
    (r'.*(\.\.\.).*'    , [1]),     # ellipsis ... anywhere
]

# track-specific removal patterns
_track_removals = [
    (r'.*(-.* (remix|mix|version|edit|dub)$)'  , [1]),
]

# album-specific removal patterns
_album_removals = [
    (r'.*((-|,)( the)? remixes.*$)'    , [1]),
    (r'.*(- ep$)'                   , [1]),
    (r'.*( the (\w+ )?remixes$)'     , [1]),
    (r'.*(- remix ep)' , [1]),
    (r'.*(- single$)' , [1]),
]

def regexRemoval(string, patterns):
    """
    Modification-loop pattern removal

    Given a list of (pattern,groups) tuples, attempts to remove any match
    until no pattern matches for a full cycle.

    Multipass safe and partially optimized
    """
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

def format(string):
    """
    Whitespace unification

    Replaces all non-space whitespace with spaces.
    Also ensures single-spacing and no leading or trailing whitespace.

    Multipass safe and partially optimzed
    """
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

def simplify(string):
    """
    General purpose string simplification

    Maps unicode characters to simplified ascii versions.
    Removes parenthesized strings, bracked stings, and ellipsis
    Performs whitespace unification.

    Multipass safe and partially optimized
    """
    string = getSimplifiedTitle(string)
    string = format(string)
    string = regexRemoval(string, _general_regex_removals)
    return format(string)

def trackSimplify(string):
    """
    Track specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
    string = regexRemoval(string, _track_removals)
    return format(string)

def albumSimplify(string):
    """
    Album specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
    string = regexRemoval(string, _album_removals)
    return format(string)

def nameSimplify(string):
    """
    Name (person) specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
    return format(string)


class ResolverObject(object):
    """
    Abstract superclass for all resolver interface objects.

    The Resolver class uses subtypes of ResolverObject to remain
    source agnostic for resolution. These wrapper types provide an
    interface to all of the necessary data needed for query/match
    comparisons.

    All ResolverObject must have a name, key, source, and type:

    name - a string that represents the name of the object (often not unique)
    key - a key that identifies the object to its source (usually unique)
    source - a string that names the source (i.e. tmdb, rdio, etc.)
    type - a string that identifies the type of the object (i.e. track, album, etc.)

    ResolverObjects also typically override their string representation methods to
    provide meaningful, human-readable output.
    """
    
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

class _RdioObject(object):
    """
    Abstract superclass (mixin) for Rdio objects.

    _RdioObjects can be instatiated with either the rdio_id or the rdio data for an entity.
    If both are provided, they must match. extras may be used to retrieve additional data
    when instantiating an object using only its id.

    Attributes:

    data - the type-specific rdio data for the entity
    rdio - an instance of Rdio (API wrapper)
    """

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
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API wrapper)
    """

    def __init__(self, spotify_id, spotify=None):
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


class _TMDBObject(object):
    """
    Abstract superclass (mixin) for TMDB objects.

    _TMDBObjects must be instantiated with their tmdb_id.

    Attributes:

    tmdb - an instance of TMDB (API wrapper)
    info (abstract) - the type-specific TMDB data for the object
    """
    def __init__(self, tmdb_id):
        self.__key = tmdb_id

    @property
    def key(self):
        return self.__key

    @property
    def source(self):
        return "tmdb"

    @lazyProperty
    def tmdb(self):
        return globalTMDB()

    @abstractproperty
    def info(self):
        pass

    def __repr__(self):
        return pformat( self.info )

#
# Artist
#


class ResolverArtist(ResolverObject):
    """
    Interface for Artist objects.

    Attributes:

    albums - a list of artist dicts which must at least contain a 'name' string.
    tracks - a list of track dicts which must at least contain a 'name' string.
    """
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
    """
    Rdio artist wrapper
    """
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
    """
    Spotify artist wrapper
    """
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
        return [ {'name':album['collectionName']} for album in results if album.pop('collectionType',None) == 'Album' ]

    @lazyProperty
    def tracks(self):
        results = self.itunes.method('lookup',id=self.key,entity='song')['results']
        return [ {'name':track['trackName']} for track in results if track.pop('wrapperType',None) == 'track' ]


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
    """
    Interface for album objects

    Attributes:

    artist - an artist dict containing at least a 'name' string.
    tracks - a list of track dicts each containing at least a 'name' string.
    """
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
    """
    Rdio album wrapper
    """
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
    """
    Spotify album wrapper
    """
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
        return [ {'name':track['trackName']} for track in results if track.pop('wrapperType',None) == 'track' ]


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

#
# Tracks
#

class ResolverTrack(ResolverObject):
    """
    Interface for track objects

    Attributes:

    artist - an artist dict containing at least a 'name' string
    album - an album dict containing at least a 'name' string
    length - a number (possibly float) inticating the length of the track in seconds
    """
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
    """
    Rdio track wrapper
    """
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
    """
    Spotify track wrapper
    """
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
        except Exception:
            return {'name':''}

    @lazyProperty
    def album(self):
        return {'name':self.data['album']['name']}

    @lazyProperty
    def length(self):
        return float(self.data['length'])


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


#
# Movie
#

class ResolverMovie(ResolverObject):
    """
    Interface for movie objects

    Attributes:

    cast - a list of actor dicts containing at least 'name' strings and possibly 'character' strings
    director - a director dict containing at least a 'name' string
    date - a datetime indicating the release date or None for unknown
    length - a number indicating the length of the movie in seconds or a negative number (-1) for unknown
    rating - a string indicating the MPAA rating of the movie or '' for unknown
    genres - a list of genre strings
    """
    @abstractproperty
    def cast(self):
        pass

    @abstractproperty
    def director(self):
        pass

    @abstractproperty
    def date(self):
        pass

    @abstractproperty
    def length(self):
        pass

    @property
    def rating(self):
        return None

    @property 
    def genres(self):
        return []

    @property 
    def type(self):
        return 'movie'

#TODO finish
class TMDBMovie(_TMDBObject, ResolverMovie):
    """
    TMDB movie wrapper
    """
    def __init__(self, tmdb_id):
        _TMDBObject.__init__(self, tmdb_id)
        ResolverMovie.__init__(self)

    @lazyProperty
    def info(self):
        return self.tmdb.movie_info(self.key)

    @lazyProperty
    def castsRaw(self):
        return self.tmdb.movie_casts(self.key)

    @lazyProperty
    def cast(self):
        return [
            {
                'name':entry['name'],
                'character':entry['character'],
                'source':self.source,
                'key':entry['id'],
            }
                for entry in self.castsRaw['cast']
        ]

    @lazyProperty
    def directory(self):
        try:
            crew = self.castsRaw['crew']
            for entry in crew:
                if entry['job'] == 'Directory':
                    return {
                        'name': entry['name'],
                        'source': self.source,
                        'key': entry['id'],
                    }
        except Exception:
            pass
        return { 'name':'' }

    @lazyProperty
    def date(self):
        try:
            string = self.info['release_date']
            return parseDateString(string)
        except KeyError:
            pass
        return None

    @lazyProperty
    def length(self):
        try:
            return self.info['runtime'] * 60
        except Exception:
            pass
        return -1

    @lazyProperty 
    def genres(self):
        try:
            return [ entry['name'] for entry in self.info['genres'] ]
        except KeyError:
            logs.info('no genres for %s (%s:%s)' % (self.name, self.source, self.key))
            return []

##
# Main Resolver class
##

class Resolver(object):
    """
    The central resolve utility class

    The Resolver class embodies the algorithms for many types of generic and fuzzy comparisons,
    as well as several high-level resolve methods for the specific object types defined in this module.

    Most Resolver methods use an options dict to customize behavior but
    Methods with public names can be safely overriden (assuming they present the same interface) in 
    subclasses to customize behavior.

    Resolver objects are virtually stateless so many can be instatiated or a few can be shared.
    """
    def __init__(self):
        pass

    def artistFromEntity(self, entity):
        """
        ResolverArtist factory method for entities.

        This method may or may not return a simple EntityArtist or
        it could return a different implementation of ResolverArtist.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, the Resolver may be
        able to safely enrich it.
        """
        return EntityArtist(entity)

    def albumFromEntity(self, entity):
        """
        ResolverAlbum factory method for entities.

        This method may or may not return a simple EntityAlbum or
        it could return a different implementation of ResolverAlbum.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, the Resolver may be
        able to safely enrich it.
        """
        return EntityAlbum(entity)

    def trackFromEntity(self, entity):
        """
        ResolverTrack factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, the Resolver may be
        able to safely enrich it.
        """
        return EntityTrack(entity)

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
        else:
            raise ValueError('Unrecognized subcategory %s for %s' % (sub, entity['title']))

    def setSimilarity(self, a, b):
        """
        Generic similarity of two sets.

        This method does not make any assumptions about set
        members except equality.
        """
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
        """
        Reduces an album name to a simplied form for fuzzy comparison.
        """
        return albumSimplify(album)

    def trackSimplify(self, track):
        """
        Reduces a track name to a simplied form for fuzzy comparison.
        """
        return trackSimplify(track)

    def actorSimplify(self, actor):
        """
        Reduces an actor name to a simplied form for fuzzy comparison.
        """
        return nameSimplify(actor)

    def nameSimilarity(self, a, b):
        """
        Generic fuzzy name comparison.

        Returns a similarity decimal [0,1]
        """
        if len(a) < len(b):
            b, a = a, b
        if a == b:
            return 1.0
        else:
            a = simplify(a)
            b = simplify(b)
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
        """
        Artist specific similarity metric.
        """
        return self.nameSimilarity(q, m)

    def albumSimilarity(self, q, m):
        """
        Album specific similarity metric.
        """
        return self.nameSimilarity(q, m)

    def trackSimilarity(self, q, m):
        """
        Track specific similarity metric.
        """
        return self.nameSimilarity(q, m)

    def movieSimilarity(self, q, m):
        """
        Movie specific similarity metric.
        """
        return self.nameSimilarity(q, m)

    def lengthSimilarity(self, q, m):
        """
        length specific similarity metric.
        """
        diff = abs(q - m)
        return (1 - (float(diff)/max(q, m)))**2

    def checkArtist(self, results, query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.artistSimilarity(q.name, m.name)),
            ('albums', lambda q, m, s, o: self.albumsSimilarity(q, m)),
            ('tracks', lambda q, m, s, o: self.tracksSimilarity(q, m)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'albums': lambda q, m, s, o: self.__albumsWeight(q, m),
            'tracks': lambda q, m, s, o: self.__tracksWeight(q, m),
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def checkAlbum(self, results, query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.albumSimilarity(q.name, m.name)),
            ('artist', lambda q, m, s, o: self.artistSimilarity(q.artist['name'], m.artist['name'])),
            ('tracks', lambda q, m, s, o: self.tracksSimilarity(q, m)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'artist': lambda q, m, s, o: self.__nameWeight(q.artist, m.artist),
            'tracks': lambda q, m, s, o: self.__tracksWeight(q, m),
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def checkTrack(self, results, query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.trackSimilarity(q.name, m.name)),
            ('artist', lambda q, m, s, o: self.artistSimilarity(q.artist['name'], m.artist['name'])),
            ('album', lambda q, m, s, o: self.albumSimilarity(q.album['name'], m.album['name'])),
            ('length', lambda q, m, s, o: self.lengthSimilarity(q.length, m.length)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'artist': lambda q, m, s, o: self.__nameWeight(q.artist, m.artist)*2,
            'album': lambda q, m, s, o: self.__nameWeight(q.album, m.album)*.3,
            'length': lambda q, m, s, o: self.__lengthWeight(q.length, m.length),
        }
        self.genericCheck(tests, weights, results, query, match, options)


    def checkMovie(query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.movieSimilarity(q.name, m.name)),
            ('cast', lambda q, m, s, o: self.castSimilarity(q, m)),
            ('director', lambda q, m, s, o: self.directorSimilarity(q, m)),
            ('length', lambda q, m, s, o: self.lengthSimilarity(q, m)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'cast': lambda q, m, s, o: self.__castWeight(q, m),
            'director': lambda q, m, s, o: self.__nameWeight(q.director, m.director),
            'length': lambda q, m, s, o: self.__lengthWeight(q.length, m.length),
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def genericCheck(self, tests, weights, results, query, match, options):
        mins = options['mins']
        if _verbose:
            print("Comparing %s and %s" % (match.name,query.name))
        success, similarities = self.__compareAll(query, match, tests, options)
        if success:
            self.__addTotal(similarities, weights, query, match, options)
            if similarities['total'] >= mins['total']:
                results.append((similarities,match))

    def resolve(self, query, source, **options):
        options = self.parseGeneralOptions(query, options)
        results = []
        index = 0
        for i in options['groups']:
            batch = self.__resolveBatch(options['check'], query, source, (index, i) , options)
            index += i
            results = self.__sortedPairs(results, batch)
            if self.__shouldFinish(query, results, options):
                break
        results = self.__finish(query, results, options)
        return results

    def tracksSet(self, entity):
        return set( [ self.trackSimplify(track['name']) for track in entity.tracks ] )

    def albumsSet(self, entity):
        return set( [ self.albumSimplify(album['name']) for album in entity.albums ] )

    def castSet(self, entity):
        return set( [ self.actorSimplify(actor['name']) for actor in entity.cast ] )

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

    def castSimilarity(self, query, match):
        query_cast_set = self.castSet(query)
        match_cast_set = self.castSet(match)

        if _verbose:
            self.__differenceLog('Cast', query_cast_set, match_cast_set, query, match)

        return self.setSimilarity(query_track_set, match_track_set)


    def parseGeneralOptions(self, query, options):
        """
        Most high level methods in this class accept an options dict as a means of customization.

        The following options are recognized:

        count -  a positive integer indicating the desired minimum result size (results may be smaller if the source is limited)
        max - a positive integer that sets the maximum number of results to return
        resolvedSimilarity -  a float which indicates a simple cutoff total similarity to consider something resolved
        pool - a positive integer indicating the size of the gevent pool to be used (use 1 for sequential)
        mins - an attribute-similarity dict which can be used to prune matches (useful for reducing execution time)
        """
        if 'count' not in options:
            options['count'] = 1
        if 'max' not in options:
            options['max'] = 1000000
        if 'resolvedSimilarity' not in options:
            options['resolvedSimilarity'] = .7
        if 'pool' not in options:
            options['pool'] = 10
        if 'mins' not in options:
            if query.type == 'album':
                options['mins'] = {
                    'name':-1,
                    'artist':-1,
                    'tracks':-1,
                    'total':-1,
                }
            elif query.type == 'track':
                options['mins'] = {
                    'name':-1,
                    'artist':-1,
                    'album':-1,
                    'length':-1,
                    'total':-1,
                }
            elif query.type == 'artist':
                options['mins'] = {
                    'name':-1,
                    'albums':-1,
                    'tracks':-1,
                    'total':-1,
                }
            elif query.type == 'movie':
                options['mins'] = {
                    'name':-1,
                    'cast':-1,
                    'director':-1,
                    'releaseDate':-1,
                    'length':-1,
                    'rating':-1,
                    'genres':-1,
                }
            else:
                #generic
                options['mins'] = {
                    'name':-1,
                }
        if 'groups' not in options:
            groups = [options['count']]
            if query.type == 'artist':
                groups.extend([4, 20, 30])
            elif query.type == 'album':
                groups.extend([10, 20, 50])
            elif query.type == 'track':
                groups.extend([20, 50, 100])
            elif query.type == 'movie':
                groups.extend([10, 20, 50]) 
            else:
                #generic
                groups.extend([10, 20, 50]) 
            options['groups'] = groups
        if 'check' not in options:
            if query.type =='track':
                options['check'] = self.checkTrack
            elif query.type =='album':
                options['check'] = self.checkAlbum
            elif query.type =='artist':
                options['check'] = self.checkArtist
            else:
                #no generic test
                raise ValueError("no test for %s (%s)" % (query.name, query.type))

        return options

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

    def __sortedPairs(self, results, batch):
        results.extend(batch)
        def pairSort(pair):
            return -pair[0]['total']
        return sorted(results , key=pairSort)

    def __resolveBatch(self, check, query, source, section, options):
        start, count = section
        results = []
        entries = source(start, count)
        pool = Pool(options['pool'])
        for entry in entries:
            pool.spawn(check, results, query, entry, options)
        pool.join()

        return results

    def __compareAll(self, query, match, tests, options):
        similarities = {}
        if 'mins' in options:
            mins = options['mins']
        else:
            mins = {}
        success = True
        for name,test in tests:
            similarity = test(query, match, similarities, options)
            similarities[name] = similarity
            if name in mins and similarity < mins[name]:
                success = False
                break
        return (success, similarities)

    def __shouldFinish(self, query, results, options):
        if len(results) >= options['max']:
            return True
        elif len(results) < options['count']:
            return False
        else:
            cutoff = options['resolvedSimilarity']
            if results[0][0]['total'] >= cutoff:
                return True
        return False

    def __finish(self, query, results, options):
        for result in results:
            result[0]['resolved'] = False
        if len(results) > 0 and results[0][0]['total'] > options['resolvedSimilarity']:
            results[0][0]['resolved'] = True
        return results

    def __addTotal(self, similarities, weights, query, match, options):
        total = 0
        weight = 0
        actual_weights = {}
        for k,f in weights.items():
            v = f(query, match, similarities, options)
            weight += v
            total += v * similarities[k]
            actual_weights[k] = v

        similarities['total'] = total / weight
        similarities['weights'] = actual_weights

    def __logSimilarities(self, similarities, query, match):
        print( 'Similarities for %s:\n%s' %(match.name, pformat(similarities) ) )

    def __differenceLog(self, label, query_set, match_set, query, match):
        diff = sorted(query_set ^ match_set)
        print('%s %s difference for %s and %s (%s %s vs %s %s)' % (
            len(diff), label, match.name , query.name, len(match_set), match.source, len(query_set), query.source
        ))
        for item in diff:
            source = match.source
            if item in query_set:
                source = query.source
            print( "%s: %s" % (source, item))

def demo(generic_source, default_title):
    import sys

    title = default_title
    subcategory = None
    count = 1

    resolver = Resolver()

    print(sys.argv)
    if len(sys.argv) > 1:
        title = sys.argv[1]
    if len(sys.argv) > 2:
        subcategory = sys.argv[2]
    if len(sys.argv) > 3:
        count = int(sys.argv[3])

    _verbose = True
    from MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db = api._entityDB
    query = {'title':title}
    if subcategory is not None:
        query['subcategory'] = subcategory
    cursor = db._collection.find(query)
    if cursor.count() == 0:
        print("Could not find a matching entity for %s" % title)
        return
    result = cursor[0]
    entity = db._convertFromMongo(result)
    query = resolver.wrapperFromEntity(entity)
    results = resolver.resolve(query, generic_source.matchSource(query), count=1)
    pprint(results)
