#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'TMDBSource', 'TMDBMovie' ]

import Globals
from logs import report

try:
    from libs.TMDB                  import globalTMDB
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from abc                        import ABCMeta, abstractproperty
    import logs
    from urllib2                    import HTTPError
    from datetime                   import datetime
    from Resolver                   import *
    from pprint                     import pformat, pprint
    from libs.LibUtils              import parseDateString
    import re
except:
    report()
    raise

class _TMDBObject(object):
    __metaclass__ = ABCMeta
    """
    Abstract superclass (mixin) for TMDB objects.

    _TMDBObjects must be instantiated with their tmdb_id.

    Attributes:

    tmdb - an instance of TMDB (API wrapper)
    info (abstract) - the type-specific TMDB data for the object
    """
    def __init__(self, tmdb_id):
        self.__key = str(tmdb_id)
        if self.__key.startswith('tt'):
            self.__key = str(self.info['id'])

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


class TMDBMovie(_TMDBObject, ResolverMovie):
    """
    TMDB movie wrapper
    """
    def __init__(self, tmdb_id):
        _TMDBObject.__init__(self, tmdb_id)
        ResolverMovie.__init__(self)        

    @property
    def valid(self):
        try:
            self.info
            return True
        except HTTPError:
            return False

    @lazyProperty
    def info(self):
        return self.tmdb.movie_info(self.key)

    @lazyProperty
    def castsRaw(self):
        return self.tmdb.movie_casts(self.key)

    @lazyProperty
    def name(self):
        return self.info['title']

    @lazyProperty
    def imdb(self):
        try:
            return self.info['imdb_id']
        except KeyError:
            return None

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
    def director(self):
        try:
            crew = self.castsRaw['crew']
            for entry in crew:
                if entry['job'] == 'Director':
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

class TMDBSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type

class TMDBSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'tmdb',
            groups=[
                'director',
                'cast',
                'desc',
                'short_description',
                'genre',
                'imdb',
            ],
            types=[
                'movie'
            ]
        )
        self.__max_cast = 6

    @lazyProperty
    def __tmdb(self):
        return globalTMDB()

    def wrapperFromKey(self, key, type=None):
        try:
            return TMDBMovie(key)
        except KeyError:
            logs.warning('UNABLE TO FIND TMDB ITEM FOR ID: %s' % key)
            raise
        return None

    def matchSource(self, query):
        if query.type == 'movie':
            return self.movieSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        else:
            return self.emptySource

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithWrapper(self, wrapper, entity, controller, decorations, timestamps)
        entity.tmdb_id = wrapper.key
        return True

    def movieSource(self, query):
        def gen():
            try:
                results = self.__tmdb.movie_search(query.name)
                for movie in results['results']:
                    yield movie
                pages = results['total_pages']

                if pages > 1:
                    for p in range(1,pages):
                        results = self.__tmdb.movie_search(query.name, page=p+1)
                        for movie in results['results']:
                            yield movie
            except GeneratorExit:
                pass
        return self.generatorSource(gen(), constructor=lambda x: TMDBMovie( x['id']) )

    def searchAllSource(self, query, timeout=None):
        if query.types is not None and len(self.types.intersection(query.types)) == 0:
            return self.emptySource
            
        def gen():
            try:    
                results = self.__tmdb.movie_search(query.query_string)
                if results is None:
                    return 
                for movie in results['results']:
                    yield movie
                pages = results['total_pages']

                if pages > 1:
                    for p in range(1,pages):
                        results = self.__tmdb.movie_search(query.query_string, page=p+1)
                        for movie in results['results']:
                            yield movie
            except GeneratorExit:
                pass
        return self.generatorSource(gen(), constructor=lambda x: TMDBSearchAll(TMDBMovie( x['id'])) )

    def __release_date(self, movie):
        result = None
        if 'release_date' in movie:
            date_string = movie['release_date']
            if date_string is not None:
                match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$',date_string)
                if match is not None:
                    try:
                        result = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
                    except ValueError:
                        pass
        return result

    def enrichEntity(self, entity, controller, decorations, timestamps):
        GenericSource.enrichEntity(self, entity, controller, decorations, timestamps)
        title = entity['title']
        if title is not None:
            tmdb_id = entity['tmdb_id']
            if tmdb_id is not None:
                movie = TMDBMovie(tmdb_id)
                try:
                    casts = self.__tmdb.movie_casts(tmdb_id)
                    if 'cast' in casts:
                        cast = casts['cast']
                        cast_order = {}
                        for entry in cast:
                            name = entry['name']
                            order = int(entry['order'])
                            cast_order[order] = name
                        sorted_cast = [ cast_order[k] for k in sorted(cast_order.keys()) ]
                        if len( sorted_cast ) > self.__max_cast:
                            sorted_cast = sorted_cast[:self.__max_cast]
                        cast_string = ', '.join(sorted_cast)
                        if entity['cast'] == None:
                            entity['cast'] = cast_string
                    if 'crew' in casts:
                        crew = casts['crew']
                        director = None
                        for entry in crew:
                            name = entry['name']
                            job = entry['job']
                            if job == 'Director':
                                director = name
                        if director is not None:
                            entity['director'] = director
                        
                except Exception:
                    pass
                info = movie.info
                if 'tagline' in info:
                    tagline = info['tagline']
                    if tagline is not None and tagline != '':
                        entity['short_description'] = tagline
                if 'overview' in info:
                    overview = info['overview']
                    if overview is not None and overview != '':
                        entity['desc'] = overview

                if movie.imdb is not None:
                    entity['imdb_id'] = movie.imdb;
                if len(movie.genres) > 0:
                    entity['genres'] = list(movie.genres)
        
        return True

if __name__ == '__main__':
    demo(TMDBSource(), 'Avatar')

