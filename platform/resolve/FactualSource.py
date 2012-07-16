#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FactualSource', 'FactualPlace' ]

import Globals
from logs import report

try:
    import json, re, logs
    from resolve.GenericSource              import GenericSource
    from libs.Factual               import globalFactual
    from resolve.Resolver                   import *
    from resolve.ResolverObject             import *
    from resolve.TitleUtils                 import *
    from utils                      import lazyProperty
    from functools                  import partial
    from urllib2                    import HTTPError
    from resolve.GenericSource              import generatorSource
    from pprint                     import pformat
    from gevent.pool                import Pool
    from api.Schemas                import TimesSchema, HoursSchema
    from search.ScoringUtils        import *
    from search.DataQualityUtils    import *
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


class FactualPlace(ResolverPlace):

    def __init__(self, factual_id=None, data=None):
        # Note: We don't bother with maxLookupCalls with FactualPlaces because right now we know that if data!=None
        # there won't be any lookup calls. If you change the code to implicitly call Factual even when data is provided
        # in the constructor, please add a maxLookupCalls kwarg here and set it to 0 in the constructor calls from
        # FactualSource.searchLite().
        if factual_id is None and data is None:
            raise ValueError("must have id or data")
        ResolverPlace.__init__(self)
        self.__factual_id = factual_id
        self.__data = data

    def _cleanName(self, rawName):
        return cleanPlaceTitle(rawName)

    @lazyProperty
    def factual(self):
        return globalFactual()

    @lazyProperty
    def key(self):
        if self.__factual_id is None:
            return self.data['factual_id']
        else:
            return self.__factual_id

    @lazyProperty
    def data(self):
        if self.__data is None:
            self.countLookupCall('full data')
            return self.factual.data(self.key)
        else:
            return self.__data

    @lazyProperty
    def raw_name(self):
        return self.data['name']

    @lazyProperty
    def coordinates(self):
        try:
            return (self.data['latitude'], self.data['longitude'])
        except Exception:
            return None
    
    @lazyProperty
    def address(self):
        pairs = [
            (k2, self.data[k1])
                for k1, k2 in {
                    'address':'street',
                    'country':'country',
                    'locality':'locality',
                    'postcode':'postcode',
                    'region':'region',
                    'country':'country',
                }.items()
                    if k1 in self.data
        ]
        address = {}
        for k,v in pairs:
            address[k] = v
        return address

    @lazyProperty
    def phone(self):
        if 'tel' in self.data:
            return self.data['tel']
        else:
            return None

    @lazyProperty
    def url(self):
        if 'website' in self.data:
            return self.data['website']
        else:
            return None

    @lazyProperty
    def types(self):
        arts = {
            'Bars': 'bar',
            'Night Clubs': 'night_club',
        }
        food = {
            'Bakeries': 'bakery',
            'Beer, Wine & Spirits': 'bar',
            'Breweries': 'bar',
            'Cafes, Coffee Houses & Tea Houses': 'cafe',
        }
        try:
            c = self.data['category'].split(' > ')
            if c[0] == 'Food & Beverage':
                if c[1] in food:
                    return food[c[1]]
                return ['restaurant']

            elif c[0] == 'Arts, Entertainment & Nightlife':
                if c[1] in arts:
                    return [arts[c[1]]]
        except Exception:
            pass
        return []

    @lazyProperty
    def cuisine(self):
        if 'cuisine' in self.data:
            return [ unicode(i.strip()) for i in self.data['cuisine'].split(',') ]
        return []

    @property 
    def source(self):
        return 'factual'

    def __repr__(self):
        return pformat(self.data)


class FactualSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)


