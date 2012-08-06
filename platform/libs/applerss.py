#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import Entity
import copy, json, re, urllib, utils, logs

from resolve                import EntityProxyContainer
from gevent.pool            import Pool
from resolve.iTunesSource   import iTunesSource
from pprint                 import pprint, pformat


__all__ = [ "AppleRSS", "AppleRSSError" ]

class AppleRSSError(Exception):
    pass

class AppleRSS(object):
    
    DEFAULT_FORMAT = 'json'
    
    _webobject_feeds = set([
        'newreleases', 
        'justadded', 
    ])
    
    def __init__(self):
        self._id_re  = re.compile('.*\/id([0-9]+).*')
        self._source = iTunesSource()
    
    def get_top_albums(self, **kwargs):
        return self._parse_feed('topalbums', **kwargs)
    
    def get_top_songs(self, **kwargs):
        return self._parse_feed('topsongs', **kwargs)
    
    def get_top_free_apps(self, **kwargs):
        return self._parse_feed('topfreeapplications', **kwargs)
    
    def get_top_paid_apps(self, **kwargs):
        return self._parse_feed('toppaidapplications', **kwargs)
    
    def get_top_grossing_apps(self, **kwargs):
        return self._parse_feed('topgrossingapplications', **kwargs)
    
    def get_new_releases(self, **kwargs):
        return self._parse_feed('newreleases', **kwargs)
    
    def get_just_added(self, **kwargs):
        return self._parse_feed('justadded', **kwargs)
    
    def _parse_feed(self, feedname, **kwargs):
        webobject   = (feedname in self._webobject_feeds)
        
        # extract keyword arguments and defaults
        region      = kwargs.pop('region', 'us')
        limit       = kwargs.pop('limit', 10)
        genre       = kwargs.pop('genre', None)
        explicit    = kwargs.pop('explicit', True)
        transform   = kwargs.pop('transform', True)
        format      = kwargs.pop('format', 'xml' if webobject else self.DEFAULT_FORMAT)

        if format not in [ 'xml', 'json' ]:
            raise AppleRSSError("invalid request format")
        
        if webobject:
            url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wpa/MRSS/%s/sf=143441/' % (feedname, )
        else:
            url = 'http://itunes.apple.com/%s/rss/%s/' % (region, feedname)
        
        if limit is not None:
            url = '%slimit=%d/' % (url, limit)
        
        if genre is not None:
            url = '%sgenre=%s/' % (url, genre)
        
        if explicit is not None:
            url = '%sexplicit=%s/' % (url, str(explicit).lower())
        
        if webobject:
            url += 'rss.%s' % format
        else:
            url += format

        # attempt to download feed
        utils.log(url)
        data = utils.getFile(url)

        """
        f=open('out.xml', 'w')
        f.write(data)
        f.close()
        """
        
        if not transform:
            return data
        
        try:
            data = json.loads(data)
        except ValueError:
            utils.printException()
            utils.log(data)
            return []
        
        entries  = data['feed']['entry']
        entities = []
        
        if isinstance(entries, dict):
            entries = [ entries ]
        
        def _parse_entry(entities, entry):
            try:
                # We skip pre-orders because we can't actually look them up by ID. This is actually a pretty fatal
                # error because right now we don't even use the data in the feed itself; we immediately re-crawl based
                # on the iTunes ID. Anyway, there doesn't seem to be any big advantage to having preorders, so this is
                # hardly the most pressing problem.

                if 'id' in entry and 'label' in entry['id']:
                    if '/preorder/' in entry['id']['label']:
                        logs.info('Skipping preorder!')
                        return
                else:
                    logs.info('WARNING: Missing id.label!')
                entity = self._parse_entity(entry)
                if entity is not None:
                    entities.append(entity)
            except:
                utils.printException()

        pool = Pool(16)
        for entry in entries:
            pool.spawn(_parse_entry, entities, entry)
        
        pool.join()
        return entities
    
    def _parse_entity(self, entry):
        logs.info(pformat(entry))
        aid = entry['id']['attributes']['im:id']

        # TODO: Why can't we parse the proxies directly from the feed results?
        proxy = self._source.entityProxyFromKey(aid)
        return EntityProxyContainer.EntityProxyContainer().addProxy(proxy).buildEntity()
        
    def _get_id(self, s):
        match = self._id_re.match(s)
        if match is not None:
            return match.groups()[0]
        
        return None

def main():
    rss = AppleRSS()
    #ret = rss.get_top_albums(limit=10, transform=True)
    ret = rss.get_top_songs(limit=10, transform=True)
    
    for entity in ret:
        pprint(entity.value)

if __name__ == '__main__':
    main()

