#!/usr/bin/python

import sys, time, traceback, urllib2

from BeautifulSoup import BeautifulSoup

def Log(s):
    # TODO: look into logging module with logging.basicConfig(format="%(threadName)s:%(message)s")
    print str(s)

def Write(s, n):
    """
        Simple debug utility to write a string out to a file.
    """
    if n is None:
        n = "t"
    f = open(n, "w")
    f.write(s)
    f.close()

def HandleException():
    """
        Simple debug utility to print a stack trace.
    """
    traceback.print_exc()

def GetFile(url):
    """
        Wrapper around urllib2.urlopen(url).read(), which attempts to increase 
        the success rate by sidestepping server-side issues and usage limits by
        retrying unsuccessful attempts with increasing delays between retries, 
        capped at a maximum possibly delay, after which the request will simply
        fail and propagate any exceptions normally.
    """
    
    maxDelay = 64
    delay = 0.5
    html = ""
    
    while True:
        try:
            html = urllib2.urlopen(url).read()
            break
        except IOError:
            # encountered error GETing document. delay for a bit and try again,
            # or if delay is already too large, request will likely not 
            # complete successfully, so propagate the error and return.
            if delay > maxDelay:
                raise
            
            Log("Encountered IOError fetching url '" + url + "'")
            Log("Attempting to recover with delay of %d" % delay)
            
            # put the current thread to sleep for a bit, increase the delay, 
            # and retry the request
            time.sleep(delay)
            delay *= 2
    
    # return the successfully parsed html
    return html

def GetSoup(url):
    return BeautifulSoup(GetFile(url))

