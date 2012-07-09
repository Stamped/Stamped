#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import api.HTTPSchemas
import os, pprint, utils

from django.http                import HttpResponseRedirect
from servers.web2.core.schemas  import *
from servers.web2.core.helpers  import *

# TODO: stricter input schema validation

@stamped_view()
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return stamped_render(request, 'index.html', {
        'autoplay_video' : autoplay_video, 
    })

@stamped_view()
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

@stamped_view(schema=HTTPWebTimeSlice, ignore_extra_params=True)
def profile(request, schema, **kwargs):
    return handle_profile(request, schema, **kwargs)

@stamped_view(schema=HTTPWebTimeMapSlice, ignore_extra_params=True)
def map(request, schema, **kwargs):
    return handle_map(request, schema, **kwargs)

def handle_profile(request, schema, **kwargs):
    url_format = "/{screen_name}"
    prev_url   = None
    next_url   = None
    
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = schema.limit  or 25
    screen_name   = schema.screen_name
    ajax          = schema.ajax
    mobile        = schema.mobile
    
    del schema.ajax
    del schema.mobile
    
    friends       = []
    followers     = []
    
    if ajax and schema.user_id is not None:
        user        = None
        user_id     = schema.user_id
    else:
        user        = kwargs.get('user', stampedAPIProxy.getUser(dict(screen_name=schema.screen_name)))
        user_id     = user['user_id']
    
    # simple sanity check validation of user_id
    if utils.tryGetObjectId(user_id) is None:
        raise StampedInputError("invalid user_id")
    
    #utils.log(pprint.pformat(schema.dataExport()))
    schema_data = schema.dataExport()
    del schema_data['screen_name']
    schema_data['user_id'] = user_id
    
    stamps = stampedAPIProxy.getUserStamps(schema_data)
    
    if user is None:
        user = {
            'user_id' : user_id
        }
        
        if len(stamps) > 0:
            user2    = stamps[0]['user']
            user2_id = user2['user_id']
            
            if user2_id is None or user2_id != user_id:
                raise StampedInputError("mismatched user_id")
            else:
                user.update(user2)
        else:
            user = stampedAPIProxy.getUser(dict(user_id=user_id))
            
            if user['user_id'] is None or user['user_id'] != user_id:
                raise StampedInputError("mismatched user_id")
    
    if not (ajax | mobile):
        friends     = stampedAPIProxy.getFriends  (user_id, limit=3)
        followers   = stampedAPIProxy.getFollowers(user_id, limit=3)
        
        friends   = shuffle_split_users(friends)
        followers = shuffle_split_users(followers)
    
    #utils.log("USER:")
    #utils.log(pprint.pformat(user))
    
    #utils.log("STAMPS:")
    #utils.log(pprint.pformat(stamps))
    
    #utils.log("FRIENDS:")
    #utils.log(pprint.pformat(friends))
    
    #utils.log("FOLLOWERS:")
    #utils.log(pprint.pformat(followers))
    
    # modify schema for purposes of next / prev gallery nav links
    schema.ajax    = True
    schema.user_id = user['user_id']
    
    if schema.offset > 0:
        prev_url = format_url(url_format, schema, {
            'offset' : max(0, schema.offset - schema.limit), 
        })
    
    if len(stamps) >= schema.limit:
        next_url = format_url(url_format, schema, {
            'offset' : schema.offset + len(stamps), 
        })
    
    #utils.log("PREV: %s" % prev_url)
    #utils.log("NEXT: %s" % next_url)
    
    title   = "Stamped - %s" % user['screen_name']
    sdetail = kwargs.get('sdetail', None)
    stamp   = kwargs.get('stamp',   None)
    entity  = kwargs.get('entity',  None)
    url     = request.build_absolute_uri(request.get_full_path())
    
    body_classes = get_body_classes('profile', schema)
    if sdetail is not None:
        body_classes += " sdetail_popup";
    
    if sdetail is not None and entity is not None:
        title = "%s - %s" % (title, stamp['entity']['title'])
    
    template = 'profile-mobile.html' if mobile else 'profile.html'
    
    return stamped_render(request, template, {
        'user'                  : user, 
        'stamps'                : stamps, 
        
        'friends'               : friends, 
        'followers'             : followers, 
        
        'prev_url'              : prev_url, 
        'next_url'              : next_url, 
        
        'body_classes'          : body_classes, 
        'sdetail'               : sdetail, 
        'stamp'                 : stamp, 
        'entity'                : entity, 
        'title'                 : title, 
        'URL'                   : url, 
    }, preload=[ 'user', 'sdetail' ])

