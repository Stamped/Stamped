#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import gevent, json, math, os, sys

import EntitySinks, EntitySources
from GooglePlacesEntityProxy import GooglePlacesEntityProxy
from AEntityProxy import AEntityProxy
from ASyncGatherSource import ASyncGatherSource
from TestEntitySink import TestEntitySink
from api.db.mongodb.AMongoCollection import MongoDBConfig

from optparse import OptionParser
from threading import Thread

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
    
    def __init__(self, options):
        Thread.__init__(self)
        self.options = options
    
    def run(self):
        sources = map(self._createSourceChain, self.options.sources)
        
        sink = self.options.sink
        sink.start()
        
        gather = ASyncGatherSource(sources)
        gather.startProducing()
        
        sink.processQueue(gather)
        
        gevent.joinall(sources)
        gather.join()
        sink.join()
        sink.close()
    
    def _createSourceChain(self, source):
        if self.options.googlePlaces and 'place' in source.types:
            source = GooglePlacesEntityProxy(source)
            #source = MultiprocessingEntityProxy(source, GooglePlacesEntityProxy)
        
        return source

#def parseDistributedHosts(option, opt, value, parser):
#    Globals.options.distributed = True
#    Globals.options.hosts = value.split(',')

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
    
    parser.add_option("-g", "--googlePlaces", default=False, 
        action="store_true", dest="googlePlaces", 
        help="cross-reference place entities with the google places api")
    
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
    
    Globals.options = options
    
    options.offset = 0
    options.limit  = None
    
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
        if ':' in options.db:
            options.host, options.port = options.db.split(':')
            options.port = int(options.port)
        else:
            options.host, options.port = (options.db, 27017)
        
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            os.mkdir(os.path.join(config_path, "conf"))
        except:
            pass
        config_path = os.path.join(config_path, "conf/stamped.conf")
        
        conf = {
            'mongodb' : {
                'host' : options.host, 
                'port' : options.port, 
            }
        }
        
        cfg = MongoDBConfig.getInstance()
        cfg.config = utils.AttributeDict(conf)
        
        #conf_str = json.dumps(conf, sort_keys=True, indent=2)
        #utils.write(config_path, conf_str)
    
    if options.sink == "test":
        options.sink = TestEntitySink()
    else:
        options.sink = MongoStampedAPI()
    
    return options

def main():
    """
    """
    
    options = parseCommandLine()
    #print "distributed: %s " % options.distributed
    #print "hosts: %s" % options.hosts
    
    Crawler(options).run()

if __name__ == '__main__':
    main()

