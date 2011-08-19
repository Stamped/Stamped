#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [
    "ResourceArgumentSchema", 
    "ResourceArgument", 
    "ResourceArgumentList", 
    "ResourceArgumentBoolean", 
    "Resource", 
]

import utils
from utils import AttributeDict, OrderedDict
from errors import *

# TODO: cleanup the code duplication between ResourceArgument.validate, 
# ResourceArgumentList.validate, and ResourceArgumentBoolean.validate.

class ResourceArgumentSchema(OrderedDict):
    def __init__(self, items=[]):
        OrderedDict.__init__(self)
        
        # hack to make ordering work... would be *much* nicer if python 
        # supported an option for order-preserving **kwargs ala:
        # http://groups.google.com/group/python-ideas/browse_thread/thread/f3663e5b1f4fe7d4
        for d in items:
            self[d[0]] = d[1]

class ResourceArgument(object):
    def __init__(self, default=None, required=False, expectedType=None):
        self.required = False
        self.expectedType = expectedType
        
        if hasattr(default, '__call__'):
            self.default = default
        else:
            self.default = self.validate(default)
        
        self.required = required
    
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value is None:
            if self.required:
                raise InvalidArgument("invalid value for arg %s" % str(value))
            else:
                return value
        elif self.expectedType is not None and not isinstance(value, self.expectedType):
            raise InvalidArgument("invalid value for arg %s" % str(value))
        else:
            return value

class ResourceArgumentList(ResourceArgument):
    def __init__(self, default=None, required=False, expectedType=None, options=None):
        self.options = options
        ResourceArgument.__init__(self, default, required, expectedType)
    
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value is None:
            if self.required:
                raise InvalidArgument("invalid value for arg %s" % str(value))
            else:
                return value
        
        if not isinstance(value, (tuple, list)):
            value = [ value ]
        
        # validate each element in the argument list
        for v in value:
            if hasattr(v, '__call__'):
                continue
            elif (self.expectedType is not None and not isinstance(v, self.expectedType)) or \
                (self.options is not None and not v in self.options):
                raise InvalidArgument("invalid value '%s'" % str(v))
        
        return value

class ResourceArgumentBoolean(ResourceArgument):
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value == "True" or value == "true" or value == 1:
            value = True
        if value == "False" or value == "false" or value == 0:
            value = False
        
        value = ResourceArgument.validate(self, value)
        if not value in (None, True, False):
            raise InvalidArgument("Expected a boolean but received %r" % value)
        
        return value

class Resource():
    s_globalSchema = ResourceArgumentSchema([
        # TODO
    ])
    
    @staticmethod
    def parse(name, schema, args):
        #utils.log("Parsing API function '%s' with args: %s" % (name, args))
        output = AttributeDict()
        seen = set()
        
        # validate resource arguments
        for arg in args:
            if arg not in schema and arg not in Resource.s_globalSchema:
                raise InvalidArgument("Unexpected argument '%s' provided to API function '%s'" % (arg, name))
            elif arg in seen:
                raise InvalidArgument("Duplicate argument '%s' provided to API function '%s'" % (arg, name))
            else:
                try:
                    if arg in schema:
                        resourceArg = schema[arg]
                    else:
                        resourceArg = Resource.s_globalSchema[arg]
                    
                    value = args[arg]
                    value = resourceArg.validate(value)
                    output[arg] = value
                except InvalidArgument as e:
                    utils.log("Error initializing argument '%s' for API function '%s'" % (arg, name))
                    utils.printException()
                    raise e
        
        for sch in [ schema, Resource.s_globalSchema ]:
            for key in sch:
                if not key in output:
                    if sch[key].required:
                        raise Fail("Required argument '%s' to API function '%s' not found" % (key, name))
                    
                    output[key] = sch[key].default
        
        return output

