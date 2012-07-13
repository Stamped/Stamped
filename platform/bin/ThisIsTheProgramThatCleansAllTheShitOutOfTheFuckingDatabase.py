#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from optparse import OptionParser
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from api.db.mongodb.MongoStampCollection import MongoStampCollection
from api.db.mongodb.MongoTodoCollection import MongoTodoCollection

def main():
    usage = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('--dry_run', action='store_true', dest='dry_run', default=False)
    parser.add_option('--nuclear', action='store_true', dest='nuclear', default=False)
    parser.add_option('--max_to_remove', action='store', dest='max_to_remove', default=None)
    (options, args) = parser.parse_args()
    if options.nuclear or options.dry_run:
        print 'FUCK THE WORLD'
        MongoEntityColleciton()._collection.drop()
        # "Welcome to the human race." --Snake Plissken
        return

    entity_collection = MongoEntityCollection()._collection
    entity_ids = [result['_id'] for result in entity_collection.find(fields={'_id':True})]
    todos = MongoTodoCollection()
    stamps = MongoStampCollection()

    removed = 0
    for entity_id in entity_ids:
        if options.max_to_remove is not None and removed >= options.max_to_remove:
            return
        has_attached_user_interactions = (
            list(todos._collection.find({'entity.entity_id' : str(entity_id)}, fields={'_id':1})) or
            list(stamps._collection.find({'entity.entity_id' : str(entity_id)}, fields={'_id':1}))
        )
        if has_attached_user_interactions:
            print 'SKIPPING', entity_id
            continue
        entity_collection.remove({'_id':entity_id})
        removed += 1

if __name__ == '__main__':
    main()