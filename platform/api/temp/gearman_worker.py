from gevent import monkey
monkey.patch_all()

import Globals

import gearman, gevent, time, pickle
import sys


# Basic function for gearman to add to a gevent queue
def addToApiQueue(key, data):
    print('handled: %s : %s' % (key, data))

def enterWorkLoop(functions):
    worker = gearman.GearmanWorker(['localhost:4730'])
    for k,v in functions.items():
        def wrapper(worker, job):
            data = pickle.loads(job.data)
            print(k,v)
            v(k, data)
            return ''
        print "registering for %s" % k
        worker.register_task(k, wrapper)
    worker.work()

def enrichTasks():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    # tasks = [
    #     api.mergeEntityAsync,
    #     api.mergeEntityIdAsync,
    # ]
    m = {}
    def mergeEntityAsyncHelper(key, data):
        api.mergeEntityAsync(data['entityDict'])
    m[api.taskName(api.mergeEntityAsync)] = mergeEntityAsyncHelper

    def mergeEntityIdAsyncHelper(key, data):
        api.mergeEntityIdAsync(data['entity_id'])
    m[api.taskName(api.mergeEntityIdAsync)] = mergeEntityIdAsyncHelper

    # for task in tasks:

        # m[api.taskName(task)] = lambda task
    return m

if __name__ == '__main__':
    enterWorkLoop(enrichTasks())

