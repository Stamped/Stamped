#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, utils
import copy, gevent, os, re, string, sys

from BeautifulSoup  import BeautifulSoup
from optparse       import OptionParser
from api_old.Schemas    import BasicEntity
from lxml           import objectify, etree
from libs.bottlenose     import Amazon
from errors         import Fail
from pprint         import pprint

__all__      = [ "AmazonAPI" ]
ASSOCIATE_ID = 'stamped01-20'

class AmazonAPI(object):
    """
        Amazon API wrapper
    """
    
    _subcategory_map = {
        'book'  : 'book', 
        'books' : 'book', 
        'dvd'   : 'movie', 
        'video' : 'movie', 
        'movie' : 'movie', 
        'music' : 'music', 
        'video games' : 'video_game', 
        'digital music track' : 'song', 
    }
    
    _binding_blacklist = set([
        'accessory', 
    ])
    
    _product_type_names = {
        'abis_book'  : 'book', 
        'abis_music' : 'album', 
        'abis_dvd'   : 'movie', 
        'console_video_games'    : 'video_game', 
        'video_game_hardware'    : None, 
        'video_game_accessories' : None, 
    }
    
    def __init__(self):
        self.amazon = Amazon(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY, ASSOCIATE_ID)
    
    def item_search(self, **kwargs):
        return self._item_helper(self.amazon.ItemSearch, **kwargs)
    
    def item_detail_search(self, **kwargs):
        transform = kwargs.pop('transform', False)
        kwargs['transform'] = True
        entities = self.item_search(**kwargs)
        
        """
        for entity in entities:
            pprint(entity)
        print '\n\n\n'
        """
        
        item_ids = string.joinfields((e.asin for e in entities), ',')
        
        if 0 == len(item_ids):
            return []
        else:
            return self.item_lookup(ItemId=item_ids, ResponseGroup='Large', transform=transform)
    
    def item_lookup(self, **kwargs):
        return self._item_helper(self.amazon.ItemLookup, **kwargs)
    
    def _item_helper(self, func, **kwargs):
        transform = kwargs.pop('transform', False)
        tree = self._call(func, **kwargs)
        
        if not transform:
            return tree
        else:
            items    = tree.findall('.//Item')
            entities = filter(lambda e: e is not None, map(self._parse_entity, items))
            
            return entities
    
    def _parse_entity(self, item, entity=None):
        try:
            if entity is None:
                entity = BasicEntity()
            
            attributes = item.find('.//ItemAttributes')
            
            # parse the product group and shortcut the parsing process to return 
            # None in the likely event that this entity doesn't belong to one of 
            # the targeted product groups that we're interested in.
            try:
                product_group = attributes.find('.//ProductGroup').text.lower()
                entity.subcategory = self._subcategory_map[product_group]
            except:
                #print product_group
                #pprint(entity)
                return None
            
            attribute_elems = {
                'Title' : 'title', 
                'Brand' : 'brand', 
                'Publisher' : 'publisher', 
                'Studio' : 'studio_name', 
                'ReleaseDate' : 'original_release_date', 
                'Title' : 'title', 
            }
            
            item_elems = {
                'ASIN' : 'asin', 
                'DetailPageURL' : 'amazon_link', 
            }
            
            elems = []
            for k, v in attribute_elems.iteritems():
                elems.append((attributes, k, v))
            
            for k, v in item_elems.iteritems():
                elems.append((item, k, v))
            
            # parse all optional fields which are relatively easy-to-extract
            for elem in elems:
                node = elem[0].find(elem[1])
                if node is not None:
                    entity[elem[2]] = node.text
            
            # ensure that every entity has a valid title and a valid asin
            if entity.title is None or entity.asin is None:
                return None
            
            # parse the author(s)
            authors = attributes.findall('Author')
            if len(authors) > 0:
                entity.author = string.joinfields(map(lambda a: a.text, authors), ', ')
            
            # parse the artist(s)
            artists = attributes.findall('Artist')
            if len(artists) > 0:
                entity.artist_display_name = string.joinfields(map(lambda a: a.text, artists), ', ')
            
            # parse the running time
            running_time = attributes.find('RunningTime')
            if running_time is not None:
                length = running_time.pyval
                if running_time.get('Units').lower() == 'minutes':
                    # internally, duration is stored in seconds
                    length = length * 60
                
                entity.track_length = length
            
            # parse the manufacturer
            manufacturer = attributes.find('.//Manufacturer')
            if manufacturer:
                if entity.subcategory == 'book':
                    entity.publisher = manufacturer.text
                else:
                    entity.manufacturer = manufacturer.text
            
            # parse the price of this product
            price = attributes.find('ListPrice')
            if price is not None:
                entity.amount          = price.find('Amount').pyval
                entity.currency_code   = price.find('CurrencyCode').text
                entity.formatted_price = price.find('FormattedPrice').text
            
            # parse the amazon sales rank of this product
            sales_rank = item.find('SalesRank')
            if sales_rank is not None:
                entity.salesRank = sales_rank.pyval
            
            # parse the number of pages for a book
            num_pages = item.find('NumberOfPages')
            if num_pages is not None:
                entity.num_pages = num_pages.pyval
            
            # parse the track list for an album
            tracks = item.find('Tracks')
            if tracks is not None:
                tracks = tracks.findall('.//Track')
                tracks = list(track.text for track in tracks)
                
                if len(tracks) > 0:
                    entity.tracks = tracks
            
            # parse the editorial review as the closest thing we have to a 
            # real product description
            editorial_review = item.find('.//EditorialReview')
            if editorial_review is not None:
                desc = editorial_review.find('Content')
                
                if desc is not None:
                    desc = desc.text
                    soup = BeautifulSoup(desc)
                    entity.desc = ''.join(soup.findAll(text=True))
            
            # parse browse nodes to try and narrow in on a more accurate subcategory
            browse_nodes = item.find('BrowseNodes')
            if browse_nodes is not None:
                names = []
                
                for node in browse_nodes.findall('.//BrowseNode'):
                    name = node.find('Name')
                    
                    if name is not None:
                        name = name.text.lower()
                        names.append(name)
                
                #print "%s) %s" % (entity.title, names)
                if 'tv' in names:
                    entity.subcategory = 'tv'
                #elif 'singer-songwriters' in names:
                #    entity.subcategory = 'artist'
            
            # parse the binding to try and narrow in on a more accurate subcategory
            binding = attributes.find('Binding')
            if binding is not None:
                binding = binding.text.strip().lower()
                
                if binding in self._binding_blacklist:
                    return None
            
            # parse the ProductTypeName to try and narrow in on a more accurate subcategory
            product_type_name = attributes.find('ProductTypeName')
            if product_type_name is not None:
                product_type_name = product_type_name.text.strip().lower()
                
                try:
                    subcategory = self._product_type_names[product_type_name]
                    if subcategory is None:
                        return
                    else:
                        entity.subcategory = subcategory
                except KeyError:
                    pass
            
            # parse images associated with this product
            potential_images = {
                'SmallImage'  : 'tiny', 
                'MediumImage' : 'small', 
                'LargeImage'  : 'large', 
            }
            
            for k, v in potential_images.iteritems():
                image = item.find(k)
                
                if image is not None:
                    entity[v] = image.find('URL').text
            
            return entity
        except (AttributeError, KeyError):
            utils.printException()
            raise
            return None
    
    def _call(self, func, **kwargs):
        #pprint(kwargs)
        result = func(**kwargs)
        
        if result is None:
            return None
        else:
            result = re.sub('xmlns="[^"]*"', '', result)
            tree   = objectify.fromstring(result)
            
            """
            f = open('out.xml', 'w')
            f.write(etree.tostring(tree, pretty_print=True))
            f.close()
            """
            
            return tree
    
    def __str__(self):
        return self.__class__.__name__

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    defaults = {
        'SearchIndex'  : 'All', 
        'Availability' : 'Available', 
        'Sort'         : None, 
    }
    
    parser.add_option("-i", "--SearchIndex", action="store", default=defaults['SearchIndex'], 
                      help="Amazon SearchIndex parameter (defaults to %s)" % defaults['SearchIndex'])
    
    parser.add_option("-a", "--Availability", action="store", default=defaults['Availability'], 
                      help="Amazon Availability parameter (defaults to %s)" % defaults['Availability'])
    
    parser.add_option("-s", "--Sort", action="store", default=defaults['Sort'], 
                      help="Amazon Sort parameter to sort results (defaults to %s)" % defaults['Sort'])
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Print out verbose results")
    
    parser.add_option("-d", "--details", action="store_true", default=False, 
                      help="Query and parse details for all search results with an extra ItemLookup operation")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    
    options.Keywords = args[0]
    return (options, args)

def extract_amazon_args(options):
    func_args = copy.copy(options.__dict__)
    delete = []
    for arg in func_args:
        if arg == arg.lower() or func_args[arg] is None:
            delete.append(arg)
    
    for d in delete:
        del func_args[d]
    
    func_args['transform'] = not options.verbose
    return func_args

def main():
    options, args = parseCommandLine()
    
    api = AmazonAPI()
    api_args = extract_amazon_args(options)
    
    if options.details:
        results = api.item_detail_search(**api_args)
    else:
        results = api.item_search(**api_args)
    
    if options.verbose:
        print etree.tostring(results, pretty_print=True)
    else:
        for entity in results:
            pprint(entity)

if __name__ == '__main__':
    main()

