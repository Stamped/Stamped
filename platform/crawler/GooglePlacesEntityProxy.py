#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.EntityMatcher import EntityMatcher
from crawler.AEntityProxy import AEntityProxy
from Schemas import Entity
from pprint import pprint

class GooglePlacesEntityProxy(AEntityProxy):
    
    # maps of entity attribute names to funcs which extract the corresponding 
    # attribute from a Google Places detail response.
    _map = {
        'title'     : lambda src: src['name'], 
        'vicinity'  : lambda src: src['vicinity'], 
        'types'     : lambda src: src['types'], 
        'phone'     : lambda src: src['formatted_phone_number'], 
        'address'   : lambda src: src['formatted_address'], 
        'lat'       : lambda src: src['geometry']['location']['lat'], 
        'lng'       : lambda src: src['geometry']['location']['lng'], 
        'gid'       : lambda src: src['id'], 
        'gurl'      : lambda src: src['url'], 
    }
    
    def __init__(self, source):
        AEntityProxy.__init__(self, source)
        
        self._entityMatcher = EntityMatcher()
        self._seen = set()
    
    def _processItems(self, items):
        utils.log("[%s] processing %d items" % (self, utils.count(items)))
        AEntityProxy._processItems(self, items)
    
    def _transform(self, entity):
        #print entity.title
        
        try:
            address = entity.address
        except KeyError:
            try:
                latLng = (entity.lat, entity.lng)
            except KeyError:
                # entity is not a place, so don't try to cross-reference it with google
                return entity
        
        (match, numIterations, interestingResults) = self._entityMatcher.getEntityDetailsFromGooglePlaces(entity)
        
        match_gid = None
        if match is None:
            utils.log('FAIL: %d %s' % (numIterations, entity.title))
            pprint(entity.getDataAsDict())
            return []
        else:
            reference = match['reference']
            details = self._entityMatcher.googlePlaces.getPlaceDetails(reference)
            
            if details is not None:
                match_gid = match['id']
                self._seen.add(match_gid)
                
                for key, extractFunc in self._map.iteritems():
                    try:
                        value = extractFunc(details)
                        entity[key] = value
                    except KeyError:
                        pass
        
        entities = [ entity ]
        
        #print len(interestingResults)
        
        for name in interestingResults:
            result = interestingResults[name]
            gid = result['id']
            
            if gid in self._seen:
                if gid != match_gid:
                    utils.log('DUPLICATE: %s %s' % (gid, name))
                continue
            
            reference = result['reference']
            details = self._entityMatcher.googlePlaces.getPlaceDetails(reference)
            if details is None:
                continue
            else:
                self._seen.add(gid)
            
            e2 = Entity()
            e2.category = "restaurant"
            
            for key, extractFunc in self._map.iteritems():
                try:
                    value = extractFunc(details)
                    e2[key] = value
                except KeyError:
                    pass
                #utils.log("'%s' => '%s'" % (key, str(entity[key])))
            
            entities.append(e2)
        
        return entities
        #if details is not None:
        #    #utils.log('PASS: %d %s' % (numIterations, entity.title))
        #    if details['id'] in self._seen:
        #        utils.log('DUPLICATE: %s %s vs %s' % (details['id'], entity.title, details['name']))
        #        return None
        #    else:
        #        self._seen.add(details['id'])
        #    
        #    for key, extractFunc in self._map.iteritems():
        #        try:
        #            value = extractFunc(details)
        #            entity[key] = value
        #        except KeyError:
        #            pass
        #        #utils.log("'%s' => '%s'" % (key, str(entity[key])))
        #else:
        #    utils.log('FAIL: %d %s' % (numIterations, entity.title))
        #    pprint(entity._data)
        #
        #return entity

