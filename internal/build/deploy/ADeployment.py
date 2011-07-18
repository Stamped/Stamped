#print !/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import utils
from abc import abstractmethod

class ADeploymentSystem(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
    
    @abstractmethod
    def create_stack(self, *args):
        pass
    
    @abstractmethod
    def delete_stack(self, *args):
        pass
    
    @abstractmethod
    def describe_stack(self, *args):
        pass
    
    @abstractmethod
    def describe_stack_events(self, *args):
        pass
    
    @abstractmethod
    def connect(self, *args):
        pass
    
    @abstractmethod
    def list_stacks(self, *args, **kwargs):
        pass
    
    def local(self, cmd, env=None):
        print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

class ADeploymentStack(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
    
    @abstractmethod
    def init(self):
        pass
    
    @abstractmethod
    def delete(self):
        pass
    
    @abstractmethod
    def describe(self):
        pass
    
    @abstractmethod
    def describe_events(self):
        pass
    
    @abstractmethod
    def connect(self):
        pass
    
    def local(self, cmd, env=None):
        print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

