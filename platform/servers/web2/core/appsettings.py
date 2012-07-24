#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from api.MongoStampedAPI            import globalMongoStampedAPI
from api.MongoStampedAuth           import MongoStampedAuth
from django.views.decorators.http   import require_http_methods
from django.http                    import HttpResponseRedirect

from errors                         import *
from servers.web2.core.schemas      import *
from servers.web2.core.helpers      import *

g_stamped_auth = MongoStampedAuth()

@stamped_view(schema=HTTPResetPasswordViewSchema)
def password_reset(request, schema, **kwargs):
    body_classes = "password_reset main"
    token        = schema.token
    
    # Verify token is valid
    user_id = g_stamped_auth.verifyPasswordResetToken(token)
    
    if user_id is None:
        raise StampedInputError("invalid token")
    
    return stamped_render(request, 'password_reset.html', {
        'body_classes'      : body_classes, 
        'page'              : 'password_reset', 
        'title'             : 'Stamped - Reset Password', 
        'token'             : token
    }, preload=[ 'token' ])

@stamped_view()
def password_forgot(request, **kwargs):
    body_classes = "password_forgot main"
    
    return stamped_render(request, 'password.html', {
        'body_classes'      : body_classes, 
        'page'              : 'password_forgot', 
        'title'             : 'Stamped - Forgot Password', 
    })

@stamped_view()
def alert_settings(request, **kwargs):
    body_classes = "alert_settings main"
    
    return stamped_render(request, 'alert_settings.html', {
        'body_classes'      : body_classes, 
        'page'              : 'alert_settings', 
        'title'             : 'Stamped - Alert Settings', 
    })

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

