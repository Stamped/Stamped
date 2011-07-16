#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, utils
from utils import AttributeDict
from environment import Environment
from system import System
from errors import Fail

class Cookbook(object):
    def __init__(self, name, path, config=None):
        self.name = name
        self.path = path
        
        self._meta    = None
        self._library = None
    
    @property
    def config(self):
        return self.meta.get('__config__', {})
    
    @property
    def loader(self):
        return self.meta.get('__loader__', lambda kit:None)
    
    @property
    def meta(self):
        if self._meta is None:
            metapath = os.path.join(self.path, "__init__.py")
            
            meta = {'system': System.getInstance()}
            
            if os.path.exists(metapath):
                with open(metapath, "rb") as fp:
                    source = fp.read()
                
                exec compile(source, metapath, "exec") in meta
            else:
                meta['__config__'] = { }
                meta['__loader__'] = { }
            
            self._meta = meta
        
        return self._meta
    
    @property
    def library(self):
        if self._library is None:
            libpath = os.path.join(self.path, "libraries")
            globs = {}
            
            if os.path.exists(libpath):
                for f in sorted(os.listdir(libpath)):
                    if not f.endswith('.py'):
                        continue
                    
                    path = os.path.join(libpath, f)
                    with open(path, "rb") as fp:
                        source = fp.read()
                    
                    exec compile(source, libpath, "exec") in globs
            
            self._library = AttributeDict(globs)
        
        return self._library
    
    def getRecipe(self, name):
        path = os.path.join(self.path, "recipes", name + ".py")
        
        if not os.path.exists(path):
            raise Fail("Recipe %s in cookbook %s not found" % (name, self.name))
        
        with open(path, "rb") as fp:
            return fp.read()
    
    def __getattr__(self, name):
        try:
            return self.library[name]
        except KeyError:
            utils.log("Error resolving dynamic key name '%s' in cookbook '%s'" % (name, self.name))
            raise
    
    def __repr__(self):
        return "Cookbook(name=%s)" % (self.name, )
    
    @classmethod
    def loadFromPath(cls, name, path):
        return cls(name, path)

