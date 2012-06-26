#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import api.HTTPSchemas
import os, utils

from django.http    import HttpResponse, HttpResponseRedirect
from schemas        import *
from helpers        import *

import travis_test

ENABLE_TRAVIS_TEST = (False and not IS_PROD)

def _is_static_profile_image(url):
    return url.lower().strip() == 'http://static.stamped.com/users/default.jpg'

def _get_body_classes(base, schema):
    has_category    = False
    has_subcategory = False
    body_classes    = base
    
    try:
        has_category    = (schema.category is not None)
        has_subcategory = (schema.subcategory is not None)
    except:
        pass
    
    if has_category:
        body_classes += " %s" % schema.category
    else:
        body_classes += " default"
    
    if has_subcategory:
        body_classes += " %s" % schema.subcategory
    
    return body_classes

# ensure friends and followers are randomly shuffled s.t. different users will 
# appear every page refresh, with preferential treatment always going to users 
# who have customized their profile image away from the default.
def _shuffle_split_users(users):
    has_image        = (lambda a: a.get('image_url', None) is not None)
    has_custom_image = (lambda a: has_image(a) and not _is_static_profile_image(a['image_url']))
    
    # find all users who have a custom profile image
    a0 = filter(has_custom_image, users)
    
    # find all users who have the default profile image
    a1 = filter(lambda a: not has_custom_image(a), users)
    
    # shuffle them both independently
    a0 = utils.shuffle(a0)
    a1 = utils.shuffle(a1)
    
    # and combine the results s.t. all users with custom profile images precede 
    # all those without custom profile images
    a0.extend(a1)
    
    return a0

@stamped_view()
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return stamped_render(request, 'index.html', {
        'autoplay_video' : autoplay_video, 
    })

@stamped_view()
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

@stamped_view(schema=HTTPWebTimeSlice)
def profile(request, schema, **kwargs):
    url_format = "/{screen_name}"
    prev_url   = None
    next_url   = None
    
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = schema.limit  or 25
    screen_name   = schema.screen_name
    ajax          = schema.ajax
    del schema.ajax
    
    friends       = []
    followers     = []
    
    if ENABLE_TRAVIS_TEST and schema.screen_name == 'travis' and (schema.sort is None or schema.sort == 'modified'):
        # useful debugging utility -- circumvent dev server to speed up reloads
        user        = travis_test.user
        user_id     = user['user_id']
        
        stamps      = travis_test.stamps
        
        if schema.category is not None:
            stamps  = filter(lambda s: s['entity']['category'] == schema.category or ('coordinates' in s['entity'] and s['entity']['coordinates'] is not None and schema.category == 'place'), stamps)
        
        if schema.subcategory is not None:
            stamps  = filter(lambda s: s['entity']['subcategory'] == schema.subcategory, stamps)
        
        stamps      = stamps[schema.offset : (schema.offset + schema.limit if schema.limit is not None else len(stamps))]
    else:
        if ajax and schema.user_id is not None:
            user        = None
            user_id     = schema.user_id
        else:
            user        = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
            user_id     = user['user_id']
        
        """
        r = "4e57048accc2175fcd000001"
        utils.log(user_id)
        utils.log(r)
        assert user_id == r
        """
        
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
    
    if not ajax:
        if ENABLE_TRAVIS_TEST:
            friends     = travis_test.friends
            followers   = travis_test.followers
        else:
            params      = dict(user_id=user_id, screen_name=screen_name)
            friends     = stampedAPIProxy.getFriends  (params, limit=10)
            followers   = stampedAPIProxy.getFollowers(params, limit=10)
        
        friends   = _shuffle_split_users(friends)
        followers = _shuffle_split_users(followers)
    
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
    
    body_classes = _get_body_classes('profile', schema)
    
    return stamped_render(request, 'profile.html', {
        'user'                  : user, 
        'stamps'                : stamps, 
        
        'friends'               : friends, 
        'followers'             : followers, 
        
        'prev_url'              : prev_url, 
        'next_url'              : next_url, 
        
        'body_classes'          : body_classes, 
    }, preload=[ 'user' ])

