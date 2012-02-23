#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'Resolver', 'ResolverArtist' ]

import Globals
from logs import report

try:
    from libs.Rdio                  import Rdio
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    import re
    from pprint                     import pprint, pformat
    import sys
    from Entity                     import getSimplifiedTitle
    from gevent.pool                import Pool
    import math
    from abc                        import ABCMeta, abstractmethod, abstractproperty
except:
    report()
    raise

_verbose = False
_very_verbose = False


_general_regex_removals = [
    (r'.*(\(.*\)).*'    , [1]),     # a name ( with parens ) anywhere
    (r'.*(\[.*]).*'     , [1]),     # a name [ with brackets ] anywhere
    (r'.*(\(.*)'        , [1]),     # a name ( bad parathetical
    (r'.*(\[.*)'        , [1]),     # a name [ bad brackets
    (r'.*(\.\.\.).*'    , [1]),     # ellipsis ... anywhere
]

_track_removals = [
    (r'.*(-.* (remix|mix|version|edit|dub)$)'  , [1]),
]

_album_removals = [
    (r'.*((-|,)( the)? remixes.*$)'    , [1]),
    (r'.*(- ep$)'                   , [1]),
    (r'.*( the (\w+ )?remixes$)'     , [1]),
    (r'.*(- remix ep)' , [1]),
    (r'.*(- single$)' , [1]),
]

def _regexRemoval(string, patterns):
    modified = True
    while modified:
        modified = False
        for pattern, groups in patterns:
            while True:
                match = re.match(pattern, string)
                if match is None:
                    break
                else:
                    for group in groups:
                        string2 = string.replace(match.group(group),'')
                        if _very_verbose:
                            print('Replaced %s with %s' % (string, string2))
                        string = string2
                        modified = True
    return string

def _format(string):
    modified = True
    li = [ '\t' , '\n', '\r', '  ' ]
    while modified:
        modified = False
        for ch in li:
            string2 = string.replace(ch,' ')
            if string2 != string:
                modified = True
                string = string2
    return string.strip()

def _simplify(string):
    string = getSimplifiedTitle(string)
    string = _format(string)
    string = _regexRemoval(string, _general_regex_removals)
    return _format(string)

def _trackSimplify(string):
    string = _simplify(string)
    string = _regexRemoval(string, _track_removals)
    return _format(string)

def _albumSimplify(string):
    string = _simplify(string)
    string = _regexRemoval(string, _album_removals)
    return _format(string)

class ResolverArtist(object):
    __metaclass__ = ABCMeta
    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def key(self):
        pass

    @abstractproperty
    def source(self):
        pass

    @abstractproperty
    def albums(self):
        pass

    @abstractproperty
    def tracks(self):
        pass

class _EntityArtist(ResolverArtist):

    def __init__(self, entity):
        ResolverArtist.__init__(self)
        self.__entity = entity

    @lazyProperty
    def name(self):
        return self.__entity['title']

    @lazyProperty
    def key(self):
        return self.__entity['entity_id']

    @property 
    def source(self):
        return "stamped"

    @lazyProperty
    def albums(self):
        return [ album['album_name'] for album in self.__entity['albums'] ]

    @lazyProperty
    def tracks(self):
        return [ song['song_name'] for song in self.__entity['songs'] ]


