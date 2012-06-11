#!/usr/bin/env python

"""
    # DEPRECATED (travis)
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from datetime       import datetime
from datetime       import timedelta
from functools      import partial

class SourceController(object):

    def __init__(self):
        self.__max_ages = {
            'address': timedelta(60),
        }
        self.__priorities = {
            'address': ['factual','googleplaces']
        }
        self.__tests = {
            'address':partial(self.__simple_test,'address'),
        }

    def writeTo(self, group, source, entity):
        if group in self.__tests:
            test = self.__tests[group]
            return test(entity,source)
        else:
            return False
    
    def __simple_test(self, group, source, entity):
        if 'address_source' not in entity or 'address_timestamp' not in entity:
            return True
        else:
            cur_source = entity.address_source
            cur_timestamp = entity.address_timestamp
            age = datetime.utcnow() - cur_timestamp
            if age > self.__max_ages[group]:
                return True
            else:
                priority = self.__priorities[group]
                if source not in priority:
                    return True
                if cur_source not in priority:
                    return True
                result = priority.index(cur_source) > priority.index(source)
                return result

if __name__ == '__main__':
    pass

