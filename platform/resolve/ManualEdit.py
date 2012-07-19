#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals

try:
    from pprint                 import pformat
    from datetime               import datetime
    import logs
    import re
except:
    raise

_invalidPlaceholder = '__INVALID__'

_place_fields = ['address_street', 'address_street_ext', 'address_locality', 'address_region', 'address_postcode', 'address_country', 'phone']

def _rdio():
    import libs.Rdio
    return libs.Rdio.globalRdio()

def _tmdb():
    import libs.TMDB
    return libs.TMDB.globalTMDB()

def _entityDB():
    from api import MongoStampedAPI
    stamped_api = MongoStampedAPI.globalMongoStampedAPI()
    db = stamped_api._entityDB
    return db

def _itunes():
    import libs.iTunes
    return libs.iTunes.globaliTunes()

def _fullResolveContainer():
    import resolve.FullResolveContainer
    return resolve.FullResolveContainer.FullResolveContainer()

def formForEntity(entity_id, **hidden_params):
    db = _entityDB()
    entity = db.getEntity(entity_id)
    fields = {}

    print("%s" % entity.isType('movie'))
    if entity.kind == 'place':
        for k in _place_fields:
            fields[k] = getattr(entity, k)
    else:
        itunes_id = entity.sources.itunes_id
        itunes_url = ''
        if itunes_id is not None:
            itunes_url = _invalidPlaceholder
            try:
                itunes_data = _itunes().method('lookup',id=itunes_id)['results'][0]
                if entity.isType('artist'):
                    itunes_url = itunes_data['artistViewUrl']
                elif entity.isType('album'):
                    itunes_url = itunes_data['collectionViewUrl']
                elif entity.isType('track') or entity.isType('movie') or entity.isType('app') or entity.isType('book'):
                    itunes_url = itunes_data['trackViewUrl']
                elif entity.isType('tv'):
                    itunes_url = itunes_data['artistLinkUrl']
            except KeyError:
                raise
            except IndexError:
                raise
        fields['itunes_url'] = itunes_url

    if entity.isType('artist') or entity.isType('album') or entity.isType('track'):
        rdio_url = ''
        rdio_id = entity.sources.rdio_id
        if rdio_id is not None:
            rdio_url = _invalidPlaceholder
            try:
                rdio_url = _rdio().method('get', keys=rdio_id)['result'][rdio_id]['shortUrl']
            except KeyError:
                pass
        fields['rdio_url'] = rdio_url
    if entity.isType('tv') or entity.isType('movie'):
        imdb_url = ''
        tmdb_id = entity.sources.tmdb_id
        if tmdb_id is not None:
            imdb_url = _invalidPlaceholder
            try:
                imdb_id = _tmdb().movie_info(tmdb_id)['imdb_id']
                imdb_url = 'http://www.imdb.com/title/%s/' % imdb_id
            except KeyError:
                pass
        fields['imdb_url'] = imdb_url
        netflix_url = ''
        netflix_id = entity.sources.netflix_id
        if netflix_id is not None:
            netflix_url = _invalidPlaceholder
            try:
                netflix_number = netflix_id.split('/')[-1]
                netflix_url = 'http://movies.netflix.com/WiMovie/%s' % netflix_number
            except Exception:
                pass
        fields['netflix_url'] = netflix_url
    hidden_params['entity_id'] = entity_id
    html = []
    html.append("""
<html>
<head>
    <title>%s</title>
</head>
<body>
<form action="update.html" method="post">
title:<input type="text" name="title" value="%s"/><br/>
desc:<textarea name="desc" style="width:300pt; height:100pt;">%s</textarea><br/>
 """ % (entity.title, entity.title, entity.desc))
    for k,v in hidden_params.items():
        html.append("""
<input type="hidden" name="%s" value="%s"/>
            """ % (k,v))
    for k,v in fields.items():
        if v is None:
            v = ''
        html.append("""
%s: <input type="text" name="%s" value="%s" size="100"/><br />
            """ % (k, k, v))

    html.append("""

<input type="submit" value="Submit" />
</form>
</body>
</html>

""")
    return ''.join(html)

def update(updates):
    db = _entityDB()
    now = datetime.utcnow()
    entity = db.getEntity(updates.entity_id)
    if updates.title:
        entity.title = updates.title
    if updates.desc:
        entity.desc = updates.desc
        entity.desc_source = 'seed'
        entity.desc_timestamp = now
    simple_fields = []
    if entity.kind == 'place':
        simple_fields.extend(_place_fields)

    bad_versions = set(['', _invalidPlaceholder])
    rdio_url = updates.rdio_url
    if rdio_url is not None and rdio_url not in bad_versions:
        rdio_data = _rdio().method('getObjectFromUrl', url=rdio_url)
        rdio_id = rdio_data['result']['key']
        entity.sources.rdio_id = rdio_id
        entity.sources.rdio_source = 'seed'
        entity.sources.rdio_timestamp = now
    imdb_url = updates.imdb_url
    if imdb_url is not None and imdb_url not in bad_versions:
        imdb_id = imdb_url.replace('http://www.imdb.com/title/','').replace('/','')
        tmdb_data = _tmdb().movie_info(imdb_id)
        entity.sources.tmdb_id = tmdb_data['id']
        entity.sources.tmdb_source = 'seed'
        entity.sources.tmdb_timestamp = now
    netflix_url = updates.netflix_url
    if netflix_url is not None and netflix_url not in bad_versions:
        match = re.match(r'http://movies.netflix.com/WiMovie/(.+/)?(\d+)(\?trkid=\d+)?',netflix_url)
        netflix_number = match.group(2)
        netflix_id = None
        if entity.isType('movie'):
            netflix_id = 'http://api.netflix.com/catalog/titles/movies/%s' % netflix_number
        if netflix_id is not None:
            entity.sources.netflix_id = netflix_id
            entity.sources.netflix_source = 'seed'
            entity.sources.netflix_timestamp = now
    itunes_url = updates.itunes_url
    if itunes_url is not None and itunes_url not in bad_versions:
        itunes_id = None
        if entity.isType('artist'):
            match = re.match(r'http://itunes.apple.com/us/artist/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(2)
        if itunes_id is not None:
            itunes_data = _itunes.method('lookup', id=itunes_id)['results'][0]
            if 'previewUrl' in itunes_data:
                entity.sources.itunes_preview = itunes_data['previewUrl']
            if entity.isType('artist'):
                entity.sources.itunes_url = itunes_data['artistViewUrl']
            elif entity.isType('album'):
                entity.sources.itunes_url = itunes_data['collectionViewUrl']
            elif entity.isType('track') or entity.isType('movie') or entity.isType('app') or entity.isType('book'):
                entity.sources.itunes_url = itunes_data['trackViewUrl']
            elif entity.isType('tv'):
                entity.sources.itunes_url = itunes_data['artistLinkUrl']
            entity.sources.itunes_id = itunes_id
            entity.sources.itunes_source = 'seed'
            entity.sources.itunes_timestamp = now
    for k in simple_fields:
        v = getattr(updates, k)
        if v == '':
            v = None
        if v != _invalidPlaceholder:
            setattr(entity, k, v)
    db.updateEntity(entity)




