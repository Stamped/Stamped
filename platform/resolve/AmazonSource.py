#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'AmazonSource' ]

import Globals
from logs import report

try:
    from BasicSource    import BasicSource
    import logs
    import re
    from datetime       import datetime
    from libs.LibUtils           import months, parseDateString
    from libs.AmazonAPI     import AmazonAPI
    from utils          import lazyProperty
    from json           import loads
except:
    report()
    raise


class AmazonSource(BasicSource):
    """
    Amazon entities
    """
    def __init__(self):
        BasicSource.__init__(self, 'amazon',
            'artist_display_name',
            'genre',
            'track_length',
            'album_name',
            'release_date',
        )

    @lazyProperty
    def __amazon(self):
        return AmazonAPI().amazon

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if entity['subcategory'] == 'song':
            asin = entity['asin']
            if asin is not None and asin != '':
                info = loads(self.__amazon.ItemLookup(
                    ItemId = asin,
                    Style = "http://xml2json-xslt.googlecode.com/svn/trunk/xml2json.xslt",
                    ResponseGroup='ItemAttributes,RelatedItems',
                    RelationshipType='Tracks'
                ))
                try:
                    item = info['ItemLookupResponse']['Items']['Item']
                    attributes = item['ItemAttributes']
                    entity['genre'] = attributes['Genre']
                    entity['track_length'] = int(attributes['RunningTime'])
                    entity['release_date'] = parseDateString(attributes['ReleaseDate'])
                    album = item['RelatedItems']['RelatedItem']['Item']
                    album_attributes = album['ItemAttributes']
                    entity['album_name'] = album_attributes['Title']
                    entity['artist_display_name'] = album_attributes['Creator']
                except KeyError:
                    logs.info('Key error for %s (%s) when querying Amazon for %s' % (entity['title'], entity['entity_id'], asin))
        return True

