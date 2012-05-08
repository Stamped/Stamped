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
    from time                       import time
except:
    report()
    raise




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

    def __init__(self, types=None):
        if types is not None:
            self.__types = set(types)
    
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
        if t in self.types:
            return True
        return False


### KINDS

class ResolverPlace(ResolverObject):
    """
    Generic interface for Place objects.
    """

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
            l.append(v)
        
        return [ v for v in l if v != '' ]


class ResolverPerson(ResolverObject):
    """
    Generic interface for Person objects.
    """

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