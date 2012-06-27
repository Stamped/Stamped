#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

# Results with lower data quality than this are summarily dropped pre-clustering.
MIN_RESULT_DATA_QUALITY_TO_CLUSTER = 0.1
# Results with lower data quality than this are allowed to cluster for the purposes of boosting the cluster's final
# score, but are never included in the final result.
MIN_RESULT_DATA_QUALITY_TO_INCLUDE = 0.3
# Clusters with data quality lower than this are not returned to the user.
MIN_CLUSTER_DATA_QUALITY = 0.7

############################################################################################################
################################################    FILM    ################################################
############################################################################################################

"""

    TITLE_REMOVAL_REGEXES = [
        re.compile(r'\s\[.*\]\s*$', re.IGNORECASE),
        re.compile(r'\s\(.*\)\s*$', re.IGNORECASE),
        re.compile(r'\sHD'),
        re.compile(r'\sBlu-?ray', re.IGNORECASE),
        ]

    @lazyProperty
    def name(self):
        rawTitle = xp(self.attributes, 'Title')['v']
        currTitle = rawTitle
        for titleRemovalRegex in self.TITLE_REMOVAL_REGEXES:
            alteredTitle = titleRemovalRegex.sub('', currTitle)
            # I'm concerned that a few of these titles could devour an entire title if something were named, like,
            # "The Complete Guide to _____" so this safeguard is built in for that purpose.
            if len(alteredTitle) >= 3:
                currTitle = alteredTitle
            else:
                logs.warning("Avoiding transformation to AmazonMovie title '%s' because result would be too short" %
                             rawTitle)
        if currTitle != rawTitle:
            logs.warning("Converted Amazon movie title: '%s' => '%s'" % (rawTitle, currTitle))
        return currTitle




            TITLE_REMOVAL_REGEXES = [
        re.compile(r'\s\[.*\]\s*$', re.IGNORECASE),
        re.compile(r'\s\(.*\)\s*$', re.IGNORECASE),
        re.compile(r'(\s*[:,;.-]+\s*|\s)(the )?complete.*$', re.IGNORECASE),
        re.compile(r'(\s*[:,;.-]+\s*|\s)(the )?[a-zA-Z0-9]{2,10} seasons?$', re.IGNORECASE),
        re.compile(r'(\s*[:,;.-]+\s*|\s)seasons?\s[a-zA-Z0-9].*$', re.IGNORECASE),
        re.compile(r'(\s*[:,;.-]+\s*|\s)(the )?[a-zA-Z0-9]{2,10} volumes?$', re.IGNORECASE),
        re.compile(r'(\s*[:,;.-]+\s*|\s)(volumes?|vol\.)\s[a-zA-Z0-9].*$', re.IGNORECASE),
        re.compile(r'^(the )?best (\w+ )?of ', re.IGNORECASE),
    ]

    @lazyProperty
    def name(self):
        rawTitle = xp(self.attributes, 'Title')['v']
        currTitle = rawTitle
        for titleRemovalRegex in self.TITLE_REMOVAL_REGEXES:
            alteredTitle = titleRemovalRegex.sub('', currTitle)
            # I'm concerned that a few of these titles could devour an entire title if something were named, like,
            # "The Complete Guide to _____" so this safeguard is built in for that purpose.
            if len(alteredTitle) >= 3:
                currTitle = alteredTitle
            else:
                logs.warning("Avoiding transformation to AmazonTvShow title '%s' because result would be too short" %
                             rawTitle)
        if currTitle != rawTitle:
            logs.warning("Converted Amazon TV title: '%s' => '%s'" % (rawTitle, currTitle))
        return currTitle

"""

def augmentFilmDataQualityOnBasicAttributePresence(filmSearchResult):
    pass


############################################################################################################
################################################   MUSIC    ################################################
############################################################################################################

def augmentMusicDataQualityOnBasicAttributePresence(musicSearchResult):
    pass


############################################################################################################
################################################   BOOKS    ################################################
############################################################################################################

def augmentBookDataQualityOnBasicAttributePresence(bookSearchResult):
    pass


############################################################################################################
################################################    APPS    ################################################
############################################################################################################

def augmentAppDataQualityOnBasicAttributePresence(appSearchResult):
    pass



############################################################################################################
################################################   PLACES   ################################################
############################################################################################################

def augmentPlaceDataQualityOnBasicAttributePresence(placeSearchResult):
    pass