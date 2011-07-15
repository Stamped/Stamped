#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, sys, utils
from optparse import OptionParser

from deployments.aws import AWSDeploymentSystem, AWSDeploymentStack
from errors import Fail

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-l", "--local", action="store_true", dest="local", 
        default=False, help="Run all commands locally (defaults to AWS)")
    
    (options, args) = parser.parse_args()
    
    commands = [
        'create_stack', 
        'delete_stack', 
        'describe_stack', 
        'describe_stack_events', 
        'connect_stack', 
        'list_stacks', 
    ]
    
    if len(args) < 1:
        print "Error: must provide at least one command"
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
    deploymentSystem = deploymentSystemClass(deploymentSystemClass.__name__)
    
    func = getattr(deploymentSystem, args[0], None)
    if func is None:
        raise Fail("'%s' does not support command '%s'" % (deploymentSystem, args[0]))
    
    try:
        func(*args[1:])
    except Exception:
        utils.log("Error: command '%s' on '%s' failed" % (args[0], deploymentSystem))
        raise

if __name__ == '__main__':
    main()

