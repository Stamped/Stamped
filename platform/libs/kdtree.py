#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

def get_squared_dist(p0, p1):
    return sum((p0[i] - p1[i]) ** 2 for i in xrange(len(p0)))

class _KDTreeNode():
    def __init__(self, data, left, right):
        self.data  = data
        self.left  = left
        self.right = right
    
    def is_leaf(self):
        return (self.left == None and self.right == None)

class _NearestNeighbors():
    """ Internal structure used in nearest-neighbours search """
    
    def __init__(self, query_point, k, dist_func=get_squared_dist):
        self.query_point    = query_point
        self.k              = k # neighbours wanted
        self.largest_dist   = 0 # squared
        self._dist_func     = dist_func
        
        # TODO: use max heap for current_best!
        self.current_best   = []
    
    def calculate_largest(self):
        if self.k >= len(self.current_best):
            self.largest_dist = self.current_best[-1][1]
        else:
            self.largest_dist = self.current_best[self.k - 1][1]
    
    def add(self, data):
        sd = self._dist_func(data[0], self.query_point)
        
        # run through current_best, try to find appropriate place
        for i, e in enumerate(self.current_best):
            if i == self.k:
                return
            
            if e[1] > sd:
                self.current_best.insert(i, [data, sd])
                self.calculate_largest()
                return
        
        # append it to the end otherwise
        self.current_best.append([data, sd])
        self.calculate_largest()
    
    def get_best(self):
        return [element[0] for element in self.current_best[:self.k]]

class KDTree():
    """ KDTree implementation.
    
        Example usage:
        
            from libs.kdtree import KDTree
            
            data    = <load data> # iterable of tuples, with tuple[0] being 
                                  # itself a coordinate tuple, and tuple[1] 
                                  # being any arbitrary data.
            point   = <the point of which neighbours we're looking for>
            
            tree    = KDTree(data)
            nearest = tree.query(point, k=4) # find nearest 4 points
    """
    
    def __init__(self, data, dist_func=None):
        self._dist_func = dist_func if dist_func else get_squared_dist
        
        def build_kdtree(objects, depth):
            # code based on wikipedia article: http://en.wikipedia.org/wiki/Kd-tree
            if not objects:
                return None

            # select axis based on depth so that axis cycles through all valid values
            axis = depth % len(objects[0][0]) # assumes all points have the same dimension
            
            # sort object list and choose median as pivot point,
            # TODO: better selection method, linear-time selection, distribution
            objects.sort(key=lambda obj: obj[0][axis])
            median = len(objects) / 2 # choose median
            
            # create node and recursively construct subtrees
            return _KDTreeNode(data=objects[median],
                               left=build_kdtree(objects[0:median], depth+1),
                               right=build_kdtree(objects[median+1:], depth+1))
        
        self.root_node = build_kdtree(data, depth=0)
    
    def query(self, query_point, k=1):
        def _nn_search(node, query_point, k, depth, neighbors):
            if node == None:
                return
            
            # stop recursion if we've reached a leaf node
            if node.is_leaf():
                neighbors.add(node.data)
                return
            
            # select dimension for comparison (based on current depth)
            axis = depth % len(query_point)
            
            # figure out which subtree(s) to search
            near_subtree = None
            far_subtree  = None
            node_axis    = node.data[0][axis]
            
            # compare query_point and point of current node in selected dimension
            # and figure out which subtree is farther than the other
            if query_point[axis] < node_axis:
                near_subtree = node.left
                far_subtree  = node.right
            else:
                near_subtree = node.right
                far_subtree  = node.left
            
            # recursively search through the tree until a leaf is found
            _nn_search(near_subtree, query_point, k, depth + 1, neighbors)
            
            # while unwinding the recursion, check if the current node
            # is closer to query point than the current best,
            # also, until k points have been found, search radius is infinity
            neighbors.add(node.data)
            
            # check whether there could be any points on the other side of the
            # splitting plane that are closer to the query point than the current best
            if (node_axis - query_point[axis]) ** 2 < neighbors.largest_dist:
                _nn_search(far_subtree, query_point, k, depth + 1, neighbors)
            
            return
        
        if self.root_node is None:
            return []
        
        neighbours = _NearestNeighbors(query_point, k, self._dist_func)
        _nn_search(self.root_node, query_point, k, depth=0, neighbors=neighbours)
        
        return neighbours.get_best()

if __name__ == '__main__':
    tree = KDTree([ ((1, 2), 'test0'), ((3, 4), 'test1'), ((0, 0), 'test2'), ((-7, 3), 'test3') ])
    print tree.query((0, -1), k=2)

