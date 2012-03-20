#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [
    'Resolver',
    'ResolverObject',
    'ResolverProxy',
    'SimpleResolverObject',
    'ResolverSearchAll',
    'ResolverArtist',
    'ResolverAlbum',
    'ResolverTrack',
    'SimpleResolverTrack',
    'ResolverMovie',
    'ResolverBook',
    'demo',
    'regexRemoval',
    'simplify',
    'format',
    'trackSimplify',
    'albumSimplify',
    'artistSimplify',
    'movieSimplify',
    'bookSimplify',
    'nameSimplify',
]

import Globals
from logs import report

try:
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    import re
    from pprint                     import pprint, pformat
    import sys
    from Entity                     import getSimplifiedTitle
    from gevent.pool                import Pool
    import math
    from abc                        import ABCMeta, abstractmethod, abstractproperty
    from libs.LibUtils              import parseDateString
    from datetime                   import datetime
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
    (r".*(').*"         , [1]),
    (r'.*(").*'         , [1]),
]

# track-specific removal patterns
_track_removals = [
    (r'^(the ).*$'      , [1]),
    (r'.*(-.* (remix|mix|version|edit|dub)$)'  , [1]),
]

# album-specific removal patterns
_album_removals = [
    (r'^(the ).*$'      , [1]),
    (r'.*((-|,)( the)? remixes.*$)'    , [1]),
    (r'.*(- ep$)'                   , [1]),
    (r'.*( the (\w+ )?remixes$)'     , [1]),
    (r'.*(- remix ep)' , [1]),
    (r'.*(- single$)' , [1]),
]

# artist-specific removal patterns
_artist_removals = [
    (r'^(the ).*$'      , [1]),
    (r'^.*( band)'      , [1]),
]

