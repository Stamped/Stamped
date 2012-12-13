#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, utils
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
    def __init__(self, text, style, stamp_image, placement=36):
        self.paragraph = Paragraph(text, style)
        self.stamp_placement = placement
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
        if w < mw and h < mh:
            self.width = w
            self.height = h
            return w, h
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
        if os.path.exists(self.image_file):
            try:
                Image(self.image_file, self.width, self.height).drawOn(self.canv, 0, 0)
            except Exception:
                utils.printException()


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

    title_decor = create_gradient(214, 314, user)
    title_decor = title_decor.resize((640, 944))
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
            logo_file = get_image_from_url(STAMP_LOGO_BASE % (user.color_primary, user.color_secondary))
            logo = PILImage.open(logo_file).resize((161, 161))
            words = PILImage.open(os.path.join(SCRIPT_DIR, 'stamped-type.png'))
            words.paste(logo, (0, 0), logo)
            logo_file = NamedTemporaryFile(suffix='.png', delete=False)
            words.save(logo_file.name)
            self.logo_image = logo_file.name
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
        
        if self.profile_image is not None and os.path.exists(self.profile_image):
            try:
                Image(self.profile_image, 132, 132).drawOn(canvas, 194, 9)
            except Exception:
                utils.printException()
        
        if self.logo_image is not None and os.path.exists(self.logo_image):
            try:
                Image(self.logo_image).drawOn(canvas, 250, 100)
            except Exception:
                utils.printException()
        
        canvas.restoreState()


class FollowingInfo(Flowable):
    def __init__(self, following, follower, style):
        self.following = following
        self.follower = follower
        self.style = style

    def wrap(self, *args):
        w, h = Paragraph('Followers', self.style).wrap(640, 200)
        return 640, h * 2

    def draw_group(self, group, shift):
        offset = 0
        for item in group:
            w, h = item.wrap(640, 200)
            item.drawOn(self.canv, shift, offset)
            offset += h

    def draw(self):
        follower_story = [
            Paragraph('Followers', self.style),
            Paragraph('<b>%d</b>' % (self.follower if self.follower else 0), self.style),
            ]
        following_story = [
            Paragraph('Following', self.style),
            Paragraph('<b>%d</b>' % (self.following if self.following else 0), self.style),
            ]
        self.draw_group(follower_story, 0)
        self.draw_group(following_story, 250)
        

class DataExporter(object):
    def __init__(self, api):
        self.__api = api
        self.user_collection = self.__api._userDB

        self.spacer = NiceSpacer(1, 20)
        self.separator = Separator(552)
        self.cover_title_style = styles.ParagraphStyle(
                name='covertitle',
                textColor=colors.HexColor(0x262626),
                fontName='TitleFont',
                fontSize=110,
                leading=120,
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
        story.append(Spacer(1, 30))
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
        story.append(Spacer(1, 80))
        story.append(Paragraph(align_center(str(count)), self.stamp_count_style))
        story.append(NextPageTemplate('Decorated'))
        story.append(PageBreak())
        return story

    def make_stamp_story(self, user, ending, stamp_image, stamp, entity):
        story = []

        story.append(StampTitle(entity.title, self.title_style, stamp_image))

        subtitle = entity.subtitle
        if entity.kind == 'place':
            address = entity.formatted_address
            if address is not None:
                subtitle = address
        story.append(Paragraph(subtitle, self.subtitle_style))

        for content in stamp.contents:
            blurb = content.blurb
            if blurb is not None:
                story.append(self.spacer)
                story.append(Paragraph('<b>%s</b> said:' % user.screen_name, self.subtitle_style))
                story.append(Paragraph(blurb, self.normal_style))

            if content.images:
                for image in content.images:
                    img_file = get_image_from_url(image.sizes[0].url)
                    story.append(Spacer(1, 15))
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

        story.append(FollowingInfo(stats.num_friends, stats.num_followers, self.normal_style))
        story.append(separator)

        stamp_image = get_image_from_url(STAMP_BASE % (user.color_primary, user.color_secondary))
        story.append(StampTitle(str(stats.num_stamps), self.cover_title_style, stamp_image, 76))
        story.append(Paragraph('Total Stamps', self.normal_style))
        story.append(separator)
        
        if stats.distribution is None or len(stats.distribution) == 0:
            distribution = self.__api._getUserStampDistribution(user.user_id)
            stats.distribution = distribution
        
        for kind, display in categories:
            count = 0
            for dist in stats.distribution:
                if dist.category == kind:
                    count = dist.count
                    break

            story.append(Paragraph('%s <font color=#999999>/</font> <b>%d</b>' % (display, count), self.normal_style))
            story.append(spacer)
        story.append(NextPageTemplate('FullBlank'))
        story.append(PageBreak())
        return story

    def export_user_data(self, user_id, output_file):
        story = []

        user_stamps_collection = self.__api._stampDB.user_stamps_collection
        stamp_collection = self.__api._stampDB
        entity_collection = self.__api._entityDB

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
        # data_exporter.export_user_data('4e57048dccc2175fca000005', fout) # travis
