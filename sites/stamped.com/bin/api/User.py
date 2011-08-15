#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime
from Schemas import *

class User(UserSchema):

    def exportFlat(self):
        export = [
            'user_id',
            'first_name',
            'last_name',
            'screen_name',
            'display_name',
            'profile_image',
            'bio',
            'website',
            'color_primary',
            'color_secondary',
            'privacy',
            ]
        return self.exportFields(export)

    def exportMini(self):
        export = [
            'user_id',
            'screen_name',
            'display_name',
            'profile_image',
            'color_primary',
            'color_secondary',
            'privacy',
        ]
        return self.exportFields(export)

    def exportTiny(self):
        export = [
            'user_id',
            'screen_name',
            'display_name',
        ]
        return self.exportFields(export)

