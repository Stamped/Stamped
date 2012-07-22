#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [
    'ResolverObject',
    'ResolverPlace',
    'ResolverPerson',
    'ResolverMediaCollection',
    'ResolverMediaItem',
    'ResolverSoftware',
    'ResolverSearchAll',
    'LookupRequiredError'
]

import Globals
from logs import report

try:
    import utils, re, string
    import logs, sys, math
    from utils                      import lazyProperty
    from pprint                     import pprint, pformat
    from abc                        import ABCMeta, abstractmethod, abstractproperty
    from datetime                   import datetime
except:
    report()
    raise


class LookupRequiredError(Exception):
    def __init__(self, sourceName, entityDescription, fieldName):
        super(LookupRequiredError, self).__init__(
            'Error: can\'t retrieve field %s for entity %s from source %s without a lookup call!' %
            (fieldName, entityDescription, sourceName))

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

    def __init__(self, types=None, maxLookupCalls=None):
        if types is not None:
            self.__types = set(types)
        self.__maxLookupCalls = maxLookupCalls
        self.__lookupCallsMade = 0
        self._properties = [ 'name', 'raw_name', 'source', 'key', 'kind', 'types', 'url', 'keywords', 'related_terms',
                             'description', 'priority', 'subcategory', 'images']

    __metaclass__ = ABCMeta

    def countLookupCall(self, fieldName):
        if (self.__maxLookupCalls is not None) and (self.__maxLookupCalls <= self.__lookupCallsMade):
            # I used to use self.name here, but you get into this weird problem where self.name is a lazyProperty that
            # opens self.data, and self.data requires a lookup, which throws an error here, and for the error text we
            # try to get self.name. If I try to break the loop here with a fieldName == 'name' check it doesn't matter
            # because the problem is actually beneath here in the lazyProperty code -- basically it ends up with one
            # thread trying to hold the same lock twice.
            raise LookupRequiredError(self.source, self.key, fieldName)

        self.__lookupCallsMade += 1

    def __str__(self):
        # Temporary disable lookup calls because we don't want to make them just for printing.
        # There are some obvious concurrency issues here.
        oldMax = self.__maxLookupCalls
        self.__maxLookupCalls = 0

        lines = []
        for property in self._properties:
            try:
                propertyValue = getattr(self, property)
                if isinstance(propertyValue, unicode):
                    propertyValue = propertyValue.encode('utf-8')
                if propertyValue is not None and propertyValue != [] and propertyValue != '':
                    lines.append('%s\t:%s' % (property, propertyValue))
            except LookupRequiredError:
                pass

        self.__maxLookupCalls = oldMax
        return '\n'.join(lines)

    @abstractmethod
    def _cleanName(self, rawName):
        raise NotImplementedError()

    # ResolverObject.name is intended to be the cleaned name of the entity that this resolver object represents.
    @lazyProperty
    def name(self):
        return self._cleanName(self.raw_name)

    # ResolverObject.raw_name is the unprocessed name given to us by the source. It may describe one incarnation or
    # productization of the entity.
    @abstractproperty
    def raw_name(self):
        pass

    @abstractproperty
    def key(self):
        pass

    @abstractproperty
    def source(self):
        pass

    @abstractproperty
    def kind(self):
        pass

    @lazyProperty
    def types(self):
        try:
            return list(str(i) for i in self.__types)
        except:
            return []

    @lazyProperty
    def keywords(self):
        words = set()
        for term in self.related_terms:
            try:
                term = punctuation_re.sub(' ', term)
                for w in term.split():
                    if w != '':
                        words.add(w)
            except Exception:
                pass
        
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
    def subcategory(self):
        return None

    @property 
    def images(self):
        return []

    def isType(self, t):
        return t in self.types


### KINDS

class ResolverPlace(ResolverObject):
    """
    Generic interface for Place objects.
    """

    def __init__(self, *args, **kwargs):
        super(ResolverPlace, self).__init__(*args, **kwargs)
        self._properties.extend([
            'coordinates', 'address', 'address_string', 'neighborhoods', 'gallery', 'phone', 'email', 'has_food',
            'has_drinks', 'cuisines'
        ])

    @property 
    def kind(self):
        return 'place'

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
    def gallery(self):  #expects list of dicts with 'url' and 'caption'
        return []

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

    @lazyProperty
    def related_terms(self):
        l = [ self.name ]
        l.extend([ i for i in self.types ])

        for k,v in self.address.items():
            if v is not None:
                l.append(v)
        
        return [ v for v in l if v != '' ]


