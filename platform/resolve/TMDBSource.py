#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'TMDBSource' ]

import Globals
from logs import report

try:
    from libs.TMDB                  import TMDB
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    from urllib2                    import HTTPError
    from datetime                   import datetime
    import re
except:
    report()
    raise

class TMDBSource(BasicSource):
    """
    """
    def __init__(self):
        BasicSource.__init__(self, 'tmdb',
            'tmdb',

            'director',
            'cast',
        )
        self.__max_cast = 6

    @lazyProperty
    def __tmdb(self):
        return TMDB()

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

