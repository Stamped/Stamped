#!/usr/bin/env python

__author__  = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"
__all__     = [ "File", "Directory", "Link", "Execute", "Script" ]

import pynode.Utils
from pynode.Resource import *

class File(Resource):
    _schema = {
        "path"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "action"    : ResourceArgumentList(default="create", 
                                           options=[ "create", "delete", "touch" ]), 
        "backup"    : ResourceArgument(expectedType=basestring), 
        "mode"      : ResourceArgument(expectedType=int), 
        "owner"     : ResourceArgument(expectedType=basestring), 
        "group"     : ResourceArgument(expectedType=basestring), 
        "content"   : ResourceArgument(expectedType=basestring), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

class Directory(Resource):
    _schema = {
        "path"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "action"    : ResourceArgumentList(default="create", 
                                           options=[ "create", "delete" ]), 
        "mode"      : ResourceArgument(expectedType=int), 
        "owner"     : ResourceArgument(expectedType=basestring), 
        "group"     : ResourceArgument(expectedType=basestring), 
        "recursive" : ResourceArgumentBoolean(default=True), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

class Link(Resource):
    _schema = {
        "path"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "action"    : ResourceArgumentList(default="create", 
                                           options=[ "create", "delete" ]), 
        "to"        : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "hard"      : ResourceArgumentBoolean(default=False), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

class Execute(Resource):
    _schema = {
        "action"    : ResourceArgumentList(default="create", 
                                           options=[ "create", "delete" ]), 
        "command"   : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "creates"   : ResourceArgument(expectedType=basestring), 
        "cwd"       : ResourceArgument(expectedType=basestring), 
        "env"       : ResourceArgument(expectedType=dict), 
        "user"      : ResourceArgument(expectedType=basestring), 
        "group"     : ResourceArgument(expectedType=basestring), 
        "returns"   : ResourceArgumentList(default=0), 
        "timeout"   : ResourceArgument(default=-1, 
                                       expectedType=int)
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

class Script(Resource):
    _schema = {
        "action"    : ResourceArgumentList(default="run", 
                                           options=[ "run" ]), 
        "path"      : ResourceArgument(required=True, 
                                       expectedType=basestring), 
        "cwd"       : ResourceArgument(expectedType=basestring), 
        "env"       : ResourceArgument(expectedType=dict), 
        "shell"     : ResourceArgument(default="/bin/bash", 
                                       expectedType=basestring), 
        "user"      : ResourceArgument(expectedType=basestring), 
        "group"     : ResourceArgument(expectedType=basestring), 
    }
    
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, self._schema, *args, **kwargs)

