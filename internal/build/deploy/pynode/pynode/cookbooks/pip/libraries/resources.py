#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "PipPackage" ]

from pynode.resource import *

class PipPackage(Resource):
    _schema = ResourceArgumentSchema([
        ("name",       ResourceArgument(required=True, 
                                        expectedType=basestring)), 
        ("action",     ResourceArgumentList(default="install", 
                                            options=[ "install", "upgrade", "remove" ])), 
        ("version",    ResourceArgument(expectedType=basestring)), 
        ("virtualenv", ResourceArgument(expectedType=basestring)), 
        ("provider",   ResourceArgument(default="*pip.PipPackageProvider", 
                                        expectedType=basestring)), 
    ])

