#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, gevent, utils
import gevent, thread

import EntitySinks, EntitySources
from GooglePlacesEntityProxy import GooglePlacesEntityProxy
from AEntityProxy import AEntityProxy
from ASyncGatherSource import ASyncGatherSource
from TestEntitySink import TestEntitySink

from optparse import OptionParser
from threading import *

# import specific data sources
import sources

# import all databases
import api.db
from api.MongoStampedAPI import MongoStampedAPI

#-----------------------------------------------------------


# TODO: commandline control over setting up / erasing / updating crawler
# TODO: commandline control over DB versioning s.t. an entire run of the crawler may be rolled back if desired


# TODO: use Crawler(multiprocessing.Process) instead of Thread!
class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, lock, options):
        Thread.__init__(self)
        self.lock = lock
        self.options = options
    
    def run(self):
        sources = map(self._createSourceChain, self.options.sources)
        sink = self.options.sink
        
        sink.start()
        gather = ASyncGatherSource(sources)
        
        gather.startProducing()
        #for entity in gather:
        #    sink.put(entity)
        
        sink.processQueue(gather)
        gevent.joinall(sources)
        gather.join()
        
        sink.join()
        #timeout=2)
        #sink.kill()
        sink.close()
    
    def _createSourceChain(self, source):
        source.limit = self.options.limit
        
        if self.options.googlePlaces and 'place' in source.types:
            source = GooglePlacesEntityProxy(source)
        
        return source

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=True, help="crawl all available sources")
    
    parser.set_defaults(all=False)
    
    parser.add_option("-n", "--numThreads", default=1, type="int", 
        help="sets the number of top-level threads to run")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")
    
    parser.add_option("-s", "--sink", default=None, type="string", 
          action="store", dest="sink", 
        help="where to output to (test or mongodb)")
    
    parser.add_option("-c", "--collection", default="entities", type="string", 
        action="store", dest="collection", 
        help="the collection (mongodb parlance or table in SQL) to populate")
    
    parser.add_option("-t", "--test", default=False, 
        action="store_true", dest="test", 
        help="run the crawler with limited input for testing purposes")
    
    parser.add_option("-u", "--update", default=False, 
        action="store_true", dest="update", 
        help="update the existing collection as opposed to dropping it and " + 
        "overwriting any previous contents (the default)")
    
    parser.add_option("-g", "--googlePlaces", default=False, 
        action="store_true", dest="googlePlaces", 
        help="cross-reference place entities with the google places api")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    if len(args) == 0:
        options.all = True
    
    if options.all:
        options.sources = EntitySources.instantiateAll()
    else:
        options.sources = [ ]
        for arg in args:
            source = EntitySources.instantiateSource(arg)
            
            if source is None:
                print "Error: unrecognized source '%s'" % arg
                parser.print_help()
                return None
            else:
                options.sources.append(source)
    
    if options.sink == "test":
        options.sink = TestEntitySink()
    else:
        options.sink = MongoStampedAPI()
    
    return options

def main():
    """
        Usage: crawler.py [options] [sources]

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -a, --all             crawl all available sources
          -n NUMTHREADS, --numThreads=NUMTHREADS
                                sets the number of top-level threads to run
          -l LIMIT, --limit=LIMIT
                                limits the number of entities to import
          -c COLLECTION, --collection=COLLECTION
                                the collection (mongodb parlance or table in SQL) to
                                populate
          -t, --test            run the crawler with limited input for testing
                                purposes
          -u, --update          update the existing collection as opposed to dropping
                                it and overwriting any previous contents (the default)
          -g, --googlePlaces    cross-reference place entities with the google places
                                api
          -d SINK, --db=SINK    sets the destination database to persist entities to
    """
    
    options = parseCommandLine()
    if options is None:
        return
    
    # global lock used to synchronize access to the DB across threads
    lock = Lock()
    
    if options.numThreads <= 1:
        Crawler(lock, options).run()
    else:
        threads = []
        for i in range(options.numThreads):
            thread = Crawler(lock, options)
            threads.append(thread)
            thread.log("Spawning thread %d" % i)
            thread.start()
        
        for thread in threads:
           thread.join()

# where all the magic starts
if __name__ == '__main__':
    main()

