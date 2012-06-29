#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from os import path

import difflib
import itertools
import optparse
import os
import pickle
import pprint
import random
import sys
import EntitiesSxSTemplates

# We need the import(s) in the following section because they are referenced by
# the pickled objects
import datetime
import search.SearchResultCluster
from api.Schemas import PlaceEntity

def loadSearchResultsFromFile(filename):
    returnDict = {}
    with open(filename) as f:
        fullResults = pickle.load(f)
    for query, resultList in fullResults.iteritems():
        stripedList = [(entity, stripEntity(entity.dataExport()), cluster) for entity, cluster in resultList]
        returnDict[query] = stripedList
    return returnDict


def stripEntity(entityDict):
    """Strip out irrelevant/noisy fields in the entity dict, so the output is
    more readable.
    """

    def stripTimestamps(d):
        return {k : v for k, v in d.iteritems() if 'timestamp' not in k}
    def stripSourceFields(d):
        return {k : v for k, v in d.iteritems() if '_source' not in k}
    entityDict = stripTimestamps(entityDict)
    entityDict = stripSourceFields(entityDict)
    if 'sources' in entityDict:
        entityDict['sources'] = stripTimestamps(entityDict['sources'])
    return entityDict


def differenceScore(left, right):
    commonKeys = left.viewkeys() & right.viewkeys()
    score = len(left) + len(right) - len(commonKeys) * 2
    for key in commonKeys:
        if left[key] != right[key]:
            # TODO(geoff): maybe consider recursing if the field is a nested
            # message.
            score += 1
    return score


def writeComparisons(oldResults, newResults, outputDir, diffThreshold):
    changedTableRows = []
    allTableRows = []
    statsText = '%d same position, %d moved, %d added, %d droped'
    linkText = '<a href="%s">%s</a>'
    for key in sorted(oldResults.keys()):
        (same, moved, added, dropped), filename = compareSingleSearch(
                key, oldResults[key], newResults[key], outputDir, diffThreshold)
        row = linkText % (filename, key), statsText % (same, moved, added, dropped)
        if moved or added or dropped:
            changedTableRows.append(row)
        allTableRows.append(row)
    random.shuffle(changedTableRows)

    summary = "%d out of %d queries had changes (%f%%). Here's a random list of them" % (
            len(changedTableRows), len(oldResults), float(len(changedTableRows)) / len(oldResults) * 100)
    summary += ' <a href="index_all.html">show all</a>'

    htmlRowTpl = '<tr><td>%s</td><td>%s</td></tr>'
    with open(path.join(outputDir, 'index.html'), 'w') as fout:
        print >> fout, EntitiesSxSTemplates.SUMMARY_TPL % (
                summary, ''.join(htmlRowTpl % row for row in changedTableRows))
    with open(path.join(outputDir, 'index_all.html'), 'w') as fout:
        print >> fout, EntitiesSxSTemplates.SUMMARY_TPL % (
                'All queries', ''.join(htmlRowTpl % row for row in allTableRows))


def compareSingleSearch(query, oldResults, newResults, outputDir, diffThreshold):
    diffScores = []
    for i, left in enumerate(oldResults):
        for j, right in enumerate(newResults):
            score = differenceScore(left[1], right[1])
            if score <= diffThreshold:
                diffScores.append((score, i, j))
    # Find the most similar pair. When there are ties, lower i values (higher
    # ranked items in the original list) come first, since they are probably
    # relevant, and then lower values of j (causes a smaller shift) come first.
    diffScores.sort()

    movements = {}
    for _, i, j in diffScores:
        if i in movements or j in movements.values():
            continue
        movements[i] = j

    filenameBase = ''.join(c if c.isalnum() else '_' for c in query)

    linksLeft = []
    linksRightIndexed = {}
    for i, entity in enumerate(oldResults):
        if i in movements:
            diffFileName = '%s-c%d.html' % (filenameBase, i)
            destination = movements[i]
            newEntity = newResults[destination]
            writeCompareEntity(entity, newEntity, outputDir, diffFileName)

            cellId = "diff" + str(i)
            anchorTextTpl = '%s<a href="%s">%%s</a></td>' % (makeHighlightingTableCell(cellId), diffFileName)
            linksLeft.append(anchorTextTpl % extractLinkText(entity))
            linksRightIndexed[destination] = anchorTextTpl % extractLinkText(newEntity)
        else:
            linksLeft.append(writeSingleEntity(entity, outputDir, '%s-l%d.html' % (filenameBase, i), 'l%d' % i))

    linksRight = []
    for i, entity in enumerate(newResults):
        if i in linksRightIndexed:
            linksRight.append(linksRightIndexed[i])
        else:
            linksRight.append(writeSingleEntity(entity, outputDir, '%s-r%d.html' % (filenameBase, i), 'r%d' % i))

    fileContent = [EntitiesSxSTemplates.COMPARE_HEADER % (query, query)]
    for links in itertools.izip_longest(linksLeft, linksRight, fillvalue='<td></td>'):
        fileContent.append('<tr>%s%s</tr>' % links)
    fileContent.append(EntitiesSxSTemplates.COMPARE_FOOTER)

    with open(path.join(outputDir, filenameBase) + '.html', 'w') as fout:
        for line in fileContent:
            print >> fout, line.encode('utf-8')

    # Now compute the stats:
    same = sum(1 for i, j in movements.iteritems() if i == j)
    moved = len(movements) - same
    added = len(newResults) - len(movements)
    dropped = len(oldResults) - len(movements)
    return (same, moved, added, dropped), filenameBase + '.html'


def writeSingleEntity(entity, outputDir, filename, cellId):
    with open(path.join(outputDir, filename), 'w') as fout:
        # TODO(geoff): This doesn't produce proper HTML
        print >> fout, '<pre>'
        pprint.pprint(entity[1:], fout)
        print >> fout, '</pre>'
    return '%s<a href="%s">%s</a></td>' % (
            makeHighlightingTableCell(cellId), filename, extractLinkText(entity))


def makeHighlightingTableCell(name):
    return '<td onmouseover=highlightCell("%s") onmouseout=unhighlightCell("%s") name="%s">' % ((name,) * 3)

def writeCompareEntity(left, right, outputDir, filename):
    leftLines = pprint.pformat(left[1:]).split('\n')
    rightLines = pprint.pformat(right[1:]).split('\n')
    differ = difflib.HtmlDiff(wrapcolumn=100)
    with open(path.join(outputDir, filename), 'w') as fout:
        print >> fout, differ.make_file(leftLines, rightLines)


def extractLinkText(entity):
    subtitle = entity[0].subtitle
    if isinstance(entity[0], PlaceEntity) and entity[0].formatAddress():
        subtitle = entity[0].formatAddress()
    return '<p>%s</p><p style="text-indent:4em">%s</p>' % (entity[0].title, subtitle)


def ensureDirectory(pathName):
    if not path.exists(pathName):
        os.mkdir(pathName)
    if not path.isdir(pathName):
        raise Exception(pathName + ' exists but is not a directory')


def main():
    parser = optparse.OptionParser()
    parser.add_option('-t', dest='diffThreshold', type='int', default=3)
    options, args = parser.parse_args()

    if len(args) != 3:
        print >> sys.stderr, 'Usage: EntitiesSxS.py oldResults newResults outputDir'
        return 1

    ensureDirectory(args[2])

    oldResults = loadSearchResultsFromFile(args[0])
    newResults = loadSearchResultsFromFile(args[1])
    writeComparisons(oldResults, newResults, args[2], options.diffThreshold)


if __name__ == '__main__':
    main()
