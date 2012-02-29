#!/usr/bin/python

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
    from pprint                     import pformat
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
    def name(self):
        return self.info['title']

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

class TMDBSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'tmdb',
            'director',
            'cast',
        )
        self.__max_cast = 6

    @lazyProperty
    def __tmdb(self):
        return globalTMDB()

    def matchSource(self, query):
        if query.type == 'movie':
            return self.movieSource(query)
        else:
            return self.emptySource

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
        generator = gen()
        movies = []
        def source(start, count):
            total = start + count
            while total - len(movies) > 0:
                try:
                    movies.append(generator.next())
                except StopIteration:
                    break

            if start + count <= len(movies):
                result = movies[start:start+count]
            elif start < len(movies):
                result = movies[start:]
            else:
                result = []
            return [ TMDBMovie( entry['id'] ) for entry in result ]
        return source

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
        if controller.shouldEnrich('tmdb',self.sourceName,entity):
            title = entity['title']
            if title is not None:
                tmdb_id = None
                timestamps['tmdb'] = controller.now
                movies = self.__tmdb.movie_search(title)['results']
                if len(movies) > 5:
                    movies = movies[:5]
                best_movie = None
                for movie in movies:
                    score = 0
                    release_date = self.__release_date(movie)
                    if 'release_date' in entity:
                        if release_date == entity['release_date']:
                            score += 6
                        else:
                            score -= 2
                    if title == movie['title']:
                        score += 3
                    elif title == movie['original_title']:
                        score += 2
                    else:
                        alternative_titles = self.__tmdb.movie_alternative_titles(movie['id'])
                        found = False
                        for alternative_title in alternative_titles:
                            if alternative_title == title:
                                found = True
                                break
                        if found:
                            score += 1
                        else:
                            score -= 5
                    if score > 6:
                        best_movie = movie
                        break
                    if score < -5:
                        break
                if best_movie is not None:
                    tmdb_id = str(best_movie['id'])
                entity['tmdb_id'] = tmdb_id
                if tmdb_id is not None:
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
        return True

if __name__ == '__main__':
    demo(TMDBSource(), 'Avatar')
