#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gevent, gzip, os, re, time

from crawler.sources.dumps.Netflix import NetflixClient
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity
from pprint import pprint

try:
    from lxml import etree
except ImportError:
    utils.log("warning: couldn't find lxml")

__all__ = [ "NetflixDump" ]

NETFLIX_API_KEY    = 'nr5nzej56j3smjra6vtybbvw'
NETFLIX_API_SECRET = 'H5A633JsYk'

class NetflixDump(AExternalDumpEntitySource):
    """
        Netflix API wrapper
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, 'Netflix', self.TYPES, None)
        
        self._client = NetflixClient("Stamped", NETFLIX_API_KEY, NETFLIX_API_SECRET, '', False)
    
    def getMaxNumEntities(self):
        return 64000 # approximation for now
    
    def _run(self):
        utils.log("[%s] parsing movie index" % (self, ))
        
        filename = 'netflix.index.gz'
        
        if not os.path.exists(filename):
            utils.log("[%s] downloading movie index (this may take a few minutes...)" % (self, ))
            index = self._client.catalog.getIndex()
            
            out = gzip.open(filename, 'wb')
            out.write(index)
            out.close()
        
        count = self._parse_dump(filename)
        
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d movies" % (self, count))
    
    def _parse_dump(self, filename):
        f = gzip.open(filename, 'rb')
        context = iter(etree.iterparse(f, events=("start", "end")))
        
        event, root = context.next()
        
        nid_re              = re.compile('.*\/([0-9]*)$')
        language_re         = re.compile('.*\/languages$')
        match_genre_re      = re.compile('.*\/genres$')
        match_ratings_re    = re.compile('.*\/mpaa_ratings$')
        
        match_genre_func    = lambda c: re.match(match_genre_re, c.get('scheme')) is not None
        match_ratings_func  = lambda c: re.match(match_ratings_re, c.get('scheme')) is not None
        match_language_func = lambda c: re.match(language_re, c.get('scheme')) is not None
        
        count = 0
        bonus_materials = set()
        
        # loop through each XML catalog_title element and parse it as a movie Entity
        for event, elem in context:
            if event == "end" and elem.tag == "catalog_title":
                root.clear()
                
                try:
                    rating_elem = elem.find('average_rating')
                    if rating_elem is None:
                        continue
                    
                    entity = Entity()
                    nid = elem.find('id').text
                    nid = int(re.match(nid_re, nid).groups()[0])
                    
                    bonus_materials_elem = elem.find('.//bonus_materials')
                    if bonus_materials_elem is not None:
                        links = map(lambda l: l.get('href'), bonus_materials_elem.findall('link'))
                        
                        for link in links:
                            bonus_material_id = int(re.match(nid_re, link).groups()[0])
                            #bonus_material_id = re.match(bonus_materials_id_re, link).groups()[0]
                            bonus_materials.add(bonus_material_id)
                    
                    if nid in bonus_materials:
                        continue
                    
                    title = elem.find('title').get('regular')
                    titlel = title.lower()
                    
                    if 'bonus material' in titlel:
                        continue
                    
                    entity.title = title
                    entity.nid = nid
                    entity.desc = elem.find('.//synopsis').text
                    entity.nrating = float(rating_elem.text)
                    
                    categories = elem.findall('category')
                    
                    genres = map(lambda c: c.get('label'), filter(match_genre_func, categories))
                    entity.ngenres = genres
                    
                    tv = False
                    for genre in genres:
                        if 'tv' in genre.lower():
                            tv = True
                            break
                    
                    if tv:
                        entity.subcategory = 'tv'
                    else:
                        entity.subcategory = 'movie'
                    
                    ratings = map(lambda c: c.get('label'), filter(match_ratings_func, categories))
                    if 1 == len(ratings):
                        entity.mpaa_rating = ratings[0]
                    
                    images = elem.find('.//box_art').findall('link')
                    if 3 == len(images) or 4 == len(images):
                        entity.tiny  = images[0].get('href')
                        entity.small = images[1].get('href')
                        entity.large = images[2].get('href')
                        
                        if 4 == len(images):
                            entity.hd = images[3].get('href')
                    
                    links = filter(lambda l: 'web page' == l.get('title'), elem.findall('link'))
                    if 1 == len(links):
                        entity.nurl = links[0].get('href')
                    
                    language_elem  = elem.find('.//languages_and_audio')
                    language_elems = filter(match_language_func, language_elem.findall('.//category'))
                    
                    release_year_elem = elem.find('release_year')
                    if release_year_elem is not None:
                        entity.original_release_date = release_year_elem.text
                    
                    duration = elem.find('runtime')
                    if duration is not None:
                        entity.track_length = duration.text
                    
                    languages = set()
                    for elem2 in language_elems:
                        languages.add(elem2.get('label').lower())
                    
                    if 'english' not in languages:
                        continue
                    
                    #utils.log(entity.title)
                    #pprint(entity.getDataAsDict())
                    
                    """
                    self._globals['n'] = elem
                    self._globals['s'] = etree.tostring(elem, pretty_print=True)
                    self._globals['e'] = entity
                    break
                    """
                    
                    self._output.put(entity)
                    count += 1
                    
                    # give the downstream consumer threads an occasional chance to work
                    if 0 == (count % 512):
                        time.sleep(0.1)
                    
                    elem.clear()
                except Exception, e:
                    utils.printException()
                    utils.log(elem.find('title').get('regular'))
        
        f.close()
        return count

from crawler import EntitySources
EntitySources.registerSource('netflix', NetflixDump)

