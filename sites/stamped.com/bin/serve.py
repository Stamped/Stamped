#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello Stamped!"

if __name__ == '__main__':
    app.run(debug=True)

