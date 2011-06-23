#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import EntityDatabases, EntityDataSources
import Globals, MySQLdb, Utils

from EntityMatcher import EntityMatcher
from optparse import OptionParser
from threading import *

# import specific data sources
from sources.crawlers.OpenTableCrawler import OpenTableCrawler
from sources.dumps.OpenTableDump import OpenTableDump

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB

#-----------------------------------------------------------

# TODO: use Crawler(multiprocessing.Process) instead of Thread!
class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, lock, options):
        Thread.__init__(self)
        self.lock = lock
        self.options = options
        self.log = Utils.log
    
    def run(self):
        for source in self.options.sources:
            self.log("Importing entities from '%s'" % source.name)
            source.importAll(self.options.db, self.options.limit)
        
        #self.crossRencerenceResults()
    
    def crossRencerenceResults(self):
        self.log('')
        self.log('')
        self.log('')
        self.log('Attempting to cross-reference OpenTable restaurants with Google Places')
        self.log('')
        self.log('')
        self.log('')
        
        matcher = EntityMatcher(self.log)
        matched = 0
        count   = len(self.entities)
        
        for entity in self.entities:
            match = None
            
            try:
                match = matcher.tryMatchEntityWithGooglePlaces(entity)
            except (KeyboardInterrupt, SystemExit):
                thread.interrupt_main()
                raise
            except:
                self.log("Error matching entity " + str(entity) + "\n")
                Utils.printException()
                pass
            
            if match is None:
                self.log('NOMATCH ' + str(entity))
            else:
                matched += 1
                self.log('MATCH ' + str(entity))
                self.log(match)
            
            self.log('')
        
        self.log('')
        self.log('MATCHED %d out of %d (%g%%)' % (matched, count, (100.0 * matched) / count))
        self.log('')

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="crawl all available sources")
    
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
    
    if options.all:
        options.sources = EntityDataSources.instantiateAll()
    else:
        if len(args) == 0:
            parser.print_help()
            return None
        
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

