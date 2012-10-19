from __future__ import division

import Globals
import svmapi
import datetime
from resolve.StringComparator import titleComparison
from resolve.StringNormalizationUtils import movieSimplify
from resolve.TitleUtils import endsInDifferentNumbers
from libs.LRUCache import lru_cache

def parse_line(line):
    clusters = eval(line)
    items = []
    grouping = []
    counter = 0
    for c in clusters:
        group = []
        for r in c:
            items.append(r)
            group.append(counter)
            counter += 1
        grouping.append(set(group))
    return items, grouping


def read_examples(filename, sparm):
    with open(filename) as fin:
        return [parse_line(line) for line in fin]


def init_model(sample, sm, sparm):
    sm.size_psi = 14


def merge(v1, v2):
    return [a + b for a, b in zip(v1, v2)]


@lru_cache(1000)
def title_similarity(p1, p2):
    return titleComparison(p1, p2, movieSimplify)


@lru_cache(1000)
def release_similarity(p1, p2):
    return abs((p1 - p2).days / 365)


def score_stats(scores):
    if not scores:
        return [0, 0, 0]
    return [max(scores), sum(scores) / len(scores), min(scores)]


def psi_list(x, y):
    result = []
    used_pairs = set()
    title_scores = []
    release_scores = []
    different_numbers_count = 0
    for group in y:
        for a, b in [(a, b) for a in group for b in group if a > b]:
            used_pairs.add((a, b))
            title_scores.append(title_similarity(x[a][0], x[b][0]))
            if x[a][1] and x[b][1]:
                release_scores.append(release_similarity(x[a][1], x[b][1]))
            if endsInDifferentNumbers(x[a][0], x[b][0]):
                different_numbers_count += 1
    result.extend(score_stats(title_scores))
    result.extend(score_stats(release_scores))
    result.append(different_numbers_count)

    all_indices = range(len(x))
    all_pairs = {(a, b) for a in all_indices for b in all_indices if a > b}
    remaining_pairs = all_pairs - used_pairs
    title_scores = []
    release_scores = []
    different_numbers_count = 0
    for a, b in remaining_pairs:
        title_scores.append(title_similarity(x[a][0], x[b][0]))
        if x[a][1] and x[b][1]:
            release_scores.append(release_similarity(x[a][1], x[b][1]))
        if endsInDifferentNumbers(x[a][0], x[b][0]):
            different_numbers_count += 1
    result.extend(score_stats(title_scores))
    result.extend(score_stats(release_scores))
    result.append(different_numbers_count)
    return result


def psi(x, y, sm, sparm):
    return svmapi.Sparse(psi_list(x, y))


def loss(y, ybar, sparm):
    for c in ybar:
        if not any(c <= cy for cy in y):
            return 10
    assert len(ybar) >= len(y)
    if not ybar:
        return 0
    diff = len(ybar) - len(y)
    return diff * 10 / len(ybar)


def find_most_violated_constraint(x, y, sm, sparm):
    print 'START ' * 10
    print list(sm.w)
    print y
    def eval_func(x, y, ybar, py):
        pybar = psi_list(x, ybar)
        return loss(y, ybar, None) - del_psi(py, pybar, sm.w)
    result = accumulate_clusters(x, y, eval_func)
    print 'MOST VIOLATED', result
    print
    print
    print
    return result


def classify_example(x, sm, sparm):
    def eval_func(x, y, ybar, py):
        pybar = psi_list(x, ybar)
        return sum(wi * yi for wi, yi in zip(sm.w, pybar))
    return accumulate_clusters(x, [], eval_func)


def del_psi(y, ybar, w):
    return sum(wi * (yi - ybi) for wi, yi, ybi in zip(w, y, ybar))


def accumulate_clusters(x, y, eval_func):
    py = psi_list(x, y)
    current = [set([i]) for i in xrange(len(x))]
    best = eval_func(x, y, current, py)
    results = [(best, current)]
    while True:
        best, current = results[-1]
        if len(current) < 2:
            break
        scores = []
        for i in xrange(len(current)):
            for j in xrange(i):
                trial = list(current)
                merged = current[i] | current[j]
                del trial[i]
                del trial[j]
                trial.append(merged)
                scores.append((eval_func(x, y, trial, py), trial))
        results.append(max(scores))
    result = max(results)
    return result[1]


