#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from django.http    import HttpResponse, HttpResponseRedirect
from Schemas        import *
from helpers        import *

import travis_test

@stamped_view()
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return stamped_render(request, 'index.html', {
        'autoplay_video' : autoplay_video, 
    })

@stamped_view()
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

@stamped_view(schema=HTTPUserCollectionSlice)
def profile(request, schema, **kwargs):
    url_format = "/{screen_name}"
    prev_url   = None
    next_url   = None
    
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = schema.limit  or 25
    
    if not IS_PROD and schema.screen_name == 'travis':
        # useful debugging utility -- circumvent dev server to speed up reloads
        user        = travis_test.user
        user_id     = user['user_id']
        
        stamps      = travis_test.stamps[schema.offset : schema.offset + schema.limit]
        friends     = travis_test.friends
        followers   = travis_test.followers
    else:
        user        = stampedAPIProxy.getUser(screen_name=schema.screen_name)
        user_id     = user['user_id']
        
        stamps      = stampedAPIProxy.getUserStamps(**schema.exportSparse())
        friends     = stampedAPIProxy.getFriends(user_id=user_id, screen_name=schema.screen_name)
        followers   = stampedAPIProxy.getFollowers(user_id=user_id, screen_name=schema.screen_name)
    
    def _is_static_profile_image(url):
        return url.lower().strip() == 'http://static.stamped.com/users/default.jpg'
    
    # ensure friends and followers are randomly shuffled s.t. different users will 
    # appear every page refresh, with preferential treatment always going to users 
    # who have customized their profile image away from the default.
    def _shuffle_split_users(users):
        # find all users who have a custom profile image
        a0 = filter(lambda a: a['image_url'] and not _is_static_profile_image(a['image_url']), users)
        
        # find all users who have the default profile image
        a1 = filter(lambda a: not (a['image_url'] and _is_static_profile_image(a['image_url'])), users)
        
        # shuffle them both independently
        a0 = utils.shuffle(a0)
        a1 = utils.shuffle(a1)
        
        # and combine the results s.t. all users with custom profile images precede 
        # all those without custom profile images
        a0.extend(a1)
        
        return a0
    
    friends   = _shuffle_split_users(friends)
    followers = _shuffle_split_users(followers)
    
    if schema.offset > 0:
        prev_url = format_url(url_format, schema, {
            'offset' : max(0, schema.offset - schema.limit), 
        })
    
    if len(stamps) >= schema.limit:
        next_url = format_url(url_format, schema, {
            'offset' : schema.offset + len(stamps), 
        })
    
    return stamped_render(request, 'profile.html', {
        'user'      : user, 
        'stamps'    : stamps, 
        
        'friends'   : friends, 
        'followers' : followers, 
        
        'prev_url'  : prev_url, 
        'next_url'  : next_url, 
    }, preload=[ 'user' ])

@stamped_view(schema=HTTPUserCollectionSlice)
def map(request, schema, **kwargs):
    url_format = "/{screen_name}/map"
    prev_url   = None
    next_url   = None
    
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = schema.limit  or 25
    
    if not IS_PROD and schema.screen_name == 'travis':
        # useful debugging utility -- circumvent dev server to speed up reloads
        user        = travis_test.user
        user_id     = user['user_id']
        
        stamps      = filter(lambda s: 'coordinates' in s['entity'], travis_test.stamps)
        stamps      = stamps[schema.offset : schema.offset + schema.limit]
        
        friends     = travis_test.friends
        followers   = travis_test.followers
    else:
        user        = stampedAPIProxy.getUser(screen_name=schema.screen_name)
        user_id     = user['user_id']
        
        stamps      = stampedAPIProxy.getUserStamps(**schema.exportSparse())
        friends     = stampedAPIProxy.getFriends(user_id=user_id, screen_name=schema.screen_name)
        followers   = stampedAPIProxy.getFollowers(user_id=user_id, screen_name=schema.screen_name)
    
    def _is_static_profile_image(url):
        return url.lower().strip() == 'http://static.stamped.com/users/default.jpg'
    
    # ensure friends and followers are randomly shuffled s.t. different users will 
    # appear every page refresh, with preferential treatment always going to users 
    # who have customized their profile image away from the default.
    def _shuffle_split_users(users):
        # find all users who have a custom profile image
        a0 = filter(lambda a: a['image_url'] and not _is_static_profile_image(a['image_url']), users)
        
        # find all users who have the default profile image
        a1 = filter(lambda a: not (a['image_url'] and _is_static_profile_image(a['image_url'])), users)
        
        # shuffle them both independently
        a0 = utils.shuffle(a0)
        a1 = utils.shuffle(a1)
        
        # and combine the results s.t. all users with custom profile images precede 
        # all those without custom profile images
        a0.extend(a1)
        
        return a0
    
    friends   = _shuffle_split_users(friends)
    followers = _shuffle_split_users(followers)
    
    if schema.offset > 0:
        prev_url = format_url(url_format, schema, {
            'offset' : max(0, schema.offset - schema.limit), 
        })
    
    if len(stamps) >= schema.limit:
        next_url = format_url(url_format, schema, {
            'offset' : schema.offset + len(stamps), 
        })
    
    return stamped_render(request, 'map.html', {
        'user'      : user, 
        'stamps'    : stamps, 
        
        'friends'   : friends, 
        'followers' : followers, 
        
        'prev_url'  : prev_url, 
        'next_url'  : next_url, 
    }, preload=[ 'user' ])

