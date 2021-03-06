#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import difflib
import os
import logs
import pickle
import pprint
import random

from sys import argv
from os import path

def __createDiffTable(leftData, rightData):
    leftLines = leftData.split('\n')
    rightLines = rightData.split('\n')
    differ = difflib.HtmlDiff(wrapcolumn=100)
    return differ.make_table(leftLines, rightLines)


def __stripEntity(entityDict):
    """Strip out irrelevant/noisy fields in the entity dict, so the output is
    more readable.
    """

    def stripTimestamps(d):
        return {k : v for k, v in d.iteritems() if 'timestamp' not in k}
    entityDict = stripTimestamps(entityDict)
    entityDict = {k : v for k, v in entityDict.iteritems() if not k.endswith('_source')}
    if 'sources' in entityDict:
        entityDict['sources'] = stripTimestamps(entityDict['sources'])
    return entityDict


DIFF_FILE_HEADER = """
<html>
    <head>
        <style type="text/css">
            .diff {font-family:Courier; border:medium;}
            .diff_header {background-color:#e0e0e0}
            td.diff_header {text-align:right}
            .diff_next {background-color:#c0c0c0}
            .diff_add {background-color:#aaffaa}
            .diff_chg {background-color:#ffff77}
            .diff_sub {background-color:#ffaaaa}
        </style>
    </head>
    <body>
"""


def __formatProxyList(proxies):
    # OK, so this line is a weird hack. Ugh.
    # Basically -- ResolverObject.__str__ won't issue any lookups to get information about something. But sometimes we
    # end up with proxies that literally just have keys and have to issue lookups to even have a title. Since __str__
    # won't force that, we force it ourselves here.
    # TODO: FIND A BETTER SOLUTION HERE.
    [proxy.name for proxy in proxies]

    return '\n\n'.join(str(proxy) for proxy in proxies)


def __hasClusteringChange(oldList, newList):
    oldSources = set([(proxy.source, proxy.key) for proxy in oldList])
    newSources = set([(proxy.source, proxy.key) for proxy in newList])
    return oldSources != newSources


def writeComparisons(oldResults, newResults, outputDir):
    oldKeys = oldResults.viewkeys()
    newKeys = newResults.viewkeys()
    if oldKeys ^ newKeys:
        print 'WARNING: old and new results have mismatched keys:'
        print '%d OLD KEYS:' % len(oldKeys - newKeys), oldKeys - newKeys
        print '%d NEW KEYS:' % len(newKeys - oldKeys), newKeys - oldKeys

    changedRows = []
    clusteringChanges = []
    allRows = []
    commonKeys = oldKeys & newKeys
    for key in commonKeys:
        oldResolved, oldOriginal, oldProxyList = oldResults[key]
        newResolved, newOriginal, newProxyList = newResults[key]

        filename = key[:40] + '.html'
        oldData = __stripEntity(oldResolved.dataExport())
        newData = __stripEntity(newResolved.dataExport())
        try:
            with open(path.join(outputDir, filename), 'w') as fout:
                print >> fout, DIFF_FILE_HEADER
                print >> fout, '<h1>%s</h1>' % 'Enrich Input'
                print >> fout, __createDiffTable(pprint.pformat(oldOriginal), pprint.pformat(newOriginal))
                print >> fout, '<h1>%s</h1>' % 'Resolve output'
                print >> fout, __createDiffTable(pprint.pformat(oldResolved.dataExport()), pprint.pformat(newResolved.dataExport()))
                print >> fout, '<h1>%s</h1>' % 'List of resolver objects:'
                print >> fout, __createDiffTable(__formatProxyList(oldProxyList), __formatProxyList(newProxyList))
                print >> fout, '</body></html>'
        except Exception:
            logs.warning('Error writing diff file!')
            logs.report()
        diffLink = '<td><a href="%s">show diffs</a></td>' % filename

        tableRow = '<tr><td>%s</td>%s</tr>' % (oldOriginal['title'][:100], diffLink)
        if oldData != newData:
            changedRows.append(tableRow)
        if __hasClusteringChange(oldProxyList, newProxyList):
            clusteringChanges.append(tableRow)
        allRows.append(tableRow)
    allRowsFilename = 'index_all.html'
    writeTableOfContent(allRows, 'All results', path.join(outputDir, allRowsFilename))

    summary = """
        %d out of %d (%f%%) of the rows had clustering change. Here's a shuffled list of them.
        <a href="%s">show all</a>
        """ % (len(clusteringChanges), len(allRows), float(len(clusteringChanges)) * 100 / len(allRows), allRowsFilename)
    random.shuffle(clusteringChanges)
    writeTableOfContent(clusteringChanges, summary, path.join(outputDir, 'index_cluster.html'))

    summary = """
        %d out of %d (%f%%) of the rows changed. Here's a shuffled list of them.
        <a href="%s">show all</a>
        """ % (len(changedRows), len(allRows), float(len(changedRows)) * 100 / len(allRows), allRowsFilename)
    random.shuffle(changedRows)
    writeTableOfContent(changedRows, summary, path.join(outputDir, 'index.html'))


def writeTableOfContent(table, heading, filename):
    # TODO(geoff): write a real HTML doc when not so lazy anymore.
    with open(filename, 'w') as fout:
        print >> fout, '<h1>%s</h1>' % heading
        print >> fout, '<table cellpadding="5">'
        for line in table:
            print >> fout, line.encode('utf-8')
        print >> fout, '</table>'


def main():
    if len(argv) != 4:
        print >> sys.stderr, 'Usage: ResolutionSxS.py oldResults newResults outputDir'
        return 1

    outputDir = argv[3]
    if not path.exists(outputDir):
        os.mkdir(outputDir)
    if not path.isdir(outputDir):
        raise Exception(outputDir + ' exists but is not a directory')

    with open(argv[1]) as fileIn:
        oldResults = pickle.load(fileIn)
    with open(argv[2]) as fileIn:
        newResults = pickle.load(fileIn)
    writeComparisons(oldResults, newResults, outputDir)


if __name__ == '__main__':
    main()
