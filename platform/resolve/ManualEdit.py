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
    import urlparse
    from api.Schemas            import *
    from resolve.EntityReviver import *
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

def _thetvdb():
    import libs.TheTVDB
    return libs.TheTVDB.globalTheTVDB()

def _itunes():
    import libs.iTunes
    return libs.iTunes.globaliTunes()

def _fullResolveContainer():
    import resolve.FullResolveContainer
    return resolve.FullResolveContainer.FullResolveContainer()

def _stampedAPI():
    from api import MongoStampedAPI
    return MongoStampedAPI.globalMongoStampedAPI()

def _entityDB():
    db = _stampedAPI()._entityDB
    return db

# copied HTTPSchemas.py
def _cleanImageURL(url):
    domain = urlparse.urlparse(url).netloc

    if 'mzstatic.com' in domain:
        # try to return the maximum-resolution apple photo possible if we have 
        # a lower-resolution version stored in our db
        url = url.replace('100x100', '200x200').replace('170x170', '200x200')

    elif 'amazon.com' in domain:
        # strip the 'look inside' image modifier
        url = amazon_image_re.sub(r'\1.jpg', url)
    elif 'nflximg.com' in domain:
        # replace the large boxart with hd
        url = url.replace('/large/', '/ghd/')

    return url

def _buildOpenTableURL(opentable_id=None, opentable_nickname=None, client=None):
    if opentable_id is not None:
        if client is not None and isinstance(client, Client) and client.is_mobile == True:
            return 'http://m.opentable.com/Restaurant/Referral?RestID=%s&Ref=9166' % opentable_id
        else:
            return 'http://www.opentable.com/single.aspx?rid=%s&ref=9166' % opentable_id

    if opentable_nickname is not None:
        return 'http://www.opentable.com/reserve/%s&ref=9166' % opentable_nickname

    return None

# Paul, add your extra output here
def extraInfo(entity):
    extra = []
    if entity.isType('artist') and entity.albums is not None and len(entity.albums) > 0:
        for album in entity.albums[:10]:
            try:
                image_url        = _cleanImageURL(album.images[0].sizes[0].url)
                extra.append("""
<img src="%s"/>
<a href="%s">%s</a><br/>
                    """ % (image_url, image_url, album.title))
            except Exception as e:
                print e
    itunes_id = entity.sources.itunes_id
    if itunes_id is not None:
        extra.append('<h1>From iTunes:</h1><br/>')
        entity_group = ''
        if entity.isType('artist'):
            entity_group = 'album'
        elif entity.isType('tv'):
            entity_group = 'tvSeason'
        itunes_results = _itunes().method('lookup', id=itunes_id, entity=entity_group)
        for result in itunes_results['results']:
            if 'artworkUrl100' in result:
                art_url = _cleanImageURL(result['artworkUrl100'])
                extra.append("""
<img src="%s"/>
<a href="%s">%s</a><br/>
                """ % (art_url, art_url, result.pop('collectionName','<unknown>')))

    extra.append("""
<a href="https://api1.stamped.com/v1/entities/show.json?entity_id=%s">entity/show.json</a><br/>
<a href="https://api1.stamped.com/v1/entities/edit.html?secret=supersmash&entity_id=%s">entity/edit.html</a><br/>
        """ % (entity.entity_id, entity.entity_id))
    return ''.join(extra)

def _quickLink(key, value):
    if key == 'tombstone_id' and value:
        value = 'v1/entities/edit.html?secret=supersmash&entity_id=' + value
    elif value is None or value == '' or value == _invalidPlaceholder or value.find('http') == -1:
        return ""
    return """
<a href="%s">%s</a>
""" % (value, key)

def primaryImageURL(entity):
    try:
        return _cleanImageURL(entity.images[0].sizes[0].url)
    except Exception as e:
        print e
        return None


