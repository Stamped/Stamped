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
from libs import image_utils

from PIL import Image as PILImage
from reportlab.lib import pagesizes, styles, colors, units
from reportlab.platypus import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import urllib
from collections import defaultdict
from tempfile import NamedTemporaryFile

STAMP_BASE = 'https://s3.amazonaws.com/stamped.com.static.images/logos/%s-%s-email-36x36.png'
STAMP_LOGO_BASE = 'https://s3.amazonaws.com/stamped.com.static.images/logos/%s-%s-logo-195x195.png'
PROFILE_BASE = 'https://s3.amazonaws.com/stamped.com.static.images/users/%s-144x144.jpg'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont('TitleFont', os.path.join(SCRIPT_DIR, 'titlefont.ttf')))

def categorize_entity(entity):
    # TODO: this is wrong...
    if entity.kind == 'place':
        return 'place'
    if 'book' in entity.types:
        return 'book'
    if entity.isType('track') or entity.isType('album') or entity.isType('artist'):
        return 'music'
    if entity.isType('movie') or entity.isType('tv'):
        return 'film'
    if entity.isType('app'):
        return 'app'
    return 'other'


def get_image_from_url(url):
    suffix = url[-4:]
    assert suffix.lower() in ('.png', '.jpg'), suffix
    tmpfile = NamedTemporaryFile(suffix=suffix, delete=False)
    urllib.urlretrieve(url, tmpfile.name)
    return tmpfile.name


def align_center(text):
    return '<para align="center">%s</para>' % text


class Separator(Flowable):
    def __init__(self, width):
        self.width = width
        self.hAlign = 'CENTER'

    def wrap(self, *args):
        return self.width, 41

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor(0xe5e5e5))
        self.canv.line(0, 21, self.width, 21)

    def getSpaceBefore(self):
        return 4

    def split(self, width, height):
        if 41 > height:
            return [Spacer(1, 0.001)]
        return [self]


class NiceSpacer(Spacer):
    def split(self, width, height):
        if self.height > height:
            return [Spacer(1, 0.001)]
        return [self]


class StampTitle(Flowable):
    def __init__(self, text, style, stamp_image):
        self.paragraph = Paragraph(text, style)
        self.stamp_placement = 36
        self.stamp_image = Image(stamp_image)

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

        self.stamp_image.drawOn(self.canv, self.width - remain - 18, self.stamp_placement)
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
        w, h = w * 0.99, h * 0.99
        if w * 2 > mw:
            self.width = w
            self.height = h
            return w, h
        return mw + 100, mh + 100

    def draw(self):
        Image(self.image_file, self.width, self.height).drawOn(self.canv, 0, 0)


def create_gradient(width, height, user):
    alpha  = 255
    stops  = [(
            2.0, 
            image_utils.parse_rgb(user.color_primary,   alpha), 
            image_utils.parse_rgb(user.color_secondary, alpha)
        )]
    return image_utils.get_gradient_image((width, height), stops)


def create_doc_template(output_file, user):
    band = create_gradient(640, 20, user)
    page_decor = PILImage.new("RGBA", (640, 960))
    page_decor.paste(band, (0, 0))
    page_decor.paste(band, (0, 940))
    overlay = PILImage.open(os.path.join(SCRIPT_DIR, 'pagebg.png'))
    page_decor.paste(overlay, (0, 0), overlay)
    page_bg = NamedTemporaryFile(suffix='.png', delete=False)
    page_decor.save(page_bg.name)

    def new_content_page(canvas, doc):
        canvas.drawImage(page_bg.name, 0, 0)

    title_decor = create_gradient(640, 944, user)
    overlay = PILImage.open(os.path.join(SCRIPT_DIR, 'covertexture.png'))
    title_decor.paste(overlay, (0, 0), overlay)
    title_bg = NamedTemporaryFile(suffix='.png', delete=False)
    title_decor.save(title_bg.name)

    def new_cover_page(canvas, doc):
        canvas.drawImage(title_bg.name, 0, 16)

    doc_parameters = {
            'pagesize' : (640, 960),
            'leftMargin' : 54,
            'rightMargin' : 54,
            'topMargin' : 54,
            'bottomMargin' : 54,
            }
    doc = BaseDocTemplate(output_file, **doc_parameters)

    full_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    pages = []
    pages.append(PageTemplate(id='CoverPage', frames=full_frame, onPage=new_cover_page, pagesize=doc.pagesize))
    pages.append(PageTemplate(id='FullBlank', frames=full_frame, pagesize=doc.pagesize))
    pages.append(PageTemplate(id='Decorated', frames=full_frame, onPage=new_content_page, pagesize=doc.pagesize))

    toc_frame = Frame(138, 0, 364, 900, id='toc')
    pages.append(PageTemplate(id='TOC', frames=toc_frame, pagesize=doc.pagesize))
    doc.addPageTemplates(pages)
    return doc


