#!/usr/bin/env python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class ATodoDB(object):
    
    @abstract    
    def addTodo(self, todo):
        pass
    
    @abstract
    def getTodo(self, userId, entityId):
        pass
    
    @abstract
    def removeTodos(self, userId, entityId):
        pass
    
    @abstract
    def completeTodo(self, entityId, userId, complete=True):
        pass
    
    @abstract
    def getTodos(self, userId, **kwargs):
        pass

