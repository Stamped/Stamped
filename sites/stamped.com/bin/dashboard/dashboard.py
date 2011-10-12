#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from flask      import request, render_template, Flask
from datetime   import datetime

# ################ #
# Global Variables #
# ################ #

ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
monitor = Monitor()

@app.route('/')
def index():
    #monitor.ping()
    #monitor.status
    return "Test: %s" % (datetime.utcnow())

# ######## #
# Mainline #
# ######## #

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False, debug=True)

# TODO: web interface to logger
# TODO: web interface to statsd & graphite
# TODO: web interface to monitoring daemon

#   * nodes
#       * status
#       * stats?

