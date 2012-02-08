#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import libs.ec2_utils, os

from AStampedAPITestCase    import *
from api.MongoStampedAPI    import MongoStampedAPI
from api.HTTPSchemas        import *
from api.Schemas            import *

# #### #
# USER #
# #### #

class StampedAPITest(AStampedAPITestCase):
    def setUp(self):
        self.stampedAPI = MongoStampedAPI(lite_mode=True)
    
    def tearDown(self):
        pass

class StampedAPIUserTests(StampedAPITest):
    def test_user_regex(self):
        tests = {
            '@test'                  : [ 'test', ], 
            ' @ test'                : [], 
            ' @ @@ @favre @@'        : [ 'favre', ], 
            '@testa @testb'          : [ 'testa', 'testb' ], 
            '@0'                     : [ '0', ], 
            'abc\n@travis\n@bc'      : [ 'travis', 'bc' ], 
            '@ab\ncd'                : [ 'ab', ], 
            '@@'                     : [], 
            '@1234567890123456789'   : [ '1234567890123456789', ], 
            '@123456789012345678901' : [], # invalid; too long
            '@ab_cd a@ef @gh'        : [ 'ab_cd', 'gh', ], 
            '@ab123cd'               : [ 'ab123cd', ], 
            'devbot@stamped.com'     : [], # invalid: email address
            'Here.@you.'             : ['you', ],
            'Well--@you--why w..'    : ['you', ],
        }
        
        for test in tests:
            expected = tests[test]
            groups   = self.stampedAPI._user_regex.findall(test)
            
            #print expected, groups
            self.assertLength(groups, len(expected))
            
            for i in xrange(len(groups)):
                self.assertEqual(expected[i], groups[i])

