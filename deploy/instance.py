#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import utils
from utils import lazy_property
from abc import abstractmethod

class Instance(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
    
    @property
    def stack_name(self):
        raise NotImplementedError
    
    @property
    def name(self):
        raise NotImplementedError
    
    @property
    def roles(self):
        raise NotImplementedError
    
    @property
    def public_dns_name(self):
        raise NotImplementedError
    
    @property
    def private_dns_name(self):
        return self.public_dns_name
    
    @property detail(self):
        raise NotImplementedError
    
    def __str__(self):
        return ("%s) %s" % (self.name, self.public_dns_name)

