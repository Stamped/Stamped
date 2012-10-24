#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api.db.mongodb import MongoUserCollection
from api.db.mongodb import MongoUserStampsCollection
from api.db.mongodb import MongoStampCollection
from api.db.mongodb import MongoEntityCollection
from api import MongoStampedAPI

from collections import defaultdict
from reportlab.lib import pagesizes, styles
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, KeepTogether

stylesheet = styles.getSampleStyleSheet()
normal_style = stylesheet['Normal']


def categorize_entity(entity):
    # TODO: this is wrong...
    if entity.kind == 'place':
        return 'place'
    if entity.kind == 'media_item' and 'book' in entity.types:
        return 'book'
    if entity.kind in ('media_item', 'media_collection', 'person'):
        return 'music'
    return 'other'


class DataExporter(object):
    def __init__(self, api):
        self.__api = api

    def make_title_page(self, user):
        # TODO: add picture and style
        story = []
        story.append(Paragraph(user.name, normal_style))
        story.append(Paragraph(user.screen_name, normal_style))
        story.append(Paragraph(user.location, normal_style))
        story.append(PageBreak())
        return story

    def make_section_title_page(self, user_name, stamp_type, count):
        # TODO: add picture and style
        # TODO: don't have first name
        story = []
        story.append(Paragraph(user_name + "'s", normal_style))
        story.append(Paragraph(stamp_type + " Stamps", normal_style))
        story.append(Paragraph(str(count), normal_style))
        story.append(PageBreak())
        return story

    def make_stamp_story(self, user_name, stamp, entity):
        # TODO: add picture and style
        story = []
        story.append(Paragraph(entity.title, normal_style))
        story.append(Paragraph(entity.subtitle, normal_style))
        
        for content in stamp.contents:
            blurb = content.blurb
            if blurb is not None:
                story.append(Paragraph(user_name + ' said:', normal_style))
                story.append(Paragraph(blurb, normal_style))

        if stamp.credits is not None:
            credit_users = (credit.user.screen_name for credit in stamp.credits)
            story.append(Paragraph('Credit to: ' + ', '.join(credit_users), normal_style))

        return [KeepTogether(story)]

    def make_section(self, user_name, stamp_type, stamps):
        story = []
        story.extend(self.make_section_title_page(user_name, stamp_type, len(stamps)))
        for stamp in stamps:
            story.extend(self.make_stamp_story(user_name, *stamp))
        story.append(PageBreak())
        return story

    def export_user_data(self, user_id):
        # TODO: TOC
        story = []

        user_collection = MongoUserCollection.MongoUserCollection(self.__api)
        user_stamps_collection = MongoUserStampsCollection.MongoUserStampsCollection()
        stamp_collection = MongoStampCollection.MongoStampCollection()
        entity_collection = MongoEntityCollection.MongoEntityCollection()

        user = user_collection.getUser(user_id)
        story.extend(self.make_title_page(user))

        stamp_ids = user_stamps_collection.getUserStampIds(user_id)
        stamps = stamp_collection.getStamps(stamp_ids)
        stamps_and_entities = []
        for stamp in stamps:
            entity = entity_collection.getEntity(stamp.entity.entity_id)
            stamps_and_entities.append((stamp, entity))

        categories = defaultdict(list)
        for stamp, entity in stamps_and_entities:
            categories[categorize_entity(entity)].append((stamp, entity))

        category_names = [
                ('place', 'Place'),
                ('music', 'Music'),
                ('film', 'Film'),
                ('book', 'Book'),
                ('app', 'App')]

        for category, readable_name in category_names:
            if category in categories:
                story.extend(self.make_section(user.screen_name, readable_name, categories[category]))

        doc = SimpleDocTemplate('/tmp/test.pdf', pagesize=pagesizes.A6)
        doc.build(story)
    

if __name__ == '__main__':
    api = MongoStampedAPI.MongoStampedAPI()
    data_exporter = DataExporter(api)
    data_exporter.export_user_data('4ff5e81f971396609000088a')
