#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, sys
from resolve import EntityProxyComparator
from resolve.AmazonSource import AmazonSource
from resolve.FactualSource import FactualSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.iTunesSource import iTunesSource
from resolve.NetflixSource import NetflixSource
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.TMDBSource import TMDBSource
from resolve.TheTVDBSource import TheTVDBSource
from resolve.ResolverObject import *

SOURCES = {
    'amazon' : AmazonSource(),
    'factual' : FactualSource(),
    'googleplaces' : GooglePlacesSource(),
    'itunes' : iTunesSource(),
    'rdio' : RdioSource(),
    'spotify' : SpotifySource(),
    'tmdb' : TMDBSource(),
    'thetvdb' : TheTVDBSource(),
    'netflix' : NetflixSource(),
}

SOURCE_AND_KEY_RE = re.compile('([a-z_]+):(.*)')
def main():
    EntityProxyComparator.logComparisonLogic = True

    proxies = []
    for arg in sys.argv[1:]:
        source_and_key_match = SOURCE_AND_KEY_RE.match(arg)
        source_name, key = source_and_key_match.group(1), source_and_key_match.group(2)
        source = SOURCES[source_name]
        proxies.append(source.entityProxyFromKey(key))

    if len(proxies) < 2:
        raise Exception('You are shit at this.')

    if isAlbum(proxies[0]):
        comparator = EntityProxyComparator.AlbumEntityProxyComparator
    elif isArtist(proxies[0]):
        comparator = EntityProxyComparator.ArtistEntityProxyComparator
    elif isTrack(proxies[0]):
        comparator = EntityProxyComparator.TrackEntityProxyComparator
    elif isTvShow(proxies[0]):
        comparator = EntityProxyComparator.TvEntityProxyComparator
    elif isMovie(proxies[0]):
        comparator = EntityProxyComparator.MovieEntityProxyComparator
    elif isBook(proxies[0]):
        comparator = EntityProxyComparator.BookEntityProxyComparator
    elif isPlace(proxies[0]):
        comparator = EntityProxyComparator.PlaceEntityProxyComparator
    elif isApp(proxies[0]):
        comparator = EntityProxyComparator.AppEntityProxyComparator
    else:
        raise Exception('Unrecognized proxy type!')

    for i in range(len(proxies)):
        for j in range(i):
            proxy1 = proxies[i]
            proxy2 = proxies[j]
            print '\n\nCOMPARING: %s (%s:%s) to %s (%s:%s)' % (
                repr(proxy1.raw_name), proxy1.source, proxy1.key,
                repr(proxy2.raw_name), proxy2.source, proxy2.key,
            )
            result = comparator.compare_proxies(proxy1, proxy2)
            print '\nRESULT:', result, '\n\n'


if __name__ == '__main__':
    main()
