#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, time, traceback, urllib2

from BeautifulSoup import BeautifulSoup

def log(s):
    # TODO: look into logging module with logging.basicConfig(format="%(threadName)s:%(message)s")
    print unicode(str(s), "utf-8")

def write(s, n):
    """
        Simple debug utility to write a string out to a file.
    """
    if n is None:
        n = "t"
    f = open(n, "w")
    f.write(s)
    f.close()

def printException():
    """
        Simple debug utility to print a stack trace.
    """
    traceback.print_exc()

def getFile(url):
    """
        Wrapper around urllib2.urlopen(url).read(), which attempts to increase 
        the success rate by sidestepping server-side issues and usage limits by
        retrying unsuccessful attempts with increasing delays between retries, 
        capped at a maximum possibly delay, after which the request will simply
        fail and propagate any exceptions normally.
    """
    
    maxDelay = 64
    delay = 0.5
    html = None
    
    while True:
        try:
            html = urllib2.urlopen(url).read()
            break
        except urllib2.HTTPError, e:
            log("'%s' fetching url '%s'" % (str(e), url))
            
            # reraise the exception if the request resulted in an HTTP client 4xx error code, 
            # since it was a problem with the url / headers and retrying most likely won't 
            # solve the problem.
            if e.code >= 400 and e.code < 500:
                raise
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except IOError, e:
            log("Error '%s' fetching url '%s'" % (str(e), url))
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except Exception, e:
            log("Unexpected Error '%s' fetching url '%s'" % (str(e), url))
            printException()
            raise
        
        # encountered error GETing document. delay for a bit and try again
        log("Attempting to recover with delay of %d" % delay)
        
        # put the current thread to sleep for a bit, increase the delay, 
        # and retry the request
        time.sleep(delay)
        delay *= 2
    
    # return the successfully parsed html
    return html

def getSoup(url):
    return BeautifulSoup(getFile(url))

def createEnum(*sequential, **named):
    return dict(zip(sequential, range(len(sequential))), **named)

