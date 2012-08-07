#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, json, utils, random, time, hashlib, logs
import datetime

from errors                         import *
from api_old.auth                           import convertPasswordForStorage
from api_old.HTTPSchemas                    import *
from api_old.MongoStampedAPI                import MongoStampedAPI
from api_old.MongoStampedAuth               import MongoStampedAuth
from django.http                    import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.views.decorators.http   import require_http_methods

stampedAPI  = MongoStampedAPI()
stampedAuth = MongoStampedAuth()

def passwordReset(request, **kwargs):
    token  = kwargs.pop('token', None)

    errorMsg = 'An error occurred. Please try again.'

    try:
        # Verify token is valid
        authUserId = stampedAuth.verifyPasswordResetToken(token)

        # Check if a form exists with data
        if request.method == 'POST':
            # User submitted the form
            data = request.POST

            # Verify passwords match and len > 0
            if not data['password']:
                logs.warning("Invalid password: %s" % data['password'])
                raise StampedInvalidPasswordError("Invalid password")

            if data['password'] != data['confirm']:
                logs.warning("Password match failed")
                raise StampedInvalidPasswordError("Invalid password")
            
            # Store password            
            stampedAuth.updatePassword(authUserId, data['password'])

            # Return success
            response = HttpResponseRedirect('/settings/password/success')

        else:
            # Display 'change password' form
            account = stampedAPI.getAccount(authUserId)
            params = {
                'token' : token,
                'form'  : True,
            }
            response = render_to_response('password-reset.html', params)

        return response

    except Exception as e:
        logs.begin(
            addLog=stampedAPI._logsDB.addLog, 
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            requestData=request,
        )
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        logs.save()

        return render_to_response('password-reset.html', {'error': errorMsg})

def passwordForgot(request):

    errorMsg = 'An error occurred. Please try again.'

    try:
        # Check if a form exists with data
        if request.method == 'POST':
            # User submitted the form
            data = request.POST

            # Validate email address
            email = str(data['forgotemail']).lower().strip()
            if not utils.validate_email(email):
                msg = "Invalid format for email address"
                logs.warning(msg)
                raise StampedInvalidEmailError("Invalid email address")
            
            # Verify account exists
            try:
                user = stampedAPI.checkAccount(email)
            except:
                ### TODO: Display appropriate error message
                errorMsg = 'No account information was found for that email address.'
                raise StampedHTTPError(404, msg="Email address not found", kind='invalid_input')

            # Send email
            stampedAuth.forgotPassword(email)

            # Return success
            response = HttpResponseRedirect('/settings/password/sent')

        else:
            # Display 'submit email' form
            response = render_to_response('password-forgot.html', None)

        return response

    except Exception as e:
        logs.begin(
            addLog=stampedAPI._logsDB.addLog, 
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            requestData=request,
        )
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        logs.save()

        return render_to_response('password-forgot.html', {'error': errorMsg})

    return True

def passwordSuccess(request):
    try:
        # Return success
        response = render_to_response('password-reset.html', None)
        return response

    except Exception as e:
        raise Http404

def passwordSent(request):
    try:
        # Return success
        response = render_to_response('password-forgot.html', {'email': True})
        return response

    except Exception as e:
        raise Http404


@require_http_methods(["GET"])
def alertSettings(request, **kwargs):
    try:
        # Check token
        tokenId     = request.GET.get('token', None)
        authUserId  = stampedAuth.verifyEmailAlertToken(tokenId)

        # Display 'change settings' form
        account = stampedAPI.getAccount(authUserId)

        alerts  = HTTPAccountAlerts().importSchema(account)
        user    = HTTPUser().importSchema(account)

        image_url = user['image_url'].replace('.jpg', '-31x31.jpg')
        stamp_url = 'http://static.stamped.com/logos/%s-%s-credit-18x18.png' % \
                    (user.color_primary, user.color_secondary)

        settings = {
            'email_alert_credit':   alerts.email_alert_credit,
            'email_alert_like':     alerts.email_alert_like,
            'email_alert_fav':      alerts.email_alert_fav,
            'email_alert_mention':  alerts.email_alert_mention,
            'email_alert_comment':  alerts.email_alert_comment,
            'email_alert_reply':    alerts.email_alert_reply,
            'email_alert_follow':   alerts.email_alert_follow,
        }

        params = {
            'screen_name':      user.screen_name,
            'name':             user.name,
            'image_url':        image_url,
            'stamp_url':        stamp_url,
            'action_token':     tokenId,
            'json_settings':    json.dumps(settings, sort_keys=True)
        }
        
        return render_to_response('notifications.html', params)

    except Exception as e:
        logs.begin(
            addLog=stampedAPI._logsDB.addLog, 
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            requestData=request,
        )
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        logs.save()

        ### TODO: CHANGE URL
        return render_to_response('password-reset.html', {'error': 'FAIL'})


@require_http_methods(["POST"])
def alertSettingsUpdate(request, **kwargs):
    try:
        # Check token
        tokenId     = request.POST.get('token', None)
        authUserId  = stampedAuth.verifyEmailAlertToken(tokenId)

        def _checkBool(v):
            if v in ['True', 'true', '1', 1, True]:
                return True
            return False

        # Get settings
        alerts = {
            'email_alert_credit':   _checkBool(request.POST.get('email_alert_credit', False)),
            'email_alert_like':     _checkBool(request.POST.get('email_alert_like', False)),
            'email_alert_fav':      _checkBool(request.POST.get('email_alert_fav', False)),
            'email_alert_mention':  _checkBool(request.POST.get('email_alert_mention', False)),
            'email_alert_comment':  _checkBool(request.POST.get('email_alert_comment', False)),
            'email_alert_reply':    _checkBool(request.POST.get('email_alert_reply', False)),
            'email_alert_follow':   _checkBool(request.POST.get('email_alert_follow', False)),
        }

        stampedAPI.updateAlerts(authUserId, alerts)
        
        params = {}
        params.setdefault('content_type', 'text/javascript; charset=UTF-8')
        params.setdefault('mimetype', 'application/json')
        
        output_json = json.dumps(alerts, sort_keys=True)
        output = HttpResponse(output_json, **params)
        
        return output
    
    except Exception as e:
        logs.begin(
            addLog=stampedAPI._logsDB.addLog, 
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            requestData=request,
        )
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        logs.save()
        
        return HttpResponse("internal server error", status=500)

