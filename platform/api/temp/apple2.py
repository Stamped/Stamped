#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.sources.dumps.AppleEPFRelationalDB import *
from api.MongoStampedAPI        import MongoStampedAPI
from crawler.match.EntityMatcher    import EntityMatcher
from gevent.pool            import Pool
from libs.apple             import AppleAPI
from optparse               import OptionParser
from pprint                 import pprint

#-----------------------------------------------------------

"""
rm -rf /postgres
mkdir -p /postgres
chmod 0700 /postgres

initdb /postgres
pg_ctl -D /postgres -l /postgres/postgres.log start
createdb stamped

"""

#-----------------------------------------------------------

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run the dedupper in noop mode without modifying anything")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    if options.db:
        utils.init_db_config(options.db)
    
    return options

def main():
    options = parseCommandLine()
    
    ret = utils.shell(r"grep 'class.*(AppleEPFRelationalDB' sources/dumps/AppleEPFRelationalDB.py | sed 's/class \([^(]*\)(.*/\1/g'")
    ret = map(lambda r: r.strip() + "()", ret[0].split('\n'))
    
    for r in ret:
        cls = eval(r)
        
        cls._run()
        #cls.start()
        #cls.join()
        cls.close()

if __name__ == '__main__':
    main()

# TODO: how to get desc for artist or album?

"""



"""
