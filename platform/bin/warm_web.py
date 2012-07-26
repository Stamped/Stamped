#!/usr/bin/env python

"""
    Small utility for warming the web server caches for the pages which we anticipate 
    will receive the most traffic and are therefore the most important.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import time, urllib2, utils

from collections    import defaultdict
from gevent.pool    import Pool

def handle_request(url, stats, count=8):
    print "processing '%s'" % url
    
    for i in xrange(count):
        try:
            utils.getFile(url, maxDelay=0)
            stats['200'] += 1
        except urllib2.HTTPError, e:
            print "error %s '%s'" % (e.code, url)
            
            stats['%s' % e.code] += 1
            time.sleep(.5)
            break
        except Exception, e:
            print "error %s '%s'" % (e, url)
            
            stats['error'] += 1
            time.sleep(.5)
            break

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', action='store', default="http://www.stamped.com")
    parser.add_argument('-c', '--count', action='store', type=int, default=8)
    parser.add_argument('-s', '--stamps', action='store', type=int, default=64)
    
    args  = parser.parse_args()
    stats = defaultdict(int)
    pool  = Pool(16)
    
    profiles = {
        'name'  : 'profiles', 
        'paths' : [
            # tastemakers
            'justinbieber', 
            'mariobatali', 
            'urbandaddy', 
            'nymag', 
            'michaelkors', 
            'parislemon', 
            
            "ellendegeneres", 
            "ryanseacrest", 
            "nytimes", 
            "time", 
            "nickswisher", 
            "passionpit", 
            "harvard", 
            "barondavis", 
            "tconrad", 
            "bostonglobe", 
            "hoogs", 
            "smanson22", 
            "austinchronicle", 
            "laureni", 
            "glazer", 
            "swissmiss", 
            "anthonyhawk", 
            "restaurantgirl", 
            "gruber", 
            
            # team-members
            'robby', 
            'bart', 
            'kevin', 
            'anthony', 
            'travis', 
            'landon', 
            'lizwalton', 
            'landon', 
            'ml', 
            'geoffliu', 
            'pauleastlund', 
            'joeystaehle', 
            
            # misc
            'kevinsystrom', 
            'andybons', 
        ]
    }
    
    prefetch = [
        {
            'name'  : 'index', 
            'paths' : [
                '', 'index', 'index.htm', 'index.html', 
                'about', 'about.html', 
                'legal', 'legal.html', 
            ]
        }, 
        profiles, 
        {
            'name'  : 'sdetail', 
        }, 
        {
            'name'  : 'map', 
        }, 
        {
            'name'  : 'map-lite', 
            'paths' : [
                'justinbieber/map?lite=true', 
                'mariobatali/map?lite=true', 
                'urbandaddy/map?lite=true', 
                'nymag/map?lite=true', 
                'michaelkors/map?lite=true', 
                'parislemon/map?lite=true', 
            ]
        }, 
    ]
    
    slash = '/'
    if args.url.endswith('/'):
        slash = ''
    
    for d in prefetch:
        print
        print "-" * 80
        print "prefetching '%s'" % d['name']
        print "-" * 80
        print
        
        if d.get('paths', None) is not None:
            for path in d['paths']:
                url = "%s%s%s" % (args.url, slash, path)
                
                pool.spawn(handle_request, url, stats, args.count)
        elif d['name'] == 'sdetail':
            for path in profiles['paths']:
                for i in xrange(args.stamps):
                    url = "%s%s%s/s/%d" % (args.url, slash, path, i)
                    
                    pool.spawn(handle_request, url, stats, args.count)
        elif d['name'] == 'map':
            for path in profiles['paths']:
                url = "%s%s%s/map" % (args.url, slash, path)
                
                pool.spawn(handle_request, url, stats, args.count)
        
        pool.join()
    
    print
    print "-" * 80
    print "prefetching results:"
    
    for k, v in stats.iteritems():
        print "   %s) %d" % (k, v)
    
    print "-" * 80
    print

