#!/usr/bin/env python

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
            'amazon',
        )

    @lazyProperty
    def __amazon(self):
        return AmazonAPI().amazon

    def __bookInfo(self, asin):
        try:
            loads(api.ItemLookup(
                ItemId=asin,
                Style="http://xml2json-xslt.googlecode.com/svn/trunk/xml2json.xslt",
                ResponseGroup='AlternateVersions,Large'
            ))['ItemLookupResponse']['Items']['Item']
        except KeyError:
            logs.warning('Lookup failed for Amazon book %s' % asin)
            return None

    def __enrichSong(self, entity, asin):
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

    def __enrichBook(self, entity, asin, resolve=False):
        info = self.__bookInfo(asin)
        if info is not None:
            try:
                if info['ItemAttributes']['Binding'] != 'Kindle Edition' and resolve:
                    for version in info['AlternateVersions']:
                        if version['Binding'] == 'Kindle Edition':
                            kindle_info = self.__bookInfo(version['ASIN'])
                            if kindle_info is not None:
                                asin = version['ASIN']
                                info = kindle_info
                                break
                entity['amazon_id'] = asin
                entity['author'] = attributes['Author']
                entity['publisher'] = attributes['Publisher']
                entity['publish_date'] = attributes['PublicationData']
                for review in info['EditorialReview']:
                    if review['Source'] == 'Product Description':
                        entity['desc'] = review['Content']
                        break
                attributes = info['ItemAttributes']
                entity['book_format'] = attributes['Format']
                if 'ISBN' in attributes:
                    entity['isbn'] = str(attributes['ISBN'])
                elif 'EISBN' in attributes:
                    entity['isbn'] = str(attributes['EISBN'])
                entity['edition'] = str(attributes['Edition'])
                entity['num_pages'] = int(attributes['NumberOfPages']) 
                entity['language'] = attributes['Languages']['Language']['Name']
            except KeyError:
                report()

    def enrichEntity(self, entity, controller, decorations, timestamps):
        asin = entity['asin']
        if asin is not None and asin != '':
            if entity['subcategory'] == 'song':
                self.__enrichSong(entity, asin)
            if entity['subcategory'] == 'book':
                self.__enrichBook(entity, asin, resolve=True)
        else:
            pass


        return True

