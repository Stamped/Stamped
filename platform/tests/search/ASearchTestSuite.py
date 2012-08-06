#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils           import *
from tests.search.SearchResultConstraints    import *
from search.EntitySearch        import EntitySearch
from resolve.Resolver           import simplify
from gevent.pool                import Pool
from pprint                     import pprint, pformat
from copy                       import copy
from abc                        import ABCMeta, abstractmethod

"""
TODO:
    * incorporate global web search signal into ranking via category or source_id hinting
    * incorporate global web search related terms into ranking algorithm
    * 
    * run these tests regularly on prod via cron job
    * verify:
        * movies
            * different language movie
        * tv
            * new / recent shows
            * upcoming shows
            * really popular shows
            * really old shows
            * different language show
        * tracks
            * rdio / spotify top chart lists
        * albums
        * artist
        * app
            * search for ipad-only app
        * place
            * search w/ and w/out coordinates
            * search w/ and w/out location hints
                * test invalid location hints (e.g., it's always sunny IN philadelphia)
            * several international places
        * restaurant
            * same permutations as place
            * new / recent restaurants from opentable
            * remote restaurants
            * search for generic chain (e.g., mcdonald's)
            * search for really unique name (e.g., absinthe)
        * book
            * new / recent book
            * book_name
            * book_name by artist_name
            * book_name artist_name (and vice-versa)
            * target NYTimes' or Amazon's RSS feed
    * target:
        * local search
        * search filters
        * offset and limit
"""

class ASearchTestSuite(AStampedTestCase):
    
    """
        Base class for all search-related test suites, providing the core _run_tests 
        method which is used extensively in all subclasses.
    """
    
    __metaclass__ = ABCMeta
    
    def setUp(self):
        self.searcher = EntitySearch()
    
    def tearDown(self):
        pass
    
    def _run_tests(self, tests, base_args, retries=3, delay=1, 
                   test_coords=False, test_unique=True, async=True):
        """
            Runs a list of search tests, verifying that each one satisfies its accompanying 
            SearchResultConstraint(s).
            
            tests       - list of tests, where each test is a tuple(dict, list(SearchResultConstraint))
            base_args   - dict containing base entity search parameters shared across all tests, all or 
                          some of which may override specific args.
            retries     - int denoting the number of times to retry a test case if one or more 
                          constraints fail before aborting.
            test_coords - boolean denoting whether or not to perform each test twice, once with coords 
                          enabled, and once without coords enabled (useful for verifying that certain 
                          searches really are coordinate agnostic).
            
            Example usage with a single test case (excerpt from MovieSearchTests subclass):
                args = {
                    'query'  : '', 
                    'coords' : None, 
                    'limit'  : 10, 
                }
                
                tests = [
                    # search for 'ninja turtles' and expect a movie entity of the same name 
                    # as the top result (e.g., at index 0)
                    ({ 'query' : 'ninja turtles', }, [ 
                        SearchResultConstraint(title='teenage mutant ninja turtles', 
                                               types='movie', 
                                               index=0), 
                    ]), 
                ]
                
                self._run_tests(tests, args)
        """
        
        async = False
        # optionally run test cases in parallel
        if async:
            pool = Pool(4)
        
        for test in tests:
            args = copy(base_args)
            
            for k, v in test[0].iteritems():
                args[k] = v
            
            assert 'query' in args
            def validate(results, args, constraints):
                if test_unique:
                    #constraints = copy(constraints)
                    #constraints.append(UniqueSearchResultConstraint())
                    #constraints = [ UniqueSearchResultConstraint() ]
                    pass
                
                # TODO: optionally test uniqueness / dedupping w.r.t. results via another SearchResultConstraint
                for constraint in constraints:
                    if not constraint.validate(results):
                        utils.log("")
                        utils.log("-" * 80)
                        utils.log("[%s] SEARCH ERROR query '%s'" % (self, args['query'], ))
                        for r in results:
                            utils.log(r)
                        utils.log("-" * 80)
                        utils.log("")
                        
                        raise Exception("search constraint failed (%s) (%s)" % (args, constraint))
            
            subtests = [ args ]
            
            # optionally run each test twice, once with coordinates enabled, and once with them 
            # disabled and expect the same constraints to be satisfied; note: test_coords should 
            # not be set to true for non-national place search tests, but all other search tests
            # should be agnostic to coords (e.g., movies, books, etc.)
            if test_coords:
                args2  = copy(args)
                coords = (40.736, -73.989)
                
                if 'coords' not in args2 or args2['coords'] is None:
                    args2['coords'] = coords
                else:
                    args2['coords'] = None
                
                subtests.append(args2)
            
            def __do_search(args, constraints):
                utils.log("")
                utils.log("-" * 80)
                utils.log("[%s] SEARCH TEST query '%s'" % (self, args['query'], ))
                utils.log("-" * 80)
                utils.log("")
                
                # perform the actual search itself, validating the results against all constraints 
                # specified by this test case, and retrying if necessary until either the test case 
                # satisfies its constraints or the maximum number of allotted retries is exceeded.
                fullArgs = copy(args)
                query = args.pop('query')
                category = args.pop('category')
                self.async(lambda: self.searcher.searchEntities(category, query, **args),
                           lambda r: validate(r, fullArgs, constraints),
                           retries=retries, 
                           delay=delay)
            
            for args in subtests:
                if async:
                    pool.spawn_link_exception(__do_search, args, test[1])
                else:
                    __do_search(args, test[1])
        
        if async:
            pool.join()
    
    def __str__(self):
        return self.__class__.__name__

