#!/usr/bin/env python
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FormatSource' ]

import Globals
from logs import report

try:
    from resolve.BasicSource    import BasicSource
    import logs
    import re
    from datetime       import datetime
    from libs.LibUtils  import months
    from resolve.Resolver       import *
    from utils          import lazyProperty
    from libs.Geocoder       import Geocoder
    from libs.Factual   import globalFactual
    from pprint         import pprint
except:
    report()
    raise


class FormatSource(BasicSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        BasicSource.__init__(self, 'format',
            groups=[
                'release_date',
                'mangled_title',
                'coordinates',
            ]
        )

    @lazyProperty
    def __geocoder(self):
        return Geocoder()

    @lazyProperty
    def __factual(self):
        return globalFactual()

    def enrichEntity(self, entity, groups, controller, decorations, timestamps):
        if entity.kind == 'place' and len(entity.types) == 0:
            if entity['lat'] is not None and entity['lng'] is not None and entity['googleplaces_id'] is not None:
                factual_id = self.__factual.factual_from_entity(entity)
                if factual_id is not None:
                    data = self.__factual.place(factual_id)
                    if data is not None:
                        prefixes = [
                            ('Arts, Entertainment & Nightlife > Bars', 'bar'),
                            ('Food & Beverage > Restaurants', 'restaurant'),
                            ('Food & Beverage > Bakeries', 'bakery'),
                            ('Food & Beverage > Beer, Wine & Spirits','bar'),
                            ('Food & Beverage > Cafes, Coffee Houses & Tea Houses','cafe'),
                            ('Food & Beverage','restaurant'),
                        ]
                        category = data['category']
                        for prefix, subcategory in prefixes:
                            if category.startswith(prefix):
                                entity['types'].add(subcategory)
                                break

        if entity.kind == 'place':
            if entity.lat is None and (entity.formatted_address is not None or entity.address_country is not None):
                latLng = self.__geocoder.addressToLatLng(entity.formatted_address)
                if latLng is not None:
                    entity['coordinates'] = {'lat':latLng[0],'lng':latLng[1]}

        # if subcategory == 'artist':
        #     entity['mangled_title'] = artistSimplify(entity['title'])
        # elif entity['subcategory'] == 'song':
        #     entity['mangled_title'] = trackSimplify(entity['title'])
        # elif entity['subcategory'] == 'album':
        #     entity['mangled_title'] = albumSimplify(entity['title'])
        # elif entity['subcategory'] == 'movie':
        #     entity['mangled_title'] = movieSimplify(entity['title'])
        # else:
        #     entity['mangled_title'] = simplify(entity['title'])
        
        # if controller.shouldEnrich('release_date', self.sourceName, entity):
        #     if 'original_release_date' in entity:
        #         date = entity['original_release_date']
        #         if date is not None:
        #             new_date = None
        #             match = re.match(r'^(\d\d\d\d) (\d\d) (\d\d)$',date)
        #             if match is not None:
        #                 try:
        #                     new_date = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
        #                 except ValueError:
        #                     pass
        #                 except TypeError:
        #                     pass
        #             match = re.match(r'^(\w+) (\d+), (\d\d\d\d)$',date)
        #             if match is not None:
        #                 try:
        #                     month = match.group(1)
        #                     if month in months:
        #                         new_date = datetime(int(match.group(3)),months[month],int(match.group(2)))
        #                 except ValueError:
        #                     pass
        #                 except TypeError:
        #                     pass
        #             #sample 2009-05-29T07:00:00Z
        #             match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)\w+\d\d:\d\d:\d\d\w+$',date)
        #             if match is not None:
        #                 try:
        #                     new_date = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
        #                 except ValueError:
        #                     pass
        #                 except TypeError:
        #                     pass
        #             if new_date is not None:
        #                 entity['release_date'] = new_date
        #                 logs.info('created release date (%s) from %s' % (new_date, date))
        #     elif 'fid' in entity:
        #         desc = entity['desc'].replace('\n',' ')

        #         release_date_match = desc[-23:].split('Release Date:')
        #         if len(release_date_match) == 2:
        #             month, day, year = map(lambda x: int(x), release_date_match[-1].split('/'))
        #             if month >= 1 and month <= 12 and day >= 1 and day <= 31 and year > 1800 and year < 2200:
        #                 entity['release_date'] = datetime(year, month, day)
        #                 logs.info('created release_date (%s) from Fandango description' % entity['release_date'] )

        return True

