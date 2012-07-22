#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os
import keys
import logs
from ec2_utils import get_stack

__stack_name = get_stack().instance.stack if get_stack() is not None else 'local'
__keys_dir = os.path.dirname(keys.__file__)

__api_keys = None
def _api_keys():
    """ Singleton for api-key definitions. On first load, opens keys/apikeys-<stack>.conf to load stack-specific
        api keys
    """

    global __api_keys, __stack_name, __keys_dir
    if __api_keys is not None:
        return __api_keys

    filename = 'apikeys-%s.conf' % __stack_name
    apikeys_path = '%s/%s' % (__keys_dir, filename)

    print ('apikeys_path: %s' % apikeys_path)
    try:
        meta = {}
        if os.path.exists(apikeys_path):
            with open(apikeys_path, "rb") as fp:
                source = fp.read()

            exec compile(source, apikeys_path, "exec") in meta
        else:
            logs.warning("### Could not find '%s': no limits defined" % apikeys_path)
            return
    except Exception as e:
        logs.warning("Exception while trying to execute '%s' file: %s" % (filename, e))
        return

    __api_keys = meta['keys']

    return __api_keys

def get_api_key(service_name, key):
    return _api_keys()[service_name][key]