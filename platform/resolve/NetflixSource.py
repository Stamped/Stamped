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

    def __init__(self, netflix_id):
        self.__nef

    @lazyProperty
    def netflix(self):
        return globalNetflix()

    @lazyProperty
    def key(self):
        return self.__spotify_id

    @property 
    def source(self):
        return "spotify"

    def __repr__(self):
        return "<%s %s %s>" % (self.source, self.type, self.name)


