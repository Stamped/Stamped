#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pprint, utils
import libs.sms

import servers.web2.settings as settings

from django.views.decorators.http   import require_http_methods
from django.http                    import HttpResponseRedirect

from servers.web2.core.schemas      import *
from servers.web2.core.helpers      import *

# TODO: stricter input schema validation

TRAVIS = False
import travis_test

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
        if TRAVIS:
            user    = travis_test.user
        else:
            user    = kwargs.get('user', stampedAPIProxy.getAccountByScreenName(schema.screen_name))
        
        user_id     = user['user_id']
    
    # simple sanity check validation of user_id
    if utils.tryGetObjectId(user_id) is None:
        raise StampedInputError("invalid user_id")
    
    #utils.log(pprint.pformat(schema.dataExport()))
    schema_data = schema.dataExport()
    del schema_data['screen_name']
    schema_data['user_id'] = user_id
    
    if TRAVIS:
        stamps = travis_test.stamps
    else:
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
            user = stampedAPIProxy.getAccount(user_id)
            
            if user['user_id'] is None or user['user_id'] != user_id:
                raise StampedInputError("mismatched user_id")
    
    """
    if not (ajax | mobile):
        friends     = stampedAPIProxy.getFriends  (user_id, limit=3)
        followers   = stampedAPIProxy.getFollowers(user_id, limit=3)
        
        friends   = shuffle_split_users(friends)
        followers = shuffle_split_users(followers)
    """
    
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
    
    #if not mobile:
    #    body_classes += " wide-body";
    
    if sdetail is not None and entity is not None:
        title = "%s - %s" % (title, stamp['entity']['title'])
    
    template = 'profile.html'
    
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
        'mobile'                : mobile, 
    }, preload=[ 'user', 'sdetail', 'mobile' ])

def handle_map(request, schema, **kwargs):
    screen_name     = schema.screen_name
    stamp_id        = schema.stamp_id
    ajax            = schema.ajax
    lite            = schema.lite
    mobile          = schema.mobile
    schema.offset   = schema.offset or 0
    schema.limit    = 25 if lite else 1000 # TODO: customize this
    
    uri             = request.get_full_path()
    url             = request.build_absolute_uri(uri)
    
    if mobile:
        redirect_uri = "/%s?category=place" % screen_name
        redirect_url = request.build_absolute_uri(redirect_uri)
        logs.info("redirecting mobile map from '%s' to: '%s'" % (uri, redirect_uri))
        
        return HttpResponseRedirect(redirect_url)
    
    del schema.stamp_id
    del schema.ajax
    del schema.lite
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
    
    if len(stamps) <= 0:
        redirect_uri = "/%s?category=place" % screen_name
        redirect_url = request.build_absolute_uri(redirect_uri)
        logs.info("redirecting empty map from '%s' to: '%s'" % (uri, redirect_uri))
        
        return HttpResponseRedirect(redirect_url)
    
    for stamp in stamps:
        subcategory = stamp['entity']['subcategory']
        
        if '_' in subcategory:
            stamp['entity']['subcategory'] = subcategory.replace('_', ' ')
    
    body_classes = get_body_classes('map collapsed-header', schema)
    
    title = "Stamped - %s map" % user['screen_name']
    
    return stamped_render(request, 'map.html', {
        'user'          : user, 
        'stamps'        : stamps, 
        'lite'          : lite, 
        
        'stamp_id'      : stamp_id, 
        'body_classes'  : body_classes, 
        'title'         : title, 
        'URL'           : url, 
        'mobile'        : mobile, 
    }, preload=[ 'user', 'stamps', 'stamp_id', 'lite' ])

@stamped_view(schema=HTTPStampDetail, ignore_extra_params=True)
def sdetail(request, schema, **kwargs):
    body_classes = get_body_classes('sdetail collapsed-header', schema)
    ajax         = schema.ajax
    
    del schema.ajax
    
    #import time
    #time.sleep(2)
    
    logs.info('SDETAIL: %s/%s/%s' % (schema.screen_name, schema.stamp_num, schema.stamp_title))
    
    #user   = stampedAPIProxy.getUser(dict(screen_name=schema.screen_name))
    user   = stampedAPIProxy.getAccountByScreenName(schema.screen_name)
    stamp  = stampedAPIProxy.getStampFromUser(user['user_id'], schema.stamp_num)
    
    if stamp is None:
        raise StampedUnavailableError("stamp does not exist")
    
    stamp    = convert_stamp(stamp)
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
        'entity'             : entity
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

