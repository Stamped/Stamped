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
    TYPES = 'restaurant|food|establishment'
    
    def __init__(self, log=Utils.log):
        self.log = log
        self.googlePlaces = GooglePlaces(log)
        self.initWordBlacklistSets()
    
    def tryMatchEntityWithGooglePlaces(self, entity, tolerance=DEFAULT_TOLERANCE):
        address = entity.address
        latLng  = self.googlePlaces.addressToLatLng(address)
        
        if latLng is None:
            return None
        
        numComplexityLevels = 16
        prevName = None
        origName = entity['name'].lower()
        
        # attempt to match the entity with increasing simplifications applied 
        # to the search name, beginning with no simplification and retrying as 
        # necessary until we find a match, eventually falling back to a blank 
        # name search at the most simplified level
        for i in xrange(numComplexityLevels):
            complexity = float(numComplexityLevels - i - 1) / (max(1, numComplexityLevels - 1))
            name = self.getCanonicalizedName(origName, complexity, True)
            nameToMatch = self.getCanonicalizedName(origName, complexity, False)
            
            # don't attempt to find a match if this simplified name is the same 
            # as the previous level's simplified name (e.g., because we know it 
            # will return the same negative results)
            if name != prevName:
                self.log("NAME: %s, complexity: %g" % (name, complexity))
                prevName = name
                
                # attempt to match the current simplified name and latLng 
                match = self.tryMatchNameLatLngWithGooglePlaces(name, 
                    latLng, tolerance, nameToMatch)
                
                if match is not None:
                    return (match[0], ((match[1] + 0.2) * complexity / 1.2))
        
        return None
    
    def tryMatchNameAddressWithGooglePlaces(self, 
                                            name, 
                                            address, 
                                            tolerance=DEFAULT_TOLERANCE, 
                                            nameToMatch=None):
        params  = self._getParams(name, { 'types' : self.TYPES })
        results = self.googlePlaces.getSearchResultsByAddress(address, params)
        
        if results is None:
            # occasionally a google place search will leave out valid results 
            # if the optional 'types' parameter is set, even though those 
            # results conform to the given types... to get around this bug, 
            # if a more specific query containing the desired 'types' fails 
            # to return any results, we try once more without the 'types'.
            params  = self._getParams(name)
            results = self.googlePlaces.getSearchResultsByLatLng(latLng, params)
            
            if results is None:
                return None
        
        return self.tryMatchNameWithGooglePlacesResults(name, results, tolerance, nameToMatch)
    
    def tryMatchNameLatLngWithGooglePlaces(self, 
                                           name, 
                                           latLng, 
                                           tolerance=DEFAULT_TOLERANCE, 
                                           nameToMatch=None):
        params  = self._getParams(name, { 'types' : self.TYPES })
        results = self.googlePlaces.getSearchResultsByLatLng(latLng, params)
        
        if results is None:
            # occasionally a google place search will leave out valid results 
            # if the optional 'types' parameter is set, even though those 
            # results conform to the given types... to get around this bug, 
            # if a more specific query containing the desired 'types' fails 
            # to return any results, we try once more without the 'types'.
            params  = self._getParams(name)
            results = self.googlePlaces.getSearchResultsByLatLng(latLng, params)
            
            if results is None:
                return None
        
        return self.tryMatchNameWithGooglePlacesResults(name, results, tolerance, nameToMatch)
    
    def tryMatchNameWithGooglePlacesResults(self, 
                                            name, 
                                            results, 
                                            tolerance=DEFAULT_TOLERANCE, 
                                            nameToMatch=None):
        # perform case-insensitive, fuzzy string matching to determine the 
        # best match in the google places result set for the target entity
        bestRatio = -1
        bestMatch = None
        
        for result in results:
            # TODO: look into using edit distance as an alternative via:
            #       http://code.google.com/p/pylevenshtein/
            resultName = result['name'].lower()
            ratio = SequenceMatcher(None, nameToMatch, resultName).ratio()
            
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
    
    def getCanonicalizedName(self, name, complexity, crippleName):
        complexity = min(max(complexity, 0), 1.0)
        name = name.lower()
        
        # return the lowercase name if no simplification is to occur
        if complexity >= 1.0:
            return name
        
        # initialize complexity-dependent detail delimiters
        wordDetailDelimiterBlacklistSet  = set()
        wordDetailDelimiterBlacklistSet |= self.wordDetailDelimiterBlacklistSet
        if complexity < 0.8:
            wordDetailDelimiterBlacklistSet.add("at")
            wordDetailDelimiterBlacklistSet.add("on")
        
        # filter and process individual words
        words = name.split()
        
        prevWords = None
        while (prevWords is None or len(words) != len(prevWords)) and len(words) > 0:
            prevWords = words
            
            # remove blacklisted prefix words
            while words[0] in self.wordPrefixBlacklistSet:
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
            
            if crippleName:
                # note: only cripple the name once during multiple iterations
                # (by truncating either the number of words or the number of 
                # characters within a single word)
                crippleName = False
                
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
        # whitespace that might've snuck in to form the resulting name
        return string.joinfields(words, ' ').strip()
    
    def _getParams(self, name, optionalParams=None):
        params = { 'name' : name }
        
        if optionalParams is not None:
            for param in optionalParams:
                params[param] = optionalParams[param]
        
        return params

def parseCommandLine():
    pass

def main():
    pass

if __name__ == '__main__':
    main()