class ResolverPerson(ResolverObject):
    """
    Generic interface for Person objects.
    """

    def __init__(self, *args, **kwargs):
        super(ResolverPerson, self).__init__(*args, **kwargs)
        self._properties.extend([
            'albums', 'tracks', 'movies', 'books', 'genres'
        ])

    @property
    def kind(self):
        return 'person'

    @property
    def albums(self):
        return []

    @property
    def tracks(self):
        return []

    @property
    def movies(self):
        return []

    @property
    def books(self):
        return []

    @property
    def genres(self):
        return []

    @lazyProperty
    def related_terms(self):
        l = [ self.name ]
        l.extend([ i for i in self.types ])
        l.extend([ i['name'] for i in self.tracks ])
        l.extend([ i['name'] for i in self.albums ])
        l.extend([ i['name'] for i in self.movies ])
        l.extend([ i['name'] for i in self.books ])
        return [
            v for v in l if v != ''
        ]


class ResolverMediaCollection(ResolverObject):
    """
    Generic interface for Media Collection objects.
    """

    def __init__(self, *args, **kwargs):
        super(ResolverMediaCollection, self).__init__(*args, **kwargs)
        self._properties.extend([
            'artists', 'authors', 'tracks', 'cast', 'directors', 'publishers', 'studios', 'networks', 'release_date',
            'genres', 'length', 'mpaa_rating', 'last_popular',
        ])

    @property 
    def kind(self):
        return 'media_collection'

    @property
    def artists(self):
        return []

    @property
    def authors(self):
        return []

    @property
    def tracks(self):
        return []

    @property
    def cast(self):
        return []

    @property
    def directors(self):
        return []

    @property
    def publishers(self):
        return []

    @property
    def studios(self):
        return []

    @property
    def networks(self):
        return []

    @property
    def release_date(self):
        return None

    @property
    def genres(self):
        return []

    @property 
    def length(self):
        return -1

    @property 
    def mpaa_rating(self):
        return None

    @property
    def last_popular(self):
        return None

    @lazyProperty
    def related_terms(self):
        l = [ self.name ]
        l.extend([ i for i in self.types ])
        l.extend([ i['name'] for i in self.artists ])
        l.extend([ i['name'] for i in self.authors ])
        l.extend([ i['name'] for i in self.tracks ])
        l.extend([ i['name'] for i in self.cast ])
        l.extend([ i['name'] for i in self.directors ])
        l.extend([ i['name'] for i in self.publishers ])
        l.extend([ i['name'] for i in self.studios ])
        l.extend([ i['name'] for i in self.networks ])
        return [
            v for v in l if v != ''
        ]


class ResolverMediaItem(ResolverObject):
    """
    Generic interface for Media Item objects.
    """

    def __init__(self, *args, **kwargs):
        super(ResolverMediaItem, self).__init__(*args, **kwargs)
        self._properties.extend([
            'artists', 'authors', 'cast', 'directors', 'publishers', 'studios', 'networks', 'release_date', 'genres',
            'length', 'mpaa_rating', 'albums', 'isbn', 'sku_number', 'last_popular',
        ])

    @property
    def kind(self):
        return 'media_item'

    @property
    def artists(self):
        return []

    @property
    def authors(self):
        return []

    @property
    def cast(self):
        return []

    @property
    def directors(self):
        return []

    @property
    def publishers(self):
        return []

    @property
    def studios(self):
        return []

    @property
    def networks(self):
        return []

    @property
    def release_date(self):
        return None

    @property
    def genres(self):
        return []

    @property 
    def length(self):
        # Note that for videos/songs this is in seconds.
        return -1

    @property 
    def mpaa_rating(self):
        return None

    @property
    def albums(self):
        return []

    @property
    def isbn(self):
        return None

    @property
    def sku_number(self):
        return None

    @property
    def last_popular(self):
        return None

    @lazyProperty
    def related_terms(self):
        l = [ self.name ]
        l.extend([ i for i in self.types ])
        l.extend([ i['name'] for i in self.artists ])
        l.extend([ i['name'] for i in self.authors ])
        l.extend([ i['name'] for i in self.cast ])
        l.extend([ i['name'] for i in self.directors ])
        l.extend([ i['name'] for i in self.publishers ])
        l.extend([ i['name'] for i in self.studios ])
        l.extend([ i['name'] for i in self.networks ])
        l.extend([ i['name'] for i in self.albums ])
        return [
            v for v in l if v != ''
        ]