def handle_map(request, schema, **kwargs):
    schema.offset   = schema.offset or 0
    schema.limit    = 1000 # TODO: customize this
    screen_name     = schema.screen_name
    stamp_id        = schema.stamp_id
    ajax            = schema.ajax
    mobile          = schema.mobile
    
    uri             = request.get_full_path()
    url             = request.build_absolute_uri(uri)
    
    if mobile:
        redirect_uri = "/%s?category=place" % screen_name
        redirect_url = request.build_absolute_uri(redirect_uri)
        logs.info("redirecting mobile map from '%s' to: '%s'" % (uri, redirect_uri))
        
        return HttpResponseRedirect(redirect_url)
    
    del schema.stamp_id
    del schema.ajax
    del schema.mobile
    
    user        = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
    user_id     = user['user_id']
    
    # simple sanity check validation of user_id
    if utils.tryGetObjectId(user_id) is None:
        raise StampedInputError("invalid user_id")
    
    s = schema.dataExport()
    del s['screen_name']
    
    s['user_id']  = user_id
    s['category'] = 'place'
    
    stamps = stampedAPIProxy.getUserStamps(s)
    stamps = filter(lambda s: s['entity'].get('coordinates', None) is not None, stamps)
    
    for stamp in stamps:
        subcategory = stamp['entity']['subcategory']
        
        if '_' in subcategory:
            stamp['entity']['subcategory'] = subcategory.replace('_', ' ')
    
    body_classes = get_body_classes('map collapsed-header', schema)
    
    title = "Stamped - %s map" % user['screen_name']
    
    return stamped_render(request, 'map.html', {
        'user'          : user, 
        'stamps'        : stamps, 
        
        'stamp_id'      : stamp_id, 
        'body_classes'  : body_classes, 
        'title'         : title, 
        'URL'           : url, 
    }, preload=[ 'user', 'stamps', 'stamp_id' ])

@stamped_view(schema=HTTPStampDetail, ignore_extra_params=True)
def sdetail(request, schema, **kwargs):
    body_classes = get_body_classes('sdetail collapsed-header', schema)
    ajax         = schema.ajax
    
    del schema.ajax
    
    #import time
    #time.sleep(2)
    
    logs.info('SDETAIL: %s/%s/%s' % (schema.screen_name, schema.stamp_num, schema.stamp_title))
    
    user   = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
    stamp  = stampedAPIProxy.getStampFromUser(user['user_id'], schema.stamp_num)
    
    if stamp is None:
        raise StampedUnavailableError("stamp does not exist")
    
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
    
    template = 'sdetail.html'
    
    #users   = shuffle_split_users(users)
    entity  = stampedAPIProxy.getEntity(stamp['entity']['entity_id'])
    sdetail = stamped_render(request, template, {
        'user'               : user, 
        'feedback_users'     : users, 
        'stamp'              : stamp, 
        'entity'             : entity, 
    })
    
    if ajax:
        return sdetail
    else:
        return handle_profile(request, HTTPWebTimeSlice().dataImport({
            'screen_name'   : schema.screen_name
        }), user=user, sdetail=sdetail.content, stamp=stamp, entity=entity)

@stamped_view(schema=HTTPEntityId)
def menu(request, schema, **kwargs):
    entity  = stampedAPIProxy.getEntity(schema.entity_id)
    menu    = stampedAPIProxy.getEntityMenu(schema.entity_id)
    
    #utils.getFile(menu['attribution_image_link'])
    
    return stamped_render(request, 'menu.html', {
        'menu'   : menu, 
        'entity' : entity, 
    })

@stamped_view()
def test_view(request, **kwargs):
    user  = stampedAPIProxy.getUser(dict(screen_name='travis'))
    stamp = stampedAPIProxy.getStampFromUser(user['user_id'], 10)
    
    return stamped_render(request, 'test.html', {
        'user'  : user, 
        'stamp' : stamp
    })

@stamped_view(schema=HTTPStampId)
def popup_sdetail_social(request, schema, **kwargs):
    params = schema.dataExport()
    likes  = stampedAPIProxy.getLikes(schema.stamp_id)
    todos  = stampedAPIProxy.getTodos(schema.stamp_id)
    users  = []
    
    for user in likes:
        user['preview_type'] = 'like'
    
    for user in todos:
        user['preview_type'] = 'todo'
    
    users.extend(likes)
    users.extend(todos)
    
    users = shuffle_split_users(users)
    num_users = len(users)
    
    title = ""
    popup = "popup-sdetail-social"
    like  = "Like%s" % ("s" if len(likes) != 1 else "")
    todo  = "Todo%s" % ("s" if len(todos) != 1 else "")
    
    if len(likes) > 0:
        if len(todos) > 0:
            title = "%d %s and %d %s" % (len(likes), like, len(todos), todo)
        else:
            title = "%d %s" % (len(likes), like)
    elif len(todos) > 0:
        title = "%d %s" % (len(todos), todo)
        popup = "%s popup-todos" % popup
    
    return stamped_render(request, 'popup.html', {
        'popup_title' : title, 
        'popup_class' : popup, 
        'users'       : users, 
    })

@stamped_view(schema=HTTPUserId)
def popup_followers(request, schema, **kwargs):
    users = stampedAPIProxy.getFollowers(schema.user_id)
    num_users = len(users)
    
    return stamped_render(request, 'popup.html', {
        'popup_title' : "%d Followers" % num_users, 
        'popup_class' : 'popup-followers', 
        'users'       : users, 
    })

@stamped_view(schema=HTTPUserId)
def popup_following(request, schema, **kwargs):
    users = stampedAPIProxy.getFriends(schema.user_id)
    num_users = len(users)
    
    return stamped_render(request, 'popup.html', {
        'popup_title' : "Following %d" % num_users, 
        'popup_class' : 'popup-following', 
        'users'       : users, 
    })

