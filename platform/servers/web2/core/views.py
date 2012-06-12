#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import api.HTTPSchemas
import os, utils

from django.http    import HttpResponse, HttpResponseRedirect
from api.Schemas    import *
from helpers        import *

import travis_test

ENABLE_TRAVIS_TEST = (False and not IS_PROD)

def _is_static_profile_image(url):
    return url.lower().strip() == 'http://static.stamped.com/users/default.jpg'

def _get_body_classes(base, schema):
    has_category = False
    body_classes = base
    
    try:
        has_category = (schema.category is not None)
    except:
        pass
    
    if has_category:
        body_classes += " %s" % schema.category
    else:
        body_classes += " default"
    
    return body_classes

# ensure friends and followers are randomly shuffled s.t. different users will 
# appear every page refresh, with preferential treatment always going to users 
# who have customized their profile image away from the default.
def _shuffle_split_users(users):
    return users
    """
    has_image        = (lambda a: a['image'] and a['image']['sizes'] and len(a['image']['sizes']) > 0)
    has_custom_image = (lambda a: has_image(a) and not _is_static_profile_image(a['image']['sizes'][0]['url']))
    
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
    """

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
        user        = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
        user_id     = user['user_id']
        
        #utils.log(pprint.pformat(schema.dataExport()))
        s = schema.dataExport()
        del s['screen_name']
        s['user_id'] = user_id
        
        stamps      = stampedAPIProxy.getUserStamps(s)
    
    if ENABLE_TRAVIS_TEST:
        friends     = travis_test.friends
        followers   = travis_test.followers
    else:
        friends     = stampedAPIProxy.getFriends(dict(user_id=user_id, screen_name=schema.screen_name))
        followers   = stampedAPIProxy.getFollowers(dict(user_id=user_id, screen_name=schema.screen_name))
    
    main_cluster    = { }
    
    #utils.log("USER:")
    #utils.log(pprint.pformat(user))
    
    #utils.log("STAMPS:")
    #utils.log(pprint.pformat(stamps))
    
    #utils.log("FRIENDS:")
    #utils.log(pprint.pformat(friends))
    
    #utils.log("FOLLOWERS:")
    #utils.log(pprint.pformat(followers))
    
    """
    if schema.category == 'place':
        earthRadius = 3959.0 # miles
        clusters    = [ ]
        trivial     = True
        
        # find stamp clusters
        for stamp in stamps:
            entity = stamp['entity']
            if 'coordinates' not in entity or entity['coordinates'] is None:
                continue
            
            # TODO: really should be retaining this for stamps overall instead of just subset here...
            
            coords = api.HTTPSchemas._coordinatesFlatToDict(entity['coordinates'])
            found_cluster = False
            
            ll = [ coords['lat'], coords['lng'] ]
            #print "%s) %s" % (stamp.title, ll)
            
            for cluster in clusters:
                dist = earthRadius * utils.get_spherical_distance(ll, cluster['avg'])
                #print "%s) %s vs %s => %s (%s)" % (stamp.title, ll, cluster['avg'], dist, cluster['data'])
                
                if dist < 10:
                    cluster['data'].append((ll[0], ll[1]))
                    
                    len_cluster   = len(cluster['data'])
                    found_cluster = True
                    trivial       = False
                    
                    cluster['sum'][0] = cluster['sum'][0] + ll[0]
                    cluster['sum'][1] = cluster['sum'][1] + ll[1]
                    
                    cluster['avg'][0] = cluster['sum'][0] / len_cluster
                    cluster['avg'][1] = cluster['sum'][1] / len_cluster
                    
                    #print "%s) %d %s" % (stamp.title, len_cluster, cluster)
                    break
            
            if not found_cluster:
                clusters.append({
                    'avg'  : [ ll[0], ll[1] ], 
                    'sum'  : [ ll[0], ll[1] ], 
                    'data' : [ (ll[0], ll[1]) ], 
                })
        
        clusters_out = []
        if trivial:
            clusters_out = clusters
        else:
            # attempt to remove trivial clusters as outliers
            for cluster in clusters:
                if len(cluster['data']) > 1:
                    clusters_out.append(cluster)
            
            if len(clusters_out) <= 0:
                clusters_out.append(clusters[0])
        
        if len(clusters) > 0:
            clusters = sorted(clusters_out, key=lambda c: len(c['data']), reverse=True)
            
            for cluster in clusters:
                utils.log(pprint.pformat(cluster))
            
            main_cluster = clusters[0]
            main_cluster = {
                'coordinates' : "%f,%f" % (main_cluster['avg'][0], main_cluster['avg'][1]), 
                'markers'     : list("%f,%f" % (c[0], c[1]) for c in main_cluster['data']), 
            }
    """
    
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
    
    body_classes = _get_body_classes('profile', schema)
    
    return stamped_render(request, 'profile.html', {
        'user'                  : user, 
        'stamps'                : stamps, 
        
        'friends'               : friends, 
        'followers'             : followers, 
        
        'prev_url'              : prev_url, 
        'next_url'              : next_url, 
        
        'body_classes'          : body_classes, 
        'main_stamp_cluster'    : main_cluster, 
    }, preload=[ 'user' ])

@stamped_view(schema=HTTPWebTimeSlice)
def map(request, schema, **kwargs):
    # TODO: enforce stricter validity checking on offset and limit
    
    schema.offset = schema.offset or 0
    schema.limit  = 1000 # TODO: customize this
    
    if ENABLE_TRAVIS_TEST and schema.screen_name == 'travis':
        # useful debugging utility -- circumvent dev server to speed up reloads
        user        = travis_test.user
        user_id     = user['user_id']
        
        stamps      = filter(lambda s: s['entity'].get('coordinates', None) is not None, travis_test.stamps)
        stamps      = stamps[schema.offset : (schema.offset + schema.limit if schema.limit is not None else len(stamps))]
    else:
        user        = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
        user_id     = user['user_id']
        
        s = schema.dataExport()
        del s['screen_name']
        s['user_id'] = user_id
        
        stamps      = stampedAPIProxy.getUserStamps(s)
    
    # TODO: bake this into stampedAPIProxy request
    stamps    = filter(lambda s: s['entity'].get('coordinates', None) is not None, stamps)
    
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


@stamped_view()
def test_view(request, **kwargs):
    return stamped_render(request, 'test.html', { })

@stamped_view(schema=HTTPEntityId)
def menu(request, schema, **kwargs):
    entity  = stampedAPIProxy.getEntity(schema.entity_id)
    menu    = stampedAPIProxy.getEntityMenu(schema.entity_id)
    
    #utils.getFile(menu['attribution_image_link'])
    
    return stamped_render(request, 'menu.html', {
        'menu'   : menu, 
        'entity' : entity, 
    })

