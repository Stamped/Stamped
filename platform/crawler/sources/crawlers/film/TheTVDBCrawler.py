#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time

from datetime       import datetime
from gevent.pool    import Pool
from AEntitySource  import AExternalEntitySource
from Schemas        import Entity
from libs.TheTVDB   import TheTVDB

__all__ = [ "TheTVDBCrawler" ]

class TheTVDBCrawler(AExternalEntitySource):
    """ 
        Entity crawler which extracts all of TheTVDB shows.
    """
    
    TYPES = set([ 'tv' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "TheTVDBCrawler", self.TYPES, 512)
        self.base = 'http://thetvdb.com'
        
        self._thetvdb   = TheTVDB()
        self._id_re     = re.compile('.*&id=([0-9]+).*')
        self._actor_re  = re.compile('.*___([^_]+)___as ([^_]+)___.*')
        self._season_re = re.compile('([0-9]+) - ([0-9]+)')
        self._date_re   = re.compile('([0-9]+)-([0-9]+)-([0-9]+)')
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation
    
    def _run(self):
        utils.log("[%s] parsing site %s" % (self, self.base))
        
        seed = 'http://thetvdb.com/index.php?string=&searchseriesid=&tab=listseries&function=Search'
        try:
            soup = utils.getSoup(seed)
        except:
            utils.printException()
            return
        
        pool = Pool(32)
        rows = soup.find('table', {'id' : 'listtable'}).findAll('tr')
        rows = rows[1:]
        count = 0
        
        for row in rows:
            cols = row.findAll('td')
            
            if 3 != len(cols):
                continue
            
            lang = cols[1].getText().lower()
            if lang != 'english':
                continue
            
            link = cols[0].find('a')
            name = link.getText()
            href = link.get('href')
            url  = '%s%s' % (self.base, href)
            
            pool.spawn(self._parse_series_page, name, url)
            count += 1
            if 0 == (count % 20):
                time.sleep(1)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parse_series_page(self, name, url):
        if '**' in name or 'DUPLICATE' in name or name.startswith('.hack'):
            return
        
        utils.log('[%s] parsing page %s (%s)' % (self, name, url))
        
        try:
            soup = utils.getSoup(url)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s (%s)" % (self, name, url))
            return
        
        contents = soup.findAll('div', {'id' : 'content'})
        header = contents[0]
        
        h1 = header.find('h1') 
        title = h1.getText()
        h1.extract()
        
        entity = Entity()
        
        # parse basic show info
        entity.title = title
        entity.subcategory = 'tv'
        
        desc = header.getText().replace('\r\n', '\n')
        if len(desc) > 5:
            entity.desc = desc
        
        entity.sources.thetvdb_id = self._id_re.match(url).groups()[0]
        
        # parse images
        images = map(lambda img: img.get('src'), soup.findAll('img', {'class' : 'banner'}))
        types  = [ 'posters', 'fanart', 'graphical', ]
        
        for image_type in types:
            filtered_images = filter(lambda img: image_type in img, images)
            if len(filtered_images) > 0:
                entity.image = "%s%s" % (self.base, filtered_images[0])
                break
        
        info = contents[1].find('table').find('table')
        rows = info.findAll('tr')
        
        # parse detailed show info
        info_map = {
            0 : 'original_release_date', 
            3 : 'air_time', 
            4 : 'network_name', 
            5 : 'genre', 
        }
        
        for k, k2 in info_map.iteritems():
            try:
                value = rows[k].findAll('td')[1].getText()
                if len(value) > 0:
                    entity[k2] = value
            except:
                utils.printException()
                pass
        
        # parse cast
        try:
            actors = "%s%s" % (self.base, contents[-1].findAll('a')[-1].get('href'))
            actors_soup = utils.getSoup(actors)
            
            infotables = actors_soup.findAll('table', {'class' : 'infotable'})
            cast = []
            
            for infotable in infotables:
                text = infotable.find('td').getText(separator='___')
                match = self._actor_re.match(text)
                if match is not None:
                    groups = match.groups()
                    cast.append('%s as %s' % (groups[0].strip(), groups[1].strip()))
                    # TODO: record actor images
            
            if len(cast) > 0:
                entity.cast = ', '.join(cast)
        except:
            pass
        
        # parse seasons
        try:
            seasons = "%s%s" % (self.base, contents[2].findAll('a')[-1].get('href'))
            seasons_soup = utils.getSoup(seasons)
            
            rows = seasons_soup.find('table', {'id' : 'listtable'}).findAll('tr')[1:]
            
            highest_season = -1
            earliest = None
            latest   = None
            
            # each row is an episode; loop through each episode, recording the 
            # earliest and latest air date for the show overall and the number 
            # of seasons the show ran for.
            for row in rows:
                tds = row.findAll('td')
                episode = tds[0].getText()
                match = self._season_re.match(episode)
                
                if match is not None:
                    groups  = match.groups()
                    season  = int(groups[0])
                    episode = int(groups[1])
                    
                    if season > highest_season:
                        highest_season = season
                    
                    date  = tds[2].getText()
                    match = self._date_re.match(date)
                    
                    if match is not None:
                        year, month, day = match.groups()
                        date = datetime(year=int(year), month=int(month), day=int(day))
                        
                        if earliest is None or date < earliest:
                            earliest = date
                        
                        if latest is None or date > latest:
                            latest = date
            
            if highest_season > 0:
                entity.num_seasons = highest_season
            
            if earliest is not None:
                entity.earliest_air_date = earliest
            
            if latest is not None:
                entity.latest_air_date = latest
        except:
            utils.printException()
        
        entity2 = self._thetvdb.lookup(entity.sources.thetvdb_id)
        
        if entity2 is not None:
            if entity2.mpaa_rating is not None:
                entity.mpaa_rating = entity2.mpaa_rating
            if entity2.imdb_id is not None:
                entity.imdb_id     = entity2.imdb_id
        
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('thetvdb', TheTVDBCrawler)

