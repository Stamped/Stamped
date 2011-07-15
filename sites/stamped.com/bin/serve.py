#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import json, utils
from flask import request, Flask

from api.MongoStampedAPI import MongoStampedAPI
from exceptions import Fail
from resource import *

app = Flask(__name__)
#stampedAPI = stamped.api.MongoStampedAPI()

def transformOutput(d):
    return json.dumps(d, sort_keys=True, indent=2)

def parseRequestForm(form, schema):
    

@app.route('/')
def hello():
    return "This is where stamped.com will go -- huzzah!"

# ######## #
# Accounts #
# ######## #

@app.route('/api/v1/addAccount', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
    ])
    #from pprint import pprint
    #pprint(request.form)
    #print "%s %s" % (request.form['password'], request.form['userid'])
    
    try:
        parseRequestForm(request.form, schema)
    except Fail:
        utils.log("API function '%s' failed to parse input '%s' against schema '%s'" % \
            (utils.getFuncName(), str(request.form), str(schema)))
        raise
    
    return transformOutput(stampedAPI.addAccount())

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0')

firstName,
       lastName,
       username,
       email,
       password,
       locale,
       primary_color,
       secondary_color=None,
       img=None,
       website=None,
       bio=None,
       privacy=False

