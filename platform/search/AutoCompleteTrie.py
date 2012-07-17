#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = ['AutoCompleteTrie']

import Globals
from collections import defaultdict

class Node(object):
    __slots__ = ['data', 'children']

    def __init__(self):
        self.data = []
        self.children = defaultdict(Node)

    def add(self, key, data):
        if key:
            self.children[key[0]].add(key[1:], data)
        else:
            self.data.append(data)

    def get(self, key):
        if not key:
            return self.data
        if key[0] in self.children:
            return self.children[key[0]].get(key[1:])
        return []

    def compress(self):
        compressedChildren = {}
        for k, child in self.children.iteritems():
            prefix, node = child.compress()
            compressedChildren[k+prefix] = node
        if len(self.children) == 1 and not self.data:
            return compressedChildren.items()[0]
        return '', CompressedNode(self.data, compressedChildren)


class CompressedNode(object):
    __slots__ = ['data', 'children']

    def __init__(self, data, children):
        self.data = data
        self.children = children.items()

    def __getstate__(self):
        return self.data, self.children

    def __setstate__(self, (data, children)):
        self.data = data
        self.children = children

    def __iter__(self):
        yield '', self.data
        for k, child in self.children:
            for k2, data in child:
                yield k + k2, data

    def __len__(self):
        return sum(len(child) for k, child in self.children) + 1

    def add(self, key, data):
        raise NotImplemented

    def get(self, key):
        if not key:
            return self.data
        for k, child in self.children:
            if key.startswith(k) or k.startswith(key):
                return child.get(key[len(k):])
        return []

    def applyScoringFn(self, scoringFn, nodeLimit):
        uniqueData = set(self.data)
        for k, child in self.children:
            child.applyScoringFn(scoringFn, nodeLimit)
            uniqueData.update(child.data)
        dataList = list(uniqueData)
        dataList.sort(key=scoringFn, reverse=True)
        self.data = dataList[:nodeLimit]

    def modify(self, mutation):
        self.data = map(mutation, self.data)
        for k, child in self.children:
            child.modify(mutation)

    def prune(self, collapseThreshold):
        if len(self) < collapseThreshold:
            return PrunedLeaf(self)
        self.children = [(k, child.prune(collapseThreshold)) for k, child in self.children]
        return self


class PrunedLeaf(object):
    __slots__ = ['children']

    def __init__(self, node):
        self.children = list(node)

    def __getstate__(self):
        return self.children

    def __setstate__(self, children):
        self.children = children

    def get(self, key):
        for k, data in self.children:
            if k.startswith(key):
                return data
        return []

    def modify(self, mutation):
        self.children = [(k, map(mutation, data)) for k, data in self.children]


class AutoCompleteTrie(object):
    def __init__(self):
        self.root = Node()

    def addBinding(self, key, data):
        self.root.add(key, data)

    def __getitem__(self, key):
        return self.root.get(key)

    def pruneAndCompress(self, scoringFn, nodeLimit, collapseThreshold):
        prefix, node = self.root.compress()
        if prefix:
            self.root = CompressedNode(None, {prefix : node})
        else:
            self.root = node
        self.root.applyScoringFn(scoringFn, nodeLimit)
        self.root = self.root.prune(collapseThreshold)

    def modify(self, mutation):
        self.root.modify(mutation)
