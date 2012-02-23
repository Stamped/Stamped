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
    from gevent.pool                import Pool
    from Resolver                   import Resolver, ResolverArtist
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

class RdioArtist(ResolverArtist):
    def __init__(self, artist, rdio):
        ResolverArtist.__init__(self)
        self.__rdio = rdio
        self.__data = artist

    @lazyProperty
    def name(self):
        return self.__data['name']

    @lazyProperty
    def key(self):
        return self.__data['key']

    @property 
    def source(self):
        return "rdio"

    @lazyProperty
    def albums(self):
        album_list = self.__rdio.method('getAlbumsForArtist',artist=self.__data['key'],count=100)['result']
        return [ entry['name'] for entry in album_list ]

    @lazyProperty
    def tracks(self):
        track_list = self.__rdio.method('getTracksForArtist',artist=self.__data['key'],count=100)['result']
        return [ entry['name'] for entry in track_list ]

    def __repr__(self):
        return pformat( self.__data )

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
        resolver = Resolver()
        def source(start, count):
            response = self.__rdio.method('search',
                query=entity['title'],
                types='Artist',
                extras='albumCount',
                start=start,
                count=count,
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                if _verbose:
                    pprint(entries)
                return [ RdioArtist( entry, self.__rdio ) for entry in entries ]
            else:
                return []

        return resolver.resolveArtist( resolver.artistFromEntity(entity), source)

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

def demo(title='Katy Perry',subcategory='artist',short=False):
    import Resolver
    Resolver._verbose = True
    rdio = RdioSource()
    from MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db = api._entityDB
    query = {'title':title}
    if subcategory is not None:
        query['subcategory'] = subcategory
    cursor = db._collection.find(query)
    if cursor.count() == 0:
        print("Could not find a matching entity for %s" % title)
        return
    result = cursor[0]
    entity = db._convertFromMongo(result)
    rdio_id = None
    if entity['subcategory'] == 'artist':
        if short:
            rdio_id = rdio.resolveArtist(entity)
        else:
            rdio_id = rdio.resolveArtist(entity,0,0,0,0)
    elif entity['subcategory'] == 'album':
        rdio_id = rdio.resolveAlbum(entity)
    elif entity['subcategory'] == 'song':
        rdio_id = rdio.resolveSong(entity)
    print("Resolved %s to" % (entity['title']))
    pprint(rdio_id)

if __name__ == '__main__':
    _verbose = True
    short = False
    if '-s' in sys.argv:
        sys.argv.remove('-s')
        short = True
    if len(sys.argv) == 1:
        demo(short=short)
    elif len(sys.argv) == 2:
        demo(sys.argv[1],short=short)
    elif len(sys.argv) == 3:
        demo(sys.argv[1], sys.argv[2],short=short)
    else:
        print('bad usage')
