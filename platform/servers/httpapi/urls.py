#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
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

"""
------------------
NAMING CONVENTIONS
------------------

create.json         Create a new object. Should return the created object.

remove.json         Remove an existing object. Takes the object's id (e.g. stamp_id). Should return the deleted 
                    object.

update.json         Update an existing object. Takes the object's id as well as the new data. Should return the 
                    updated object.

show.json           Return one object based on the object's id (e.g. stamp_id).

lookup.json         Return a list of objects based on a comma-separated list of object ids.

collection.json     Return a list of objects based on a specified scope. Takes a scope param defining the collection
                    (e.g. "inbox") as well as additional filtering. Implies that a subset of data will be returned.

search.json         Return a list of objects based on a specified scope and a text query. Typically builds upon the
                    collection endpoint to overlay search on top of other filtering.
"""

urlpatterns = patterns('',
    
    ### OAUTH
    (r'v1/oauth2/token.json',                               'v0.functions.oauth2.token'),
    (r'v1/oauth2/login.json',                               'v0.functions.oauth2.login'),
    (r'v1/oauth2/login/facebook.json',                      'v0.functions.oauth2.loginWithFacebook'),
    (r'v1/oauth2/login/twitter.json',                       'v0.functions.oauth2.loginWithTwitter'),

    ### ACCOUNT
    (r'v1/account/create.json',                             'v0.functions.account.create'),
    (r'v1/account/create/facebook.json',                    'v0.functions.account.createWithFacebook'),
    (r'v1/account/create/twitter.json',                     'v0.functions.account.createWithTwitter'),
    (r'v1/account/upgrade.json',                            'v0.functions.account.upgrade'),
    (r'v1/account/remove.json',                             'v0.functions.account.remove'),
    (r'v1/account/update.json',                             'v0.functions.account.update'),
    (r'v1/account/show.json',                               'v0.functions.account.show'),
    (r'v1/account/customize_stamp.json',                    'v0.functions.account.customizeStamp'),
    (r'v1/account/reset_password.json',                     'v0.functions.account.resetPassword'),
    (r'v1/account/change_password.json',                    'v0.functions.account.changePassword'),
    (r'v1/account/check.json',                              'v0.functions.account.check'),
    (r'v1/account/alerts/show.json',                        'v0.functions.account.showAlerts'),
    (r'v1/account/alerts/update.json',                      'v0.functions.account.updateAlerts'),
    (r'v1/account/alerts/ios/update.json',                  'v0.functions.account.updateApns'),
    (r'v1/account/alerts/ios/remove.json',                  'v0.functions.account.removeApns'),

    (r'v1/account/linked/show.json',                        'v0.functions.linked.show'),
    (r'v1/account/linked/twitter/add.json',                 'v0.functions.linked.add', {'service_name' : 'twitter'}),
    (r'v1/account/linked/twitter/update.json',              'v0.functions.linked.add', {'service_name' : 'twitter'}),
    (r'v1/account/linked/twitter/remove.json',              'v0.functions.linked.remove', {'service_name' : 'twitter'}),
    (r'v1/account/linked/facebook/add.json',                'v0.functions.linked.add', {'service_name' : 'facebook'}),
    (r'v1/account/linked/facebook/update.json',             'v0.functions.linked.add', {'service_name' : 'facebook'}),
    (r'v1/account/linked/facebook/remove.json',             'v0.functions.linked.remove', {'service_name' : 'facebook'}),
    (r'v1/account/linked/facebook/settings/update.json',    'v0.functions.linked.updateSettings', {'service_name' : 'facebook'}),
    (r'v1/account/linked/facebook/settings/show.json',      'v0.functions.linked.showSettings', {'service_name' : 'facebook'}),
    (r'v1/account/linked/facebook/login.json',              'v0.functions.linked.facebookLogin'),
    (r'v1/account/linked/facebook/login_callback.json',     'v0.functions.linked.facebookLoginCallback'),
    (r'v1/account/linked/netflix/add.json',                 'v0.functions.linked.add', {'service_name' : 'netflix'}),
    (r'v1/account/linked/netflix/update.json',              'v0.functions.linked.add', {'service_name' : 'netflix'}),
    (r'v1/account/linked/netflix/remove.json',              'v0.functions.linked.remove', {'service_name' : 'netflix'}),
    (r'v1/account/linked/netflix/login.json',               'v0.functions.linked.netflixLogin'),
    (r'v1/account/linked/netflix/login_callback.json',      'v0.functions.linked.netflixLoginCallback'),
    (r'v1/account/linked/netflix/add_instant.json',         'v0.functions.linked.addToNetflixInstant'),
    (r'v1/account/linked/rdio/add.json',                    'v0.functions.linked.add', {'service_name' : 'rdio'}),
    (r'v1/account/linked/rdio/update.json',                 'v0.functions.linked.add', {'service_name' : 'rdio'}),
    (r'v1/account/linked/rdio/remove.json',                 'v0.functions.linked.remove', {'service_name' : 'rdio'}),

    ### USERS
    (r'v1/users/show.json',                                 'v0.functions.users.show'),
    (r'v1/users/lookup.json',                               'v0.functions.users.lookup'),
    (r'v1/users/images.json',                               'v0.functions.users.images'),
    (r'v1/users/search.json',                               'v0.functions.users.search'),
    (r'v1/users/suggested.json',                            'v0.functions.users.suggested'),
    (r'v1/users/privacy.json',                              'v0.functions.users.privacy'),
    (r'v1/users/find/email.json',                           'v0.functions.users.findEmail'),
    (r'v1/users/find/phone.json',                           'v0.functions.users.findPhone'),
    (r'v1/users/find/twitter.json',                         'v0.functions.users.findTwitter'),
    (r'v1/users/find/facebook.json',                        'v0.functions.users.findFacebook'),
    (r'v1/users/invite/facebook/collection.json',           'v0.functions.users.inviteFacebookCollection'),
    (r'v1/users/invite/twitter/collection.json',            'v0.functions.users.inviteTwitterCollection'),
    (r'v1/users/invite/email.json',                         'v0.functions.friendships.invite'),

    ### FRIENDS
    (r'v1/friendships/create.json',                         'v0.functions.friendships.create'),
    (r'v1/friendships/remove.json',                         'v0.functions.friendships.remove'),
    (r'v1/friendships/check.json',                          'v0.functions.friendships.check'),
    (r'v1/friendships/friends.json',                        'v0.functions.friendships.friends'),
    (r'v1/friendships/followers.json',                      'v0.functions.friendships.followers'),
    (r'v1/friendships/invite.json',                         'v0.functions.friendships.invite'),
    # (r'v1/friendships/approve.json',                        'v0.functions.friendships.approve'),
    # (r'v1/friendships/blocks/create.json',                  'v0.functions.friendships.blocksCreate'),
    # (r'v1/friendships/blocks/check.json',                   'v0.functions.friendships.blocksCheck'),
    # (r'v1/friendships/blocking.json',                       'v0.functions.friendships.blocking'),
    # (r'v1/friendships/blocks/remove.json',                  'v0.functions.friendships.blocksRemove'),
    
    ### ENTITIES
    (r'v1/entities/create.json',                            'v0.functions.entities.create'),
    (r'v1/entities/show.json',                              'v0.functions.entities.show'),
    (r'v1/entities/update.json',                            'v0.functions.entities.update'),
    (r'v1/entities/remove.json',                            'v0.functions.entities.remove'),
    (r'v1/entities/autosuggest.json',                       'v0.functions.entities.autosuggest'),
    (r'v1/entities/search.json',                            'v0.functions.entities.search'),
    (r'v1/entities/suggested.json',                         'v0.functions.entities.suggested'),
    (r'v1/entities/menu.json',                              'v0.functions.entities.menu'),
    (r'v1/entities/stamped_by.json',                        'v0.functions.entities.stampedBy'),
    (r'v1/entities/edit.html',                              'v0.functions.entities.edit'),
    (r'v1/entities/update.html',                            'v0.functions.entities.update'),
    
    ### ACTIONS
    (r'v1/actions/complete.json',                           'v0.functions.entities.completeAction'),

    ### STAMPS
    (r'v1/stamps/create.json',                              'v0.functions.stamps.create'),
    (r'v1/stamps/share/facebook.json',                      'v0.functions.stamps.share', { 'service_name' : 'facebook' }),
    (r'v1/stamps/show.json',                                'v0.functions.stamps.show'),
    (r'v1/stamps/remove.json',                              'v0.functions.stamps.remove'),
    (r'v1/stamps/collection.json',                          'v0.functions.stamps.collection'),
    (r'v1/stamps/search.json',                              'v0.functions.stamps.search'),
    
    (r'v1/stamps/likes/create.json',                        'v0.functions.stamps.likesCreate'),
    (r'v1/stamps/likes/remove.json',                        'v0.functions.stamps.likesRemove'),
    (r'v1/stamps/likes/show.json',                          'v0.functions.stamps.likesShow'),
    (r'v1/stamps/todos/show.json',                          'v0.functions.stamps.todosShow'),
    
    ### COMMENTS
    (r'v1/comments/create.json',                            'v0.functions.comments.create'),
    (r'v1/comments/remove.json',                            'v0.functions.comments.remove'),
    (r'v1/comments/collection.json',                        'v0.functions.comments.collection'),
    
    ### TODOS
    (r'v1/todos/create.json',                               'v0.functions.todos.create'),
    (r'v1/todos/complete.json',                             'v0.functions.todos.complete'),
    (r'v1/todos/remove.json',                               'v0.functions.todos.remove'),
    (r'v1/todos/collection.json',                           'v0.functions.todos.collection'),

    ### GUIDE
    (r'v1/guide/collection.json',                           'v0.functions.stamps.guide'),
    (r'v1/guide/search.json',                               'v0.functions.stamps.searchGuide'),
    
    ### ACTIVITY
    (r'v1/activity/collection.json',                        'v0.functions.activity.collection'),
    (r'v1/activity/unread.json',                            'v0.functions.activity.unread'),
    
    ### PING
    (r'v1/ping.json',                                       'v0.functions.ping.ping'),
    
    ### SETTINGS
    url(R'^pw/(?P<token>[\w-]{36})$',                       'protected.views.passwordReset'),
    url(R'^settings/password/forgot$',                      'protected.views.passwordForgot'),
    url(R'^settings/password/sent$',                        'protected.views.passwordSent'),
    url(R'^settings/password/success$',                     'protected.views.passwordSuccess'),
    
    ### CLIENT LOGGING
    (r'v1/private/logs/create.json',                        'v0.functions.logs.create'),

)
