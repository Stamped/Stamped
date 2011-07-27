#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import utils
from abc import abstractmethod

class ADeploymentStack(object):
    def __init__(self, name, system):
        self.name = name
        self.system = system
        self.instances = []
    
    @abstractmethod
    def create(self):
        pass
    
    @abstractmethod
    def delete(self):
        pass
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def init(self):
        pass
    
    @abstractmethod
    def update(self):
        pass
    
    @abstractmethod
    def crawl(self, *args):
        pass
    
    def local(self, cmd, env=None, show_cmd=True):
        if show_cmd:
            print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