@stamped_view()
def test_view(request, **kwargs):
    user  = stampedAPIProxy.getUser(dict(screen_name='travis'))
    stamp = stampedAPIProxy.getStampFromUser(user['user_id'], 10)
    
    return stamped_render(request, 'test.html', {
        'user'  : user, 
        'stamp' : stamp
    })

@stamped_view()
def temp_view(request, **kwargs):
    return stamped_render(request, 'temp.html', {
        'N' : range(10)
    })

@stamped_view(schema=HTTPDownloadAppSchema)
@require_http_methods(["GET", "POST"])
def download_app(request, schema, **kwargs):
    sms_client = libs.sms.globalSMSClient()
    result = sms_client.send_sms(schema.phone_number)
    
    return transform_output(True)

@stamped_view()
def download(request, **kwargs):
    return HttpResponseRedirect(settings.STAMPED_DOWNLOAD_APP_LINK)

@stamped_view(schema=HTTPIndexSchema, ignore_extra_params=True)
def index(request, schema, **kwargs):
    tastemakers = [
        {
            'screen_name'       : 'mariobatali', 
            'image_url'         : 'http://static.stamped.com/users/mariobatali-60x60.jpg', 
            'color_primary'     : 'FF7E00', 
            'color_secondary'   : 'FFEA00', 
        }, 
        {
            'screen_name'       : 'urbandaddy', 
            'image_url'         : 'http://static.stamped.com/users/urbandaddy-60x60.jpg', 
            'color_primary'     : '9A0004', 
            'color_secondary'   : '000130', 
        }, 
        {
            'screen_name'       : 'nymag', 
            'image_url'         : 'http://static.stamped.com/users/nymag-60x60.jpg', 
            'color_primary'     : 'A7D9ED', 
            'color_secondary'   : 'A7D9ED', 
        }, 
        {
            'screen_name'       : 'michaelkors', 
            'image_url'         : 'http://static.stamped.com/users/michaelkors-60x60.jpg', 
            'color_primary'     : '190000', 
            'color_secondary'   : 'FFEDCC', 
        }, 
        {
            'screen_name'       : 'parislemon', 
            'image_url'         : 'http://static.stamped.com/users/parislemon-60x60.jpg', 
            'color_primary'     : '0049FF', 
            'color_secondary'   : 'F4FF00', 
        }, 
    ]
    
    body_classes = "index %s" % ("intro" if schema.intro else "main")
    
    return stamped_render(request, 'index.html', {
        'body_classes'      : body_classes, 
        'tastemakers'       : tastemakers, 
        'page'              : 'index', 
        'title'             : 'Stamped', 
        'mobile'            : schema.mobile
    })

