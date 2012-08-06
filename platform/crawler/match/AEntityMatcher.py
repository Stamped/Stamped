#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs

from api.AStampedAPI            import AStampedAPI
from utils                  import abstract, AttributeDict
from crawler.GeocoderEntityProxy    import GeocoderEntityProxy
from api.Schemas            import Entity
from Entity                 import setFields, isEqual, getSimplifiedTitle
from datetime               import datetime
from pprint                 import pprint
from errors                 import *

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
    
    @property
    def _activityDB(self):
        return self.stamped_api._activityDB
    
    @property
    def _todoDB(self):
        return self.stamped_api._todoDB
    
    @property
    def _deletedEntityDB(self):
        return self.stamped_api._deletedEntityDB
    
    def addOne(self, entity, force=False, override=False):
        if not force:
            result = self.dedupeOne(entity, override=override)
            
            if result is not None and result.subcategory == entity.subcategory: # and result.title == entity.title:
                return result
        
        if 'place' in entity and entity.lat is None:
            entity2 = self._geocoderProxy._transform(entity)
            if entity2 is not None:
                entity = entity2
        
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
                logs.debug("[%s] deduping %s" % (self, entity.title))
            
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
                logs.debug("%s) found %d duplicate%s" % (keep.title, numDuplicates, '' if 1 == numDuplicates else 's'))
                self.numDuplicates += numDuplicates2
            
            for i in xrange(numDuplicates):
                dupe = dupes1[i]
                
                if dupe.entity_id is not None:
                    self.dead_entities.add(dupe.entity_id)
                    logs.debug("   %d) removing %s" % (i + 1, dupe.title))
            
            self.resolveDuplicates(keep, dupes1, override=override)
            return keep
        except Fail:
            if 'entity_id' in entity:
                entity_id = entity['entity_id']
                
                if entity_id in self.dead_entities:
                    return
                
                logs.debug("%s) removing malformed / invalid entity (%s)" % (self.__class__.__name__, entity_id))
                self.dead_entities.add(entity_id)
                
                if not self.options.noop:
                    self._entityDB.removeEntity(entity_id)
                    
                    if 'place' in entity:
                        self._placesDB.removeEntity(entity_id)
            
            return None
        except:
            utils.printException()
            raise
        
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
            
            must_keep = sorted(must_keep, reverse=True)
            keep = duplicates.pop(must_keep[0])
            delete = []
            
            for i in must_keep[1:]:
                delete.append(duplicates.pop(i))
            
            self.resolveDuplicates(keep, delete)
        
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
    
    def resolveDuplicates(self, entity1, entities, override=False):
        """
            Replaces all references to the entities in entities with 
            entity1, merging all deleted entities into entity1.
        """
        
        if not isinstance(entities, (list, tuple)):
            entities = [ entities ]
        
        # ensure we're not deleting the entity we want to keep
        filter_func = (lambda e: e is not None and e.entity_id is not None and e.entity_id != entity1.entity_id)
        entities_to_delete = filter(filter_func, entities)
        
        if 0 == len(entities_to_delete):
            return
        
        for entity2 in entities_to_delete:
            if not entity2.entity_id:
                logs.debug('SKIPPED: %s' % entity2)
                continue
            
            # update all stamp references of entity2 with entity1
            docs = self._stampDB._collection.find({ 
                'entity.entity_id' : entity2.entity_id }, output=list)
            
            if docs is not None and len(docs) > 0:
                for doc in docs:
                    item = self._stampDB._convertFromMongo(doc)
                    entity1.exportSchema(item.entity)
                    item.timestamp.modified = datetime.utcnow()
                    
                    if self.options.verbose:
                        utils.log("updating stamp '%s' with entity_id '%s' => '%s'" % \
                                  (item.stamp_id, entity2.entity_id, entity1.entity_id))
                        #pprint(item)
                    
                    if not self.options.noop:
                        self._stampDB.update(item)
            
            # update all activity references of entity2 with entity1
            docs = self._activityDB._collection.find({ 
                'link.linked_entity_id' : entity2.entity_id }, output=list)
            
            if docs is not None and len(docs) > 0:
                for doc in docs:
                    item = self._activityDB._convertFromMongo(doc)
                    #item.link.linked_entity = entity1
                    item.link.linked_entity_id = entity1.entity_id
                    
                    if self.options.verbose:
                        utils.log("updating activity '%s' with entity_id '%s' => '%s'" % \
                                  (item.activity_id, entity2.entity_id, entity1.entity_id))
                    
                    if not self.options.noop:
                        self._activityDB.update(item)
            
            # update all favorites references of entity2 with entity1
            docs = self._todoDB._collection.find({
                'entity.entity_id' : entity2.entity_id }, output=list)
            
            if docs is not None and len(docs) > 0:
                for doc in docs:
                    item = self._todoDB._convertFromMongo(doc)
                    entity1.exportSchema(item.entity)
                    
                    if self.options.verbose:
                        utils.log("updating favorite '%s' with entity_id '%s' => '%s'" % \
                                  (item.favorite_id, entity2.entity_id, entity1.entity_id))
                    
                    if not self.options.noop:
                        self._todoDB.update(item)
            
            # update all userfaventities references of entity2 with entity1
            docs = self._todoDB.user_todo_entities_collection._collection.find({
                'ref_ids' : entity2.entity_id }, output=list)
            
            if docs is not None and len(docs) > 0:
                for doc in docs:
                    item = self._todoDB.user_todo_entities_collection._convertFromMongo(doc)
                    refs = item['ref_ids']
                    found = False
                    
                    for i in xrange(len(refs)):
                        ref = refs[i]
                        
                        if ref == entity2.entity_id:
                            refs[i] = entity1.entity_id
                            found = True
                    
                    if self.options.verbose:
                        utils.log("updating userfaventities with entity_id '%s' => '%s'" % \
                                  (entity2.entity_id, entity1.entity_id))
                    
                    if not found:
                        logs.warn("ERROR: unable to update favorite with entity_id '%s' => '%s'" % \
                                  (entity2.entity_id, entity1.entity_id))
                    
                    if not self.options.noop:
                        self._todoDB.user_todo_entities_collection.update(item)
        
        filter_func = (lambda e: e is not None and e.entity_id != entity1.entity_id)
        entities = filter(filter_func, entities)
        
        # merge data from entities to delete into entity1, updating entity1 and removing 
        # all other entities from the entities and places collections
        self._mergeDuplicates(keep=entity1, duplicates=entities, override=override)
    
    def _mergeDuplicates(self, keep, duplicates, override=False):
        numDuplicates = len(duplicates)
        
        if 0 == numDuplicates:
            return
        
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
                    
                    if not stale:
                        if override and not isinstance(v, dict):
                            stale = True
                        
                        if isinstance(v, basestring) and v != dest[k] and k != "entity_id":
                            stale = True
                    
                    if stale:
                        dest[k] = v
                        wrap['stale'] = True
            
            # add any fields from this version of the duplicate to the version 
            # that we're keeping if they don't already exist
            _addDict(entity.dataExport(), keep, wrap)
            
            if not self.options.noop and 'entity_id' in entity:
                try:
                    self._entityDB.removeEntity(entity.entity_id)
                    
                    if 'place' in entity:
                        self._placesDB.removeEntity(entity.entity_id)
                except:
                    utils.log("warning: unable to remove entity '%s' (title=%s) from db (not found)" % \
                              (entity.entity_id, entity.title))
                
                try:
                    # backup the deleted entity to a collection just in case..
                    self._deletedEntityDB.addEntity(entity)
                except:
                    pass
        
        if wrap['stale']:
            if self.options.verbose:
                utils.log("[%s] retaining %s (title=%s) (removed %d):" % \
                          (self, keep.entity_id, keep.title, numDuplicates))
                pprint(keep)
            
            if not self.options.noop:
                keep.titlel = getSimplifiedTitle(keep.title)
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

