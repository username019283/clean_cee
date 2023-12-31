# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\spatial\__init__.pyc
# Compiled at: 2013-02-16 13:27:32
"""
=============================================================
Spatial algorithms and data structures (:mod:`scipy.spatial`)
=============================================================

Nearest-neighbor Queries
========================
.. autosummary::
   :toctree: generated/

   KDTree - *Class* for efficient nearest-neighbor queries
   cKDTree     -- class for efficient nearest-neighbor queries (faster impl.)
   distance - *Module* containing many different distance measures

Delaunay Triangulation, Convex Hulls and Voronoi Diagrams
=========================================================

.. autosummary::
   :toctree: generated/

   Delaunay    -- compute Delaunay triangulation of input points
   ConvexHull  -- compute a convex hull for input points
   Voronoi     -- compute a Voronoi diagram hull from input points

Plotting Helpers
================

.. autosummary::
   :toctree: generated/

   delaunay_plot_2d     -- plot 2-D triangulation
   convex_hull_plot_2d  -- plot 2-D convex hull
   voronoi_plot_2d      -- plot 2-D voronoi diagram

.. seealso:: :ref:`Tutorial <qhulltutorial>`

Simplex representation
======================
The simplices (triangles, tetrahedra, ...) appearing in the Delaunay
tesselation (N-dim simplices), convex hull facets, and Voronoi ridges
(N-1 dim simplices) are represented in the following scheme::

    tess = Delaunay(points)
    hull = ConvexHull(points)
    voro = Voronoi(points)

    # coordinates of the j-th vertex of the i-th simplex
    tess.points[tess.simplices[i, j], :]        # tesselation element
    hull.points[hull.simplices[i, j], :]        # convex hull facet
    voro.vertices[voro.ridge_vertices[i, j], :] # ridge between Voronoi cells

For Delaunay triangulations and convex hulls, the neighborhood
structure of the simplices satisfies the condition:

    ``tess.neighbors[i,j]`` is the neighboring simplex of the i-th
    simplex, opposite to the j-vertex. It is -1 in case of no
    neighbor.

Convex hull facets also define a hyperplane equation:

    (hull.equations[i,:-1] * coord).sum() + hull.equations[i,-1] == 0

Similar hyperplane equations for the Delaunay triangulation correspond
to the convex hull facets on the corresponding N+1 dimensional
paraboloid.

The Delaunay triangulation objects offer a method for locating the
simplex containing a given point, and barycentric coordinate
computations.

Functions
---------

.. autosummary::
   :toctree: generated/

   tsearch
   distance_matrix
   minkowski_distance
   minkowski_distance_p

"""
from __future__ import division, print_function, absolute_import
from ...kdtree import *
from ...ckdtree import *
from ...qhull import *
from ..._plotutils import *
__all__ = [ s for s in dir() if not s.startswith('_') ]
__all__ += ['distance']
from . import distance
from numpy.testing import Tester
test = Tester().test
bench = Tester().bench