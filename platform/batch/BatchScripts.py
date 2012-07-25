#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals

try:
    from optparse   import OptionParser
    from batch.BatchUtil import *
    from pprint import pprint
    from resolve.TitleUtils import *
    import sys
except:
    raise


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

def addRdioUrls(**kwargs):
    """
    Addes sources.rdio_url for entities that only have sources.rdio_id
    """
    rdio = _rdio()
    query = {
        'sources.rdio_id' : {'$exists':1},
        'sources.rdio_url' : {'$exists':0},
    }
    query = kwargs.pop('query', query)
    def handler(entity):
        rdio_id = entity.sources.rdio_id
        rdio_data = rdio.method('get', keys=rdio_id)
        if rdio_data is not None and 'result' in rdio_data and rdio_id in rdio_data['result']:
            rdio_url = rdio_data['result'][rdio_id].pop('url',None)
            if rdio_url is not None:
                entity.sources.rdio_url = 'http://www.rdio.com%s' % rdio_url
                return [entity]
        return []
    processBatch(handler, query=query, **kwargs)

def fixBadPlaylists(**kwargs):
    """
    Adds itunes_preview to tracks.
    """
    query = {
        'tracks': {
            '$elemMatch' : { 
                'sources.itunes_id': {'$exists':1},
                'sources.itunes_preview' : {'$exists':0}
            }
        }
    }
    query = kwargs.pop('query', query)
    itunes = _itunes()
    def handler(entity):
        tracks = entity.tracks
        for track in tracks:
            itunes_id = track.sources.itunes_id
            itunes_preview = track.sources.itunes_preview
            if itunes_id is not None and itunes_preview is None:
                itunes_data = itunes.method('lookup', id=itunes_id)
                if itunes_data is not None and 'results' in itunes_data:
                    result = itunes_data['results']
                    if len(result) > 0:
                        track_data = result[0]
                        if 'previewUrl' in track_data:
                            track.sources.itunes_preview = track_data['previewUrl']
        return [entity]
    processBatch(handler, query=query, **kwargs)

def _titleCleanerForEntity(entity):
    if entity.kind == 'place':
        return cleanPlaceTitle
    elif entity.isType('app'):
        return cleanAppTitle
    elif entity.isType('book'):
        return cleanBookTitle
    elif entity.isType('artist'):
        return cleanArtistTitle
    elif entity.isType('album'):
        return cleanAlbumTitle
    elif entity.isType('track'):
        return cleanTrackTitle
    elif entity.isType('movie'):
        return cleanMovieTitle
    elif entity.isType('tv'):
        return cleanAppTitle
    return lambda x: x

def cleanTitles(**kwargs):
    """
    Cleans titles using vertical specific functions from TitleUtils
    """
    query = {}
    query = kwargs.pop('query', query)
    def handler(entity):
        title = entity.title
        cleaner = _titleCleanerForEntity(entity)
        entity.title = cleaner(title)
        if entity.title != title:
            return [entity]
        else:
            return []
    processBatch(handler, query=query, **kwargs)

_commands = {
    'track_previews': fixBadPlaylists,
    'rdio_urls': addRdioUrls,
    'clean_titles': cleanTitles,
}

_actions = {
    'update' : outputToCollection,
    'enrich' : outputToCollectionAndEnrich,
    'print' : outputToConsole,
}

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "1.0.0"
    parser  = OptionParser(usage=usage, version=version)
        
    parser.add_option("-r", "--randomize", action="store_true", dest="shuffle", 
        default=False, help="Randomize order and slice")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", 
        default=False, help="Use keys and action.")

    parser.add_option("-s", "--sparse", action="store_true", dest="sparse", 
        default=False, help="Only print keys for non-empty results.")

    parser.add_option("-l", "--limit", dest="limit", 
        default=None, type="int", help="Limit number of entities processed")

    parser.add_option("-o", "--offset", dest="offset", 
        default=0, type="int", help="Limit number of entities processed")

    parser.add_option("-t", "--threads", dest="thread_count", 
        default=None, type="int", help="Number of threads to use")

    parser.add_option("-a", "--action", dest="action", 
        default='print', type="string", help="Specify destination - %s" % ', '.join(_actions.keys()) )

    # parser.add_option("-f", "--file", dest="file", 
    #     default=None, type="string", help="Save entities to given file")

    parser.add_option("-k", "--keys", dest="keys", 
        default=None, type="string", help="Sparsely print specific fields")

    parser.add_option("-q", "--query", dest="query", 
        default=None, type="string", help="Override query")

    (options, args) = parser.parse_args()
    
    invalid = False
    for arg in args:
        if arg not in _commands:
            invalid = True

    if len(args) < 1 or invalid or options.action not in _actions or (options.verbose and options.keys is None):
        print "Error: must provide commands from the list of available commands:"
        for command in _commands:
            print "   %s %s" % (command, _commands[command].__doc__)
        
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

if __name__ == '__main__':
    options, args = parseCommandLine()
    for arg in args:
        command = _commands[arg]
        output = _actions[options.action]
        # if options.file is not None:
        #     f = open(options.file, 'w')
        #     output = createOutputToFile(f)
        if options.keys is not None:
            keys = options.keys.split(',')

            sparse_output = createSparseOutputToConsole(keys, sparse=options.sparse)
            if options.verbose:
                old_output = output
                def doubleOutput(entity_id, results):
                    sparse_output(entity_id, results)
                    old_output(entity_id, results)
                output = doubleOutput
            else:
                output = sparse_output
        command(output=output, limit=options.limit, offset=options.offset, shuffle=options.shuffle, thread_count=options.thread_count)


