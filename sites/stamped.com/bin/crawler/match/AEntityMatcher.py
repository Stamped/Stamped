#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from utils import abstract
from Schemas import Entity
from pprint import pprint
from errors import *

__all__ = [
    "AEntityMatcher", 
]

class AEntityMatcher(object):
    """
        Abstract base class for finding and matching duplicate entities.
    """
    
    def __init__(self, stamped_api, options):
        self.stamped_api = stamped_api
        self.options = options
        
        self.dead_entities = set()
        self.numDuplicates = 0
    
    @property
    def _entityDB(self):
        return self.stamped_api._entityDB
    
    @property
    def _placesDB(self):
        return self.stamped_api._placesEntityDB
    
    @property
    def _stampDB(self):
        return self.stamped_api._stampDB
    
    def dedupeOne(self, mongo_entity, isPlace):
        try:
            if isPlace:
                entity = self._placesDB._convertFromMongo(mongo_entity)
            else:
                entity = self._convertFromMongo(mongo_entity)
            
            if entity.entity_id in self.dead_entities:
                return
            
            if self.options.verbose:
                utils.log("[%s] deduping %s" % (self, entity.title))
            
            dupes0 = self.getDuplicates(entity)
            
            if len(dupes0) <= 1:
                return
            
            keep, dupes1 = self.getBestDuplicate(dupes0)
            if keep.entity_id in self.dead_entities:
                return
            
            filter_func = (lambda e: e.entity_id != keep.entity_id and not e.entity_id in self.dead_entities)
            dupes1 = filter(filter_func, dupes1)
            
            numDuplicates = len(dupes1)
            if 0 == numDuplicates:
                return
            
            utils.log("%s) found %d duplicate%s" % (keep.title, numDuplicates, '' if 1 == numDuplicates else 's'))
            self.numDuplicates += numDuplicates
            
            for i in xrange(numDuplicates):
                dupe = dupes1[i]
                self.dead_entities.add(dupe.entity_id)
                utils.log("   %d) removing %s" % (i + 1, dupe.title))
            
            self.removeDuplicates(keep, dupes1)
        except Fail:
            try:
                entity_id = entity['_id']
            except:
                entity_id = entity['entity_id']
            
            if entity_id in self.dead_entities:
                return
            
            utils.log("%s) removing malformed / invalid entity (%s)" % (self.__class__.__name__, entity_id))
            self.dead_entities.add(entity_id)
            
            if not self.options.noop:
                self._entityDB.removeEntity(entity_id)
                self._placesDB.removeEntity(entity_id)
        except InvalidState:
            pass
    
    def getDuplicates(self, entity):
        candidate_entities = self.getDuplicateCandidates(entity)
        
        if candidate_entities is None:
            return []
        
        matches    = list(self.getMatchingDuplicates(entity, candidate_entities))
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
        
        for i in xrange(len(duplicates)):
            entity = duplicates[i]
            
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
            
            if lmatch < lshortest or (lmatch == lshortest and 'openTable' in entity):
                shortest  = entity
                lshortest = lmatch
                ishortest = i
        
        keep = duplicates.pop(ishortest)
        return (keep, duplicates)
    
    def removeDuplicates(self, keep, duplicates):
        numDuplicates = len(duplicates)
        assert numDuplicates > 0
        
        #titles = set()
        #titles.add(keep.title)
        
        # look through and remove all duplicates
        for i in xrange(numDuplicates):
            entity = duplicates[i]
            
            def _addDict(src, dest):
                for k, v in src.iteritems():
                    if not k in dest:
                        dest[k] = v
                    elif isinstance(v, dict):
                        _addDict(v, dest)
            
            # add any fields from this version of the duplicate to the version 
            # that we're keeping if they don't already exist
            _addDict(entity.value, keep)
            #titles.add(entity.title)
            
            if not self.options.noop:
                self._entityDB.removeEntity(entity.entity_id)
                self._placesDB.removeEntity(entity.entity_id)
        
        #keep.titles = list(titles)
        
        if self.options.verbose:
            utils.log("[%s] retaining %s:" % (self, keep.title))
            pprint(keep.value)
        
        if not self.options.noop:
            self._entityDB.updateEntity(keep)
            self._placesDB.updateEntity(keep)
    
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

