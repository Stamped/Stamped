#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Followers import Followers

class AFollowersDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def getFollowers(self, userID):
        raise NotImplementedError
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

