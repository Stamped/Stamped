
import Globals
import feedparser, re

from datetime import *
from resolve.FullResolveContainer import FullResolveContainer
from Schemas import *

feeds = [
    'http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839&a=12170', 
    'http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839&a=12169', 
    'http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839&a=12168', 
]

enricher = FullResolveContainer()

for url in feeds[:1]:
    data = feedparser.parse(url)
    print '\n\n%s\n%s' % ('='*40, data['feed']['title'])
    
    id_num_re   = re.compile('.*\/([0-9]*)$')
    id_title_re = re.compile('[^a-zA-Z0-9:]')
    title_re    = re.compile('^([0-9][0-9]?). (.*) (\$[0-9.M]*)')
    info_re     = re.compile('[A-Za-z]+ ([^|]+) \| Runtime:(.+)$')
    genre_re    = re.compile('Genres:(.*)$')
    length_re   = re.compile('([0-9]+) *hr. *([0-9]+) min.')
    
    for entry in data.entries[:3]:
        if entry.title == 'More Movies':
            continue
        
        print 
        print '  %s' % entry.title
        
        fid_match = id_num_re.match(entry.id)
        assert fid_match is not None
        
        id_num = fid_match.groups()[0]
        id_title = None
        
        title = entry.title 
        
        title_match = title_re.match(entry.title)
        if title_match is not None:
            title_match_groups = title_match.groups()
            title = title_match_groups[1]
        
        id_title = id_title_re.sub('', title).lower()
        
        
        release_date = None
        
        release_date_match = entry.summary[-23:].split('Release Date:')
        if len(release_date_match) == 2:
            month, day, year = map(lambda x: int(x), release_date_match[-1].split('/'))
            if month >= 1 and month <= 12 and day >= 1 and day <= 31 and year > 1800 and year < 2200:
                release_date = datetime(year, month, day)
        
        print '  TITLE:     %s' % title
        print '  ID:        %s_%s' % (id_num, id_title)
        print '  RELEASED:  %s' % release_date
        
        entity = Entity()
        entity.subcategory = 'movie'
        entity.title = title
        entity.release_date = release_date
        entity.fandango_id  = id_num
        entity.fandango_url = 'http://www.fandango.com/%s_%s/movieoverview' % (id_title, id_num)
        entity.fandango_source = 'fandango'
        entity.fandango_timestamp = datetime.utcnow()
        
        modified = enricher.enrichEntity(entity,{})
        print modified
        print entity.value


"""
fandango_id = 12345
title = '21 Jump Street'
release_date = parseDateString('2012-03-12')


movie = FandangoMovie(fandango_id, title,release_date)
resolver = Resolver()
resolvedMovie = None

sources = [TMDBSource(), iTunesSource(), AmazonSource(), StampedSource()]
for source in sources:
    gen = source.matchSource(movie)
    results = resolver.resolve(movie, gen)

    if len(results) > 0:
        similarities, best = results[0]
        if similarities['resolved']:
            resolvedMovie = best
            break

if resolvedMovie is not None:
    source = resolvedMovie.source
    if source == 'stamped':
        stampedSource = StampedSource()
        results = resolver.resolve(resolvedMovie, stampedSource(resolvedMovie))
        try:
            result = results[0]
            if result[0]['resolved']:
                entity_id = result[1].key
        except Exception:
            pass
            """