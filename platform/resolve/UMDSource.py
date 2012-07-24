# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs, re
from utils import lazyProperty
from datetime import datetime
from resolve.DumbSource import DumbSource
from resolve.Resolver import *
from resolve.ResolverObject import *
from pprint import pformat, pprint

class UMDTrack(ResolverMediaItem):
    def __init__(self, data):
        ResolverMediaItem.__init__(self, types=['track'])
        self.__data = data

    @lazyProperty
    def source(self):
        return 'umdmusic'

    @lazyProperty
    def raw_name(self):
        return self.__data['name']

    def _cleanName(self, name):
        return name

    @lazyProperty
    def artists(self):
        return [{'name' : self.__data['artist']}]

    @lazyProperty
    def key(self):
        return '%s - %s' % (self.__data['name'], self.__data['artist'])

    @lazyProperty
    def last_popular(self):
        return self.__data['last_popular']

class UMDAlbum(ResolverMediaCollection):
    def __init__(self, data):
        ResolverMediaItem.__init__(self, types=['album'])
        self.__data = data

    @lazyProperty
    def source(self):
        return 'umdmusic'

    @lazyProperty
    def raw_name(self):
        return self.__data['name']

    def _cleanName(self, name):
        return name

    @lazyProperty
    def artists(self):
        return [{'name' : self.__data['artist']}]

    @lazyProperty
    def key(self):
        return '%s - %s' % (self.__data['name'], self.__data['artist'])

    @lazyProperty
    def last_popular(self):
        return self.__data['last_popular']


class UMDSource(DumbSource):
    def __init__(self):
        super(UMDSource, self).__init__(
                'umdmusic', groups=['artists', 'last_popular'], kinds=['media_item', 'media_collection'], types=['track', 'album'])

