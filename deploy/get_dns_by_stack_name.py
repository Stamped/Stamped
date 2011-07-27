#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from boto.ec2.connection import EC2Connection
from optparse import OptionParser
import sys

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

def parseCommandLine():
    usage   = "Usage: %prog [options] stack-name"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-t", "--tag", action="store", dest="tag", type="string", 
        default=None, help="Specify a tag to find on an instance within the given stack-name")
    
    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        options.stackName = None
    else:
        options.stackName = args[0].lower()
    
    return options

def main():
    options = parseCommandLine()
    if options is None:
        return
    
    conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
    reservations = conn.get_all_instances()
    
    for reservation in reservations:
        for instance in reservation.instances:
            #from pprint import pprint
            #pprint(instance.__dict__)
            
            if 'stack' in instance.tags:
                stackName = instance.tags['stack']
                
                if options.stackName is None or stackName.lower() == options.stackName:
                    if not options.tag or \
                        ('roles' in instance.tags and options.tag in instance.tags['roles'].lower())
                        print instance.public_dns_name
                        sys.exit(0)
    
    print "error: unable to find instance matching stack-name '%s'" % options.stackName
    sys.exit(1)

if __name__ == '__main__':
    main()