class ResolverSoftware(ResolverObject):
    """
    Generic interface for Software objects.
    """

    def __init__(self, *args, **kwargs):
        super(ResolverSoftware, self).__init__(*args, **kwargs)
        self._properties.extend([
            'authors', 'publishers', 'genres', 'screenshots', 'release_date', 'platform'
        ])

    @property
    def kind(self):
        return 'software'

    @property
    def authors(self):
        return []

    @property
    def publishers(self):
        return []

    @property
    def genres(self):
        return []

    @property
    def screenshots(self):
        return []

    @property
    def release_date(self):
        return None

    @property
    def platform(self):
        return None

    @lazyProperty
    def related_terms(self):
        l = [ self.name ]
        l.extend([ i for i in self.types ])
        l.extend([ i['name'] for i in self.authors ])
        l.extend([ i['name'] for i in self.publishers ])
        return [
            v for v in l if v != ''
        ]


class ResolverSearchAll(ResolverObject):

    @property 
    def kind(self):
        return 'search'

    @property
    def query_string(self):
        return ''

    @property
    def coordinates(self):
        return None


# #
# # Artist
# #


# class ResolverArtist(ResolverObject):
#     """
#     Interface for Artist objects.

#     Attributes:

#     albums - a list of artist dicts which must at least contain a 'name' string.
#     tracks - a list of track dicts which must at least contain a 'name' string.
#     """
#     @abstractproperty
#     def albums(self):
#         pass

#     @abstractproperty
#     def tracks(self):
#         pass

#     @property
#     def genres(self):
#         return []
        
#     @property 
#     def type(self):
#         return 'artist'

#     @property 
#     def subcategory(self):
#         return 'artist'

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#             ]
#         l.extend([ track['name'] for track in self.tracks])
#         l.extend([ album['name'] for album in self.albums])
#         return [
#             v for v in l if v != ''
#         ]

# #
# # Album
# # 

# class ResolverAlbum(ResolverObject):
#     """
#     Interface for album objects

#     Attributes:

#     artist - an artist dict containing at least a 'name' string.
#     tracks - a list of track dicts each containing at least a 'name' string.
#     """
#     @abstractproperty
#     def artist(self):
#         pass

#     @abstractproperty
#     def tracks(self):
#         pass

#     @property
#     def genres(self):
#         return []

#     @property
#     def date(self):
#         return None

#     @property 
#     def type(self):
#         return 'album'

#     @property 
#     def subcategory(self):
#         return 'album'

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#                 self.artist['name'],
#             ]
#         l.extend([ track['name'] for track in self.tracks])
#         return [
#             v for v in l if v != ''
#         ]


# #
# # Tracks
# #

# class ResolverTrack(ResolverObject):
#     """
#     Interface for track objects

#     Attributes:

#     artist - an artist dict containing at least a 'name' string
#     album - an album dict containing at least a 'name' string
#     length - a number (possibly float) inticating the length of the track in seconds
#     """
#     @abstractproperty
#     def artist(self):
#         pass

#     @abstractproperty
#     def album(self):
#         pass

#     @abstractproperty
#     def length(self):
#         pass

#     @property
#     def genres(self):
#         return []

#     @property
#     def date(self):
#         return None

#     @property 
#     def type(self):
#         return 'track'

#     @property 
#     def subcategory(self):
#         return 'song'
        
#     @lazyProperty
#     def related_terms(self):
#         return [
#             v for v in [
#                 self.type,
#                 'song',
#                 self.name,
#                 self.artist['name'],
#                 self.album['name'],
#             ]
#                 if v != ''
#         ]

# #
# # Movie
# #

# class ResolverMovie(ResolverObject):
#     """
#     Interface for movie objects

#     Attributes:

#     cast - a list of actor dicts containing at least 'name' strings and possibly 'character' strings
#     director - a director dict containing at least a 'name' string
#     date - a datetime indicating the release date or None for unknown
#     length - a number indicating the length of the movie in seconds or a negative number (-1) for unknown
#     rating - a string indicating the MPAA rating of the movie or '' for unknown
#     genres - a list of genre strings
#     """
#     @property
#     def cast(self):
#         return []

