#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import collections, os, math, re
from libs.LRUCache import lru_cache

# TODO: Handle pluralization and possessives properly.

class StringComparator(object):
    PUNCTUATION_AND_SPACES = ' .,:;()[]-_"\'?'
    @classmethod
    def get_skip_cost(cls, skip_string, skip_char_idx, other_string, other_string_next_idx):
        """
        Calculates the cost of skipping the char in skip_char_idx in skip_string while the other string is at position
        other_string_next_idx. The state of the other string is required because we may have lower costs for skipping,
        for instance, a doubled consonant where the single version exists in both strings, or for skipping things at a
        word boundary.
        """
        if skip_string[skip_char_idx] in cls.PUNCTUATION_AND_SPACES:
            return 0.2
        return 1

    @classmethod
    def get_cmp_cost(cls, s1, s1_idx, s2, s2_idx):
        c1 = s1[s1_idx]
        c2 = s2[s2_idx]
        if c1 == c2:
            return 0
        if c1.lower() == c2.lower():
            return 0.05
        if c1 in cls.PUNCTUATION_AND_SPACES and c2 in cls.PUNCTUATION_AND_SPACES:
            # Punctuation mismatches are just not a big deal.
            return 0.25
        return 2

    TOKEN_RE = re.compile(r'\b\w+(-\w+)?(\'s)?\b')
    @classmethod
    def get_token_starts_and_ends(cls, string):
        starts = []
        ends = []
        for match in cls.TOKEN_RE.finditer(string):
            starts.append(match.start())
            ends.append(match.end())
        return tuple(starts), tuple(ends)

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
        if cls.PREFIX_RE.match(prefix):
            return len(prefix) * 0.4
        return len(prefix) * 0.5

    SUFFIX_RE = re.compile('[^\w]*[-:(\(].*\w+.*')
    @classmethod
    def get_skip_suffix_cost(cls, string, new_end_idx):
        suffix = string[new_end_idx:]
        if cls.SUFFIX_RE.match(suffix):
            return len(suffix) * 0.4
        return len(suffix) * 0.5

    @classmethod
    def get_difference(cls, s1, s2, max_difference=None):
        ncols = len(s1) + 1
        nrows = len(s2) + 1
        differences_array = collections.defaultdict(lambda:-1)
        differences_array[0,0] = 0
        curr_col = 1
        curr_row = 0
        difference = 0

        starts1, ends1 = cls.get_token_starts_and_ends(s1)
        starts2, ends2 = cls.get_token_starts_and_ends(s2)

        get_skip_prefix_cost = cls.get_skip_prefix_cost
        get_skip_word_cost = cls.get_skip_word_cost
        get_skip_cost = cls.get_skip_cost
        get_cmp_cost = cls.get_cmp_cost

        for curr_row in range(nrows):

            for curr_col in range(ncols):
                if curr_col == 0 and curr_row == 0:
                    continue

                least_penalty = 10000000

                # If we're at the start of a new word, consider cutting it out.
                if curr_col in starts1 and curr_col != starts1[0] and curr_row in starts2:
                    curr_start_idx = starts1.index(curr_col)
                    skip_begin = starts1[curr_start_idx-1]
                    skip_end = curr_col
                    cost = get_skip_word_cost(s1, skip_begin, skip_end)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, skip_begin])
                if curr_row in starts2 and curr_row != starts2[0] and curr_col in starts1:
                    curr_start_idx = starts2.index(curr_row)
                    skip_begin = starts2[curr_start_idx-1]
                    skip_end = curr_row
                    cost = get_skip_word_cost(s2, skip_begin, skip_end)
                    least_penalty = min(least_penalty, cost + differences_array[skip_begin, curr_col])

                # TODO: I think I should do something similar with ends.

                # Handle cutting off the entire string1 or string2 to date as an unwanted prefix.
                if curr_row == 0 and curr_col in starts1 and curr_col != 0:
                    cost = get_skip_prefix_cost(s1, curr_col)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, 0])
                if curr_col == 0 and curr_row in starts2 and curr_row != 0:
                    cost = get_skip_prefix_cost(s2, curr_row)
                    least_penalty = min(least_penalty, cost + differences_array[0, curr_col])

                # Handle the case where we want to just skip a character in one string or the other. Expensive.
                if curr_col > 0:
                    cost = get_skip_cost(s1, curr_col-1, s2, curr_row)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, curr_col-1])
                if curr_row > 0:
                    cost = get_skip_cost(s2, curr_row-1, s1, curr_col)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row-1, curr_col])

                # Handle the case where we want to just progress a character in each string.
                if curr_col > 0 and curr_row > 0:
                    char1, char2 = s1[curr_col-1], s2[curr_row-1]
                    cost = get_cmp_cost(s1, curr_col-1, s2, curr_row-1)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row-1, curr_col-1])

                differences_array[curr_row, curr_col] = least_penalty

        least_penalty = differences_array[nrows-1, ncols-1]

        for end in ends1:
            cost = cls.get_skip_suffix_cost(s1, end)
            least_penalty = min(least_penalty, cost + differences_array[nrows-1, end])

        for end in ends2:
            cost = cls.get_skip_suffix_cost(s2, end)
            least_penalty = min(least_penalty, cost + differences_array[end, ncols-1])

        return least_penalty

    @classmethod
    @lru_cache()
    def get_ratio(cls, s1, s2, min_ratio=0.8):
        rough_max_distance = 0.5 * (len(s1) + len(s2))
        if rough_max_distance == 0:
            return 0
        max_difference = rough_max_distance * (1.0 - min_ratio)
        return 1.0 - (float(cls.get_difference(s1, s2, max_difference=max_difference)) / rough_max_distance)



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
    return (sim ** 1.2) * ((sim / target_sim(unc)) ** 1.2) * ((unc / 8) ** 0.2)

