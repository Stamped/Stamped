#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import EntityDatabases, EntityDataSources
import Globals, MySQLdb, Utils
from GooglePlacesProxyEntityDB import GooglePlacesProxyEntityDB as GooglePlacesProxyEntityDB
from ProxyEntityDB import ProxyEntityDB

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
        for source in self.options.sources:
            Utils.log("")
            Utils.log("Importing entities from source '%s'" % source.name)
            Utils.log("")
            
            if 'place' in source.types:
                sinkDB = GooglePlacesProxyEntityDB(self.options.db)
            else:
                sinkDB = self.options.db
            
            source.importAll(sinkDB, self.options.limit)
            
            if isinstance(sinkDB, ProxyEntityDB):
                sinkDB.close(closeTarget=False)
        
        self.options.db.close()

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
    
    parser.add_option("-d", "--db", 
        type = 'choice', 
        action = 'store', 
        dest = 'db', 
        choices = ['mysql', 'mongo', 'cassandra', 'riak', 'redis', 'simpledb'], 
        default = 'mysql', 
        help="sets the destination database to persist entities to")
    
    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        options.all = True
    
    if options.all:
        options.sources = EntityDataSources.instantiateAll()
    else:
        options.sources = [ ]
        for arg in args:
            source = EntityDataSources.instantiateSource(arg)
            
            if not source:
                print "Error: unrecognized source '%s'" % arg
                parser.print_help()
                return None
            else:
                options.sources.append(source)
    
    if options.db:
        db = EntityDatabases.instantiateDB(options.db)
        if not db:
            print "Error: unrecognized db '%s'" % options.db
            parser.print_help()
            return None
        else:
            options.db = db
    
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
        sys.exit(0)
    
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

