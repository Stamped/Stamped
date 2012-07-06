#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'URLResolver' ]

import Globals
from logs import report

try:
    from utils                      import lazyProperty
    import logs
    from resolve.Resolver                   import *
    from urllib                     import unquote
    from pprint                     import pprint
    import re
    from resolve.iTunesSource               import iTunesSource
    from libs.Rdio                  import globalRdio
    from resolve.RdioSource                 import RdioSource
    from resolve.TMDBSource                 import TMDBMovie
except:
    report()
    raise


class URLResolver(object):

    @lazyProperty
    def __itunes_source(self):
        return iTunesSource()

    @lazyProperty
    def __rdio(self):
        return globalRdio()

    @lazyProperty
    def __rdio_source(self):
        return RdioSource()

    def resolveRdio(self, path):
        if path[0] == '#':
            path = path[1:]
        components = path.split('/')
        if components[0] == '':
            components = components[1:]
        if components[-1] == '':
            components = components[:-1]
        types = []
        values = []
        while len(components) >= 2:
            key = components[0]
            value = components[1]
            types.append(key.capitalize())
            new_value = unquote(value)
            match = re.match(r'^.*_\d$', new_value)
            value_set = []
            if match is not None:
                values.append(new_value[:-2].replace('_',' '))
            else:
                values.append(new_value.replace('_',' '))
            components = components[2:]
        results = self.__rdio.method('search',query=' '.join(values),types=','.join(types))

        for result in results['result']['results']:
            if result['url'] == path:
                return self.__rdio_source.wrapperFromData(result)
        return None

    def resolveiTunes(self, path):
        """
        Examples:
        http://itunes.apple.com/us/artist/katy-perry/id64387566 (Katy Perry)
        http://itunes.apple.com/us/album/teenage-dream-deluxe-edition/id387712061 (Teenage Dream deluxe)
        http://itunes.apple.com/us/album/firework/id387712061?i=387712108 (Firework)

        """
        wrapper = None
        match = re.match(r'^.*(id|i=)(\d+)$',path)
        if match is not None:
            wrapper = self.__itunes_source.wrapperFromId(match.group(2))
        return wrapper

    def resolveAmazon(self, path):
        """
        Examples:
        """
        info = {'source':'amazon'}
        match = re.match(r'^gp/product/([\w\d]+)/.*$',path)
        if match is not None:
            info['key'] = match.group(1)
        else:
            match = re.match(r'^.*/dp/([\w\d]+)/.*$',path)
            if match is not None:
                info['key'] = match.group(1)
            else:
                path = unquote(path)
                components = path.split('/')
                asin = components[-1].split('?')[0]
                info['key'] = asin
        return info

    def resolveIMDB(self, path):
        """
        http://www.imdb.com/title/tt0499549/
        """
        match = re.match(r'^title/(tt\d+)/.*$',path)
        if match is not None:
            key = match.group(1)
            movie = TMDBMovie(key)
            if movie.valid:
                return movie
        return None
    
    def demo(self, url):
        url = url[url.find('://')+3:]
        domain = url[:url.find('/')]
        path = url[url.find('/')+1:]
        print(url,domain)
        if domain == 'www.rdio.com':
            info = self.resolveRdio(path)
        elif domain == 'itunes.apple.com':
            info = self.resolveiTunes(path)
        elif domain == 'www.amazon.com':
            info = self.resolveAmazon(path)
        elif domain == 'www.imdb.com':
            info = self.resolveIMDB(path)
        else:
            info = None
        print info

if __name__ == '__main__':
    import sys
    URLResolver().demo(sys.argv[1])

