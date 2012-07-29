from gevent import monkey
monkey.patch_all()

import Globals

import gearman, gevent, time, pickle
import sys
import logs

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

def enterWorkLoop(functions):
    worker = StampedWorker(['localhost:4730'])
    for k,v in functions.items():
        def wrapper(worker, job):
            try:
                logs.begin(saveLog=stampedAPI._logsDB.saveLog,
                           saveStat=stampedAPI._statsDB.addStat,
                           nodeName=stampedAPI.node_name)
                data = pickle.loads(job.data)
                logs.info("%s: %s" % (k, data))
                v(k, data)
            except Exception as e:
                logs.error(str(e))
            finally:
                try:
                    logs.save()
                except Exception:
                    print 'Unable to save logs'
                    import traceback
                    traceback.print_exc()
                    logs.warning(traceback.format_exc())
            return ''
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


if __name__ == '__main__':
    m = enrichTasks()
    m.update(apiTasks())
    main(10, m)


