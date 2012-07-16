#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs, math, re
from collections import defaultdict
from resolve.StampedSource import StampedSource

stamped_source = StampedSource()

def summarize_entity_for_error_text(entity):
    title = entity.title
    if isinstance(title, unicode):
        title = title.encode('utf-8')
    return '"%s" (id:%s)' % (title, entity.entity_id)


class ExpectedResults(object):
    def __init__(self, *matchers):
        self.__matchers = tuple(matchers)

    @property
    def matchers(self):
        return self.__matchers

    def score_results(self, entities_and_clusters, errors):
        matchers_to_matched_idxs = []
        for _ in self.matchers:
            matchers_to_matched_idxs.append([])

        for idx, (entity, cluster) in enumerate(entities_and_clusters):
            idx = idx + 1
            matched_idx = False
            entity_as_proxy = stamped_source.proxyFromEntity(entity)
            for (matcher_idx, matcher) in enumerate(self.matchers):
                if matcher.matches(entity_as_proxy):
                    if matched_idx:
                        raise Exception('FUCK! Result %s matched multiple SearchResultMatchers!' %
                                        summarize_entity_for_error_text(entity))
                    matchers_to_matched_idxs[matcher_idx].append(idx)
                    matched_idx = True

        max_score = 0
        for i in range(len(self.matchers)):
            max_score += (i + 1) ** -0.5
        score = 0
        for i, matcher in enumerate(self.matchers):
            matched_idxs = matchers_to_matched_idxs[i]
            if not matched_idxs:
                errors.append('Failed to find result matching SearchResultMatcher: ' + repr(matcher))
                continue

            match_score = ((i + 1) ** -0.1) * ((matched_idxs[0] + 1) ** -0.4)
            if matched_idxs[0] > i:
                errors.append('SearchResultMatcher %s expected in results at position %d, found at position %d' % (
                    repr(matcher), i + 1, matched_idxs[0] + 1
                ))
                suboptimal_ranking = True
            if len(matched_idxs) > 1 and matcher.must_be_unique:
                errors.append('Found %i results matching SearchResultMatcher: %s' % (len(matched_idxs), repr(matcher)))
                match_score *= 0.7 ** (len(matched_idxs) - 1)
            score *= self.calculate_match_sources_penalty(matcher, entities_and_clusters[matched_idxs[0]], errors)
            score += max_score

        return float(score) / max_score

    def calculate_match_sources_penalty(self, matcher, (entity, cluster), errors):
        result_sources = set()
        for result in cluster.results:
            if result.dataQuality > DataQualityUtils.MIN_RESULT_DATA_QUALITY_TO_INCLUDE:
                result_sources.add(result.resolverObject.source)
        numerator = 5
        denominator = 5
        missing_expected_sources = []
        for source in matcher.all_sources:
            expected_source = matcher.expected_sources and source in matcher.expected_sources
            weight = 5 if expected_source else 1
            denominator += weight
            if source in result_sources:
                numerator += 5
            elif expected_source:
                missing_expected_sources.append(expected_source)
        if missing_expected_sources:
            errors.append('Result for matcher %s is missing expected sources [%s]' % (
                repr(matcher), ', '.join(missing_expected_sources)
            ))
        return float(numerator) / denominator


class ResultPenalty(object):
    def assess_penalty(self, entities_and_clusters, errors):
        raise NotImplementedError()


class ApparentDupesPenalty(object):
    def assess_penalty(self, base_score, entities_and_clusters, expected_results, errors):
        score = base_score
        titles_and_subtitles_to_counts = defaultdict(int)
        for entity, cluster in entities_and_clusters:
            titles_and_subtitles_to_counts[(entity.title, entity.search_subtitle)] += 1
        for ((title, subtitle), count) in titles_and_subtitles_to_counts.items():
            if isinstance(title, unicode):
                title = title.encode('utf-8')
            if isinstance(subtitle, unicode):
                subtitle = subtitle.encode('utf-8')
            if count > 1:
                errors.append('Result title/subtitle "%s"/"%s" occurs %d times!' % (
                    title, subtitle, count
                ))
                score *= 0.95 ** (count - 1)
        return score


class ClusterConsistencyPenalty(object):
    def assess_penalty(self, base_score, entities_and_clusters, expected_results, errors):
        score = base_score
        for matcher in expected_results.matchers:
            for entity, cluster in entities_and_clusters:
                entity_as_proxy = stamped_source.proxyFromEntity(entity)
                if matcher.matches(entity_as_proxy):
                    score = self.__check_full_cluster_matches(matcher, entity_as_proxy, cluster, score, errors)
                    break
        return score

    def __check_full_cluster_matches(self, matcher, entity_as_proxy, cluster, score, errors):
        failed_match_descriptions = []
        for result in cluster.results:
            if not matcher.matches(result):
                failed_match_descriptions.append(matcher.repr_proxy(result))
        if not failed_match_descriptions:
            return
        proportion_failed = float(len(failed_match_descriptions)) / len(cluster.results)
        penalty = 0.2 * (proportion_failed ** 0.5)
        errors.append('For result %s, matching %s, %d results within cluster were inconsistent: [%s]' % (
            matcher.repr_proxy(entity_as_proxy),
            repr(matcher),
            len(failed_match_descriptions),
            ', '.join([proxy_description for proxy_description in failed_match_descriptions])
        ))
        return score * (1 - penalty)


class SearchResultsScorer(object):
    def __init__(self):
        self.__standard_penalties = (ApparentDupesPenalty(), ClusterConsistencyPenalty())

    def score_results(self, expected_results, entities_and_clusters):
        errors = []
        score = expected_results.score_results(entities_and_clusters, errors)
        for penalty in self.__standard_penalties:
            score = penalty.assess_penalty(score, entities_and_clusters, expected_results, errors)
        return score, errors