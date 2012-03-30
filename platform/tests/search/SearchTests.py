#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from resolve.EntitySearch   import EntitySearch
from pprint                 import pprint
from copy                   import copy

"""
TODO:
    * add regression-oriented tests to search
        * run these tests regularly on prod via cron job
        * verify:
            * movies
                * movie in theaters (pull from fandango)
                * popular movie
                * really old movie
                * different language movie
            * tv
                * new / recent shows
                * upcoming shows
                * really popular shows
                * really old shows
                * different language show
            * tracks
                * itunes top chart lists
                * rdio / spotify top chart lists
                * track_name by artist_name
                * track_name artist_name
                * track_name album_name artist_name (and all permutations)
                * different language track
            * albums
                * itunes otp chart lists
                * album_name
                * album_name by artist_name
                * album_name artist_name (and vice-versa)
            * artist
                * search for artist alias / non-exact name
                    * (e.g., jayz, jay-z, and jay z should all work as expected)
                * search for track => artist in results
                * search for album => artist in results
                * international artist
            * app
                * app_name by company_name
                * app_name company_name (and vice-versa)
                * search for ipad-only app
            * restaurant
                * same permutations as place
                * new / recent restaurants from opentable
                * remote restaurants
                * search for generic chain (e.g., mcdonald's)
                * search for really unique name (e.g., absinthe)
            * place
                * search w/ and w/out coordinates
                * search w/ and w/out location hints
                * several international places
            * book
                * new / recent book
                * book_name
                * book_name by artist_name
                * book_name artist_name (and vice-versa)

"""

class ASearchTestSuite(AStampedTestCase):
    def setUp(self):
        self.searcher = EntitySearch()
    
    def tearDown(self):
        pass
    
    def _run_tests(self, tests, base_args):
        for test in tests:
            args = copy(base_args)
            
            for k, v in test[0].iteritems():
                assert k in args
                args[k] = v
            
            def validate(results):
                for constraint in test[1]:
                    if not constraint.validate(results):
                        raise Exception("search constraint failed (%s) (%s)" % (args, constraint))
            
            self.async(lambda: self.searcher.search(**args), validate)

class SearchResultConstraint(object):
    
    def __init__(self, 
                 title      = None, 
                 source     = None, 
                 id         = None, 
                 types      = None, 
                 index      = None, 
                 strict     = False, 
                 soft       = True, 
                 **extras   = None):
        
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
        self.extras = extras
    
    def _eq(self, a, b):
        a = str(a)
        b = str(b)
        
        if not self.strict:
            a = a.lower().strip()
            b = b.lower().strip()
        
        return a == b
    
    def validate(self, results):
        for i in xrange(len(results)):
            result = results[i]
            
            if self.title  is not None and not self._eq(self.title, result.title):
                continue
            
            if self.source is not None:
                source_id_key = "%s_id" % self.source
                
                if source_id_key not in result:
                    continue
                
                if self.id is not None and not self._eq(self.id, result[source_id_key]):
                    continue
            
            if self.types is not None:
                match = True
                for t in self.types:
                    if t not in result.types:
                        match = False
                        break
                
                if not match:
                    continue
            
            if self.extras is not None:
                match = True
                for key, value in self.extras.iteritems():
                    if key not in result or not self._eq(value, result[key]):
                        match = False
                        break
                
                if not match:
                    continue
            
            # constrainted result was matched
            if self.index is None or self.index == i or (self.index != -1 and self.soft):
                return True
            
            # match was not found at the desired index
            return False
        
        # specified result was not found; constraint is only satisfied if the 
        # expected index is invalid (e.g., constraint specifies that the result 
        # should not be found in the result set)
        return (self.index == -1)
    
    def __str__(self):
        options = { }
        if self.title is not None:  options['title']    = self.title
        if self.source is not None: options['source']   = self.source
        if self.id is not None:     options['id']       = self.id
        if self.types is not None:  options['types']    = self.types
        if self.index is not None:  options['index']    = self.index
        
        return "%s(%s)" % (self.__class__.__name__, str(options))

