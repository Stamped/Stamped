#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, logs
from datetime import datetime
from Schemas import *

categories = set([ 'food', 'music', 'film', 'book', 'other' ])
subcategories = {
    'restaurant' : 'food', 
    'bar' : 'food', 
    'book' : 'book', 
    'movie' : 'film', 
    'artist' : 'music', 
    'song' : 'music', 
    'album' : 'music', 
    'app' : 'other', 
    'other' : 'other',
}

class Entity2(Entity):

    # Set
    def setTimestampCreated(self):
        self.timestamp.created = datetime.utcnow()

    def setTimestampModified(self):
        self.timestamp.modified = datetime.utcnow()

    def setUserGenerated(self, user_id):
        self.sources.userGenerated.user_id = user_id

    # Get
    def getUserGenerated(self):
        return self.sources.userGenerated.user_id

    # Export
    def exportFlat(self):
        export = [
            'entity_id',
            'title',
            'subtitle',
            'category',
            'subcategory',
            'desc',
            'image',
            'timestamp.created',
            'details.place.address',
            ]
        data = self.exportFields(export)
        data['created'] = str(data.pop('timestamp.created', None))
        data['address'] = data.pop('details.place.address', None)
        return data

    def exportMini(self):
        export = [
            'entity_id',
            'title',
            'subtitle',
            'category',
            'subcategory',
            'coordinates',
            ]
        data = self.exportFields(export)
        # if data['coordinates'] != None:
        #     data['coordinates'] = "%s,%s" % (
        #         data['coordinates']['lat'],
        #         data['coordinates']['lng']
        #     )
        return data

    def exportPlace(self):
        export = ['entity_id', 'coordinates']
        return self.exportFields(export)

    def exportAutosuggest(self):
        export = ['entity_id', 'title', 'subtitle', 'category']
        return self.exportFields(export)



