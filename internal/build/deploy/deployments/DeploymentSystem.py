#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, getpass, os, pickle, re, utils
from ADeploymentSystem import ADeploymentSystem
from errors import Fail
from abc import abstractmethod

class DeploymentSystem(ADeploymentSystem):
    def __init__(self, name, options, stack_class):
        ADeploymentSystem.__init__(self, name, options)
        
        self.stack_class = stack_class
        self._stacks = { }
        self._init_env()
    
    @abstractmethod
    def _init_env(self):
        raise NotImplementedError
    
    def _get_matching_stacks(self, stackNameRegex, unique=False):
        stacks = [ ]
        
        for stackName in self._stacks:
            if re.search(stackNameRegex, stackName):
                if len(stacks) > 0 and unique:
                    raise Fail("Error: stack name regex '%s' is not unique" % stackNameRegex)
                
                stacks.append(stackName)
        
        return stacks
    
    def create_stack(self, *args):
        for stackName in args:
            if stackName in self._stacks:
                utils.log("Warning: deleting duplicate stack '%s' before create can occur" % stackName)
                self.delete_stack(stackName)
            
            stack = self.stack_class(stackName, self)
            stack.create()
            
            self._stacks[stackName] = stack
    
    def delete_stack(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                if stackName in self._stacks:
                    stack = self._stacks[stackName]
                    stack.delete()
                    
                    del self._stacks[stackName]
    
    def describe_stack(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.describe()
    
    def describe_stack_events(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.describe_events()
    
    def connect(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.connect()
    
    def init_stack(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.init()
    
    def update_stack(self, *args):
        for stackNameRegex in args:
            stacks = self._get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.update()
    
    def list_stacks(self, stackNameRegex=None, stackStatus=None):
        if stackNameRegex is not None:
            stacks = self._get_matching_stacks(stackNameRegex)
            utils.log("'%s' contains %d stacks matching '%s':" % (self, len(stacks), stackNameRegex))
        else:
            stacks = self._stacks
            utils.log("'%s' contains %d stacks:" % (self, len(stacks)))
        
        index = 1
        for (stackName, stack) in stacks.iteritems():
            utils.log("%d) '%s'" % (index, stackName))
            index += 1

