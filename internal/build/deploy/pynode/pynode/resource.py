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
    "Template", 
]

import utils
from utils import AttributeDict, OrderedDict
from environment import Environment
from exceptions import *

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
        self._required = False
        self._expectedType = expectedType
        
        if hasattr(default, '__call__'):
            self.default = default
        else:
            self.default = self.validate(default)
        
        self._required = required
    
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value is None:
            if self._required:
                raise InvalidArgument("invalid value for arg %s" % str(value))
            else:
                return value
        elif self._expectedType is not None and not isinstance(value, self._expectedType):
            raise InvalidArgument("invalid value for arg %s" % str(value))
        else:
            return value

class ResourceArgumentList(ResourceArgument):
    def __init__(self, default=None, required=False, expectedType=None, options=None):
        self._options = options
        ResourceArgument.__init__(self, default, required, expectedType)
    
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        if value is None:
            if self._required:
                raise InvalidArgument("invalid value for arg %s" % str(value))
            else:
                return value
        
        if not isinstance(value, (tuple, list)):
            value = [ value ]
        
        # validate each element in the argument list
        for v in value:
            if hasattr(v, '__call__'):
                continue
            elif (self._expectedType is not None and not isinstance(v, self._expectedType)) or \
                (self._options is not None and not v in self._options):
                raise InvalidArgument("invalid value '%s'" % str(v))
        
        return value

class ResourceArgumentBoolean(ResourceArgument):
    def validate(self, value):
        if hasattr(value, '__call__'):
            return value
        
        value = ResourceArgument.validate(self, value)
            
        print(value)
        if not value in (None, True, False):
            raise InvalidArgument("Expected a boolean but received %r" % value)
        
        return value

class Resource(AttributeDict):
    s_globalSchema = ResourceArgumentSchema([
        ("action",          ResourceArgumentList(default=None)), 
        ("ignoreFailures",  ResourceArgumentBoolean(default=False)), 
        ("notifies",        ResourceArgumentList(default=[])), 
        ("subscribes",      ResourceArgumentList(default=[])), 
        ("not_if",          ResourceArgument(expectedType=basestring)), 
        ("only_if",         ResourceArgument(expectedType=basestring)), 
        ("provider",        ResourceArgument(required=True, 
                                             expectedType=basestring)), 
    ])
    
    def __init__(self, *args, **kwargs):
        AttributeDict.__init__(self)
        
        self.env  = Environment.getInstance()
        self.resourceType = self.__class__.__name__
        self.isUpdated = False
        
        seen = set()
        
        if not hasattr(self, '_schema'):
            raise Fail("Resource failed to define a valid _schema")
        
        schema = self._schema
        
        resolvedArgs = { }
        keys = schema.keys()
        keysLen = len(keys)
        index = 0
        
        # resolve unnamed arguments with names corresponding to the order 
        # they were passed to Resource's ctor and their relative definitions 
        # in the subclass' ResourceArgumentSchema (which is an OrderedDict, 
        # so as to retain this ordering information).
        for arg in args:
            if index < keysLen:
                key = keys[index]
                resolvedArgs[keys[index]] = arg
            else:
                raise InvalidArgument("Invalid unnamed argument %s provided to resource %s" % (arg, str(self)))
            
            index += 1
        
        for arg in kwargs:
            if arg in resolvedArgs:
                raise InvalidArgument("Invalid mixture of named and unnamed arguments provided to resource %s, possibly around argument %s" % (str(self), arg))
            else:
                resolvedArgs[arg] = kwargs[arg]
        
        utils.log("Initializing resource '%s' with args: %s" % (self.resourceType, resolvedArgs))
        
        # validate resource arguments
        for arg in resolvedArgs:
            if arg not in schema and arg not in self.s_globalSchema:
                raise InvalidArgument("Unexpected argument %s provided to resource %s" % (arg, str(self)))
            elif arg in seen:
                raise InvalidArgument("Duplicate argument %s provided to resource %s" % (arg, str(self)))
            else:
                try:
                    if arg in schema:
                        resourceArg = schema[arg]
                    else:
                        resourceArg = self.s_globalSchema[arg]
                    
                    value = resolvedArgs[arg]
                    value = resourceArg.validate(value)
                    self[arg] = value
                    #utils.log("added '%s'='%s' to resource '%s'" % (arg, str(value), str(self)))
                except InvalidArgument as e:
                    utils.log("Error initializing argument '%s' for resource %s" % (arg, str(self)))
                    utils.printException()
                    raise e
        
        for key in schema:
            if not key in self:
                self[key] = schema[key].default
        
        for key in self.s_globalSchema:
            if not key in self:
                self[key] = self.s_globalSchema[key].default
        
        self.subscriptions = {
            'immediate' : set(), 
            'delayed' : set()
        }
        
        for sub in self.subscribes:
            if len(sub) == 2:
                action, resource = sub
                immediate = False
            else:
                action, resource, immediate = sub
            
            resource.subscribe(action, self, immediate)
        
        for sub in self.notifies:
            self.subscribe(*sub)
        
        self._validate()
        self._register()
        utils.log("Added new resource '%s'" % (str(self), ))
    
    def updated(self):
        self.isUpdated = True
    
    def subscribe(self, action, resource, immediate=False):
        imm = "immediate" if immediate else "delayed"
        sub = (action, resource)
        self.subscriptions[imm].add(sub)
    
    def _validate(self):
        if not 'name' in self:
            raise Fail("Unable to find name for resource %s" % str(self))
        
        if not 'provider' in self:
            raise Fail("Unable to resolve provider for resource %s" % self.name)
    
    def _register(self):
        resourceType = self.resourceType
        
        # briefly check for conflicting duplicate resources
        for resource in self.env.resources:
            if resource.name == self.name and resource.provider != self.provider:
                raise Fail("Duplicate resource %r with different providers: %r != %r" % \
                           (resource, self.provider, resource.provider))
        
        # TODO: use self.env.resources[resourceType][name] to support this usage case:
        # notifies = [("restart", env.resources["Service"]["apache2"])])
        self.env.resources.append(self)
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        if 'name' in self:
            return "%s(name=%s)" % (self.resourceType, self.name)
        else:
            return "%s(no name)" % (self.resourceType, )
    
    def __getitem__(self, name):
        item = super(Resource, self).__getitem__(name)
        
        if hasattr(item, '__call__'):
            return item(self)
        else:
            return item

class Template(object):
    
    def __init__(self, path):
        self.path = path
        # TODO

