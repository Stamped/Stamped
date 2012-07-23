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
    from resolve.GenericSource      import GenericSource, MERGE_TIMEOUT, SEARCH_TIMEOUT
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from pprint                     import pformat
    from datetime                   import datetime
    from resolve.Resolver           import *
    from resolve.ResolverObject     import *
    from resolve.TitleUtils         import *
except:
    report()
    raise

class _NetflixObject(object):
    """
    Abstract superclass for Netflix objects.

    _NetflixObjects must be instantiated with the json-dict structure returned by the api for a catalog_title
    """

    def __init__(self, titleObj):
        self.__key = str(titleObj['id'])
        self._titleObj = titleObj

    def _asList(self, elmt):
        if isinstance(elmt, list):
            return elmt
        elif elmt == None:
            return []
        return [elmt]

    def _getFromLinks(self, key, search, returnKey):
        for item in self._asList(self._titleObj['link']):
            if item[key].find(search) != -1:
                return item[returnKey]
        return None

    @property
    def key(self):
        return self.__key

    @property
    def source(self):
        return "netflix"

    @lazyProperty
    def netflix(self):
        return globalNetflix()

    @lazyProperty
    def is_instant_available(self):
        try:
            formats = self._getFromLinks('href', 'format_availability', 'delivery_formats')
            for availableType in self._asList(formats['availability']):
                if availableType['category']['term'] == 'instant':
                    return True
            return False
        except Exception:
            return False

    @lazyProperty
    def instant_available_until(self):
        try:
            formats = self._getFromLinks('href', 'format_availability', 'delivery_formats')
            for availableType in self._asList(formats['availability']):
                if availableType['category']['term'] == 'instant':
                    return datetime.fromtimestamp(availableType['available_until'])
            return None
        except Exception as e:
            return None

    def _cleanName(self, title):
        return cleanTvTitle(title)

    @lazyProperty
    def raw_name(self):
        title = self._titleObj['title']['regular']
        # OK, this is bizarre and FUCKED and we should fix the way this gets parsed in the beginning rather than hacking
        # this shit in here. But what we're dealing with is a problem where if the title is numeric -- like, "1984" --
        # we literally get an int value rather than a string here. Ugh.
        if not isinstance(title, basestring):
            title = unicode(title)
        return title

    @lazyProperty
    def cast(self):
        try:
            cast = filter(lambda link : link['title'] ==  u'cast',  self._titleObj['link'])[0]['people']['link']
            return [
                {
                'name':         entry['title'],
                'source':       self.source,
                }
            for entry in cast
            ]
        except Exception:
            return []

    @lazyProperty
    def images(self):
        try:
            #hack to replace large
            return [ self._titleObj['box_art']['large'] ]
        except Exception:
            return []


    # Netflix only returns the release year.  Since the API can't distinguish exact dates from years, this is
    #  excluded.  Also, the dateWeight function is only checking for exact matches anyway.
#    @lazyProperty
#    def release_date(self):
#        try:
#            return datetime(self._titleObj['release_year'], 1, 1)
#        except KeyError:
#            return None

    @lazyProperty
    def url(self):
        try:
            webpage = filter(lambda link :  link['title'] ==  u'web page',  self._titleObj['category'])[0]
            return webpage['href']
        except KeyError:
            return None


    def __repr__(self):
#        return "<%s %s %s>" % (self.source, self.type, self.name)
        return pformat( self._titleObj )

class NetflixMovie(_NetflixObject, ResolverMediaItem):
    """
    Netflix movie proxy
    """
    def __init__(self, titleObj):
        _NetflixObject.__init__(self, titleObj)
        ResolverMediaItem.__init__(self, types=['movie'])

    @lazyProperty
    def popularity(self):
        try:
            return self._titleObj['average_rating']
        except KeyError:
            return None

    @lazyProperty
    def directors(self):
        try:
            directors = filter(lambda link : link['title'] ==  u'directors',  self._titleObj['link'])[0]['people']['link']
            # api returns either a dict or a list of dicts depending on len > 1
            if isinstance(directors, list):
                return [
                    {
                    'name':         entry['title'],
                    'source':       self.source,
                    }
                        for entry in directors
                ]
            else:
                return [
                    {
                    'name':         directors['title'],
                    'source':       self.source
                    }
                ]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        try:
            return self._titleObj['runtime']
        except KeyError:
            return None

    @lazyProperty
    def mpaa_rating(self):
        try:
            ratings = filter(lambda link : '/mpaa_ratings' in link['scheme'],  self._titleObj['category'])
            if ratings:
                return ratings[0]['label']
        except KeyError:
            return None


class NetflixTVShow(_NetflixObject, ResolverMediaCollection):
    """
    Netflix tv show proxy
    """
    def __init__(self, titleObj):
        _NetflixObject.__init__(self, titleObj)
        ResolverMediaCollection.__init__(self, types=['tv'])

    @lazyProperty
    def mpaa_rating(self):
        try:
            rating = filter(lambda link : '/tv_ratings' in link['scheme'],  self._titleObj['category'])[0]
            return rating['label']
        except KeyError:
            return None


class NetflixSource(GenericSource):
    def __init__(self):
        GenericSource.__init__(self, 'netflix',
            groups=[
                'release_date',
                'desc',
                'directors',
                'cast',
                'mpaa_rating',
                'genres',
                'directors',
                'images',
                'length',
                'url',
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

    def getId(self, entity):
        idField = getattr(entity.sources, self.idField)
        try:
            int(idField)
            # ID fields that are just integers are broken.
            return None
        except Exception:  # Could be ValueError (if it's a string) or TypeError (if it's None)
            return idField

    def entityProxyFromKey(self, netflix_id, **kwargs):
        try:
            titleObj = self.__netflix.getTitleDetails(netflix_id, timeout=MERGE_TIMEOUT)
            if titleObj['id'].find('/movies/') != -1:
                return NetflixMovie(titleObj)
            elif titleObj['id'].find('/series/') != -1:
                return NetflixTVShow(titleObj)
        except KeyError:
            logs.warning('Unable to find Netflix item for key: %s' % netflix_id)

    def matchSource(self, query):
        if query.isType('movie'):
            return self.movieSource(query)
        if query.isType('tv'):
            return self.tvSource(query)

    def __genericSourceGen(self, query, filter):
        def gen():
            try:
                results = self.__netflix.searchTitles(query.name, timeout=MERGE_TIMEOUT)

                for title in results['catalog_title']:
                    if (filter(title)):
                        yield title

                num_results = results['number_of_results']
                result_counter = results['results_per_page']

                # return all remaining results through separate page calls to the api
                while result_counter < num_results:
                    results = self.__netflix.searchTitles(query.name, start=result_counter, timeout=MERGE_TIMEOUT)
                    result_counter += results['results_per_page']

                    # ['catalog_title'] contains the actual dict of values for a given result.  It's a weird structure.
                    for title in results['catalog_title']:
                        yield title
            except GeneratorExit:
                pass
            except KeyError:
                return
        return gen()

    def movieSource(self, query):
        def filter(title):
            return title['id'].find('/movies/') != -1
        gen = self.__genericSourceGen(query, filter)
        return self.generatorSource(gen, constructor=NetflixMovie)

    def tvSource(self, query):
        def filter(title):
            return title['id'].find('/series/') != -1
        gen = self.__genericSourceGen(query, filter)
        return self.generatorSource(gen, constructor=NetflixTVShow)


if __name__ == '__main__':
    demo(NetflixSource(), 'arrested development')
