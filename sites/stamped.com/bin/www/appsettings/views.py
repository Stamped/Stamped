#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init
import os, json, utils, random, time, hashlib, logs

from errors import *
from auth import convertPasswordForStorage
from api.HTTPSchemas import *
from api.MongoStampedAPI import MongoStampedAPI
from api.MongoStampedAuth import MongoStampedAuth
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import datetime

stampedAPI  = MongoStampedAPI()
stampedAuth = MongoStampedAuth()

def passwordReset(request, **kwargs):
    token  = kwargs.pop('token', None)

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
                raise StampedHTTPError('invalid_password', 400, "Invalid password")

            if data['password'] != data['confirm']:
                logs.warning("Password match failed")
                raise StampedHTTPError('match_failed', 400, "Password match failed")

            # Convert password to hash
            password = convertPasswordForStorage(data['password'])
            
            # Store password            
            stampedAuth.updatePassword(authUserId, password)

            # Return success
            response = render_to_response('password-reset.html', None)

        else:
            # Display 'change password' form
            account = stampedAPI.getAccount(authUserId)
            params = {
                'email': account.email, 
                'token': token,
                'form': True,
                }
            response = render_to_response('password-reset.html', params)

        return response

    except Exception as e:
        logs.begin(stampedAPI._logsDB.addLog)
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        raise Http404

def passwordForgot(request):
    try:
        email = 'kevin@stamped.com'
        stampedAuth.forgotPassword(email)

    except Exception as e:
        print 'error'
        logs.begin(
            add=stampedAPI._logsDB.addLog, 
            save=stampedAPI._logsDB.saveLog,
            requestData=request,
        )
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        logs.save()
        print 'saved'
        raise Http404

    return True

