#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v1.schemas import HTTPSettingsToggle, HTTPSettingsGroup

def build_alert_response(account):
    """
    Converts alerts settings from an account into the list format returned to the client.
    """
    alerts = getattr(account, 'alert_settings', None)
    result = []

    def buildToggle(settingType, settingGroup):
        name = 'alerts_%s_%s' % (settingGroup, settingType)
        toggle = HTTPSettingsToggle()
        toggle.toggle_id = name
        toggle.type = settingType
        toggle.value = False
        if alerts is not None and hasattr(alerts, name) and getattr(alerts, name) == True:
            toggle.value = True
        return toggle

    def buildGroup(settingGroup, settingName):
        group = HTTPSettingsGroup()
        group.group_id = 'alerts_%s' % settingGroup
        group.name = settingName
        group.toggles = [
            buildToggle('apns', settingGroup),
            buildToggle('email', settingGroup),
        ]
        return group

    result.append(buildGroup('followers', 'New Followers'))
    result.append(buildGroup('credits', 'Credit'))
    result.append(buildGroup('mentions', 'Mentions'))
    result.append(buildGroup('comments', 'Comments'))
    result.append(buildGroup('replies', 'Replies'))
    result.append(buildGroup('likes', 'Likes'))
    result.append(buildGroup('todos', 'To-Dos'))
    result.append(buildGroup('friends', 'Facebook & Twitter Friends'))
    result.append(buildGroup('actions', 'Stamp Interactions'))

    return map(lambda x: x.dataExport(), result)

