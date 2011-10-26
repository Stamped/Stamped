#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import re, utils

from utils import abstract
from errors import Fail

from ADeploymentSystem import ADeploymentSystem

class DeploymentSystem(ADeploymentSystem):
    def __init__(self, name, options, stack_class):
        ADeploymentSystem.__init__(self, name, options)
        
        self.stack_class = stack_class
        self._stacks = { }
        self._init_env()
    
    @abstract
    def _init_env(self):
        raise NotImplementedError
    
    def _get_matching_stack(self, stackName, unique=False):
        orig = stackName
        if '.' in stackName:
            stackName = stackName.split('.')[0]
        
        stackName = stackName.lower()
        for name in self._stacks:
            if name.lower() == stackName:
                return self._stacks[name]
        
        msg = "Error: no stack exists matching the name '%s'" % orig
        utils.log(msg)
        raise Fail(msg)
    
    def create_stack(self, *args):
        stackName = args[0]
        
        if stackName in self._stacks:
            utils.log("Warning: deleting duplicate stack '%s' before create can occur" % stackName)
            self.delete_stack(stackName)
        
        stack = self.stack_class(stackName, self)
        stack.create()
        
        self._stacks[stackName] = stack
    
    def delete_stack(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.delete()
        del self._stacks[stack.name]
    
    def connect(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.connect()
    
    def init_stack(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.init()
    
    def update_stack(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.update()
    
    def crawl(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.crawl()
    
    def setup_crawler_data(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.setup_crawler_data()
    
    def backup(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.backup()
    
    def list_stacks(self, stackName=None, stackStatus=None):
        stacks = self._stacks
        
        index = 1
        for (stackName, stack) in stacks.iteritems():
            utils.log("%d) '%s'" % (index, stackName))
            index += 1
    
    def add_stack(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.add(*args[1:])
    
    def stress(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.stress(*args[1:])

