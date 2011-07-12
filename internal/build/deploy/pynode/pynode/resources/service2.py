#!/usr/bin/env python

__author__  = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"
__all__     = [ "Service" ]

import pynode.Utils
from pynode.Resource import *

class Service(Resource):
    _schema = {
        "name"          : ResourceArgument(required=True, 
                                           expectedType=basestring), 
        "enabled"       : ResourceArgumentList(default="start", 
                                               options=[ "start", "stop", "restart", "reload" ]), 
        "running"       : ResourceArgument(expectedType=basestring), 
        "pattern"       : ResourceArgument(expectedType=basestring), 
        "start_cmd"     : ResourceArgument(expectedType=basestring), 
        "stop_cmd"      : ResourceArgument(expectedType=basestring), 
        "restart_cmd"   : ResourceArgument(expectedType=basestring), 
        "reload_cmd"    : ResourceArgument(expectedType=basestring), 
        "status_cmd"    : ResourceArgument(expectedType=basestring), 
        "supports_restart" : ResourceArgumentBoolean(
            default=lambda r: 'restart_cmd' in r and r['restart_cmd'] is not None), 
        "supports_reload" : ResourceArgumentBoolean(
            default=lambda r: 'reload_cmd' in r and r['reload_cmd'] is not None), 
        "supports_status" : ResourceArgumentBoolean(
            default=lambda r: 'status_cmd' in r and r['status_cmd'] is not None), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

