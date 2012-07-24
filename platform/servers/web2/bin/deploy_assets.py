#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, random, utils

import deploy_version

from libs.S3Utils   import S3Utils
from gevent.pool    import Pool

import servers.web2.settings as settings

VERSION      = ".generated.%s" % deploy_version.get_current_version()
STATIC_ROOTS = [
    "http://static.stamped.com", 
    "http://static1.stamped.com", 
    "http://static2.stamped.com", 
    "http://static3.stamped.com", 
]

def get_static_root():
    return STATIC_ROOTS[random.randint(0, len(STATIC_ROOTS) - 1)]

def deploy_assets():
    sink    = S3Utils()
    prefix  = ".."
    pool    = Pool(16)
    paths   = [
        {
            "path"          : "/assets/generated/css", 
            "content_type"  : "text/css", 
            "apply_gzip"    : True, 
            "ignore"        : [ ], 
        }, 
        {
            "path"          : "/assets/generated/js", 
            "content_type"  : "application/javascript", 
            "apply_gzip"    : True, 
            "ignore"        : [ ], 
        }, 
        {
            "path"          : "/assets/img", 
            "apply_gzip"    : False, 
            "ignore"        : [
                "/assets/generated/img/emoji", 
                "/assets/generated/img/public-home", 
                "/assets/generated/img/public-home", 
            ], 
        },
        #{  # NOTE (travis): S3 / Cloudfront doesn't support CORS, so serving fonts via 
        #   #our CDN (which is technically an external domain) to FF/IE8 won't work.. balls
        #    "path"          : "/assets/fonts", 
        #    "apply_gzip"    : True, 
        #    "ignore"        : [ ], 
        #    "headers"       : {
        #        "Access-Control-Allow-Origin" : "*", 
        #    }, 
        #}, 
    ]
    
    for path in paths:
        root = "%s%s" % (prefix, path['path'])
        apply_gzip      = path.get("apply_gzip", False)
        ignore          = path.get("ignore", [])
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
                
                spawn = True
                for p in ignore:
                    if key.startswith(p):
                        spawn = False
                        break
                
                if spawn:
                    print "deploying '%s'" % key
                    pool.spawn(deploy_asset, filepath, key, sink, content_type, apply_gzip, headers)
                else:
                    print "ignoring  '%s'" % key
    
    pool.join()
    
    # clean up temporary gzip files created by S3Utils
    utils.shell(r"rm -f .temp.*")

def deploy_asset(filepath, key, sink, content_type, apply_gzip, headers):
    with open(filepath, "rb") as f:
        data = f.read()
    
    if content_type is None: # image or font
        key_prefix, suffix = os.path.splitext(key)
        suffix = suffix.lower()
        
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
        
        #if not key_prefix.endswith(VERSION):
        #    key = "%s%s%s" % (key_prefix, VERSION, key_suffix)
    else:
        replace = [
            "img", 
            #"fonts", 
        ]
        
        for replacement in replace:
            data = data.replace("/assets/%s" % replacement, "%s%s" % (get_static_root(), "/assets/generated/%s" % replacement))
    
    sink.add_key(key, data, content_type=content_type, apply_gzip=apply_gzip, headers=headers)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    deploy_assets()

