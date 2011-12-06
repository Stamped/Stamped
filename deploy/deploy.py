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
    # CRUD
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
    
    parser.add_option("-l", "--local", action="store_true", dest="local", 
        default=False, help="Run all commands locally (defaults to AWS)")
    
    parser.add_option("-a", "--aws", action="store_false", dest="local", 
        default=False, help="Run all commands locally on AWS")
    
    parser.add_option("-i", "--ip", action="store_true", dest="ip", 
        default=False, help="Associate elastic ip address with instance (for 'init' method)")
    
    parser.add_option("-r", "--restore", action="store", dest="restore", 
        default=None, type="string", help="Instance ID to restore snapshot from")
    
    parser.add_option("-p", "--params", action="store", dest="params", 
        default="", type="string", help="Params to pass when creating a new stack")
    
    (options, args) = parser.parse_args()
    args = map(lambda arg: arg.lower(), args)
    
    if len(args) < 1 or not args[0] in available_commands:
        print "Error: must provide a command from the list of available commands:"
        for command in available_commands:
            print "   %s" % command
        
        parser.print_help()
        sys.exit(1)
    else:
        if options.local:
            options.deployment = 'local'
        else:
            options.deployment = 'aws'
    
    return (options, args)

def main():
    # parse commandline
    (options, args) = parseCommandLine()
    
    deployments = {
        'aws'   : AWSDeploymentSystem, 
        'local' : LocalDeploymentSystem, 
    }
    
    deploymentSystemClass = deployments[options.deployment]
    deploymentSystem = deploymentSystemClass(deploymentSystemClass.__name__, options)
    
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

