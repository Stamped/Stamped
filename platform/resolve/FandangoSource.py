# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FandangoSource', 'FandangoMovie' ]

import Globals
from logs import report

try:
    import logs, re
    from libs.TMDB                  import globalTMDB
    from resolve.GenericSource              import GenericSource
    from utils                      import lazyProperty
    from abc                        import ABCMeta, abstractproperty
    from urllib2                    import HTTPError
    from datetime                   import datetime
    from resolve.Resolver                   import *
    from resolve.ResolverObject             import *
    from pprint                     import pformat, pprint
    from libs.LibUtils              import parseDateString
except:
    report()
    raise

class DumbFandangoMovie(ResolverMediaItem):
    def __init__(self):
        ResolverMediaItem.__init__(self, types=['movie'])

    @lazyProperty
    def source(self):
        return 'fandango'

    @lazyProperty
    def raw_name(self):
        return None

    def _cleanName(self, name):
        return name

    @lazyProperty
    def key(self):
        return None


class FandangoMovie(ResolverMediaItem):
    @classmethod
    def createMovieFromData(cls, data):
        if hasattr(data, 'id'):
            return cls(data)

    def __init__(self, data):
        ResolverMediaItem.__init__(self, types=['movie'])
        self.__data = data

    @lazyProperty
    def source(self):
        return 'fandango'

    @lazyProperty
    def raw_name(self):
        return self.__data.title

    def _cleanName(self, name):
        return name

    @lazyProperty
    def key(self):
        return self.__data.id

    @lazyProperty
    def url(self):
        return self.__data.link


class FandangoSource(GenericSource):
    def __init__(self):
        GenericSource.__init__(self, 'fandango', groups=['url'], kinds=['media_item'], types=['movie'])

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        if proxy.key:
            entity.sources.fandango_id = proxy.key
        if proxy.url:
            entity.sources.fandango_url = proxy.url
        return True

    # At the time of writing, Fandango doesn't have good API, so we can't exactly do lookups using
    # any key or query. The next two methods are just dumb implementations.
    def entityProxyFromKey(self, key, **kwargs):
        return DumbFandangoMovie()

    def matchSource(self, query):
        return lambda start, end: []

