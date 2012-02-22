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
    from libs.rdio                  import Rdio
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
except:
    report()
    raise

class RdioSource(BasicSource):
    """
    """
    def __init__(self):
        BasicSource.__init__(self, 'rdio',
            'rdio',
        )

    @lazyProperty
    def __rdio(self):
        return Rdio(('bzj2pmrs283kepwbgu58aw47','xJSZwBZxFp'))
    
    def resolveSong(self, entity):
        pass        

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich('rdio',self.sourceName,entity):
            subcategory = entity['subcategory']
            if subcategory == 'song':
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
                    timestamps['rdio'] = controller.now
                    try:
                        result = self.__rdio.call('search',{
                            'query':' '.join(query_list),
                            'types':', '.join(type_list),
                        })
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
                                    if artistMatch and albumMatch and trackMatch and typeMatch:
                                        matches.append(entry)
                                except KeyError:
                                    pass
                            if len(matches) == 1:
                                match = matches[0]
                                entity['rdio_id'] = match['key']
                    except Exception:
                        report()
            elif subcategory == 'album':
                pass
            elif subcategory == 'song':
                pass
        return True

