#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, time, types, utils
import sys

if sys.version_info[0] == 2 and sys.version_info[1] > 6:
    import unittest2 as unittest
else:
    import unittest

from pprint import pprint

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
    
    def async(self, func, assertions, retries=5, delay=0.5):
        if not isinstance(assertions, (list, tuple)):
            assertions = [ assertions ]
        
        result = None
        
        while True:
            error = None
            
            try:
                result = func()
                # print '\n\nRESULTS\n'
                # for i in result:
                #     print '%s\n' % ('='*40)
                #     pprint (i)
                #     print ''
                # print '%s\n' % ('='*40)
                
                for assertion in assertions:
                    assertion(result)
                
                break
            except SyntaxError:
                raise
            except Exception, e:
                error = e
            
            retries -= 1
            if retries < 0:
                if result is not None:
                    pprint(result)
                raise
            
            utils.log("")
            utils.log("[%s] error '%s' (%d more retries)" % (self, str(error), retries))
            
            time.sleep(delay)
            delay *= 2
    
    def __str__(self):
        return self.__class__.__name__

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

class expected_exception:
    def __init__(self, e=Exception):
        if isinstance(e, Exception):
            self._t, self._v = e.__class__, str(e)
        elif isinstance(e, type) and issubclass(e, Exception):
            self._t, self._v = e, None
        else:
            raise Exception("usage: with expected(Exception): or with expected(Exception(\"text\"))")
        
    def __enter__(self):
        import sys
        sys.exc_clear()
    
    def __exit__(self, t, v, tb):
        assert t is not None, "expected %s to have been thrown" % self._t.__name__
        
        return issubclass(t, self._t) and (self._v is None or str(v).startswith(self._v))

