#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import log, report

try:
    from libs.FactualSource				import FactualSource
    from libs.ExternalSourceController 	import ExternalSourceController
    from tests.AStampedAPIHttpTestCase 			import *
    from api.Schemas					import Entity
    from pprint							import pformat
    from datetime                       import datetime
except:
    report()
    raise

_verbose = False

class AFactualSourceHttpTest(AStampedAPIHttpTestCase):

    def setUp(self):
        self.source = FactualSource()
        self.controller = ExternalSourceController()
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

class FactualSourceResolveTest(AFactualSourceHttpTest):

    def test_ino_resolve(self):
        modified = self.source.resolveEntity(self.ino,self.controller)
        if _verbose:
            print('\n%s\n' % (pformat(self.ino),))
        self.assertEqual(modified,True)
        self.assertEqual(self.ino.factual_id,'4333b825-8573-422c-89c5-26927e717dac')
        self.assertEqual(self.ino.factual_source,'factual')
        self.assertEqual(self.recent(self.ino,'factual_timestamp'),True)
        self.assertEqual(self.ino.singleplatform_id,'ino')
        self.assertEqual(self.ino.singleplatform_source,'factual')
        self.assertEqual(self.recent(self.ino,'singleplatform_timestamp'),True)

class FactualSourceEnrichFailTest(AFactualSourceHttpTest):

    def test_enrich_fails(self):
        modified = self.source.enrichEntity(self.ino,self.controller)
        self.assertEqual(modified,False)

class FactualSourceEnrichTest(AFactualSourceHttpTest):

    def test_ino_enrich(self):
        self.controller.clearNow()
        now = self.controller.now()
        modified = self.source.resolveEntity(self.ino,self.controller)
        self.assertEqual(modified,True)
        self.assertEqual(self.ino.factual_id,'4333b825-8573-422c-89c5-26927e717dac')
        self.assertEqual(self.ino.factual_source,'factual')
        self.assertEqual(self.ino.factual_timestamp,now)
        self.assertEqual(self.ino.singleplatform_id,'ino')
        self.assertEqual(self.ino.singleplatform_source,'factual')
        self.assertEqual(self.ino.singleplatform_timestamp,now)
        modified = self.source.enrichEntity(self.ino,self.controller)
        if _verbose:
            print('\n%s\n' % (pformat(self.ino),))
        self.assertEqual(modified,True)
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

