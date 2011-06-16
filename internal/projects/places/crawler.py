#!/usr/bin/env python

import sys, thread
import MySQLdb, Utils

from optparse import OptionParser
from threading import *

from GooglePlaces import GooglePlaces

# import site-specific crawlers
from OpenTable import *

#-----------------------------------------------------------

class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, siteName, lock, options):
        Thread.__init__(self)
        self.siteName = siteName.strip()
        self.lock = lock
        self.entities = {}
        self.numDuplicates = 0
        self.options = options
    
    def run(self):
        if (self.siteName == "opentable"):
            self.site = SiteOpenTable(self)
        else:
            raise Exception, "Unsupported site '%' specified." % (self.siteName,)
        
        self.crawl()
        self.crossRencerenceResults()
    
    def getNumEntities(self):
        return len(self.entities)
    
    def crawl(self):
        url = self.site.getNextURL()
        
        while 1:
            if url == None or url == "" or (self.options.test and len(self.entities) > 10):
                numEntities = self.getNumEntities()
                
                self.log("\n")
                self.log("Crawling finished; DB contains %d entities!" % numEntities)
                self.log("Encountered %d duplicates." % self.numDuplicates)
                self.log("\n")
                break
            else:
                self.crawlURL(url)
                url = self.site.getNextURL()
    
    def crawlURL(self, url):
        try:
            self.log("Crawling url " + url + "\n")
            entities = self.site.extractData(url)
            #print entities
            
            for entity in entities:
                if entity in self.entities:
                    self.numDuplicates += 1
                else:
                    self.entities[entity] = entities[entity]
            
            #self.updateDB(data)
        except (KeyboardInterrupt, SystemExit):
            thread.interrupt_main()
            raise
        except:
            self.log("Error crawling " + url + "\n")
            Utils.HandleException()
            pass
    
    def crossRencerenceResults(self):
        self.log('')
        self.log('')
        self.log('')
        self.log('Attempting to cross-reference OpenTable restaurants with Google Places')
        self.log('')
        self.log('')
        self.log('')
        googlePlaces = GooglePlaces(self.log)
        matched = 0
        count = len(self.entities)
        
        for opentable_rid in self.entities:
            entity = self.entities[opentable_rid]
            match  = googlePlaces.tryMatchEntity(entity)
            
            if match is None:
                self.log('NOMATCH opentable_rid ' + opentable_rid)
                self.log(entity)
                self.log('')
            else:
                matched += 1
                self.log('MATCH opentable_rid ' + opentable_rid)
                self.log(entity)
                self.log(match)
            
            self.log('')
        
        matchedDesc =         
        self.log('')
        self.log('MATCHED %d out of %d (%g%%)' % (matched, count, (100.0 * matched) / count))
        self.log('')
    
    def log(self, s):
        print("[" + self.getName() + "] " + str(s))
    
def parseCommandLine():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    
    parser.add_option("-s", "--sync", action="store_true", dest="sync", 
        default=True, help="Run crawler synchronously per request")
    parser.add_option("-a", "--async", action="store_false", dest="sync", 
        default=False, help="Run crawler asynchronously per request")
    parser.set_defaults(sync=True)
    
    parser.add_option("-t", "--test", action="store_true", dest="test", 
        default=False, help="Run crawler in test mode on a small subset of all possible links")
    parser.set_defaults(test=False)
    
    parser.add_option("-n", "--numThreads", default=4)
    
    (options, args) = parser.parse_args()
    
    if len(args) > 0:
        parser.print_help()
        return None
    
    return options

def main():
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

