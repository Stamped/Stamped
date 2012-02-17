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

class AFactualSourceTest(AStampedAPITestCase):

    def setUp(self):
        self.container = FullResolveContainer()
        self.ino = Entity()
        self.ino.title = 'Ino Cafe and Wine Bar'
        self.ino.lat = 40.72908
        self.ino.lng = -74.003697
        self.ino.subcategory = 'restaurant'

    def tearDown(self):
        pass
    
    def recent(self,entity,field):
        timestamp = entity[field]
        if timestamp is None:
            return False
        else:
            age = datetime.utcnow() - timestamp
            return age.days == 0

class FactualSourceEnrichTest(AFactualSourceTest):

    def test_ino_enrich(self):
        now = datetime.utcnow()
        modified = self.container.enrichEntity(self.ino,{},timestamp=now)
        if _verbose:
            print('\n%s\n' % (pformat(self.ino.value),))
        self.assertEqual(modified,True)
        self.assertEqual(self.ino.factual_id,'4333b825-8573-422c-89c5-26927e717dac')
        self.assertEqual(self.ino.factual_source,'factual')
        self.assertEqual(self.ino.factual_timestamp,now)
        self.assertEqual(self.ino.singleplatform_id,'ino')
        self.assertEqual(self.ino.singleplatform_source,'factual')
        self.assertEqual(self.ino.singleplatform_timestamp,now)
        self.assertEqual(self.ino.address_country, 'US')
        self.assertEqual(self.ino.address_locality, 'New York')
        self.assertEqual(self.ino.address_postcode, '10014')
        self.assertEqual(self.ino.address_region, 'NY')
        self.assertEqual(self.ino.address_street, '21 Bedford St')
        self.assertEqual(self.ino.address_source, 'factual')
        self.assertEqual(self.ino.price_range, 2)
        self.assertEqual(self.ino.address_timestamp,now)

if __name__ == '__main__':
    _verbose = True
    main()

