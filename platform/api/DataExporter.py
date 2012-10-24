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
from reportlab.lib import pagesizes, styles, colors, units
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, KeepTogether, Image, Spacer, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import urllib
from tempfile import NamedTemporaryFile

stylesheet = styles.getSampleStyleSheet()
normal_style = stylesheet['Normal']

STAMP_URL_BASE = 'https://s3.amazonaws.com/stamped.com.static.images/logos/%s-%s-email-36x36.png'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont('TitleFont', os.path.join(SCRIPT_DIR, 'titlefont.ttf')))

def categorize_entity(entity):
    # TODO: this is wrong...
    if entity.kind == 'place':
        return 'place'
    if entity.kind == 'media_item' and 'book' in entity.types:
        return 'book'
    if entity.kind in ('media_item', 'media_collection', 'person'):
        return 'music'
    return 'other'


def get_image_from_url(url):
    suffix = url[-4:]
    assert suffix.lower() in ('.png', '.jpg'), suffix
    tmpfile = NamedTemporaryFile(suffix=suffix, delete=False)
    urllib.urlretrieve(url, tmpfile.name)
    return tmpfile.name


class Separator(Flowable):
    def __init__(self, width):
        self.width = width

    def wrap(self, *args):
        return 40, 1

    def draw(self):
        self.canv.setFillColor(colors.black)
        self.canv.line(0, 0, self.width, 0)


class StampTitle(Flowable):
    def __init__(self, text, style, stamp_image):
        self.paragraph = Paragraph(text, style)
        self.radius = 8
        self.stamp_placement = 10
        self.stamp_image = Image(stamp_image, self.radius * 2, self.radius * 2)

    def wrap(self, *args):
        w, h = self.paragraph.wrap(*args)
        self.width = w
        return w, h

    def draw(self):
        blPara = self.paragraph.blPara
        if blPara.kind == 0:
            remain = blPara.lines[-1][0]
        else:
            remain = blPara.lines[-1].extraSpace

        self.stamp_image.drawOn(self.canv, self.width - remain - self.radius, self.stamp_placement)
        self.paragraph.drawOn(self.canv, 0, 0)


class ResizableImage(Flowable):
    def __init__(self, image_file):
        self.image_file = image_file

    def wrap(self, mw, mh):
        w, h = Image(self.image_file).wrap(mw, mh)
        if w > mw:
            ratio = mw / w
            w, h = w * ratio, h * ratio
        if h > mh:
            ratio = mh / h
            w, h = w * ratio, h * ratio
        w, h = w * 0.95, h * 0.95
        if w * 3 > mw * 2:
            self.width = w
            self.height = h
            return w, h
        return mw + 100, mh + 100

    def draw(self):
        Image(self.image_file, self.width, self.height).drawOn(self.canv, 0, 0)
        

class DataExporter(object):
    def __init__(self, api):
        self.__api = api

        self.spacer = Spacer(10, 20)
        self.separator = Separator(40)
        self.title_style = styles.ParagraphStyle(
                name='title',
                fontName='TitleFont',
                fontSize=24,
                leading=26,
                )
        self.subtitle_style = styles.ParagraphStyle(
                name='subtitle',
                fontName='Helvetica',
                textColor=colors.gray,
                )
        self.normal_style = styles.ParagraphStyle(
                name='normal',
                fontName='Helvetica',
                textColor=colors.darkgray,
                )

    def make_title_page(self, user):
        # TODO: add picture and style
        story = []
        story.append(Paragraph(user.name, normal_style))
        story.append(Paragraph(user.screen_name, normal_style))
        if user.location:
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

    def make_stamp_story(self, user, ending, stamp, entity):
        # TODO: add picture and style

        stamp_image = get_image_from_url(STAMP_URL_BASE % (user.color_primary, user.color_secondary))
        story = []

        story.append(StampTitle(entity.title, self.title_style, stamp_image))
        story.append(Paragraph(entity.subtitle, self.subtitle_style))

        for content in stamp.contents:
            blurb = content.blurb
            if blurb is not None:
                story.append(self.spacer)
                story.append(Paragraph('<b>%s</b> said:' % user.screen_name, self.subtitle_style))
                story.append(Paragraph(blurb, self.normal_style))

            if content.images:
                for image in content.images:
                    img_file = get_image_from_url(image.sizes[0].url)
                    story.append(ResizableImage(img_file))
        
        if stamp.credits is not None:
            story.append(self.spacer)
            first_credit = stamp.credits[0].user.screen_name
            credit_text = 'Credit to: <b>%s</b>' % first_credit
            num_credits = len(stamp.credits)
            if num_credits > 1:
                credit_text += ' and %d other' % (num_credits - 1)
            if num_credits > 2:
                credit_text += 's'
            story.append(Paragraph(credit_text, self.subtitle_style))
        story.extend(ending)
        # return [KeepTogether(story)]
        return story

    def make_section(self, user, stamp_type, stamps):
        story = []
        story.extend(self.make_section_title_page(user.screen_name, stamp_type, len(stamps)))

        divider = [self.spacer, self.separator, self.spacer]
        for stamp in stamps[:-1]:
            story.extend(self.make_stamp_story(user, divider, *stamp))
        story.extend(self.make_stamp_story(user, [], *stamps[-1]))
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
                story.extend(self.make_section(user, readable_name, categories[category]))

        doc_parameters = {
                'pagesize' : pagesizes.A6,
                'leftMargin' : units.inch * 0.5,
                'rightMargin' : units.inch * 0.5,
                'topMargin' : units.inch * 0.5,
                'bottomMargin' : units.inch * 0.5,
                }
        doc = SimpleDocTemplate('/tmp/test.pdf', **doc_parameters)
        doc.build(story)
    

if __name__ == '__main__':
    api = MongoStampedAPI.MongoStampedAPI()
    data_exporter = DataExporter(api)
    # data_exporter.export_user_data('4ff5e81f971396609000088a')
    data_exporter.export_user_data('4e57048accc2175fcd000001')
