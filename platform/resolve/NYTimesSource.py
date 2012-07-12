# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FandangoSource', 'FandangoMovie' ]

import Globals

import logs, re
from BeautifulSoup import BeautifulSoup
from utils import lazyProperty
from datetime import datetime
from resolve.DumbSource import DumbSource
from resolve.Resolver import *
from resolve.ResolverObject import *
from pprint import pformat, pprint

class NYTimesBook(ResolverMediaItem):
    @classmethod
    def parseFromRss(cls, data):
        pattern = re.compile(r'\d+. (.*), by (.*)')
        soup = BeautifulSoup(data.summary)
        result = []
        for line in soup.contents:
            if isinstance(line, basestring):
                match = pattern.match(line)
                if match:
                    result.append(cls(*match.groups()))
        return result


    def __init__(self, title, author):
        ResolverMediaItem.__init__(self, types=['book'])
        self.__title = title
        self.__author = author

    @lazyProperty
    def source(self):
        return 'nytimes'

    @lazyProperty
    def raw_name(self):
        return self.__title

    @lazyProperty
    def authors(self):
        return [{'name' : self.__author}]

    def _cleanName(self, name):
        return name.title()

    @lazyProperty
    def key(self):
        return self.__title + ' ' + self.__author

    @lazyProperty
    def last_popular(self):
        # This is the New York Times bestseller RSS scrape, so everything we see is currently
        # popular.
        return datetime.now()


class NYTimesSource(DumbSource):
    def __init__(self):
        super(NYTimesSource, self).__init__('nytimes', groups=['last_popular'])

