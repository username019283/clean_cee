# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\interpolate\ndgriddata.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Convenience interface to N-D interpolation

.. versionadded:: 0.9

"""
from __future__ import division, print_function, absolute_import
import numpy as np
from .interpnd import LinearNDInterpolator, NDInterpolatorBase, CloughTocher2DInterpolator, _ndim_coords_from_arrays
from scipy.spatial import cKDTree
__all__ = [
 'griddata', 'NearestNDInterpolator', 'LinearNDInterpolator',
 'CloughTocher2DInterpolator']

class NearestNDInterpolator(NDInterpolatorBase):
    """
    NearestNDInterpolator(points, values)

    Nearest-neighbour interpolation in N dimensions.

    .. versionadded:: 0.9

    Parameters
    ----------
    points : (Npoints, Ndims) ndarray of floats
        Data point coordinates.
    values : (Npoints,) ndarray of float or complex
        Data values.

    Notes
    -----
    Uses ``scipy.spatial.cKDTree``

    """

    def __init__(self, x, y):
        x = _ndim_coords_from_arrays(x)
        self._check_init_shape(x, y)
        self.tree = cKDTree(x)
        self.points = x
        self.values = y

    def __call__(self, *args):
        """
        Evaluate interpolator at given points.

        Parameters
        ----------
        xi : ndarray of float, shape (..., ndim)
            Points where to interpolate data at.

        """
        xi = _ndim_coords_from_arrays(args)
        xi = self._check_call_shape(xi)
        dist, i = self.tree.query(xi)
        return self.values[i]


def griddata(points, values, xi, method='linear', fill_value=np.nan):
    """
    Interpolate unstructured N-dimensional data.

    .. versionadded:: 0.9

    Parameters
    ----------
    points : ndarray of floats, shape (N, ndim)
        Data point coordinates. Can either be an array of
        size (N, ndim), or a tuple of `ndim` arrays.
    values : ndarray of float or complex, shape (N,)
        Data values.
    xi : ndarray of float, shape (M, ndim)
        Points at which to interpolate data.

    method : {'linear', 'nearest', 'cubic'}, optional
        Method of interpolation. One of

        ``nearest``: return the value at the data point closest to
          the point of interpolation.  See `NearestNDInterpolator` for
          more details.

        ``linear``: tesselate the input point set to n-dimensional
          simplices, and interpolate linearly on each simplex.  See
          `LinearNDInterpolator` for more details.

        ``cubic`` (1-D): return the value determined from a cubic
          spline.

        ``cubic`` (2-D): return the value determined from a
          piecewise cubic, continuously differentiable (C1), and
          approximately curvature-minimizing polynomial surface. See
          `CloughTocher2DInterpolator` for more details.

    fill_value : float, optional
        Value used to fill in for requested points outside of the
        convex hull of the input points.  If not provided, then the
        default is ``nan``. This option has no effect for the
        'nearest' method.

    Examples
    --------

    Suppose we want to interpolate the 2-D function

    >>> def func(x, y):
    >>>     return x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2

    on a grid in [0, 1]x[0, 1]

    >>> grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]

    but we only know its values at 1000 data points:

    >>> points = np.random.rand(1000, 2)
    >>> values = func(points[:,0], points[:,1])

    This can be done with `griddata` -- below we try out all of the
    interpolation methods:

    >>> from scipy.interpolate import griddata
    >>> grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    >>> grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    >>> grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')

    One can see that the exact result is reproduced by all of the
    methods to some degree, but for this smooth function the piecewise
    cubic interpolant gives the best results:

    >>> import matplotlib.pyplot as plt
    >>> plt.subplot(221)
    >>> plt.imshow(func(grid_x, grid_y).T, extent=(0,1,0,1), origin='lower')
    >>> plt.plot(points[:,0], points[:,1], 'k.', ms=1)
    >>> plt.title('Original')
    >>> plt.subplot(222)
    >>> plt.imshow(grid_z0.T, extent=(0,1,0,1), origin='lower')
    >>> plt.title('Nearest')
    >>> plt.subplot(223)
    >>> plt.imshow(grid_z1.T, extent=(0,1,0,1), origin='lower')
    >>> plt.title('Linear')
    >>> plt.subplot(224)
    >>> plt.imshow(grid_z2.T, extent=(0,1,0,1), origin='lower')
    >>> plt.title('Cubic')
    >>> plt.gcf().set_size_inches(6, 6)
    >>> plt.show()

    """
    points = _ndim_coords_from_arrays(points)
    if points.ndim < 2:
        ndim = points.ndim
    else:
        ndim = points.shape[-1]
    if ndim == 1 and method in ('nearest', 'linear', 'cubic'):
        from .interpolate import interp1d
        points = points.ravel()
        if isinstance(xi, tuple):
            if len(xi) != 1:
                raise ValueError('invalid number of dimensions in xi')
            xi, = xi
        idx = np.argsort(points)
        points = points[idx]
        values = values[idx]
        ip = interp1d(points, values, kind=method, axis=0, bounds_error=False, fill_value=fill_value)
        return ip(xi)
    if method == 'nearest':
        ip = NearestNDInterpolator(points, values)
        return ip(xi)
    if method == 'linear':
        ip = LinearNDInterpolator(points, values, fill_value=fill_value)
        return ip(xi)
    if method == 'cubic' and ndim == 2:
        ip = CloughTocher2DInterpolator(points, values, fill_value=fill_value)
        return ip(xi)
    raise ValueError('Unknown interpolation method %r for %d dimensional data' % (
     method, ndim))