class CoverPicture(Flowable):
    def __init__(self, user, logo):
        self.backdrop = Image(os.path.join(SCRIPT_DIR, 'profilepicborder.png'))
        self.profile_image = get_image_from_url(PROFILE_BASE % user.screen_name)
        if logo:
            self.logo_image = get_image_from_url(STAMP_LOGO_BASE % (user.color_primary, user.color_secondary))
        else:
            self.logo_image = None

    def wrap(self, mw, mh):
        h = 351 if self.logo_image is None else 405
        return 640, h

    def draw(self):
        canvas = self.canv
        canvas.saveState()

        canvas.setFillColor(colors.HexColor(0xFFFFFF))
        self.backdrop.drawOn(canvas, 185, 0)
        Image(self.profile_image, 132, 132).drawOn(canvas, 194, 9)

        if self.logo_image is not None:
            Image(self.logo_image, 161, 161).drawOn(canvas, 250, 100)
            Image(os.path.join(SCRIPT_DIR, 'stamped-type.png'), 161, 161).drawOn(canvas, 250, 100)

        canvas.restoreState()
        

class DataExporter(object):
    def __init__(self, api):
        self.__api = api
        self.user_collection = MongoUserCollection.MongoUserCollection(self.__api)

        self.spacer = NiceSpacer(1, 20)
        self.separator = Separator(552)
        self.cover_title_style = styles.ParagraphStyle(
                name='covertitle',
                textColor=colors.HexColor(0x262626),
                fontName='TitleFont',
                fontSize=110,
                leading=140,
                )
        self.stamp_count_style = styles.ParagraphStyle(
                name='stampcount',
                textColor=colors.HexColor(0x999999),
                fontName='TitleFont',
                fontSize=110,
                leading=140,
                )
        self.title_style = styles.ParagraphStyle(
                name='title',
                textColor=colors.HexColor(0x262626),
                fontName='TitleFont',
                fontSize=72,
                leading=84,
                )
        self.subtitle_style = styles.ParagraphStyle(
                name='subtitle',
                textColor=colors.HexColor(0x999999),
                fontName='Helvetica',
                fontSize=24,
                leading=32,
                )
        self.normal_style = styles.ParagraphStyle(
                name='normal',
                textColor=colors.HexColor(0x262626),
                fontName='Helvetica',
                fontSize=24,
                leading=32,
                )
        self.no_leading = styles.ParagraphStyle(
                name='noleading',
                textColor=colors.HexColor(0x262626),
                fontName='Helvetica',
                fontSize=24,
                leading=22,
                )

    def make_title_page(self, user):
        story = []
        story.append(CoverPicture(user, True))
        story.append(Paragraph(align_center(user.name), self.cover_title_style))
        story.append(Paragraph(align_center('<b>@%s</b>' % user.screen_name), self.normal_style))
        if user.location:
            story.append(Paragraph(align_center(user.location), self.normal_style))
        story.append(NextPageTemplate('TOC'))
        story.append(PageBreak())
        return story

    def make_section_title_page(self, user, stamp_type, count):
        story = []
        story.append(CoverPicture(user, False))
        story.append(Spacer(1, 4))
        story.append(Paragraph(align_center(user.name + "'s"), self.no_leading))
        story.append(Paragraph(align_center(stamp_type + " Stamps"), self.cover_title_style))
        story.append(Spacer(1, 50))
        story.append(Paragraph(align_center(str(count)), self.stamp_count_style))
        story.append(NextPageTemplate('Decorated'))
        story.append(PageBreak())
        return story

    def make_stamp_story(self, user, ending, stamp_image, stamp, entity):
        # TODO: places address
        story = []

        story.append(StampTitle(entity.title, self.title_style, stamp_image))
        story.append(Paragraph(entity.subtitle, self.subtitle_style))
        if stamp.credits is not None:
            first_credit = stamp.credits[0].user.user_id
            credit_text = 'Credit to: <b>%s</b>' % self.user_collection.getUser(first_credit).screen_name
            num_credits = len(stamp.credits)
            if num_credits > 1:
                credit_text += ' and %d other' % (num_credits - 1)
            if num_credits > 2:
                credit_text += 's'
            story.append(Paragraph(credit_text, self.subtitle_style))

        for content in stamp.contents:
            blurb = content.blurb
            if blurb is not None:
                story.append(self.spacer)
                story.append(Paragraph('<b>%s</b> said:' % user.screen_name, self.subtitle_style))
                story.append(Paragraph(blurb, self.normal_style))

            # TODO: multiple images
            if content.images:
                for image in content.images:
                    img_file = get_image_from_url(image.sizes[0].url)
                    story.append(ResizableImage(img_file))
        
        story.extend(ending)
        return [KeepTogether(story)]

    def make_section(self, user, stamp_type, stamps, stamp_image):
        story = []
        story.extend(self.make_section_title_page(user, stamp_type, len(stamps)))

        divider = [self.separator]
        for stamp in stamps[:-1]:
            story.extend(self.make_stamp_story(user, divider, stamp_image, *stamp))
        story.extend(self.make_stamp_story(user, [], stamp_image, *stamps[-1]))
        story.append(NextPageTemplate('FullBlank'))
        story.append(PageBreak())
        return story

    def make_toc_page(self, user):
        categories = [
                ('place', 'Places'),
                ('music', 'Music'),
                ('film', 'Film & TV'),
                ('book', 'Books'),
                ('app', 'Apps'),
                ('other', 'Other'),
                ]
        stats = user.stats
        story = []

        separator = Separator(404)
        spacer = NiceSpacer(1, 34)
        story.append(Paragraph("<b>%s's Info" % user.name, self.normal_style))
        story.append(separator)
        # TODO: add followers number
        story.append(Paragraph(str(stats.num_stamps), self.cover_title_style))
        story.append(Paragraph('total stamps', self.normal_style))
        story.append(separator)
        for kind, display in categories:
            count = 0
            for dist in stats.distribution:
                if dist.category == kind:
                    count = dist.count
                    break

            story.append(Paragraph('%s / <b>%d</b>' % (display, count), self.normal_style))
            story.append(spacer)
        story.append(NextPageTemplate('FullBlank'))
        story.append(PageBreak())
        return story

    def export_user_data(self, user_id, output_file):
        story = []

        user_stamps_collection = MongoUserStampsCollection.MongoUserStampsCollection()
        stamp_collection = MongoStampCollection.MongoStampCollection()
        entity_collection = MongoEntityCollection.MongoEntityCollection()

        user = self.user_collection.getUser(user_id)
        story.extend(self.make_title_page(user))
        story.extend(self.make_toc_page(user))

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
                ('app', 'App'),
                ('other', 'Other')]

        stamp_image = get_image_from_url(STAMP_BASE % (user.color_primary, user.color_secondary))
        for category, readable_name in category_names:
            if category in categories:
                story.extend(self.make_section(user, readable_name, categories[category], stamp_image))

        create_doc_template(output_file, user).build(story)
    

if __name__ == '__main__':
    api = MongoStampedAPI.MongoStampedAPI()
    data_exporter = DataExporter(api)
    with open('/tmp/test.pdf', 'w') as fout:
        # data_exporter.export_user_data('4ff5e81f971396609000088a', fout) # me
        # data_exporter.export_user_data('4e8382e0d35f732acb000342', fout) # anthony
        data_exporter.export_user_data('4e57048accc2175fcd000001', fout) # robby
