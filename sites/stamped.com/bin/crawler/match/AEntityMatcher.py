#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils

from AStampedAPI            import AStampedAPI
from utils                  import abstract, AttributeDict
from Schemas                import Entity
from pprint                 import pprint
from errors                 import *
from GeocoderEntityProxy    import GeocoderEntityProxy

__all__ = [
    "AEntityMatcher", 
]

class AEntityMatcher(object):
    """
        Abstract base class for finding and matching duplicate entities.
    """
    
    def __init__(self, stamped_api, options=None):
        if options is None:
            options = AttributeDict(
                verbose=False, 
                noop=False, 
            )
        
        self.stamped_api    = stamped_api
        self.options        = options
        self.dead_entities  = set()
        self.numDuplicates  = 0
        self._geocoderProxy = GeocoderEntityProxy(None)
    
    @property
    def _entityDB(self):
        return self.stamped_api._entityDB
    
    @property
    def _placesDB(self):
        return self.stamped_api._placesEntityDB
    
    @property
    def _stampDB(self):
        return self.stamped_api._stampDB
    
    def addOne(self, entity, force=False, override=False):
        if not force:
            result = self.dedupeOne(entity, override=override)
            
            if result is not None:
                return result
        
        if 'place' in entity and entity.lat is None:
            entity = self._geocoderProxy._transform(entity)
        
        entity = self._entityDB.addEntity(entity)
        
        if 'place' in entity:
            self._placesDB.addEntity(entity)
        
        return entity
    
    def addMany(self, entities, force=False, override=False):
        results = []
        for entity in entities or []:
            result = self.addOne(entity, force=force, override=override)
            
            if result is not None:
                results.append(result)
        
        return results
    
    def dedupeOne(self, entity, override=False):
        try:
            if entity.entity_id in self.dead_entities:
                return None
            
            if self.options.verbose:
                utils.log("[%s] deduping %s" % (self, entity.title))
            
            dupes0 = self.getDuplicates(entity)
            
            if len(dupes0) <= 0:
                return None
            
            dupes0 = self.resolveMatches(entity, dupes0)
            
            keep, dupes1 = self.getBestDuplicate(dupes0)
            if 'entity_id' not in keep or keep.entity_id in self.dead_entities:
                return None
            
            assert keep.entity_id is not None
            
            filter_func = (lambda e: e.entity_id != keep.entity_id and not e.entity_id in self.dead_entities)
            dupes1 = filter(filter_func, dupes1)
            
            filter_func2 = (lambda e: e.entity_id is not None)
            dupes2 = filter(filter_func2, dupes1)
            
            numDuplicates = len(dupes1)
            if 0 == numDuplicates:
                return None
            
            numDuplicates2 = len(dupes2)
            
            if numDuplicates2 > 0:
                utils.log("%s) found %d duplicate%s" % (keep.title, numDuplicates, '' if 1 == numDuplicates else 's'))
                self.numDuplicates += numDuplicates2
            
            for i in xrange(numDuplicates):
                dupe = dupes1[i]
                
                if dupe.entity_id is not None:
                    self.dead_entities.add(dupe.entity_id)
                    utils.log("   %d) removing %s" % (i + 1, dupe.title))
            
            self.mergeDuplicates(keep, dupes1, override=override)
            return keep
        except Fail:
            if 'entity_id' in entity:
                entity_id = entity['entity_id']
                
                if entity_id in self.dead_entities:
                    return
                
                utils.log("%s) removing malformed / invalid entity (%s)" % (self.__class__.__name__, entity_id))
                self.dead_entities.add(entity_id)
                
                if not self.options.noop:
                    self._entityDB.removeEntity(entity_id)
                    
                    if 'place' in entity:
                        self._placesDB.removeEntity(entity_id)
            
            return None
        except InvalidState:
            pass
        
        return None
    
    def getDuplicates(self, entity):
        candidate_entities = self.getDuplicateCandidates(entity)
        
        if candidate_entities is None:
            return []
        
        return list(self.getMatchingDuplicates(entity, candidate_entities))
    
    def resolveMatches(self, entity, matches):
        if 'entity_id' in entity:
            entity_id  = entity.entity_id
            numMatches = len(filter(lambda e: e.entity_id == entity_id, matches))
            
            # ensure that the entity in question is contained in the results
            if 0 == numMatches:
                matches.insert(0, entity)
            else:
                index = 0
                while numMatches > 1 and index < len(matches):
                    if matches[index].entity_id == entity_id:
                        matches.pop(index)
                        numMatches -= 1
                    else:
                        index += 1
        else:
            matches.insert(0, entity)
        
        return matches
    
    @abstract
    def getDuplicateCandidates(self, entity):
        pass
    
    @abstract
    def getMatchingDuplicates(self, entity, candidate_entities):
        pass
    
    def getBestDuplicate(self, duplicates):
        # determine which one of the duplicates to keep
        must_keep = []
        found_valid = False
        
        for i in xrange(len(duplicates)):
            entity = duplicates[i]
            
            if 'entity_id' not in entity or entity.entity_id is None:
                continue
            
            if i == len(duplicates) - 1 and not found_valid:
                must_keep.append(i)
            else:
                found_valid = True
                has_stamp = self._stampDB._collection.find_one({ 'entity.entity_id' : entity.entity_id })
                
                if has_stamp != None:
                    must_keep.append(i)
        
        if 0 == len(must_keep):
            return self._getBestDuplicate(duplicates)
        elif 1 == len(must_keep):
            keep = duplicates.pop(must_keep[0])
        else:
            msg = 'error: found %d duplicates which have been stamped' % len(must_keep)
            utils.log(msg)
            raise InvalidState(msg)
        
        return (keep, duplicates)
    
    def _getBestDuplicate(self, duplicates):
        # determine which one of the duplicates to keep
        shortest  = duplicates[0]
        lshortest = len(duplicates[0].title)
        ishortest = 0
        
        for i in xrange(len(duplicates)):
            entity = duplicates[i]
            lmatch = len(entity.title)
            
            if 'entity_id' not in entity or entity.entity_id is None:
                continue
            
            if 'entity_id' not in shortest or \
                shortest.entity_id is None or \
                lmatch < lshortest or \
                (lmatch == lshortest and 'openTable' in entity):
                shortest  = entity
                lshortest = lmatch
                ishortest = i
        
        keep = duplicates.pop(ishortest)
        return (keep, duplicates)
    
    def mergeDuplicates(self, keep, duplicates, override=False):
        numDuplicates = len(duplicates)
        
        assert numDuplicates > 0
        assert 'entity_id' in keep
        wrap = { 'stale' : False }
        
        # look through and remove all duplicates
        for i in xrange(numDuplicates):
            entity = duplicates[i]
            
            def _addDict(src, dest, wrap):
                for k, v in src.iteritems():
                    stale = False
                    
                    if not k in dest:
                        stale = True
                    elif isinstance(v, list):
                        if len(v) != len(dest[k]):
                            stale = True
                    elif isinstance(v, dict):
                        _addDict(v, dest, wrap)
                    
                    if override and not isinstance(v, dict):
                        stale = True
                    
                    if stale:
                        dest[k] = v
                        wrap['stale'] = True
            
            # add any fields from this version of the duplicate to the version 
            # that we're keeping if they don't already exist
            _addDict(entity.value, keep, wrap)
            
            if not self.options.noop and 'entity_id' in entity:
                self._entityDB.removeEntity(entity.entity_id)
                
                if 'place' in entity:
                    self._placesDB.removeEntity(entity.entity_id)
        
        if wrap['stale']:
            if self.options.verbose:
                utils.log("[%s] retaining %s:" % (self, keep.title))
                pprint(keep.value)
            
            if not self.options.noop:
                self._entityDB.updateEntity(keep)
                
                if 'place' in entity:
                    self._placesDB.updateEntity(keep)
        
        return keep
    
    def _convertFromMongo(self, mongo):
        if isinstance(mongo, dict):
            return self._entityDB._convertFromMongo(mongo)
        else:
            objs = []
            for obj in mongo:
                objs.append(self._convertFromMongo(obj))
            
            return objs
    
    def __str__(self):
        return self.__class__.__name__

