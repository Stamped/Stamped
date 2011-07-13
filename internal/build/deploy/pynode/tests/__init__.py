#!/usr/bin/env python

import os, unittest
from pynode import *

class TestKitchen(unittest.TestCase):
    def setUp(self):
        self.kitchen = Kitchen()
        self.kitchen.addCookbookPath("pynode.cookbooks", os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookbooks"))
    
    def testUnknownConfig(self):
        self.failUnlessRaises(AttributeError, lambda:self.kitchen.config.test.config1)
    
    def testDefaultConfig(self):
        self.kitchen.includeRecipe("test")
        self.kitchen.run()
        
        self.failUnlessEqual("fu", self.kitchen.config.test.config1)
        self.failUnlessEqual("manchu", self.kitchen.config.test.config2)
        self.failUnlessEqual("manchu", self.kitchen._test)
    
    def testOverrideConfig(self):
        self.kitchen.updateConfig({"test.config1": "bar"})
        self.kitchen.includeRecipe("test")
        self.kitchen.run()
        
        self.failUnlessEqual("bar", self.kitchen.config.test.config1)
        self.failUnlessEqual("manchu", self.kitchen.config.test.config2)
        self.failUnlessEqual("manchu", self.kitchen._test)

if __name__ == '__main__':
    unittest.main()

