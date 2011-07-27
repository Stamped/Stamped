#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import time, utils
from abc import ABCMeta, abstractmethod
from errors import *

class AInstance(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, stack, config):
        self.stack = stack
        self.config = utils.AttributeDict(config)
        self._init_config()
    
    @property
    def name(self):
        return self.config.name
    
    @property
    def roles(self):
        return self.config.roles
    
    @property
    def public_dns_name(self):
        raise NotImplementedError
    
    @property
    def private_ip_address(self):
        raise NotImplementedError
    
    @property
    def tags(self):
        raise NotImplementedError
    
    @property
    def state(self):
        raise NotImplementedError
    
    def create(self):
        self._pre_create()
        utils.log("[%s] create" % self)
        
        # don't create an instance more than once
        assert self.state is None
        
        # initialize the underlying instance
        self._create()
        
        # wait for the instance to start up
        utils.log("[%s] waiting to come online (this may take a few minutes)..." % self)
        while self.state == 'pending':
            time.sleep(1)
            self.update()
        
        if self.state != 'running':
            raise Fail("Error creating instance '%s', invalid state '%s' encountered" % \
                       (self.name, self.state))
        
        # add all tags
        utils.log("[%s] instance is online! adding %d tags..." % (self, len(self.config.items())))
        for tag in self.config:
            self.add_tag(tag, self.config[tag])
        
        self._post_create()
    
    def _pre_create(self):
        pass
    
    @abstractmethod
    def _create(self):
        raise NotImplementedError
    
    def _post_create(self):
        pass
    
    @abstractmethod
    def start(self):
        raise NotImplementedError
    
    @abstractmethod
    def stop(self, force=False):
        raise NotImplementedError
    
    @abstractmethod
    def terminate(self):
        raise NotImplementedError
    
    @abstractmethod
    def reboot(self):
        raise NotImplementedError
    
    @abstractmethod
    def update(self, validate=False):
        raise NotImplementedError
    
    @abstractmethod
    def add_tag(self, key, value=None):
        raise NotImplementedError
    
    @abstractmethod
    def remove_tag(self, key, value=None):
        raise NotImplementedError
    
    def _init_config(self):
        self.config['stack'] = self.stack.name
    
    def __str__(self):
        name = "%s(%s)" % (self.__class__.__name__, self.name)
        
        if self.state == 'running':
            try:
                public_dns_name = self.public_dns_name
                if public_dns_name != None and len(public_dns_name) > 0:
                    return "%s %s" % (name, public_dns_name)
            except NotInitializedError:
                pass
        
        return name

