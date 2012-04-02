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
    'ResolverPlace',
    'SimpleResolverTrack',
    'ResolverMovie',
    'ResolverBook',
    'ResolverTVShow',
    'ResolverApp',
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
    'stringComparison',
    'setComparison',
    'sortedResults',
    'formatResults',
    'typeToSubcategory',
]

import Globals
from logs import report

try:
    import utils, re, string
    import logs, sys, math
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    from pprint                     import pprint, pformat
    from Entity                     import getSimplifiedTitle
    from gevent.pool                import Pool
    from abc                        import ABCMeta, abstractmethod, abstractproperty
    from libs.LibUtils              import parseDateString
    from datetime                   import datetime
    from difflib                    import SequenceMatcher
    from time                       import time
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
    (re.compile(r'.*(\(.*\)).*')    , [1]),     # a name ( with parens ) anywhere
    (re.compile(r'.*(\[.*]).*')     , [1]),     # a name [ with brackets ] anywhere
    (re.compile(r'.*(\(.*)')        , [1]),     # a name ( bad parathetical
    (re.compile(r'.*(\[.*)')        , [1]),     # a name [ bad brackets
    (re.compile(r'.*(\.\.\.).*')    , [1]),     # ellipsis ... anywhere
    (re.compile(r".*(').*")         , [1]),
    (re.compile(r'.*(").*')         , [1]),
    (re.compile(r'^(the ).*$')      , [1]),
]

#generally applicable replacements
_general_replacements = [
    ('&', ' and '),                             # canonicalize synonyms
]

# track-specific removal patterns
_track_removals = [
    (re.compile(r'^(the ).*$')      , [1]),
    (re.compile(r'.*(-.* (remix|mix|version|edit|dub|tribute|cover|bpm)$)')  , [1]),
]

# album-specific removal patterns
_album_removals = [
    (re.compile(r'^(the ).*$')      , [1]),
    (re.compile(r'.*((-|,)( the)? remixes.*$)')     , [1]),
    (re.compile(r'.*(- ep$)')                       , [1]),
    (re.compile(r'.*( the (\w+ )?remixes$)')        , [1]),
    (re.compile(r'.*(- remix ep)')  , [1]),
    (re.compile(r'.*(- single$)')   , [1]),
]

# artist-specific removal patterns
_artist_removals = [
    (re.compile(r'^(the ).*$')      , [1]),
    (re.compile(r'^.*( band)')      , [1]),
]

# movie-specific removal patterns
_movie_removals = [
    # TODO - unimplemented and unused
]

# blacklist words and score
_negative_weights = {
    'remix'         : 0.1,
    're-mix'        : 0.1,
    'mix'           : 0.1,
    'cover'         : 0.2,
    'tribute'       : 0.2,
    'version'       : 0.1,
    'audiobook'     : 0.2,
    'instrumental'  : 0.1,
    'karaoke'       : 0.2,
    'vhs'           : 0.2,
    'dvd'           : 0.2,
    'blu-ray'       : 0.2,
    'bluray'        : 0.2,
    'season'        : 0.1,
    'edition'       : 0.05,
}

punctuation_re = re.compile('[%s]' % re.escape(string.punctuation))

_subcategory_weights = {
    # --------------------------
    #           food
    # --------------------------
    'restaurant'        : 100, 
    'bar'               : 90, 
    'bakery'            : 70, 
    'cafe'              : 70, 
    'market'            : 60, 
    'food'              : 70, 
    'night_club'        : 75, 
    'place'             : 80, 
    
    # --------------------------
    #           book
    # --------------------------
    'book'              : 50, 
    
    # --------------------------
    #           film
    # --------------------------
    'movie'             : 65, 
    'tv'                : 60, 
    
    # --------------------------
    #           music
    # --------------------------
    'artist'            : 55, 
    'song'              : 25, 
    'album'             : 45, 
    
    # --------------------------
    #           other
    # --------------------------
    'app'               : 65, 
    'other'             : 5, 
    
    # the following subcategories are from google places
    'amusement_park'    : 25, 
    'aquarium'          : 25, 
    'art_gallery'       : 25, 
    'beauty_salon'      : 15, 
    'book_store'        : 15, 
    'bowling_alley'     : 25, 
    'campground'        : 20, 
    'casino'            : 25, 
    'clothing_store'    : 20, 
    'department_store'  : 20, 
    'establishment'     : 5, 
    'florist'           : 15, 
    'gym'               : 10, 
    'home_goods_store'  : 5, 
    'jewelry_store'     : 15, 
    'library'           : 5, 
    'liquor_store'      : 10, 
    'lodging'           : 45, 
    'movie_theater'     : 45, 
    'museum'            : 70, 
    'park'              : 50, 
    'school'            : 25, 
    'shoe_store'        : 20, 
    'shopping_mall'     : 20, 
    'spa'               : 25, 
    'stadium'           : 25, 
    'store'             : 15, 
    'university'        : 65, 
    'zoo'               : 65, 
    
    # the following subcategories are from amazon
    'video_game'        : 65
}

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
                match = pattern.match(string)
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
            string2 = string.replace(ch, ' ')
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
    
    for find, replacement in _general_replacements:
        string = string.replace(find, replacement)
    
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
    return format(simplify(string))

