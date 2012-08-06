from __future__ import absolute_import
import Globals

# For core gearman functionality
import gearman, gevent, pickle
import libs.ec2_utils

# For signal handling
import signal, os

# For logging
from datetime import datetime
import logs
import utils
import traceback
import time

# For arg handling
import sys


import sys
import signal, os
import subprocess

class MetaWorker(object):

    def __init__(self, count, args):
        object.__init__(self)
        self.__shutdown = False
        self.__count = count
        self.__args = args
        if count <= 0:
            raise ValueError('count must not be > 0')
        signal.signal(signal.SIGTERM, self.signalHandler)

    def work(self):
        self.__processes = []
        sleep_time = 5 * 60
        last_sleep = time.time()
        while not self.__shutdown:
            if len(self.__processes) == self.__count:
                p = self.__processes.pop(0)
                p.terminate()
                exitstatus = p.wait()
                if exitstatus != -15:
                    print 'Problem!!!! %s' % exitstatus
                for p in self.__processes:
                    returnstatus = p.poll()
                    if returnstatus is not None:
                        if returnstatus == 0 and self.__shutdown:
                            #ignore
                            pass
                        else:
                            logs.warning('Process exited with code %s'  % returnstatus)
                sleep_until = last_sleep + sleep_time
                while True:
                    sleep_remaining = sleep_until - time.time()
                    if sleep_remaining > 0:
                        time.sleep(min(sleep_remaining, 2))
                    else:
                        break
                last_sleep = time.time()
            else:
                print 'adding process %i' % len(self.__processes)
                self.addProcess()
        for p in self.__processes:
            print 'killing process %i' % len(self.__processes)
            p.terminate()
        for p in self.__processes:
            p.wait()

    def addProcess(self):
        p = subprocess.Popen(self.__args)
        self.__processes.append(p)

    def signalHandler(self, signum, frame):
        print 'Signal handler called with signal', signum
        self.__shutdown = True

if __name__ == '__main__':
    count = int(sys.argv[1])
    args = sys.argv[2:]
    worker = MetaWorker(count, args)
    worker.work()


