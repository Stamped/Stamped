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
    import re, logs
    from Resolver                   import *
    from ResolverObject             import *
    from libs.TMDB                  import globalTMDB
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from abc                        import ABCMeta, abstractproperty
    from urllib2                    import HTTPError
    from datetime                   import datetime
    from pprint                     import pformat, pprint
    from libs.LibUtils              import parseDateString
    from search.ScoringUtils        import *
except:
    report()
    raise

class _TMDBObject(object):
    __metaclass__ = ABCMeta
    """
    Abstract superclass (mixin) for TMDB objects.

    _TMDBObjects must be instantiated with their tmdb_id.

    Attributes:

    tmdb - an instance of TMDB (API proxy)
    info (abstract) - the type-specific TMDB data for the object
    """
    def __init__(self, tmdb_id, data=None):
        self.__key = str(tmdb_id)
        if self.__key.startswith('tt'):
            self.__key = str(self.info['id'])
        # If data is provided in the constructor -- parsed from TMDB search results -- we save that in __basic_data,
        # and use that to handle field accesses until we hit one that requires the full set.
        self.__basic_data = data
        self.__full_data = None

    @property
    def data(self):
        """
        The data accessor is agnostic between basic data and full lookup data. It prefers full data if it's already
        available; if not, it falls back to basic data; if there is none, it issues the lookup.

        If the field you want is only available in lookup data, use the full_data accessor.
        """
        if self.__full_data:
            return self.__full_data
        if self.__basic_data:
            return self.__basic_data
            # Lazy property call that issues lookup.
        return self.full_data


    @lazyProperty
    def full_data(self):
        if self.__full_data:
            return self.__full_data
            # Sort of hacky -- calls a function implemented by ResolverObject.

        # We don't catch the LookupRequiredError here because if you are initializing a capped-lookup object without
        # passing in initial data, you are doing it wrong.
        self.countLookupCall('full data')
        self.__full_data = self.lookup_data()
        return self.__full_data

    def lookup_data(self):
        raise NotImplementedError()

    @property
    def key(self):
        return self.__key

    @property
    def source(self):
        return "tmdb"

    @lazyProperty
    def tmdb(self):
        return globalTMDB()

    def __repr__(self):
        return pformat( self.info )


# Note that TMDB results have two image sources -- backdrop_path and poster_path -- that we're currently not using,
# Kevin says because they won't let us directly hotlink.
class TMDBMovie(_TMDBObject, ResolverMediaItem):
    """
    TMDB movie proxy
    """
    def __init__(self, tmdb_id, data=None, maxLookupCalls=None):
        _TMDBObject.__init__(self, tmdb_id, data=data)
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=maxLookupCalls)

    @property
    def valid(self):
        try:
            self.full_data
            return True
        except HTTPError:
            return False

    def lookup_data(self):
        return self.tmdb.movie_info(self.key)

    @lazyProperty
    def _castsRaw(self):
        try:
            self.countLookupCall('cast')
            return self.tmdb.movie_casts(self.key)
        except LookupRequiredError:
            return []

    @lazyProperty
    def name(self):
        return self.data['title']

    @lazyProperty
    def popularity(self):
        try:
            return self.data['popularity']
        except Exception:
            return None
    
    @lazyProperty
    def imdb(self):
        try:
            return self.full_data['imdb_id']
        except KeyError:
            return None
        except LookupRequiredError:
            return None

    @lazyProperty
    def cast(self):
        try:
            return [
                {
                'name':entry['name'],
                'character':entry['character'],
                'source':self.source,
                'key':entry['id'],
                }
            for entry in self._castsRaw['cast']
            ]
        except Exception:
            pass
        return []

    @lazyProperty
    def directors(self):
        try:
            crew = self._castsRaw['crew']
            for entry in crew:
                if entry['job'] == 'Director':
                    return [{
                        'name': entry['name'],
                        'source': self.source,
                        'key': entry['id'],
                    }]
        except Exception:
            pass
        return []

    @lazyProperty
    def release_date(self):
        try:
            string = self.data['release_date']
            return parseDateString(string)
        except KeyError:
            pass
        return None

    @lazyProperty
    def length(self):
        try:
            if 'runtime' not in self.full_data:
                return -1  # TODO: Would None be more appropriate here?
            return self.full_data['runtime'] * 60
        except LookupRequiredError:
            return None

    @lazyProperty 
    def genres(self):
        try:
            if 'genres' not in self.full_data:
                logs.debug('No genres for %s (%s:%s)' % (self.name, self.source, self.key))
                return []
            return [ entry['name'] for entry in self.full_data['genres'] ]
        except LookupRequiredError:
            return []


class TMDBSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class TMDBSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'tmdb',
            groups=[
                'directors',
                'cast',
                'desc',
                # 'short_description',
                'genres',
                'imdb',
            ],
            kinds=[
                'media_item',
            ],
            types=[
                'movie',
            ]
        )
        self.__max_cast = 6

    @lazyProperty
    def __tmdb(self):
        return globalTMDB()

    def entityProxyFromKey(self, key, **kwargs):
        try:
            return TMDBMovie(key)
        except KeyError:
            logs.warning('Unable to find TMDB item for key: %s' % key)
            raise
        return None

    def matchSource(self, query):
        if query.isType('movie'):
            return self.movieSource(query)
        if query.kind == 'search':
            return self.searchAllSource(query)
        
        return self.emptySource

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.tmdb_id = proxy.key
        return True

    def movieSource(self, query):
        def gen():
            try:
                results = self.__tmdb.movie_search(query.name)
                if results is None:
                    return
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

    def searchLite(self, queryCategory, queryText, timeout=None):
        raw_results = self.__tmdb.movie_search(queryText)['results']
        # 20 results is good enough for us. No second requests.
        resolver_objects = [ TMDBMovie(result['id'], data=result, maxLookupCalls=0) for result in raw_results ]
        scored_results = scoreResultsWithBasicDropoffScoring(resolver_objects, sourceScore=1.0)
        # TODO: We could incorporate release date recency or popularity into our ranking, but for now will assume that
        # TMDB is clever enough to handle that for us.
        return scored_results

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.debug('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
            
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

    def entityProxyFromKey(self, tmdb_id, **kwargs):
        # Todo: Make sure we fail gracefully if id is invalid
        try:
            return TMDBMovie(tmdb_id)
        except Exception as e:
            logs.warning("Error: %s" % e)
            raise

    # def enrichEntity(self, entity, controller, decorations, timestamps):
    #     GenericSource.enrichEntity(self, entity, controller, decorations, timestamps)
    #     title = entity['title']
    #     if title is not None:
    #         tmdb_id = entity['tmdb_id']
    #         if tmdb_id is not None:
    #             movie = TMDBMovie(tmdb_id)
    #             try:
    #                 casts = self.__tmdb.movie_casts(tmdb_id)
    #                 if 'cast' in casts:
    #                     cast = casts['cast']
    #                     cast_order = {}
    #                     for entry in cast:
    #                         name = entry['name']
    #                         order = int(entry['order'])
    #                         cast_order[order] = name
    #                     sorted_cast = [ cast_order[k] for k in sorted(cast_order.keys()) ]
    #                     if len( sorted_cast ) > self.__max_cast:
    #                         sorted_cast = sorted_cast[:self.__max_cast]
    #                     cast_string = ', '.join(sorted_cast)
    #                     if entity['cast'] == None:
    #                         entity['cast'] = cast_string
    #                 if 'crew' in casts:
    #                     crew = casts['crew']
    #                     director = None
    #                     for entry in crew:
    #                         name = entry['name']
    #                         job = entry['job']
    #                         if job == 'Director':
    #                             director = name
    #                     if director is not None:
    #                         entity['director'] = director
                        
    #             except Exception:
    #                 pass
    #             info = movie.info
    #             if 'tagline' in info:
    #                 tagline = info['tagline']
    #                 if tagline is not None and tagline != '':
    #                     entity['short_description'] = tagline
    #             if 'overview' in info:
    #                 overview = info['overview']
    #                 if overview is not None and overview != '':
    #                     entity['desc'] = overview

    #             if movie.imdb is not None:
    #                 entity['imdb_id'] = movie.imdb;
    #             if len(movie.genres) > 0:
    #                 entity['genres'] = list(movie.genres)
        
    #     return True

if __name__ == '__main__':
    demo(TMDBSource(), 'Avatar')