def formForEntity(entity_id, **hidden_params):
    db = _entityDB()
    entity = db.getEntity(entity_id)
    fields = {}

    print("%s" % entity.isType('movie'))
    if entity.kind == 'place':
        for k in _place_fields:
            fields[k] = getattr(entity, k)
        singleplatform_url = ''
        singleplatform_id = entity.sources.singleplatform_id
        if singleplatform_id is not None:
            singleplatform_url = "http://www.singlepage.com/%s/menu" % singleplatform_id
        fields['singleplatform_url'] = singleplatform_url

        opentable_url = ''
        opentable_id = entity.sources.opentable_id
        if opentable_id is not None:
            opentable_url = _buildOpenTableURL(opentable_id)
        fields['opentable_url'] = opentable_url
    else:
        itunes_id = entity.sources.itunes_id
        itunes_url = ''
        if itunes_id is not None:
            itunes_url = _invalidPlaceholder
            try:
                itunes_data = _itunes().method('lookup',id=itunes_id)['results'][0]
                if entity.isType('artist'):
                    itunes_url = itunes_data['artistLinkUrl']
                elif entity.isType('album'):
                    itunes_url = itunes_data['collectionViewUrl']
                elif entity.isType('track') or entity.isType('movie') or entity.isType('app') or entity.isType('book'):
                    itunes_url = itunes_data['trackViewUrl']
                elif entity.isType('tv'):
                    try:
                        itunes_url = itunes_data['artistViewUrl']
                    except KeyError:
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
        fields['spotify_id'] = entity.sources.spotify_id
    if entity.isType('tv') or entity.isType('movie') or entity.isType('album') or entity.isType('track') or entity.isType('book'):
        amazon_url = ''
        if entity.sources.amazon_id and entity.sources.amazon_url:
            amazon_url = entity.sources.amazon_url
        fields['amazon_url'] = amazon_url
    if entity.isType('tv') or entity.isType('movie'):
        imdb_url = ''
        imdb_id = entity.sources.imdb_id
        if imdb_id is None:
            if entity.isType('movie'):
                tmdb_id = entity.sources.tmdb_id
                if tmdb_id is not None:
                    try:
                        imdb_id = _tmdb().movie_info(tmdb_id)['imdb_id']
                    except KeyError:
                        pass
            elif entity.isType('tv'):
                tvdb_id = entity.sources.thetvdb_id
                if tvdb_id is not None:
                    try:
                        imdb_id = _thetvdb().lookup(tvdb_id).sources.imdb_id
                    except Exception as e:
                        print(e)
        if imdb_id is not None:
            imdb_url = 'http://www.imdb.com/title/%s/' % imdb_id    
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
    if entity.isType('movie'):
        fandango_url = ''
        if entity.sources.fandango_url and entity.sources.fandango_id:
            fandango_url = entity.sources.fandango_url
        fields['fandango_url'] = fandango_url
    fields['image_url'] = primaryImageURL(entity)
    fields['tombstone_id'] = getattr(entity.sources, 'tombstone_id', None)
    nemesis_ids = getattr(entity.sources, 'nemesis_ids')
    fields['nemesis_ids'] = ', '.join(nemesis_ids) if nemesis_ids else ''
    hidden_params['entity_id'] = entity_id
    html = []
    desc = entity.desc
    if desc is None:
        desc = ''
    html.append("""
<html>
<head>
    <title>%s</title>
</head>
<body>
<form action="update.html" method="post">
title:<input type="text" name="title" value="%s"/><br/>
desc:<textarea name="desc" style="width:300pt; height:100pt;">%s</textarea><br/>
 """ % (entity.title, entity.title, desc))
    if entity.isType('album') or entity.isType('artist'):
        html.append("""
<input type="checkbox" name="purge_tracks"/>Purge Tracks<br/>
            """)

    html.append("""
<input type="checkbox" name="purge_tombstone"/>Purge Tombstone<br/>
            """)
    html.append("""
<input type="checkbox" name="purge_image"/>Purge Image<br/>
            """)
    for k,v in hidden_params.items():
        html.append("""
<input type="hidden" name="%s" value="%s"/>
            """ % (k,v))
    for k,v in fields.items():
        if v is None:
            v = ''
        if k == 'image_url' and v != '':
            html.append("""
<img src="%s"/><br/>
                """ % v)
        html.append("""
%s: <input type="text" name="%s" value="%s" size="100"/>%s<br />
            """ % (k, k, v, _quickLink(k,v)))

    html.append("""

<input type="submit" value="Submit" />
</form>
<br/>
%s
</body>
</html>

""" % (extraInfo(entity),))
    return ''.join(html)

