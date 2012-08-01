#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import travis_test

from api.MongoStampedAPI            import globalMongoStampedAPI
from api.MongoStampedAuth           import MongoStampedAuth
from django.views.decorators.http   import require_http_methods
from django.http                    import HttpResponseRedirect

from errors                         import *
from servers.web2.core.schemas      import *
from servers.web2.core.helpers      import *

g_stamped_auth = MongoStampedAuth()

@stamped_view(schema=HTTPResetPasswordViewSchema, no_cache=True)
def password_reset(request, schema, **kwargs):
    body_classes = "password_reset main"
    token        = schema.token
    
    # Verify token is valid
    user_id = g_stamped_auth.verifyPasswordResetToken(token)
    
    if user_id is None:
        raise StampedInputError("invalid token")
    
    account = stampedAPIProxy.getAccount(user_id)
    
    if account is None:
        raise StampedInputError("invalid account")
    
    try:
        auth_service = account['auth_service']
    except Exception as e:
        logs.warning("Unable to get auth service: %s" % e)
        auth_service = None

    if auth_service != 'stamped':
        raise StampedInputError("Account password not managed by Stamped for user '%s' (primary account service is '%s')" % (account['screen_name'], auth_service))
    
    return stamped_render(request, 'password_reset.html', {
        'body_classes'      : body_classes, 
        'page'              : 'password_reset', 
        'title'             : 'Stamped - Reset Password', 
        'token'             : token
    }, preload=[ 'token' ])

@stamped_view(no_cache=True)
def password_forgot(request, **kwargs):
    body_classes = "password_forgot main"
    
    return stamped_render(request, 'password.html', {
        'body_classes'      : body_classes, 
        'page'              : 'password_forgot', 
        'title'             : 'Stamped - Forgot Password', 
    })

@stamped_view(schema=HTTPSettingsSchema, no_cache=True)
def alert_settings(request, schema, **kwargs):
    body_classes = "settings main"
    token        = schema.token
    
    if False: # testing
        user = travis_test.user
        
        settings = {
            'alerts_credits_apns'   : False, 
            'alerts_credits_email'  : False, 
            
            'alerts_likes_apns'     : True, 
            'alerts_likes_email'    : False, 
            
            'alerts_todos_apns'     : True, 
            'alerts_todos_email'    : True, 
            
            'alerts_mentions_apns'  : True, 
            'alerts_mentions_email' : True, 
            
            'alerts_comments_apns'  : False, 
            'alerts_comments_email' : True, 
            
            'alerts_replies_apns'   : True, 
            'alerts_replies_email'  : True, 
            
            'alerts_followers_apns' : True, 
            'alerts_followers_email': False, 
            
            'alerts_friends_apns'   : True, 
            'alerts_friends_email'  : True, 
            
            'alerts_actions_apns'   : False, 
            'alerts_actions_email'  : True, 
        }
    else:
        user_id  = g_stamped_auth.verifyEmailAlertToken(token)
        account  = stampedAPIProxy.getAccount(user_id)
        user     = account
        settings = user['alert_settings']
    
    options = [
        {
            'human_name'    : 'Credit', 
            'name'          : 'credits', 
            'desc'          : 'Someone awards you credit on a stamp', 
        }, 
        {
            'human_name'    : 'Likes', 
            'name'          : 'likes', 
            'desc'          : 'Someone likes one of your stamps', 
        }, 
        {
            'human_name'    : 'Todos', 
            'name'          : 'todos', 
            'desc'          : 'Someone todos one of your stamps', 
        }, 
        {
            'human_name'    : 'Comments', 
            'name'          : 'comments', 
            'desc'          : 'Someone comments on one of your stamps.', 
        }, 
        {
            'human_name'    : 'Mentions', 
            'name'          : 'mentions', 
            'desc'          : 'Someone you on a stamp or comment', 
        }, 
        {
            'human_name'    : 'Replies', 
            'name'          : 'replies', 
            'desc'          : 'Someone replies to one of your comments', 
        }, 
        {
            'human_name'    : 'Followers', 
            'name'          : 'followers', 
            'desc'          : 'Someone follows you on Stamped', 
        }, 
        {
            'human_name'    : 'Friends', 
            'name'          : 'friends', 
            'desc'          : 'A friend from Facebook or Twitter joins Stamped', 
        }, 
        {
            'human_name'    : 'Actions', 
            'name'          : 'actions', 
            'desc'          : 'Someone performs an action on one of your stamps (e.g., listening to a song, makes a reversation, etc.)', 
        }, 
    ]
    
    for option in options:
        name = option['name']
        
        enabled_apns  = False
        enabled_email = False
        
        try:
            enabled_apns = settings['alerts_%s_apns'  % name]
        except KeyError:
            pass
        
        try:
            enabled_email = settings['alerts_%s_email' % name]
        except KeyError:
            pass
        
        option['enabled_apns']  = enabled_apns
        option['enabled_email'] = enabled_email
    
    return stamped_render(request, 'settings.html', {
        'body_classes'      : body_classes, 
        'page'              : 'settings', 
        'title'             : 'Stamped - Notification Settings', 
        'user'              : user, 
        'settings'          : options, 
        'token'             : token
    }, preload=[ 'token' ])

@stamped_view(schema=HTTPResetEmailSchema)
@require_http_methods(["POST"])
def send_reset_email(request, schema, **kwargs):
    email = schema.email
    api   = globalMongoStampedAPI()
    
    if not utils.validate_email(email):
        msg = "Invalid format for email address"
        logs.warning(msg)
        raise StampedInvalidEmailError("Invalid email address")
    
    # verify account exists
    try:
        user = stampedAPIProxy.checkAccount(email)
        
        if user is None:
            raise
    except Exception:
        utils.printException()
        logs.error("ERROR: invalid email '%s'" % email)
        
        ### TODO: Display appropriate error message
        errorMsg = 'No account information was found for that email address.'
        raise StampedHTTPError(404, msg="Email address not found", kind='invalid_input')
    
    account = stampedAPIProxy.getAccount(user['user_id'])
    auth_service = account['auth_service']
    
    if auth_service != 'stamped':
        raise StampedInputError("Account password not managed by Stamped for user '%s' (primary account service is '%s')" % (account['screen_name'], auth_service))
    
    # send email
    logs.info("sending email to '%s' (user: '%s')" % (email, user['screen_name']))
    result = g_stamped_auth.forgotPassword(email)
    
    return transform_output(result)

@stamped_view(schema=HTTPResetPasswordSchema)
@require_http_methods(["POST"])
def reset_password(request, schema, **kwargs):
    user_id = g_stamped_auth.verifyPasswordResetToken(schema.token)
    
    if schema.password is None or len(schema.password) <= 0:
        raise StampedInputError("invalid password")
    
    # store password            
    result = g_stamped_auth.updatePassword(user_id, schema.password)
    
    return transform_output(result)

@stamped_view(schema=HTTPUpdateSettingsSchema)
@require_http_methods(["POST"])
def update_alert_settings(request, schema, **kwargs):
    user_id  = g_stamped_auth.verifyEmailAlertToken(schema.token)
    settings = schema.dataExport()
    del settings['token']
    
    on  = filter(lambda k: settings[k], settings.keys())
    off = filter(lambda k: not settings[k], settings.keys())
    
    logs.info("user_id: %s" % user_id)
    logs.info("ON:  %s" % ", ".join(on))
    logs.info("OFF: %s" % ", ".join(off))
    
    stampedAPIProxy.updateAlerts(user_id, on, off)
    return transform_output(True)

