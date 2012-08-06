from __future__ import absolute_import

from sys import argv
import datetime
import pickle
from collections import defaultdict

popularDate = {}
ranks = defaultdict(list)
with open(argv[1]) as fin:
    for line in fin:
        song = eval(line)
        key = song['name'].strip(), song['artist'].strip()
        popularDate[key] = song['last_popular']
        ranks[key].append(song['rank'])

for key, popular in popularDate.iteritems():
    allRanks = ranks[key]
    bestRank = min(allRanks)
    sincePopular = datetime.datetime.today() - popular
    if sincePopular.days * bestRank < 15000:
        name, artist = key
        totalPopularity = sum(100 / (2 ** r) for r in allRanks)
        print repr({'name' : name, 'artist' : artist, 'last_popular' : popular, 'total_popularity' : totalPopularity})
        
