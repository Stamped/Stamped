#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'httpapi.views.home', name='home'),
    # url(r'^httpapi/', include('httpapi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'v0/account/create.json', 'v0.functions.account.create'),
    (r'v0/account/remove.json', 'v0.functions.account.remove'),
    (r'v0/account/settings.json', 'v0.functions.account.settings'),
    (r'v0/account/update_profile.json', 'v0.functions.account.update_profile'),
    (r'v0/account/update_profile_image.json', 'v0.functions.account.update_profile_image'),
    (r'v0/account/verify_credentials.json', 'v0.functions.account.verify_credentials'),
    (r'v0/account/reset_password.json', 'v0.functions.account.reset_password'),
)
