#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ExternalSourceController' ]

import Globals
from logs import log, report

try:
    from ASourceController  import ASourceController
    from datetime           import datetime
    from datetime           import timedelta
except:
    report()
    raise

class ExternalSourceController(ASourceController):

    def __init__(self):
        ASourceController.__init__(self)
        self.__resolve = {
            'ages': {
            },
            'priorities': {
                'factual': ['factual','singleplatform'],
                'singleplatform': ['factual'],
                'tmdb':['tmdb'],
            },
            'timestamps': {
            },
            'sources': {
            }
        }
        self.__enrich = {
            'ages': {
            },
            'priorities': {
                'address':['factual','googleplaces'],
                'neighborhood':['googleplaces'],
                'phone':['factual','googleplaces'],
                'site':['factual','googleplaces'],
                'hours':['factual'],
                'price_range':['factual'],
                'cuisine':['factual'],
                'alcohol_flag':['factual'],
                'release_date':['cleaner'],
                'cast_list':['tmdb'],
            },
            'timestamps': {
            },
            'sources': {
            },
        }
        self.__decorate = {
            'ages': {
            },
            'priorities': {
                'menu':['singleplatform'],
            },
            'timestamps': {
            },
            'sources': {
            },
        }

    def shouldResolve(self, group, source, entity,timestamp=None):
        return self.genericShould(group, source, entity, timestamp, self.__resolve)
    
    def shouldEnrich(self, group, source, entity,timestamp=None):
        return self.genericShould(group, source, entity, timestamp, self.__enrich)

    def shouldDecorate(self, group, source, entity,timestamp=None):
        return self.genericShould(group, source, entity, timestamp, self.__decorate)

    def genericShould(self, group, source, entity, timestamp, state):
        if timestamp is None:
            timestamp = self.now()
        priorities = state['priorities']
        if group not in priorities:
            return False

        max_age = timedelta(30)
        timestamp_path = ["%s_timestamp" % group]
        sources = state['sources']
        source_path = ["%s_source" % group]

        ages = state['ages']
        sources = state['sources']
        ages = state['ages']
        timestamps = state['timestamps']
        if group in timestamps:
            timestamp_path = timestamps[group]
        if group in sources:
            source_path = sources[group]
        if group in ages:
            max_age = ages[group]

        if source in priorities[group]:
            old_source = self.__field(entity, source_path)
            delta = self.__compare(old_source, source, priorities[group])
            if delta > 0:
                return True
            elif delta < 0:
                return False
            else:
                old_timestamp = self.__field(entity, timestamp_path)
                return self.__stale(old_timestamp, timestamp, max_age)
        else:
            return False

    def __field(self, entity, path):
        cur = entity
        for k in path:
            if k in cur:
                cur = cur[k]
            else:
                return None
        return cur
    
    def __compare(self, old_source, new_source, priorities):
        if old_source is None:
            return 1000 #arbitrary largish positive number
        else:
            return priorities.index(old_source) - priorities.index(new_source)
    
    def __stale(self, old_timestamp, new_timestamp, max_age):
        if old_timestamp is None:
            return True
        else:
            return new_timestamp - old_timestamp > max_age
            