def update(updates):
    bad_versions = set(['', _invalidPlaceholder])
    db = _entityDB()
    now = datetime.utcnow()
    entity = db.getEntity(updates.entity_id)
    if updates.purge_image == 'on':
        del entity.images
        del entity.images_timestamp
        del entity.images_source
    if updates.title:
        entity.title = updates.title
    if updates.desc:
        entity.desc = updates.desc
        entity.desc_source = 'manual'
        entity.desc_timestamp = now
    simple_fields = []
    if entity.kind == 'place':
        simple_fields.extend(_place_fields)
    singleplatform_url = updates.singleplatform_url
    if singleplatform_url is not None and singleplatform_url not in bad_versions:
        singleplatform_id = re.match(r'http://www.singlepage.com/(.+)/menu(\?.*)?', singleplatform_url).group(1)
        entity.sources.singleplatform_url = singleplatform_url
        entity.sources.singleplatform_id = singleplatform_id
        entity.sources.singleplatform_source = 'manual'
        entity.sources.singleplatform_timestamp = now
    rdio_url = updates.rdio_url
    if rdio_url is not None and rdio_url not in bad_versions:
        rdio_data = _rdio().method('getObjectFromUrl', url=rdio_url)
        rdio_id = rdio_data['result']['key']
        entity.sources.rdio_id = rdio_id
        entity.sources.rdio_url = rdio_url
        entity.sources.rdio_source = 'manual'
        entity.sources.rdio_timestamp = now
    imdb_url = updates.imdb_url
    if imdb_url is not None and imdb_url not in bad_versions:
        imdb_id = imdb_url.replace('http://www.imdb.com/title/','').replace('/','')
        entity.sources.imdb_id = imdb_id
        entity.sources.imdb_timestamp = now
        entity.sources.imdb_source = 'manual'
        if entity.isType('movie'):
            tmdb_data = _tmdb().movie_info(imdb_id)
            entity.sources.tmdb_id = tmdb_data['id']
            entity.sources.tmdb_source = 'manual'
            entity.sources.tmdb_timestamp = now
        elif entity.isType('tv'):
            tvdb_raw_data = _thetvdb().lookupIMDBRaw(imdb_id)
            match = re.match(r'.*<id>(\d+)</id>.*', tvdb_raw_data.replace('\n',''))
            tvdb_id = match.group(1)
            entity.sources.thetvdb_id = tvdb_id
            entity.sources.thetvdb_source = 'manual'
            entity.sources.thetvdb_timestamp = now 
    spotify_id = updates.spotify_id
    if spotify_id is not None and spotify_id not in bad_versions:
        entity.sources.spotify_id = spotify_id
        entity.sources.spotify_source = 'manual'
        entity.sources.spotify_timestamp = now
    amazon_url = updates.amazon_url
    if amazon_url is not None and amazon_url not in bad_versions:
        amazon_id = re.match(r'http://www.amazon.com(/.+)+/dp/([A-Za-z0-9]+)(/.+)?(\?.+)?', amazon_url).group(2)
        entity.sources.amazon_id = amazon_id
        entity.sources.amazon_url = amazon_url
        entity.sources.amazon_source = 'manual'
        entity.sources.amazon_underlying = amazon_id
        entity.sources.amazon_timestamp = now
    netflix_url = updates.netflix_url
    if netflix_url is not None and netflix_url not in bad_versions:
        match = re.match(r'http(s)?://movies.netflix.com/WiMovie/(.+/)?(\d+)(\?.+)?',netflix_url)
        netflix_number = match.group(3)
        netflix_id = None
        if entity.isType('movie'):
            netflix_id = 'http://api.netflix.com/catalog/titles/movies/%s' % netflix_number
        elif entity.isType('tv'):
            netflix_id = 'http://api.netflix.com/catalog/titles/series/%s' % netflix_number
        if netflix_id is not None:
            entity.sources.netflix_id = netflix_id
            entity.sources.netflix_source = 'manual'
            entity.sources.netflix_timestamp = now
    itunes_url = updates.itunes_url
    if itunes_url is not None and itunes_url not in bad_versions:
        itunes_id = None
        if entity.isType('artist'):
            match = re.match(r'http://itunes.apple.com/(.+)/artist/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(3)
        elif entity.isType('album'):
            match = re.match(r'http://itunes.apple.com/(.+)/album/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(3)
        elif entity.isType('track'):
            match = re.match(r'http://itunes.apple.com/(.+)/album/(.+)/id(\d+)\?i=(\d+)', itunes_url)
            itunes_id = match.group(4)
        elif entity.isType('book'):
            match = re.match(r'http://itunes.apple.com/(.+)/book/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(3)
        elif entity.isType('tv'):
            match = re.match(r'http://itunes.apple.com/(.+)/tv-show/(.+)/id(\d+)(\?.+)?', itunes_url)
            if match is None:
                match = re.match(r'http://itunes.apple.com/(.+)/tv-season/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(3)
        elif entity.isType('movie'):
            match = re.match(r'http://itunes.apple.com/(.+)/movie/(.+)/id(\d+)(\?.+)?', itunes_url)
            itunes_id = match.group(3)

        if itunes_id is not None:
            itunes_data = _itunes().method('lookup', id=itunes_id)['results'][0]
            if 'previewUrl' in itunes_data:
                entity.sources.itunes_preview = itunes_data['previewUrl']
            if entity.isType('artist'):
                entity.sources.itunes_url = itunes_data['artistLinkUrl']
            elif entity.isType('album'):
                entity.sources.itunes_url = itunes_data['collectionViewUrl']
            elif entity.isType('track') or entity.isType('movie') or entity.isType('app') or entity.isType('book'):
                entity.sources.itunes_url = itunes_data['trackViewUrl']
            elif entity.isType('tv'):
                try:
                    entity.sources.itunes_url = itunes_data['artistViewUrl']
                except KeyError:
                    entity.sources.itunes_url = itunes_data['artistLinkUrl']
            entity.sources.itunes_id = itunes_id
            entity.sources.itunes_source = 'manual'
            entity.sources.itunes_timestamp = now
    fandango_url = updates.fandango_url
    if fandango_url is not None and fandango_url not in bad_versions and not fandango_url.startswith('http://www.qksrv.net/'):
        #'http://www.qksrv.net/click-5348839-10576760?url=http%3a%2f%2fmobile.fandango.com%3fa%3d%26m%3d154970
        match = re.match(r'http://www.fandango.com/(.+)_(\d+)/(.+)(\?.+)?', fandango_url)
        fandango_raw_id = match.group(2)
        entity.sources.fandango_id = 'http://www.fandango.com/rss/%s' % fandango_raw_id
        entity.sources.fandango_url = 'http://www.qksrv.net/click-5348839-10576760?url=http%3a%2f%2fmobile.fandango.com%3fa%3d%26m%3d' + fandango_raw_id
        entity.sources.fandango_timestamp = now
        entity.sources.fandango_source = 'manual'
    opentable_url = updates.opentable_url
    if opentable_url is not None and opentable_url not in bad_versions:
        match = re.match(r'http://www.opentable.com/(.+)?\?(.+)?rid=(\d+)(.+)', opentable_url)
        opentable_nickname = None
        opentable_id = None
        if match is not None:
            opentable_nickname = match.group(1)
            opentable_id = match.group(3)
        else:
            match = re.match(r'http://www.opentable.com/single.aspx\?rid=(\d+)&ref=9166', opentable_url)
            if match is not None:
                opentable_id = match.group(1)
            else:
                match = re.match(r'http://www.opentable.com/(.+)\?rid=(\d+)&ref=9166', opentable_url)
                opentable_id = match.group(2)
                opentable_nickname = match.group(1)

        entity.sources.opentable_id = opentable_id
        entity.sources.opentable_nickname = opentable_nickname
        entity.sources.opentable_source = 'manual'
        entity.sources.opentable_timestamp = now
    image_url = updates.image_url
    if image_url is not None and image_url not in bad_versions:
        img = ImageSchema()
        size = ImageSizeSchema()
        size.url = image_url
        img.sizes = [size]
        entity.images = [img]
        entity.images_source = 'manual'
        entity.images_timestamp = now
    if updates.purge_tracks == 'on':
        del entity.tracks
        del entity.tracks_timestamp
        del entity.tracks_source

    tombstone_id = updates.tombstone_id
    if tombstone_id is not None and tombstone_id not in bad_versions:
        entity.sources.tombstone_id = tombstone_id
        entity.sources.tombstone_source = 'manual'
        entity.sources.tombstone_timestamp = now
    nemesis_ids = updates.nemesis_ids
    if nemesis_ids is not None and nemesis_ids not in bad_versions:
        entity.sources.nemesis_ids = [item.strip() for item in nemesis_ids.split(',')]
        entity.sources.nemesis_source = 'manual'
        entity.sources.nemesis_timestamp = now
        revive_tombstoned_entities(entity.entity_id)
    if updates.purge_tombstone == 'on':
        del entity.sources.tombstone_id
        del entity.sources.tombstone_timestamp
        del entity.sources.tombstone_source
    for k in simple_fields:
        v = getattr(updates, k)
        if v == '':
            v = None
        if v != _invalidPlaceholder:
            setattr(entity, k, v)
    db.updateEntity(entity)
    _stampedAPI().mergeEntity(entity)




