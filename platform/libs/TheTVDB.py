#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__       = [ 'TheTVDB', 'globalTheTVDB' ]

import Globals
import string, sys, urllib, utils

from Schemas    import *
from optparse   import OptionParser
from LibUtils   import parseDateString
from lxml       import objectify, etree
from pprint     import pprint
from LRUCache   import lru_cache
from Memcache   import memcached_function

class TheTVDB(object):
    
    def __init__(self, api_key='F1D337C9BF2357FB'):
        self.api_key = api_key
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function(time=7*24*60*60)
    def search(self, query, transform=True, detailed=False):
        url = self._get_url(query)
        
        try:
            xml = utils.getFile(url)
        except:
            return []
        
        tree = objectify.fromstring(xml)
        
        if not transform:
            return tree
        
        items  = tree.findall('.//Series')
        output = []
        
        for item in items:
            language = item.find('language')
            
            if language is not None and language.text is not None:
                if language.text.lower() != 'en':
                    continue
            
            if detailed:
                entity = self.lookup(item.find('id'))
            else:
                entity = self._parse_entity(item)
            
            if entity is not None:
                output.append(entity)
        
        return output
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function(time=7*24*60*60)
    def lookup(self, thetvdb_id):
        details_url = 'http://www.thetvdb.com/api/%s/series/%s/all/' % \
                      (self.api_key, thetvdb_id)
        xml   = utils.getFile(details_url)
        tree  = objectify.fromstring(xml)
        items = tree.findall('.//Series')
        
        """# useful debugging aid
        f = open('thetvdb.%s.xml' % thetvdb_id, 'w')
        f.write(xml)
        f.close()
        """
        
        if items is not None and 1 == len(items):
            item = items[0]
            
            return self._parse_entity(item)
        
        return None
    
    def _parse_entity(self, item):
        _map = {
            'SeriesName'    : 'title', 
            'Overview'      : 'desc', 
            'IMDB_ID'       : 'imdb_id', 
            'id'            : 'thetvdb_id', 
            'ContentRating' : 'mpaa_rating', 
        }
        
        _map2 = {
            'Network'       : ('networks', lambda n: [ BasicEntityMini({ 'title' : n }) ]), 
            'Actors'        : ('cast',     lambda n: map(lambda _: BasicEntityMini({ 'title' : _ }), filter(lambda _: len(_) > 0, n.split('|')))), 
            'Genre'         : ('genres',   lambda n: filter(lambda _: len(_) > 0, n.split('|'))), 
            'Runtime'       : ('length',   lambda n: 60 * int(n)), 
            'FirstAired'    : ('release_date', parseDateString), 
        }
        
        try:
            entity = MediaCollectionEntity()
            entity.types = [ 'tv', ]
            
            for k, v in _map.iteritems():
                elem = item.find(k)
                
                if elem is not None and elem.text is not None:
                    elem = elem.text.strip()
                    
                    if len(elem) > 0:
                        entity[v] = elem
            
            for k, v in _map2.iteritems():
                elem = item.find(k)
                
                if elem is not None and elem.text is not None:
                    elem = elem.text.strip()
                    
                    if len(elem) > 0:
                        entity_key, func = v
                        
                        entity[entity_key] = func(elem)
            
            if entity.title is None:
                return None
            
            images = [ 'poster', 'fanart', 'banner' ]
            entity.images = []
            
            for image in images:
                image = item.find(image)
                
                if image is not None and image.text is not None:
                    image = image.text.strip()
                    
                    if len(image) > 0:
                        image = ImageSchema({
                            'sizes' : [ImageSizeSchema({
                                'url': 'http://thetvdb.com/banners/%s' % image
                            }),]
                        })
                        
                        entity.images.append(image)
                        break
            
            return entity
        except:
            utils.printException()
            return None
    
    def _get_url(self, query):
        params = { 'seriesname' : query }
        
        return 'http://www.thetvdb.com/api/GetSeries.php?%s' % (urllib.urlencode(params))

__globalTheTVDB = None

def globalTheTVDB():
    global __globalTheTVDB
    if __globalTheTVDB is None:
        __globalTheTVDB = TheTVDB()
    
    return __globalTheTVDB

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Print out verbose results")
    
    parser.add_option("-d", "--detailed", action="store_true", default=False, 
                      help="Perform detailed lookup")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    db = globalTheTVDB()
    results = db.search(args[0], 
                        transform = not options.verbose, 
                        detailed  = options.detailed)
    
    if options.verbose:
        print etree.tostring(results, pretty_print=True)
    else:
        for entity in results:
            pprint(entity)

if __name__ == '__main__':
    main()

"""
api = TheTVDB()
ret = api.search('archer', transform=False)
"""

