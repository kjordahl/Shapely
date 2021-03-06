from itertools import islice
import unittest
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.ops import unary_union

def halton(base):
    """Returns an iterator over an infinite Halton sequence"""
    def value(index):
        result = 0.0
        f = 1.0/base
        i = index
        while i > 0:
            result += f * (i % base)
            i = i//base
            f = f/base
        return result
    i = 1
    while i > 0:
        yield value(i)
        i += 1

class UnionTestCase(unittest.TestCase):
    coords = zip(
        list(islice(halton(5), 20, 120)),
        list(islice(halton(7), 20, 120)) )

    def test_1(self):
        # Instead of random points, use deterministic, pseudo-random Halton
        # sequences for repeatability sake.
        coords = list(zip(
            list(islice(halton(5), 20, 120)),
            list(islice(halton(7), 20, 120)) ))
        patches = [Point(xy).buffer(0.05) for xy in coords]
        u = unary_union(patches)
        self.failUnlessEqual(u.geom_type, 'MultiPolygon')
        self.failUnlessAlmostEqual(u.area, 0.71857254056)

    def test_multi(self):
        # Test of multipart input based on comment by @schwehr at
        # https://github.com/Toblerity/Shapely/issues/47#issuecomment-21809308
        patches = MultiPolygon([Point(xy).buffer(0.05) for xy in self.coords])
        self.failUnlessAlmostEqual(unary_union(patches).area, 0.71857254056)
        self.failUnlessAlmostEqual(unary_union([patches, patches]).area, 0.71857254056)

def test_suite():
    try:
        patches = [Point((0, 0)).buffer(0.05)]
        unary_union(patches)
    except KeyError:
        return lambda x: None
    return unittest.TestLoader().loadTestsFromTestCase(UnionTestCase)