# movie-specific removal patterns
_movie_removals = [
    (r'^(the ).*$'      , [1]),
    (r'^.*( band)'      , [1]),
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

def artistSimplify(string):
    """
    Album specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
    string = regexRemoval(string, _artist_removals)
    return format(string)

def movieSimplify(string):
    """
    Movie specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
    return format(string)

def bookSimplify(string):
    """
    book specific simplification for fuzzy comparisons.

    Multipass safe and partially optimized
    """
    string = simplify(string)
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

    @property
    def keywords(self):
        return []
    
    @property 
    def related_terms(self):
        return []

    @property 
    def description(self):
        return ''

    @property 
    def url(self):
        return None

    @property 
    def priority(self):
        return 0

class ResolverProxy(object):

    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @lazyProperty
    def name(self):
        return self.target.name

    @lazyProperty
    def url(self):
        return self.target.url

    @lazyProperty
    def key(self):
        return self.target.key

    @property 
    def source(self):
        return self.target.source

    def __repr__(self):
        return "ResolverProxy:%s" % str(self.target)

    @property
    def keywords(self):
        return self.target.keywords
    
    @property
    def name(self):
        return self.target.name

    @property 
    def priority(self):
        return self.target.type

    @property 
    def related_terms(self):
        return self.target.related_terms

class SimpleResolverObject(ResolverObject):

    def __init__(self, **data):
        self.__data = data

    @property
    def data(self):
        return self.__data

    @lazyProperty
    def name(self):
        try:
            return str(self.data['name'])
        except KeyError:
            return ''

    @lazyProperty
    def key(self):
        try:
            return str(self.data['key'])
        except KeyError:
            return ''

    @lazyProperty
    def source(self):
        try:
            return str(self.data['source'])
        except KeyError:
            return ''

    @property
    def description(self):
        try:
            return str(self.data['description'])
        except KeyError:
            return ''

    @property 
    def url(self):
        try:
            return str(self.data['url'])
        except KeyError:
            return None


class ResolverSearchAll(ResolverObject):
    """
    Interface for Artist objects.

    Attributes:

    albums - a list of artist dicts which must at least contain a 'name' string.
    tracks - a list of track dicts which must at least contain a 'name' string.
    """

    @property
    def coordinates(self):
        return None

    @abstractproperty
    def query_string(self):
        pass

    @property
    def subcategory(self):
        return None

    @property 
    def type(self):
        return 'search_all'

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
    def genres(self):
        return []
        
    @property 
    def type(self):
        return 'artist'


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
    def genres(self):
        return []

    @property 
    def type(self):
        return 'album'


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
    def genres(self):
        return []

    @property
    def date(self):
        return None

    @property 
    def type(self):
        return 'track'

class SimpleResolverTrack(SimpleResolverObject):
    """
    """
    def __init__(self, **data):
        SimpleResolverObject.__init__(self, **data)

    @lazyProperty
    def artist(self):
        try:
            return self.data['artist']
        except KeyError:
            return {'name':''}

    @lazyProperty
    def album(self):
        try:
            return self.data['album']
        except KeyError:
            return {'name':''}

    @lazyProperty
    def length(self):
        try:
            return float(self.data['length'])
        except Exception:
            return -1

    @lazyProperty
    def genres(self):
        try:
            return self.data['genres']
        except KeyError:
            return []

    @lazyProperty
    def date(self):
        try:
            return self.data['date']
        except KeyError:
            return None

    @property 
    def type(self):
        return 'track'

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
    @property
    def cast(self):
        return []

    @property
    def director(self):
        return {'name':''}

    @property
    def date(self):
        return None

    @property
    def length(self):
        return -1

    @property
    def rating(self):
        return None

    @property 
    def genres(self):
        return []

    @property 
    def type(self):
        return 'movie'


#
# Books
#

class ResolverBook(ResolverObject):
    """
    Interface for track objects

    Attributes:

    author - an author dict containing at least a 'name' string
    publisher - an publisher dict containing at least a 'name' string
    length - a number (possibly float) inticating the length of the book in pages
    """
    @abstractproperty
    def author(self):
        pass

    @abstractproperty
    def publisher(self):
        pass

    @property
    def date(self):
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

    @property 
    def type(self):
        return 'book'

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
    def __init__(self,verbose=False):
        self.__verbose = verbose

    @property 
    def verbose(self):
        return self.__verbose

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

    def artistSimplify(self, artist):
        """
        Reduces an artist name to a simplied form for fuzzy comparison.
        """
        return artistSimplify(artist)

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
        if a is None or b is None:
            return 0
        if a == '' or b == '':
            return 0
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
        if q <= 0 or m <= 0:
            return 0
        diff = abs(q - m)
        return (1 - (float(diff)/max(q, m)))**2

    def dateSimilarity(self, q, m):
        """
        Date specific similarity metric.
        """
        if q is None or m is None:
            return 0
        diff = abs((q - m).days)
        v = 0
        if diff <= 1:
            v = 1.0
        elif diff <= 31:
            v = .90
        elif diff <= 100:
            v = .80
        elif diff <= 365:
            v = .70
        elif diff <= 700:
            v = .30
        else:
            v = 0
        if q.year != m.year:
            v *= .8
        return v

    def directorSimilarity(self, q, m):
        """
        Director specific similarity metric.
        """
        return self.nameSimilarity(q['name'], m['name'])

    def authorSimilarity(self, q, m):
        """
        Author specific similarity metric.
        """
        return self.nameSimilarity(q['name'], m['name'])

    def publisherSimilarity(self, q, m):
        """
        Publisher specific similarity metric.
        """
        return self.nameSimilarity(q['name'], m['name'])

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


    def checkMovie(self, results, query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.movieSimilarity(q.name, m.name)),
            ('cast', lambda q, m, s, o: self.castSimilarity(q, m)),
            ('director', lambda q, m, s, o: self.directorSimilarity(q.director, m.director)),
            ('length', lambda q, m, s, o: self.lengthSimilarity(q.length, m.length)),
            ('date', lambda q, m, s, o: self.dateSimilarity(q.date, m.date)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name,exact_boost=2.0),
            'cast': lambda q, m, s, o: self.__castWeight(q, m),
            'director': lambda q, m, s, o: self.__nameWeight(q.director['name'], m.director['name']),
            'length': lambda q, m, s, o: self.__lengthWeight(q.length, m.length,q_empty=.2) * 3,
            'date': lambda q, m, s, o: self.__dateWeight(q.date, m.date,exact_boost=4),
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def checkBook(self, results, query, match, options):
        tests = [
            ('name', lambda q, m, s, o: self.movieSimilarity(q.name, m.name)),
            ('author', lambda q, m, s, o: self.authorSimilarity(q.author, m.author)),
            ('publisher', lambda q, m, s, o: self.publisherSimilarity(q.publisher, m.publisher)),
            ('length', lambda q, m, s, o: self.lengthSimilarity(q.length, m.length)),
            ('date', lambda q, m, s, o: self.dateSimilarity(q.date, m.date)),
        ]
        weights = {
            'name': lambda q, m, s, o: self.__nameWeight(q.name, m.name, exact_boost=1.5),
            'author': lambda q, m, s, o: self.__nameWeight(q.author['name'], m.author['name'],
                exact_boost=3, m_empty=7 ),
            'publisher': lambda q, m, s, o: self.__nameWeight(q.publisher['name'], m.publisher['name'],
                exact_boost=2, m_empty=4 ),
            'length': lambda q, m, s, o: self.__lengthWeight(q.length, m.length) * .5,
            'date': lambda q, m, s, o: self.__dateWeight(q.date, m.date) * .2,
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def checkSearchAll(self, results, query, match, options):
        tests = [
            ('query_string', self.__queryStringTest),
            ('title',self.__titleTest),
            ('location', self.__locationTest),
            ('subcategory', self.__subcategoryTest),
            ('priority', lambda q, m, s, o: m.priority),
            ('source_priority', lambda q, m, s, o: 1),
            ('keywords', self.__keywordsTest),
            ('related_terms', self.__relatedTermsTest),

        ]
        weights = {
            ('query_string', lambda q, m, s, o: 1),
            ('title',lambda q, m, s, o: 1),
            ('location', lambda q, m, s, o: 1),
            ('subcategory', lambda q, m, s, o: 1),
            ('priority', lambda q, m, s, o: 1),
            ('source_priority', lambda q, m, s, o: self.__sourceWeight(m.source)),
            ('keywords', lambda q, m, s, o: 1),
            ('related_terms', lambda q, m, s, o: 1),
        }
        self.genericCheck(tests, weights, results, query, match, options)

    def genericCheck(self, tests, weights, results, query, match, options):
        mins = options['mins']
        if self.verbose:
            print("Comparing %s and %s" % (match.name,query.name))
        success, similarities = self.__compareAll(query, match, tests, options)
        if success:
            self.__addTotal(similarities, weights, query, match, options)
            if 'total' not in mins or similarities['total'] >= mins['total']:
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

        if self.verbose:
            self.__differenceLog('Album', query_album_set, match_album_set, query, match)

        return self.setSimilarity(query_album_set, match_album_set)

    def tracksSimilarity(self, query, match):
        query_track_set = self.tracksSet(query)
        match_track_set = self.tracksSet(match)

        if self.verbose:
            self.__differenceLog('Track', query_track_set, match_track_set, query, match)

        return self.setSimilarity(query_track_set, match_track_set)

    def castSimilarity(self, query, match):
        query_cast_set = self.castSet(query)
        match_cast_set = self.castSet(match)

        if self.verbose:
            self.__differenceLog('Cast', query_cast_set, match_cast_set, query, match)

        return self.setSimilarity(query_cast_set, match_cast_set)


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
                groups.extend([5, 10, 50])
            elif query.type == 'track':
                groups.extend([20, 50, 100])
            elif query.type == 'movie':
                groups.extend([10, 20, 50]) 
            elif query.type == 'book':
                groups.extend([20, 50, 100])
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
            elif query.type =='movie':
                options['check'] = self.checkMovie
            elif query.type =='book':
                options['check'] = self.checkBook
            elif query.type == 'search_all':
                options['check'] = self.checkSearchAll
            else:
                #no generic test
                raise ValueError("no test for %s (%s)" % (query.name, query.type))

        return options

    def __nameWeight(self, a, b, exact_boost=1, q_empty=1, m_empty=1, both_empty=1):
        if a is None or b is None:
            return 1
        la = len(a)
        lb = len(b)
        if la == 0:
            if lb == 0:
                return both_empty
            else:
                return q_empty
        elif lb == 0:
            return m_empty
        weight = 2*float(la+lb)/(math.log(la+1)+math.log(lb+1))
        if a == b:
            weight = exact_boost * weight
        return weight

    def __lengthWeight(self, q, m, exact_boost=1, q_empty=1, m_empty=1, both_empty=1):
        if q < 0:
            if m < 0:
                return both_empty
            else:
                return q_empty
        elif m < 0:
            return m_empty
        #TODO
        weight = 4
        if q == m:
            weight = exact_boost * weight
        return weight

    def __dateWeight(self, q, m, exact_boost=1, q_empty=1, m_empty=1, both_empty=1):
        if q is None:
            if m is None:
                return both_empty
            else:
                return q_empty
        elif m is None:
            return m_empty
        #TODO
        weight = 4
        if q == m:
            weight = exact_boost * weight
        return weight

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

    def __castWeight(self, query, match):
        if query.cast == []:
            return 1
        else:
            return self.__setWeight(self.castSet(query), self.castSet(match))

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
    """
    Generic command-line demo function

    usage:
    python SOURCE_MODULE.py [ title [ subcategory [ count ] ] ]

    This demo queries the EntityDB for an entity matching the
    given title (or default_title). If a subcategory is given,
    the query is restricted to that category. Othewise, the
    query is title-based and the type is determined by the 
    results subcategory.

    Once an entity is selected, it is converted to a query and
    resolved against the given source, with extemely verbose 
    output enabled (not necessarilly to logger, possibly stdout).
    The count option (1 by default) will be passed to resolve.

    If the entity was successfully resolved, demo() will attempt to
    invert it using a StampedSource. The result of this inversion 
    will also be verbosely outputted. 
    """
    _verbose = True
    import sys
    import StampedSource

    title = default_title
    subcategory = None
    count = 1

    resolver = Resolver(verbose=True)
    entity_source = StampedSource.StampedSource()
    index = 0

    print(sys.argv)
    if len(sys.argv) > 1:
        title = sys.argv[1]
    if len(sys.argv) > 2:
        subcategory = sys.argv[2]
    if len(sys.argv) > 3:
        count = int(sys.argv[3])
    if len(sys.argv) > 4:
        index = int(sys.argv[3])

    from MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db = api._entityDB
    query = {'title':title}
    if subcategory is not None:
        query['subcategory'] = subcategory
    else:
        query = {
            '$or': [
                { 'mangled_title' : simplify(title) },
                { 'title' : title },
            ]
        }
    pprint(query)
    cursor = db._collection.find(query)
    if cursor.count() <= index:
        print("Could not find a matching entity for %s" % title)
        return
    result = cursor[index]
    entity = db._convertFromMongo(result)
    query = entity_source.wrapperFromEntity(entity)
    results = resolver.resolve(query, generic_source.matchSource(query), count=count)
    pprint(results)
    print("\n\nFinal result:\n")
    print(query)
    if len(results) > 0:
        best = results[0]
        pprint(best[0])
        pprint(best[1])
        if best[0]['resolved']:
            print("\nAttempting to invert")
            new_query = best[1]
            new_results = resolver.resolve(new_query, entity_source.matchSource(new_query), count=1)
            print('Inversion results:\n%s' % pformat(new_results) )
            if len(new_results) > 0 and new_results[0][0]['resolved']:
                best = new_results[0][1]
                if best.key == query.key:
                    print("Inversion succesful")
                else:
                    print("Inverted to different entity! (dup or false positive)")
            else:
                print("Inversion failed! (low asymetric similarity?)")

    else:
        print("No results")
