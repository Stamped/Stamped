#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *
from api.MongoStampedAPI import MongoStampedAPI

# #### #
# USER #
# #### #

class StampedAPITest(AStampedAPITestCase):
    def setUp(self):
        self.stampedAPI = MongoStampedAPI(lite_mode=True)
    
    def tearDown(self):
        pass

class StampedAPIUserTest(StampedAPITest):
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

if __name__ == '__main__':
    main()

