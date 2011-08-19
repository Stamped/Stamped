#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime
from Schemas import *
# from Stamp import Stamp
# from Comment import Comment
# from Favorite import Favorite

# class Activity(ActivitySchema):

#     # Set
#     def setTimestampCreated(self):
#         self.timestamp.created = datetime.utcnow()

#     # Export
#     def exportFlat(self):

#         data = {}
#         data['activity_id'] = self.activity_id
#         data['genre'] = self.genre
#         data['user'] = self.user.value

#         if self.stamp.stamp_id != None:
#             stamp = Stamp(self.stamp.value)
#             data['stamp'] = stamp.exportFlat()
        
#         if self.comment.comment_id != None:
#             comment = Comment(self.comment.value)
#             data['comment'] = comment.exportFlat()

#         if self.favorite.favorite_id != None:
#             favorite = Favorite(self.favorite.value)
#             data['favorite'] = favorite.exportFlat()

#         data['created'] = str(self.timestamp.created)

#         return data

