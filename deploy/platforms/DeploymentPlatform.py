#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, utils

from utils import abstract
from errors import Fail

from ADeploymentPlatform import ADeploymentPlatform

class DeploymentPlatform(ADeploymentPlatform):
    def __init__(self, stack_class, db_stack=None):
        ADeploymentPlatform.__init__(self)
        
        self.stack_class = stack_class
        self.db_stack = db_stack
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
    
    def create(self, *args):
        stackName = args[0]
        
        if stackName in self._stacks:
            utils.log("Warning: deleting duplicate stack '%s' before create can occur" % stackName)
            self.delete(stackName)
        
        stack = self.stack_class(stackName, self, db_stack=self.db_stack)
        stack.create()
        
        self._stacks[stackName] = stack
    
    def delete(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.delete()
        del self._stacks[stack.name]
    
    def update(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.update(*args[1:])
    
    def repair(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.repair(*args[1:])
    
    def force_db_primary_change(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.force_db_primary_change(*args[1:])
    
    def clear_cache(self, *args):
        stack = self._get_matching_stack(args[0])
        stack.clear_cache(*args[1:])
    
    def remove_db_node(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.remove_db_node(*args[1:])
    
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
    
    def list(self, stackName=None, stackStatus=None):
        stacks = self._stacks
        
        index = 1
        for (stackName, stack) in stacks.iteritems():
            utils.log("%d) '%s'" % (index, stackName))
            index += 1
    
    def add(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.add(*args[1:])
    
    def stress(self, *args):
        stackName = args[0]
        stack = self._get_matching_stack(stackName)
        stack.stress(*args[1:])

