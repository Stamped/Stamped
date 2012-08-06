#!/usr/bin/env python
from __future__ import absolute_import

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
from pprint import pprint

from resolve.AmazonSource import AmazonBook
from resolve.FandangoSource import FandangoMovie
from resolve.NYTimesSource import NYTimesBook
from resolve.StampedSource import StampedSource
from resolve.ResolverObject import *

FEED_SOURCES = {
    'fandango_upcoming' : ('http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839', FandangoMovie.createMovie),
    'fandango_opening' : ('http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839', FandangoMovie.createMovie),
    'fandango_popular' : ('http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839', FandangoMovie.createMovieFromTopBoxOffice),

    'amazon_book_new' : ('http://www.amazon.com/gp/rss/new-releases/books', AmazonBook.createFromRssEntry(False)),
    'amazon_book_bestseller' : ('http://www.amazon.com/gp/rss/bestsellers/books', AmazonBook.createFromRssEntry(True)),
    'amazon_kindle_new' : ('http://www.amazon.com/gp/rss/new-releases/digital-text', AmazonBook.createFromRssEntry(False)),
    'amazon_kindle_bestseller' : ('http://www.amazon.com/gp/rss/bestsellers/digital-text', AmazonBook.createFromRssEntry(True)),

    'nytimes_bestseller' : ('http://feeds.nytimes.com/nyt/rss/BestSellers', NYTimesBook.parseFromRss),
}


class RssFeedScraper(object):
    def fetchSources(self, sources=None):
        sources = sources or FEED_SOURCES.keys()

        proxies = []
        for source in sources:
            proxies.extend(self.__fetchFromSource(source))
        return proxies

    def __fetchFromSource(self, source):
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


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'all':
        args = FEED_SOURCES.keys()
    else:
        args = sys.argv[1:]

    for source in args:
        if source not in FEED_SOURCES:
            print >> sys.stderr, 'Source "%s" not found. Valid sources are: %s' % (source, FEED_SOURCES.keys())
            return

    scraper = RssFeedScraper()
    for proxy in scraper.fetchSources(args):
        print str(proxy)


if __name__ == '__main__':
    main()
