#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.match.AEntityMatcher           import AEntityMatcher
from crawler.match.PlacesEntityMatcher      import PlacesEntityMatcher
from crawler.match.FilmEntityMatcher        import FilmEntityMatcher
from crawler.match.BookEntityMatcher        import BookEntityMatcher
from crawler.match.MusicEntityMatcher       import MusicEntityMatcher

from crawler.match.TitleBasedEntityMatchers import *
from crawler.match.IDBasedEntityMatchers    import *

from utils import lazyProperty

__all__ = [
    "EntityMatcher", 
]

class EntityMatcher(AEntityMatcher):
    
    def __init__(self, stamped_api, options=None):
        AEntityMatcher.__init__(self, stamped_api, options)
    
    # --------------------------
    #          matchers
    # --------------------------
    
    @lazyProperty
    def _places_matcher(self):
        return PlacesEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _film_matcher(self):
        return FilmEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _book_matcher(self):
        return BookEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _music_matcher(self):
        return MusicEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _apple_matcher(self):
        return AppleEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _fandango_matcher(self):
        return FandangoEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _openTable_matcher(self):
        return OpenTableEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _googlePlaces_matcher(self):
        return GooglePlacesEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _amazon_matcher(self):
        return AmazonEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _factual_matcher(self):
        return FactualEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _thetvdb_matcher(self):
        return TheTVDBMatcher(self.stamped_api, self.options)
    
    # --------------------------
    #        proxy methods
    # --------------------------
    
    def getDuplicates(self, entity):
        matchers = self._get_matchers_for_entity(entity)
        dupes = []
        
        for matcher in matchers:
            candidates = list(matcher.getDuplicateCandidates(entity))
            cur_dupes  = list(matcher.getMatchingDuplicates(entity, candidates))
            
            dupes.extend(cur_dupes)
        
        def _get_id(e):
            return e.entity_id
        
        dupes  = sorted(dupes, key=_get_id)
        delete = []
        index  = 0
        
        # remove duplicate matches
        while index < len(dupes) - 1:
            if dupes[index].entity_id == dupes[index + 1].entity_id:
                dupes.pop(index)
            else:
                index += 1
        
        return dupes
    
    # --------------------------
    #        proxy mapping
    # --------------------------
    
    def _get_matchers_for_entity(self, entity):
        matchers = set()
        
        matcher_map = {
            'place'         : self._places_matcher, 
            'apple'         : self._apple_matcher, 
            'fandango'      : self._fandango_matcher, 
            'openTable'     : self._openTable_matcher, 
            'googlePlaces'  : self._googlePlaces_matcher, 
            'amazon'        : self._amazon_matcher, 
            'factual'       : self._factual_matcher, 
            'thetvdb'       : self._thetvdb_matcher, 
        }
        
        """
        if (not hasattr(self.options, 'merge')) or (not self.options.merge):
            if entity.category == 'food':
                matchers.add(self._places_matcher)
            elif entity.category == 'film':
                matchers.add(self._film_matcher)
            elif entity.category == 'book':
                matchers.add(self._book_matcher)
            elif entity.category == 'music':
                matchers.add(self._music_matcher)
        """
        
        for k, v in matcher_map.iteritems():
            if k in entity:
                matchers.add(v)
        
        if len(matchers) > 0:
            return list(matchers)
        
        print type(entity)
        from pprint import pprint
        pprint(entity)
        
        assert False

