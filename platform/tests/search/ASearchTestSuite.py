#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from resolve.EntitySearch   import EntitySearch
from resolve.Resolver       import simplify
from pprint                 import pprint, pformat
from copy                   import copy

"""
TODO:
    * make test_unique_results into a separate SearchResultConstraint
    * add regression-oriented tests to search
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
            * video games
"""

class ASearchTestSuite(AStampedTestCase):
    
    """
        Base class for all search-related test suites, providing the core _run_tests 
        method which is used extensively in all subclasses.
    """
    
    def setUp(self):
        self.searcher = EntitySearch()
    
    def tearDown(self):
        pass
    
    def _run_tests(self, tests, base_args, retries=3, test_coords=True):
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
        """
        
        for test in tests:
            args = copy(base_args)
            
            for k, v in test[0].iteritems():
                args[k] = v
            
            assert 'query' in args
            def validate(results):
                # TODO: optionally test uniqueness / dedupping w.r.t. results via another SearchResultConstraint
                
                for constraint in test[1]:
                    if not constraint.validate(results):
                        raise Exception("search constraint failed (%s) (%s)" % (args, constraint))
            
            todo = [ args ]
            
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
                
                todo.append(args2)
            
            for args in todo:
                utils.log("")
                utils.log("-" * 80)
                utils.log("[%s] SEARCH TEST query '%s'" % (self, args['query'], ))
                utils.log("-" * 80)
                utils.log("")
                
                # perform the actual search itself, validating the results against all constraints 
                # specified by this test case, and retrying if necessary until either the test case 
                # satisfies its constraints or the maximum number of allotted retries is exceeded.
                self.async(lambda: self.searcher.searchEntities(**args), validate, retries=retries)
    
    def __str__(self):
        return self.__class__.__name__

class SearchResultConstraint(object):
    
    """
        Represents a single constraint with respect to entity search results, 
        providing the ability to verify that the constraint is satisfied via 
        the validate function.
    """
    
    def __init__(self, 
                 title      = None, 
                 source     = None, 
                 id         = None, 
                 types      = None, 
                 index      = None, 
                 strict     = False, 
                 match      = None, 
                 **extras):
        
        if types is not None and not isinstance(types, set):
            if isinstance(types, (tuple, list)):
                types = set(types)
            else:
                types = set([ types ])
        
        self.title  = title
        self.source = source
        self.id     = id
        self.types  = types
        self.index  = index
        self.strict = strict
        self.match  = match
        self.extras = extras
    
    def validate(self, results):
        """
            Validates this constraint against the given search results, verifying 
            one or more of the following:
                * a specific result exists
                * a specific result exists at the desired index in the results
                * a specific result does *not* exist in the results
            
            Returns True iff the constraint was satisfied or False otherwise.
        """
        
        for i in xrange(len(results)):
            result = results[i]
            valid  = (self.index is None or self.index == i)
            
            if valid:
                t0 = list(self.types)
                t1 = list(map(lambda t: t.value, result.types))
                
                if len(t0) == 1: t0 = t0[0]
                if len(t1) == 1: t1 = t1[0]
                
                utils.log("VALIDATE %s/%s) %s vs %s (%s vs %s)" % 
                          (i, self.index, self.title, result.title, t0, t1))
                utils.log(pformat(utils.normalize(result.value, strict=True)))
            
            # optionally verify the validity of this result's title
            if self.title  is not None and not self._eq(self.title, result.title):
                continue
            
            # optionally verify the origin of this result and/or it's source_id
            if self.source is not None:
                source_id_key = "%s_id" % self.source
                
                if source_id_key not in result:
                    continue
                
                if self.id is not None and not self._eq(self.id, result[source_id_key]):
                    continue
            
            # optionally ensure the validity of this result's type
            if self.types is not None:
                match = False
                for t in self.types:
                    for t2 in result.types:
                        try:
                            t2 = t2.value
                        except Exception:
                            pass
                        
                        if self._eq(t, t2):
                            match = True
                            break
                    
                    if not match:
                        break
                
                if not match:
                    continue
            
            # optionally ensure the validity of other misc entity attributes
            if self.extras is not None:
                match = True
                for key, value in self.extras.iteritems():
                    if key not in result or not self._eq(value, result[key]):
                        match = False
                        break
                
                if not match:
                    continue
            
            # constrainted result was matched
            if valid:
                return True
            
            if self.index != -1:
                # match was not found at the desired index
                return False
        
        # specified result was not found; constraint is only satisfied if the 
        # expected index is invalid (e.g., constraint specifies that the result 
        # should not be found in the result set)
        return (self.index == -1)
    
    def _eq(self, a, b):
        """ Returns whether or not a fuzzily matches b """
        
        a = unicode(a)
        b = unicode(b)
        
        if not self.strict:
            a = simplify(a)
            b = simplify(b)
            
            if len(a) > len(b):
                a, b = b, a
            
            if self.match == 'prefix':
                return b.startswith(a)
            
            if self.match == 'contains':
                return a in b
        
        return a == b
    
    def __str__(self):
        options = { }
        
        if self.title is not None:  options['title']    = self.title
        if self.source is not None: options['source']   = self.source
        if self.id is not None:     options['id']       = self.id
        if self.types is not None:  options['types']    = self.types
        if self.index is not None:  options['index']    = self.index
        
        return "%s(%s)" % (self.__class__.__name__, str(options))

