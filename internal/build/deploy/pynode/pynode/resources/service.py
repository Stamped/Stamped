#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "Service" ]

from pynode.resource import *

class Service(Resource):
    _schema = ResourceArgumentSchema([
        ("name",             ResourceArgument(required=True, expectedType=basestring)), 
        ("enabled",          ResourceArgumentBoolean()), 
        ("running",          ResourceArgumentBoolean()), 
        ("pattern",          ResourceArgumentBoolean()), 
        ("start_cmd",        ResourceArgument(expectedType=basestring)), 
        ("reload_cmd",       ResourceArgument(expectedType=basestring)), 
        ("restart_cmd",      ResourceArgument(expectedType=basestring)), 
        ("status_cmd",       ResourceArgument(expectedType=basestring)), 
        ("supports_restart", ResourceArgumentBoolean(default=lambda r: r.restart_cmd is not None)), 
        ("supports_reload",  ResourceArgumentBoolean(default=lambda r: r.reload_cmd is not None)), 
        ("supports_status",  ResourceArgumentBoolean(default=lambda r: r.status_cmd is not None)), 
    ])