class FactualSource(GenericSource):
    """
    Data-Source proxy for Factual services.
    """
    def __init__(self):
        GenericSource.__init__(self, 'factual',
            groups=[
                'singleplatform',
                'address',
                'price_range',
                'phone',
                'site',
                'cuisine',
                'alcohol_flag',
                'opentable',
                'foursquare',
            ],
            kinds=[
                'place',
            ]
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
            'alcohol_flag':'alcohol',
        }

    @lazyProperty
    def __factual(self):
        return globalFactual()

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.factual_id = proxy.key
        return True

    def matchSource(self, query):
        if query.kind == 'search':
            return self.searchAllSource(query)
        
        if query.kind == 'place':
            return self.placeSource(query)
        
        return self.emptySource

    def placeSource(self, query):
        def gen():
            try:
                results = self.__factual.search(query.name)
                for result in results:
                    yield FactualPlace(data=result)
            except GeneratorExit:
                pass
        return generatorSource(gen())

    def entityProxyFromKey(self, key, **kwargs):
        try:
            data = self.__factual.data(key)
            return FactualPlace(factual_id=key, data=data)
        except KeyError:
            pass
        return None


    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
            
        def gen():
            try:
                raw_results = []

                def getFactualSearch(q, useLocation=False):
                    if useLocation and q.coordinates is not None:
                        results = self.__factual.search(q.query_string, coordinates=q.coordinates)
                    else:
                        results = self.__factual.search(q.query_string)
                    for result in results:
                        raw_results.append(result)

                if query.coordinates is not None:
                    pool = Pool(2)
                    pool.spawn(getFactualSearch, query, False)
                    pool.spawn(getFactualSearch, query, True)
                    pool.join(timeout=timeout)
                else:
                    raw_results = getFactualSearch(query)

                if raw_results is not None:
                    for result in raw_results:
                        yield FactualPlace(data=result)
            except GeneratorExit:
                pass
        return generatorSource(gen(), constructor=FactualSearchAll)


    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=None):
        if queryCategory != 'place':
            raise NotImplementedError()

        local_results = []
        national_results = []

        def getLocalResults():
            # Radius is == the radius used with Google Places.
            results = self.__factual.search(queryText, coordinates=coords, radius=20000, priority="high")
            local_results.extend(results)
        def getNationalResults():
            results = self.__factual.search(queryText, priority="high")
            national_results.extend(results)
        if coords is not None:
            pool = Pool(2)
            pool.spawn(getLocalResults)
            pool.spawn(getNationalResults)
            pool.join(timeout=timeout)
        else:
            getNationalResults()

        if logRawResults:
            logComponents = ['\n\n\nFACTUAL RAW RESULTS\nFACTUAL RAW RESULTS\nFACTUAL RAW RESULTS\n\n\n']
            logComponents.append('NATIONAL RESULTS\n\n')
            logComponents.extend(['\n\n%s\n\n' % pformat(result) for result in national_results])
            if coords:
                logComponents.append('LOCAL RESULTS\n\n')
                logComponents.extend(['\n\n%s\n\n' % pformat(result) for result in local_results])
            logComponents.append('\n\n\nEND FACTUAL RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))
            
        local_results = [FactualPlace(data=result) for result in local_results]
        national_results = [FactualPlace(data=result) for result in national_results]

        # The nice thing about Factual (as compared to Google) is that both national and local search return full
        # results, so we can weight them the same. We weight them both low.
        # TODO: Investigate adding in city name querytext matching to the score augmentation!
        local_results = scoreResultsWithBasicDropoffScoring(local_results, sourceScore=0.4)
        national_results = scoreResultsWithBasicDropoffScoring(national_results, sourceScore=0.4)

        augmentPlaceRelevanceScoresForTitleMatchAndProximity(local_results, queryText, coords)
        augmentPlaceRelevanceScoresForTitleMatchAndProximity(national_results, queryText, coords)

        smoothRelevanceScores(local_results)
        smoothRelevanceScores(national_results)

        jointResults = dedupeById(local_results + national_results)
        for searchResult in jointResults:
            augmentPlaceDataQualityOnBasicAttributePresence(searchResult)
        return jointResults


    def enrichEntity(self, entity, controller, decorations, timestamps):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        #Override and ignores GenericSource.enrichEntity
        try:
            factual_id = entity.sources.factual_id
            if controller.shouldEnrich('factual', self.sourceName, entity):
                factual_id = self.__factual.factual_from_entity(entity)
                entity.sources.factual_id = factual_id
                entity.addThirdPartyId(self.sourceName, factual_id)
                timestamps['factual'] = controller.now
            else:
                return False

            if factual_id is None:
                return True
            if controller.shouldEnrich('singleplatform', self.sourceName, entity):
                singleplatform_id = self.__factual.singleplatform(factual_id)
                entity.sources.singleplatform_id = singleplatform_id
                timestamps['singleplatform'] = controller.now

            if controller.shouldEnrich('foursquare', self.sourceName, entity):
                foursquare_id = self.__factual.foursquare(factual_id)
                entity.sources.foursquare_id = foursquare_id
                timestamps['foursquare'] = controller.now

            # all further enrichments require place/restaurant data so return if not present
            data = self.__factual.data(factual_id,entity=entity, priority="low")

            if data is None:
                return True

            factualPlace = FactualPlace(data=data)

            # set all simple mappings
            for k,v in self.__simple_fields.items():
                if v in data:
                    setattr(entity, k, data[v])

            # set address group
            self.writeFields(entity, data, self.__address_fields)

            # set type
            types = factualPlace.types
            if len(types) > 0:
                entity.types = types

            # Cuisines
            if len(factualPlace.cuisines) > 0:
                entity.cuisine = factualPlace.cuisine

            if 'price' in data:
                try:
                    price = int(float(data['price']))
                    entity.price_range = price
                except:
                    logs.warning('bad formatting on Factual price data: %s', data['price'],exc_info=1)

            if 'hours' in data:
                raw_hours_s = data['hours']
                try:
                    raw_hours = json.loads(raw_hours_s)
                    hours = TimesSchema()
                    broken = False
                    for k,v in raw_hours.items():
                        k = int(k)-1
                        if k < len(self.__hours_map):
                            day = self.__hours_map[k]
                            times = []
                            for slot in v:
                                time_d = HoursSchema()
                                time_d.open = slot[0]
                                time_d.close = slot[1]
                                if len(slot) > 2:
                                    time_d.desc = slot[2]
                                times.append(time_d)
                            setattr(hours, day, times)
                        else:
                            broken = True
                            break
                    if not broken:
                        entity.hours = hours
                except ValueError:
                    logs.warning('bad json for hours')

            try:
                crosswalk_results = self.__factual.crosswalk_id(factual_id, namespace='opentable')
                print(crosswalk_results)
                for result in crosswalk_results:
                    if result['namespace'] == 'opentable':
                        if 'namespace_id' in result and result['namespace_id'] != '':
                            entity.sources.opentable_id = result['namespace_id']
                        else:
                            url = result['url']
                            match = re.match(r'^http://www.opentable.com/([^./]+)$',url)
                            if match is not None:
                                entity.sources.opentable_nickname = match.group(1)
            except:
                pass
        except HTTPError as e:
            logs.warning("Factual threw an %s error for %s (%s)" % (e.code, entity.title, entity.entity_id))
            #timestamps['factual'] = controller.now
            # Let container deal with it
            raise

        return True

if __name__ == '__main__':
    demo(FactualSource(),'Barley Swine')

