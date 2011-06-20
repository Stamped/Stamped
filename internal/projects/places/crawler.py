#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import MySQLdb, Utils

from EntityMatcher import EntityMatcher
from optparse import OptionParser
from threading import *

# import site-specific crawlers
from OpenTable import *

#-----------------------------------------------------------

# TODO: use Crawler(multiprocessing.Process) instead of Thread!
class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, siteName, lock, options):
        Thread.__init__(self)
        self.siteName = siteName.strip()
        self.lock = lock
        self.entities = {}
        self.options = options
    
    def run(self):
        if (self.siteName == "opentable"):
            self.site = SiteOpenTable(self)
        else:
            raise Exception, "Unsupported site '%' specified." % (self.siteName,)
        
        if self.options.crawl:
            self.crawl()
        else:
            import opentabledata
            self.entities = opentabledata.g_opentable_entities
        
        self.crossRencerenceResults()
    
    def getNumEntities(self):
        return len(self.entities)
    
    def crawl(self):
        url = self.site.getNextURL()
        
        while 1:
            if url == None or url == "" or (self.options.test and len(self.entities) > 30):
                numEntities = self.getNumEntities()
                
                self.log("\n")
                self.log("Crawling finished; DB contains %d entities!" % numEntities)
                self.log("\n")
                break
            else:
                self.crawlURL(url)
                url = self.site.getNextURL()
    
    def crawlURL(self, url):
        try:
            self.log("Crawling url " + url + "\n")
            self.entities = self.site.extractData(url)
            
            #self.updateDB(data)
        except (KeyboardInterrupt, SystemExit):
            thread.interrupt_main()
            raise
        except:
            self.log("Error crawling " + url + "\n")
            Utils.printException()
            pass
    
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
    
    def log(self, s):
        print("[" + self.getName() + "] " + str(s))

def parseCommandLine():
    usage   = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-s", "--sync", action="store_true", dest="sync", 
        default=True, help="Run crawler synchronously per request")
    parser.add_option("-a", "--async", action="store_false", dest="sync", 
        default=False, help="Run crawler asynchronously per request")
    parser.set_defaults(sync=True)
    
    parser.add_option("-t", "--test", action="store_true", dest="test", 
        default=False, help="Run crawler in test mode on a small subset of " + 
        "all possible links (~30 New York restaurants, which should be " + 
        "statistically significant)")
    
    parser.add_option("-l", "--load", action="store_false", dest="crawl", 
        help="Bypass crawling by loading OpenTable data from " +
        "previous run and only process the results")
    
    parser.set_defaults(test=False)
    parser.set_defaults(crawl=True)
    
    parser.add_option("-n", "--numThreads", default=4, 
        help="Set the number of top-level threads to run (assumes --async)")
    
    (options, args) = parser.parse_args()
    print str(options)
    if len(args) > 0:
        parser.print_help()
        return None
    
    return options

def main():
    """
        Usage: crawler.py [options]

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -s, --sync            Run crawler synchronously per request
          -a, --async           Run crawler asynchronously per request
          -t, --test            Run crawler in test mode on a small subset of all
                                possible links (~30 New York restaurants, which should
                                be statistically significant)
          -l, --load            Bypass crawling by loading OpenTable data from
                                previous run and only process the results
          -n NUMTHREADS, --numThreads=NUMTHREADS
                                Set the number of top-level threads to run (assumes
                                --async)
    """
    
    options = parseCommandLine()
    if options is None:
        sys.exit(0)
    
    # global lock used to synchronize access to the DB across threads
    lock = Lock()
    site = "opentable"
    
    if options.sync:
        # synchronous version
        Crawler(site, lock, options).run()
    else:
        # asynchronous, threaded version
        threads = []
        for i in range(options.numThreads):
            thread = Crawler(site, lock, options)
            threads.append(thread)
            thread.log("Spawning thread %d" % i)
            thread.start()

        for thread in threads:
           thread.join()

# where all the magic starts
if __name__ == '__main__':
    main()

