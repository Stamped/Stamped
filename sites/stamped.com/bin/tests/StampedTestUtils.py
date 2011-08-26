#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import os, types, unittest

class AStampedTestCase(unittest.TestCase):
    """
        Abstract base class for all Stamped unit test cases defined herein.
    """
    
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
    
    def assertIn(self, a, b):
        self.assertTrue(a in b)
    
    def assertLength(self, a, size):
        self.assertEqual(len(a), size)

class StampedTestRunner(object):
    """
        Class which facilitates finding and running test cases defined in one 
        or more modules (by following module imports).
    """
    
    def __init__(self, module=None, **kwargs):
        self._loader = unittest.TestLoader()
        self._suite  = unittest.TestSuite()
        
        self._verbosity = kwargs.pop('verbosity', 2)
        self.addModule(module)
    
    def addModule(self, module, seen=None):
        """
            Recursively searches the given module for imported test cases / 
            suites, adding any which are found to this runner.
        """
        
        if module is None:
            return seen
        
        if seen is None:
            seen = set()
        else:
            seen.add(module)
        
        if isinstance(module, types.ModuleType):
            suite = self._loader.loadTestsFromModule(module)
            if suite.countTestCases() > 0 and hasattr(module, '__name__'):
                print "adding tests from '%s'" % module.__name__
                self._suite.addTests(suite)
            
            path = self._getPath(module)
            
            for v in module.__dict__.itervalues():
                if isinstance(v, types.ModuleType) and \
                    v not in seen and \
                    hasattr(v, '__file__') and \
                    self._getPath(v).startswith(path):
                    seen = self.addModule(v, seen)
        
        return seen
    
    def addModules(self, modules):
        """
            Recursively searches the given modules for imported test cases / 
            suites, adding any which are found to this runner.
        """
        
        if modules is None:
            return
        
        for module in modules:
            self.addModule(module)
    
    def addTest(self, test):
        """
            Adds the given test to this runner (test case or suite).
        """
        
        self._suite.addTest(test)
    
    def addTests(self, tests):
        """
            Adds the given tests to this runner (test cases or suites).
        """
        
        self._suite.addTests(tests)
    
    def run(self):
        """ 
            Invokes all tests this runner knows about or the default unittest 
            main to discover other tests if this runner is empty.
        """
        
        count  = self._suite.countTestCases()
        runner = unittest.TextTestRunner(verbosity=self._verbosity)
        
        if 0 == count:
            unittest.main(testRunner=runner)
        else:
            print
            print "----------------------------------------------------------------------"
            runner.run(self._suite)
    
    def _getPath(self, module):
        assert isinstance(module, types.ModuleType)
        assert hasattr(module, '__file__')
        
        return os.path.dirname(os.path.abspath(module.__file__))

