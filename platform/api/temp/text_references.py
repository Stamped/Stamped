#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"




import Globals
import copy, urllib, urlparse, re, logs, string, time, utils
import libs.ec2_utils
import Entity
import HTTPSchemas

mention_re      = re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)
url_re          = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)


def _formatURL(url):
    try:
        return url.split('://')[-1].split('/')[0].split('www.')[-1]
    except Exception:
        return url


blurbs = [
    'This is a long blurb. Booyah.',
    'This is a blurb with a @mention in it.',
    'This is a blurb with @two @mentions in it.',
    'This blurb has @two mentioned @two times.',
    "Tricky url at www.stamped.com/ for sure",
    "Tricky url at www.stamped.com/abcdef for sure",
    "Tricky url at www.stamped.com/abcdefg for sure",
    "Tricky url at www.stamped.com?abcdefg for sure",
    'This blurb has a basic url at http://www.stamped.com so check it out',
    'More urls http://www.stamped.com/kevin/maps',
    "It's http://docs.python.org/library/string.html or https://www.google.com/search?sugexp=chrome,mod=1&sourceid=chrome&ie=UTF-8&q=python+url+regex -- which one is better?",
    "Gotta love @Laut. Great restaurant. Full review here: http://nymag.com/listings/restaurant/laut02/. Go there now! By @kevin.",
]

for text in blurbs:
    print '=' * 40
    print 'TEXT: %s' % text
    print HTTPSchemas._buildTextReferences(text)
"""
    refs = []
    offsets = {}

    # Mentions
    mentions = mention_re.finditer(text)
    for item in mentions:
        # print 'MENTION: "%s" (%s, %s)' % (item.groups()[0], item.start(), item.end())
        # refs.append({'action': item.groups()[0], 'indices': (item.start(), item.end())})

        source = HTTPActionSource()
        source.name = 'View profile'
        source.source = 'stamped'
        source.source_id = item.groups()[0]

        action = HTTPAction()
        action.type = 'stamped_view_screen_name'
        action.name = 'View profile'
        action.sources = [ source ]

        reference = HTTPTextReference()
        reference.indices = [ item.start(), item.end() ]
        reference.action = action

        refs.append(reference)

    # URL
    urls = url_re.finditer(text)
    for item in url_re.finditer(text):
        # print 'URL: "%s" (%s, %s)' % (item.groups()[0], item.start(), item.end())
        
        url = item.groups()[0]

        formatted = url.split('://')[-1].split('?')[0]
        if '/' in formatted:
            truncated = "%s..." % formatted[:formatted.index('/')+4]
            if len(truncated) < len(formatted):
                formatted = truncated
        offsets[item.end()] = len(formatted) - len(url)
        text = string.replace(text, url, formatted)

        source = HTTPActionSource()
        source.link = url
        source.name = 'Go to %s' % formatted
        source.source = 'link'

        action = HTTPAction()
        action.type = 'link'
        action.name = 'Go to %s' % formatted
        action.sources = [ source ]

        reference = HTTPTextReference()
        reference.indices = [ item.start(), item.end() ]
        reference.action = action

        refs.append(reference)

    for ref in refs:
        indices = ref.indices
        for position, offset in offsets.items():
            if position <= ref.indices[0]:
                indices = (indices[0] + offset, indices[1] + offset)
            elif position <= ref.indices[1]:
                indices = (indices[0], indices[1] + offset)
        ref.indices = indices
        # newRefs.append(newRef)
    refs.sort(key=lambda x: x.indices[0])
    print refs
    # print offsets

    for i in range((len(text) / 40) + 1):
        print text[(40*i):(40*(i+1))]
        print ('0123456789'*4)
    # print text
    print 
"""