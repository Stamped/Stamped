#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import log, report

try:
    from libs.GooglePlacesSource        import GooglePlacesSource
    from libs.ExternalSourceController  import ExternalSourceController
    from AStampedAPITestCase            import *
    from Schemas                        import Entity
    from pprint                         import pformat
    from datetime                       import datetime
except:
    report()
    raise

_verbose = False

class APlacesSourceTest(AStampedAPITestCase):

    def setUp(self):
        self.source = GooglePlacesSource()
        self.controller = ExternalSourceController()
        self.entity = Entity()
        self.entity.title = 'Peter Luger Steak House'
        self.entity.lat = 40.709982
        self.entity.lng = -73.962501

    def tearDown(self):
        pass
    
    def recent(self,entity,field):
        timestamp = entity[field]
        if timestamp is None:
            return False
        else:
            age = datetime.utcnow() - timestamp
            return age.days == 0

class PlacesSourceEnrichTest(APlacesSourceTest):

    def test_luger_enrich(self):
        modified = self.source.enrichEntity(self.entity,self.controller)
        if _verbose:
            print(pformat(self.entity))
        self.assertEqual(modified,True)
        self.assertEqual(self.entity.address_country, 'US')
        self.assertEqual(self.entity.address_locality, 'Brooklyn')
        self.assertEqual(self.entity.address_postcode[:5], '11211')
        self.assertEqual(self.entity.address_region, 'NY')
        self.assertEqual(self.entity.address_street, '178 Broadway')
        self.assertEqual(self.entity.address_source, 'googleplaces')
        self.assertEqual(self.recent(self.entity,'address_timestamp'),True)

"""
class PlacesSourceEnrichTest(AFactualSourceTest):

    def test_ino_enrich(self):
        modified = self.source.resolveEntity(self.ino,self.controller)
        self.assertEqual(modified,True)
        self.assertEqual(self.entity.factual_id,'4333b825-8573-422c-89c5-26927e717dac')
        self.assertEqual(self.entity.factual_source,'factual')
        self.assertEqual(self.recent(self.ino,'factual_timestamp'),True)
        self.assertEqual(self.entity.singleplatform_id,'ino')
        self.assertEqual(self.entity.singleplatform_source,'factual')
        self.assertEqual(self.recent(self.ino,'singleplatform_timestamp'),True)
        modified = self.source.enrichEntity(self.ino,self.controller)
        self.assertEqual(modified,True)
        self.assertEqual(self.entity.address_country, 'US')
        self.assertEqual(self.entity.address_locality, 'New York')
        self.assertEqual(self.entity.address_postcode, '10014')
        self.assertEqual(self.entity.address_region, 'NY')
        self.assertEqual(self.entity.address_street, '21 Bedford St')
        self.assertEqual(self.entity.address_source, 'factual')
        self.assertEqual(self.recent(self.ino,'address_timestamp'),True)
"""
if __name__ == '__main__':
    _verbose = True
    main()