@stamped_view()
def about(request, **kwargs):
    body_classes = "about main main-animating"
    mobile   = kwargs.get('mobile', False)
    
    founders = [
        {
            'name'              : 'Robby Stein', 
            'subtitle'          : 'CEO &amp; Co-Founder', 
            'screen_name'       : 'robby', 
            'color_primary'     : '00119F', 
            'color_secondary'   : '6C7DFF', 
            'desc'              : "Robby worked at Google for 4 years, on Gmail launches and most recently as Product Manager for the Ad Exchange. He built the first Stamped prototype in his tiny NYC apartment. He graduated from Northwestern and is not Bart's brother.", 
            'twitter'           : 'rmstein', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Kevin Palms', 
            'subtitle'          : 'Co-Founder, Technology', 
            'screen_name'       : 'kevin', 
            'color_primary'     : '070067', 
            'color_secondary'   : '005B9A', 
            'desc'              : 'Kevin previously led development of risk analytics technology at a hedge fund in New York. He and Robby also built a social calendering app together at Northwestern; a movie about it, "The Social Calendar," has not yet been made.', 
            'twitter'           : 'kevinpalms', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Bart Stein', 
            'subtitle'          : 'Co-Founder, Marketing &amp; Partnerships', 
            'screen_name'       : 'bart', 
            'color_primary'     : '010048', 
            'color_secondary'   : '570000', 
            'desc'              : 'Bart previously worked at the Google Creative Lab, where he contributed to Google\'s first Super Bowl campaign. He also worked for David Pogue, the NY Times tech columnist. He graduated from Brown and is not Robby\'s brother.', 
            'twitter'           : 'bartjstein', 
            'inner'             : range(2), 
        }, 
    ]
    
    team = [
        {
            'name'              : 'Paul Eastlund', 
            'subtitle'          : 'VP, Engineering', 
            'screen_name'       : 'pauleastlund', 
            'color_primary'     : 'FF7E00', 
            'color_secondary'   : 'FFEA00', 
            'desc'              : 'Paul previously worked at Google for 5 years as an engineer where he led development teams on Google Maps. The ultimate startup hipster, Paul lives in rural Connecticut with his wife, three children, and dog. He holds a B.A. and M.Eng. in Computer Science from Cornell.', 
            'twitter'           : 'pauleastlund', 
            'inner'             : range(1), 
        }, 
        {
            'name'              : 'Travis Fischer', 
            'subtitle'          : 'Backend Architect &amp; Web Lead', 
            'screen_name'       : 'travis', 
            'color_primary'     : 'FF6000', 
            'color_secondary'   : 'FF6000', 
            'desc'              : 'Travis previously worked at Microsoft on a next-generation OS incubator and before that at Pixar on the film Up. He got his start programming TI calculator <a href="http://www.ticalc.org/archives/files/authors/78/7869.html">games</a> in high school and graduated from Brown with a B.S. in Computer Science &amp; Math.', 
            'twitter'           : 'fisch0920', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Anthony Cafaro', 
            'subtitle'          : 'Lead Product Designer', 
            'screen_name'       : 'anthony', 
            'color_primary'     : 'FFF2C7', 
            'color_secondary'   : 'FFE1B4', 
            'desc'              : 'Anthony was previously at the Google Creative Lab as a designer. He graduated from the School of Visual Arts and is by far the coolest person at Stamped.', 
            'twitter'           : 'anthonycafaro', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Landon Judkins', 
            'subtitle'          : 'Software Engineer, Mobile Lead', 
            'screen_name'       : 'landon', 
            'color_primary'     : '004AB2', 
            'color_secondary'   : '066800', 
            'desc'              : 'Landon previously built software for a large European manufacturing company. He also designs programming languages in his spare time. He graduated from Brown with an B.A. in Computer Science and is the best disc golf player on the Stamped team.', 
            'twitter'           : 'landonjudkins', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Liz Walton', 
            'subtitle'          : 'Marketing Manager', 
            'screen_name'       : 'lizwalton', 
            'color_primary'     : '00BBAD', 
            'color_secondary'   : '9CFFFA', 
            'desc'              : 'Liz was previously at Weber Shandwick where she managed social media for large consumer brands. She is the best female employee at Stamped, and graduated from Northwestern University.', 
            'twitter'           : 'lizwalton', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Mike Lowin', 
            'subtitle'          : 'Software Engineer', 
            'screen_name'       : 'ml', 
            'color_primary'     : 'FF7E00', 
            'color_secondary'   : 'FFEA00', 
            'desc'              : 'Mike previously worked with Kevin at a hedge fund building analytics software, and apparently liked him enough to want to join Stamped (we were surprised too). He graduated from Vassar College with a B.A. in Computer Science.', 
            'twitter'           : 'michaellowin', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Geoff Liu', 
            'subtitle'          : 'Software Engineer', 
            'screen_name'       : 'geoffliu', 
            'color_primary'     : 'FAD1CC', 
            'color_secondary'   : 'E70D4B', 
            'desc'              : 'Geoff worked at Google as an engineer on Google Maps. He is fluent in both Mandarin and English and can translate in both directions synchronously. He graduated from Cornell with a B.A. in Math and Computer Science.', 
            'twitter'           : 'geoff_liu', 
            'inner'             : range(2), 
        }, 
        {
            'name'              : 'Joey Staehle', 
            'subtitle'          : 'Software Engineering Intern', 
            'screen_name'       : 'jstaehle', 
            'color_primary'     : 'E00058', 
            'color_secondary'   : 'FFD494', 
            'desc'              : 'Joey is Stamped\'s first intern and has spent the summer honing his engineering and video game skills. He is currently enrolled at Cornell and plans to graduate with a B.S. in Computer Science in 2013.', 
            'twitter'           : 'joeystaehle', 
            'inner'             : range(2), 
        }, 
    ]
    
    advisors = [
        {
            'name'              : 'Mario Batali', 
            'screen_name'       : 'mariobatali', 
            'color_primary'     : 'FF7E00', 
            'color_secondary'   : 'FFEA00', 
            'desc'              : "With nineteen restaurants, nine cookbooks and a host of television shows including ABC's The Chew, Mario Batali is one of the most recognized and respected chefs working in America today. In 2008, Mario started the Mario Batali Foundation with the mission of feeding, protecting, educating, and empowering children. To learn more about Mario's mission, visit <a href='http://www.mariobatalifoundation.org'>www.mariobatalifoundation.org</a>.", 
            'twitter'           : 'mariobatali', 
        }, 
        {
            'name'              : 'Kevin Systrom', 
            'screen_name'       : 'kevinsystrom', 
            'color_primary'     : '51C4BB', 
            'color_secondary'   : '91EDE8', 
            'desc'              : "Kevin Systrom is the CEO and co-founder of <a href='http://instagram.com/'>Instagram</a>, the popular photo-sharing service with over 50 million users and was recently acquired by Facebook. got his first taste of the startup world as an intern at Odeo, which later became Twitter. He also spent two years at Google, working on Gmail and Google Reader. Kevin graduated from Stanford University in 2006 with a BS in Management Science &amp; Engineering.", 
            'twitter'           : 'kevin', 
        }, 
    ]
    
    return stamped_render(request, 'about.html', {
        'body_classes'      : body_classes, 
        'page'              : 'about', 
        'founders'          : founders, 
        'team'              : team, 
        'advisors'          : advisors, 
        'title'             : 'Stamped - About Us', 
        'mobile'            : mobile, 
    })

