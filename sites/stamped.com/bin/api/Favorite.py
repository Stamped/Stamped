#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime
from Schemas import *

class Favorite(FavoriteSchema):

    # Set
    def setTimestampCreated(self):
        self.timestamp.created = datetime.utcnow()

    # Export
    def exportFlat(self):
        export = [
            'favorite_id',
            'user',
            'stamp',
            'entity',
            'complete',
            'timestamp.created',
            ]
        data = self.exportFields(export)

        data['created'] = str(data['timestamp.created'])
        del(data['timestamp.created'])
        
        return data

