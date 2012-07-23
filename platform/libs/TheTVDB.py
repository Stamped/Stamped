#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__       = [ 'TheTVDB', 'globalTheTVDB' ]

import Globals
import string, sys, urllib, utils

from api.Schemas            import *
from optparse        import OptionParser
from libs.LibUtils        import parseDateString
from lxml            import objectify, etree
from pprint          import pprint
from libs.LRUCache        import lru_cache
from libs.CachedFunction  import cachedFn
from libs.CountedFunction import countedFn
from libs.Request        import service_request
from api.Schemas         import MediaCollectionEntity
from APIKeys import get_api_key

API_KEY = get_api_key('tvdb', 'api_key')

class TheTVDB(object):
    
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn(name='TheTVDB (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn(schemaClasses=[MediaCollectionEntity])
    @countedFn(name='TheTVDB (after caching)')
    def searchRaw(self, query, priority='low', timeout=None):

        url = 'http://www.thetvdb.com/api/GetSeries.php'
        params = { 'seriesname' : query }
        try:
            response, xml = service_request('tvdb', 'GET', url, query_params=params, priority=priority, timeout=timeout)
        except:
            return None

        # Putting results into the mongo cache will convert them to unicode, so in order to keep things parallel between
        # the case where this does go through the cache and the case where it doesn't, we decode here and encode on the
        # other side.
        return xml.decode('utf-8')

    def search(self, query, transform=True, detailed=False, priority='low', timeout=None):
        xml = self.searchRaw(query, priority, timeout)
        if xml is None:
            return []

        tree = objectify.fromstring(xml.encode('utf-8'))
        
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
                entity = self.lookup(int(item.find('id')))
            else:
                entity = self._parse_entity(item)
            
            if entity is not None:
                output.append(entity)
        
        return output

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn(name='TheTVDB (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn(schemaClasses=[MediaCollectionEntity])
    @countedFn(name='TheTVDB (after caching)')
    def lookup(self, thetvdb_id, priority='low', timeout=None):
        details_url = 'http://www.thetvdb.com/api/%s/series/%s/all/' % \
                      (self.api_key, thetvdb_id)

        response, xml = service_request('tvdb', 'GET', details_url, priority=priority, timeout=timeout)
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

    # TODO: There's a lot of similar code to this in other places translating between schemas; consolidate into a single
    # utility class somewhere!
    class SingleFieldTranslator(object):
        def __init__(self, original_name, new_path, conversion_func=lambda x: x):
            self.__original_name = original_name
            if isinstance(new_path, basestring):
                new_path = [new_path]
            elif not isinstance(new_path, list):
                raise Exception("Invalid new_path passed to TVDBSingleFieldTranslator()")
            self.__new_path = new_path
            self.__conversion_func = conversion_func

        def translateFieldToEntity(self, tvdb_item, entity):
            elem = tvdb_item.find(self.__original_name)
            if elem is None or elem.text is None:
                return
            elem = elem.text.strip()
            if len(elem) == 0:
                return
            target = entity
            for i in range(len(self.__new_path) - 1):
                target = getattr(target, self.__new_path[i])
            setattr(target, self.__new_path[-1], self.__conversion_func(elem))

    def _parse_entity(self, item):
        # TODO: This is completely out of keeping with how every other source does this. The rest all return raw
        # XML here and then map fields in the ResolverObject class, whereas this actually converts to an Entity here
        # and then has a resolver class that just passes through to the entity. Ugh.
        def makeBasicEntityMini(title, mini_type=BasicEntityMini):
            result = mini_type()
            result.title = title
            return result

        translators = [
            TheTVDB.SingleFieldTranslator('SeriesName',     'title'),
            TheTVDB.SingleFieldTranslator('Overview',       'desc'),
            TheTVDB.SingleFieldTranslator('IMDB_ID',        ['sources', 'imdb_id']),
            TheTVDB.SingleFieldTranslator('id',             ['sources', 'thetvdb_id']),
            TheTVDB.SingleFieldTranslator('ContentRating',  'mpaa_rating'),
            TheTVDB.SingleFieldTranslator('Network',        'networks',     lambda n: [ makeBasicEntityMini(n) ]),
            TheTVDB.SingleFieldTranslator('Actors',         'cast',
                                          lambda n: map(lambda _: makeBasicEntityMini(_, mini_type=PersonEntityMini), filter(lambda _: len(_) > 0, n.split('|')))),
            TheTVDB.SingleFieldTranslator('Genre',          'genres',       lambda n: filter(lambda _: len(_) > 0, n.split('|'))),
            TheTVDB.SingleFieldTranslator('Runtime',        'length',       lambda n: 60 * int(n)),
            TheTVDB.SingleFieldTranslator('FirstAired',     'release_date', parseDateString)
        ]
        
        try:
            entity = MediaCollectionEntity()
            entity.types = [ 'tv', ]
            
            for translator in translators:
                translator.translateFieldToEntity(item, entity)

            if entity.title is None:
                return None
            
            images = [ 'poster', 'fanart', 'banner' ]
            entity.images = []
            
            for image in images:
                image = item.find(image)
                
                if image is not None and image.text is not None:
                    image = image.text.strip()
                    
                    if len(image) > 0:
                        inner_img_schema = ImageSizeSchema()
                        inner_img_schema.url = 'http://thetvdb.com/banners/%s' % image
                        img_schema = ImageSchema()
                        img_schema.sizes = [ inner_img_schema ]
                        entity.images = [ img_schema ]
                        break
            
            return entity
        except:
            utils.printException()
            return None
    

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

