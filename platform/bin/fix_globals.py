#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import collections, os, re, sys

class Node(object):
    TYPE_MODULE = 'module'
    TYPE_CLASS = 'class'
    TYPE_FUNCTION = 'function'

    def __init__(self, name, pathComponents, type_str):
        self.__name = name
        self.__pathComponents = tuple(pathComponents)
        self.__type_str = type_str
        print 'Building node:', self

    @property
    def name(self):
        return self.__name

    @property
    def pathComponents(self):
        return self.__pathComponents

    @property
    def type_str(self):
        return self.__type_str

    @property
    def parentModuleStr(self):
        return '.'.join(list(self.__pathComponents))

    @property
    def fullImportStr(self):
        return '.'.join(list(self.__pathComponents) + [self.__name])

    def __repr__(self):
        return '<Node: %s, type: %s>' % (self.fullImportStr, self.__type_str)


CLASS_DEFINITION = re.compile(r'\nclass ([A-Za-z0-9_]+)[(:]')
FUNCTION_DEFINITION = re.compile(r'\ndef ([a-zA-Z0-9_]+)\(.*\):')
def parseClassesAndFunctionsFromFile(fileText):
    classDefMatches = [match for match in CLASS_DEFINITION.findall(fileText)]
    functionDefMatches = [match for match in FUNCTION_DEFINITION.findall(fileText)]
    return classDefMatches, functionDefMatches

def buildNamesToNodesMap(basePath):
    namesToNodes = collections.defaultdict(list)
    for dir, subdir, files in os.walk(basePath):
        assert(dir.startswith(basePath))
        relativePath = dir[len(basePath):]
        pathComponents = filter(lambda x: x, relativePath.split('/'))

        pyfiles = filter(lambda file: file.endswith('.py'), files)
        for pyfile in pyfiles:
            # We're ignoring Globals and __init__ for what I think are obvious reasons.
            # BeautifulSoup is a file we have but also a Python library and we always mean the Python library, so I
            # just avoid that confusion here.
            if pyfile in ('Globals.py', '__init__.py', 'BeautifulSoup.py'):
                continue

            moduleName = pyfile[:-len('.py')]
            moduleNode = Node(moduleName, pathComponents, Node.TYPE_MODULE)
            namesToNodes[moduleName].append(moduleNode)

            fullPath = os.path.join(dir, pyfile)
            with open(fullPath) as f:
                contents = f.read()

            print 'Building module node:', fullPath

            modulePathComponents = pathComponents + [moduleName]
            classes, functions = parseClassesAndFunctionsFromFile(contents)
            for className in classes:
                namesToNodes[className].append(Node(className, modulePathComponents, Node.TYPE_CLASS))
            for functionName in functions:
                namesToNodes[functionName].append(Node(functionName, modulePathComponents, Node.TYPE_FUNCTION))

    return namesToNodes

def findMatches(namesToNodes, importPath, importName=None, reqType=None, currModule=None):
    if 'MongoAlertQueue' in importPath or (importName and 'MongoAlertQueue' in importName):
        print 'FUCK FUCK FUCK FINDING MATCHES FOR importName=', importName, 'importPath=', importPath
    pathSegments = importPath.split('.')
    if not importName:
        importName = pathSegments.pop()
    if importName not in namesToNodes:
        return ()
    nodes = namesToNodes[importName]
    matches = []
    for node in nodes:
        if reqType is not None and node.type_str != reqType:
            #print 'KILLING MATCH BECAUSE OF REQTYPE:', node
            continue
        if not pathSegments and node.type_str != Node.TYPE_MODULE:
            # You can't just say 'import foo' to import class foo. The first piece has to be a module.
            #print 'KILLING MATCH BECAUSE OF REQTYPE2:', node
            continue
        nodePathSegments = node.pathComponents
        if len(nodePathSegments) < len(pathSegments):
            continue
        potentialMatch = True
        for (seg1, seg2) in zip(reversed(nodePathSegments), reversed(pathSegments)):
            potentialMatch &= seg1 == seg2
        if potentialMatch:
            #print 'POTENTIAL MATCH:',node
            matches.append(node)
    if not matches:
        print 'NO MATCHES FOR IMPORT:', '.'.join(pathSegments + [importPath])
    if len(matches) > 2:
        print '\n\nWARNING: AMBIGUOUS MATCHES FOR IMPORT:', '.'.join(pathSegments + [importPath])
        for match in matches:
            print match
        print 'END MATCHES\n\n'
        for match in matches:
            if match.parentModuleStr == currModule:
                print 'PICKING OBVIOUS MATCH', match
                return [match]
        print 'NO OBVIOUS MATCH'
    return matches

