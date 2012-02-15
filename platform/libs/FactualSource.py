#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FactualSource' ]

import Globals
from logs import log, report

try:
    from AExternalSource    import AExternalSource
    from libs.Factual       import Factual
    from utils              import lazyProperty
    from datetime           import datetime
    from functools          import partial
    import json
except:
    report()
    raise

def _path(path,data):
    cur = data
    for k in path:
        if k in cur:
            cur = cur[k]
        else:
            return None
    return cur

def _ppath(*args):
    return partial(_path,args)

class FactualSource(AExternalSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        AExternalSource.__init__(self)
        self.__address_fields = {
            ('address_street',):_ppath('address'),
            ('address_street_ext',):_ppath('address_extended'),
            ('address_locality',):_ppath('locality'),
            ('address_region',):_ppath('region'),
            ('address_postcode',):_ppath('postcode'),
            ('address_country',):_ppath('country'),
        }
        self.__hours_map = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        self.__simple_fields = {
            'phone':'tel',
            'site':'website',
            'cuisine':'cuisine',
            'alcohol_flag':'alcohol',
        }
        self.__eligible_subcategories = {
            'restaurant'        : 'food', 
            'bar'               : 'food', 
            'bakery'            : 'food', 
            'cafe'              : 'food', 
            'market'            : 'food', 
            'food'              : 'food', 
            'night_club'        : 'food', 
            'establishment'     : 'other',
        }

    @lazyProperty
    def __factual(self):
        return Factual()

    def resolveEntity(self, entity, controller):
        """
        Attempt to fill populate id fields based on seed data.

        Returns True if the entity was modified.
        """
        result = False
        factual_id = entity['factual_id']
        if entity['subcategory'] not in self.__eligible_subcategories:
            return False
        if controller.shouldResolve('factual','factual',entity):
            factual_id = self.__factual.factual_from_entity(entity)
            entity['factual_id'] = factual_id
            entity['factual_timestamp'] = controller.now()
            entity['factual_source'] = 'factual'
            result = True
        if factual_id is not None and controller.shouldResolve('singleplatform','factual',entity):
            singleplatform_id = self.__factual.singleplatform(factual_id)
            entity['singleplatform_id'] = singleplatform_id
            entity['singleplatform_timestamp'] = controller.now()
            entity['singleplatform_source'] = 'factual'
            result = True
        return result
    
    def enrichEntity(self, entity, controller):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        factual_id = entity['factual_id']
        if entity['subcategory'] not in self.__eligible_subcategories:
            return False
        if factual_id is None:
            return False
        result = False
        fields = ['address','phone','tel','site','cuisine','hours','price_range']
        fields.extend(self.__simple_fields.keys())
        should_enrich = False
        for f in fields:
            if controller.shouldEnrich(f,self.sourceName,entity):
                should_enrich = True
                break
        if should_enrich:
            data = self.__factual.data(factual_id,entity=entity)
            if data is not None:
                for k,v in self.__simple_fields.items():
                    if controller.shouldEnrich(k,self.sourceName,entity) and v in data:
                        self.writeSingleton(entity,k,data[v],controller=controller)
                        result = True
                if controller.shouldEnrich('address','factual',entity):
                    self.writeFields(entity, data, self.__address_fields)
                    entity['address_source'] = 'factual'
                    entity['address_timestamp'] = controller.now()
                    result = True
                if controller.shouldEnrich('price_range',self.sourceName,entity) and 'price' in data:
                    try:
                        price = int(data['price'])
                        self.writeSingleton(entity,'price_range',price,controller=controller)
                    except:
                        log.warning('bad formatting on Factual price data: %s', data['price'],exc_info=1)
                if controller.shouldEnrich('hours',self.sourceName,entity) and 'hours' in data:
                    raw_hours_s = data['hours']
                    try:
                        raw_hours = json.loads(raw_hours_s)
                        hours = {}
                        broken = False
                        for k,v in raw_hours.items():
                            k = int(k)-1
                            if k < len(self.__hours_map):
                                day = self.__hours_map[k]
                                times = []
                                for slot in v:
                                    time_d = {}
                                    time_d['open'] = slot[0]
                                    time_d['close'] = slot[1]
                                    if len(slot) > 2:
                                        time_d['desc'] = slot[2]
                                    times.append(time_d)
                                hours[day] = times
                            else:
                                broken = True
                                break
                        if not broken and len(hours) > 0:
                            entity['hours'] = hours
                            entity['hours_timestamp'] = controller.now()
                            entity['hours_source'] = self.sourceName
                            result = True
                    except ValueError:
                        log.warning('bad json for hours')

        return result

    def decorateEntity(self, entity, controller, decoration_db):
        """
        Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity fields if necessary.

        Returns True if the entity was modified.
        """
        return False

    @property
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        return 'factual'
    

