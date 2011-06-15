#!/usr/bin/env python

import urllib, string, re, os, sys
import MySQLdb, Utils

from BeautifulSoup import BeautifulSoup
from optparse import OptionParser
from sqlite3 import *
from threading import *

# import site-specific crawlers
from OpenTable import *

#-----------------------------------------------------------

class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, siteName, lock):
        Thread.__init__(self)
        self.siteName = siteName.strip()
        self.lock = lock
        self.entities = {}
        self.numDuplicates = 0
    
    def run(self):
        if (self.siteName == "opentable"):
            self.site = SiteOpenTable(self)
        else:
            raise Exception, "Unsupported site '%' specified." % (self.siteName,)
        
        self.initDB()
        self.crawl()
    
    def initDB(self):
        self.lock.acquire()
        self.db = {}
        #self.conn = connect(self.dbInfo['dbName'] + ".db")
        #self.db = self.conn.cursor()
        
        #self.db.execute('CREATE TABLE IF NOT EXISTS ' + self.dbInfo['mainTable'] + 
        #                     ' (viewkey TEXT PRIMARY KEY, title TEXT, pornstars TEXT, tags TEXT, rating DOUBLE, numRatings INT, numViews INT, id INT, visited INT)')

        #self.db.execute('CREATE TABLE IF NOT EXISTS ' + self.dbInfo['relatedVideosTable'] + 
        #                     ' (firstVideoId TEXT, secondVideoId TEXT)')
        self.lock.release()
    
    def getNumEntities(self):
        return len(self.entities)
    
    def crawl(self):
        url = self.site.getNextURL(self.db)
        
        while 1:
            if url == None or url == "":
                numEntities = self.getNumEntities()
                
                self.log("\n")
                self.log("Crawling finished; DB contains %d entities!" % numEntities)
                self.log("Encountered %d duplicates." % self.numDuplicates)
                self.log("\n")
                self.db.close()
                break
            else:
                self.crawlURL(url)
                url = self.site.getNextURL(self.db)
    
    def crawlURL(self, url):
        try:
            self.log("Crawling url " + url + "\n")
            html = urllib.urlopen(url).read()
            entities = self.site.extractData(url, html)
            #print entities
            
            for entity in entities:
                if entity in self.entities:
                    ++self.numDuplicates
                self.entities[entity] = entities[entity]
            
            #self.updateDB(data)
        except (KeyboardInterrupt, SystemExit):
            thread.interrupt_main()
            raise
        except:
            self.log("Error crawling " + url + "\n")
            Utils.HandleException()
            pass
    
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
    
    parser.add_option("-t", "--numThreads", default=8)
    
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
        crawler = Crawler(site, lock)
        crawler.run()
        sys.exit(0)
    else:
        # asynchronous, threaded version
        threads = []
        for i in range(options.numThreads):
            thread = Crawler(site, lock)
            threads.append(thread)
            thread.log("Spawning thread %d" % i)
            thread.start()

        for thread in threads:
           thread.join()

# where all the magic starts
if __name__ == '__main__':
    main()

