#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "Group", "User" ]

from pynode.resource import *

class Group(Resource):
    _schema = ResourceArgumentSchema([
        ("name",     ResourceArgument(required=True, expectedType=basestring)), 
        ("action",   ResourceArgumentList(default="create", 
                                          options=[ "create", "remove", "modify", "manage", "lock", "unlock" ])), 
        ("gid",      ResourceArgument()), 
        ("members",  ResourceArgumentList(expectedType=basestring)), 
        ("password", ResourceArgument(expectedType=basestring)), 
    ])

class User(Resource):
    _schema = ResourceArgumentSchema([
        ("name",     ResourceArgument(required=True, expectedType=basestring)), 
        ("action",   ResourceArgumentList(default="create", 
                                          options=[ "create", "remove", "modify", "manage", "lock", "unlock" ])), 
        ("comment",  ResourceArgument(expectedType=basestring)), 
        ("uid",      ResourceArgument()), 
        ("gid",      ResourceArgument()), 
        ("groups",   ResourceArgumentList(expectedType=basestring)), 
        ("home",     ResourceArgument(default=lambda r: "/home/%s" % r.name, 
                                      expectedType=basestring)), 
        ("shell",    ResourceArgument(default="/bin/bash", 
                                      expectedType=basestring)), 
        ("password", ResourceArgument(expectedType=basestring)), 
        ("system",   ResourceArgumentBoolean(default=False)), 
    ])

