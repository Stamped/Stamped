#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import math, os, re

from pprint import pprint, pformat
from libs.kdtree import KDTree
from libs.data import CityList

__regions = None
__region_suffixes = None

def parse_worldcities():
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/worldcities.txt")

    return parse_file(filename)

def parse_file(filename):
    f = open(filename, 'r')
    f.readline() # header

    for l in f:
        if l.startswith('#'):
            continue

        try:
            row  = l.replace('\n', '').split(',')
            assert len(row) >= 7

            yield {
                'country'       : row[0],
                'cityl'         : row[1],
                'city'          : row[2],
                'region'        : row[3],
                'population'    : int(row[4]) if row[4] else None,
                'lat'           : float(row[5]),
                'lng'           : float(row[6]),
            }
        except:
            pass

def get_world_cities_kdtree():
    cities = list(((city['lat'], city['lng']), city) for city in parse_worldcities())
    cities = filter(lambda city: city[1]['population'] > 100000, cities)
    kdtree = KDTree(cities)

    return kdtree

def __init_regions():
    """
        Initialize the list of regions used to guide searches with location hints.
    """

    global __regions, __region_suffixes

    city_in_state = {}
    __regions     = {}

    for k, v in CityList.popular_cities.iteritems():
        if 'synonyms' in v:
            for synonym in v['synonyms']:
                __regions[synonym.lower()] = v

        v['name'] = k
        __regions[k.lower()] = v

        state = v['state'].lower()
        if not state in city_in_state or v['population'] > city_in_state[state]['population']:
            city_in_state[state] = v

    # push lat/lng as best candidate for state
    for state, v in city_in_state.iteritems():
        __regions[state] = v

        abbreviation = CityList.state_abbreviations[state]
        if abbreviation not in __regions:
            __regions[abbreviation] = v
    
    __region_suffixes = []
    
    for region_name in __regions:
        __region_suffixes.append((' in %s'   % region_name, region_name))
        __region_suffixes.append((' near %s' % region_name, region_name))

def try_get_region(query):
    if __regions is None:
        __init_regions()
    
    query = query.lower()
    
    # process 'in' or 'near' location hint
    if ' in ' in query or ' near ' in query:
        for suffix in __region_suffixes:
            if query.endswith(suffix[0]):
                region_name = suffix[1]
                region = __regions[region_name]
                query  = query[:-len(region_name)]
                
                if query.endswith('in '):
                    query = query[:-3]
                elif query.endswith('near '):
                    query = query[:-5]
                
                query  = query.strip()
                coords = [ region['lat'], region['lng'], ]
                
                return (query, coords, region_name)
    
    return None

if __name__ == '__main__':
    #for city in parse_worldcities():
    #    pprint(city)
    
    kdtree = get_world_cities_kdtree()
    
    tests  = {
        'new york'      : (40.763901, -73.9777), 
        'san francisco' : (37.785911, -122.423401), 
        'los angeles'   : (34.034453, -118.300781), 
        'seattle'       : (47.623752, -122.338257), 
        'miami'         : (25.786908, -80.217361), 
        'phoenix'       : (33.468108, -112.082520), 
        'austin'        : (30.292275, -97.748108), 
        'chicago'       : (41.862402, -87.625580), 
    }
    
    for region, center in tests.iteritems():
        print "%s)" % region
        
        ret    = kdtree.query(center, k=2)
        
        for result in ret:
            dist = math.sqrt((center[0] - result[0][0]) ** 2 + (center[1] - result[0][1]) ** 2)
            
            print "   %s (%s)" % (pformat(result[1]), dist)
        
        print
        print

