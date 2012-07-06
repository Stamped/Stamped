#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from django.conf.urls.defaults  import patterns, include, url
from django.conf.urls.static    import static

import settings

urlpatterns = patterns('',
    # ------------------------------- BLOG -------------------------------------
    # e.g., stamped.com/blog
    url(r'^blog$',                              'core.views.blog'), 
    
    
    # ------------------------------- TEST -------------------------------------
    # e.g., stamped.com/test
    url(r'^test$',                              'core.views.test_view'), 
    
    
    # ------------------------------ POPUPS ------------------------------------
    # e.g., stamped.com/entities/menu, stamped.com/entities/menu.html
    url(r'^entities/menu$',                     'core.views.menu'), 
    url(r'^entities/menu\.html?$',              'core.views.menu'), 
    
    # e.g., stamped.com/popups/likes, stamped.com/popups/likes.html
    url(r'^popups/sdetail-social$',             'core.views.popup_sdetail_social'), 
    url(r'^popups/sdetail-social\.html?$',      'core.views.popup_sdetail_social'), 
    
    # e.g., stamped.com/popups/followers, stamped.com/popups/followers.html
    url(r'^popups/followers$',                  'core.views.popup_followers'), 
    url(r'^popups/followers\.html?$',           'core.views.popup_followers'), 
    
    # e.g., stamped.com/popups/following, stamped.com/popups/following.html
    url(r'^popups/following$',                  'core.views.popup_following'), 
    url(r'^popups/following\.html?$',           'core.views.popup_following'), 
    
    
    # ------------------------------ INDEX -------------------------------------
    # e.g., stamped.com, stamped.com/index, stamped.com/index.html
    url(r'^index$',                             'core.views.index'), 
    url(r'^index\.html?$',                      'core.views.index'), 
    url(r'^/?$',                                'core.views.index'), 
    
    
    # ----------------------------- PROFILE ------------------------------------
    # e.g., stamped.com/travis
    url(r'^(?P<screen_name>[\w-]{1,20})\/?$',   'core.views.profile'), 
    
    
    # ------------------------------- MAP --------------------------------------
    # e.g., stamped.com/travis/map
    url(r'^(?P<screen_name>[\w-]{1,20})\/map$', 'core.views.map'), 
    
    
    # ----------------------------- SDETAIL ------------------------------------
    # e.g., stamped.com/travis/1/nobu
    url(r'^(?P<screen_name>[\w-]{1,20})/stamps/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 
                                                'core.views.sdetail'), 
    # e.g., stamped.com/travis/1
    url(r'^(?P<screen_name>[\w-]{1,20})/s/(?P<stamp_num>\d+)', 
                                                'core.views.sdetail'), 
    
    # --------------------------------------------------------------------------
    # ------------------------------ MOBILE ------------------------------------
    # --------------------------------------------------------------------------
    
    # ----------------------------- PROFILE ------------------------------------
    # e.g., stamped.com/mobile/travis
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})\/?$',   'mobile.views.profile'), 
    
    # ------------------------------- MAP --------------------------------------
    # e.g., stamped.com/mobile/travis/map
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})\/map$', 'mobile.views.map'), 
)

# static assets
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DOC_ROOT)
#urlpatterns += static("^mobile%s" % settings.STATIC_URL, document_root=settings.STATIC_DOC_ROOT)

