#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import difflib
import os
import pickle
import pprint
import random

from sys import argv
from os import path

def writeComparisons(oldResults, newResults, outputDir):
    oldKeys = oldResults.viewkeys()
    newKeys = newResults.viewkeys()
    if oldKeys ^ newKeys:
        print 'WARNING: old and new results have mismatched keys:'
        print 'OLD KEYS:', oldKeys - newKeys
        print 'NEW KEYS:', newKeys - oldKeys

    changedRows = []
    allRows = []
    commonKeys = oldKeys & newKeys
    for key in sorted(commonKeys):
        original, oldResolved = oldResults[key]
        _, newResolved = newResults[key]

        filename = key + '.html'
        with open(path.join(outputDir, filename), 'w') as fout:
            print >> fout, '<pre>'
            pprint.pprint(original, fout)
            print >> fout, '</pre>'
        originalLink = '<td><a href="%s">original</a></td>' % filename

        leftData = oldResolved.dataExport()
        rightData = newResolved.dataExport()
        leftLines = pprint.pformat(leftData).split('\n')
        rightLines = pprint.pformat(rightData).split('\n')
        differ = difflib.HtmlDiff(wrapcolumn=100)
        filename = key + '_diff.html'
        with open(path.join(outputDir, filename), 'w') as fout:
            print >> fout, differ.make_file(leftLines, rightLines)
        diffLink = '<td><a href="%s">show diff</a></td>' % filename

        tableRow = '<tr><td>%s</td>%s%s' % (original['title'], originalLink, diffLink)
        if leftData != rightData:
            changedRows.append(tableRow)
        allRows.append(tableRow)
    allRowsFilename = 'index_all.html'
    writeTableOfContent(allRows, 'All results', path.join(outputDir, allRowsFilename))

    summary = """
        %d out of %d (%f%%) of the rows changed. Here's a shuffled list of them.
        <a href="%s">show all</a>
        """ % (len(changedRows), len(allRows), float(len(changedRows)) / len(allRows), allRowsFilename)
    random.shuffle(changedRows)
    writeTableOfContent(changedRows, summary, path.join(outputDir, 'index.html'))


def writeTableOfContent(table, heading, filename):
    # TODO(geoff): write a real HTML doc when not so lazy anymore.
    with open(filename, 'w') as fout:
        print >> fout, '<h1>%s</h1>' % heading
        print >> fout, '<table>'
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
