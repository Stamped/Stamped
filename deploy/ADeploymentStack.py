#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

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
    def update(self):
        pass
    
    @abstract
    def repair(self):
        pass
    
    @abstract
    def force_db_primary_change(self):
        pass
    
    @abstract
    def clear_cache(self, *args):
        pass
    
    @abstract
    def crawl(self, *args):
        pass
    
    @abstract
    def stress(self, *args):
        pass
    
    @abstract
    def setup_crawler_data(self, *args):
        pass
    
    @abstract
    def backup(self, *args):
        pass
    
    @abstract
    def add(self, *args):
        pass
    
    def local(self, cmd, env=None, show_cmd=True):
        if show_cmd:
            print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