IMPORT_RE = re.compile(r'\s*#?\s*import\s+([a-zA-Z0-9_*.]+(\s*,\s*[a-zA-Z0-9_*.]+)*)(\s+as[^\n]+)?\s*')
IMPORT_FROM_RE = re.compile(r'\s*#?\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_*.]+(\s*,\s*[a-zA-Z0-9_*.]+)*)(\s+as[^\n]+)?\s*')
def fixImports(basePath, namesToNodes):
    for dir, subdir, files in os.walk(basePath):
        pyfiles = filter(lambda file: file.endswith('.py'), files)
        for pyfile in pyfiles:
            if pyfile == 'Globals.py':
                continue
            fullPath = os.path.join(dir, pyfile)
            print '\n\nHANDLING:', fullPath

            relativePath = dir[len(basePath):]
            pathComponents = filter(lambda x: x, relativePath.split('/'))
            currModule = '.'.join(pathComponents)

            with open(fullPath) as f:
                lines = f.readlines()
            changedFile = False
            for lineIdx in range(len(lines)):
                line = lines[lineIdx]
                newLine = line
                foundImport = False
                if IMPORT_RE.match(line):
                    foundImport = True
                    match = IMPORT_RE.match(line)
                    importBody = match.group(1)
                    importStrs = [importStr.strip() for importStr in importBody.split(',')]
                    changed = False
                    for importStrIdx in range(len(importStrs)):
                        importStr = importStrs[importStrIdx]
                        segments = importStr.split('.')
                        name = segments[-1]
                        potentialMatches = findMatches(namesToNodes, importStr, currModule=currModule)
                        if len(potentialMatches) == 1 and potentialMatches[0].fullImportStr != importStr:
                            importStrs[importStrIdx] = potentialMatches[0].fullImportStr
                            changed = True
                    if changed:
                        importBody = ', '.join(importStrs)
                        newLine = line[:match.start(1)] + importBody + line[match.end(1):]

                elif IMPORT_FROM_RE.match(line):
                    foundImport = True
                    match = IMPORT_FROM_RE.match(line)
                    parentModule = match.group(1)
                    acceptableParentModules = None
                    importStrs = [importStr.strip() for importStr in match.group(2).split(',')]
                    if len(importStrs) == 1 and importStrs[0] == '*':
                        potentialMatches = findMatches(namesToNodes, parentModule, reqType=Node.TYPE_MODULE, currModule=currModule)
                        if len(potentialMatches) == 1 and potentialMatches[0].fullImportStr != importStrs[0]:
                            newLine = line[:match.start(1)] + potentialMatches[0].fullImportStr + line[match.end(1):]

                    else:
                        for importStr in importStrs:
                            potentialMatches = findMatches(namesToNodes, parentModule, importName=importStr, currModule=currModule)
                            currPotentialParentModules = set(match.parentModuleStr for match in potentialMatches)
                            if acceptableParentModules is None:
                                acceptableParentModules = currPotentialParentModules
                            else:
                                acceptableParentModules = acceptableParentModules.intersection(currPotentialParentModules)
                        if not acceptableParentModules:
                            pass
                        elif len(acceptableParentModules) > 1:
                            print 'WARNING: MULTIPLE NODES POSSIBLE FOR LINE:', line.strip()
                        elif parentModule != acceptableParentModules:
                            newLine = line[:match.start(1)] + list(acceptableParentModules)[0] + line[match.end(1):]
                        else:
                            print 'OH SNAP', parentModule
                elif 'import ' in line:
                    # Flag these as suspicious just so we can read the output and make sure we're not missing anything.
                    print 'SUSPICIOUS:', line.strip()
                    continue

                if foundImport and newLine != line:
                    print '>>>>>>>>> CHANGED:', line, \
                          '>>>>>>>>> TO:     ', newLine[:-1]
                    lines[lineIdx] = newLine
                    changedFile = True
                elif foundImport:
                    print 'UNCHANGED:', line.strip()

            if changedFile:
                with open(fullPath, 'w') as fout:
                    fout.write(''.join(lines))


def main():
    if len(sys.argv) != 2:
        print "USAGE: fix_globals.py <path/to/stamped>"
    namesToNodes = buildNamesToNodesMap(sys.argv[1])
    fixImports(sys.argv[1], namesToNodes)

if __name__ == '__main__':
    main()

