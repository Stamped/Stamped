from gevent import monkey
monkey.patch_all()

import Globals

import gearman, gevent, time, pickle

# Basic function for gearman to add to a gevent queue
def addToApiQueue(worker, job):
    print('handled')

def enterWorkLoop(functions):
    worker = gearman.GearmanWorker(['localhost:4730'])
    for k,v in functions.items():
        worker.register_task(k, v)
    worker.work()

if __name__ == '__main__':
    enterWorkLoop({'apiQueue': addToApiQueue})
