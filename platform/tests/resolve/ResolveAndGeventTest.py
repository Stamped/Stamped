import Globals

import gevent
from db.mongodb.MongoEntityCollection import MongoEntityCollection

import random

def generate_bigass_query():
    sources = [
        'amazon',
        'spotify',
        'rdio',
        'opentable',
        'tmdb',
        'factual',
        'instagram',
        'singleplatform',
        'foursquare',
        'fandango',
        'googleplaces',
        'itunes',
        'netflix',
        'thetvdb',
    ]
    num_clauses = random.randint(20, 60)
    clauses = []
    for i in range(num_clauses):
        clauses.append({'sources.' + sources[random.randint(0, len(sources)-1)] : str(random.randint(0, 100000000000))})
    query = {'$or': clauses}

queries = []
for i in range(20):
    queries.append(generate_bigass_query())

pool = gevent.pool.Pool(20)

events = []
import datetime

def run_query(idx, query):
    events.append('starting query %d at time %s' % (idx, datetime.datetime.now()))
    results = MongoEntityCollection()._collection.find(query, fields=['sources'])
    events.append('finished query %d at time %s' % (idx, datetime.datetime.now()))
    if len(results) == 42:
        print 'blaaaargh'
        raise Exception('blaaaargh')

for idx, query in enumerate(queries):
    pool.spawn(run_query, idx, query)
pool.join()

print '\n'.join(events)