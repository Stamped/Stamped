#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Globals
from search.EntitySearch import EntitySearch

FILM_QUERIES = [
    '1984',  # This one is a DISASTER.
    '90210',
    'LOST',
    'Le ragazze di Piazza di Spagna',
    'a-team',
    'ateam',
    'a team',
    'american idol',
    'animaniacs',
    'arrested development',
    'athf',
    'aqua teen hunger force',
    'avengers',
    'big bang theory',
    'breaking bad',
    'casablanca',
    'coupling',
    'dark angel',
    'deadwood',
    'dexter',
    'die hard',
    'drive (2011)',
    'drive',
    'family guy',
    'firefly',
    'footballer\'s wives',
    'friends',
    'futurama movie',
    'futurama',
    'game of thrones',
    'girl with the dragon tattoo',
    'godfather',
    'harry potter',
    'hotel babylon',
    'how i met your mother',
    'hunger games',
    'inception',
    'incredibles',
    'it\'s always sunny in philadelphia',
    'jeeves and wooster',
    'la belle et la bête',
    'lord of the rings',
    'misfits',
    'mission impossible ghost protocol',
    'new girl',
    'raiders of the lost ark',
    'requiem',
    'requiem for a dream',
    'rome',
    'saturday night live',
    'south park',
    'superman',
    'spongebob squarepants',
    'spongebob',
    'star wars',
    'star wars tng',
    'star wars deep space nine',
    'star trek',
    'star trek wrath of khan',
    'taken',
    'teenage mutant ninja turtles II',
    'teenage mutant ninja turtles III',
    'teenage mutant ninja turtles',
    'the a-team',
    'the avengers',
    'the fifth element',
    'the godfather',
    'the hunger games',
    'the simpsons',
    'the sopranos',
    'the walking dead',
    'tomorrow never dies',
    'trailer park boys',
    'true grit',
    'two towers',
    'up all night',

    # Tests for title + corroborating detail
    'true grit john wayne',
    'true grit 2010',
    'true grit jeff bridges',
    'true grit coens brothers',
    'superman reeves',
    'superman brandon routh',
    'superman kirk alyn',
    'superman ii',
    'superman iii',
    'superman kevin spacey',
]

def summarize_proxy(proxy):
    return proxy.name, proxy.release_date

def summarize_cluster(cluster):
    return [summarize_proxy(result.resolverObject) for result in cluster.results]

if __name__ == '__main__':
    searcher = EntitySearch()
    samples = []
    for query in FILM_QUERIES:
        entitiesAndClusters = searcher.searchEntitiesAndClusters('film', query)
        samples.append([summarize_cluster(cluster) for _, cluster in entitiesAndClusters])

    print 
    for s in samples:
        print s

