#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

"""
Defines a decorator that counts the number of invocations of a function.
"""

import utils, functools, collections

functionCounts = collections.defaultdict(int)

def countedFn(name=None, devOnly=True):
    def decoratorFn(userFn):
        if devOnly and utils.is_ec2():
            return userFn

        @functools.wraps(userFn)
        def wrappedFn(*args, **kwargs):
            global functionCounts
            fnName = name if name is not None else userFn.__name__
            functionCounts[fnName] += 1
            return userFn(*args, **kwargs)

        return wrappedFn

    return decoratorFn


def printFunctionCounts():
    functionsAndCounts = functionCounts.items()
    functionsAndCounts.sort(key=lambda (function, count): count, reverse=True)
    print "\n\nFUNCTION COUNTS\n\n"
    print "<Function Name>\t\t<Count>"
    for (function, count) in functionsAndCounts:
        print function, "\t\t", count
    print "\n\n"
