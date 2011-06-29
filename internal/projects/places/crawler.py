#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, gevent, Utils
import gevent, thread

import EntitySinks, EntitySources
from GooglePlacesEntityProxy import GooglePlacesEntityProxy
from AEntityProxy import AEntityProxy
from ASyncGatherSource import ASyncGatherSource

from optparse import OptionParser
from threading import *

# import specific data sources
from sources.crawlers.OpenTableCrawler import OpenTableCrawler
from sources.dumps.OpenTableDump import OpenTableDump
from sources.dumps.FactualiPhoneAppsDump import FactualiPhoneAppsDump
from sources.dumps.FactualUSPlacesDump import FactualUSPlacesDump
from sources.dumps.FactualUSRestaurantsDump import FactualUSRestaurantsDump

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB

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
        sources = (self._createSourceChain(source) for source in self.options.sources)
        
        self.options.sink.start()
        gather = ASyncGatherSource(sources)
        
        gather.startProducing()
        for entity in gather:
            self.options.sink.put(entity)
        
        gevent.joinall(self.options.sources)
        
        #self.options.sink.join()
        self.options.sink.kill()
        self.options.sink.close()
    
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
    
    parser.add_option("-g", "--googlePlaces", default=False, 
        action="store_true", dest="googlePlaces", 
        help="cross-reference place entities with the google places api")
    
    parser.add_option("-d", "--db", 
        type = 'choice', 
        action = 'store', 
        dest = 'sink', 
        choices = ['mysql', 'mongo', 'cassandra', 'riak', 'redis', 'simpledb'], 
        default = 'mysql', 
        help="sets the destination database to persist entities to")
    
    (options, args) = parser.parse_args()
    
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
    
    if options.sink:
        sink = EntitySinks.instantiateSink(options.sink)
        
        if sink is None:
            print "Error: unrecognized db '%s'" % options.sink
            parser.print_help()
            return None
        else:
            options.sink = sink
    
    return options

def main():
    """
        Usage: crawler.py [options] [sources]

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -a, --all             Crawl all available sources
          -n NUMTHREADS, --numThreads=NUMTHREADS
                                Set the number of top-level threads to run
          -d DB, --db=DB        Sets the destination database to persist entities to.
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

