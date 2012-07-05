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

class GooglePlacesEntityMatcher(object):
    """
        Utility class which attempts to cross-reference entities from various 
    sources with Google Places.
    """
    
    DEFAULT_TOLERANCE = 0.9
    TYPES = 'restaurant|food|bar|cafe|establishment'
    
    def __init__(self):
        self.googlePlaces = GooglePlaces()
        self.initWordBlacklistSets()
    
    def tryMatchEntityWithGooglePlaces(self, entity, tolerance=DEFAULT_TOLERANCE, detailed=False):
        try:
            latLng = (entity.lat, entity.lng)
        except KeyError:
            address = entity.address
            latLng  = self.googlePlaces.addressToLatLng(address)
            
            if latLng is None:
                return None
            
            entity.lat = latLng[0]
            entity.lng = latLng[1]
            latLng = (entity.lat, entity.lng)
        
        if 'openTable' in entity.sources:
            numComplexityLevels = 16
        else:
            numComplexityLevels = 4
        
        prevTitle = None
        origTitle = entity['title'].lower()
        
        # attempt to match the entity with increasing simplifications applied 
        # to the search title, beginning with no simplification and retrying as 
        # necessary until we find a match, eventually falling back to a blank 
        # title search at the most simplified level
        for i in xrange(numComplexityLevels):
            complexity = float(numComplexityLevels - i - 1) / (max(1, numComplexityLevels - 1))
            title = self.getCanonicalizedTitle(origTitle, complexity, True)
            
            # don't attempt to find a match if this simplified title is the same 
            # as the previous level's simplified title (e.g., because we know it 
            # will return the same negative results)
            if title != prevTitle:
                titleToMatch = self.getCanonicalizedTitle(origTitle, complexity, False)
                #utils.log("NAME: %s, complexity: %g" % (title, complexity))
                prevTitle = title
                
                # attempt to match the current simplified title and latLng 
                match = self.tryMatchTitleLatLngWithGooglePlaces(title, 
                    latLng, tolerance, titleToMatch)
                
                if match is not None:
                    return self.googlePlaces.getEntityFromResult(match, detailed=detailed)
        
        return None
    
    def tryMatchTitleLatLngWithGooglePlaces(self, 
                                            title, 
                                            latLng, 
                                            tolerance=DEFAULT_TOLERANCE, 
                                            titleToMatch=None):
        params  = self._getParams(title, { 'types' : self.TYPES })
        results = self.googlePlaces.getSearchResultsByLatLng(latLng, params)
        
        if results is None:
            # occasionally a google place search will leave out valid results 
            # if the optional 'types' parameter is set, even though those 
            # results conform to the given types... to get around this bug, 
            # if a more specific query containing the desired 'types' fails 
            # to return any results, we try once more without the 'types'.
            params  = self._getParams(title)
            results = self.googlePlaces.getSearchResultsByLatLng(latLng, params)
            
            if results is None:
                return None
        
        return self.tryMatchTitleWithGooglePlacesResults(title, results, tolerance, titleToMatch)
    
    def tryMatchTitleWithGooglePlacesResults(self, 
                                             title, 
                                             results, 
                                             tolerance=DEFAULT_TOLERANCE, 
                                             titleToMatch=None):
        # perform case-insensitive, fuzzy string matching to determine the 
        # best match in the google places result set for the target entity
        bestRatio = -1
        bestMatch = None
        
        for result in results:
            # TODO: look into using edit distance as an alternative via:
            #       http://code.google.com/p/pylevenshtein/
            resultTitle = result['name'].lower()
            ratio = SequenceMatcher(None, titleToMatch, resultTitle).ratio()
            
            if ratio > bestRatio:
                bestRatio = ratio
                bestMatch = result
            
            types = result['types']
        
        # if no results matched the entity within the acceptable tolerance 
        # level, then disregard the results as irrelevant and return 
        # empty-handed
        if bestRatio <= 1.0 - tolerance:
            return None
        
        # otherwise, we have a match!
        return bestMatch
    
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
    
    def _getParams(self, title, optionalParams=None):
        params = { 'name' : title }
        
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

