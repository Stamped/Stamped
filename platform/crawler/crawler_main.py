#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gevent, json, math, os, sys

from crawler import EntitySources
from crawler.GeocoderEntityProxy import GeocoderEntityProxy
from crawler.AEntityProxy import AEntityProxy
from crawler.ASyncGatherSource import ASyncGatherSource
from crawler.TestEntitySink import TestEntitySink
from crawler.MergeEntitySink import MergeEntitySink

from optparse import OptionParser
from threading import Thread

# import specific data sources
import sources

# import all databases
import api_old.db

#-----------------------------------------------------------

_globals = {}

# TODO: use Crawler(multiprocessing.Process) instead of Thread!
class Crawler(Thread):
    """Crawls for objects..."""
    
    def __init__(self, options):
        Thread.__init__(self)
        self.options = options
    
    def run(self):
        sources = map(self._createSourceChain, self.options.sources)
        
        sink = self.options.sink
        sink.start()
        
        gather = ASyncGatherSource(sources)
        gather.startProducing()
        
        # TODO: get asynchronous mongoDB entity sink processing to work properly
        #sink.processQueue(gather, async=True, poolSize = 4)
        sink.processQueue(gather, async=False)
        
        gevent.joinall(sources)
        gather.join()
        sink.join()
        sink.close()
    
    def _createSourceChain(self, source):
        if self.options.geocode:
            source = GeocoderEntityProxy(source)
        
        return source

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="crawl all available sources (defaults to true if no sources are specified)")
    
    parser.add_option("-o", "--offset", default=None, 
        type="int", dest="offset", 
        help="start index of entities to import")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")
    
    parser.add_option("-r", "--ratio", default=None, type="string", 
        action="store", dest="ratio", 
        help="where this crawler fits in to a distributed stack")
    
    parser.add_option("-s", "--sink", default=None, type="string", 
        action="store", dest="sink", 
        help="where to output to (test or mongodb)")
    
    parser.add_option("-t", "--test", default=False, 
        action="store_true", dest="test", 
        help="run the crawler with limited input for testing purposes")
    
    parser.add_option("-c", "--count", default=False, 
        action="store_true", dest="count", 
        help="print overall entity count from all sources specified and return")
    
    parser.add_option("-u", "--update", default=False, 
        action="store_true", dest="update", 
        help="update the existing collection as opposed to dropping it and " + 
        "overwriting any previous contents (the default)")
    
    parser.add_option("-g", "--geocode", default=False, 
        action="store_true", dest="geocode", 
        help="Geocode places to ensure all places have a valid lat/lng associated with them.")
    
    parser.add_option("-m", "--mount", default=False, 
        action="store_true", dest="mount", 
        help="mount crawler data directory if necessary")
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    #parser.add_option("-d", "--distribute", type="string", 
    #    action="callback", callback=parseDistributedHosts, 
    #    help="run the crawler distributed across the given set of hosts")
    
    (options, args) = parser.parse_args()
    #if hasattr(Globals.options, 'distributed'):
    #    options.distributed = Globals.options.distributed
    #    options.hosts = Globals.options.hosts
    #else:
    #    options.distributed = False
    #    options.hosts = []
    
    options.offset = 0
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
                sys.exit(1)
            else:
                options.sources.append(source)
    
    for source in options.sources:
        source._globals = _globals
    
    if options.count or options.ratio:
        count = 0
        
        for source in options.sources:
            count += source.getMaxNumEntities()
        
        if options.count:
            print count
            sys.exit(0)
        else:
            options.count = count
            num, den = options.ratio.split('/')
            num, den = int(num), int(den)
            num, den = float(num), float(den)
            options.offset = int(math.floor((count * (num - 1)) / den))
            options.limit  = int(math.ceil(count / den) + 1)
    
    if options.db:
        utils.init_db_config(options.db)
    
    if options.sink == "test":
        options.sink = TestEntitySink()
    elif options.sink == "merge":
        options.sink = MergeEntitySink()
    else:
        from api_old.MongoStampedAPI import MongoStampedAPI
        options.sink = MongoStampedAPI(options.db)
    
    return options

def main():
    options = parseCommandLine()
    
    Crawler(options).run()

if __name__ == '__main__':
    main()

