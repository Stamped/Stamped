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

search.json         Return a list of objects based on a sepcified scope and a text query. Typically builds upon the 
                    collection endpoint to overlay search on top of other filtering.
"""

urlpatterns = patterns('',
    
    ### OAUTH
    (r'v0/oauth2/token.json',                               'v0.functions.oauth2.token'),
    (r'v0/oauth2/login.json',                               'v0.functions.oauth2.login'),
    (r'v0/oauth2/login/facebook.json',                      'v0.functions.oauth2.loginWithFacebook'),
    (r'v0/oauth2/login/twitter.json',                       'v0.functions.oauth2.loginWithTwitter'),

    ### ACCOUNT
    (r'v0/account/create.json',                             'v0.functions.account.create'),
    (r'v0/account/create/facebook.json',                    'v0.functions.account.createWithFacebook'),
    (r'v0/account/create/twitter.json',                     'v0.functions.account.createWithTwitter'),
    (r'v0/account/upgrade.json',                            'v0.functions.account.upgrade'),
    (r'v0/account/remove.json',                             'v0.functions.account.remove'),
    (r'v0/account/update.json',                             'v0.functions.account.update'),
    (r'v0/account/show.json',                               'v0.functions.account.show'),
    (r'v0/account/customize_stamp.json',                    'v0.functions.account.customizeStamp'),
    (r'v0/account/reset_password.json',                     'v0.functions.account.resetPassword'),
    (r'v0/account/change_password.json',                    'v0.functions.account.changePassword'),
    (r'v0/account/check.json',                              'v0.functions.account.check'),
    (r'v0/account/alerts/show.json',                        'v0.functions.account.showAlerts'),
    (r'v0/account/alerts/update.json',                      'v0.functions.account.updateAlerts'),
    (r'v0/account/alerts/ios/update.json',                  'v0.functions.account.updateApns'),
    (r'v0/account/alerts/ios/remove.json',                  'v0.functions.account.removeApns'),

    (r'v0/account/linked/show.json',                        'v0.functions.linked.show'),
    (r'v0/account/linked/add.json',                         'v0.functions.linked.add'),
    (r'v0/account/linked/remove.json',                      'v0.functions.linked.remove'),
    (r'v0/account/linked/update_share_settings.json',       'v0.functions.linked.updateShareSettings'),
    (r'v0/account/linked/twitter/add.json',                 'v0.functions.linked.add'),
    (r'v0/account/linked/facebook/add.json',                'v0.functions.linked.add'),
    (r'v0/account/linked/netflix/add.json',                 'v0.functions.linked.add'),

    # TODO: REMOVE FROM PROD
    (r'v0/account/linked_accounts.json',                    'v0.functions.linked.linked_accounts'),
    
    (r'v0/account/linked/twitter/update.json',              'v0.functions.linked.linked_accounts'),
    (r'v0/account/linked/twitter/remove.json',              'v0.functions.linked.removeTwitter'),
    (r'v0/account/linked/facebook/login_callback.json',     'v0.functions.linked.facebookLoginCallback'),
    (r'v0/account/linked/facebook/update.json',             'v0.functions.linked.linked_accounts'),
    (r'v0/account/linked/facebook/remove.json',             'v0.functions.linked.removeFacebook'),
    (r'v0/account/linked/netflix/login.json',               'v0.functions.linked.netflixLogin'),
    (r'v0/account/linked/netflix/login_callback.json',      'v0.functions.linked.netflixLoginCallback'),
    (r'v0/account/linked/netflix/update.json',              'v0.functions.linked.linked_accounts'),
    (r'v0/account/linked/netflix/remove.json',              'v0.functions.linked.removeNetflix'),
    (r'v0/account/linked/netflix/add_instant.json',         'v0.functions.linked.addToNetflixInstant'),
    (r'v0/account/linked/instagram/login_callback.json',    'v0.functions.linked.instagramLogin'),

    ### USERS
    (r'v0/users/show.json',                                 'v0.functions.users.show'),
    (r'v0/users/lookup.json',                               'v0.functions.users.lookup'),
    (r'v0/users/images.json',                               'v0.functions.users.images'),
    (r'v0/users/search.json',                               'v0.functions.users.search'),
    (r'v0/users/suggested.json',                            'v0.functions.users.suggested'),
    (r'v0/users/privacy.json',                              'v0.functions.users.privacy'),
    (r'v0/users/find/email.json',                           'v0.functions.users.findEmail'),
    (r'v0/users/find/phone.json',                           'v0.functions.users.findPhone'),
    (r'v0/users/find/twitter.json',                         'v0.functions.users.findTwitter'),
    (r'v0/users/find/facebook.json',                        'v0.functions.users.findFacebook'),
    
    ### FRIENDS
    (r'v0/friendships/create.json',                         'v0.functions.friendships.create'),
    (r'v0/friendships/remove.json',                         'v0.functions.friendships.remove'),
    (r'v0/friendships/check.json',                          'v0.functions.friendships.check'),
    (r'v0/friendships/friends.json',                        'v0.functions.friendships.friends'),
    (r'v0/friendships/followers.json',                      'v0.functions.friendships.followers'),
    (r'v0/friendships/invite.json',                         'v0.functions.friendships.invite'),
    # (r'v0/friendships/approve.json',                        'v0.functions.friendships.approve'),
    # (r'v0/friendships/blocks/create.json',                  'v0.functions.friendships.blocksCreate'),
    # (r'v0/friendships/blocks/check.json',                   'v0.functions.friendships.blocksCheck'),
    # (r'v0/friendships/blocking.json',                       'v0.functions.friendships.blocking'),
    # (r'v0/friendships/blocks/remove.json',                  'v0.functions.friendships.blocksRemove'),
    
    ### ENTITIES
    (r'v0/entities/create.json',                            'v0.functions.entities.create'),
    (r'v0/entities/show.json',                              'v0.functions.entities.show'),
    (r'v0/entities/update.json',                            'v0.functions.entities.update'),
    (r'v0/entities/remove.json',                            'v0.functions.entities.remove'),
    (r'v0/entities/autosuggest.json',                       'v0.functions.entities.autosuggest'),
    (r'v0/entities/search.json',                            'v0.functions.entities.search'),
    (r'v0/entities/suggested.json',                         'v0.functions.entities.suggested'),
    (r'v0/entities/menu.json',                              'v0.functions.entities.menu'),
    (r'v0/entities/stamped_by.json',                        'v0.functions.entities.stampedBy'),
    
    ### ACTIONS
    (r'v0/actions/complete.json',                           'v0.functions.entities.completeAction'),

    ### STAMPS
    (r'v0/stamps/create.json',                              'v0.functions.stamps.create'),
    (r'v0/stamps/update.json',                              'v0.functions.stamps.update'),
    (r'v0/stamps/show.json',                                'v0.functions.stamps.show'),
    (r'v0/stamps/remove.json',                              'v0.functions.stamps.remove'),
    (r'v0/stamps/collection.json',                          'v0.functions.stamps.collection'),
    (r'v0/stamps/search.json',                              'v0.functions.stamps.search'),
    
    (r'v0/stamps/likes/create.json',                        'v0.functions.stamps.likesCreate'),
    (r'v0/stamps/likes/remove.json',                        'v0.functions.stamps.likesRemove'),
    (r'v0/stamps/likes/show.json',                          'v0.functions.stamps.likesShow'),
    
    ### COMMENTS
    (r'v0/comments/create.json',                            'v0.functions.comments.create'),
    (r'v0/comments/remove.json',                            'v0.functions.comments.remove'),
    (r'v0/comments/collection.json',                        'v0.functions.comments.collection'),
    
    ### TODOS
    (r'v0/todos/create.json',                               'v0.functions.todos.create'),
    (r'v0/todos/complete.json',                             'v0.functions.todos.complete'),
    (r'v0/todos/remove.json',                               'v0.functions.todos.remove'),
    (r'v0/todos/show.json',                                 'v0.functions.todos.show'),

    ### GUIDE
    (r'v0/guide/collection.json',                           'v0.functions.stamps.guide'),
    (r'v0/guide/search.json',                               'v0.functions.stamps.searchGuide'),
    
    ### ACTIVITY
    (r'v0/activity/collection.json',                        'v0.functions.activity.collection'),
    (r'v0/activity/unread.json',                            'v0.functions.activity.unread'),
    
    ### PING
    (r'v0/ping.json',                                       'v0.functions.ping.ping'),
    
    ### SETTINGS
    url(R'^pw/(?P<token>[\w-]{36})$',                       'protected.views.passwordReset'),
    url(R'^settings/password/forgot$',                      'protected.views.passwordForgot'),
    url(R'^settings/password/sent$',                        'protected.views.passwordSent'),
    url(R'^settings/password/success$',                     'protected.views.passwordSuccess'),
    
    ### CLIENT LOGGING
    (r'v0/private/logs/create.json',                        'v0.functions.logs.create'),

)