SUBTITLE_RE = re.compile('(\w)\s*[:|-]+\s\w+.*$')
COMMA_SUBTITLE_RE = re.compile('(\w)\s*,\s*\w+.*$')
PARENTHETICAL_RE = re.compile('[.,;: -]+[(\[][^\])]+[)\]]\s*$')
TOKENS_RE = re.compile('[a-zA-Z0-9]+')
# TODO get this unified with token lists used in TitleUtils!
WORTHLESS_SUBTITLE_TOKENS = set([
    # film/tv
    'uncut', 'unrated', 'nr', 'pg', 'r', 'edition', 'collection', 'volume', 'vol', 'cut', 'version', 'starring',
    'episodes', 'eps', 'vols', 'volumes', 'film', 'movie',
    # books
    'paperback', 'hardcover', 'print', 'illustrated', 'novel', 'story', 'stories', 'tale', 'tales', 'biography',
    'autobiography', 'history', 'abridged', 'complete', 'book', 'books',
    # music
    'remix', 'mix', 'remixed', 're-mix', 're-mixed', 'featuring', 'feat', 'inst', 'instrumental', 'karaoke'
])
def strip_subtitle(title):
    match = SUBTITLE_RE.search(title)
    if match:
        subtitle_tokens = [token.lower() for token in TOKENS_RE.findall(match.group(0)[1:])]
        print 'TOKENS:', subtitle_tokens
        subtitle_is_worthless = bool(set(subtitle_tokens) & WORTHLESS_SUBTITLE_TOKENS)
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


def titleComparison(title1, title2, simplificationFn):
    score1 = get_odds_from_sim_unc(StringComparator.get_ratio(title1, title2),
        min(complexUncommonness(title1), complexUncommonness(title2)))
    simple_title1 = simplificationFn(title1)
    simple_title2 = simplificationFn(title2)
    score2 = get_odds_from_sim_unc(StringComparator.get_ratio(simple_title1, simple_title2) * 0.98,
        min(complexUncommonness(simple_title1), complexUncommonness(simple_title2)))
    return max(score1, score2)





if __name__ == '__main__':
    import sys
    print StringComparator.get_ratio(sys.argv[1], sys.argv[2])
