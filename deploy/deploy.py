#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import os, sys, utils
from optparse import OptionParser

from deployments import AWSDeploymentSystem, LocalDeploymentSystem
from errors import Fail

available_commands = set([
    # crud
    'create', 
    'list', 
    'update', 
    'delete', 
    
    # node management
    'add', 
    'repair', 
    'force_db_primary_change', 
    'remove_db_node', 
    
    # utilities
    'bootstrap', 
    'crawl', 
    'stress', 
    'setup_crawler_data', 
    'backup', 
])

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="enable verbose logging")
    
    parser.add_option("-n", "--noop", action="store_true", default=False, 
                      help="enable dry run noop mode, where no actual action will be taken (useful to test & debug commands before running them for real)")
    
    (options, args) = parser.parse_args()
    args = map(lambda arg: arg.lower(), args)
    
    if len(args) < 1 or not args[0] in available_commands:
        print "Error: must provide a command from the list of available commands:"
        for command in available_commands:
            print "   %s" % command
        
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

def main():
    # parse commandline
    (options, args) = parseCommandLine()
    
    deploymentSystem = AWSDeploymentSystem(AWSDeploymentSystem.__name__, options)
    command = args[0]
    
    func = getattr(deploymentSystem, command, None)
    if func is None:
        raise Fail("'%s' does not support command '%s'" % (deploymentSystem, command))
    
    try:
        func(*args[1:])
    except Exception:
        utils.log("Error: command '%s' on '%s' failed" % (command, deploymentSystem))
        raise

if __name__ == '__main__':
    main()

