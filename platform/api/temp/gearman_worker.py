from gevent import monkey
monkey.patch_all()

import gearman, gevent, time, pickle
from gevent.queue import Queue, Empty, Full

NUM_WORKERS = 3

queue = Queue(NUM_WORKERS)

# Basic gevent worker
def gworker():
    while True:
        i = queue.get()
        print 'Running %s(*args=%s, **kwargs=%s)' % (i['fn'], i['args'], i['kwargs'])
        for j in range(5):
            print j
            gevent.sleep(2)

# Basic function for gearman to add to a gevent queue
def addToApiQueue(worker, job):
    data = pickle.loads(job.data)
    print 'Grabbing %s' % data['fn']
    while True:
        try:
            queue.put(data)
            break
        except Full:
            gevent.sleep(0)
    
    return job.data

# Register a gearman worker
def handler():
    worker = gearman.GearmanWorker(['localhost:4730'])
    worker.register_task('apiQueue', addToApiQueue)
    worker.work()

# Spawn handler and workers
greenlets = [ gevent.spawn(handler) ]
for i in range(NUM_WORKERS):
    greenlets.append(gevent.spawn(gworker))

gevent.joinall(greenlets)
