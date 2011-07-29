#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import utils
from utils import abstract

class ADeploymentStack(object):
    def __init__(self, name, system):
        self.name = name
        self.system = system
        self.instances = []
    
    @abstract
    def create(self):
        pass
    
    @abstract
    def delete(self):
        pass
    
    @abstract
    def connect(self):
        pass
    
    @abstract
    def init(self):
        pass
    
    @abstract
    def update(self):
        pass
    
    @abstract
    def crawl(self, *args):
        pass
    
    @abstract
    def setup_crawler_data(self, *args):
        pass
    
    def local(self, cmd, env=None, show_cmd=True):
        if show_cmd:
            print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

