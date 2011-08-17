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

class Entity(EntitySchema):

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
        data['created'] = str(data['timestamp.created'])
        del(data['timestamp.created'])
        data['address'] = str(data['details.place.address'])
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

class FlatEntity(EntityFlatSchema):

    def convertToEntity(self):
        data = self.value
        if 'coordinates' in data and data['coordinates'] != None \
            and not isinstance(data['coordinates'], dict):
            coordinates = data['coordinates'].split(',')
            del(data['coordinates'])
            data['coordinates'] = {
                'lat': coordinates[0],
                'lng': coordinates[1]
            }
        if 'address' in data:
            data['details'] = {
                'place': { 'address': data['address'] }
            }
            del(data['address'])
            
        return Entity(data)

