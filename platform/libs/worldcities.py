#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import math, os, re

from pprint import pprint, pformat
from kdtree import KDTree

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

