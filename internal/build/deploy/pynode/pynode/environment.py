#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import subprocess, utils
from datetime import datetime

from utils import AttributeDict, Singleton
from provider import Provider
from system import System
from version import version, longVersion

class Environment(object):
    _instances = []
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.system = System.getInstance()
        self.config = AttributeDict()
        
        self.resources = [ ]
        self.delayedActions = set()
        
        now = datetime.now()
        self.updateConfig({
            'date': now, 
            'pynode.version': version(),
            'pynode.longVersion': longVersion(),
            'pynode.backup.path': '/tmp/pynode/backup',
            'pynode.backup.prefix': now.strftime("%Y%m%d%H%M%S"),
        })
    
    def run(self):
        with self:
            # Run resource actions
            for resource in self.resources:
                utils.log("Running resource %r" % resource)
                
                if resource.not_if is not None and self._checkCondition(resource.not_if):
                    utils.log("Skipping %s due to not_if" % resource)
                    continue
                
                if resource.only_if is not None and not self._checkCondition(resource.only_if):
                    utils.log("Skipping %s due to only_if" % resource)
                    continue
                
                for action in resource.action:
                    self._runAction(resource, action)
            
            # Run delayed actions
            while self.delayedActions:
                (action, resource) = self.delayedActions.pop()
                self._runAction(resource, action)
    
    def updateConfig(self, attributes, overwrite=True):
        for key, value in attributes.items():
            attr = self.config
            path = key.split('.')
            
            for pth in path[:-1]:
                if pth not in attr:
                    attr[pth] = AttributeDict()
                attr = attr[pth]
            
            if overwrite or path[-1] not in attr:
                attr[path[-1]] = value
    
    def _runAction(self, resource, action):
        utils.log("Performing action %s on %s" % (action, resource))
        
        providerClass = Provider.resolve(self, resource.__class__.__name__, resource.provider)
        provider = providerClass(resource)
        
        try:
            providerAction = getattr(provider, 'action_%s' % action)
        except AttributeError:
            raise Fail("%r does not implement action %s" % (provider, action))
        
        providerAction()
        
        if resource.isUpdated:
            for action, res in resource.subscriptions['immediate']:
                utils.log("%s sending %s action to %s (immediate)" % (resource, action, res))
                self._runAction(res, action)
            
            for action, res in resource.subscriptions['delayed']:
                utils.log("%s sending %s action to %s (delayed)" % (resource, action, res))
            
            self.delayedActions |= resource.subscriptions['delayed']
    
    def _checkCondition(self, cond):
        if hasattr(cond, '__call__'):
            return cond()
        
        if isinstance(cond, basestring):
            ret = subprocess.call(cond, shell=True)
            return ret == 0
        
        raise Exception("Unknown condition type %r" % cond)
    
    @classmethod
    def getInstance(cls):
        if len(cls._instances) <= 0:
            raise Exception("Internal error: no environment instance")
        else:
            return cls._instances[-1]
    
    def __enter__(self):
        self.__class__._instances.append(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__._instances.pop()
        return False
    
    def __getstate__(self):
        return dict(
            config = self.config,
            resources = self.resources,
            delayedActions = self.delayedActions,
        )
    
    def __setstate__(self, state):
        self.__init__()
        self.config = state['config']
        self.resources = state['resources']
        self.delayedActions = state['delayedActions']

