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
    (r'v1/account/create.json',                             'v1.account.create.run'),
    (r'v1/account/create/facebook.json',                    'v1.account.create_facebook.run'),
    (r'v1/account/create/twitter.json',                     'v1.account.create_twitter.run'),
    (r'v1/account/upgrade.json',                            'v1.account.upgrade.run'),
    (r'v1/account/remove.json',                             'v1.account.remove.run'),
    (r'v1/account/update.json',                             'v1.account.update.run'),
    (r'v1/account/show.json',                               'v1.account.show.run'),
    (r'v1/account/customize_stamp.json',                    'v1.account.customize_stamp.run'),
    (r'v1/account/check.json',                              'v1.account.check.run'),
    (r'v1/account/change_password.json',                    'v1.account.change_password.run'),
    (r'v1/account/alerts/show.json',                        'v1.account.show_alerts.run'),
    (r'v1/account/alerts/update.json',                      'v1.account.update_alerts.run'),
    (r'v1/account/alerts/ios/update.json',                  'v1.account.update_apns.run'),
    (r'v1/account/alerts/ios/remove.json',                  'v1.account.remove_apns.run'),

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
    (r'v1/friendships/create.json',                         'v1.friendships.create.run'),
    (r'v1/friendships/remove.json',                         'v1.friendships.remove.run'),
    (r'v1/friendships/check.json',                          'v1.friendships.check.run'),
    (r'v1/friendships/friends.json',                        'v1.friendships.friends.run'),
    (r'v1/friendships/followers.json',                      'v1.friendships.followers.run'),
    (r'v1/friendships/invite.json',                         'v1.friendships.invite.run'),
    
    ### ENTITIES
    (r'v1/entities/create.json',                            'v1.entities.create.run'),
    (r'v1/entities/show.json',                              'v1.entities.show.run'),
    (r'v1/entities/remove.json',                            'v1.entities.remove.run'),
    (r'v1/entities/autosuggest.json',                       'v1.entities.autosuggest.run'),
    (r'v1/entities/search.json',                            'v1.entities.search.run'),
    (r'v1/entities/suggested.json',                         'v1.entities.suggested.run'),
    (r'v1/entities/menu.json',                              'v1.entities.menu.run'),
    (r'v1/entities/stamped_by.json',                        'v1.entities.stamped_by.run'),
    
    ### ACTIONS
    (r'v1/actions/complete.json',                           'v1.entities.action.run'),

    ### STAMPS
    (r'v1/stamps/create.json',                              'v1.stamps.create.run'),
    (r'v1/stamps/show.json',                                'v1.stamps.show.run'),
    (r'v1/stamps/remove.json',                              'v1.stamps.remove.run'),
    (r'v1/stamps/share/facebook.json',                      'v1.stamps.share.run', { 'service_name' : 'facebook' }),
    (r'v1/stamps/collection.json',                          'v1.stamps.collection.run'),
    (r'v1/stamps/search.json',                              'v1.stamps.search.run'),
    
    ### LIKES
    (r'v1/stamps/likes/create.json',                        'v1.likes.create.run'),
    (r'v1/stamps/likes/remove.json',                        'v1.likes.remove.run'),
    (r'v1/stamps/likes/show.json',                          'v1.likes.show.run'),

    (r'v1/stamps/todos/show.json',                          'v0.functions.likes.todosShow'),
    
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

    ### CUSTOM
    (r'v1/entities/edit.html',                              'v0.functions.entities.edit'),
    (r'v1/entities/update.html',                            'v0.functions.entities.update'),

)
