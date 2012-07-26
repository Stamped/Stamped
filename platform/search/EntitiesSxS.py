#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from os import path

import difflib
import inspect
import itertools
import optparse
import os
import pickle
import pprint
import random
import shutil
import sys
import EntitiesSxSTemplates
from search.DataQualityUtils import MIN_RESULT_DATA_QUALITY_TO_INCLUDE

# We need the import(s) in the following section because they are referenced by
# the pickled objects
import datetime
import search.SearchResultCluster
from api.Schemas import PlaceEntity
from resolve.ResolverObject import *

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
    clusterKeysLeft = set(result.resolverObject.key for result in left.results)
    clusterKeysRight = set(result.resolverObject.key for result in right.results)
    commonKeys = clusterKeysLeft & clusterKeysRight
    if not commonKeys:
        return 1000
    diffKeys = clusterKeysLeft ^ clusterKeysRight
    return float(len(diffKeys)) / len(commonKeys)


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


def getProxySummary(proxy):
    title = repr(proxy.raw_name)
    if isBook(proxy) and proxy.authors:
        title = '%s by %s' % (proxy.raw_name, proxy.authors[0]['name'])
    elif isAlbum(proxy) and proxy.artists:
        title = '%s by %s' % (proxy.raw_name, proxy.artists[0]['name'])
    elif isTrack(proxy) and proxy.artists:
        title = '%s by %s' % (proxy.raw_name, proxy.artists[0]['name'])
    elif isTvShow(proxy) and proxy.release_date:
        title = '%s (%d)' % (proxy.raw_name, proxy.release_date.year)
    return ('%s, %s:%s' % (title, proxy.source, str(proxy.key)[:15]))


def getClusteringDifference(cellId, oldCluster, newCluster):
    def makeProxyDict(cluster):
        proxyDict = {}
        for result in cluster.results:
            proxy = result.resolverObject
            proxyDict[proxy.source, proxy.key] = proxy, result.dataQuality
        return proxyDict

    def makeListItem(text, dataQualityScore):
        openTag, closeTag = '<li>', '</li>'
        if dataQualityScore < MIN_RESULT_DATA_QUALITY_TO_INCLUDE:
            openTag, closeTag = '<li><font color="grey">', '</font></li>'
        return '%s%s%s' % (openTag, text, closeTag)

    oldProxies = makeProxyDict(oldCluster)
    newProxies = makeProxyDict(newCluster)
    dropped = oldProxies.viewkeys() - newProxies.viewkeys()
    added = newProxies.viewkeys() - oldProxies.viewkeys()
    same = newProxies.viewkeys() & oldProxies.viewkeys()
    summary = ''
    if same:
        summary += '<h3>Elements stayed the same</h3><ul>'
        for source in same:
            proxy, score = oldProxies[source]
            summary += makeListItem(getProxySummary(proxy), score)
        summary += '</ul>'
    majorChange = False
    if dropped:
        summary += '<h3>Elements dropped from cluster</h3><ul>'
        for source in dropped:
            proxy, score = oldProxies[source]
            summary += makeListItem(getProxySummary(proxy), score)
            if score > MIN_RESULT_DATA_QUALITY_TO_INCLUDE:
                majorChange = True
        summary += '</ul>'
    if added:
        summary += '<h3>Elements added to cluster</h3><ul>'
        for source in added:
            proxy, score = newProxies[source]
            summary += makeListItem(getProxySummary(proxy), score)
            if score > MIN_RESULT_DATA_QUALITY_TO_INCLUDE:
                majorChange = True
        summary += '</ul>'
    return summary, majorChange


def getSingleClusterSummary(cellId, cluster):
    summary = '<h3>Cluster component summary</h3><ul>'
    for result in cluster.results:
        proxy = result.resolverObject
        summary += '<li>%s</li>' % getProxySummary(proxy)
    summary += '</ul>'
    return summary


