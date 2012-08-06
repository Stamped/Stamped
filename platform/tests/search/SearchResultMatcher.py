#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs, re
from resolve.Resolver import simplify

# Title matchers for use with SearchResultMatcher.

class StringMatcher(object):
    def matches(self, string):
        raise NotImplementedError()


class In(StringMatcher):
    def __init__(self, *strings):
        self.__strings = set([string.lower() for string in strings])

    def matches(self, string):
        return string.lower() in self.__strings

    def __repr__(self):
        return 'In(%s)' % repr(self.__strings)


class Contains(StringMatcher):
    def __init__(self, substring):
        self.__substring = substring.lower()

    def matches(self, string):
        # TODO: Check for word boundaries around substring.
        return self.__substring in string.lower()

    def __repr__(self):
        return 'Contains(%s)' % repr(self.__substring)


class StartsWith(StringMatcher):
    def __init__(self, prefix):
        self.__prefix = prefix.lower()

    def matches(self, string):
        # TODO: Check for word boundaries around prefix.
        return string.lower().startswith(self.__prefix)

    def __repr__(self):
        return 'StartsWith(%s)' % repr(self.__prefix)


class Equals(StringMatcher):
    def __init__(self, string):
        self.__string = string.lower()

    def matches(self, string):
        return self.__string == string.lower()

    def __repr__(self):
        return 'Equals(%s)' % repr(self.__string)


class LooselyEquals(StringMatcher):
    def __init__(self, string):
        self.__string = string.lower()

    def matches(self, string):
        return simplify(self.__string) == simplify(string.lower())

    def __repr__(self):
        return 'LooselyEquals(%s)' % repr(self.__string)


class MatchesRegex(StringMatcher):
    def __init__(self, pattern):
        self.__pattern = pattern
        self.__regex = re.compile(pattern, re.IGNORECASE)

    def matches(self, string):
        return bool(self.__regex.match(string))

    def __repr__(self):
        return 'MatchesRegex(%s)' % repr(self.__pattern)


class SearchResultMatcher(object):
    def __init__(self, kind, _type,
                 title = None,
                 expected_sources = None,
                 consistent = True,
                 unique = True):
        if not isinstance(title, StringMatcher):
            raise Exception('title param to SearchResultMatcher must be a StringMatcher!')
        self.__kind = kind
        self.__type = _type
        self._title = title
        self.__expected_sources = expected_sources
        self.__all_components_must_match = consistent
        self.__must_be_unique = unique

    @property
    def expected_sources(self):
        return self.__expected_sources

    @property
    def all_components_must_match(self):
        return self.__all_components_must_match

    @property
    def must_be_unique(self):
        return self.__must_be_unique

    def matches(self, proxy):
        if self.__type and self.__type not in proxy.types:
            return False
        if self.__kind and self.__kind != proxy.kind:
            return False
        return self._title.matches(proxy.name)

    @property
    def all_sources(self):
        raise NotImplementedError()

    def repr_proxy(self, proxy):
        """
        Sometimes we want to produce an error message when a matcher fails to match a proxy, and we want the error
        message to include a representation of the relevant sections of the proxy. So each SearchResultMatcher type is
        responsible for being able to represent proxies in a concise way that contains enough information to determine
        why there wasn't a match.
        """
        return '(title=%s, key=%s:%s)' % (repr(proxy.name), proxy.source, proxy.key)

    def __repr__(self):
        return '%s(title=%s)' % (self.__class__.__name__, repr(self._title))


class ArtistResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        super(ArtistResultMatcher, self).__init__(None, 'artist', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes', 'rdio', 'spotify'])


class AlbumResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        self.__artist = kwargs.pop('artist', None)
        if self.__artist is not None and not isinstance(self.__artist, StringMatcher):
            raise Exception('artist param to AlbumSearchResultMatcher must be a StringMatcher!')
        super(AlbumResultMatcher, self).__init__(None, 'album', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes', 'rdio', 'spotify', 'amazon'])

    def matches(self, proxy):
        if not super(AlbumResultMatcher, self).matches(proxy):
            return False
        if self.__artist is None:
            return True
        return proxy.artists and len(proxy.artists) == 1 and self.__artist.matches(proxy.artists[0]['name'])

    def repr_proxy(self, proxy):
        return '(title=%s, artists=[%s], key=%s:%s)' % (
            repr(proxy.name),
            ', '.join([repr(artist['name']) for artist in proxy.artists]),
            proxy.source, proxy.key
        )

    def __repr__(self):
        return '%s(title=%s, artist=%s)' % (self.__class__.__name__, repr(self._title), repr(self.__artist))


class TrackResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        self.__artist = kwargs.pop('artist', None)
        if self.__artist is not None and not isinstance(self.__artist, StringMatcher):
            raise Exception('artist param to TrackSearchResultMatcher must be a StringMatcher!')
        super(TrackResultMatcher, self).__init__(None, 'track', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes', 'rdio', 'spotify', 'amazon'])

    def matches(self, proxy):
        if not super(TrackResultMatcher, self).matches(proxy):
            return False
        if self.__artist is None:
            return True
        return proxy.artists and len(proxy.artists) == 1 and self.__artist.matches(proxy.artists[0]['name'])

    def repr_proxy(self, proxy):
        return '(title=%s, artists=[%s], key=%s:%s)' % (
            repr(proxy.name),
            ', '.join([repr(artist['name']) for artist in proxy.artists]),
            proxy.source, proxy.key
        )

    def __repr__(self):
        return '%s(title=%s, artist=%s)' % (self.__class__.__name__, repr(self._title), repr(self.__artist))


class MovieResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        super(MovieResultMatcher, self).__init__(None, 'movie', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes', 'tmdb', 'netflix'])


class TvResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        super(TvResultMatcher, self).__init__(None, 'tv', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes', 'thetvdb', 'netflix'])


class BookResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        self.__author = kwargs.pop('author', None)
        if self.__author is not None and not isinstance(self.__author, StringMatcher):
            raise Exception('author param to AlbumSearchResultMatcher must be a StringMatcher!')
        super(BookResultMatcher, self).__init__(None, 'book', **kwargs)

    def matches(self, proxy):
        if not super(BookResultMatcher, self).matches(proxy):
            return False
        if self.__author is None:
            return True
        return proxy.authors and len(proxy.authors) == 1 and self.__author.matches(proxy.authors[0]['name'])

    @property
    def all_sources(self):
        return set(['itunes', 'amazon'])

    def repr_proxy(self, proxy):
        return '(title=%s, authors=[%s], key=%s:%s)' % (
            repr(proxy.name),
            ', '.join([repr(author['name']) for author in proxy.authors]),
            proxy.source, proxy.key
        )

    def __repr__(self):
        return '%s(title=%s, author=%s)' % (self.__class__.__name__, repr(self._title), repr(self.__author))


class PlaceResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        super(PlaceResultMatcher, self).__init__('place', None, **kwargs)

    @property
    def all_sources(self):
        return set(['googleplaces', 'factual'])


class AppResultMatcher(SearchResultMatcher):
    def __init__(self, **kwargs):
        super(AppResultMatcher, self).__init__(None, 'app', **kwargs)

    @property
    def all_sources(self):
        return set(['itunes'])