@stamped_view()
def jobs(request, **kwargs):
    body_classes = "jobs main main-animating"
    mobile       = schema.mobile
    
    return stamped_render(request, 'jobs.html', {
        'body_classes'      : body_classes, 
        'page'              : 'jobs', 
        'title'             : 'Stamped - Jobs', 
        'mobile'            : mobile, 
    })

@stamped_view()
def legal(request, **kwargs):
    body_classes = "legal main"
    mobile       = kwargs.get('mobile', False)
    
    return stamped_render(request, 'legal.html', {
        'body_classes'      : body_classes, 
        'page'              : 'legal', 
        'title'             : 'Stamped - Legal', 
        'mobile'            : mobile, 
    }, preload=[ 'page' ])

@stamped_view()
def licenses(request, **kwargs):
    body_classes = "legal main"
    mobile       = kwargs.get('mobile', False)
    
    return stamped_render(request, 'legal.html', {
        'body_classes'      : body_classes, 
        'page'              : 'licenses', 
        'title'             : 'Stamped - Licenses', 
        'mobile'            : mobile, 
    }, preload=[ 'page' ])

@stamped_view()
def privacy_policy(request, **kwargs):
    body_classes = "legal main"
    mobile       = kwargs.get('mobile', False)
    
    return stamped_render(request, 'legal.html', {
        'body_classes'      : body_classes, 
        'page'              : 'privacy-policy', 
        'title'             : 'Stamped - Privacy Policy', 
        'mobile'            : mobile, 
    }, preload=[ 'page' ])

@stamped_view()
def terms_of_service(request, **kwargs):
    body_classes = "legal main"
    mobile       = kwargs.get('mobile', False)
    
    return stamped_render(request, 'legal.html', {
        'body_classes'      : body_classes, 
        'page'              : 'terms-of-service', 
        'title'             : 'Stamped - Terms of Service', 
        'mobile'            : mobile, 
    }, preload=[ 'page' ])

@stamped_view()
def faq(request, **kwargs):
    body_classes = "legal faq main"
    mobile       = kwargs.get('mobile', False)
    
    return stamped_render(request, 'faq.html', {
        'body_classes'      : body_classes, 
        'page'              : 'faq', 
        'title'             : 'Stamped - FAQ', 
        'mobile'            : mobile, 
    }, preload=[ 'page' ])

