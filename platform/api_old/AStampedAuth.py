#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract
from api_old.AEntitySink import AEntitySink

class AStampedAuth(AEntitySink):
    """
        Defines the internal API for accessing and manipulating all Stamped 
        backend databases.
    """
    
    def __init__(self, desc):
        AEntitySink.__init__(self, desc)
    
    # ####### #
    # Clients #
    # ####### #
    
    @abstract
    def addClient(self, params):
        raise NotImplementedError
    
    @abstract
    def verifyClientCredentials(self, params):
        raise NotImplementedError
    
    @abstract
    def removeClient(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    @abstract
    def verifyUserCredentials(self, params):
        raise NotImplementedError
    
    # ############## #
    # Refresh Tokens #
    # ############## #
    
    @abstract
    def addRefreshToken(self, params):
        raise NotImplementedError
    
    @abstract
    def verifyRefreshToken(self, params):
        raise NotImplementedError
    
    @abstract
    def removeRefreshToken(self, params):
        raise NotImplementedError
    
    # ############# #
    # Access Tokens #
    # ############# #
    
    @abstract
    def addAccessToken(self, params):
        raise NotImplementedError
    
    @abstract
    def verifyAccessToken(self, params):
        raise NotImplementedError
    
    @abstract
    def removeAccessToken(self, params):
        raise NotImplementedError

