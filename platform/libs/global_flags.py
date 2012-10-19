#!/usr/bin/env python

"""
Global flags parsing for a few generally useful options.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'parse_global_flags', 'global_flags' ]

import argparse
import sys

__global_flags = None


def is_bowser():
    import ec2_utils
    stack = ec2_utils.get_stack()
    return stack and str(stack['instance']['stack']) == 'bowser'


def parse_global_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--enable_type_checking', action='store_true', default=is_bowser())
    global __global_flags
    __global_flags, new_argv = parser.parse_known_args(sys.argv)
    sys.argv[:] = new_argv[:]


def get_global_flags():
    return __global_flags