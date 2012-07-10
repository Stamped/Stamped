#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import feedparser
import sys

from collections import Iterable
from optparse import OptionParser
from pprint import pprint

from api.MongoStampedAPI import globalMongoStampedAPI
from resolve.AmazonSource import AmazonBook
from resolve.EntityProxyContainer import EntityProxyContainer
from resolve.FandangoSource import FandangoMovie
from resolve.NYTimesSource import NYTimesBook
from resolve.StampedSource import StampedSource
from resolve.ResolverObject import *
from utils import lazyProperty

FEED_SOURCES = {
    'fandango_upcoming' : ('http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839', FandangoMovie.createMovie),
    'fandango_opening' : ('http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839', FandangoMovie.createMovie),
    'fandango_popular' : ('http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839', FandangoMovie.createMovieFromTopBoxOffice),

    'amazon_book_new' : ('http://www.amazon.com/gp/rss/new-releases/books', AmazonBook.createFromRssEntry),
    'amazon_book_bestseller' : ('http://www.amazon.com/gp/rss/bestsellers/books', AmazonBook.createFromRssEntry),
    'amazon_kindle_new' : ('http://www.amazon.com/gp/rss/new-releases/digital-text', AmazonBook.createFromRssEntry),
    'amazon_kindle_bestseller' : ('http://www.amazon.com/gp/rss/bestsellers/digital-text', AmazonBook.createFromRssEntry),

    'nytimes_bestseller' : ('http://feeds.nytimes.com/nyt/rss/BestSellers', NYTimesBook.parseFromRss),
}


def fetchFromSource(source):
    feedUrl, parserFn = FEED_SOURCES[source]
    data = feedparser.parse(feedUrl)
    parsed = filter(None, (parserFn(entry) for entry in data.entries))
    results = []
    for parsedEntry in parsed:
        if isinstance(parsedEntry, Iterable):
            results.extend(parsedEntry)
        else:
            results.append(parsedEntry)
    return results


def mergeProxyIntoDb(proxy, stampedApi, stampedSource):
    entity_id = stampedSource.resolve_fast(proxy.source, proxy.key)

    if entity_id is None:
        results = stampedSource.resolve(proxy)
        if len(results) > 0 and results[0][0]['resolved']:
            # Source key found in the Stamped DB
            entity_id = results[0][1].key
    if entity_id:
        stampedApi.mergeEntityId(entity_id)

    if entity_id is None:
        entityProxy = EntityProxyContainer(proxy)
        entity = entityProxy.buildEntity()
        stampedApi.mergeEntity(entity)


def main():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("--save_to_db", action='store_true', dest='saveToDb', default=False)

    options, args = parser.parse_args()
    if len(args) == 1 and args[0] == 'all':
        args = FEED_SOURCES.keys()

    for source in args:
        if source not in FEED_SOURCES:
            print >> sys.stderr, 'Source "%s" not found. Valid sources are: %s' % (source, FEED_SOURCES.keys())
            return

    proxies = []
    for source in args:
        proxies.extend(fetchFromSource(source))

    if options.saveToDb:
        stampedApi = globalMongoStampedAPI()
        stampedSource = StampedSource(stamped_api=stampedApi)
        for proxy in proxies:
            mergeProxyIntoDb(proxy, stampedApi, stampedSource)
    else:
        for proxy in proxies:
            print str(proxy)

if __name__ == '__main__':
    main()
