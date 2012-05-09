#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from SeedSource             import SeedSource
    from FactualSource          import FactualSource
    from GooglePlacesSource     import GooglePlacesSource
    from SinglePlatformSource   import SinglePlatformSource
    from TMDBSource             import TMDBSource
    from FormatSource           import FormatSource
    from RdioSource             import RdioSource
    from SpotifySource          import SpotifySource
    from iTunesSource           import iTunesSource
    from AmazonSource           import AmazonSource
    from StampedSource          import StampedSource
    from TheTVDBSource          import TheTVDBSource
    from NetflixSource          import NetflixSource
    from InstagramSource        import InstagramSource
except:
    report()
    raise

allSources = [
    SeedSource,
    FormatSource,
    FactualSource,
    GooglePlacesSource,
    SinglePlatformSource,
    InstagramSource,
    iTunesSource,
    TMDBSource,
    RdioSource,
    SpotifySource,
    AmazonSource,
    TheTVDBSource,
    NetflixSource,
    StampedSource,
]

def getSource(name):
    for source in allSources:
        source = source()
        if source.sourceName == name:
            return source
    raise KeyError('Source not found: %s' % name)
