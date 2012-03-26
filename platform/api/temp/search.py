#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
from HTTPSchemas import *
from Schemas import *
from pprint import pprint

stampedAPI = MongoStampedAPI()

q = 'auction house'
# q = 'little owl'
coords = CoordinatesSchema({'lat': 37.781697, 'lng':-122.392146})   # SF
coords = CoordinatesSchema({'lat': 40.742273, 'lng':-74.007549})   # NYC
# coords = None

results = stampedAPI.searchEntitiesNew(q, coords=coords, category='food')

for i in range(len(results)):
    # pprint(results[i][0].value)
    entity = HTTPEntityAutosuggest().importSchema(results[i][0], results[i][1]).exportSparse()

    print '%2s. %s' % (i+1, entity['search_id'])
    print '    title:     %s' % entity['title']
    print '    subtitle:  %s' % entity['subtitle']
    print '    category:  %s' % entity['category']
    if 'distance' in entity:
        print '    distance:  %s' % entity['distance']

    # print '%2s. %s %10s %s' % (i+1, results[i].entity_id, results[i].subcategory, results[i].title)

    # pprint(entity)
    print 

# pprint(results[1][0].value)