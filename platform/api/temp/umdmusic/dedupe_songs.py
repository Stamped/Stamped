
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

for key, ranks in ranks.iteritems():
    bestRank = min(ranks)
    if bestRank <= 1:
        name, artist = key
        popular = popularDate[key]
        totalPopularity = sum(100 / (2 ** r) for r in ranks)
        print repr({'name' : name, 'artist' : artist, 'last_popular' : popular, 'total_popularity' : totalPopularity})
        
