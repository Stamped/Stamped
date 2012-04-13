#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import Entity

from utils                      import lazyProperty
from collections                import defaultdict

from libs.GooglePlaces          import GooglePlaces
from libs.applerss              import AppleRSS
from libs.Fandango              import Fandango
from libs.LRUCache              import lru_cache
from libs.Memcache              import memcached_function

from ASuggestedEntities         import ASuggestedEntities
from MongoCollectionCollection  import MongoCollectionCollection
from MongoEntityCollection      import MongoEntityCollection
from MongoStampCollection       import MongoStampCollection

class MongoSuggestedEntities(ASuggestedEntities):
    
    def getSuggestedEntities(self, userId=None, coords=None, category=None, subcategory=None, limit=None):
        if category is not None:
            category = category.lower().strip()
        if subcategory is not None:
            subcategory = subcategory.lower().strip()
        
        if category is None and subcategory is None:
            raise NotImplementedError
            categories = [
                ('place', 'Nearby places'), 
                ('music', 'Music'), 
                ('book', 'Books'),
            ]
            
            subcategories = [
                ('tv', 'TV Shows'), 
                ('movie', 'Movies'), 
                ('app', 'Apps'), 
            ]
            suggested = [ ]
            
            for c in categories:
                self.getSuggestedEntities(userId, coords, c, None, limit)
        else:
            if category is None:
                try:
                    category = Entity.subcategories[subcategory]
                except KeyError:
                    raise StampedInputError("invalid subcategory '%s'" % subcategory)
        
        if category != 'place' and category != 'food':
            coords = None
        
        suggested    = self._getSuggestedEntities(coords, category, subcategory)
        num_sections = len(suggested)
        
        if num_sections > 0:
            # filter suggested entities already stamped by this user
            if userId is not None:
                stampIds      = self._collection_collection.getUserStampIds(user_id)
                stamps        = self._stamp_collection.getStamps(stampIds, limit=1000, sort='modified')
                entity_ids    = frozenset(s.entity_id for s in stamps)
            else:
                entity_ids    = frozenset()
            
            section_limit     = limit / num_sections if limit else None
            
            out_suggested = []
            for section in suggested:
                section[1] = filter(lambda e: e.entity_id not in entity_ids, section[1])[:section_limit]
                
                if len(section[1]) > 0:
                    out_suggested.append(section)
            
            suggested = out_suggested
        
        return suggested
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 2 days
    @lru_cache(maxsize=16)
    @memcached_function(time=2*24*60*60)
    def _getSuggestedEntities(self, coords, category, subcategory):
        popular   = True
        suggested = []
        
        if category == 'place' or category == 'food':
            params  = { 'radius' : 100 }
            results = self._google_places.getEntityResultsByLatLng(coords, params)
            
            if results is None:
                return []
            
            popular = False
            suggested.append([ 'Nearby', results ])
        elif category == 'music':
            songs   = self._appleRSS.get_top_songs (limit=10)
            albums  = self._appleRSS.get_top_albums(limit=10)
            
            artists = []
            artists.extend([ s.artists[0] for s in filter(lambda s: len(s.artists) > 0, songs)  ])
            artists.extend([ a.artists[0] for a in filter(lambda a: len(a.artists) > 0, albums) ])
            
            unique_artists = []
            seen = set()
            
            for artist in artists:
                if artist.itunes_id not in seen:
                    seen.add(artist.itunes_id)
                    unique_artists.append(artist)
            
            suggested.append([ 'Artists', unique_artists ])
            suggested.append([ 'Songs',   songs ])
            suggested.append([ 'Albums',  albums ])
        elif category == 'film':
            if subcategory == 'tv':
                # TODO
                pass
            elif subcategory == 'movie':
                movies = self._fandango.get_top_box_office_movies()
                
                suggested.append([ 'Box Office', movies ])
        elif category == 'book':
            subcategory = 'book'
        elif subcategory == 'app':
            top_free_apps       = self._appleRSS.get_top_free_apps(limit=5)
            top_paid_apps       = self._appleRSS.get_top_paid_apps(limit=5)
            top_grossing_apps   = self._appleRSS.get_top_grossing_apps(limit=5)
            
            suggested.append([ 'Top free apps', top_free_apps ])
            suggested.append([ 'Top paid apps', top_paid_apps ])
            suggested.append([ 'Top grossing apps', top_grossing_apps ])
        
        if len(suggested) == 0 or popular:
            suggested.append([ 'Popular', self._get_popular_entities(category, subcategory) ])
        
        return suggested
    
    def _get_popular_entities(self, category, subcategory, limit=10):
        spec = {}
        
        if subcategory is not None:
            spec["entity.subcategory"] = subcategory
        elif category is not None:
            spec["entity.category"] = category
        else:
            return []
        
        ids = self._stamp_collection._collection.find(
            spec=spec, fields={ "entity.entity_id" : 1, "_id" : 0}, output=list)
        
        entity_count = defaultdict(int)
        
        for result in ids:
            entity_count[result['entity']['entity_id']] += 1
        
        entity_ids = list(sorted(entity_count, key=entity_count.__getitem__, reverse=True))
        entity_ids = entity_ids[:limit]
        
        return self._entity_collection.getEntities(entity_ids)
    
    @lazyProperty
    def _google_places(self):
        return GooglePlaces()
    
    @lazyProperty
    def _fandango(self):
        return Fandango()
    
    @lazyProperty
    def _appleRSS(self):
        return AppleRSS()
    
    @lazyProperty
    def _collection_collection(self):
        return MongoCollectionCollection()
    
    @lazyProperty
    def _entity_collection(self):
        return MongoEntityCollection()
    
    @lazyProperty
    def _stamp_collection(self):
        return MongoStampCollection()

