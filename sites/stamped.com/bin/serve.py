#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import flask, json, utils
from flask import request, Flask

from api.MongoStampedAPI import MongoStampedAPI
from utils import AttributeDict
from errors import *
from resource import *

app = Flask(__name__)
stampedAPI = MongoStampedAPI()

def transformOutput(d):
    return json.dumps(d, sort_keys=True, indent=2)

def parseRequestForm(schema, form):
    apiFuncName = utils.getFuncName(0)
    
    try:
        return Resource.parse(apiFuncName, schema, form)
    except (InvalidArgument, Fail) as e:
        utils.log("API function '%s' failed to parse input '%s' against schema '%s'" % \
            (apiFuncName, str(request.form), str(schema)))
        utils.printException()
        raise

@app.route('/')
def hello():
    return "This is where stamped.com will go -- huzzah!"

# ######## #
# Accounts #
# ######## #

@app.route('/api/v1/addAccount', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
        ("firstName",         ResourceArgument(required=True, expectedType=basestring)), 
        ("lastName",          ResourceArgument(required=True, expectedType=basestring)), 
        ("username",          ResourceArgument(required=True, expectedType=basestring)), 
        ("email",             ResourceArgument(required=True, expectedType=basestring)), 
        ("password",          ResourceArgument(required=True, expectedType=basestring)), 
        ("locale",            ResourceArgument(required=True, expectedType=basestring)), 
        ("primary_color",     ResourceArgument(required=True, expectedType=basestring)), 
        ("secondary_color",   ResourceArgument(expectedType=basestring)), 
        ("img",               ResourceArgument(expectedType=basestring)), 
        ("website",           ResourceArgument(expectedType=basestring)), 
        ("bio",               ResourceArgument(expectedType=basestring)), 
        ("privacy",           ResourceArgumentBoolean(default=False)), 
    ])
    
    try:
        o = parseRequestForm(schema, request.form)
    except (InvalidArgument, Fail) as e:
        return str(e), 400
    
    return transformOutput(stampedAPI.addAccount(o.firstName, 
                                                 o.lastName, o.username, o.email, 
                                                 o.password, o.locale, o.primary_color, 
                                                 o.secondary_color, o.img, o.website, o.bio, 
                                                 o.privacy))

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0')

