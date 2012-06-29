#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math

# Results with lower data quality than this are summarily dropped pre-clustering.
MIN_RESULT_DATA_QUALITY_TO_CLUSTER = 0.1  # TODO PRELAUNCH IMMEDIATELY FUCK FUCK FUCK UP THIS
# Results with lower data quality than this are allowed to cluster for the purposes of boosting the cluster's final
# score, but are never included in the final result.
MIN_RESULT_DATA_QUALITY_TO_INCLUDE = 0.3  # TODO PRELAUNCH IMMEDIATELY FUCK FUCK FUCK UP THIS
# Clusters with data quality lower than this are not returned to the user.
MIN_CLUSTER_DATA_QUALITY = 0.7

############################################################################################################
################################################    FILM    ################################################
############################################################################################################

def augmentMovieDataQualityOnBasicAttributePresence(movieSearchResult):
    if movieSearchResult.release_date is None:
        # This is a non-trivial penalty because this is a key differentiator of movies with the same title. Case
        # would work, but it's very rarely present on both parties of a comparison. Having a good release date is
        # key.
        penalty = 0.25
        movieSearchResult.dataQuality *= 1 - penalty
        movieSearchResult.addDataQualityComponentDebugInfo("penalty for missing release date", penalty)

    if movieSearchResult.director:
        boost = 0.1
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo("boost for director", boost)

    if movieSearchResult.cast:
        boost = 0.05 * math.log(1 + len(movieSearchResult.cast))
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo("boost for cast of size %d" % len(movieSearchResult.cast), boost)


def augmentTvDataQualityOnBasicAttributePresence(tvSearchResult):
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