#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import os, pickle, sys
from subprocess import Popen, PIPE
from optparse import OptionParser

def shell(cmd):
    pp = Popen(cmd, shell=True, stdout=PIPE)
    status = pp.wait()
    
    return status

def parse(source, params):
    try:
        from jinja2 import Template
    except ImportError:
        print "error: must install python module Jinja2"
        raise
    
    template = Template(source)
    return template.render(params)

def parse_file(src, params):
    return parse(src.read(), params)

def parseCommandLine():
    usage   = "Usage: %prog [[param1=value] [param2=value]...]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-t", "--template", action="store", dest="input", 
        default=None, help="Read input from given template file instead of stdin")
    
    parser.add_option("-o", "--output", action="store", dest="output", 
        default=None, help="Store output to given file instead of stdout")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    
    params = pickle.loads(args[0])
    
    """
    params = { }
    
    for arg in args:
        if not '=' in arg:
            print "error: invalid param=value arg '%s'" % arg
            parser.print_help()
            sys.exit(1)
        
        (name, value) = arg.split('=')
        params[name] = value
    """
    
    if options.input is None:
        options.input = sys.stdin
    else:
        options.input = open(options.input, 'r')
    if options.output is None:
        options.output = sys.stdout
    else:
        options.output = open(options.output, 'w')
    
    return (options, params)

def main():
    # parse commandline
    (options, params) = parseCommandLine()
    
    shell('easy_install Jinja2')
    output = parse_file(options.input, params)
    options.input.close()
    
    options.output.write(output)
    options.output.close()

if __name__ == '__main__':
    main()

