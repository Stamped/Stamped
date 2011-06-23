#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Mention import Mention

class AMentionDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addMention(self, mention):
        raise NotImplementedError
    
    def getMention(self, mentionID):
        raise NotImplementedError
    
    def removeMention(self, mentionID):
        raise NotImplementedError
    
    def addMentions(self, mentions):
        return map(self.addMention, mentions)
    
    def getMentions(self, mentionIDs):
        return map(self.getMention, mentionIDs)
    
    def removeMentions(self, mentionIDs):
        return map(self.removeMention, mentionIDs)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

