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
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from abc                        import ABCMeta, abstractproperty
    from urllib2                    import HTTPError
    from datetime                   import datetime
    from Resolver                   import *
    from ResolverObject             import *
    from pprint                     import pformat, pprint
    from libs.LibUtils              import parseDateString
except:
    report()
    raise

class _FandangoObject(object):
    __metaclass__ = ABCMeta
    """
    Abstract superclass (mixin) for Fandango objects.

    _FandangoObjects must be instantiated with their fandango_id.

    Attributes:

    fandango - an instance of Fandango (API wrapper)
    info (abstract) - the type-specific Fandango data for the object
    """
    def __init__(self, fandango_id):
        self.__key = int(fandango_id)

    @property
    def key(self):
        return self.__key

    @property
    def source(self):
        return "fandango"

    def __repr__(self):
        return "%s %s %s" % (self.name, self.source, self.date)


class FandangoMovie(_FandangoObject, ResolverMediaItem):
    """
    Fandango movie wrapper
    """
    def __init__(self, fandango_id, title, date):
        _FandangoObject.__init__(self, fandango_id)
        ResolverMovie.__init__(self)        
        self.__date = date
        self.__title = title

    @lazyProperty
    def name(self):
        return self.__title

    @lazyProperty
    def date(self):
        return self.__date


class FandangoSource(GenericSource):
    def __init__(self):
        GenericSource.__init__(self, 'fandango',
            'release_date',
        )

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithWrapper(self, wrapper, entity, controller, decorations, timestamps)
        entity.sources.fandango_id = wrapper.key
        return True


def testFandango(fandango_id, title, release_date):
    import TMDBSource
    tmdb = TMDBSource.TMDBSource()

    source = tmdb.matchSource(movie)

    results = resolver.resolve(movie, source)

    pprint(results)


if __name__ == '__main__':
    testFandango('1234', '21 Jump Street', parseDateString('2012-03-12'))

