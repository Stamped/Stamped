#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import os, re

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
                'city'          : row[1], 
                'accent_city'   : row[2], 
                'region'        : row[3], 
                'population'    : int(row[4]) if row[4] else None, 
                'lat'           : float(row[5]), 
                'lng'           : float(row[6]), 
            }
        except:
            pass

if __name__ == '__main__':
    #for city in parse_worldcities():
    #    pprint(city)
    
    cities = list(((city['lat'], city['lng']), city) for city in parse_worldcities())
    kdtree = KDTree(cities)
    
    print "New York:"
    ret = kdtree.query((40.763901, -73.9777), k=10)
    
    for result in ret:
        print "   %s" % (pformat(result[1]))

