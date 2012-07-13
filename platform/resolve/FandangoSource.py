# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FandangoSource', 'FandangoMovie' ]

import Globals

import logs, re
from utils import lazyProperty
from datetime import datetime
from resolve.DumbSource import DumbSource
from resolve.Resolver import *
from resolve.ResolverObject import *
from pprint import pformat, pprint

class FandangoMovie(ResolverMediaItem):
    @classmethod
    def createMovie(cls, data):
        if hasattr(data, 'id'):
            return cls(data, False)

    @classmethod
    def createMovieFromTopBoxOffice(cls, data):
        if hasattr(data, 'id'):
            titlePattern = re.compile(r'\d+\.\s*(.*)\$.*$')
            match = titlePattern.match(data.title)
            if match:
                data.title = match.group(1)
            return cls(data, True)

    def __init__(self, data, popular):
        ResolverMediaItem.__init__(self, types=['movie'])
        self.__data = data
        self.__popular = popular

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

    @lazyProperty
    def release_date(self):
        # TODO(geoff): This is a huge huge huge huge hack. We don't get much info from Fandango, but
        # we only use it for upcoming releases, so we just use now as an approximation of the
        # release date.
        return datetime.now()

    @lazyProperty
    def last_popular(self):
        if self.__popular:
            return datetime.now()


class FandangoSource(DumbSource):
    def __init__(self):
        super(FandangoSource, self).__init__('fandango', groups=['last_popular'], kinds=['media_item'], types=['movie'])

