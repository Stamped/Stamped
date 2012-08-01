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
