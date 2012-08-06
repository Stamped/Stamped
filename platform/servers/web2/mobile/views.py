#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import api.HTTPSchemas
import utils

import servers.web2.core.views       as views
import servers.web2.core.appsettings as appsettings

from servers.web2.core.schemas  import *
from servers.web2.core.helpers  import *

def profile(*args, **kwargs):
    kwargs['mobile'] = True
    
    return views.profile(*args, **kwargs)

def map(*args, **kwargs):
    kwargs['mobile'] = True
    
    return views.map(*args, **kwargs)

@stamped_view(schema=HTTPStampDetail, ignore_extra_params=True)
def sdetail(request, schema, **kwargs):
    body_classes = 'sdetail'
    ajax         = schema.ajax
    
    del schema.ajax
    
    logs.info('MOBILE SDETAIL: %s/%s/%s' % (schema.screen_name, schema.stamp_num, schema.stamp_title))
    
    user   = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
    stamp  = stampedAPIProxy.getStampFromUser(user['user_id'], schema.stamp_num)
    
    if stamp is None:
        raise StampedUnavailableError("unable to find stamp")
    
    previews = stamp['previews']
    users    = []
    
    if 'likes' in previews and len(previews['likes']) > 0:
        likes = previews['likes']
        
        for u in likes:
            u['preview_type'] = 'like'
        
        likes = shuffle_split_users(likes)
        users.extend(likes)
    
    if 'todos' in previews and len(previews['todos']) > 0:
        todos = previews['todos']
        
        for u in todos:
            u['preview_type'] = 'todo'
        
        todos = shuffle_split_users(todos)
        users.extend(todos)
    
    template = 'sdetail-mobile.html'
    
    entity  = stampedAPIProxy.getEntity(stamp['entity']['entity_id'])
    return stamped_render(request, 'sdetail-mobile.html', {
        'user'               : user, 
        'feedback_users'     : users, 
        'stamp'              : stamp, 
        'entity'             : entity, 
    }, preload=[ 'user', 'stamp', 'entity' ])

def index(*args, **kwargs):
    kwargs['mobile'] = True
    return views.index(*args, **kwargs)

def about(*args, **kwargs):
    kwargs['mobile'] = True
    return views.about(*args, **kwargs)

def jobs(*args, **kwargs):
    kwargs['mobile'] = True
    return views.jobs(*args, **kwargs)

def legal(*args, **kwargs):
    kwargs['mobile'] = True
    return views.legal(*args, **kwargs)

def licenses(*args, **kwargs):
    kwargs['mobile'] = True
    return views.licenses(*args, **kwargs)

def privacy_policy(*args, **kwargs):
    kwargs['mobile'] = True
    return views.privacy_policy(*args, **kwargs)

def faq(*args, **kwargs):
    kwargs['mobile'] = True
    return views.faq(*args, **kwargs)

def password_reset(*args, **kwargs):
    kwargs['mobile'] = True
    return appsettings.password_reset(*args, **kwargs)

def password_forgot(*args, **kwargs):
    kwargs['mobile'] = True
    return appsettings.password_forgot(*args, **kwargs)

def alert_settings(*args, **kwargs):
    kwargs['mobile'] = True
    return appsettings.alert_settings(*args, **kwargs)

