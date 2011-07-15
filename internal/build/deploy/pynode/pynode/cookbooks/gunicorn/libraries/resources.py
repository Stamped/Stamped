#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "GreenUnicornConfigFile" ]

from pynode.resource import *

class GreenUnicornConfigFile(Resource):
    _schema = ResourceArgumentSchema([
        ("path",                ResourceArgument(required=True, 
                                                 expectedType=basestring)), 
        ("action",              ResourceArgumentList(default="create", 
                                                     options=[ "create", "delete" ])), 
        ("template",            ResourceArgument(required=True, 
                                                 expectedType=basestring)), 
        ("listen",              ResourceArgument(default="0.0.0.0:8000", 
                                                 expectedType=basestring)), 
        ("backlog",             ResourceArgument(default=2048, 
                                                 expectedType=int)), 
        ("preload_app",         ResourceArgumentBoolean(default=False)), 
        ("worker_processes",    ResourceArgument(default=4, 
                                                 expectedType=int)), 
        ("worker_class",        ResourceArgument(default='sync', 
                                                 expectedType=basestring)), 
        ("worker_timeout",      ResourceArgument(default=60, 
                                                 expectedType=int)), 
        ("worker_keepalive",    ResourceArgument(default=2, 
                                                 expectedType=int)), 
        ("worker_max_requests", ResourceArgument(default=0, 
                                                 expectedType=int)), 
        ("pid",                 ResourceArgument(expectedType=basestring)), 
        ("name",                ResourceArgument(default=lambda r: r['path'], 
                                                 expectedType=basestring)), 
        ("provider",            ResourceArgument(default="*gunicorn.GreenUnicornProvider", 
                                                 expectedType=basestring)), 
        
        """ TODO: support nested ResourceArgumentSchemas
        ("server_hooks",        ResourceArgument(expectedType=ResourceArgumentSchema, 
                                                 default=ResourceArgumentSchema([
            ('when_ready',      ResourceArgument(expectedType=basestring)), 
            ('pre_fork',        ResourceArgument(expectedType=basestring)), 
            ('post_fork',       ResourceArgument(expectedType=basestring)), 
            ('pre_exec',        ResourceArgument(expectedType=basestring)), 
            ('pre_request',     ResourceArgument(expectedType=basestring)), 
            ('post_request',    ResourceArgument(expectedType=basestring)), 
            ('worker_exit',     ResourceArgument(expectedType=basestring)), 
        ]))), 
        """
    ])

