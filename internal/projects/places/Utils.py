#!/usr/bin/python

import sys, traceback

def Log(s):
    # TODO: look into logging module with logging.basicConfig(format="%(threadName)s:%(message)s")
    print str(s)

def Write(s, n):
    if n is None:
        n = "t"
    f = open(n, "w")
    f.write(s)
    f.close()

def HandleException():
    traceback.print_exc()