def stringComparison(a, b, strict=False):
    """
    Generic fuzzy string comparison.

    Returns a comparison decimal [0,1]
    """
    if not strict:
        a = simplify(a)
        b = simplify(b)
    
    if a == b:
        return 1.0
    else:
        junk_to_ignore = " \t-.;&".__contains__ # characters for SequenceMatcher to disregard
        return SequenceMatcher(junk_to_ignore, a, b).ratio()

def setComparison(a, b, symmetric=False, strict=False):
    """
    Generic comparison of two sets.
    
    This method does not make any assumptions about set
    members except equality.
    
    assymetric - denotes if a and b are interchangable
    strict - avoid fuzzy matching, etc.
    """
    
    def cleanSet(s):
        clean = set()
        for i in s:
            clean.add(simplify(i).lower())
        return clean
    
    def symmetricComparion(a, b):
        return (asymmetricComparison(a, b) + asymmetricComparison(b, a)) / 2.0
    
    def asymmetricComparison(a, b):
        score = 0
        total = 0
        
        for x in a:
            total = total + len(x)
            if x in b:
                score = score + len(x)
            else:
                x_score = 0
                for y in b:
                    xy_score = stringComparison(x, y, strict=strict)
                    if xy_score > x_score:
                        x_score = xy_score
                
                score = score + x_score 
        
        if total <= 0:
            return 0
        
        return 1.0 * score / total
    
    if not strict:
        a = cleanSet(a)
        b = cleanSet(b)
    
    if a == b:
        return 1.0
    
    if len(b) == 0 or len(a) == 0:
        return 0
    
    if symmetric:
        return symmetricComparion(a, b)
    else:
        return asymmetricComparison(a, b)

def weightedDictComparison(a, b, symmetric=False, strict=False):
    def _simplifyDict(d):
        clean = {}
        for k, v in d.iteritems():
            k2 = simplify(k).lower()
            clean[k2] = v
        return clean
    
    def _symmetricComparison(a, b):
        return (_asymmetricComparison(a, b) + _asymmetricComparison(b, a)) / 2.0
    
    def _asymmetricComparison(a, b):
        score = 0.0
        total = 0.0
        
        for x, wa in a.iteritems():
            value  = 0.0
            weight = 0.0
            
            try:
                weight = b[x]
                value  = 1.0
            except KeyError:
                for y, wb in b.iteritems():
                    xy_value = stringComparison(x, y, strict=strict)
                    
                    if xy_value > value:
                        value  = xy_value
                        weight = wb
            
            weight *= wa
            score  += value * weight
            total  += weight
        
        if total <= 0:
            return 0.0
        
        return score / total
    
    if not strict:
        a = _simplifyDict(a)
        b = _simplifyDict(b)
    
    if len(b) == 0 or len(a) == 0:
        return 0
    
    if symmetric:
        return _symmetricComparion(a, b)
    else:
        return _asymmetricComparison(a, b)

def sortedResults(results):
    def pairSort(pair):
        return -pair[0]['total']
    return sorted(results , key=pairSort)

def formatResults(results, reverse=True, verbose=True):
    n = len(results)
    l = []
    
    if reverse:
        results = list(reversed(results))
    
    if verbose:
        for i in range(len(results)):
            result = results[i]
            l.append('\n%3s %s' % (n - i, '=' * 37))
            
            scores  = result[0]
            weights = scores['weights']
            total_weight = 0.0
            for k, v in weights.iteritems():
                total_weight = total_weight + float(v)
            l.append('%16s   Val     Wght     Total' % ' ')
            
            for k, v in weights.iteritems():
                s = float(scores[k])
                w = float(weights[k])
                t = 0
                if total_weight > 0:
                    t = s * w / total_weight
                l.append('%16s %5s  * %5s  => %5s' % (k, '%.2f' % s, '%.2f' % w, '%.2f' % t))
            
            l.append(' ' * 37 + '%.2f' % scores['total'])
            l.append("%s from %s with key %s" % (result[1].name, result[1].source, result[1].key))
            l.append(str(result[1]))
    else:
        for i in range(len(results)):
            result = results[i]
            scores = result[0]
            
            r = result[1]
            s = "\n%3d) %s (%s) from %s { score=%f, key=%s }" % \
                (n - i, r.name, r.subtype, r.source, scores['total'], r.key)
            
            l.append(s)
    
    return utils.normalize('\n'.join(l), strict=True)