class Resolver(object):
    """
    """
    def __init__(self):
        pass

    def artistFromEntity(self, entity):
        return _EntityArtist(entity)

    def setSimilarity(self, a, b):
        if a == b:
            return 1.0
        elif len(b) == 0 or len(a) == 0:
            return 0
        else:
            inter = a & b
            value = math.log(2+len(inter))/math.log(2+len(a))
            if inter == a:
                value = float(1 + value) / 2
            return value 

    def albumSimplify(self, album):
        return _albumSimplify(album)

    def trackSimplify(self, track):
        return _trackSimplify(track)

    def nameSimilarity(self, a, b):
        if len(a) < len(b):
            b, a = a, b
        if a == b:
            return 1.0
        else:
            a = _simplify(a)
            b = _simplify(b)
            if a == b:
                return .90

            if len(a) < len(b):
                b, a = a, b
            index = a.find(b)
            if index == 0:
                return len(b)*.90 / max(len(a),1)
            elif index != -1:
                if a[index-1] == ' ':
                    return len(b)*.70 / max(len(a),1)
                else:
                    return len(b)*.40 / max(len(a),1)
        return 0.0

    def __nameWeight(self, a, b):
        la = len(a)
        lb = len(b)
        if la == 0 or lb == 0:
            return 1
        return 2*float(la+lb)/(math.log(la+1)+math.log(lb+1))

    def __setWeight(self, q, m):
        size = len( q | m )
        if size == 0:
            return 1
        weight = float(size)/math.log(size+1)
        if q & m == q:
            weight *= 1.2
        return weight

    def __albumsWeight(self, a, b):
        return self.__setWeight(a, b)

    def __tracksWeight(self, a, b):
        return self.__setWeight(a, b)

    def __resolveArtistBatch(self, query, source, start, count, mins):
        results = []
        entries = source(start, count)

        def checkArtist(query, match, mins):
            if _verbose:
                print("Comparing %s and %s" % (match.name,query.name))
            similarities = {}

            similarities['name'] = self.nameSimilarity(query.name, match.name)
            if similarities['name'] >= mins['name']:

                query_album_set = set( [ self.albumSimplify(album) for album in query.albums ] )
                match_album_set = set( [ self.albumSimplify(album) for album in match.albums ] )

                if _verbose:
                    diff = sorted(query_album_set ^ match_album_set)
                    print('%s Album difference for %s and %s (%s %s vs %s %s)' % (
                        len(diff), match.name , query.name, len(match_album_set), match.source, len(query_album_set), query.source
                    ))
                    for album in diff:
                        source = match.source
                        if album in query_album_set:
                            source = query.source
                        print( "%s: %s" % (source, album))

                similarities['albums'] = self.setSimilarity(query_album_set, match_album_set)
                if similarities['albums'] >= mins['albums']:
                    query_track_set = set( [ self.trackSimplify(track) for track in query.tracks ] )
                    match_track_set = set( [ self.trackSimplify(track) for track in match.tracks ] )

                    if _verbose:
                        diff = sorted(query_track_set ^ match_track_set)
                        print('%s Track difference for %s and %s (%s %s vs %s %s)' % (
                            len(diff), match.name , query.name, len(match_track_set), match.source, len(query_track_set), query.source
                        ))
                        for album in diff:
                            source = match.source
                            if album in query_track_set:
                                source = query.source
                            print( "%s: %s" % (source, album))

                    similarities['tracks'] = self.setSimilarity(query_track_set, match_track_set)

                    if similarities['tracks']  > mins['tracks']:
                        name_weight = self.__nameWeight(query.name, match.name)
                        total = similarities['name'] * name_weight

                        albums_weight = self.__albumsWeight(query_album_set, match_album_set)
                        total += albums_weight * similarities['albums']

                        tracks_weight = self.__tracksWeight(query_track_set, match_track_set)
                        total += tracks_weight * similarities['tracks']

                        if _verbose:
                            print( "Weights for %s- name:%s, albums:%s, tracks:%s" % (match.name, name_weight, albums_weight, tracks_weight))
                        weight = name_weight + albums_weight + tracks_weight
                        weights = {}
                        weights['tracks'] = tracks_weight
                        weights['albums'] = albums_weight
                        weights['name'] = name_weight
                        similarities['weights'] = weights
                        similarities['total'] = total / weight
                        if similarities['total'] >= mins['total']:
                            results.append((similarities,match))
        pool = Pool(10)
        for entry in entries:
            pool.spawn(checkArtist, query, entry, mins)
        pool.join()

        return results

    def resolveArtist(self, query, source):
        mins = {
            'total' : 0,
            'name' : 0,
            'albums' : 0,
            'tracks' : 0,
        }
        groups = [1, 4, 10, 25]
        results = []
        index = 0
        for i in groups:
            batch = self.__resolveArtistBatch(query, source, index, i , mins)
            for result in batch:
                result[0]['resolved'] = False
            index += i
            results.extend( batch )

            def finalSort(pair):
                return -pair[0]['total']
            results = sorted(results , key=finalSort)
            if len(results) > 0 and results[0][0]['total'] > .7:
                results[0][0]['resolved'] = True
                break

        return results


