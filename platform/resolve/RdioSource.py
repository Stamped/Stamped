#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'RdioSource' ]

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
except:
    report()
    raise

_verbose = False
_suffix_regexes = [
    re.compile('^(.*) \[[^\]]+\] *$'), 
    re.compile('^(.*) \([^)]+\) *$'), 
    re.compile('^(.*) \([^)]+\) *by +[A-Za-z. -]+$'), 
]

def _simplify(string):
    string = getSimplifiedTitle(string)
    for regex in _suffix_regexes:
        match = regex.match(string)
        
        if match is not None:
            string = match.groups()[0]
    return string.strip()

class RdioSource(BasicSource):
    """
    """
    def __init__(self):
        BasicSource.__init__(self, 'rdio',
            'rdio',
        )

    @lazyProperty
    def __rdio(self):
        return Rdio()

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich('rdio',self.sourceName,entity):
            timestamps['rdio'] = controller.now
            subcategory = entity['subcategory']
            if subcategory == 'song':
                entity['rdio_id'] = self.resolveSong(entity)
            elif subcategory == 'album':
                entity['rdio_id'] = self.resolveAlbum(entity)
            elif subcategory == 'artist':
                results = self.resolveArtist(entity)
                if len(results) != 0:
                    best = results[0]
                    if best['resolved']:
                        entity['rdio_id'] = best['key']
        return True
    
    def resolveSong(self, entity):
        query_dict = {
            'Artist': entity['artist_display_name'],
            'Album': entity['album_name'],
            'Track': entity['title'],
        }
        query_list = []
        type_list = []
        failed = False
        for k,v in query_dict.items():
            if v is not None:
                query_list.append(v)
                type_list.append(k)
            else:
                failed = True
        if not failed:
            try:
                result = self.__rdio.method('search',
                    query=' '.join(query_list),
                    types=', '.join(type_list),
                )
                if result['status'] == 'ok':
                    entries = result['result']['results']
                    length = min(10,len(entries))
                    matches = []
                    for entry in entries[:length]:
                        try:
                            artistMatch = entry['artist'] == query_dict['Artist']
                            albumMatch =  entry['album'] == query_dict['Album']
                            trackMatch = entry['name'] == query_dict['Track']
                            typeMatch = entry['type'] == 't'
                            lengthMatch = True
                            if 'track_length' in entity:
                                track_length = int(entity['track_length'])
                                lengthMatch = abs(int(entry['duration']) - track_length) < 30
                            if artistMatch and albumMatch and trackMatch and typeMatch and lengthMatch:
                                matches.append(entry)
                        except KeyError:
                            pass
                    if len(matches) == 1:
                        match = matches[0]
                        return match['key']
            except Exception:
                report()
        return None
    
    def resolveAlbum(self, entity):
        query_dict = {
            'Artist': entity['artist_display_name'],
            'Album': entity['title'],
        }
        query_list = []
        type_list = []
        failed = False
        for k,v in query_dict.items():
            if v is not None:
                query_list.append(v)
                type_list.append(k)
            else:
                failed = True
        if not failed:
            try:
                result = self.__rdio.method('search',
                    query=' '.join(query_list),
                    types=', '.join(type_list),
                )
                if result['status'] == 'ok':
                    entries = result['result']['results']
                    length = min(10,len(entries))
                    matches = []
                    for entry in entries[:length]:
                        try:
                            artistMatch = entry['artist'] == query_dict['Artist']
                            albumMatch =  entry['name'] == query_dict['Album']
                            typeMatch = entry['type'] == 'a'
                            if artistMatch and albumMatch and typeMatch:
                                matches.append(entry)
                        except KeyError:
                            pass
                    good_matches = []
                    for match in matches:
                        try:
                            track_list = ','.join(match['trackKeys'])
                            songs = self.__rdio.method('get',keys=track_list)['result']
                            song_set = set()
                            failed = False
                            for k,song in songs.items():
                                song_set.add(str(song['name']))
                            for song_name in entity['tracks']:
                                if str(song_name) not in song_set:
                                    failed = True
                                    break
                            if not failed:
                                good_matches.append(match)
                        except KeyError:
                            pass
                    if len(good_matches) > 1:
                        best_match = None
                        best_diff = None
                        for match in good_matches:
                            diff = abs( len(entity['tracks']) - match['length'] )
                            if best_match == None or diff < best_diff:
                                best_match = match
                                best_diff = diff
                        if best_match != None:
                            return best_match['key']
                    
            except Exception:
                report()
        return None

    def resolveArtist(self, entity, minSimilarity=0, nameMin=.4, albumMin=.25, trackMin=.25):
        results = []
        try:
            response = self.__rdio.method('search',
                query=entity['title'],
                types='Artist',
                extras='albumCount',
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                matches = []
                entity_album_set = set( [ _simplify(album_entity['album_name']) for album_entity in entity['albums'] ] )
                entity_track_set = set( [ _simplify(song_entity['song_name']) for song_entity in entity['songs'] ] )
                for entry in entries:
                    try:
                        if entry['type'] == 'r':
                            artistSimilarity = self.similarity(entry['name'], entity['title'])
                            if artistSimilarity >= nameMin:
                                entry['nameSimilarity'] = artistSimilarity
                                results.append(entry)
                    except KeyError:
                        pass
                def nameSimilarityKey(entry):
                    return -entry['nameSimilarity']
                results = sorted(results, key=nameSimilarityKey)

                if len( entity_album_set ) > 0:
                    it = results
                    results = []
                    for match in it:
                        try:
                            albums = self.__rdio.method('getAlbumsForArtist',artist=match['key'],count=100)['result']
                            album_set = set()
                            for album in albums:
                                album_set.add(_simplify(album['name']))
                            album_intersection = album_set & entity_album_set
                            if len(album_intersection) < 10:
                                album_similarity = min(len(album_intersection)*2.0 / len(entity_album_set), 1.0)
                            else:
                                #if there are 10 common albums and the names are close, it's a match
                                album_similarity = 1.00

                            if album_similarity >= albumMin:
                                match['albumSimilarity'] = album_similarity
                                results.append(match)
                        except KeyError:
                            pass

                def albumSimilarityKey(entry):
                    return -(entry['albumSimilarity'] * entry['nameSimilarity'])
                results = sorted(results, key=albumSimilarityKey)

                if len( entity_track_set ) > 0:
                    it = results
                    results = []
                    for match in it:
                        try:
                            tracks = self.__rdio.method('getTracksForArtist',artist=match['key'],count=300)['result']
                            track_set = set()
                            for track in tracks:
                                track_set.add(_simplify(track['name']))
                            track_intersection = track_set & entity_track_set
                            if len(track_intersection) < 20:
                                track_similarity = min( len(track_intersection)*2.0 / len(entity_track_set) , 1.0)
                            else:
                                #if there are 40 common tracks and the names and albums are close, it's a match
                                track_similarity = 1.00
                            if track_similarity > trackMin:
                                match['trackSimilarity'] = track_similarity
                                results.append(match)
                        except KeyError:
                            pass

                it = results
                results = []

                tags = ['trackSimilarity','nameSimilarity','albumSimilarity']
                for match in it:
                    try:
                        stats = {}
                        for tag in tags:
                            if tag in match:
                                stats[tag] = match[tag]
                        total = 0
                        for k,v in stats.items():
                            total += v
                        total = total / len(stats)
                        if total >= minSimilarity:
                            match['similarity'] = total
                            match['resolved'] = False
                            results.append(match)
                    except KeyError:
                        pass

                def finalSort(match):
                    return -match['similarity']

                results = sorted(results, key=finalSort)
                if len(results) == 1:
                    result = results[0]
                    if result['similarity'] > .90:
                        result['resolved'] = True
                elif len(results) > 1:
                    result1 = results[0]
                    result2 = results[1]
                    if result1['similarity'] > .90 and result1['similarity'] - result2['similarity'] > .3:
                        result1['resolved'] = True

                return results

        except Exception:
            report()
        return None

    #TODO improve
    def mangle(self, string):
        return string

    #TODO improve
    def similarity(self, a, b):
        if len(a) < len(b):
            return self.similar(b, a)
        elif a == b:
            return 1.0
        else:
            la = _simplify(a)
            lb = _simplify(b)
            if la == lb:
                return .90
            elif la.startswith(lb):
                return len(lb)*.90 / len(la)
            else:
                ma = self.mangle(la)
                mb = self.mangle(lb)
                if ma.startswith(mb) and len(ma) > 0 and len(mb) > 0:
                    return len(mb)*.5 /len(ma)
        return 0.0

def demo(title='Katy Perry',subcategory=None):
    rdio = RdioSource()
    from MongoStampedAPI import MongoStampedAPI
    api =MongoStampedAPI()
    db = api._entityDB
    query = {'title':title}
    if subcategory is not None:
        query['subcategory'] = subcategory
    cursor = db._collection.find(query)
    if cursor.count() == 0:
        print("Could not find a matching entity")
        return
    result = cursor[0]
    entity = db._convertFromMongo(result)
    rdio_id = None
    if entity['subcategory'] == 'artist':
        rdio_id = rdio.resolveArtist(entity,0,0,0,0)
    elif entity['subcategory'] == 'album':
        rdio_id = rdio.resolveAlbum(entity)
    elif entity['subcategory'] == 'song':
        rdio_id = rdio.resolveSong(entity)
    print("Resolved %s to" % (entity['title']))
    pprint(rdio_id)

if __name__ == '__main__':
    _verbose = True
    if len(sys.argv) == 1:
        demo()
    elif len(sys.argv) == 2:
        demo(sys.argv[1])
    elif len(sys.argv) == 3:
        demo(sys.argv[1], sys.argv[2])
    else:
        print('bad usage')
