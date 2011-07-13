#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "Package", "PythonPackage" ]

from pynode.resource import *

class Package(Resource):
    _schema = ResourceArgumentSchema([
        ("name",    ResourceArgument(required=True, expectedType=basestring)), 
        ("action",  ResourceArgumentList(default="install", 
                                         options=[ "install", "upgrade", "remove" ])), 
        ("version", ResourceArgument(expectedType=basestring)), 
    ])

class PythonPackage(Package):
    # the only difference between PythonPackage and Package by default is 
    # that pynode uses a different provider for PythonPackages as opposed 
    # to normal system packages. see Provider.getProvider for details.
    pass

