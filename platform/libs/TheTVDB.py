#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import string, sys, urllib, utils

from optparse   import OptionParser
from lxml       import objectify, etree
from Schemas    import Entity
from pprint     import pprint

class TheTVDB(object):
    
    def __init__(self, api_key='F1D337C9BF2357FB'):
        self.api_key = api_key
    
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
    
    def lookup(self, thetvdb_id):
        details_url = 'http://www.thetvdb.com/api/%s/series/%s/all/' % \
                      (self.api_key, thetvdb_id)
        xml   = utils.getFile(details_url)
        tree  = objectify.fromstring(xml)
        items = tree.findall('.//Series')
        
        """
        f = open('out.xml', 'w')
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
            'FirstAired'    : 'original_release_date', 
            'ContentRating' : 'mpaa_rating', 
            'Network'       : 'network_name', 
            'Actors'        : 'cast', 
            'Genre'         : 'genre', 
        }
        
        def _strip(s):
            return string.joinfields(filter(lambda g: len(g) > 0, s.split('|')), ', ')
        
        try:
            entity = Entity()
            entity.subcategory = 'tv'
            
            for k, v in _map.iteritems():
                elem = item.find(k)
                
                if elem is not None and elem.text is not None:
                    elem = elem.text.strip()
                    
                    if len(elem) > 0:
                        entity[v] = elem
            
            if entity.title is None:
                return None
            
            images = [ 'poster', 'fanart', 'banner' ]
            
            for image in images:
                image = item.find(image)
                
                if image is not None and image.text is not None:
                    image = image.text.strip()
                    
                    if len(image) > 0:
                        entity.image = 'http://thetvdb.com/banners/%s' % image
                        break
            
            if entity.genre is not None:
                entity.genre = _strip(entity.genre)
            
            if entity.cast is not None:
                entity.cast = _strip(entity.cast)
            
            return entity
        except:
            utils.printException()
            return None
    
    def _get_url(self, query):
        params = { 'seriesname' : query }
        
        return 'http://www.thetvdb.com/api/GetSeries.php?%s' % (urllib.urlencode(params))

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Print out verbose results")
    
    parser.add_option("-d", "--detailed", action="store_true", default=False, 
                      help="Print out verbose results")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    db = TheTVDB()
    results = db.search(args[0], 
                        transform = not options.verbose, 
                        detailed  = options.detailed)
    
    if options.verbose:
        print etree.tostring(results, pretty_print=True)
    else:
        for entity in results:
            pprint(entity.value)

if __name__ == '__main__':
    main()

"""
db = TheTVDB()
ret = db.search('archer', transform=False)
"""

