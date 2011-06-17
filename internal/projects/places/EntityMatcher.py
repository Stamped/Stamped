#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import string, sys, Utils

from optparse import OptionParser
from difflib import SequenceMatcher
from GooglePlaces import GooglePlaces

class EntityMatcher(object):
    DEFAULT_TOLERANCE = 0.9
    
    def __init__(self, log=Utils.log):
        self.log = log
        self.googlePlaces = GooglePlaces(log)
        self.initWordBlacklistSets()
    
    def tryMatchEntityWithGooglePlaces(self, entity, tolerance=DEFAULT_TOLERANCE):
        address = entity['address']
        
        numComplexityLevels = 6
        prevName = None
        
        for i in xrange(numComplexityLevels):
            complexity = float(numComplexityLevels - i - 1) / numComplexityLevels
            name = self.getSimplifiedName(entity['name'], complexity)
            
            print "NAME: %s, complexity: %g" % (name, complexity)
            
            if name != prevName:
                prevName = name
                
                match = self.tryMatchNameAddressWithGooglePlaces(name, address, tolerance)
                if match is not None:
                    return match
        
        return None
    
    def tryMatchNameAddressWithGooglePlaces(self, name, address, tolerance=DEFAULT_TOLERANCE):
        params = { 'name' : name }
        results = self.googlePlaces.getSearchResultsByAddress(address, params)
        
        if results is None:
            return None
        
        # perform case-insensitive, fuzzy string matching to determine the 
        # best match in the google places result set for the target entity
        bestRatio  = -1
        bestMatch  = None
        
        for result in results:
            # TODO: alternatively look into using edit distance via:
            #       http://code.google.com/p/pylevenshtein/
            matcher = SequenceMatcher(None, name, result['name'].lower())
            ratio = matcher.ratio()
            
            if ratio > bestRatio:
                bestRatio = ratio
                bestMatch = result
        
        # if no results matched the entity within the acceptable tolerance 
        # level, then disregard the results as irrelevant and return 
        # empty-handed
        if bestRatio <= 1.0 - tolerance:
            return None
        
        # otherwise, we have a match!
        return (bestMatch, bestRatio)
    
    def initWordBlacklistSets(self):
        # remove leading words
        self.wordPrefixBlacklistSet = set()
        self.wordPrefixBlacklistSet.add("the")
        
        # remove words regardless of position
        self.wordBlacklistSet = set()
        self.wordBlacklistSet.add("restaurant")
        self.wordBlacklistSet.add("ristorante")
        
        # remove trailing words
        self.wordSuffixBlacklistSet = set()
        self.wordSuffixBlacklistSet.add("-")
        self.wordSuffixBlacklistSet.add("@")
        self.wordSuffixBlacklistSet.add("...")
        self.wordSuffixBlacklistSet.add("at")
        
        # remove special character sequences
        self.wordSpecialBlacklistSet = set()
        self.wordSpecialBlacklistSet.add("...")
    
    def getSimplifiedName(self, name, complexity):
        complexity = min(max(complexity, 0), 1.0)
        name = name.lower()

        if complexity >= 1.0:
            return name
        
        words = name.split()
        
        while words[0] in self.wordPrefixBlacklistSet:
            words = words[1:]
        
        if complexity < 0.8:
            words = filter(lambda x: not x in self.wordBlacklistSet, words)
        
        finalWords = None
        
        for i in xrange(len(words)):
            if finalWords is not None:
                break
            
            word = words[i]
            
            if word in self.wordSuffixBlacklistSet:
                finalWords = words[0:i]
            else:
                for suffix in self.wordSpecialBlacklistSet:
                    j = word.find(suffix)
                    if j == 0:
                        finalWords = words[0:i]
                        break
                    elif j >= 0:
                        words[i] = word[0:j]
                        finalWords = words[0:i+1]
                        break
        
        finalWords = map(lambda x: x.strip(), finalWords or words)
        
        if complexity <= 0.5:
            numWords = int(complexity * 10)
            numWords = min(len(finalWords), max(numWords, 0))
            finalWords = finalWords[0:numWords]
        
        return string.joinfields(finalWords, ' ').strip()

def parseCommandLine():
    pass

def main():
    pass

if __name__ == '__main__':
    main()

