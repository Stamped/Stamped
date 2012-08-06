#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from tests.framework.FixtureTest  import fixtureTest
from tests.search.SearchTestsRunner import SearchTestCase, SearchTestsRunner, main
from tests.search.SearchResultMatcher import *
from tests.search.SearchResultsScorer import *
from libs.applerss          import AppleRSS


def makeTestCase(query, *expected_results):
    return SearchTestCase('app', query, *expected_results)

Matcher = AppResultMatcher

class AppSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        """ Test basic app searches """

        # TODO: Incorporate iTunes IDs

        test_cases = (
            makeTestCase('stamped', Matcher(title=Equals('stamped'))), # 467924760
            makeTestCase('instagram', Matcher(title=Equals('instagram'))), # 389801252
            makeTestCase('doodle jump', Matcher(title=Equals('doodle jump'))), # 307727765
            makeTestCase('tiny wings', Matcher(title=Equals('tiny wings'))), # 417817520
            makeTestCase('flipboard', Matcher(title=StartsWith('flipboard'))), # 358801284
            makeTestCase('facebook app', Matcher(title=StartsWith('facebook'), unique=False)), # 284882215
            makeTestCase('facebook', Matcher(title=Equals('facebook'))), # 284882215
            makeTestCase('temple run', Matcher(title=Equals('temple run'))), # 420009108
            makeTestCase('pandora', Matcher(title=Equals('pandora radio'))) # 284035177
        )

        self._run_tests('static_app_tests', test_cases)

    def test_top_free_apps(self):
        rss  = AppleRSS()
        apps = rss.get_top_free_apps(limit=10)
        
        self.__test_apps('top_free_apps', apps)
    
    def test_top_paid_apps(self):
        rss  = AppleRSS()
        apps = rss.get_top_paid_apps(limit=10)
        
        self.__test_apps('top_paid_apps', apps)
    
    def test_top_grossing_apps(self):
        rss  = AppleRSS()
        apps = rss.get_top_grossing_apps(limit=10)
        
        self.__test_apps('top_grossing_apps', apps)
    
    def __test_apps(self, test_name, apps):
        test_cases = []
        
        for app in apps:
            name  = app.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            if name.lower() != name2:
                # don't test apps whose names contain weird unicode strings
                continue

            test_cases.append(makeTestCase(name, Matcher(title=Equals(name))))

        self._run_tests(test_name, test_cases)

if __name__ == '__main__':
    main()

