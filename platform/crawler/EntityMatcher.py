#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import string

from optparse import OptionParser
from difflib import SequenceMatcher
from libs.GooglePlaces import GooglePlaces

class EntityMatcher(object):
    """
        Utility class which attempts to determine whether or not a given entity 
    matches other entities.
    """
    
    DEFAULT_TOLERANCE = 0.9
    
    def __init__(self):
        self.initWordBlacklistSets()
    
    def genEntityDetail(self, entity):
        numComplexityLevels = 4
        
        prevTitle = None
        origTitle = entity['title'].lower()
        
        for i in xrange(numComplexityLevels):
            complexity = float(numComplexityLevels - i - 1) / (max(1, numComplexityLevels - 1))
            title = self.getCanonicalizedTitle(origTitle, complexity, False)
            if len(title) < 1:
                break
            
            yield title
    
    def genMatchingEntities(self, entity, entities, tolerance=DEFAULT_TOLERANCE):
        base_detail  = list(self.genEntityDetail(entity))
        lbase_detail = len(base_detail)
        
        for candidate in entities:
            candidate_detail = self.genEntityDetail(candidate)
            level = 0
            match = False
            
            for candidate_title in candidate_detail:
                if lbase_detail <= level:
                    break
                
                base_title = base_detail[level]
                level += 1
                
                ratio = SequenceMatcher(None, base_title, candidate_title).ratio()
                #print "%f) %s vs %s" % (ratio, base_title, candidate_title)
                
                if ratio <= 0:
                    break
                if ratio >= 0.95:
                    match = True
                    break
            
            if match:
                yield candidate
    
    def initWordBlacklistSets(self):
        # remove leading words
        self.wordPrefixBlacklistSet = set()
        self.wordPrefixBlacklistSet.add("the")
        
        # remove words regardless of position
        self.wordBlacklistSet = set()
        self.wordBlacklistSet.add("restaurant")
        self.wordBlacklistSet.add("ristorante")
        self.wordBlacklistSet.add("steakhouse")
        
        # remove characters delimiting the start of a detail suffix string
        # e.g., "Mike's Bar - Soho" would remove " - Soho" as extraneous detail
        self.wordDetailDelimiterBlacklistSet = set()
        self.wordDetailDelimiterBlacklistSet.add("-")
        self.wordDetailDelimiterBlacklistSet.add("@")
        self.wordDetailDelimiterBlacklistSet.add("...")
        
        # remove trailing words
        self.wordSuffixBlacklistSet = set()
        self.wordSuffixBlacklistSet.add("&")
        self.wordSuffixBlacklistSet.add("at")
        self.wordSuffixBlacklistSet.add("the")
        
        # remove special character sequences
        self.wordSpecialBlacklistSet = set()
        self.wordSpecialBlacklistSet.add("...")
    
    def getCanonicalizedTitle(self, title, complexity, crippleTitle):
        complexity = min(max(complexity, 0), 1.0)
        title = title.lower()
        
        # return the lowercase title if no simplification is to occur
        if complexity >= 1.0:
            return title
        
        # initialize complexity-dependent detail delimiters
        wordDetailDelimiterBlacklistSet  = set()
        wordDetailDelimiterBlacklistSet |= self.wordDetailDelimiterBlacklistSet
        if complexity < 0.8:
            wordDetailDelimiterBlacklistSet.add("at")
            wordDetailDelimiterBlacklistSet.add("on")
        
        # filter and process individual words
        words = title.split()
        
        prevWords = None
        while (prevWords is None or len(words) != len(prevWords)) and len(words) > 0:
            prevWords = words
            
            # remove blacklisted prefix words
            while len(words) > 0 and words[0] in self.wordPrefixBlacklistSet:
                words = words[1:]
            
            if complexity < 0.9:
                # remove blacklisted words that are agnostic to where they appear
                # in the query string
                words = filter(lambda x: not x in self.wordBlacklistSet, words)
            
            truncatedWords = None
            
            # loop through each word, filtering it if it's blacklisted w.r.t. the 
            # context it appears in
            for i in xrange(len(words)):
                if truncatedWords is not None:
                    break
                
                word = words[i]
                
                if word in wordDetailDelimiterBlacklistSet:
                    # remove all words after and including this one which are 
                    # (hopefully) extraneous
                    truncatedWords = words[0:i]
                else:
                    # search within word for special blacklisted sequences which 
                    # hint at the start of detail (e.g., "Mike's bar...great food!"
                    # we'd remove "...great food!")
                    for sequence in self.wordSpecialBlacklistSet:
                        j = word.find(sequence)
                        if j == 0:
                            truncatedWords = words[0:i]
                            break
                        elif j >= 0:
                            words[i] = word[0:j]
                            truncatedWords = words[0:i+1]
                            break
            
            # strip all remaining words of extra whitespace
            words = map(lambda x: x.strip(), truncatedWords or words)
            if len(words) == 0:
                break
            
            # remove all blacklisted suffix words
            while words[-1] in self.wordSuffixBlacklistSet:
                words = words[0:max(len(words) - 1, 0)]
                
                if len(words) == 0:
                    break
            
            # depending on the desired complexity level, break and refrain from 
            # looping on the simplification process multiple times
            limit = 0.85
            if complexity > limit:
                break
            
            if crippleTitle:
                # note: only cripple the title once during multiple iterations
                # (by truncating either the number of words or the number of 
                # characters within a single word)
                crippleTitle = False
                
                # depending on complexity, cap the number of remaining words such that 
                # more simplified queries will use less words, with a base case of 
                # complexity being less than 0.1 resulting in no words and thus, an 
                # empty search string
                percent = (complexity + 1.0 - limit)
                count   = len(words)
                
                # if we only have one word left, truncate the number of 
                # characters depending on the desired complexity
                if count == 1 and complexity > 0:
                    count    = len(words[0])
                    numChars = min(count, max(int(percent * count), 0))
                    words[0] = words[0][0:numChars]
                else:
                    # else truncate the number of words depending on the 
                    # desired complexity
                    numWords = min(count, max(int(percent * count), 0))
                    words    = words[0:numWords]
        
        # join the remaining words back together and strip any possible 
        # whitespace that might've snuck in to form the resulting title
        return string.joinfields(words, ' ').strip()

