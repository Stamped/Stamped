from gevent import monkey
monkey.patch_all()

import gearman, gevent, time, pickle
from gevent.queue import Queue, Empty, Full

import Globals

from MongoStampedAPI import globalMongoStampedAPI


# Basic function for gearman to add to a gevent queue
def addToApiQueue(worker, job):
    
    print('handled')
    return job.data

# Register a gearman worker
def handler():
    worker = gearman.GearmanWorker(['localhost:4730'])
    worker.register_task('apiQueue', addToApiQueue)
    worker.work()

def enterWorkLoop(functions):
    worker = gearman.GearmanWorker(['localhost:4730'])
    for k,v in functions.items():
        worker.register_task(k, v)
    worker.work()

if __name__ == '__main__':
    # Spawn handler and workers
    handler()

