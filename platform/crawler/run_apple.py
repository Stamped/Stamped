#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import string, sys, time

from subprocess import Popen, PIPE
from optparse   import OptionParser
from pprint     import pprint

#-----------------------------------------------------------

def parseCommandLine():
    usage   = "Usage: %prog [options] num_processes"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run the dedupper in noop mode without modifying anything")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    valid = False
    if len(args) == 1:
        try:
            options.num = int(args[0])
            valid = True
        except:
            pass
    
    if not valid:
        parser.print_help()
        sys.exit(1)
    
    return options

def main():
    options = parseCommandLine()
    
    params = []
    if options.db is not None:
        params.append(" --db %s" % options.db)
    if options.noop:
        params.append(" -n")
    
    params = string.joinfields(params, ' ')
    procs  = []
    
    for i in xrange(options.num):
        output = "out.apple%d" % (i + 1, )
        cmd = "./apple.py %s -r %d/%d < /dev/null >& %s" % (params, i + 1, options.num, output)
        utils.log(cmd)
        
        proc = Popen(cmd, shell=True)
        procs.append(proc)
        time.sleep(i + 1)
    
    for proc in procs:
        proc.wait()

if __name__ == '__main__':
    main()

