from gevent import monkey
monkey.patch_all()

import Globals

import gearman, gevent, time, pickle
import sys
import logs
import libs.ec2_utils
import random

import signal, os

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
    logs.info("starting worker for %s" % functions.keys())
    worker = StampedWorker(getHosts())
    def wrapper(worker, job):
        request_num = random.randint(1, 1 << 32)
        try:
            k = job.task
            logs.begin(saveLog=api._logsDB.saveLog,
                       saveStat=api._statsDB.addStat,
                       nodeName=api.node_name)
            logs.async_request(k)
            v = functions[k]
            data = pickle.loads(job.data)
            logs.info("Request %d: %s: %s: %s" % (request_num, k, v, data))
            v(k, data)
            logs.info("Finished with request %d" % (request_num,))
        except Exception as e:
            logs.error("Failed request %d" % (request_num,))
            logs.report()
        finally:
            logs.info('Saving request log for request %d' % (request_num,))
            try:
                logs.save()
            except Exception:
                print 'Unable to save logs'
                import traceback
                traceback.print_exc()
                logs.warning(traceback.format_exc())
        return ''
    for k,v in functions.items():
        worker.register_task(k, wrapper)
    worker.work(poll_timeout=1)

def main(count, functions):
    greenlets = []
    for i in range(count):
        greenlets.append(gevent.spawn(enterWorkLoop, functions))
    gevent.joinall(greenlets)

def enrichTasks():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    m = {}
    def mergeEntityAsyncHelper(key, data):
        api.mergeEntityAsync(data['entityDict'])
    m[api.taskName(api.mergeEntityAsync)] = mergeEntityAsyncHelper

    def mergeEntityIdAsyncHelper(key, data):
        api.mergeEntityIdAsync(data['entity_id'])
    m[api.taskName(api.mergeEntityIdAsync)] = mergeEntityIdAsyncHelper
    return m

def apiTasks():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    m = {}
    def customizeStampAsyncHelper(key, data):
        api.customizeStampAsync()
    m[api.taskName(api.customizeStampAsync)] = customizeStampAsyncHelper
    return m


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
        api.mergeEntityAsync(data['s3_filename'], data.get('request_id', ''))
    def findAmicablePairsNaiveHelper(key, data):
        api.mergeEntityAsync(data['n'])
    return {
        'writeTimestampToS3' : writeTimestampToS3Helper,
        'findAmicablePairsNaive' : findAmicablePairsNaiveHelper
    }

_functionSets = {
    'enrich': enrichTasks,
    'api': apiTasks,
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Must provide at least one function set (i.e. %s)' %  ','.join(_functionSets.keys())
        sys.exit(1)
    # All workers have test tasks enabled.
    m = testTasks()
    for k in sys.argv[1:]:
        if k in _functionSets:
            f = _functionSets[k]
            m.update(f())
        else:
            print("%s is not a valid function set" % k)
            sys.exit(1)
    main(10, m)


