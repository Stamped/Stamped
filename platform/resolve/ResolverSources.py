#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from resolve.SeedSource import SeedSource
from resolve.FactualSource import FactualSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.SinglePlatformSource import SinglePlatformSource
from resolve.TMDBSource import TMDBSource
from resolve.FormatSource import FormatSource
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.iTunesSource import iTunesSource
from resolve.AmazonSource import AmazonSource
from resolve.StampedSource import StampedSource
from resolve.TheTVDBSource import TheTVDBSource
from resolve.NetflixSource import NetflixSource
from resolve.InstagramSource import InstagramSource
from resolve.FandangoSource import FandangoSource
from resolve.NYTimesSource import NYTimesSource
from resolve.UMDSource import UMDSource

allSources = [
    SeedSource,
    FormatSource,
    FactualSource,
    FandangoSource,
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
    NYTimesSource,
    UMDSource,
]

def getSource(name):
    for source in allSources:
        source = source()
        if source.sourceName == name:
            return source
    raise KeyError('Source not found: %s' % name)
