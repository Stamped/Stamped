#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, os, pystache, utils, pybars
import api.HTTPSchemas

from subprocess import Popen, PIPE
from pprint     import pformat
from django     import template

def _flatten_scope(s):
    d = s
    
    if isinstance(s, pybars._compiler.Scope):
        d = s.context
        
        if not isinstance(d, dict):
            d = d.__dict__
    
    return dict((k, v if not isinstance(v, pybars._compiler.Scope) else _flatten_scope(v)) 
                 for k, v in d.iteritems())

def debug(template_name, pad, scope, *args, **kwargs):
    logs.info("\n%s\n%s\n%s" % (pad, pformat(_flatten_scope(scope)), pad))

def user_profile_image(template_name, pad, scope, *args, **kwargs):
    size = 144
    
    if len(args) == 1 and isinstance(size, (basestring, int)):
        size = int(args[0])
    
    screen_name = scope.get('screen_name')
    name = scope.get('name')
    alt  = ""
    
    if size > 72:
        alt = "@%s" % screen_name
        
        if name is not None:
            alt  = "%s (%s)" % (name, alt)
        
        alt = 'alt="%s" ' % alt
    
    screen_name = screen_name.lower()
    url = scope.get('image_url', None)
    
    try:
        if url is None:
            ts  = scope.get('timestamp', {}).get('image_cache', None)
            url = api.HTTPSchemas._profileImageURL(screen_name, ts, size)
    except Exception:
        pass
    
    if url is None:
        url = "http://static.stamped.com/users/%s-%sx%s.jpg" % (screen_name, size, size)
    
    #if not url.endswith('default.jpg'):
    #    url = "http://static.stamped.com/users/%s-%sx%s.jpg" % (screen_name, size, size)
    
    return pybars.strlist('<img %s src="%s" />' % (alt, url))

def entity_image(template_name, pad, scope, *args, **kwargs):
    size = None
    
    if len(args) == 1 and isinstance(size, (basestring, int)):
        size = int(args[0])
    
    alt   = scope.get('title', "")
    url   = None
    large = None
    width = -1
    
    images = scope.get('images')
    
    if images is not None:
        for multires_image in images:
            for sized_image in multires_image['sizes']:
                if (size is None and url is None) or ('width' in sized_image and sized_image['width'] == size):
                    url = sized_image['url']
                
                if large is None or (width is not None and 'width' in sized_image and sized_image['width'] > width):
                    large = sized_image['url']
                    width = sized_image.get('width', None)
            
            if url is not None:
                break
        
        if url is None:
            for multires_image in images:
                for sized_image in multires_image['sizes']:
                    url = sized_image['url']
                    break
                
                if url is not None:
                    break
    
    if url is None:
        return ""
    
    onerror = "this.className='hidden'; if (typeof(window.g_update_stamps) !== 'undefined') { g_update_stamps(); }"
    pre     = '<div class="entity-image-wrapper"><img alt="%s" src="%s" onerror="%s" />' % (alt, url, onerror)
    body    = '<a class="lightbox zoom" href="%s"></a></div>' % large
    
    return pybars.strlist(pre + "\n" + body)

def missing(template_name, pad, scope, name):
    logs.warn("'%s' missing key '%s'" % (template_name, name))
    return ""