def typeToSubcategory(t):
    m = {
        'track':'song',
        'album':'album',
        'artist':'artist',
        'book':'book',
        'movie':'movie',
        'tv':'tv',
        'app':'app'
    }
    if t in m:
        return m[t]
    else:
        return None

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

    @lazyProperty
    def keywords(self):
        words = set()
        for term in self.related_terms:
            term = punctuation_re.sub(' ', term)
            for w in term.split():
                if w != '':
                    words.add(w)
        return words
    
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

    @property
    def coordinates(self):
        return None

    @property
    def address(self):
        return {}

    @property
    def address_string(self):
        return None

    @property 
    def neighborhoods(self):
        return []

    @property 
    def subcategory(self):
        return None

    @property 
    def image(self):
        return None

    @property
    def date(self):
        return None

class ResolverProxy(object):

    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

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
        try:
            return "ResolverProxy:%s" % str(self.target)
        except:
            return "ResolverProxy"

    @property
    def keywords(self):
        return self.target.keywords
    
    @property
    def name(self):
        return self.target.name

    @property 
    def priority(self):
        return self.target.priority

    @property 
    def related_terms(self):
        return self.target.related_terms

    @property
    def coordinates(self):
        return self.target.coordinates

    @property
    def address(self):
        return self.target.address

    @property
    def image(self):
        return self.target.image

    @property
    def date(self):
        return self.target.date

    @property 
    def subcategory(self):
        return self.target.subcategory

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

    @property
    def coordinates(self):
        return None

    @property
    def query_string(self):
        return ''

    @property
    def subtype(self):
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

    @property 
    def subcategory(self):
        return 'artist'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
            ]
        l.extend([ track['name'] for track in self.tracks])
        l.extend([ album['name'] for album in self.albums])
        return [
            v for v in l if v != ''
        ]

#
# Album
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
    def date(self):
        return None

    @property 
    def type(self):
        return 'album'

    @property 
    def subcategory(self):
        return 'album'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
                self.artist['name'],
            ]
        l.extend([ track['name'] for track in self.tracks])
        return [
            v for v in l if v != ''
        ]


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

    @property 
    def subcategory(self):
        return 'song'
        
    @lazyProperty
    def related_terms(self):
        return [
            v for v in [
                self.type,
                'song',
                self.name,
                self.artist['name'],
                self.album['name'],
            ]
                if v != ''
        ]


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

    @property 
    def subcategory(self):
        return 'song'

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

    @property 
    def subcategory(self):
        return 'movie'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
                self.director['name']
            ]
        l.extend(self.genres)
        for actor in self.cast:
            l.append(actor['name'])
            if 'character' in actor:
                l.append(actor['character'])
        return [
            v for v in l if v != ''
        ]
#
# TV Show
#

class ResolverTVShow(ResolverObject):
    """
    Interface for tv show objects

    Attributes:

    cast - a list of actor dicts containing at least 'name' strings and possibly 'character' strings
    director - a director dict containing at least a 'name' string
    date - a datetime indicating the release date or None for unknown
    rating - a string indicating the MPAA rating of the show or '' for unknown
    genres - a list of genre strings
    seasons - the number of seasons of the show
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
    def rating(self):
        return None

    @property 
    def genres(self):
        return []

    @property 
    def type(self):
        return 'tv'

    @property 
    def subcategory(self):
        return 'tv'

    @property
    def seasons(self):
        return -1

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
                self.director['name']
            ]
        l.extend(self.genres)
        for actor in self.cast:
            l.append(actor['name'])
            if 'character' in actor:
                l.append(actor['character'])
        return [
            v for v in l if v != ''
        ]

#
# Books
#

class ResolverBook(ResolverObject):
    """
    Interface for book objects

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
    def genres(self):
        return []

    @property 
    def type(self):
        return 'book'

    @property 
    def subcategory(self):
        return 'book'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
                self.author['name'],
                self.publisher['name'],
            ]
        return [
            v for v in l if v != ''
        ]

#
# Places
# 

class ResolverPlace(ResolverObject):
    """
    Interface for place objects

    Attributes:

    TODO
    """

    @property
    def phone(self):
        return None

    @property
    def email(self):
        return None

    @property 
    def has_food(self):
        return False

    @property 
    def has_drinks(self):
        return False

    @property 
    def cuisines(self):
        return []

    @property 
    def type(self):
        return 'place'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
            ]
        for k,v in self.address.items():
            l.append(v)
        return [
            v for v in l if v != ''
        ]

