#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import sys, traceback, string, random
import logs, utils, time, bson
import libs.ec2_utils

from errors                 import *
from optparse               import OptionParser

from api.MongoStampedAPI import MongoStampedAPI

from api.db.mongodb.MongoInboxStampsCollection          import MongoInboxStampsCollection
from api.db.mongodb.MongoUserStampsCollection           import MongoUserStampsCollection
from api.db.mongodb.MongoCreditReceivedCollection       import MongoCreditReceivedCollection
from api.db.mongodb.MongoUserLikesCollection            import MongoUserLikesCollection
from api.db.mongodb.MongoUserTodosEntitiesCollection    import MongoUserTodosEntitiesCollection
from api.db.mongodb.MongoStampCommentsCollection        import MongoStampCommentsCollection

from api.db.mongodb.MongoAccountCollection              import MongoAccountCollection
from api.db.mongodb.MongoEntityCollection               import MongoEntityCollection, MongoEntityStatsCollection
from api.db.mongodb.MongoStampCollection                import MongoStampCollection, MongoStampStatsCollection
from api.db.mongodb.MongoTodoCollection                 import MongoTodoCollection

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
    MongoAccountCollection,
    MongoEntityCollection,
    MongoStampCollection,
    MongoTodoCollection,

    # Stats
    MongoEntityStatsCollection,
    MongoStampStatsCollection, 
]

WORKER_COUNT = 10

api = MongoStampedAPI()


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
    
    parser.add_option("-s", "--sampleSetSize", default=None, type="int", 
        action="store", help="sample size as a percentage (e.g., 5 for 5%)")
    
    (options, args) = parser.parse_args()
    
    if options.sampleSetSize is None:
        options.sampleSetRatio = 1.0
    else:
        options.sampleSetRatio = options.sampleSetSize / 100.0
    
    # if options.db:
    #     utils.init_db_config(options.db)
    
    return (options, args)

documentIds = Queue(maxsize=10)

def worker(db, collection, api, stats, options):
    try:
        while True:
            documentId = documentIds.get(timeout=2) # decrements queue size by 1
            
            try:
                result = db.checkIntegrity(documentId, repair=(not options.noop), api=api)
                stats['passed'] += 1

            except NotImplementedError:
                logs.warning("WARNING: Collection '%s' not implemented" % collection.__name__)
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1

            except StampedDataError as e:
                logs.warning("%s: FAIL" % documentId)
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
                stats['errors'].append(e)

            except Exception as e:
                logs.warning("%s: FAIL: %s (%s)" % (documentId, e.__class__, e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                f = traceback.format_exception(exc_type, exc_value, exc_traceback)
                f = string.joinfields(f, '')
                print f
                stats[e.__class__.__name__] = stats.setdefault(e.__class__.__name__, 0) + 1
                stats['errors'].append(e)

    except Empty:
        print('Done!')

def handler(db, options):
    query = {}
    # query = {'_id': bson.objectid.ObjectId("4e4c691ddb6bbe2bcd00034d")}
    for i in db._collection.find(query, fields=['_id']):
        if options.sampleSetRatio < 1 and random.random() > options.sampleSetRatio:
            continue
        documentIds.put(i['_id'])


def main():
    options, args = parseCommandLine()

    warnings = {}

    # Verify that existing documents are valid
    for collection in collections:
        logs.info("Running checks for %s" % collection.__name__)
        db = collection()
        begin = time.time()

        stats = {
            'passed': 0,
            'errors': [],
        }

        # Build handler
        greenlets = [ gevent.spawn(handler, db, options) ]

        # Build workers
        for i in range(WORKER_COUNT):
            greenlets.append(gevent.spawn(worker, db, collection, api, stats, options))

        # Run!
        gevent.joinall(greenlets)

        passed = stats.pop('passed', 0)
        errors = stats.pop('errors', [])
        total = passed

        print ('='*80)
        print '%40s: %s' % ('PASSED', passed)
        for k, v in stats.items():
            print '%40s: %s' % (k, v)
            total += int(v)
        print ('-'*80)
        print '%40s: %s%s Accuracy (%.2f seconds)' % (collection.__name__, int(100.0*passed/total*1.0), '%', (time.time()-begin))
        print 

        if len(errors) > 0:
            warnings[collection.__name__] = errors

            for error in errors:
                print error 
            print 

    # TODO: Repopulate missing documents

    # Email dev if any errors come up
    if libs.ec2_utils.is_ec2():
        if len(warnings) > 0:
            try:
                stack = libs.ec2_utils.get_stack().instance.stack
                email = {}
                email['from'] = 'Stamped <noreply@stamped.com>'
                email['to'] = 'dev@stamped.com'
                email['subject'] = '%s: Integrity Checker Failure' % stack

                html = '<html><body><p>Integrity checker caught the following errors:</p>'
                for k, v in warnings.iteritems():
                    html += '<hr><h3>%s</h3>' % k 
                    for e in v:
                        html += ('<p><code>%s</code></p>' % e).replace('\n','<br>')
                html += '</body></html>'

                email['body'] = html
                utils.sendEmail(email, format='html')
            except Exception as e:
                logs.warning('UNABLE TO SEND EMAIL: %s' % e)

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
