#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from libs.S3Utils   import S3Utils
from gevent.pool    import Pool

import servers.web2.settings as settings

STATIC_ROOT = "http://static.stamped.com"

def deploy_assets():
    sink    = S3Utils()
    prefix  = ".."
    pool    = Pool(32)
    paths   = [
        {
            "path"          : "/assets/generated/css", 
            "content_type"  : "text/css", 
            "apply_gzip"    : True, 
        }, 
        {
            "path"          : "/assets/generated/js", 
            "content_type"  : "application/javascript", 
            "apply_gzip"    : True, 
        }, 
        {
            "path"          : "/assets/img", 
            "apply_gzip"    : False, 
        },
        {
            "path"          : "/assets/fonts", 
            "apply_gzip"    : True, 
            "headers"       : {
                "Access-Control-Allow-Origin" : "*", 
            }, 
        }, 
    ]
    
    for path in paths:
        root = "%s%s" % (prefix, path['path'])
        apply_gzip      = path.get("apply_gzip", False)
        headers         = path.get("headers", None)
        content_type    = path.get("content_type", None)
        no_content_type = (content_type is None)
        
        for directory in os.walk(root):
            dirname = directory[0]
            
            for filename in directory[2]:
                if filename.startswith("."):
                    continue
                
                filepath = "%s/%s" % (dirname, filename)
                key = filepath[len(prefix):]
                
                if no_content_type:
                    key = "/assets/generated%s" % key[len("/assets"):]
                
                pool.spawn(deploy_asset, filepath, key, sink, content_type, apply_gzip, headers)
    
    pool.join()

def deploy_asset(filepath, key, sink, content_type, apply_gzip, headers):
    print "deploying '%s'" % key
    
    with open(filepath, "rb") as f:
        data = f.read()
    
    if content_type is None: # image or font
        suffix = os.path.splitext(key)[1].lower()
        
        if suffix == '.jpg' or suffix == '.jpeg':
            content_type = "image/jpeg"
        elif suffix == '.png':
            content_type = "image/png"
        elif suffix == '.gif':
            content_type = "image/gif"
        elif suffix == '.ico':
            content_type = "image/x-icon"
        elif suffix == '.otf':
            content_type = "font/opentype"
        elif suffix == '.ttf':
            content_type = "font/x-font-ttf"
        elif suffix == '.eot':
            content_type = "font/vnd.ms-fontobject"
        elif suffix == '.svg':
            content_type = "font/svg+xml"
        elif suffix == '.woff':
            content_type = "font/x-woff"
        elif suffix == '.htm' or suffix == ".html":
            content_type = "text/html"
        elif suffix == '.txt':
            content_type = "text/plain"
        else:
            raise Exception("unsupported file type: '" + suffix + "'")
    else:
        replace = [
            "img", 
        ]
        
        for replacement in replace:
            data = data.replace("/assets/%s" % replacement, "%s%s" % (STATIC_ROOT, "/assets/generated/%s" % replacement))
    
    sink.add_key(key, data, content_type=content_type, apply_gzip=apply_gzip, headers=headers)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    deploy_assets()

