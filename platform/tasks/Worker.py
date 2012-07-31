from gevent import monkey
monkey.patch_all()

import Globals

import gearman, gevent, time, pickle
import sys
import logs
import libs.ec2_utils
import random
import utils

import signal, os

from datetime import datetime

class StampedWorker(gearman.GearmanWorker):

    killed = False

    def __init__(self, host):
        gearman.GearmanWorker.__init__(self, host)

    def after_poll(self, any_activity):
        return not StampedWorker.killed

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    StampedWorker.killed = True

signal.signal(signal.SIGTERM, handler)

def getHosts():
    stack = libs.ec2_utils.get_stack()

    if stack is None:
        return ['localhost:4730']

    hosts = []
    for node in stack['nodes']:
        if 'broker' in node['roles'] or 'monitor' in node['roles']: # TEMP: monitor is deprecated
            hosts.append("%s:4730" % node['private_ip_address'])

    assert len(hosts) > 0

    return hosts
    
def enterWorkLoop(functions):
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    worker = StampedWorker(getHosts())
    def wrapper(worker, job):
        k = 'not parsed yet'
        request_num = 'not yet parsed'
        try:
            job_data = pickle.loads(job.data)
            k = job_data['key']
            request_num = job_data['task_id']
            logs.begin(saveLog=api._logsDB.saveLog,
                       saveStat=api._statsDB.addStat,
                       nodeName=api.node_name)
            logs.async_request(k)
            data = job_data['data']
            logs.info("Request %s: %s: %s" % (request_num, k, data))
            if functions is not None:
                v = functions[k]
                v(k, data)
            else:
                fnName = k.split('::')[1]
                v = getattr(api, fnName)
                v(**data)
            logs.info("Finished with request %s" % (request_num,))

        except Exception as e:
            logs.error("Failed request %s" % (request_num,))
            logs.report()

            if libs.ec2_utils.is_ec2():
                try:
                    email = {}
                    email['from'] = 'Stamped <noreply@stamped.com>'
                    email['to'] = 'dev@stamped.com'
                    email['subject'] = '%s - Failed Async Task - %s - %s' % (api.node_name, k, datetime.utcnow().isoformat())
                    email['body'] = logs.getHtmlFormattedLog()
                    utils.sendEmail(email, format='html')
                except Exception as e:
                    logs.warning('UNABLE TO SEND EMAIL: %s' % e)

        finally:
            logs.info('Saving request log for request %s' % (request_num,))
            try:
                logs.save()
            except Exception:
                print 'Unable to save logs'
                import traceback
                traceback.print_exc()
                logs.warning(traceback.format_exc())

        return ''
    queues = set()
    if functions is not None:
        for k,v in functions.items():
            queue = k.split('::')[0]
            queues.add(queue)
    else:
        queues.add('api')
    for k in queues:
        worker.register_task(k, wrapper)
    worker.work(poll_timeout=1)

def main(functions=None, api=False):
    enterWorkLoop(functions)


def enrichTasks():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    m = {}
    def mergeEntityAsyncHelper(key, data):
        api.mergeEntityAsync(data['entityDict'])
    m[api.taskKey('enrich', api.mergeEntityAsync)] = mergeEntityAsyncHelper

    def mergeEntityIdAsyncHelper(key, data):
        api.mergeEntityIdAsync(data['entityId'])
    m[api.taskKey('enrich', api.mergeEntityIdAsync)] = mergeEntityIdAsyncHelper
    return m

################
### TEST STUFF
################

def findAmicablePairsNaive(n):
    def sumOfDivisors(i):
        s = 0
        for j in range(1, i):
            if i % j == 0:
                s += j
        return s
    results = []
    for i in range(n):
        for j in range(i):
            if sumOfDivisors(i) == j and i == sumOfDivisors(j):
                results.append((i, j))
    print results

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import keys.aws
from contextlib import closing
import datetime

def getS3Key(filename):
    BUCKET_NAME = 'stamped.com.static.images'

    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    bucket = conn.create_bucket(BUCKET_NAME)
    key = bucket.get_key(filename)
    if key is None:
        key = bucket.new_key(filename)
    return key

def writeTimestampToS3(s3_filename, request_id=""):
    logs.debug('Writing timestamp to S3 file %s' % s3_filename)
    file_content = '%s: %s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id)
    delay = 0.1
    max_delay = 3
    max_tries = 40
    for i in range(max_tries):
        try:
            with closing(getS3Key(s3_filename)) as key:
                key.set_contents_from_string(file_content)
                key.set_acl('private')
                return
        except:
            time.sleep(delay)
            delay = min(max_delay, delay*1.5)
    raise Exception('Failed 40 fucking times. How does that even happen.')


def testTasks():
    def writeTimestampToS3Helper(key, data):
        writeTimestampToS3(data['s3_filename'], data.get('request_id', ''))
    def findAmicablePairsNaiveHelper(key, data):
        findAmicablePairsNaive(data['n'])
    return {
        'writeTimestampToS3' : writeTimestampToS3Helper,
        'findAmicablePairsNaive' : findAmicablePairsNaiveHelper
    }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Must provide a queue'
        sys.exit(1)
    # All workers have test tasks enabled.
    arg = sys.argv[1]
    if arg == 'enrich':
        main(functions = enrichTasks(), api=False)
    elif arg == 'api':
        main(functions = None, api=True)
    else:
        print "Unrecognized queue"


