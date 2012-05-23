#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django url configuration: controls httpapi dispatch

DOCUMENTED SAMPLE PATH MODULE
prev:   ./settings.py
next:   ./v0.functions.account.py
see:   urlpatterns
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# DOCUMENTED SAMPLE PATH ATTRIBUTE
# url to function mappings for django
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'httpapi.views.home', name='home'),
    # url(r'^httpapi/', include('httpapi.foo.urls')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    ### OAUTH
    (r'v0/oauth2/token.json',                       'v0.functions.oauth2.token'),
    (r'v0/oauth2/login.json',                       'v0.functions.oauth2.login'),
    
    ### ACCOUNT
    #
    # DOCUMENTED SAMPLE PATH DATA
    # establishes mapping of the REST command account/create to the implementing function, platform.servers.httpapi.v0.functions.account.create
    (r'v0/account/create.json',                     'v0.functions.account.create'),
    (r'v0/account/create_using_facebook.json',      'v0.functions.account.createUsingFacebook'),
    (r'v0/account/remove.json',                     'v0.functions.account.remove'),
    (r'v0/account/settings.json',                   'v0.functions.account.settings'),
    (r'v0/account/update_profile.json',             'v0.functions.account.update_profile'),
    (r'v0/account/update_profile_image.json',       'v0.functions.account.update_profile_image'),
    (r'v0/account/customize_stamp.json',            'v0.functions.account.customize_stamp'),
    (r'v0/account/verify_credentials.json',         'v0.functions.account.verify_credentials'),
    (r'v0/account/reset_password.json',             'v0.functions.account.reset_password'),
    (r'v0/account/change_password.json',            'v0.functions.account.change_password'),
    (r'v0/account/check.json',                      'v0.functions.account.check'),
    (r'v0/account/alerts/show.json',                'v0.functions.account.show_alerts'),
    (r'v0/account/alerts/update.json',              'v0.functions.account.update_alerts'),
    (r'v0/account/alerts/ios/update.json',          'v0.functions.account.update_apns'),
    (r'v0/account/alerts/ios/remove.json',          'v0.functions.account.remove_apns'),
    
    # TODO: REMOVE FROM PROD
    (r'v0/account/linked_accounts.json',            'v0.functions.account.linked_accounts'),
    
    (r'v0/account/linked/twitter/update.json',      'v0.functions.account.linked_accounts'),
    (r'v0/account/linked/twitter/followers.json',   'v0.functions.account.alertFollowersFromTwitter'),
    (r'v0/account/linked/twitter/remove.json',      'v0.functions.account.removeTwitter'),
    (r'v0/account/linked/facebook/login_callback.json', 'v0.functions.account.facebookLoginCallback'),
    (r'v0/account/linked/facebook/update.json',     'v0.functions.account.linked_accounts'),
    (r'v0/account/linked/facebook/followers.json',  'v0.functions.account.alertFollowersFromFacebook'),
    (r'v0/account/linked/facebook/remove.json',     'v0.functions.account.removeFacebook'),
    (r'v0/account/linked/netflix/login.json',       'v0.functions.account.netflixLogin'),
    (r'v0/account/linked/netflix/login_callback.json','v0.functions.account.netflixLoginCallback'),
    (r'v0/account/linked/netflix/update.json',      'v0.functions.account.linked_accounts'),
    (r'v0/account/linked/netflix/remove.json',      'v0.functions.account.removeNetflix'),
    (r'v0/account/linked/netflix/add_instant.json',   'v0.functions.account.addToNetflixInstant'),
    (r'v0/account/linked/netflix/remove_instant.json','v0.functions.account.removeFromNetflixInstant'),
    (r'v0/account/linked/instagram/login_callback.json', 'v0.functions.accounts.instagramLogin'),

    ### USERS
    (r'v0/users/show.json',                         'v0.functions.users.show'),
    (r'v0/users/lookup.json',                       'v0.functions.users.lookup'),
    (r'v0/users/search.json',                       'v0.functions.users.search'),
    (r'v0/users/suggested.json',                    'v0.functions.users.suggested'),
    (r'v0/users/privacy.json',                      'v0.functions.users.privacy'),
    (r'v0/users/distribution.json',                 'v0.functions.users.distribution'),
    (r'v0/users/find/email.json',                   'v0.functions.users.findEmail'),
    (r'v0/users/find/phone.json',                   'v0.functions.users.findPhone'),
    (r'v0/users/find/twitter.json',                 'v0.functions.users.findTwitter'),
    (r'v0/users/find/facebook.json',                'v0.functions.users.findFacebook'),
    (r'v0/users/alert/twitter.json',                'v0.functions.users.alertFriendsFromTwitter'),
    (r'v0/users/alert/facebook.json',               'v0.functions.users.alertFriendsFromFacebook'),
    
    ### FRIENDS
    (r'v0/friendships/create.json',                 'v0.functions.friendships.create'),
    (r'v0/friendships/remove.json',                 'v0.functions.friendships.remove'),
    (r'v0/friendships/check.json',                  'v0.functions.friendships.check'),
    (r'v0/friendships/friends.json',                'v0.functions.friendships.friends'),
    (r'v0/friendships/followers.json',              'v0.functions.friendships.followers'),
    (r'v0/friendships/approve.json',                'v0.functions.friendships.approve'),
    (r'v0/friendships/blocks/create.json',          'v0.functions.friendships.blocksCreate'),
    (r'v0/friendships/blocks/check.json',           'v0.functions.friendships.blocksCheck'),
    (r'v0/friendships/blocking.json',               'v0.functions.friendships.blocking'),
    (r'v0/friendships/blocks/remove.json',          'v0.functions.friendships.blocksRemove'),
    (r'v0/friendships/invite.json',                 'v0.functions.friendships.invite'),
    
    ### ENTITIES
    (r'v0/entities/create.json',                    'v0.functions.entities.create'),
    (r'v0/entities/show.json',                      'v0.functions.entities.show'),
    (r'v0/entities/update.json',                    'v0.functions.entities.update'),
    (r'v0/entities/remove.json',                    'v0.functions.entities.remove'),
    (r'v0/entities/search.json',                    'v0.functions.entities.search'),
    (r'v0/entities/nearby.json',                    'v0.functions.entities.nearby'),
    (r'v0/entities/menu.json',                      'v0.functions.entities.menu'),
    (r'v0/entities/stamped_by.json',                'v0.functions.entities.stampedBy'),
    (r'v0/entities/suggested.json',                 'v0.functions.entities.suggested'),
    
    ### ACTIONS
    (r'v0/actions/complete.json',                   'v0.functions.entities.completeAction'),

    ### STAMPS
    (r'v0/stamps/create.json',                      'v0.functions.stamps.create'),
    (r'v0/stamps/update.json',                      'v0.functions.stamps.update'),
    (r'v0/stamps/update_image.json',                'v0.functions.stamps.update_image'),
    (r'v0/stamps/show.json',                        'v0.functions.stamps.show'),
    (r'v0/stamps/remove.json',                      'v0.functions.stamps.remove'),
    (r'v0/stamps/collection.json',                  'v0.functions.stamps.collection'),
    (r'v0/stamps/search.json',                      'v0.functions.stamps.search'),
    
    (r'v0/stamps/likes/create.json',                'v0.functions.stamps.likesCreate'),
    (r'v0/stamps/likes/remove.json',                'v0.functions.stamps.likesRemove'),
    (r'v0/stamps/likes/show.json',                  'v0.functions.stamps.likesShow'),
    
    ### COMMENTS
    (r'v0/comments/create.json',                    'v0.functions.comments.create'),
    (r'v0/comments/remove.json',                    'v0.functions.comments.remove'),
    (r'v0/comments/show.json',                      'v0.functions.comments.show'),
    
    ### COLLECTIONS
    (r'v0/collections/inbox.json',                  'v0.functions.collections.inbox'),
    (r'v0/collections/user.json',                   'v0.functions.collections.user'),
    (r'v0/collections/credit.json',                 'v0.functions.collections.credit'),
    (r'v0/collections/friends.json',                'v0.functions.collections.friends'),
    (r'v0/collections/suggested.json',              'v0.functions.collections.suggested'),
    (r'v0/collections/consumption.json',            'v0.functions.collections.consumption'),
    
    ### FAVORITES
    (r'v0/favorites/create.json',                   'v0.functions.favorites.create'),
    (r'v0/favorites/remove.json',                   'v0.functions.favorites.remove'),
    (r'v0/favorites/show.json',                     'v0.functions.favorites.show'),
    
    ### ACTIVITY
    (r'v0/activity/show.json',                      'v0.functions.activity.show'),
    (r'v0/activity/friends.json',                   'v0.functions.activity.friends'),
    (r'v0/activity/unread.json',                    'v0.functions.activity.unread'),
    
    ### PING
    (r'v0/temp/ping.json',                          'v0.functions.ping.ping'),
    (r'v0/ping.json',                               'v0.functions.ping.ping'),
    
    ### TEMP
    (r'v0/temp/timeout.json',                       'v0.functions.temp.timeout'),
    
    ### SETTINGS
    url(R'^pw/(?P<token>[\w-]{36})$',               'protected.views.passwordReset'),
    url(R'^settings/password/forgot$',              'protected.views.passwordForgot'),
    url(R'^settings/password/sent$',                'protected.views.passwordSent'),
    url(R'^settings/password/success$',             'protected.views.passwordSuccess'),
    
    ### CLIENT LOGGING
    (r'v0/private/logs/create.json',                'v0.functions.logs.create'),
    
    ### DOCS
    # (r'v0/oauth2/$',                    'v0.views.oauth2'),
    # (r'v0/account/$',                   'v0.views.account'),
    # (r'v0/users/$',                     'v0.views.users'),
    # (r'v0/friendships/$',               'v0.views.friendships'),
    # (r'v0/entities/$',                  'v0.views.entities'),
    # (r'v0/stamps/$',                    'v0.views.stamps'),
    # (r'v0/comments/$',                  'v0.views.comments'),
    # (r'v0/collections/$',               'v0.views.collections'),
    # (r'v0/favorites/$',                 'v0.views.favorites'),
    # (r'v0/activity/$',                  'v0.views.activity'),
    # (r'v0/temp/$',                      'v0.views.temp'),
    # (r'v0/$',                           'v0.views.index'),
    
    # url(r'^$', 'v0.views.default'),
)
