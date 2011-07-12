#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "ResourceArgument", "ResourceArgumentList", "ResourceArgumentBoolean", 
            "Resource" ]

import pynode.Utils
from pynode.Utils import AttributeDictionary

class ResourceArgument(object):
    def __init__(self, default=None, required=False, expectedType=None):
        self._required = False
        self._expectedType = expectedType
        
        if hasattr(default, '__call__'):
            self._default = default
        else:
            self._default = self.validate(default)
        
        self._required = required
    
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value is None:
            if self._required:
                raise Exception("invalid value for arg %s" % str(value))
            else:
                return value
        elif self._expectedType is not None and not isinstance(value, self._expectedType):
            raise Exception("invalid value for arg %s" % str(value))
        else:
            return value

class ResourceArgumentList(ResourceArgument):
    def __init__(self, default=None, required=False, expectedType=None, options=None):
        self._options = options
        ResourceArgument.__init__(self, default, required, expectedType)
    
    def validate(self, value):
        value = ResourceArgument.validate(self, value)
        
        if not isinstance(value, (tuple, list)):
            value = [ value ]
        
        # validate each element in the argument list
        for v in value:
            if hasattr(v, '__call__'):
                continue
            elif (self._expectedType is not None and not isinstance(v, self._expectedType)) or \
                (self._options is not None and not v in self._options):
                raise Exception("invalid value for arg %s" % str(value))
        
        return value

class ResourceArgumentBoolean(ResourceArgument):
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        value = ResourceArgument.validate(self, value)
        if not value in (None, True, False):
            raise Exception("Expected a boolean but received %r" % value)
        
        return value

class Resource(AttributeDictionary):
    def __init__(self, schema, *args, **kwargs):
        seen = set()
        
        # validate resource arguments
        for arg in kwargs:
            if arg not in schema:
                raise Exception("Unexpected argument %s provided to resource %s" % (arg, str(self)))
            elif arg in seen:
                raise Exception("Duplicate argument %s provided to resource %s" % (arg, str(self)))
            else:
                try:
                    resourceArg = schema[arg]
                    value = kwargs[arg]
                    value = resourceArg.validate(value)
                    self[arg] = value
                except Exception as e:
                    Utils.log("Error initializing argument %s for resource %s" % (arg, str(self)))
                    Utils.printException()
                    raise
    
    def updated(self):
        pass

