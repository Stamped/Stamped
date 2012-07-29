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
    print('asdfadsfasd')
    for k,v in functions.items():
        def wrapper(worker, job):
            data = pickle.loads(job.data)
            v(k, data)
            return ''
        print "registering for %s" % k
        worker.register_task(k, wrapper)
    worker.work()

def enrichTasks():
    m = {}
    

if __name__ == '__main__':
    enterWorkLoop({'test': addToApiQueue})

