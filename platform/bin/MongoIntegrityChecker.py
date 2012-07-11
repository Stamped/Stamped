#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import sys, traceback, string
import logs, time, bson

from errors                 import *
from optparse               import OptionParser

from api.db.mongodb.MongoInboxStampsCollection          import MongoInboxStampsCollection
from api.db.mongodb.MongoUserStampsCollection           import MongoUserStampsCollection
from api.db.mongodb.MongoCreditReceivedCollection       import MongoCreditReceivedCollection
from api.db.mongodb.MongoUserLikesCollection            import MongoUserLikesCollection
from api.db.mongodb.MongoUserTodosEntitiesCollection    import MongoUserTodosEntitiesCollection
from api.db.mongodb.MongoStampCommentsCollection        import MongoStampCommentsCollection

from api.db.mongodb.MongoStampCollection                import MongoStampCollection
from api.db.mongodb.MongoEntityCollection               import MongoEntityCollection

import gevent
from gevent.queue import Queue, Empty

collections = [
    # Indexes 
    # MongoInboxStampsCollection, 
    # MongoCreditReceivedCollection, 
    # MongoStampCommentsCollection, 
    # MongoUserLikesCollection, 
    # MongoUserStampsCollection, 
    # MongoUserTodosEntitiesCollection, 

    # Documents
    # MongoStampCollection,
    MongoEntityCollection,
]


def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    # parser.add_option("-d", "--db", default=None, type="string", 
    #     action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, 
        action="store_true", help="noop mode (don't apply fixes)")
    
    parser.add_option("-c", "--check", default=None, 
        action="store", help="optionally filter checks based off of their name")
    
    # parser.add_option("-s", "--sampleSetSize", default=None, type="int", 
    #     action="store", help="sample size as a percentage (e.g., 5 for 5%)")
    
    (options, args) = parser.parse_args()
    
    # if options.sampleSetSize is None:
    #     options.sampleSetRatio = 1.0
    # else:
    #     options.sampleSetRatio = options.sampleSetSize / 100.0
    
    # if options.db:
    #     utils.init_db_config(options.db)
    
    return (options, args)

documentIds = Queue(maxsize=10)

stats = {
    'passed': 0,
}

def worker(db, collection, stats):
    try:
        while True:
            documentId = documentIds.get(timeout=1) # decrements queue size by 1
            
            try:
                result = db.checkIntegrity(documentId, repair=True)
                print documentId, 'PASS'
                stats['passed'] += 1
            except NotImplementedError:
                logs.warning("WARNING: Collection '%s' not implemented" % collection.__name__)
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
            except StampedStaleRelationshipKeyError:
                print documentId, 'FAIL: Key deleted'
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
            except StampedStaleRelationshipDataError:
                print documentId, 'FAIL: References updated'
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
            except StampedDataError as e:
                print documentId, 'FAIL'
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
            except Exception as e:
                print documentId, 'FAIL: %s (%s)' % (e.__class__, e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                f = traceback.format_exception(exc_type, exc_value, exc_traceback)
                f = string.joinfields(f, '')
                print f
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1

    except Empty:
        print('Quitting time!')

def handler(db):
        # for i in db._collection.find({'user.user_id': '4e570489ccc2175fcd000000'}, fields=['_id']).limit(1000):
        for i in db._collection.find(fields=['_id']):
            documentIds.put(i['_id'])


for collection in collections:
    logs.info("Running checks for %s" % collection.__name__)
    db = collection()
    gevent.joinall([
        gevent.spawn(handler, db),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
        gevent.spawn(worker, db, collection, stats),
    ])

passed = stats.pop('passed', 0)
total = passed

print ('='*80)
print '%40s: %s' % ('PASSED', passed)
for k, v in stats.items():
    print '%40s: %s' % (k, v)
    total += int(v)
print ('-'*80)
print '%40s: %s%s' % ('RATIO', int(100.0*passed/total*1.0), '%')

"""
def main():
    pass

def mainOld():
    options, args = parseCommandLine()

    # Verify that existing documents are valid
    for collection in collections:
        logs.info("Running checks for %s" % collection.__name__)
        db = collection()
        begin = time.time()
        # for i in db._collection.find({'user.user_id': '4e570489ccc2175fcd000000'}, fields=['_id']).limit(1000):
        for i in db._collection.find(fields=['_id']).limit(100):
            print '%s' % ('='*40)
            try:
                result = db.checkIntegrity(i['_id'], repair=(not options.noop))
                print i['_id'], 'PASS'
            except NotImplementedError:
                logs.warning("WARNING: Collection '%s' not implemented" % collection.__name__)
                break
            except StampedStaleRelationshipKeyError:
                print i['_id'], 'FAIL: Key deleted'
            except StampedStaleRelationshipDataError:
                print i['_id'], 'FAIL: References updated'
            except StampedDataError:
                print i['_id'], 'FAIL'
            except Exception as e:
                print i['_id'], 'FAIL: %s (%s)' % (e.__class__, e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                f = traceback.format_exception(exc_type, exc_value, exc_traceback)
                f = string.joinfields(f, '')
                print f
                break

        logs.info("Completed checks for %s (%s seconds)" % (collection.__name__, (time.time() - begin)))

    # TODO: Repopulate missing documents

if __name__ == '__main__':
    main()
"""