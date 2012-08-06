#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import sys

from crawler.match.EntityMatcher import EntityMatcher
from api.MongoStampedAPI     import MongoStampedAPI
from Schemas             import Entity
from optparse            import OptionParser

#-----------------------------------------------------------

def parseCommandLine():
    usage   = "Usage: %prog [options] one_or_more_entity_ids_to_delete entity_id_to_keep"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run the dedupper in noop mode without modifying anything")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    parser.add_option("-f", "--force", default=False, action="store_true", 
        help="force overriding of keys during deduping")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI()
    matcher = EntityMatcher(api, options)
    
    keep = Entity()
    keep.entity_id = args[-1]
    
    remove = []
    for arg in args[:-1]:
        entity = Entity()
        entity.entity_id = arg
        remove.append(entity)
    
    matcher.resolveDuplicates(keep, remove, override=options.force)

if __name__ == '__main__':
    main()

