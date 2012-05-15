#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs, Entity

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
    
    """
        Responsible for suggesting relevant / popular entities.
    """
    
    def getSuggestedEntities(self, userId=None, coords=None, category=None, subcategory=None, limit=None):
        """
            Returns a list of suggested entities (separated into sections), restricted 
            to the given category / subcategory, and possibly personalized with respect 
            to the given userId.
            
            Each section is a dict, with at least two required attributes, name, and entities.
        """
        
        if category is not None:
            category    = category.lower().strip()
        if subcategory is not None:
            subcategory = subcategory.lower().strip()
        
        if category is None and subcategory is None:
            # TODO: what is the expected behavior here?
            raise NotImplementedError
        else:
            if category is None:
                try:
                    category = Entity.subcategories[subcategory]
                except KeyError:
                    raise StampedInputError("invalid subcategory '%s'" % subcategory)
        
        if category != 'place' and category != 'food':
            coords = None
        
        suggested    = self._getGlobalSuggestedEntities(coords, category, subcategory)
        from pprint import pformat
        for section in suggested:
            for entity in section['entities']:
                logs.info ('### suggested entity:\n%s' % pformat(entity))
        num_sections = len(suggested)
        
        if num_sections > 0:
            out_suggested     = []
            seen              = defaultdict(set)
            
            # filter suggested entities already stamped by this user
            if userId is not None:
                stampIds      = self._collection_collection.getUserStampIds(userId)
                stamps        = self._stamp_collection.getStamps(stampIds, limit=1000, sort='modified')
                
                for stamp in stamps:
                    seen['entity_id'].add(stamp.entity_id)
            
            def _get_section_limit(i):
                if limit:
                    return (limit / num_sections) + (1 if i + 1 <= (limit % num_sections) else 0)
                
                return None
            
            # process each section, removing obvious duplicates and enforcing per section limits
            for i in xrange(num_sections):
                section_limit = _get_section_limit(i)
                
                section  = suggested[i]

                entities = Entity.fast_id_dedupe(section['entities'], seen)
                entities = entities[:section_limit]
                
                if len(entities) > 0:
                    section['entities'] = entities
                    out_suggested.append(section)
            
            suggested = out_suggested
        
        return suggested
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 8 items 
    # and also cached remotely via memcached with a TTL of 2 days
    #@lru_cache(maxsize=8)
    #@memcached_function(time=2*24*60*60)
    def _getGlobalSuggestedEntities(self, coords, category, subcategory):
        """
            Returns a list of suggested entities (separated into sections), restricted 
            to the given category / subcategory.
            
            Note that this method is global and not personalized to a particular user's 
            preferences.
        """
        
        popular   = True
        suggested = []
        
        def _add_suggested_section(title, entities):
            suggested.append({ 'name' : title, 'entities' : entities })
        
        if category == 'place' or category == 'food':
            if coords is not None:
                params  = { 'radius' : 100 }
                results = self._google_places.getEntityResultsByLatLng(coords, params)
                
                if results is not None:
                    _add_suggested_section('Nearby', results)
                    popular = False
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
            
            _add_suggested_section('Artists', unique_artists)
            _add_suggested_section('Songs',   songs)
            _add_suggested_section('Albums',  albums)
        elif category == 'film':
            if subcategory == 'tv':
                # TODO
                pass
            elif subcategory == 'movie':
                movies = self._fandango.get_top_box_office_movies()
                
                _add_suggested_section('Box Office', movies)
        elif category == 'book':
            subcategory = 'book'
        elif subcategory == 'app':
            top_free_apps       = self._appleRSS.get_top_free_apps(limit=5)
            top_paid_apps       = self._appleRSS.get_top_paid_apps(limit=5)
            top_grossing_apps   = self._appleRSS.get_top_grossing_apps(limit=5)
            
            _add_suggested_section('Top free apps', top_free_apps)
            _add_suggested_section('Top paid apps', top_paid_apps)
            _add_suggested_section('Top grossing apps', top_grossing_apps)
        
        if len(suggested) == 0 or popular:
            _add_suggested_section('Popular', self._get_popular_entities(category, subcategory))
        
        return suggested
    
    def _get_popular_entities(self, category, subcategory, limit=10):
        """ 
            Returns the most popular entities on Stamped restricted to the category / 
            subcategory given, with popularity defined simply by the number of stamps 
            an entity has received.
        """
        
        spec = {}
        
        if subcategory is not None:
            spec["entity.subcategory"] = subcategory
        elif category is not None:
            spec["entity.category"] = category
        else:
            return []
        
        # fetch all entity_ids for stamps in the given category / subcategory
        ids = self._stamp_collection._collection.find(
            spec=spec, fields={ "entity.entity_id" : 1, "_id" : 0}, output=list)
        
        entity_count = defaultdict(int)
        
        # calculate the total number of times each entity was stamped
        for result in ids:
            entity_count[result['entity']['entity_id']] += 1
        
        # sort the resulting entities by stamp count and return the top slice
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

