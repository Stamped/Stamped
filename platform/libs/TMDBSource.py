#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'TMDBSource' ]

import Globals
from logs import log, report

try:
    from AExternalSource    import AExternalSource
    from libs.TMDB          import TMDB
    from utils              import lazyProperty
    from datetime           import datetime
    import re
except:
    report()
    raise

class TMDBSource(AExternalSource):
    """
    Data-Source wrapper for TMDB services.
    """
    def __init__(self):
        AExternalSource.__init__(self)
        self.__eligible_subcategories = {
            'movie'             : 'film', 
        }

    @lazyProperty
    def __tmdb(self):
        return TMDB()

    def __release_date(self, movie):
        result = None
        if 'release_date' in movie:
            date_string = movie['release_date']
            match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$',date_string)
            if match is not None:
                try:
                    result = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
                except ValueError:
                    pass
        return result

    def resolveEntity(self, entity, controller):
        """
        Attempt to fill populate id fields based on seed data.

        Returns True if the entity was modified.
        """
        if entity['subcategory'] not in self.__eligible_subcategories:
            return False
        result = False
        if controller.shouldResolve('tmdb',self.sourceName,entity):
            title = entity['title']
            if title is not None:
                movies = self.__tmdb.movie_search(title)['results']
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
                        for alternative_title in alternative_title:
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
                    entity['tmdb_id'] = str(best_movie['id'])
                    entity['tmdb_timestamp'] = controller.now()
                    entity['tmdb_source'] = self.sourceName
                    result = True

        return result
    
    def enrichEntity(self, entity, controller):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        result = False

        return result

    def decorateEntity(self, entity, controller, decoration_db):
        """
        Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity fields if necessary.

        Returns True if the entity was modified.
        """
        return False

    @property
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        return 'tmdb'
    

