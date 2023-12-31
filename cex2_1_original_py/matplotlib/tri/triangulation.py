# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\tri\triangulation.pyc
# Compiled at: 2012-10-30 18:11:14
from __future__ import print_function
import matplotlib.delaunay as delaunay, matplotlib._tri as _tri, numpy as np

class Triangulation(object):
    """
    An unstructured triangular grid consisting of npoints points and
    ntri triangles.  The triangles can either be specified by the user
    or automatically generated using a Delaunay triangulation.

    Read-only attributes:

      *x*: array of shape (npoints).
        x-coordinates of grid points.

      *y*: array of shape (npoints).
        y-coordinates of grid points.

      *triangles*: integer array of shape (ntri,3).
        For each triangle, the indices of the three points that make
        up the triangle, ordered in an anticlockwise manner.

      *mask*: optional boolean array of shape (ntri).
        Which triangles are masked out.

      *edges*: integer array of shape (?,2).
        All edges of non-masked triangles.  Each edge is the start
        point index and end point index.  Each edge (start,end and
        end,start) appears only once.

      *neighbors*: integer array of shape (ntri,3).
        For each triangle, the indices of the three triangles that
        share the same edges, or -1 if there is no such neighboring
        triangle.  neighbors[i,j] is the triangle that is the neighbor
        to the edge from point index triangles[i,j] to point index
        triangles[i,(j+1)%3].
    """

    def __init__(self, x, y, triangles=None, mask=None):
        """
        Create a Triangulation object.

        The first two arguments must be:

        *x*, *y*: arrays of shape (npoints).
          Point coordinates.

        Optional arguments (args or keyword args):

        *triangles*: integer array of shape (ntri,3).
          For each triangle, the indices of the three points that make
          up the triangle.  If the points are ordered in a clockwise
          manner, they are converted to anticlockwise.

          If not specified, matplotlib.delaunay is used to create a
          Delaunay triangulation of the points.

        *mask*: optional boolean array of shape (ntri).
          Which triangles are masked out.
        """
        self.x = np.asarray(x, dtype=np.float64)
        self.y = np.asarray(y, dtype=np.float64)
        if self.x.shape != self.y.shape or len(self.x.shape) != 1:
            raise ValueError('x and y must be equal-length 1-D arrays')
        self.mask = None
        self._edges = None
        self._neighbors = None
        if triangles is None:
            dt = delaunay.Triangulation(self.x, self.y)
            self.triangles = np.asarray(dt.to_client_point_indices(dt.triangle_nodes), dtype=np.int32)
            if mask is None:
                self._edges = np.asarray(dt.to_client_point_indices(dt.edge_db), dtype=np.int32)
                neighbors = np.asarray(dt.triangle_neighbors, dtype=np.int32)
                self._neighbors = np.roll(neighbors, 1, axis=1)
        else:
            self.triangles = np.asarray(triangles, dtype=np.int32)
            if self.triangles.ndim != 2 or self.triangles.shape[1] != 3:
                raise ValueError('triangles must be a (?,3) array')
            if self.triangles.max() >= len(self.x):
                raise ValueError('triangles max element is out of bounds')
            if self.triangles.min() < 0:
                raise ValueError('triangles min element is out of bounds')
        if mask is not None:
            self.mask = np.asarray(mask, dtype=np.bool)
            if len(self.mask.shape) != 1 or self.mask.shape[0] != self.triangles.shape[0]:
                raise ValueError('mask array must have same length as triangles array')
        self._cpp_triangulation = None
        return

    @property
    def edges(self):
        if self._edges is None:
            self._edges = self.get_cpp_triangulation().get_edges()
        return self._edges

    def get_cpp_triangulation(self):
        """
        Return the underlying C++ Triangulation object, creating it
        if necessary.
        """
        if self._cpp_triangulation is None:
            self._cpp_triangulation = _tri.Triangulation(self.x, self.y, self.triangles, self.mask, self._edges, self._neighbors)
        return self._cpp_triangulation

    def get_masked_triangles(self):
        """
        Return an array of triangles that are not masked.
        """
        if self.mask is not None:
            return self.triangles.compress(1 - self.mask, axis=0)
        else:
            return self.triangles
            return

    @staticmethod
    def get_from_args_and_kwargs(*args, **kwargs):
        """
        Return a Triangulation object from the args and kwargs, and
        the remaining args and kwargs with the consumed values removed.

        There are two alternatives: either the first argument is a
        Triangulation object, in which case it is returned, or the args
        and kwargs are sufficient to create a new Triangulation to
        return.  In the latter case, see Triangulation.__init__ for
        the possible args and kwargs.
        """
        if isinstance(args[0], Triangulation):
            triangulation = args[0]
            args = args[1:]
        else:
            x = args[0]
            y = args[1]
            args = args[2:]
            triangles = kwargs.pop('triangles', None)
            from_args = False
            if triangles is None and len(args) > 0:
                triangles = args[0]
                from_args = True
            if triangles is not None:
                try:
                    triangles = np.asarray(triangles, dtype=np.int32)
                except ValueError:
                    triangles = None

            if triangles is not None and (triangles.ndim != 2 or triangles.shape[1] != 3):
                triangles = None
            if triangles is not None and from_args:
                args = args[1:]
            mask = kwargs.pop('mask', None)
            triangulation = Triangulation(x, y, triangles, mask)
        return (
         triangulation, args, kwargs)

    @property
    def neighbors(self):
        if self._neighbors is None:
            self._neighbors = self.get_cpp_triangulation().get_neighbors()
        return self._neighbors

    def set_mask(self, mask):
        """
        Set or clear the mask array.  This is either None, or a boolean
        array of shape (ntri).
        """
        if mask is None:
            self.mask = None
        else:
            self.mask = np.asarray(mask, dtype=np.bool)
            if len(self.mask.shape) != 1 or self.mask.shape[0] != self.triangles.shape[0]:
                raise ValueError('mask array must have same length as triangles array')
        if self._cpp_triangulation is not None:
            self._cpp_triangulation.set_mask(self.mask)
        self._edges = None
        self._neighbors = None
        return