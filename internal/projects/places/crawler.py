#!/usr/bin/env python

import urllib, string, re, os, sys
import MySQLdb

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
        Thread.__init__(self);
        self.siteName = siteName.strip();
        self.lock = lock;
    
    def run(self):
        if (self.siteName == "opentable"):
            self.site = SiteOpenTable(self);
        else:
            raise Exception, "Unsupported site '%' specified." % (self.siteName,);
        
        self.dbInfo = self.site.getDBInfo();
        self.initDB();
        self.crawl();
    
    def initDB(self):
        self.dbInfo = self.site.getDBInfo();
        self.lock.acquire();
        #self.conn = connect(self.dbInfo['dbName'] + ".db")
        #self.db = self.conn.cursor()
        
        #self.db.execute('CREATE TABLE IF NOT EXISTS ' + self.dbInfo['mainTable'] + 
        #                     ' (viewkey TEXT PRIMARY KEY, title TEXT, pornstars TEXT, tags TEXT, rating DOUBLE, numRatings INT, numViews INT, id INT, visited INT)');

        #self.db.execute('CREATE TABLE IF NOT EXISTS ' + self.dbInfo['relatedVideosTable'] + 
        #                     ' (firstVideoId TEXT, secondVideoId TEXT)');
        self.lock.release();
    
    def getNumEntries(self):
        #self.db.execute('SELECT COUNT(*) FROM ' + self.dbInfo['mainTable'] + ' WHERE visited = 1');
        #numEntries = self.db.fetchone();
        numEntries = 0;
        if (numEntries == None):
            numEntries = 0;
        else:
            numEntries = numEntries[0];
        
        return numEntries;
    
    def crawl(self):
        url = self.site.getNextURL(self.db);
        
        while 1:
            if url == None or url == "":
                numEntries = self.getNumEntries();
                
                self.log("\nCrawling finished; DB contains %d entries!\n" % numEntries);
                self.db.close();
                break;
            else:
                self.crawlURL(url);
                url = self.site.getNextURL(self.db);
    
    def crawlURL(self, url):
        try:
            #self.log("Crawling url " + url);
            html = urllib.urlopen(url).read();
            data = self.site.extractData(url, html);
            #print data;
            
            self.updateDB(data);
        except (KeyboardInterrupt, SystemExit):
            thread.interrupt_main();
            raise
        except:
            self.log("Error crawling " + url + "\n");
            pass
    
    def log(self, s):
        print("[" + self.getName() + "] " + s);
    
    def updateDB(self, data):
        """
        parentViewkey = data['viewkey'];
        
        if parentViewkey is None or parentViewkey == "":
            return;
        
        try:
            self.db.execute('insert into ' + self.dbInfo['mainTable'] + ' values (?,?,?,?,?,?,?,?,?)', (
                parentViewkey, 
                data['title'], 
                data['pornstars'], 
                data['tags'], 
                data['rating'], 
                data['numRatings'], 
                data['numViews'], 
                data['id'], 
                1
            ));
        except (KeyboardInterrupt, SystemExit):
            thread.interrupt_main();
            raise
        except: 
            self.db.execute('update ' + self.dbInfo['mainTable'] + ' set title=?, pornstars=?, tags=?, rating=?, numRatings=?, numViews=?, id=?, visited=1 where viewkey=?', (
                data['title'], 
                data['pornstars'], 
                data['tags'], 
                data['rating'], 
                data['numRatings'], 
                data['numViews'], 
                data['id'], 
                parentViewkey, 
            ));
            pass
        
        for item in data['relatedVideos']:
            viewkey = item['viewkey'];
            if viewkey != "":
                try:
                    self.db.execute('insert into ' + self.dbInfo['mainTable'] + ' values (?,?,?,?,?,?,?,?,?)', (
                        viewkey, 
                        item['title'], 
                        '', 
                        '', 
                        '', 
                        0, 
                        0, 
                        0, 
                        0, # has not been visited yet
                    ));
                except (KeyboardInterrupt, SystemExit):
                    thread.interrupt_main();
                    raise
                except:
                    pass
                
                try:
                    self.db.execute('insert into ' + self.dbInfo['relatedVideosTable'] + ' values (?, ?)', (
                        parentViewkey, 
                        viewkey
                    ));
                except (KeyboardInterrupt, SystemExit):
                    thread.interrupt_main();
                    raise
                except:
                    pass
        
        self.conn.commit();
        """

def parseCommandLine():
    usage = "Usage: %prog [options]";
    parser = OptionParser(usage);
    
    parser.add_option("-s", "--sync", action="store_true", dest="sync", 
        default=True, help="Run crawler synchronously per request");
    parser.add_option("-a", "--async", action="store_false", dest="sync", 
        default=False, help="Run crawler asynchronously per request");
    parser.set_defaults(sync=True);
    
    parser.add_option("-t", "--numThreads", default=8);
    
    (options, args) = parser.parse_args();
    
    if len(args) > 0:
        parser.print_help();
        return None;
    
    return options;

def main():
    options = parseCommandLine();
    if options is None:
        sys.exit(0);
    
    # global lock used to synchronize access to the DB across threads
    lock = Lock();
    site = "opentable";
    
    if options.sync:
        # synchronous version
        crawler = Crawler(site, lock);
        crawler.run();
        sys.exit(0);
    else:
        # asynchronous, threaded version
        threads = [];
        for i in range(options.numThreads):
            thread = Crawler(site, lock);
            threads.append(thread);
            thread.log("Spawning thread %d" % i);
            thread.start();

        for thread in threads:
           thread.join();

# where all the magic starts
if __name__ == '__main__':
    main()

