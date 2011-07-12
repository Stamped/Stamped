#!/usr/bin/env python

__author__  = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"
__all__     = [ "Package" ]

import pynode.Utils
from pynode.Resource import *




# TODO: how to specify provider s.t. python packages may be listed 
# before external dependencies such as libevent before gevent?



class Package(Resource):
    _schema = {
        "name"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "action"    : ResourceArgumentList(default="install", 
                                           options=[ "install", "upgrade", "remove" ]), 
        "version"   : ResourceArgument(expectedType=basestring), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

class PythonPackage(Resource):
    _schema = {
        "name"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "action"    : ResourceArgumentList(default="install", 
                                           options=[ "install", "upgrade", "remove" ]), 
        "version"   : ResourceArgument(expectedType=basestring), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

