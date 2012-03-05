#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import keys.aws
    from LibUtils           import xmlToPython
    import bottlenose   
    import logs
except:
    report()
    raise


__all__      = [ "Amazon" ]
ASSOCIATE_ID = 'stamped01-20'

class Amazon(object):
    """
        Amazon API wrapper (2)
    """
    
    def __init__(self):
        self.amazon = bottlenose.Amazon(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY, ASSOCIATE_ID)
    
    def item_search(self, **kwargs):
        logs.info("Amazon API: ItemSearch %s" % kwargs)
        return self._item_helper(self.amazon.ItemSearch, **kwargs)
    
    def item_lookup(self, **kwargs):
        logs.info("Amazon API: ItemLookup %s" % kwargs)
        return self._item_helper(self.amazon.ItemLookup, **kwargs)
    
    def _item_helper(self, func, **kwargs):
        string = func(**kwargs)
        return xmlToPython(string)

_globalAmazon = Amazon()

def globalAmazon():
    return _globalAmazon

def main():
    api = Amazon()
    import sys
    import re
    import pprint

    method = 'search'
    
    args = {
    }
    if len(sys.argv) > 1:
        method = sys.argv[1]
        for pair in sys.argv[2:]:
            l = pair.split('=')
            args[l[0]] = l[1]
    
    if method == 'search' or method == "ItemSearch":
        pprint.pprint(api.item_search(**args))
    elif method == 'lookup' or method == 'ItemLookup':
        pprint.pprint(api.item_lookup(**args))
    else:
        print('Unknown method %s' % method)

if __name__ == '__main__':
    main()