class StampedAPIStampTests(StampedAPITest):
    
    def setUp(self):
        StampedAPITest.setUp(self)
        
        self._run = not libs.ec2_utils.is_prod_stack()
        
        if self._run:
            self._loadCollection("stamps")
            
            self._params = {
                'authUserId'    : "4e57048dccc2175fca000005", # travis
                'stampIds'      : [ # a specific subset of travis' stamps
                    "4e99f0a0fe4a1d44dd00036d", 
                    "4e7ab4cfd6970356a20009f7", 
                    "4e94927e967ed374ea000000", 
                    "4ebd8f0c6d520b781c00002d", 
                    "4e756a94d697034427000027", 
                    "4ec45e0b6d520b0db2000d62", 
                    "4e9626cefe4a1d22d60001bf", 
                    "4e6e6f244b752051d6000000", 
                    "4e812b6dd6970356a20019be", 
                    "4ec9e06e3408337fd4000036", 
                    "4e792a21d6970356a40000eb", 
                    "4e84ef6cd35f7336fc000055", 
                    "4e961f3cfe4a1d22d50000f4", 
                    "4e964685fe4a1d22d3000121", 
                    "4e9698c9fe4a1d22d6000419", 
                    "4e990f5cfe4a1d44dd0001bd", 
                    "4e9c8645fe4a1d77bb000006", 
                    "4e9c884efe4a1d77bb000010", 
                    "4e9c894bfe4a1d77bc000008", 
                    "4e9c8a0cfe4a1d77bd00000f", 
                    "4ea989ccfe4a1d2a410007ba", 
                    "4ec9b80bfc905f7fa4000001", 
                    "4ee05d9054533e78810000d3", 
                    "4eaa32e2fe4a1d2a42000a40", 
                    "4eaba043fe4a1d2a43001293", 
                    "4ecc2e7e56f8685164000492", 
                    "4eb4b6df1f2adc74c200019c", 
                    "4ed8781fe8ef217b5b001291", 
                    "4ecacd78e4146a12d300024e", 
                    "4ecaef4e4820c5024c000b7d", 
                    "4ed70a56fc905f717e000b06", 
                    "4ee1b9e254533e7daa0001e3", 
                    "4f0cef5c54533e437b0002b1", 
                    "4ee3b1726e33433bdd00026b", 
                    "4ed50b9d340833159b000004", 
                    "4f054a136e334369240001fd", 
                ], 
                'enrich'        : False, 
            }
    
    def tearDown(self):
        StampedAPITest.tearDown(self)
        
        if self._run:
            self._dropCollection("stamps")
    
    def _getStamps(self, httpGenericSlice):
        self._params['genericSlice'] = httpGenericSlice.exportSchema(GenericSlice())
        
        ret = self.stampedAPI._getStampCollection(**self._params)
        self.assertIsInstance(ret, list)
        
        return ret
    
    def _assertStampsEqual(self, s0, s1):
        self.assertEqual(s0["stamp_id"],            s1["stamp_id"])
        self.assertEqual(s0["blurb"],               s1["blurb"])
        self.assertEqual(s0["user"]["user_id"],     s1["user"]["user_id"])
        self.assertEqual(s0["entity"]["title"],     s1["entity"]["title"])
        self.assertEqual(s0["entity"]["entity_id"], s1["entity"]["entity_id"])
    
    def _test_reverse(self, genericSlice, results0):
        genericSlice.reverse    = True
        
        results1 = self._getStamps(genericSlice)
        self.assertEqual(len(results0), len(results1))
        
        # test reverse to ensure stamps are exactly mirrored
        for i in xrange(len(results0)):
            s0 = results0[i]
            s1 = results1[len(results1) - (i + 1)]
            
            self._assertStampsEqual(s0, s1)
    
    def test_slicing_coverage(self):
        # test strictly for coverage with a bunch of different parameter 
        # permutations to try and hit as many code paths as possible, 
        # not checking the correctness of results at all here.
        if not self._run:
            return
        
        genericSlice            = HTTPGenericSlice()
        
        genericSlice.limit      = 10
        ret = self._getStamps(genericSlice)
        self.assertTrue(len(ret) <= 10)
        
        genericSlice.offset     = 10
        ret = self._getStamps(genericSlice)
        self.assertTrue(len(ret) <= 10)
        
        genericSlice.subcategory = "restaurant"
        ret = self._getStamps(genericSlice)
        
        genericSlice.subcategory = None
        genericSlice.query      = "speakeasy"
        genericSlice.sort       = "relevance"
        ret = self._getStamps(genericSlice)
        
        genericSlice.category   = "food"
        ret = self._getStamps(genericSlice)
        
        genericSlice.category   = None
        genericSlice.query      = None
        genericSlice.sort       = "alphabetical"
        genericSlice.reverse    = True
        ret = self._getStamps(genericSlice)
        
        genericSlice.sort       = "created"
        genericSlice.reverse    = False
        ret = self._getStamps(genericSlice)
        
        genericSlice.sort       = "proximity"
        genericSlice.center     = "44,-80"
        ret = self._getStamps(genericSlice)
        
        genericSlice.sort       = "popularity"
        genericSlice.center     = None
        ret = self._getStamps(genericSlice)
        
        genericSlice.sort       = "relevance"
        genericSlice.viewport   = "44,-80,40,-70"
        ret = self._getStamps(genericSlice)
        
        genericSlice.sort       = "relevance"
        genericSlice.query      = "tacos"
        genericSlice.viewport   = "44,-80,40,-70"
        ret = self._getStamps(genericSlice)
        
        genericSlice.since      = 1000
        genericSlice.before     = 100000000
        genericSlice.viewport   = None
        ret = self._getStamps(genericSlice)
    
    def test_relevance_sort(self):
        genericSlice            = HTTPGenericSlice()
        genericSlice.sort       = "relevance"
        genericSlice.query      = "aWeSoMe" # test case insensitivity
        genericSlice.offset     = 0
        genericSlice.limit      = 10
        
        ret0 = self._getStamps(genericSlice)
        self.assertLength(ret0, 5)
        
        genericSlice.offset     = 2
        genericSlice.limit      = len(ret0) - genericSlice.offset + 1
        
        ret1 = self._getStamps(genericSlice)
        self.assertLength(ret1, len(ret0) - genericSlice.offset)
        
        # ensure overlapping stamps across slice match up
        for i in xrange(genericSlice.offset, len(ret0)):
            s0 = ret0[i]
            s1 = ret1[i - genericSlice.offset]
            
            self._assertStampsEqual(s0, s1)
        
        # test reverse
        genericSlice.offset     = 0
        genericSlice.limit      = 10
        
        self._test_reverse(genericSlice, ret0)
    
    def test_popularity_sort(self):
        genericSlice            = HTTPGenericSlice()
        genericSlice.sort       = "popularity"
        genericSlice.offset     = 0
        genericSlice.limit      = 50
        expected_len            = min(len(self._params["stampIds"]), genericSlice.limit)
        
        ret0 = self._getStamps(genericSlice)
        self.assertLength(ret0, expected_len)
        
        self.assertTrue(ret0[0].stats.num_credit   >= ret0[-1].stats.num_credit)
        self.assertTrue(ret0[0].stats.num_likes    >= ret0[-1].stats.num_likes)
        self.assertTrue(ret0[0].stats.num_comments >= ret0[-1].stats.num_comments)
        
        self._test_reverse(genericSlice, ret0)
    
    def test_proximity_sort(self):
        genericSlice            = HTTPGenericSlice()
        center                  = (40.73, -73.99) # ~NYC
        genericSlice.sort       = "proximity"
        genericSlice.offset     = 0
        genericSlice.limit      = 10
        genericSlice.center     = "%s,%s" % (center[0], center[1])
        
        ret0 = self._getStamps(genericSlice)
        self.assertLength(ret0, 9)
        
        earthRadius = 3959.0 # miles
        prev_dist   = -earthRadius
        
        # ensure results are approximately sorted by distance
        for s in ret0:
            coords = (s.entity.coordinates.lat, s.entity.coordinates.lng)
            dist   = utils.get_spherical_distance(center, coords) * earthRadius
            
            # allow a one-mile fudge factor because we're using spherical 
            # distance here, and the distance calculation when sorting 
            # results is less precise but faster to calculate (L2 norm)
            self.assertTrue(dist >= prev_dist - 1)
            prev_dist = dist
        
        # test reverse
        self._test_reverse(genericSlice, ret0)
    
    def test_alphabetical_sort(self):
        genericSlice            = HTTPGenericSlice()
        genericSlice.sort       = "alphabetical"
        genericSlice.offset     = 0
        genericSlice.limit      = 50
        expected_len            = min(len(self._params["stampIds"]), genericSlice.limit)
        
        ret0 = self._getStamps(genericSlice)
        self.assertLength(ret0, expected_len)
        
        prev_title = None
        
        # ensure results are approximately sorted by entity title
        for s in ret0:
            title = s.entity.title.lower()
            
            if prev_title is not None:
                self.assertTrue(title >= prev_title)
            
            prev_title = title
        
        self._test_reverse(genericSlice, ret0)
    
    def test_viewport_filter(self):
        genericSlice            = HTTPGenericSlice()
        viewport                = (40.8, -74.05, 40.5, -73.5) # ~NYC
        genericSlice.sort       = "modified"
        genericSlice.offset     = 0
        genericSlice.limit      = 10
        genericSlice.viewport   = ",".join(map(str, viewport))
        
        ret0 = self._getStamps(genericSlice)
        self.assertLength(ret0, 4)
        
        # ensure all results fall within the desired viewport
        # NOTE: this simple viewport check would fail if the viewport crossed 
        # the -180 / 180 longitude border, but this test is purposefully 
        # centered around NYC to avoid this pitfall.
        for s in ret0:
            self.assertTrue(s.lat <= viewport[0] and s.lat >= viewport[2])
            self.assertTrue(s.lng >= viewport[1] and s.lng <= viewport[3])
        
        # test reverse
        self._test_reverse(genericSlice, ret0)
    
    def test_invalid_params(self):
        genericSlice            = HTTPGenericSlice()
        genericSlice.sort       = "popularity"
        genericSlice.query      = "noop"
        
        # ensure that we can't include a search query for non-relevance-based sorts
        with expected_exception():
            self._getStamps(genericSlice)
        
        genericSlice.sort       = "alphabetical"
        with expected_exception():
            self._getStamps(genericSlice)
        
        genericSlice.sort       = "created"
        with expected_exception():
            self._getStamps(genericSlice)
        
        genericSlice.sort       = "modified"
        with expected_exception():
            self._getStamps(genericSlice)
        
        genericSlice.sort       = "proximity"
        genericSlice.query      = None
        
        # ensure that we must have a center point for proximity sort
        with expected_exception():
            self._getStamps(genericSlice)
        
        # reset to a valid state
        genericSlice.sort       = "created"
        self._getStamps(genericSlice)
        
        invalid_centers = [
            "30;40.2", 
            ",", 
            "", 
            " ", 
            "30a, 40", 
            "ab,cd", 
            "-20+2,43", 
        ]
        
        # ensure that we catch improperly formatted center points
        for center in invalid_centers:
            genericSlice.center = center
            
            with expected_exception():
                self._getStamps(genericSlice)
        
        # reset to a valid state
        genericSlice.center     = None
        self._getStamps(genericSlice)
        
        invalid_viewports = [
            "30,40.2,,20", 
            "40,-80,43,-", 
            "40,-80;43,-78", 
            "40,,43,-78", 
            ",,,", 
            " , , , ", 
            "", 
            " ", 
            "a,b,c,d", 
            ",-200,200,200", 
        ]
        
        # ensure that we catch improperly formatted viewports
        for viewport in invalid_viewports:
            genericSlice.viewport   = viewport
            
            with expected_exception():
                self._getStamps(genericSlice)
        
        # reset to a valid state
        genericSlice.viewport   = None
        self._getStamps(genericSlice)
        
        invalid_timestamps = [
            "a", 
            "datetime.datetime(1969, 12, 31, 23, 59, 30)", 
            "30:40:57", 
            "30.32", 
            "-30.32l", 
            "ab:12:23", 
            "", 
            " ", 
            "9999999999999999999999999999999", 
        ]
        
        # ensure that we must catch invalid since / before parameters
        for timestamp in invalid_timestamps:
            # test since parameter alone
            with expected_exception():
                genericSlice.since = timestamp
                self._getStamps(genericSlice)
            
            # reset to a valid state
            genericSlice.since  = None
            self._getStamps(genericSlice)
            
            # test before parameter alone
            with expected_exception():
                genericSlice.before = timestamp
                self._getStamps(genericSlice)
            
            # reset to a valid state
            genericSlice.before = None
            self._getStamps(genericSlice)
            
            # test both before and since parameters
            with expected_exception():
                genericSlice.before = timestamp
                genericSlice.since  = timestamp
                
                self._getStamps(genericSlice)

if __name__ == '__main__':
    main()

