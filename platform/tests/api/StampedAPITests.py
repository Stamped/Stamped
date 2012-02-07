#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

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
    def test_slicing_coverage(self):
        genericSlice = HTTPGenericSlice()
        
        params = {
            'authUserId'    : "4e57048accc2175fcd000001", 
            'stampIds'      : [ "4e570576ccc2175fcc000001", 
                                "4e57058eccc2175fca000009", 
                                "4e570610ccc2175fcb000003", ], 
            'enrich'        : False, 
        }
        
        def getStamps():
            params['genericSlice'] = genericSlice.exportSchema(GenericSlice())
            ret = self.stampedAPI._getStampCollection(**params)
            self.assertIsInstance(ret, list)
            return ret
        
        genericSlice.limit = 10
        ret = getStamps()
        self.assertTrue(len(ret) <= 10)
        
        genericSlice.offset = 10
        ret = getStamps()
        self.assertTrue(len(ret) <= 10)
        
        genericSlice.query = "pizza"
        ret = getStamps()
        
        genericSlice.query = "speakeasy"
        genericSlice.sort  = "relevance"
        ret = getStamps()
        
        genericSlice.category = "food"
        ret = getStamps()
        
        genericSlice.category = None
        genericSlice.query    = None
        genericSlice.sort     = "alphabetical"
        genericSlice.reverse  = True
        ret = getStamps()
        
        genericSlice.sort     = "created"
        genericSlice.reverse  = False
        ret = getStamps()
        
        genericSlice.sort     = "proximity"
        genericSlice.center   = "44,-80"
        ret = getStamps()
        
        genericSlice.sort     = "popularity"
        genericSlice.center   = None
        ret = self.stampedAPI._getStampCollection(**params)
        
        genericSlice.sort     = "relevance"
        genericSlice.viewport = "44,-80,40,-70"
        ret = getStamps()
        
        genericSlice.sort     = "relevance"
        genericSlice.query    = "tacos"
        genericSlice.viewport = "44,-80,40,-70"
        ret = getStamps()
        
        genericSlice.since    = 1000
        genericSlice.before   = 100000000
        genericSlice.viewport = None
        ret = getStamps()

if __name__ == '__main__':
    main()

