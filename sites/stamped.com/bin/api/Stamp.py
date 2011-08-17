#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
# from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict
from datetime import datetime
from Schemas import *

class Stamp(StampSchema):

    # Set
    def setTimestampCreated(self):
        self.timestamp.created = datetime.utcnow()

    def setTimestampModified(self):
        self.timestamp.modified = datetime.utcnow()

    # Get
    def getOwnerId(self):
        return self.user.user_id
        
    def getStampPrivacy(self):
        return self.user.privacy

    # Export
    def exportFlat(self):
        export = [
            'stamp_id',
            'user',
            'entity',
            'blurb',
            'image',
            'credit',
            'mentions',
            'timestamp.created',
            'comment_preview',
            'stats.num_comments',
            ]
        data = self.exportFields(export)
        
        data['created'] = str(data['timestamp.created'])
        del(data['timestamp.created'])

        data['num_comments'] = data['stats.num_comments']
        del(data['stats.num_comments'])
        if data['num_comments'] == None:
            data['num_comments'] = 0

        data['entity']['coordinates'] = None
        if self.entity.coordinates.lat != None:
            data['entity']['coordinates'] = "%s,%s" % (
                self.entity.coordinates.lat,
                self.entity.coordinates.lng
            )
        
        return data