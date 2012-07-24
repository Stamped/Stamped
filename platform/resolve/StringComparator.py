#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import collections, os, math, re
import fastcompare
from libs.LRUCache import lru_cache

# TODO: Handle pluralization and possessives properly.

WORTHLESS_SUBTITLE_TOKENS = set([
    # film/tv
    'uncut', 'unrated', 'nr', 'pg', 'r', 'edition', 'collection', 'volume', 'vol', 'cut', 'version', 'starring',
    'episodes', 'eps', 'vols', 'volumes', 'film', 'movie', 'rated',
    # books
    'paperback', 'hardcover', 'print', 'illustrated', 'novel', 'story', 'stories', 'tale', 'tales', 'biography',
    'autobiography', 'history', 'abridged', 'complete', 'book', 'books',
    # music
    'remix', 'mix', 'remixed', 're-mix', 're-mixed', 'featuring', 'feat', 'inst', 'instrumental', 'karaoke', 'vocals',
    'dub', 'edit', 'remix', 'limited'
])

class StringComparator(object):
    TOKEN_RE = re.compile(r'\b\w+(-\w+)?(\'s)?\b')
    @classmethod
    def get_token_starts_and_ends(cls, string):
        starts = []
        ends = []
        for match in cls.TOKEN_RE.finditer(string):
            starts.append(match.start())
            ends.append(match.end())
        return starts, ends

    SKIP_WORD_COSTS = {
        'the': 0.4, 'a': 0.4, 'an': 0.4,
        'of': 0.75, 'and': 0.75
    }
    @classmethod
    def get_skip_word_cost(cls, string, skip_begin, skip_end):
        word = string[skip_begin:skip_end].strip().lower()
        return cls.SKIP_WORD_COSTS.get(word, len(word) * 0.6)

    PREFIX_RE = re.compile('.*\w+.*[-:(\(][^\w]*$')
    @classmethod
    def get_skip_prefix_cost(cls, string, new_start_idx):
        prefix = string[:new_start_idx]
        if prefix.lower().strip() in cls.SKIP_WORD_COSTS:
            return cls.SKIP_WORD_COSTS[prefix.lower().strip()] * 0.8
        tokens = set([group1.lower() for group1, group2 in cls.TOKEN_RE.findall(prefix)])
        worthless_indicator_tokens = tokens & WORTHLESS_SUBTITLE_TOKENS
        if cls.PREFIX_RE.match(prefix):
            return len(prefix) * 0.2 * (0.6 ** len(worthless_indicator_tokens))

        return len(prefix) * 0.5 * (0.85 ** len(worthless_indicator_tokens))

    SUFFIX_RE = re.compile('[^\w]*[-:(\(].*\w+.*')
    @classmethod
    def get_skip_suffix_cost(cls, string, new_end_idx):
        suffix = string[new_end_idx:]
        tokens = set([group1.lower() for group1, group2 in cls.TOKEN_RE.findall(suffix)])
        worthless_indicator_tokens = tokens & WORTHLESS_SUBTITLE_TOKENS
        if cls.SUFFIX_RE.match(suffix):
            return len(suffix) * 0.2 * (0.6 ** len(worthless_indicator_tokens))
        return len(suffix) * 0.5 * (0.85 ** len(worthless_indicator_tokens))

    @classmethod
    def get_difference(cls, s1, s2, max_difference=None):
        if isinstance(s1, unicode):
            s1 = s1.encode('utf-8')
        if isinstance(s2, unicode):
            s2 = s2.encode('utf-8')
        starts1, ends1 = cls.get_token_starts_and_ends(s1)
        starts2, ends2 = cls.get_token_starts_and_ends(s2)

        result = fastcompare.get_difference(
                s1, s2, starts1, ends1, starts2, ends2, cls.get_skip_prefix_cost,
                cls.get_skip_suffix_cost, cls.get_skip_word_cost)
        return result

    @classmethod
    @lru_cache()
    def get_ratio(cls, s1, s2, min_ratio=0.8):
        rough_max_distance = 0.5 * (len(s1) + len(s2))
        if rough_max_distance == 0:
            return 0
        max_difference = rough_max_distance * (1.0 - min_ratio)
        return 1.0 - (float(cls.get_difference(s1, s2, max_difference=max_difference)) / rough_max_distance)


class ArtistTitleComparator(StringComparator):
    TWO_ARTISTS_RE = re.compile('[^\w]*(and |with |\&|featuring |feat\.? ).*\w+.*')
    MORE_ARTISTS_RE = re.compile('[^\w]*,.*[^\w]+(and|&).*\w+.*')
    @classmethod
    def get_skip_suffix_cost(cls, string, new_end_idx):
        suffix = string[new_end_idx:]
        if cls.TWO_ARTISTS_RE.match(suffix) or cls.MORE_ARTISTS_RE.match(suffix):
            return len(suffix) * 0.05
        return len(suffix) * 0.5



# A bunch of shit that needs a home, followed by a main() for testing StringComparator.get_ratio().

