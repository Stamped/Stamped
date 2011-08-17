#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import math, pymongo, sys

from MongoStampedAPI import MongoStampedAPI
from db.mongodb.AMongoCollection import MongoDBConfig
from optparse import OptionParser
from Entity import Entity
from difflib import SequenceMatcher
from pprint import pprint
from pymongo.son import SON

# TODO:
    # lazy loading of external entities
        # google places if location is turned on
        # barnes n noble search results otherwise?
    # image support
        # find good python image library
    # fast auxillary data structure for autocomplete, indexed on title?
        # written in C++; would have to take into account alternate titles
    # regression tester for sorting

# TODO: high level
    # how to approach sorting?
        # text match assuming prefix versus full text match
        # proximity (DONE)
        # number of sources (DONE)
        # quality of source (DONE)
        # quality signals within source
            # iTunes rank (DONE)
            # zagat-rated
            # currently on Fandango
        # social signals
            # friends who've stamped an entity
            # is an entity stamped in your inbox?
    # how to approach autocomplete db vs full db?
        # autocomplete data structure vs db?

# TODO: test iTunes album popularity in autocomplete
    # need to ensure that popular artists will appear at the top
    # to what degree should this trump other ranking rules?

# TODO: searchEntities should take into account whether or not 
    # it's an autocompletion (e.g., prefix vs. full match) 
    # and treat certain weights and regexes differently

# TODO: add valid affiliate urls to fandangofeed
# TODO: merge autocomplete.py with MongoEntityCollection.searchEntities

# TODO: add -f option to crawler to either force overwrite of preexisting data or disregard previous records?

# TODO: (DONE) add fandango source
# TODO: (DONE) add pricing info to movies and albums
# TODO: (DONE) filter albums the same way we're filtering movies by retaining 
    # only those which have a valid us storefront price
# TODO: (DONE) add indexing to AppleEPFRelationalDB
# TODO: (DONE) buffer output of AppleEPFRelationalDB
# TODO: (DONE) change AppleEPFRelationalDB to output to a single db file spread over multiple tables
# TODO: (DONE) what are the other regex options available?

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
    
    parser.add_option("-a", "--a", default=None, type="string", 
        action="store", dest="location", help="location")
    
    parser.add_option("-f", "--full", default=False, action="store_true", 
        help="use full search")
    
    parser.add_option("-v", "--verbose", default=False, 
        action="store_true", 
        help="turn verbosity on")
    
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
    
    return (options, args)

subcategory_weights = {
    'restaurant' : 100, 
    'bar' : 90, 
    'book' : 50, 
    'movie' : 60, 
    'artist' : 60, 
    'song' : 20, 
    'album' : 25, 
    'app' : 15, 
    'other' : 10,
}

source_weights = {
    'googlePlaces' : 90, 
    'openTable' : 100, 
    'factual' : 5, 
    'apple' : 75, 
    'zagat' : 95, 
    'urbanspoon' : 80, 
    'nymag' : 95, 
    'sfmag' : 95, 
    'latimes' : 80, 
    'bostonmag' : 90, 
    'fandango' : 1000, 
    'chicagomag' : 80, 
    'phillymag'  : 80, 
}

def _get_subcategory_value(entity):
    subcat = entity.subcategory
    
    if subcat in subcategory_weights:
        weight = subcategory_weights[subcat]
    else:
        weight = 30
    
    return weight / 100.0

def _get_source_value(entity):
    sources = entity.sources
    
    source_value_sum = 0 #sum(source_weights[s] for s in sources)
    for source in sources:
        if source in source_weights:
            source_value_sum += source_weights[source]
        else:
            source_value_sum += 80
    
    return source_value_sum / 100.0

def _get_quality_value(entity):
    value = 1.0
    
    if 'popularity' in entity:
        # popularity is in the range [1,1000]
        value *= 5 * ((2000 - int(entity['popularity'])) / 1000.0)
    
    return value

