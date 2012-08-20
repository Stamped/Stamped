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
    from resolve.Resolver           import *
    from resolve.ResolverObject     import *
    from resolve.TitleUtils         import *
    from libs.TMDB                  import globalTMDB
    from resolve.GenericSource      import GenericSource, MERGE_TIMEOUT, SEARCH_TIMEOUT
    from utils                      import lazyProperty
    from abc                        import ABCMeta, abstractproperty
    from urllib2                    import HTTPError
    from datetime                   import datetime, timedelta
    from pprint                     import pformat, pprint
    from libs.LibUtils              import parseDateString
    from search.ScoringUtils        import *
    from search.DataQualityUtils    import *
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


# Note that TMDB results have two image sources -- backdrop_path and poster_path -- that we're currently not using,
# Kevin says because they won't let us directly hotlink.
class TMDBMovie(_TMDBObject, ResolverMediaItem):
    """
    TMDB movie proxy
    """
    def __init__(self, tmdb_id, data=None, maxLookupCalls=None):
        _TMDBObject.__init__(self, tmdb_id, data=data)
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=maxLookupCalls)

    def _cleanName(self, rawName):
        return cleanMovieTitle(rawName)

    @property
    def valid(self):
        try:
            self.full_data
            return True
        except HTTPError:
            return False

    def lookup_data(self):
        return self.tmdb.movie_info(self.key, priority='low', timeout=MERGE_TIMEOUT)

    @lazyProperty
    def _castsRaw(self):
        try:
            self.countLookupCall('cast')
            return self.tmdb.movie_casts(self.key, priority='low', timeout=MERGE_TIMEOUT)
        except LookupRequiredError:
            return []

    @lazyProperty
    def raw_name(self):
        if self.data:
            return self.data['title']
        return ''

    @lazyProperty
    def popularity(self):
        if self.data:
            return self.data['popularity']
        return ''
    
    @lazyProperty
    def imdb(self):
        try:
            if self.full_data:
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
            if self.data:
                string = self.data['release_date']
                return parseDateString(string)
        except KeyError:
            pass
        return None

    @lazyProperty
    def length(self):
        try:
            if not self.full_data:
                return []
            if not self.full_data.get('runtime', None):
                return -1  # TODO: Would None be more appropriate here?
            return self.full_data['runtime'] * 60
        except LookupRequiredError:
            return None

    @lazyProperty 
    def genres(self):
        try:
            if not self.full_data:
                return []
            if not self.full_data.get('genres', None):
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
                'genres',
                'imdb',
                'length',
                'release_date',
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

    def movieSource(self, query):
        def gen():
            results = self.__tmdb.movie_search(query.name, priority='low', timeout=MERGE_TIMEOUT)
            if results is None:
                return
            for movie in results['results']:
                yield movie
            pages = results['total_pages']

            if pages > 1:
                for p in range(1,pages):
                    results = self.__tmdb.movie_search(query.name, page=p+1, priority='low', timeout=MERGE_TIMEOUT)
                    for movie in results['results']:
                        yield movie
        return self.generatorSource(gen(), constructor=lambda x: TMDBMovie(x['id'], x, 0))

    def __pareOutResultsFarInFuture(self, resolverObjects):
        """
        TMDB has a bad habit of giving results that are still far out, sometimes results that are too far out to be sure
        that a movie will ever be made. We make the editorial decision not to show any movie more than 90 days out.
        In 99.9% of cases this should be beneficial. Every once in a blue moon someone might want to stamp a movie they
        just saw a first trailer for and are really excited about, but I think that's not strictly an appropriate use
        of a stamp anyway; how can you recommend what you haven't seen, because it isn't even finished yet?
        """
        cutoff = datetime.now() + timedelta(90)
        def isFarInFuture(resolverObject):
            return resolverObject.release_date and resolverObject.release_date > cutoff

        return [resolverObject for resolverObject in resolverObjects if not isFarInFuture(resolverObject)]

    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=False):
        raw_results = self.__tmdb.movie_search(queryText, priority='high', timeout=SEARCH_TIMEOUT)['results']
        if logRawResults:
            logComponents = ['\n\n\nTMDB RAW RESULTS\nTMDB RAW RESULTS\nTMDB RAW RESULTS\n\n\n']
            for result in raw_results:
                logComponents.extend(['\n\n', pformat(result), '\n\n'])
            logComponents.append('\n\n\nEND TMDB RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))

        # 20 results is good enough for us. No second requests.
        resolver_objects = [ TMDBMovie(result['id'], data=result, maxLookupCalls=0) for result in raw_results ]
        resolver_objects = self.__pareOutResultsFarInFuture(resolver_objects)
        search_results = scoreResultsWithBasicDropoffScoring(resolver_objects, sourceScore=1.0)
        for search_result in search_results:
            applyMovieTitleDataQualityTests(search_result, queryText)
            adjustMovieRelevanceByQueryMatch(search_result, queryText)
            augmentMovieDataQualityOnBasicAttributePresence(search_result)
        # TODO: We could incorporate release date recency or popularity into our ranking, but for now will assume that
        # TMDB is clever enough to handle that for us.
        return search_results

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
                results = self.__tmdb.movie_search(query.query_string, priority='high', timeout=SEARCH_TIMEOUT)
                if results is None:
                    return 
                for movie in results['results']:
                    yield movie
                pages = results['total_pages']

                if pages > 1:
                    for p in range(1,pages):
                        results = self.__tmdb.movie_search(query.query_string, page=p+1, priority='high', timeout=SEARCH_TIMEOUT)
                        for movie in results['results']:
                            yield movie
            except GeneratorExit:
                pass
        return self.generatorSource(gen(), constructor=lambda x: TMDBSearchAll(TMDBMovie(x['id'], x, 0)))

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


if __name__ == '__main__':
    demo(TMDBSource(), 'Avatar')

