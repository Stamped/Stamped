#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FactualSource' ]

import Globals
from logs import report

try:
    from BasicSource    import BasicSource
    from libs.Factual       import Factual
    from utils              import lazyProperty
    from functools          import partial
    import json
    import logs
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

class FactualSource(BasicSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        BasicSource.__init__(self, 'factual',
            'factual',
            'singleplatform',

            'address',
            'price_range',
            'phone',
            'site',
            'cuisine',
            'alcohol_flag',
        )
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

    @lazyProperty
    def __factual(self):
        return Factual()

    def enrichEntity(self, entity, controller, decorations, timestamps):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        factual_id = entity['factual_id']
        if controller.shouldEnrich('factual', self.sourceName, entity):
            factual_id = self.__factual.factual_from_entity(entity)
            entity['factual_id'] = factual_id
            timestamps['factual'] = controller.now
        else:
            # Only populate fields when factual id is refreshed
            return False

        if factual_id is None:
            return True
        if controller.shouldEnrich('singleplatform', self.sourceName, entity):
            singleplatform_id = self.__factual.singleplatform(factual_id)
            entity['singleplatform_id'] = singleplatform_id
            timestamps['singleplatform'] = controller.now
        
        # all further enrichments require place/restaurant data so return if not present
        data = self.__factual.data(factual_id,entity=entity)

        if data is None:
            return True
        
        # set all simple mappings
        for k,v in self.__simple_fields.items():
            if v in data:
                entity[k] = data[v]

        # set address group
        self.writeFields(entity, data, self.__address_fields)

        if 'price' in data:
            try:
                price = int(float(data['price']))
                entity['price_range'] = price
            except:
                logs.warning('bad formatting on Factual price data: %s', data['price'],exc_info=1)

        if 'hours' in data:
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
            except ValueError:
                logs.warning('bad json for hours')

        return True