def _get_distance_value(distance):
    if distance < 0:
        return 0
    
    value = 1.0 / math.log1p(1 + distance)
    value = max(min(value, 100), 0)
    value = value ** 2
    return value

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI()
    #api._entityDB.matchEntities(params.q, limit=10)
    entityDB = api._entityDB
    placesDB = api._placesEntityDB
    
    entityDB._collection.ensure_index([("title", pymongo.ASCENDING)])
    
    input_query = args[0].strip().lower()
    query = input_query
    query = query.replace('[', '\[?')
    query = query.replace(']', '\]?')
    query = query.replace('(', '\(?')
    query = query.replace(')', '\)?')
    query = query.replace('|', '\|')
    query = query.replace('.', '\.?')
    query = query.replace(':', ':?')
    query = query.replace('&', ' & ')
    query = query.replace(' and ', ' (and|&)? ')
    query = query.replace('-', '-?')
    query = query.replace(' ', '[ \t-_]?')
    query = query.replace("'", "'?")
    query = query.replace("$", "[$st]?")
    query = query.replace("5", "[5s]?")
    query = query.replace("!", "[!li]?")
    utils.log("query: %s" % query)
    
    entity_query = {"title": {"$regex": query, "$options": "i"}}
    db_results = entityDB._collection.find(entity_query).limit(250)
    
    results = []
    results_set = set()
    
    if options.location:
        # NOTE: geoNear uses lng/lat and coordinates *must* be stored in lng/lat order in underlying collection
        # TODO: enforce this constraint when storing into mongo
        
        earthRadius = 3959.0 # miles
        q = SON([('geoNear', 'places'), ('near', [options.location[1], options.location[0]]), ('num', 10), ('distanceMultiplier', earthRadius), ('spherical', True), ('query', entity_query)])
        
        ret = placesDB._collection.command(q)
        
        for doc in ret['results']:
            entity = Entity(entityDB._mongoToObj(doc['obj'], 'entity_id'))
            result = (entity, doc['dis'])
            
            results.append(result)
            results_set.add(entity.entity_id)
    
    for entity in db_results:
        e = Entity(entityDB._mongoToObj(entity, 'entity_id'))
        
        if e.entity_id not in results_set:
            results.append((e, -1))
    
    if options.category is not None:
        results = filter(lambda e: e[0].category == options.category, results)
    if options.subcategory is not None:
        results = filter(lambda e: e[0].subcategory == options.subcategory, results)
    
    num_results = len(results)
    if num_results <= 0:
        sys.exit(1)
    
    is_junk = " \t-".__contains__
    
    def _get_weight(result):
        entity   = result[0]
        distance = result[1]
        
        title_value         = SequenceMatcher(is_junk, input_query, entity.title.lower()).ratio()
        subcategory_value   = _get_subcategory_value(entity)
        source_value        = _get_source_value(entity)
        quality_value       = _get_quality_value(entity)
        distance_value      = _get_distance_value(distance)
        
        title_weight        = 1.0
        subcategory_weight  = 0.5
        source_weight       = 0.2
        quality_weight      = 1.0
        distance_weight     = 1.0
        
        # TODO: revisit and iterate on this simple linear ranking formula
        aggregate_value     = title_value * title_weight + \
                              subcategory_value * subcategory_weight + \
                              source_value * source_weight + \
                              quality_value * quality_weight + \
                              distance_value * distance_weight
        
        data = {}
        data['title']  = entity.title
        data['titlev'] = title_value
        data['subcatv'] = subcategory_value
        data['sourcev'] = source_value
        data['qualityv'] = quality_value
        data['distancev'] = distance_value
        data['totalv'] = aggregate_value
        
        #from pprint import pprint
        #pprint(data)
        
        return aggregate_value
    
    # sort the results based on the _get_weight function
    results = sorted(results, key=_get_weight, reverse=True)
    
    # optionally limit the number of results shown
    if options.limit is not None and options.limit >= 0:
        results = results[0 : min(len(results), options.limit)]
    
    # display all results
    for result in results:
        entity = result[0]
        distance = result[1]
        
        if options.verbose:
            data = entity.getDataAsDict()
            data['distance'] = distance
        else:
            data = { }
            data['title'] = utils.normalize(entity.title)
            #data['category'] = entity.category
            data['subcategory'] = utils.normalize(entity.subcategory)
            if 'address' in entity:
                data['addr'] = utils.normalize(entity.address)
            if distance >= 0:
                data['distance'] = distance
        
        pprint(data)
    
    print "%d results found" % (num_results, )

if __name__ == '__main__':
    main()

