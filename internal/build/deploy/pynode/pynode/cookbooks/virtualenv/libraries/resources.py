#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "VirtualEnv" ]

from pynode.resource import *

class VirtualEnv(Resource):
    _schema = ResourceArgumentSchema([
        ("path",               ResourceArgument(required=True, 
                                                expectedType=basestring)), 
        ("action",             ResourceArgumentList(default=[ "create", "activate" ], 
                                                    options=[ "create", "activate", "delete" ])), 
        ("site_packages",      ResourceArgumentBoolean(default=True)), 
        ("clear",              ResourceArgumentBoolean(default=False)), 
        ("unzip_setuptools",   ResourceArgumentBoolean(default=False)), 
        ("use_distribute",     ResourceArgumentBoolean(default=False)), 
        ("never_download",     ResourceArgumentBoolean(default=False)), 
        ("name",               ResourceArgument(default=lambda r: r['path'], 
                                                expectedType=basestring)), 
        ("provider",           ResourceArgument(default="*virtualenv.VirtualEnvProvider", 
                                                expectedType=basestring)), 
    ])

