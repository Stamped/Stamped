#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from resolve.FullResolveContainer   import FullResolveContainer
    from AStampedAPITestCase            import *
    from Schemas                        import Entity
    from pprint                         import pformat
    from datetime                       import datetime
except:
    report()
    raise

_verbose = False

_now = datetime.utcnow()

_cases = [
    (
        {
            "subcategory" : "restaurant",
            "title" : "Olives",
            "coordinates" : {
                "lat" : 40.736623,
                "lng" : -73.988658
            },
        },
        {'category': 'food',
         'coordinates': {'lat': 40.736623, 'lng': -73.988658},
         'details': {'contact': {'phone': u'(212) 353-8345',
                                 'phone_source': 'factual',
                                 'phone_timestamp': _now,
                                 'site': u'http://www.toddenglish.com/',
                                 'site_source': 'googleplaces',
                                 'site_timestamp': _now},
                     'place': {'address_country': u'US',
                               'address_locality': u'New York',
                               'address_postcode': u'10003',
                               'address_region': u'NY',
                               'address_source': 'factual',
                               'address_street': u'201 Park Ave S',
                               'address_timestamp': _now}},
         'sources': {'factual': {'factual_id': u'dde8bf50-d829-012e-561a-003048cad9da',
                                 'factual_source': 'factual',
                                 'factual_timestamp': _now},
                     'singleplatform': {'singleplatform_id': u'olives-18',
                                        'singleplatform_source': 'factual',
                                        'singleplatform_timestamp': _now}},
         'subcategory': 'restaurant',
         'title': 'Olives'},
    ),
    (
        {
            "subcategory" : "restaurant",
            "title" : "Peter Luger Steak House",
            "coordinates" : {
                "lat" : 40.709982,
                "lng" : -73.962501
            },
        },
        {'category': 'food',
         'coordinates': {'lat': 40.709982, 'lng': -73.962501},
         'details': {'contact': {'phone': u'(718) 387-7400',
                                 'phone_source': 'factual',
                                 'phone_timestamp': _now,
                                 'site': u'http://www.peterluger.com/',
                                 'site_source': 'factual',
                                 'site_timestamp': _now},
                     'place': {'address_country': u'US',
                               'address_locality': u'Brooklyn',
                               'address_postcode': u'11211',
                               'address_region': u'NY',
                               'address_source': 'factual',
                               'address_street': u'178 Broadway',
                               'address_timestamp': _now},
                     'restaurant': {'cuisine': u'Steak, American',
                                    'cuisine_source': 'factual',
                                    'cuisine_timestamp': _now,
                                    'price_range': 4,
                                    'price_range_source': 'factual',
                                    'price_range_timestamp': _now}},
         'sources': {'factual': {'factual_id': u'5af9664f-8307-4964-98b9-bce2a55c5c3f',
                                 'factual_source': 'factual',
                                 'factual_timestamp': _now},
                     'singleplatform': {'singleplatform_id': u'peter-luger-steakhouse-2',
                                        'singleplatform_source': 'factual',
                                        'singleplatform_timestamp': _now}},
         'subcategory': 'restaurant',
         'title': 'Peter Luger Steak House'}
    ),
]

class AResolveTest(AStampedAPITestCase):

    def setUp(self):
        self.container = FullResolveContainer()
        self.cases = []
        for case in _cases:
            before = Entity()
            before.importData(case[0])
            self.cases.append((before,case[1]))

    def tearDown(self):
        pass
    
    def compare(self, result, after):
        if type(after) is dict:
            for k,v in after.items():
                self.assertEqual(k in result, True, "%s not in %s should be %s" % (k, result, v) )
                if type(v) is dict:
                    self.compare( result[k] , v )
                else:
                    self.assertEqual( result[k] , v , "%s should be %s; is %s in %s" % (k, v, result[k], result) )
        else:
            self.assertEqual(result,after)

class ResolveCasesTest(AResolveTest):

    def test_cases_resolve(self):
        now = _now
        for before, after in self.cases:
            if _verbose:
                before_string = 'Before:\n%s' % (pformat(before.value),)
            modified = self.container.enrichEntity(before,{},timestamp=_now)
            if _verbose:
                print(before_string)
                print('After\n%s' % (pformat(before.value),))
            self.compare(before, after)

if __name__ == '__main__':
    _verbose = True
    main()