WHITESPACE_RE = re.compile('\s+')
SEPARATOR_RE = re.compile('[:-_;]+')
def simplifyLite(title):
    title = WHITESPACE_RE.sub(' ', title)
    title = title.strip()
    title = SEPARATOR_RE.sub('-', title)
    return title.lower()


def loadWordFrequencyTable():
    resolve_dir = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(resolve_dir, 'lexicon.txt')
    f = open(fname)
    lines = f.readlines()
    f.close()
    line_pairs = [tuple(line.strip().split(' ')) for line in lines]
    return dict(line_pairs[1:])

word_frequencies = loadWordFrequencyTable()

def simpleUncommonness(string):
    return len(string)

WORD_RE = re.compile('([a-zA-Z0-9]+(-[a-zA-Z0-9]+)?)(\'s)?')
def complexUncommonness(string):
    uncommonness = 0.0
    words = [word for (word, _, _) in WORD_RE.findall(string)]
    if not words:
        return 0.5 * len(string)
    exponent = len(words) ** -0.3
    for word in words:
        if word.isdigit():
            uncommonness += len(word) ** 1.5
            continue

        if word in word_frequencies:
            word_frequency = 2000000.0 / int(word_frequencies[word])
        elif word.endswith("'s") and word[:len(word)-2] in word_frequencies:
            word_frequency = 4000000.0 / int(word_frequencies[word[:len(word)-2]])
        elif word.isalpha():
            word_frequency = 2000000.0
        else:
            word_frequency = 4000000.0

        word_frequency = 2000000.0 / int(word_frequencies.get(word.lower(), 1))
        word_uncommonness = 0.5*math.log(word_frequency) + 0.5*len(word)
        uncommonness += word_uncommonness
    return uncommonness

MIN_TARGET_SIM = 0.875
def target_sim(unc):
    return MIN_TARGET_SIM + 2 * ((1 - MIN_TARGET_SIM) / (1 + math.exp(unc / 10.0)))

def get_odds_from_sim_unc(sim, unc):
    if sim <= 0:
        return 0
    unc = max(unc, 5.0)
    return (sim ** 1.2) * ((sim / target_sim(unc)) ** 1.2) * ((unc / 8) ** 0.2)

SUBTITLE_RE = re.compile('(\w)\s*[:|-]+\s\w+.*$')
COMMA_SUBTITLE_RE = re.compile('(\w)\s*,\s*\w+.*$')
PARENTHETICAL_RE = re.compile('[.,;: -]+[(\[][^\])]+[)\]]\s*$')
TOKENS_RE = re.compile('[a-zA-Z0-9]+')
# TODO get this unified with token lists used in TitleUtils!
def strip_subtitle(title):
    match = SUBTITLE_RE.search(title)
    if match:
        subtitle_tokens = [token.lower() for token in TOKENS_RE.findall(match.group(0)[1:])]
        print 'TOKENS:', subtitle_tokens
        worthless_tokens_found = len(set(subtitle_tokens) & WORTHLESS_SUBTITLE_TOKENS)
        return SUBTITLE_RE.sub('\\1', title), subtitle_is_worthless

    match = COMMA_SUBTITLE_RE.search(title)
    # Sometimes a comma is used for subtitles, but we want to be a lot more conservative with
    # them. So we will only split it if there is only one comma.
    if match and title.count(',') == 1 and title.find(',') >= 3:
        subtitle_tokens = [token.lower() for token in TOKENS_RE.findall(match.group(0)[1:])]
        subtitle_is_worthless = bool(set(subtitle_tokens) & WORTHLESS_SUBTITLE_TOKENS)
        return SUBTITLE_RE.sub('\\1', title), subtitle_is_worthless

    match = PARENTHETICAL_RE.search(title)
    if match:
        subtitle_tokens = [token.lower() for token in TOKENS_RE.findall(match.group(0))]
        subtitle_is_worthless = bool(set(subtitle_tokens) & WORTHLESS_SUBTITLE_TOKENS)
        return PARENTHETICAL_RE.sub('', title), subtitle_is_worthless


def titleComparison(title1, title2, simplificationFn, comparator=StringComparator):
    def combinedUncommonness(unc1, unc2):
        return (min(unc1, unc2) * min(unc1, unc2) * max(unc1, unc2)) ** (1.0/3)
    score1 = get_odds_from_sim_unc(comparator.get_ratio(title1, title2),
        combinedUncommonness(complexUncommonness(title1), complexUncommonness(title2)))
    simple_title1 = simplificationFn(title1)
    simple_title2 = simplificationFn(title2)
    score2 = get_odds_from_sim_unc(comparator.get_ratio(simple_title1, simple_title2) * 0.98,
        combinedUncommonness(complexUncommonness(simple_title1), complexUncommonness(simple_title2)))
    return max(score1, score2)





if __name__ == '__main__':
    import sys
    print StringComparator.get_ratio(sys.argv[1], sys.argv[2])