#     @property
#     def director(self):
#         return {'name':''}

#     @property
#     def date(self):
#         return None

#     @property
#     def length(self):
#         return -1

#     @property
#     def rating(self):
#         return None

#     @property 
#     def genres(self):
#         return []

#     @property 
#     def type(self):
#         return 'movie'

#     @property 
#     def subcategory(self):
#         return 'movie'

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#                 self.director['name']
#             ]
#         l.extend(self.genres)
#         for actor in self.cast:
#             l.append(actor['name'])
#             if 'character' in actor:
#                 l.append(actor['character'])
        
#         return [ v for v in l if v != '' ]
# #
# # TV Show
# #

# class ResolverTVShow(ResolverObject):
#     """
#     Interface for tv show objects

#     Attributes:

#     cast - a list of actor dicts containing at least 'name' strings and possibly 'character' strings
#     director - a director dict containing at least a 'name' string
#     date - a datetime indicating the release date or None for unknown
#     rating - a string indicating the MPAA rating of the show or '' for unknown
#     genres - a list of genre strings
#     seasons - the number of seasons of the show
#     """
#     @property
#     def cast(self):
#         return []

#     @property
#     def director(self):
#         return {'name':''}

#     @property
#     def date(self):
#         return None

#     @property
#     def rating(self):
#         return None

#     @property 
#     def genres(self):
#         return []

#     @property 
#     def type(self):
#         return 'tv'

#     @property 
#     def subcategory(self):
#         return 'tv'

#     @property
#     def seasons(self):
#         return -1

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#                 self.director['name']
#             ]
#         l.extend(self.genres)
#         for actor in self.cast:
#             l.append(actor['name'])
#             if 'character' in actor:
#                 l.append(actor['character'])
        
#         return [ v for v in l if v != '' ]

# #
# # Books
# #

# class ResolverBook(ResolverObject):
#     """
#     Interface for book objects

#     Attributes:

#     author - an author dict containing at least a 'name' string
#     publisher - an publisher dict containing at least a 'name' string
#     length - a number (possibly float) inticating the length of the book in pages
#     """
#     @abstractproperty
#     def author(self):
#         pass

#     @abstractproperty
#     def publisher(self):
#         pass

#     @property
#     def date(self):
#         return None

#     @property
#     def length(self):
#         return -1

#     @property
#     def isbn(self):
#         return None

#     @property
#     def eisbn(self):
#         return None

#     @property
#     def sku(self):
#         return None

#     @property 
#     def genres(self):
#         return []

#     @property 
#     def type(self):
#         return 'book'

#     @property 
#     def subcategory(self):
#         return 'book'

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#                 self.author['name'],
#                 self.publisher['name'],
#             ]
#         return [ v for v in l if v != '' ]


# #
# # Apps
# #

# class ResolverApp(ResolverObject):
#     """
#     Interface for app objects

#     Attributes:

#     genres - a list containing any applicable genres
#     publisher - an publisher dict containing at least a 'name' string
#     """
#     @abstractproperty
#     def publisher(self):
#         pass

#     @property
#     def date(self):
#         return None

#     @property 
#     def genres(self):
#         return []

#     @property 
#     def type(self):
#         return 'app'

#     @property 
#     def subcategory(self):
#         return 'app'

#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type,
#                 self.name,
#                 self.publisher['name'],
#             ]
#         return [ v for v in l if v != '' ]

#     @lazyProperty 
#     def screenshots(self):
#         return []

# class ResolverVideoGame(ResolverObject):
#     """
#     Interface for video game objects
    
#     Attributes:
    
#     author - an author dict containing at least a 'name' string
#     publisher - an publisher dict containing at least a 'name' string
#     """
    
#     @abstractproperty
#     def author(self):
#         pass
    
#     @abstractproperty
#     def publisher(self):
#         pass
    
#     @property
#     def date(self):
#         return None
    
#     @property
#     def sku(self):
#         return None
    
#     @property 
#     def genres(self):
#         return []
    
#     @property 
#     def type(self):
#         return 'video_game'
    
#     @property 
#     def subcategory(self):
#         return 'video_game'
    
#     @lazyProperty
#     def related_terms(self):
#         l = [
#                 self.type, 
#                 self.name, 
#                 self.author['name'], 
#                 self.publisher['name'], 
#             ]
#         return [ v for v in l if v != '' ]
