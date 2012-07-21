#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re
from numpy import array

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
        row = tuple([-1] * ncols)
        differences_array = array([row] * nrows, dtype=float)
        differences_array[0,0] = 0
        curr_col = 1
        curr_row = 0
        difference = 0

        starts1, ends1 = cls.get_token_starts_and_ends(s1)
        starts2, ends2 = cls.get_token_starts_and_ends(s2)
        for curr_row in range(nrows):

            for curr_col in range(ncols):
                if curr_col == 0 and curr_row == 0:
                    continue

                least_penalty = 10000000

                # If we're at the start of a new word, consider cutting it out.
                if curr_col in starts1[1:] and curr_row in starts2:
                    curr_start_idx = starts1.index(curr_col)
                    skip_begin = starts1[curr_start_idx-1]
                    skip_end = curr_col
                    cost = cls.get_skip_word_cost(s1, skip_begin, skip_end)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, skip_begin])
                if curr_row in starts2[1:] and curr_col in starts1:
                    curr_start_idx = starts2.index(curr_row)
                    skip_begin = starts2[curr_start_idx-1]
                    skip_end = curr_row
                    cost = cls.get_skip_word_cost(s2, skip_begin, skip_end)
                    least_penalty = min(least_penalty, cost + differences_array[skip_begin, curr_col])

                # TODO: I think I should do something similar with ends.

                # Handle cutting off the entire string1 or string2 to date as an unwanted prefix.
                if curr_col in starts1 and curr_col != 0 and curr_row == 0:
                    cost = cls.get_skip_prefix_cost(s1, curr_col)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, 0])
                if curr_row in starts2 and curr_row != 0 and curr_col == 0:
                    cost = cls.get_skip_prefix_cost(s2, curr_row)
                    least_penalty = min(least_penalty, cost + differences_array[0, curr_col])

                # Handle the case where we want to just skip a character in one string or the other. Expensive.
                if curr_col > 0:
                    cost = cls.get_skip_cost(s1, curr_col-1, s2, curr_row)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row, curr_col-1])
                if curr_row > 0:
                    cost = cls.get_skip_cost(s2, curr_row-1, s1, curr_col)
                    least_penalty = min(least_penalty, cost + differences_array[curr_row-1, curr_col])

                # Handle the case where we want to just progress a character in each string.
                if curr_col > 0 and curr_row > 0:
                    char1, char2 = s1[curr_col-1], s2[curr_row-1]
                    cost = cls.get_cmp_cost(s1, curr_col-1, s2, curr_row-1)
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
    def get_ratio(cls, s1, s2):
        return cls.get_difference(s1, s2) / ((len(s1) + len(s2)) * 0.5)

if __name__ == '__main__':
    import sys
    print StringComparator.get_ratio(sys.argv[1], sys.argv[2])