def compareSingleSearch(query, oldResults, newResults, outputDir, diffThreshold):
    diffScores = []
    for i, left in enumerate(oldResults):
        for j, right in enumerate(newResults):
            score = differenceScore(left[2], right[2])
            if score <= diffThreshold or left[0].title == right[0].title and left[0].subtitle == right[0].subtitle:
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
    clusterSummariesLeft = []
    clusterSummariesRightIndexed = {}
    for i, entity in enumerate(oldResults):
        if i in movements:
            diffFileName = '%s-c%d.html' % (filenameBase, i)
            destination = movements[i]
            newEntity = newResults[destination]
            writeCompareEntity(entity, newEntity, outputDir, diffFileName)

            cellId = "diff" + str(i)
            summary, changeMajor = getClusteringDifference(cellId, entity[2], newEntity[2])
            majorChangeIcon = '<img src="major_change_icon.jpg" style="max-height:40;max-width:40;float:left" />' if changeMajor else ''
            anchorTextTpl = '%s<a href="%s">%s%%s</a></td>' % (makeHighlightingTableCell(cellId), diffFileName, majorChangeIcon)
            linksLeft.append(anchorTextTpl % extractLinkText(entity))
            linksRightIndexed[destination] = anchorTextTpl % extractLinkText(newEntity)
            clusterSummariesLeft.append(summary)
            clusterSummariesRightIndexed[destination] = summary
        else:
            cellId = 'l%d' % i
            linksLeft.append(writeSingleEntity(entity, outputDir, '%s-l%d.html' % (filenameBase, i), cellId))
            clusterSummariesLeft.append(getSingleClusterSummary(cellId, entity[2]))

    linksRight = []
    clusterSummariesRight = []
    for i, entity in enumerate(newResults):
        if i in linksRightIndexed:
            linksRight.append(linksRightIndexed[i])
            clusterSummariesRight.append(clusterSummariesRightIndexed[i])
        else:
            cellId = 'r%d' % i
            linksRight.append(writeSingleEntity(entity, outputDir, '%s-r%d.html' % (filenameBase, i), cellId))
            clusterSummariesRight.append(getSingleClusterSummary(cellId, entity[2]))

    summaries = list(itertools.izip_longest(clusterSummariesLeft, clusterSummariesRight, fillvalue=''))
    fileContent = [EntitiesSxSTemplates.COMPARE_HEADER % (query, query)]
    for rowNumber, links in enumerate(itertools.izip_longest(linksLeft, linksRight, fillvalue='<td></td>')):
        rowId = 'row%d' % rowNumber
        fileContent.append('<tr onmouseover=showCell("%s") onmouseout=hideCell("%s")>%s%s</tr>' % ((rowId, rowId,) + links))
        fileContent.append('<tr style="display:none" name="%s"><td>%s</td><td>%s</td></tr>' % ((rowId,) + summaries[rowNumber]))
    fileContent.append(EntitiesSxSTemplates.COMPARE_FOOTER)

    with open(path.join(outputDir, filenameBase) + '.html', 'w') as fout:
        for line in fileContent:
            if isinstance(line, unicode):
                line = line.encode('utf-8')
            print >> fout, line

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
    entity = entity[0]
    subtitle = entity.subtitle
    if isinstance(entity, PlaceEntity) and entity.formatAddress():
        subtitle = entity.formatAddress()
    if entity.images:
        imageUrl = entity.images[0].sizes[0].url
        imageTag = '<img src="%s" style="float:right" />' % imageUrl
    else:
        imageTag = ''
    return '%s<p>%s</p><p style="text-indent:4em">%s</p>' % (imageTag, entity.title, subtitle)


def ensureDirectory(pathName):
    if not path.exists(pathName):
        os.mkdir(pathName)
    if not path.isdir(pathName):
        raise Exception(pathName + ' exists but is not a directory')


def main():
    parser = optparse.OptionParser()
    parser.add_option('-t', dest='diffThreshold', type='int', default=0.5)
    options, args = parser.parse_args()

    if len(args) != 3:
        print >> sys.stderr, 'Usage: EntitiesSxS.py oldResults newResults outputDir'
        return 1

    ensureDirectory(args[2])

    majorChangeIcon = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            'major_change_icon.jpg')
    shutil.copy(majorChangeIcon, args[2])

    oldResults = loadSearchResultsFromFile(args[0])
    newResults = loadSearchResultsFromFile(args[1])
    writeComparisons(oldResults, newResults, args[2], options.diffThreshold)


if __name__ == '__main__':
    main()
