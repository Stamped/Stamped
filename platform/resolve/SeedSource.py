#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SeedSource' ]

import Globals
from logs import report

try:
    from BasicSource    import BasicSource
    import logs
    import re
    from datetime       import datetime
    from libs.LibUtils           import months
    # from schema         import SchemaElement
except:
    report()
    raise


class SeedSource(BasicSource):
    """
    Seed data labeler
    """
    def __init__(self):
        BasicSource.__init__(self, 'seed')
        
        # TODO: reassess these seed groups
        self.__simple_groups = [
            # 'mpaa_rating',
            # 'artist_display_name',
            # 'tracks',
            # 'genre',
            # 'desc',
            # 'subtitle',
            # 'track_length',
            # 'cast',
            # 'short_description',
            # 'coordinates',
            # 'author',
            # 'publisher',
            # 'isbn',
            # 'release_date',
        ]
        for group in self.__simple_groups:
            self.addGroup(group)

    def enrichEntity(self, entity, controller, decorations, timestamps):
        for group in self.__simple_groups:
            try:
                source = "%s_source" % group
                cur = entity[source]
                value = entity[group]
                # if isinstance(value, SchemaElement):
                #     value = value.value
                if cur == None and value is not None and value != '' and value != {} and value != []:
                    timestamps[group] = controller.now
            except Exception as e:
                print e
        return True

