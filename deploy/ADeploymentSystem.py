#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import utils
from utils import abstract

class ADeploymentSystem(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
    
    @abstract
    def bootstrap(self, *args):
        pass
    
    @abstract
    def create(self, *args):
        pass
    
    @abstract
    def delete(self, *args):
        pass
    
    @abstract
    def list(self, *args, **kwargs):
        pass
    
    @abstract
    def update(self, *args):
        pass
    
    @abstract
    def repair(self, *args):
        pass
    
    @abstract
    def force_db_primary_change(self, *args):
        pass
    
    @abstract
    def remove_db_node(self, *args):
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
    
    def local(self, cmd, env=None):
        print "[%s-local] %s" % (self, cmd, )
        
        if env is None:
            if not hasattr(self, 'env'):
                return utils.shell3(cmd)
            
            env = self.env
        
        return utils.shell3(cmd, env)
    
    def __str__(self):
        return self.name

