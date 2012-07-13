# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals

import logs, re
from resolve.GenericSource import GenericSource
from utils import lazyProperty
from resolve.Resolver import *
from resolve.ResolverObject import *

class DumbMediaItem(ResolverMediaItem):
    def __init__(self, sourceName, key):
        ResolverMediaItem.__init__(self, types=[])
        self.__sourceName = sourceName
        self.__key = key

    @lazyProperty
    def source(self):
        return self.__sourceName

    @lazyProperty
    def raw_name(self):
        return None

    def _cleanName(self, name):
        return name

    @lazyProperty
    def key(self):
        return self.__key

class DumbSource(GenericSource):
    def __init__(self, sourceName, *args, **kwargs):
        GenericSource.__init__(self, sourceName, *args, **kwargs)
        self.__sourceName = sourceName

    def entityProxyFromKey(self, key, **kwargs):
        return DumbMediaItem(self.__sourceName, key)

    def matchSource(self, query):
        return lambda start, end: []
