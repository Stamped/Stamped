#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import random

from utils import abstract

class ASimulatedUserAction(object):
    def __init__(self, weight, repeat=1):
        self.weight = weight
        self.repeat = repeat
    
    def __call__(self, parent, user):
        for i in xrange(self.repeat):
            try:
                self._execute(parent, user)
            except:
                utils.log("[%s] ERROR: unable to perform action '%s']" % (user, self))
    
    @abstract
    def _execute(self, parent, user):
        pass
    
    def __str__(self):
        return self.__class__.__name__

class UpdateInboxAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        path = "collections/inbox.json"
        data = {
            "oauth_token": user.token['access_token'], 
        }
        return parent._parent.handleGET(path, data)

class SearchAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        path   = "entities/search.json"
        lat    = random.normalvariate(40.797898, 1.0)
        lng    = random.normalvariate(-73.968148, 1.0)
        coords = '%f,%f' % (lat, lng)
        
        data = {
            "oauth_token" : user.token['access_token'],
            "q" : parent.getRandomSearchString(), 
            "coordinates" : coords, 
        }
        
        results = parent._parent.handleGET(path, data)
        if len(results) > 0:
            for result in results:
                result['entity_id'] = result['search_id']
                parent.addEntity(result)
        
        return results

class StampAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        stamp = parent._parent.createStamp(user.token, parent.getRandomEntityID(), 
                                           blurb=parent.getRandomText())
        parent.addStamp(stamp)
        
        return stamp

class CommentAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        return parent._parent.createComment(user.token, 
                                            parent.getRandomStampID(), 
                                            parent.getRandomText())

class UpdateActivityAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        path = "activity/show.json"
        data = {
            "oauth_token": user.token['access_token'],
        }
        
        return parent._parent.handleGET(path, data)

class LikeAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        path = "stamps/likes/create.json"
        data = {
            "oauth_token": user.token['access_token'],
            "stamp_id": parent.getRandomStampID(), 
        }
        
        return parent._parent.handlePOST(path, data)

class AddTodoAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        return parent._parent.createTodo(user.token, parent.getRandomEntityID())

class NullAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)
    
    def _execute(self, parent, user):
        # note: purposefully empty
        pass


class BaselineBeginAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)

    def _execute(self, parent, user):
        path = 'test/begin.json'
        entity_id = parent._parent.handleGET(path, {'n': 1})
        user.entity_ids.append(entity_id)
        return True

class BaselineReadAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)

    def _execute(self, parent, user):
        path = 'test/read.json'

        data = {'entity_ids': parent.getRandomEntityID()}
        # if len(user.entity_ids) == 0:
        #     return False
        # data = {'entity_ids': user.entity_ids[-1]} # parent.getRandomEntityID()
        
        return parent._parent.handleGET(path, data)

class BaselineWriteAction(ASimulatedUserAction):
    def __init__(self, weight, repeat=1):
        ASimulatedUserAction.__init__(self, weight, repeat)

    def _execute(self, parent, user):
        path = 'test/write.json'
        data = {'n': 1}
        entity_ids = parent._parent.handleGET(path, data)
        user.entity_ids += entity_ids
        return True

