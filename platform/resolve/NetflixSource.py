#!/usr/bin/env python

"""
"""
__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'NetflixSource', 'NetflixMovie' ]

import Globals
from logs import report

try:
    import logs
    from libs.Netflix               import globalNetflix
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from Resolver                   import *
except:
    report()
    raise


# TODO: this class is unfinished!


class _NetflixObject(object):
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API wrapper)
    """

    def __init__(self, titleObj):
        self.__key = str(titleObj['id'])
        self.__titleObj = titleObj

    @property
    def key(selfself):
        return self.__key

    @property
    def source(self):
        return "netflix"

    @lazyProperty
    def netflix(self):
        return globalNetflix()

    @lazyProperty
    def name(self):
        return self.__titleObj['title']


#    @abstractproperty
#    def info(self):
#        pass

#    def __repr__(self):
#        return pformat(self.info)

    def __repr__(self):
        return "<%s %s %s>" % (self.source, self.type, self.name)


class _NetflixMovie(_NetflixObject, ResolverMediaItem):
    """
    Netflix movie proxy
    """
    def __init__(self, titleObj):
        _NetflixObject.__init__(self, titleObj)
        ResolveMediaItem.__init__(self, types=['movie'])

    @lazyProperty
    def popularity(self):
        try:
            return self.__titleObj['average_rating']
        except KeyError:
            return None

    @lazyProperty
    def cast(self):
        try:
            cast = filter(lambda link : 'cast' in link['href'], self.__titleObj['link'])[0]['people']['link']
            return [
                {
                    'name':         entry['title'],
                    'source':       self.source,
                }
                    for entry in cast
            ]
        except Exception:
            return None

    @lazyProperty
    def release_date(self):
        try:
            string = self.__titleObj['release_year']
        except KeyError:
            return None



class _NetflixTVShow(_NetflixObject, ResolverMediaCollection):
    """
    Netflix tv show proxy
    """
    def __init__(self, titleObj):
        _NetflixObject.__init__(self, titleObj)
        ResolverMediaItem.__init__(self, types=['tv'])




class NetflixSearchAll(ResolverProxy, ResolverSearchAll):
    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class NetflixSource(GenericSource):
    """

    """
    def __init__(self):
        GenericSource.__init__(self, 'netflix',
            groups=[
                'release_date',
                'directors',
                'cast',
                'desc',
                'mpaa_rating',
                'genres',
                'tracks',
                'publishers',
                'images',
                'length'
            ],
            kinds=[
                'media_item',
                'media_collection'
            ],
            types=[
                'movie',
                'tv'
            ]
        )

    @lazyProperty
    def __netflix(self):
        return globalNetflix()


#    def entityProxyFromKey(self, key, **kwargs):
#        try:
#            return
#        except KeyError:
#            raise

    def matchSource(self, query):
        if query.isType('movie'):
            return self.movieSource(query)
        if query.isType('tv'):
            return self.tvSource(query)
        if query.kind == 'search':
            return self.searchAllSource(query)

    def __genericSourceGen(self, query, filter):
        def gen():
            try:
                results = self.__netflix.title_search(query.name)['catalog_titles']
                for title in results['catalog_title']:
                    if (filter(title)):
                        yield title

                num_results = results['number_of_results']
                result_counter = results['results_per_page']

                # return all remaining results through separate page calls to the api
                while (result_counter < num_results):
                    results = self.__netflix.title_search(query, start_index=result_counter)['catalog_titles']
                    result_counter += results['results_per_page']
                    # 'catalog_title'value  is the actual dict of values for a given result.  It's a weird structure.
                    for title in results['catalog_title']:
                        yield title
            except GeneratorExit:
                pass
        return gen()

    def movieSource(self, query):
        def filter(title):
            return title['id'].contains('/movies/')
        gen = self.__genericSourceGen(query, filter)
        return self.generatorSource(gen, constructor=NetflixMovie)

    def tvSource(self, query):
        def filter(title):
            return title['id'].contains('/series/')
        gen = self.__genericSourceGen(query, filter)
        return self.generatorSource(gen, constructor=NetflixTVShow)


    def searchAllSource(self, query):
        def gen():
            try:
                results = self.__netflix.movie_search
            except GeneratorExit:
                    pass
