#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from boto.ec2.connection import EC2Connection
from optparse import OptionParser
import sys

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_ACCESS_KEY_SECRET = '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'

def parseCommandLine():
    usage   = "Usage: %prog [options] stack-name"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
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
    
    conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_ACCESS_KEY_SECRET)
    reservations = conn.get_all_instances()
    stackNameKey = 'aws:cloudformation:stack-name'
    found = False
    
    for reservation in reservations:
        for instance in reservation.instances:
            #from pprint import pprint
            #pprint(instance.__dict__)
            
            if stackNameKey in instance.tags:
                stackName = instance.tags[stackNameKey]
                
                if options.stackName is None or stackName.lower() == options.stackName:
                    found = True
                    print instance.public_dns_name
    
    if not found:
        print "error: unable to find instance matching stack-name"
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

