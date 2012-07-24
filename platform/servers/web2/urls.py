#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import re
import settings

from django.conf.urls.defaults  import patterns, include, url
from django.core.exceptions     import ImproperlyConfigured

urlpatterns = patterns('',
    url(r'^test$',                                      'core.views.test_view'), 
    
    # --------------------------------------------------------------------------
    # ------------------------------ MOBILE ------------------------------------
    # --------------------------------------------------------------------------
    
    
    # ------------------------------ ERRORS ------------------------------------
    # e.g., stamped.com/mobile/404, stamped.com/mobile/404.html
    url(r'^mobile/404/?$',                              'error.views.error_404'), 
    url(r'^mobile/404.html?$',                          'error.views.error_404'), 
    
    # e.g., stamped.com/mobile/503, stamped.com/mobile/503.html
    url(r'^mobile/503/?$',                              'error.views.error_503'), 
    url(r'^mobile/503.html?$',                          'error.views.error_503'), 
    
    # e.g., stamped.com/mobile/500, stamped.com/mobile/500.html
    url(r'^mobile/500/?$',                              'error.views.error_500'), 
    url(r'^mobile/500.html?$',                          'error.views.error_500'), 
    
    
    # ----------------------------- SETTINGS -----------------------------------
    # e.g., stamped.com/mobile/pw/screen_name
    url(R'^mobile/pw/(?P<token>[\w-]{36})$',            'mobile.views.password_reset'),
    
    # e.g., stamped.com/mobile/settings/password/forgot
    url(R'^mobile/settings/password/forgot/?$',         'mobile.views.password_forgot'),
    
    # e.g., stamped.com/mobile/settings/password/sent
    url(R'^mobile/settings/password/sent/?$',           'mobile.views.password_sent'),
    
    # e.g., stamped.com/mobile/settings/password/success
    url(R'^mobile/settings/password/success/?$',        'mobile.views.password_success'),
    
    # e.g., stamped.com/mobile/settings/alerts
    url(R'^mobile/settings/alerts/?$',                  'mobile.views.alert_settings'),
    
    # e.g., stamped.com/mobile/settings/alerts/update.json
    url(R'^mobile/settings/alerts/update.json$',        'mobile.views.alert_settings_update'),
    
    url(r'^/?mobile/settings/password/send-reset-email$',  'core.appsettings.send_reset_email'), 
    url(r'^/?settings/password/send-reset-email$',         'core.appsettings.send_reset_email'), 
    
    
    # ------------------------------ INDEX -------------------------------------
    # e.g., stamped.com/mobile, stamped.com/mobile/index, stamped.com/mobile/index.html
    url(r'^mobile/index$',                              'mobile.views.index'), 
    url(r'^mobile/index\.html?$',                       'mobile.views.index'), 
    url(r'^mobile/?$',                                  'mobile.views.index'), 
    
    
    # ------------------------------ ABOUT -------------------------------------
    # e.g., stamped.com/mobile/about, stamped.com/mobile/about.html
    url(r'^mobile/about$',                              'mobile.views.about'), 
    url(r'^mobile/about\.html?$',                       'mobile.views.about'), 
    
    
    # ------------------------------ JOBS --------------------------------------
    # e.g., stamped.com/mobile/jobs, stamped.com/mobile/jobs.html
    url(r'^mobile/jobs$',                               'mobile.views.jobs'), 
    url(r'^mobile/jobs\.html?$',                        'mobile.views.jobs'), 
    
    
    # ----------------------------- PROFILE ------------------------------------
    # e.g., stamped.com/mobile/travis
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})\/?$',    'mobile.views.profile'), 
    
    
    # ------------------------------- MAP --------------------------------------
    # e.g., stamped.com/mobile/travis/map
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})\/map$',  'mobile.views.map'), 
    
    
    # ----------------------------- SDETAIL ------------------------------------
    # e.g., stamped.com/travis/1/nobu
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})/stamps/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 
                                                        'mobile.views.sdetail'), 
    
    # e.g., stamped.com/travis/1
    url(r'^mobile/(?P<screen_name>[\w-]{1,20})/s/(?P<stamp_num>\d+)', 
                                                        'mobile.views.sdetail'), 
    
    
    # --------------------------------------------------------------------------
    # ---------------------------- NON-MOBILE ----------------------------------
    # --------------------------------------------------------------------------
    
    
    # ------------------------------ ERRORS ------------------------------------
    # e.g., stamped.com/404, stamped.com/404.html
    url(r'^404/?$',                             'error.views.error_404'), 
    url(r'^404.html?$',                         'error.views.error_404'), 
    
    # e.g., stamped.com/503, stamped.com/503.html
    url(r'^503/?$',                             'error.views.error_503'), 
    url(r'^503.html?$',                         'error.views.error_503'), 
    
    # e.g., stamped.com/500, stamped.com/500.html
    url(r'^500/?$',                             'error.views.error_500'), 
    url(r'^500.html?$',                         'error.views.error_500'), 
    
    
    # ----------------------------- SETTINGS -----------------------------------
    url(R'^pw/(?P<token>[\w-]{36})$',           'core.appsettings.password_reset'),
    url(R'^settings/password/forgot/?$',        'core.appsettings.password_forgot'),
    url(R'^settings/password/reset/?$',         'core.appsettings.password_reset'),
    
    url(R'^settings/alerts/?$',                 'core.appsettings.alert_settings'),
    url(R'^settings/alerts/update.json$',       'core.appsettings.alert_settings_update'),
    
    url(r'^/?mobile/settings/password/send-reset-email$',   'core.appssettings.reset_email'), 
    url(r'^/?settings/password/send-reset-email$',          'core.appsettings.reset_email'), 
    
    
    # ------------------------------- BLOG -------------------------------------
    # e.g., stamped.com/blog
    url(r'^blog$',                              'core.views.blog'), 
    
    
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
    
    
    # ------------------------ APP STORE DOWNLOAD ------------------------------
    url(r'^/?mobile/download$',                 'core.views.download'), 
    url(r'^/?download$',                        'core.views.download'), 
    
    
    # --------------------------- SMS DOWNLOAD ---------------------------------
    url(r'^/?mobile/download-app$',             'core.views.download_app'), 
    url(r'^/?download-app$',                    'core.views.download_app'), 
    
    
    # ------------------------------ ABOUT -------------------------------------
    # e.g., stamped.com/about, stamped.com/about.html
    url(r'^about$',                             'core.views.about'), 
    url(r'^about\.html?$',                      'core.views.about'), 
    
    
    # ------------------------------ JOBS --------------------------------------
    # e.g., stamped.com/jobs, stamped.com/jobs.html
    url(r'^jobs$',                              'core.views.jobs'), 
    url(r'^jobs\.html?$',                       'core.views.jobs'), 
    
    
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
)

#from django.conf.urls.static    import static
def custom_static(prefix, view='django.views.static.serve', **kwargs):
    """
        Helper function to return a URL pattern for serving files.
        
        from django.conf import settings
        from django.conf.urls.static import static
        
        urlpatterns = patterns('',
            # ... the rest of your URLconf goes here ...
        ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    
    if prefix and '://' in prefix:
        return []
    elif not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    else:
        return patterns('', 
            url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs), 
        )

# static assets
urlpatterns += custom_static(settings.STATIC_URL, document_root=settings.STATIC_DOC_ROOT)

