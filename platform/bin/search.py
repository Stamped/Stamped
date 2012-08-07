#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import sys, time

from resolve.EntitySearch   import EntitySearch
from optparse       import OptionParser
from pprint         import pprint
from api_old.Entity     import categories

# TODO: AUTOSUGGEST
    # after setting up CDN, going to have to run a cache-warming process
    # need a concrete benchmark to tune autosuggest against
    # possibly route geo-based searches to nearest edge location:
        # http://aws.amazon.com/cloudfront/#details
        # static.stamped.com/search/...

# TODO:
    # entity keyword search by breaking title up into distinct lexemes
    # unit tests and regression tests for autocomplete
        # Beauty & Essex, Per Se
    # fuzzy autocomplete to help with misspellings?

# TODO: debug Beauty & Essex test case (multiple sources)
# TODO: add simple regression-oriented set of unit tests for entity searcher
    # fast auxillary data structure for autocomplete, indexed on title?
        # written in C++; would have to take into account alternate titles
        # or possibly a smaller mongo collection, optimized for search
    # regression tester for search results

# TODO: high level
    # how to approach sorting?
        # text match assuming prefix versus full text match
        # proximity (DONE)
        # number of sources (DONE)
        # quality of source (DONE)
        # quality signals within source
            # iTunes rank (DONE)
            # zagat-rated (DONE)
            # currently on Fandango (DONE)
        # social signals
            # friends who've stamped an entity
            # is an entity stamped in your inbox?
    # how to approach autocomplete db vs full db?
        # autocomplete data structure vs db?

# TODO: test iTunes album popularity in autocomplete
    # need to ensure that popular artists will appear at the top
    # to what degree should this trump other ranking rules?

# TODO: add valid affiliate urls to fandangofeed
# TODO: add -f option to crawler to either force overwrite of preexisting data or disregard previous records?

# TODO: (DONE) add photo support
# TODO: (DONE) add fandango source
# TODO: (DONE) add pricing info to movies and albums
# TODO: (DONE) filter albums the same way we're filtering movies by retaining 
    # only those which have a valid us storefront price
# TODO: (DONE) add indexing to AppleEPFRelationalDB
# TODO: (DONE) buffer output of AppleEPFRelationalDB
# TODO: (DONE) change AppleEPFRelationalDB to output to a single db file spread over multiple tables
# TODO: (DONE) what are the other regex options available?
# TODO: (DONE) searchEntities should take into account whether or not 
# TODO: (DONE) merge autocomplete.py with MongoEntityCollection.searchEntities
# TODO: (DONE) support 'blank (in|near) [city or region]'
    # would need to support general recognizing of city/region
    # would need city/region list to match against
# TODO: (DONE)
    # dedupe books
    # unit tests for deduper
# TODO: (DONE)
    # lazy loading of external entities
        # location
            # google places
        # misc:
            # amazon
    # image support
        # find good python image library (PIL?)
        # static.stamped.com or cdn.stamped.com

# travis' manhattan apartment (for proximity testing purposes): '40.797898,-73.968148'

#-----------------------------------------------------------


def parseCommandLine():
    """
        Usage: autocomplete.py [options] query

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -d DB, --db=DB        db to connect to for output
          -l LIMIT, --limit=LIMIT
                                limits the number of entities to import
          -a LOCATION, --a=LOCATION
                                location
          -f, --full            use full search
          -v, --verbose         turn verbosity on
          -c CATEGORY, --category=CATEGORY
                                filters results by a given category
          -s SUBCATEGORY, --subcategory=SUBCATEGORY
                                filters results by a given subcategory
    """
    
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")
    
    parser.add_option("-L", "--Local", default=False, action="store_true", 
        help="local nearby search")
    
    parser.add_option("-a", "--a", default=None, type="string", 
        action="store", dest="location", help="location (lat/lng, e.g. '40.7360067,-73.98884296')")
    
    parser.add_option("-f", "--full", default=False, action="store_true", 
        help="use full search")
    
    parser.add_option("-p", "--prefix", default=False, action="store_true", 
        help="use faster prefix-based search")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="turn verbosity on")
    
    parser.add_option("-S", "--Stats", default=False, action="store_true", 
        help="view ranking stats")
    
    parser.add_option("-c", "--category", default=None, type="string", 
        action="store", dest="category", 
        help="filters results by a given category")
    
    parser.add_option("-s", "--subcategory", default=None, type="string", 
        action="store", dest="subcategory", 
        help="filters results by a given subcategory")
    
    (options, args) = parser.parse_args()
    
    if len(args) <= 0:
        parser.print_help()
        sys.exit(1)
    
    if options.db:
        utils.init_db_config(options.db)
    
    if options.location:
        assert ',' in options.location
        
        lat, lng = options.location.split(',')
        options.location = (float(lat), float(lng))

    if options.category and options.category not in categories:
        raise Exception("Unrecognized category: '%s'; must be one of: %s" % (options.category, ", ".join(categories)))
    
    return (options, args)

def main():
    options, args = parseCommandLine()

    t1 = time.time()
    results = EntitySearch().searchEntities(query=args[0],
                                            limit=options.limit,
                                            coords=options.location,
                                            category=options.category,
                                            subcategory=options.subcategory)
    t2 = time.time()

    duration = (t2 - t1) * 1000.0
    print "search took %g ms" % duration
        
    # display all results
    for result in results:
        entity   = result

        if options.verbose:
            data = entity.dataExport()
            if not options.Stats:
                try:
                    del data['stats']
                except:
                    pass
        else:
            data = { }
            data['title']  = utils.normalize(entity.title)
            data['subtitle'] = entity.subtitle

            #data['titles'] = utils.normalize(entity.simplified_title)

            data['subcategory'] = utils.normalize(entity.subcategory)
            if hasattr(entity, 'address_locality') and entity.address_locality is not None:
                data['addr'] = entity.formatAddress()
            #data['subtitle'] = utils.normalize(entity.subtitle)

            if options.Stats:
                data['stats'] = entity.dataExport()['stats']
        pprint(data)

    print
    print

if __name__ == '__main__':
    main()