@stamped_view(schema=HTTPWebTimeSlice)
def map(request, schema, **kwargs):
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = 1000 # TODO: customize this
    screen_name = schema.screen_name
    del schema.ajax
    
    if ENABLE_TRAVIS_TEST and schema.screen_name == 'travis':
        # useful debugging utility -- circumvent dev server to speed up reloads
        user        = travis_test.user
        user_id     = user['user_id']
        
        stamps      = filter(lambda s: s['entity'].get('coordinates', None) is not None, travis_test.stamps)
        stamps      = stamps[schema.offset : (schema.offset + schema.limit if schema.limit is not None else len(stamps))]
    else:
        user        = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
        user_id     = user['user_id']
        
        # simple sanity check validation of user_id
        if utils.tryGetObjectId(user_id) is None:
            raise StampedInputError("invalid user_id")
        
        s = schema.dataExport()
        del s['screen_name']
        s['user_id']  = user_id
        s['category'] = 'place'
        
        stamps      = stampedAPIProxy.getUserStamps(s)
    
    stamps = filter(lambda s: s['entity'].get('coordinates', None) is not None, stamps)
    
    for stamp in stamps:
        subcategory = stamp['entity']['subcategory']
        
        if '_' in subcategory:
            stamp['entity']['subcategory'] = subcategory.replace('_', ' ')
    
    body_classes = _get_body_classes('map collapsed-header', schema)
    
    return stamped_render(request, 'map.html', {
        'user'          : user, 
        'stamps'        : stamps, 
        
        'body_classes'  : body_classes, 
    }, preload=[ 'user', 'stamps' ])

@stamped_view(schema=HTTPStampDetail)
def sdetail(request, schema, **kwargs):
    body_classes = _get_body_classes('sdetail collapsed-header', schema)
    
    #import time
    #time.sleep(2)
    
    logs.info('%s/%s/%s' % (schema.screen_name, schema.stamp_num, schema.stamp_title))
    
    if ENABLE_TRAVIS_TEST and schema.screen_name == 'travis':
        user  = travis_test.user
        #stamp = travis_test.stamps[(-schema.stamp_num) - 1]
        
        #stamp  = travis_test.sdetail_stamp
        #entity = travis_test.sdetail_entity
    else:
        user   = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
    
    stamp  = stampedAPIProxy.getStampFromUser(user['user_id'], schema.stamp_num)
    
    if stamp is None:
        raise StampedUnavailableError("stamp does not exist")
    
    entity = stampedAPIProxy.getEntity(stamp['entity']['entity_id'])
    
    """
    from pprint import pprint
    pprint(stamp)
    
    from pprint import pprint
    pprint(entity)
    """
    
    #stamp = Stamp().importData(stamp)
    '''
    encodedStampTitle = encodeStampTitle(stamp.entity.title)
    
    if encodedStampTitle != schema.stamp_title:
        i = encodedStampTitle.find('.')
        if i != -1:
            encodedStampTitle = encodedStampTitle[:i]
        
        if encodedStampTitle != schema.stamp_title:
            raise Exception("Invalid stamp title: '%s' (received) vs '%s' (stored)" % 
                            (schema.stamp_title, encodedStampTitle))
    '''
    
    return stamped_render(request, 'sdetail.html', {
        'user'   : user, 
        'stamp'  : stamp, 
        'entity' : entity, 
    })

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
    return stamped_render(request, 'test.html', { })

@stamped_view(schema=HTTPStampId)
def popup_likes(request, schema, **kwargs):
    users = stampedAPIProxy.getLikes(schema.dataExport())
    num_likes = len(users)
    
    return stamped_render(request, 'popup-likes.html', {
        'num_likes' : num_likes, 
        'users'     : users, 
    })

@stamped_view(schema=HTTPStampId)
def popup_todos(request, schema, **kwargs):
    users = stampedAPIProxy.getTodos(schema.dataExport())
    num_todos = len(users)
    
    return stamped_render(request, 'popup-todos.html', {
        'num_todos' : num_todos, 
        'users'     : users, 
    })

