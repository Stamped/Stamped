#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import sys
import signal, os
import subprocess

count = sys.argv[1]
args = sys.argv[2:]

processes = []
for i in range(int(count)):
    p = subprocess.Popen(args)
    processes.append(p)

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    for p in processes:
        p.terminate()

signal.signal(signal.SIGTERM, handler)

for p in processes:
    p.wait()