#
# Apps
#

class ResolverApp(ResolverObject):
    """
    Interface for app objects

    Attributes:

    genres - a list containing any applicable genres
    publisher - an publisher dict containing at least a 'name' string
    """
    @abstractproperty
    def publisher(self):
        pass

    @property
    def date(self):
        return None

    @property 
    def genres(self):
        return []

    @property 
    def type(self):
        return 'app'

    @property 
    def subcategory(self):
        return 'app'

    @lazyProperty
    def related_terms(self):
        l = [
                self.type,
                self.name,
                self.publisher['name'],
            ]
        return [
            v for v in l if v != ''
        ]

    @lazyProperty 
    def screenshots(self):
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
    def __init__(self,verbose=False):
        self.__verbose = verbose
    
    @property 
    def verbose(self):
        return self.__verbose
    
    def setComparison(self, a, b, options):
        score = setComparison(a, b, options['symmetric'])
        if options['negative'] and not options['symmetric']:
            for word, weight in _negative_weights.iteritems():
                if setComparison([word], a) < 0.4 and setComparison([word], b) > 0.6:
                    score = score * (1.0 - abs(weight))
        return score
    
    def termComparison(self, query, terms, options):
        def checkTerms(query, valid):
            maxLenTerms = 0
            for term in valid:
                lenTerms = 0
                a = query.split(term)
                if len(a) > 1:
                    lenTerms = len(term)
                    for section in a:
                        if section == ' ':
                            lenTerms = lenTerms + 1
                        elif len(section) > 0:
                            lenTerms = lenTerms + checkTerms(section, valid)
                if lenTerms > maxLenTerms:
                    maxLenTerms = lenTerms
            return maxLenTerms
        
        def score(query, terms):
            valid = []
            for term in terms:
                if term.lower() in query.lower():
                    valid.append(term.lower())
            return checkTerms(query.lower(), valid) * 1.0 / len(query)
        
        return score(query, terms)
    
    def albumSimplify(self, album):
        """ Reduces an album name to a simplified form for fuzzy comparison. """
        return albumSimplify(album)
    
    def trackSimplify(self, track):
        """ Reduces a track name to a simplified form for fuzzy comparison. """
        return trackSimplify(track)
    
    def movieSimplify(self, movie):
        """ Reduces a movie name to a simplified form for fuzzy comparison. """
        return movieSimplify(movie)
    
    def artistSimplify(self, artist):
        """ Reduces an artist name to a simplified form for fuzzy comparison. """
        return artistSimplify(artist)
    
    def actorSimplify(self, actor):
        """ Reduces an actor name to a simplified form for fuzzy comparison. """
        return nameSimplify(actor)
    
    def nameComparison(self, a, b):
        """ Generic fuzzy name comparison. Returns a comparison decimal [0,1] """
        return stringComparison(a, b)
    
    def artistComparison(self, q, m):
        """ Artist specific comparison metric. """
        return self.nameComparison(self.artistSimplify(q), self.artistSimplify(m))
    
    def albumComparison(self, q, m):
        """ Album specific comparison metric. """
        return self.nameComparison(self.albumSimplify(q), self.albumSimplify(m))
    
    def trackComparison(self, q, m):
        """ Track specific comparison metric. """
        return self.nameComparison(self.trackSimplify(q), self.trackSimplify(m))
    
    def movieComparison(self, q, m):
        """ Movie specific comparison metric. """
        return self.nameComparison(self.movieSimplify(q), self.movieSimplify(m))
    
    def lengthComparison(self, q, m):
        """ Length specific comparison metric. """
        if q <= 0 or m <= 0:
            return 0
        diff = abs(q - m)
        return (1 - (float(diff)/max(q, m)))**2
    
    def dateComparison(self, q, m):
        """ Date specific comparison metric. """
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

    def directorComparison(self, q, m):
        """ Director specific comparison metric. """
        return self.nameComparison(q['name'], m['name'])

    def authorComparison(self, q, m):
        """ Author specific comparison metric. """
        return self.nameComparison(q['name'], m['name'])

    def publisherComparison(self, q, m):
        """ Publisher specific comparison metric. """
        return self.nameComparison(q['name'], m['name'])

    def placeComparison(self, q, m):
        """ Place specific comparison metric. """
        return self.nameComparison(q['name'], m['name'])

    def checkArtist(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.artistComparison(q.name, m.name)), 
            ('albums',      lambda q, m, s, o: self.albumsComparison(q, m, o)), 
            ('tracks',      lambda q, m, s, o: self.tracksComparison(q, m, o)), 
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeightBoost(q, m, s, o, boost=5.0), 
            'albums':       lambda q, m, s, o: self.__albumsWeight(q, m), 
            'tracks':       lambda q, m, s, o: self.__tracksWeight(q, m), 
        }
        self.genericCheck(tests, weights, results, query, match, options, order)

    def checkAlbum(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.albumComparison(q.name, m.name)),
            ('artist',      lambda q, m, s, o: self.artistComparison(q.artist['name'], m.artist['name'])),
            ('tracks',      lambda q, m, s, o: self.tracksComparison(q, m, o)),
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'artist':       lambda q, m, s, o: self.__nameWeight(q.artist['name'], m.artist['name']),
            'tracks':       lambda q, m, s, o: self.__tracksWeight(q, m),
        }
        self.genericCheck(tests, weights, results, query, match, options, order)

    def checkTrack(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.trackComparison(q.name, m.name)),
            ('artist',      lambda q, m, s, o: self.artistComparison(q.artist['name'], m.artist['name'])),
            ('album',       lambda q, m, s, o: self.albumComparison(q.album['name'], m.album['name'])),
            ('length',      lambda q, m, s, o: self.lengthComparison(q.length, m.length)),
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name),
            'artist':       lambda q, m, s, o: self.__nameWeight(q.artist['name'], m.artist['name'])*2,
            'album':        lambda q, m, s, o: self.__nameWeight(q.album['name'], m.album['name'])*.3,
            'length':       lambda q, m, s, o: self.__lengthWeight(q.length, m.length),
        }
        self.genericCheck(tests, weights, results, query, match, options, order)

    def checkMovie(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.movieComparison(q.name, m.name)),
            ('cast',        lambda q, m, s, o: self.castComparison(q, m, o)),
            ('director',    lambda q, m, s, o: self.directorComparison(q.director, m.director)),
            ('length',      lambda q, m, s, o: self.lengthComparison(q.length, m.length)),
            ('date',        lambda q, m, s, o: self.dateComparison(q.date, m.date)),
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name,exact_boost=2.0),
            'cast':         lambda q, m, s, o: self.__castWeight(q, m),
            'director':     lambda q, m, s, o: self.__nameWeight(q.director['name'], m.director['name']),
            'length':       lambda q, m, s, o: self.__lengthWeight(q.length, m.length,q_empty=.2) * 3,
            'date':         lambda q, m, s, o: self.__dateWeight(q.date, m.date,exact_boost=4),
        }
        self.genericCheck(tests, weights, results, query, match, options, order)

    def checkBook(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.movieComparison(q.name, m.name)),
            ('author',      lambda q, m, s, o: self.authorComparison(q.author, m.author)),
            ('publisher',   lambda q, m, s, o: self.publisherComparison(q.publisher, m.publisher)),
            ('length',      lambda q, m, s, o: self.lengthComparison(q.length, m.length)),
            ('date',        lambda q, m, s, o: self.dateComparison(q.date, m.date)),
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name, exact_boost=1.5),
            'author':       lambda q, m, s, o: self.__nameWeight(q.author['name'], m.author['name'], exact_boost=3, m_empty=7 ),
            'publisher':    lambda q, m, s, o: self.__nameWeight(q.publisher['name'], m.publisher['name'], exact_boost=2, m_empty=4 ),
            'length':       lambda q, m, s, o: self.__lengthWeight(q.length, m.length) * .5,
            'date':         lambda q, m, s, o: self.__dateWeight(q.date, m.date) * .2,
        }
        self.genericCheck(tests, weights, results, query, match, options, order)
    
    def checkPlace(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.nameComparison(q.name, m.name)),
            ('location',    self.__locationTest),
        ]
        weights = {
            'name':         lambda q, m, s, o: 1.0, #self.__nameWeight(q.name, m.name, exact_boost=1.5),
            'location':     self.__locationWeight, 
        }
        self.genericCheck(tests, weights, results, query, match, options, order)
    
    def checkTVShow(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.movieComparison(q.name, m.name)),
            ('cast',        lambda q, m, s, o: self.castComparison(q, m, o)),
            ('director',    lambda q, m, s, o: self.directorComparison(q.director, m.director)),
            ('date',        lambda q, m, s, o: self.dateComparison(q.date, m.date)),
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name, exact_boost=2.0),
            'cast':         lambda q, m, s, o: self.__castWeight(q, m),
            'director':     lambda q, m, s, o: self.__nameWeight(q.director['name'], m.director['name']),
            'date':         lambda q, m, s, o: self.__dateWeight(q.date, m.date, exact_boost=4),
        }
        self.genericCheck(tests, weights, results, query, match, options, order)
    
    def checkApp(self, results, query, match, options, order):
        tests = [
            ('name',        lambda q, m, s, o: self.nameComparison(q.name, m.name)),
            ('date',        lambda q, m, s, o: self.dateComparison(q.date, m.date)),
            ('publisher',   lambda q, m, s, o: self.publisherComparison(q.publisher, m.publisher))
        ]
        weights = {
            'name':         lambda q, m, s, o: self.__nameWeight(q.name, m.name, exact_boost=4),
            'date':         lambda q, m, s, o: self.__dateWeight(q.date, m.date, exact_boost=4),
            'publisher':    lambda q, m, s, o: self.__nameWeight(q.publisher['name'], m.publisher['name'],
                                                                 exact_boost=2, m_empty=4),
        }
        self.genericCheck(tests, weights, results, query, match, options, order)
    
    def checkSearchAll(self, results, query, match, options, order):
        if match.target is None:
            logs.info("Aborted match for %s due to None target" % type(match))
            return
        
        tests = [
            ('query_string',        self.__queryStringTest),
            ('name',                self.__nameTest),
            ('location',            self.__locationTest),
            ('subcategory',         self.__subcategoryTest), 
            ('priority',            lambda q, m, s, o: m.priority), 
            ('popularity',          self.__popularityTest), 
            ('recency',             self.__recencyTest),
            ('source_priority',     self.__sourceTest),
            ('keywords',            self.__keywordsTest),
            ('related_terms',       self.__relatedTermsTest),
        ]
        
        weights = {
            'query_string':         lambda q, m, s, o: 0, 
            'name':                 lambda q, m, s, o: self.__nameWeightBoost(q, m, s, o, boost=50.0), 
            'location':             lambda q, m, s, o: self.__locationWeightBoost(q, m, s, o, boost=40), 
            'subcategory':          lambda q, m, s, o: 1, 
            'priority':             lambda q, m, s, o: 1, 
            'popularity':           self.__popularityWeight, 
            'recency':              lambda q, m, s, o: self.__recencyWeight(q, m, s, o, boost=5),
            'source_priority':      lambda q, m, s, o: 1.0, #self.__sourceWeight(m.source),
            'keywords':             self.__keywordsWeight,
            'related_terms':        self.__relatedTermsWeight,
        }
        
        self.genericCheck(tests, weights, results, query, match, options, order)
    
    def genericCheck(self, tests, weights, results, query, match, options, order):
        mins = options['mins']
        if self.verbose:
            print("Comparing %s and %s" % (match.name,query.name))
        
        success, similarities = self.__compareAll(query, match, tests, options)
        
        if success:
            self.__addTotal(similarities, weights, query, match, options)
            
            if 'total' not in mins or similarities['total'] >= mins['total']:
                #print("Total %s for %s from %s" % (similarities['total'], match.name, match.source))
                result = (similarities, match)
                results.append(result)
                options['callback'](result, order)
    
    def resolve(self, query, source, **options):
        options = self.parseGeneralOptions(query, options)
        results = []
        index = 0
        
        for i in options['groups']:
            batch   = self.__resolveBatch(options['check'], query, source, (index, i) , options)
            index  += i
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

    def albumsComparison(self, query, match, options):
        query_album_set = self.albumsSet(query)
        match_album_set = self.albumsSet(match)
        
        if self.verbose:
            self.__differenceLog('Album', query_album_set, match_album_set, query, match)
        
        return self.setComparison(query_album_set, match_album_set, options)

    def tracksComparison(self, query, match, options):
        query_track_set = self.tracksSet(query)
        match_track_set = self.tracksSet(match)

        if self.verbose:
            self.__differenceLog('Track', query_track_set, match_track_set, query, match)

        return self.setComparison(query_track_set, match_track_set, options)

    def castComparison(self, query, match, options):
        query_cast_set = self.castSet(query)
        match_cast_set = self.castSet(match)

        if self.verbose:
            self.__differenceLog('Cast', query_cast_set, match_cast_set, query, match)

        return self.setComparison(query_cast_set, match_cast_set, options)


    def parseGeneralOptions(self, query, options):
        """
        Most high level methods in this class accept an options dict as a means of customization.

        The following options are recognized:

        count -  a positive integer indicating the desired minimum result size (results may be smaller if the source is limited)
        max - a positive integer that sets the maximum number of results to return
        symmetric - a boolean which denotes if the comparison should by symmetric (i.e. a to b == b to a)
        negative - a boolean which denotes if negative weights should be used
        resolvedComparison -  a float which indicates a simple cutoff total comparison to consider something resolved
        pool - a positive integer indicating the size of the gevent pool to be used (use 1 for sequential)
        mins - an attribute-comparison dict which can be used to prune matches (useful for reducing execution time)
        """
        if 'callback' not in options:
            options['callback'] = lambda x,y: None
        if 'count' not in options:
            options['count'] = 1
        if 'limit' not in options:
            options['limit'] = 10
        if 'offset' not in options or options['offset'] is None:
            options['offset'] = 0
        if 'strict' not in options:
            options['strict'] = False
        if 'symmetric' not in options:
            options['symmetric'] = False
        if 'negative' not in options:
            options['negative'] = True
        if 'max' not in options:
            options['max'] = 1000000
        if 'resolvedComparison' not in options:
            options['resolvedComparison'] = .7
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
            elif query.type == 'search_all':
                groups.extend([])
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
            elif query.type =='place':
                options['check'] = self.checkPlace
            elif query.type =='tv':
                options['check'] = self.checkTVShow
            elif query.type =='app':
                options['check'] = self.checkApp
            elif query.type == 'search_all':
                options['check'] = self.checkSearchAll
            else:
                #no generic test
                raise ValueError("no test for %s (%s)" % (query.name, query.type))
        
        return options
    
    def __sourceTest(self, query, match, similarities, options):
        source_name = match.source.lower()
        
        weights = {
            'stamped'       : 1.0,
            'itunes'        : 0.8,
            'rdio'          : 0.6,
            'spotify'       : 0.6,
            'factual'       : 0.6,
            'tmdb'          : 0.8,
            'amazon'        : 0.6,
            'netflix'       : 0.8,
            'googleplaces'  : 0.7,
        }
        
        try:
            return weights[source_name]
        except KeyError:
            logs.warn("ERROR: unrecognized source '%s'" % source_name)
        
        return 0
    
    def __sourceWeight(self, source):
        return 1
    
    def __queryStringTest(self, query, match, similarities, options):
        return 0
    
    def __nameTest(self, query, match, similarities, options):
        value = stringComparison(query.query_string, match.name)
        
        a = simplify(query.query_string)
        b = simplify(match.name)
        
        if len(a) > len(b):
            a, b = b, a
        
        if a in b:
            if b.startswith(a):
                value = min(0.99, value * 1.2)
            else:
                value = min(0.99, value * 1.1)
        
        return value
    
    def __popularityTest(self, query, match, similarities, options):
        try:
            popularity = math.log(float(match.target.popularity) + 1)
            
            if popularity > 3:
                return 1.0
        except AttributeError:
            pass
        
        return 0
    
    def __locationTest(self, query, match, similarities, options):
        if query.coordinates is None or match.coordinates is None:
            return 0
        
        try:
            distance = utils.get_spherical_distance(query.coordinates, match.coordinates)
            distance = abs(distance * 3959)
        except Exception:
            return 0
        
        if distance < 0 or distance > 50:
            return 0
        
        # Simple parabolic curve to weight closer distances
        return (1.0 / 2500) * distance * distance - (1.0 / 25) * distance + 1.0
    
    def __locationWeightBoost(self, query, match, similarities, options, boost=1):
        weight = 1.0
        
        if 'location' in similarities:
            weight = (similarities['location'] ** 2)
        
        return weight * boost
    
    def __locationWeight(self, query, match, similarities, options):
        weight = 1000.0
        
        if 'location' in similarities:
            location = similarities['location']
            if location > 0:
                if location >= 0.90:
                    return 0
                
                weight = 1.0 / (5 * location)
        
        return max(0, min(1000.0, weight))
    
    def __subcategoryTest(self, query, match, similarities, options):
        try:
            return _subcategory_weights[match.subtype] / 100.0
        except Exception:
            return 0.0
        return 1
    
    def __keywordsTest(self, query, match, similarities, options):
        if len(query.keywords) > 0:
            return self.setComparison(set(query.keywords), set(match.keywords), options)
        
        return self.setComparison(set(query.query_string.split()), set(match.keywords), options)
    
    def __keywordsWeight(self, query, match, similarities, options):
        if len(query.keywords) > 0:
            if len(match.keywords) == 0:
                return 1
            return 5
        else:
            if len(match.keywords) == 0 or query.query_string == '':
                return 0
            
            string = query.query_string
            for term in match.keywords:
                if string.find(term) != -1:
                    string.replace(term,' ')
            
            string = simplify(string)
            return len(string) / max(1, len(query.query_string))
    
    def __relatedTermsTest(self, query, match, similarities, options):
        return self.termComparison(query.query_string, match.related_terms, options)
    
    def __relatedTermsWeight(self, query, match, similarities, options):
        if len(match.related_terms) == 0:
            if match.target.type == 'place' and similarities['related_terms'] < similarities['name']:
                return 0
            return 1
        return 5
    
    def __nameWeightBoost(self, query, match, similarities, options, boost=1):
        try:
            value = similarities['name']
        except KeyError:
            value = 0.0
        
        a = simplify(query.query_string)
        b = simplify(match.name)
        
        if len(a) > len(b):
            a, b = b, a
        
        if a in b:
            if b.startswith(a):
                value = min(0.99, value * 1.2)
            else:
                value = min(0.99, value * 1.1)
        
        # note (travis):
        # the purpose of this formula is to smoothly weight names that are 
        # very strong matches or very weak matches heavily with partial 
        # name matches still being weighted proportionally to the name 
        # similarity but with a much smaller weight because the name 
        # signal is less important w.r.t. ranking for these cases.
        weight = 4 * ((value - 0.5) ** 2)
        weight = weight + (1.0 - weight) / 1.5
        
        return boost * weight
    
    def __popularityWeight(self, query, match, similarities, options):
        try:
            popularity = math.log(float(match.target.popularity) + 1)
            
            if popularity > 3:
                return popularity
        except AttributeError:
            pass
        
        return 0.0
    
    def __nameWeight(self, a, b, exact_boost=1, q_empty=1, m_empty=1, both_empty=1):
        if a is None or b is None:
            return 1
        
        assert isinstance(a, basestring)
        assert isinstance(b, basestring)
        
        weight = 1.0
        
        if a == b:
            weight = exact_boost
        else:
            la = len(a)
            lb = len(b)
            
            if la == 0:
                if lb == 0:
                    return both_empty
                else:
                    return q_empty
            elif lb == 0:
                return m_empty
            
            weight = 2 * float(la + lb) / (math.log(la + 1) + math.log(lb + 1))
            
            if len(a) > len(b):
                b, a = a, b
            
            # weight string similarity comparison slightly higher if a is a substring of b
            if a in b:
                if b.startswith(a) or b.endswith(a):
                    weight = weight * 3
                else:
                    weight = weight * 2
        
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
    
    def __recencyTest(self, query, match, similarities, options):
        factor = 0.9
        
        if match.subtype == 'movie':
            factor = 1
        
        try:
            diff = (datetime.utcnow() - match.date).days
            if diff <= 90 and diff > -60:
                return factor
        except:
            pass
        
        return 0
    
    def __recencyWeight(self, query, match, similarities, options, boost=1):
        if match.subtype == 'movie':
            boost *= 3
        
        try:
            diff = (datetime.utcnow() - match.date).days
            
            if diff <= 90 and diff > -60:
                return boost
        except:
            pass
        
        return 0
    
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
        for i in range(len(entries)):
            entry = entries[i]
            pool.spawn(check, results, query, entry, options, start+i)
        pool.join()
        
        return results
    
    def __compareAll(self, query, match, tests, options):
        similarities = {}
        if 'mins' in options:
            mins = options['mins']
        else:
            mins = {}
        success = True
        for name, test in tests:
            try:
                before = time()
                comparison = float(test(query, match, similarities, options))
            except ValueError:
                print("test %s failed with ValueError" % name)
                raise
            similarities[name] = comparison
            if name in mins and comparison < mins[name]:
                success = False
                break
        return (success, similarities)
    
    def __shouldFinish(self, query, results, options):
        num_results = len(results)
        
        if num_results == 0:
            return False # TODO: is this right?
        elif num_results >= options['max']:
            return True
        elif num_results < options['count']:
            return False
        else:
            cutoff = options['resolvedComparison']
            if results[0][0]['total'] >= cutoff:
                return True
        return False

    def __finish(self, query, results, options):
        for result in results:
            result[0]['resolved'] = False
        if len(results) > 0 and results[0][0]['total'] > options['resolvedComparison']:
            results[0][0]['resolved'] = True
        return results

    def __addTotal(self, similarities, weights, query, match, options):
        actual_weights = {}
        total  = 0
        weight = 0
        
        for k, f in weights.iteritems():
            v = f(query, match, similarities, options)
            
            weight += v
            total  += v * similarities[k]
            
            actual_weights[k] = v
        
        similarities['total']   = total / weight
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
    import Schemas

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
                print("Inversion failed! (low asymetric comparison?)")
            blank = Schemas.Entity()
            generic_source.enrichEntityWithWrapper(new_query, blank)
            pprint(blank.value)

    else:
        print("No results")

