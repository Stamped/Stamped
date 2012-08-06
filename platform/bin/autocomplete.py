#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import json, re, sys, string, urllib2, utils

from optparse import OptionParser
from pprint   import pprint

#-----------------------------------------------------------

class Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        self.impl = _GetchUnix()
    
    def __call__(self):
        return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys
    
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return ch

def parseCommandLine():
    usage   = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    (options, args) = parser.parse_args()
    return (options, args)

def encode_s3_name(name):
    name = name.lower().replace(' ', '_').encode('ascii', 'ignore')
    name = re.sub('([^a-zA-Z0-9._-])', '', name)
    return name

def main():
    options, args = parseCommandLine()
    
    getch = Getch()
    query = ''
    while True:
        diff = False
        ch = getch()
        
        if ch == '\x04': # EOF
            break
        elif ch == '\x7f': # backspace
            if len(query) > 0:
                query = query[:-1]
                diff  = True
        elif ch in string.ascii_letters or ch in string.digits or ch == ' ' or ch == '.' or ch == '-':
            query = query + ch
            diff  = True
        
        if diff:
            print query
            try:
                raw_result = utils.getFile('http://static.stamped.com/search/v2/%s.json.gz' % encode_s3_name(query))
            except urllib2.HTTPError:
                # ignore errors in the (likely) event of a non-existent autocomplete file
                continue
            
            if raw_result:
                results = json.loads(raw_result)
                
                for i in xrange(min(10, len(results))):
                    result = results[i]
                    print "%d) %s (%s - %s)" % (i + 1, result['title'], result['subtitle'], result['category'])

if __name__ == '__main__':
    main()

