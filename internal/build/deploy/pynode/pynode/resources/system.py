#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "File", "Directory", "Link", "Execute", "Script", "Mount" ]

from pynode.resource import *

class File(Resource):
    _schema = ResourceArgumentSchema([
        ("path",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="create", 
                                             options=[ "create", "delete", "touch" ])), 
        ("backup",      ResourceArgument(expectedType=basestring)), 
        ("mode",        ResourceArgument(expectedType=int)), 
        ("owner",       ResourceArgument(expectedType=basestring)), 
        ("group",       ResourceArgument(expectedType=basestring)), 
        ("content",     ResourceArgument(expectedType=basestring)), 
        ("name",        ResourceArgument(default=lambda r: r.path, 
                                         expectedType=basestring)), 
    ])

class Directory(Resource):
    _schema = ResourceArgumentSchema([
        ("path",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="create", 
                                             options=[ "create", "delete" ])), 
        ("mode",        ResourceArgument(expectedType=int)), 
        ("owner",       ResourceArgument(expectedType=basestring)), 
        ("group",       ResourceArgument(expectedType=basestring)), 
        ("recursive",   ResourceArgumentBoolean(default=True)), 
        ("name",        ResourceArgument(default=lambda r: r.path, 
                                         expectedType=basestring)), 
    ])

class Link(Resource):
    _schema = ResourceArgumentSchema([
        ("path",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="create", 
                                             options=[ "create", "delete" ])), 
        ("to",          ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("hard",        ResourceArgumentBoolean(default=False)), 
        ("name",        ResourceArgument(default=lambda r: r.path, 
                                         expectedType=basestring)), 
    ])

class Execute(Resource):
    _schema = ResourceArgumentSchema([
        ("path",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="run", 
                                             options=[ "run" ])), 
        ("creates",     ResourceArgument(expectedType=basestring)), 
        ("cwd",         ResourceArgument(expectedType=basestring)), 
        ("environment", ResourceArgument(expectedType=basestring)), 
        ("user",        ResourceArgument(expectedType=basestring)), 
        ("group",       ResourceArgument(expectedType=basestring)), 
        ("returns",     ResourceArgumentList(default=0, 
                                             expectedType=int)), 
        ("timeout",     ResourceArgument(expectedType=int)), 
        ("name",        ResourceArgument(default=lambda r: r.path, 
                                         expectedType=basestring)), 
    ])

class Script(Resource):
    _schema = ResourceArgumentSchema([
        ("name",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("code",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="run", 
                                             options=[ "run" ])), 
        ("cwd",         ResourceArgument(expectedType=basestring)), 
        ("environment", ResourceArgument(expectedType=basestring)), 
        ("interpreter", ResourceArgument(default="/bin/bash", 
                                         expectedType=basestring)), 
        ("user",        ResourceArgument(expectedType=basestring)), 
        ("group",       ResourceArgument(expectedType=basestring)), 
    ])

class Mount(Resource):
    _schema = ResourceArgumentSchema([
        ("path",        ResourceArgument(required=True, 
                                         expectedType=basestring)), 
        ("action",      ResourceArgumentList(default="mount", 
                                             options=[ "mount", "unmount", "remount", "enable", "disable" ])), 
        ("device",      ResourceArgument(expectedType=basestring)), 
        ("fstype",      ResourceArgument(expectedType=basestring)), 
        ("options",     ResourceArgumentList(default=[ "defaults" ], 
                                             expectedType=basestring)), 
        ("dump",        ResourceArgument(default=0, 
                                         expectedType=int)), 
        ("passno",      ResourceArgument(default=2, 
                                         expectedType=int)), 
        ("name",        ResourceArgument(default=lambda r: r.path, 
                                         expectedType=basestring)), 
    ])

