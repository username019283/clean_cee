# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\interpolate\fitpack2.pyc
# Compiled at: 2013-02-16 13:27:30
"""
fitpack --- curve and surface fitting with splines

fitpack is based on a collection of Fortran routines DIERCKX
by P. Dierckx (see http://www.netlib.org/dierckx/) transformed
to double routines by Pearu Peterson.
"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'UnivariateSpline', 
 'InterpolatedUnivariateSpline', 
 'LSQUnivariateSpline', 
 'BivariateSpline', 
 'LSQBivariateSpline', 
 'SmoothBivariateSpline', 
 'LSQSphereBivariateSpline', 
 'SmoothSphereBivariateSpline', 
 'RectBivariateSpline', 
 'RectSphereBivariateSpline']
import warnings
from numpy import zeros, concatenate, alltrue, ravel, all, diff, array, ones
import numpy as np
from . import fitpack
from . import dfitpack
_curfit_messages = {1: '\nThe required storage space exceeds the available storage space, as\nspecified by the parameter nest: nest too small. If nest is already\nlarge (say nest > m/2), it may also indicate that s is too small.\nThe approximation returned is the weighted least-squares spline\naccording to the knots t[0],t[1],...,t[n-1]. (n=nest) the parameter fp\ngives the corresponding weighted sum of squared residuals (fp>s).\n', 
   2: '\nA theoretically impossible result was found during the iteration\nproces for finding a smoothing spline with fp = s: s too small.\nThere is an approximation returned but the corresponding weighted sum\nof squared residuals does not satisfy the condition abs(fp-s)/s < tol.', 
   3: '\nThe maximal number of iterations maxit (set to 20 by the program)\nallowed for finding a smoothing spline with fp=s has been reached: s\ntoo small.\nThere is an approximation returned but the corresponding weighted sum\nof squared residuals does not satisfy the condition abs(fp-s)/s < tol.', 
   10: '\nError on entry, no approximation returned. The following conditions\nmust hold:\nxb<=x[0]<x[1]<...<x[m-1]<=xe, w[i]>0, i=0..m-1\nif iopt=-1:\n  xb<t[k+1]<t[k+2]<...<t[n-k-2]<xe'}

class UnivariateSpline(object):
    """
    One-dimensional smoothing spline fit to a given set of data points.

    Fits a spline y=s(x) of degree `k` to the provided `x`, `y` data.  `s`
    specifies the number of knots by specifying a smoothing condition.

    Parameters
    ----------
    x : (N,) array_like
        1-D array of independent input data. Must be increasing.
    y : (N,) array_like
        1-D array of dependent input data, of the same length as `x`.
    w : (N,) array_like, optional
        Weights for spline fitting.  Must be positive.  If None (default),
        weights are all equal.
    bbox : (2,) array_like, optional
        2-sequence specifying the boundary of the approximation interval. If
        None (default), ``bbox=[x[0], x[-1]]``.
    k : int, optional
        Degree of the smoothing spline.  Must be <= 5.
    s : float or None, optional
        Positive smoothing factor used to choose the number of knots.  Number
        of knots will be increased until the smoothing condition is satisfied:

        sum((w[i]*(y[i]-s(x[i])))**2,axis=0) <= s

        If None (default), s=len(w) which should be a good value if 1/w[i] is
        an estimate of the standard deviation of y[i].  If 0, spline will
        interpolate through all data points.

    See Also
    --------
    InterpolatedUnivariateSpline : Subclass with smoothing forced to 0
    LSQUnivariateSpline : Subclass in which knots are user-selected instead of
        being set by smoothing condition
    splrep : An older, non object-oriented wrapping of FITPACK
    splev, sproot, splint, spalde
    BivariateSpline : A similar class for two-dimensional spline interpolation

    Notes
    -----
    The number of data points must be larger than the spline degree `k`.

    Examples
    --------
    >>> from numpy import linspace,exp
    >>> from numpy.random import randn
    >>> from scipy.interpolate import UnivariateSpline
    >>> x = linspace(-3, 3, 100)
    >>> y = exp(-x**2) + randn(100)/10
    >>> s = UnivariateSpline(x, y, s=1)
    >>> xs = linspace(-3, 3, 1000)
    >>> ys = s(xs)

    xs,ys is now a smoothed, super-sampled version of the noisy gaussian x,y.

    """

    def __init__(self, x, y, w=None, bbox=[None] * 2, k=3, s=None):
        """
        Input:
          x,y   - 1-d sequences of data points (x must be
                  in strictly ascending order)

        Optional input:
          w          - positive 1-d sequence of weights
          bbox       - 2-sequence specifying the boundary of
                       the approximation interval.
                       By default, bbox=[x[0],x[-1]]
          k=3        - degree of the univariate spline.
          s          - positive smoothing factor defined for
                       estimation condition:
                         sum((w[i]*(y[i]-s(x[i])))**2,axis=0) <= s
                       Default s=len(w) which should be a good value
                       if 1/w[i] is an estimate of the standard
                       deviation of y[i].
        """
        data = dfitpack.fpcurf0(x, y, k, w=w, xb=bbox[0], xe=bbox[1], s=s)
        if data[-1] == 1:
            data = self._reset_nest(data)
        self._data = data
        self._reset_class()

    def _reset_class(self):
        data = self._data
        n, t, c, k, ier = (data[7], data[8], data[9], data[5], data[-1])
        self._eval_args = (t[:n], c[:n], k)
        if ier == 0:
            pass
        elif ier == -1:
            self._set_class(InterpolatedUnivariateSpline)
        elif ier == -2:
            self._set_class(LSQUnivariateSpline)
        else:
            if ier == 1:
                self._set_class(LSQUnivariateSpline)
            message = _curfit_messages.get(ier, 'ier=%s' % ier)
            warnings.warn(message)

    def _set_class(self, cls):
        self._spline_class = cls
        if self.__class__ in (UnivariateSpline, InterpolatedUnivariateSpline,
         LSQUnivariateSpline):
            self.__class__ = cls

    def _reset_nest(self, data, nest=None):
        n = data[10]
        if nest is None:
            k, m = data[5], len(data[0])
            nest = m + k + 1
        elif not n <= nest:
            raise ValueError('`nest` can only be increased')
        t, c, fpint, nrdata = [ np.resize(data[n], nest) for n in [8, 9, 11, 12] ]
        args = data[:8] + (t, c, n, fpint, nrdata, data[13])
        data = dfitpack.fpcurf1(*args)
        return data

    def set_smoothing_factor(self, s):
        """ Continue spline computation with the given smoothing
        factor s and with the knots found at the last call.

        """
        data = self._data
        if data[6] == -1:
            warnings.warn('smoothing factor unchanged forLSQ spline with fixed knots')
            return
        args = data[:6] + (s,) + data[7:]
        data = dfitpack.fpcurf1(*args)
        if data[-1] == 1:
            data = self._reset_nest(data)
        self._data = data
        self._reset_class()

    def __call__(self, x, nu=0):
        """ Evaluate spline (or its nu-th derivative) at positions x.

        Note: x can be unordered but the evaluation is more efficient
        if x is (partially) ordered.
        """
        x = np.asarray(x)
        if x.size == 0:
            return array([])
        return fitpack.splev(x, self._eval_args, der=nu)

    def get_knots(self):
        """ Return positions of (boundary and interior) knots of the spline.
        """
        data = self._data
        k, n = data[5], data[7]
        return data[8][k:n - k]

    def get_coeffs(self):
        """Return spline coefficients."""
        data = self._data
        k, n = data[5], data[7]
        return data[9][:n - k - 1]

    def get_residual(self):
        """Return weighted sum of squared residuals of the spline
        approximation: ``sum((w[i] * (y[i]-s(x[i])))**2, axis=0)``.
        """
        return self._data[10]

    def integral(self, a, b):
        """ Return definite integral of the spline between two given points.
        """
        return dfitpack.splint(*(self._eval_args + (a, b)))

    def derivatives(self, x):
        """ Return all derivatives of the spline at the point x."""
        d, ier = dfitpack.spalde(*(self._eval_args + (x,)))
        if not ier == 0:
            raise ValueError('Error code returned by spalde: %s' % ier)
        return d

    def roots(self):
        """ Return the zeros of the spline.

        Restriction: only cubic splines are supported by fitpack.
        """
        k = self._data[5]
        if k == 3:
            z, m, ier = dfitpack.sproot(*self._eval_args[:2])
            if not ier == 0:
                raise ValueError('Error code returned by spalde: %s' % ier)
            return z[:m]
        raise NotImplementedError('finding roots unsupported for non-cubic splines')


class InterpolatedUnivariateSpline(UnivariateSpline):
    """
    One-dimensional interpolating spline for a given set of data points.

    Fits a spline y=s(x) of degree `k` to the provided `x`, `y` data. Spline
    function passes through all provided points. Equivalent to
    `UnivariateSpline` with  s=0.

    Parameters
    ----------
    x : (N,) array_like
        Input dimension of data points -- must be increasing
    y : (N,) array_like
        input dimension of data points
    w : (N,) array_like, optional
        Weights for spline fitting.  Must be positive.  If None (default),
        weights are all equal.
    bbox : (2,) array_like, optional
        2-sequence specifying the boundary of the approximation interval. If
        None (default), bbox=[x[0],x[-1]].
    k : int, optional
        Degree of the smoothing spline.  Must be 1 <= `k` <= 5.

    See Also
    --------
    UnivariateSpline : Superclass -- allows knots to be selected by a
        smoothing condition
    LSQUnivariateSpline : spline for which knots are user-selected
    splrep : An older, non object-oriented wrapping of FITPACK
    splev, sproot, splint, spalde
    BivariateSpline : A similar class for two-dimensional spline interpolation

    Notes
    -----
    The number of data points must be larger than the spline degree `k`.

    Examples
    --------
    >>> from numpy import linspace,exp
    >>> from numpy.random import randn
    >>> from scipy.interpolate import InterpolatedUnivariateSpline
    >>> x = linspace(-3, 3, 100)
    >>> y = exp(-x**2) + randn(100)/10
    >>> s = InterpolatedUnivariateSpline(x, y)
    >>> xs = linspace(-3, 3, 1000)
    >>> ys = s(xs)

    xs,ys is now a smoothed, super-sampled version of the noisy gaussian x,y

    """

    def __init__(self, x, y, w=None, bbox=[None] * 2, k=3):
        """
        Input:
          x,y   - 1-d sequences of data points (x must be
                  in strictly ascending order)

        Optional input:
          w          - positive 1-d sequence of weights
          bbox       - 2-sequence specifying the boundary of
                       the approximation interval.
                       By default, bbox=[x[0],x[-1]]
          k=3        - degree of the univariate spline.
        """
        self._data = dfitpack.fpcurf0(x, y, k, w=w, xb=bbox[0], xe=bbox[1], s=0)
        self._reset_class()


class LSQUnivariateSpline(UnivariateSpline):
    """
    One-dimensional spline with explicit internal knots.

    Fits a spline y=s(x) of degree `k` to the provided `x`, `y` data.  `t`
    specifies the internal knots of the spline

    Parameters
    ----------
    x : (N,) array_like
        Input dimension of data points -- must be increasing
    y : (N,) array_like
        Input dimension of data points
    t: (M,) array_like
        interior knots of the spline.  Must be in ascending order
        and bbox[0]<t[0]<...<t[-1]<bbox[-1]
    w : (N,) array_like, optional
        weights for spline fitting.  Must be positive.  If None (default),
        weights are all equal.
    bbox : (2,) array_like, optional
        2-sequence specifying the boundary of the approximation interval. If
        None (default), bbox=[x[0],x[-1]].
    k : int, optional
        Degree of the smoothing spline.  Must be 1 <= `k` <= 5.

    Raises
    ------
    ValueError
        If the interior knots do not satisfy the Schoenberg-Whitney conditions

    See Also
    --------
    UnivariateSpline : Superclass -- knots are specified by setting a
        smoothing condition
    InterpolatedUnivariateSpline : spline passing through all points
    splrep : An older, non object-oriented wrapping of FITPACK
    splev, sproot, splint, spalde
    BivariateSpline : A similar class for two-dimensional spline interpolation

    Notes
    -----
    The number of data points must be larger than the spline degree `k`.

    Examples
    --------
    >>> from numpy import linspace,exp
    >>> from numpy.random import randn
    >>> from scipy.interpolate import LSQUnivariateSpline
    >>> x = linspace(-3,3,100)
    >>> y = exp(-x**2) + randn(100)/10
    >>> t = [-1,0,1]
    >>> s = LSQUnivariateSpline(x,y,t)
    >>> xs = linspace(-3,3,1000)
    >>> ys = s(xs)

    xs,ys is now a smoothed, super-sampled version of the noisy gaussian x,y
    with knots [-3,-1,0,1,3]

    """

    def __init__(self, x, y, t, w=None, bbox=[None] * 2, k=3):
        """
        Input:
          x,y   - 1-d sequences of data points (x must be
                  in strictly ascending order)
          t     - 1-d sequence of the positions of user-defined
                  interior knots of the spline (t must be in strictly
                  ascending order and bbox[0]<t[0]<...<t[-1]<bbox[-1])

        Optional input:
          w          - positive 1-d sequence of weights
          bbox       - 2-sequence specifying the boundary of
                       the approximation interval.
                       By default, bbox=[x[0],x[-1]]
          k=3        - degree of the univariate spline.
        """
        xb = bbox[0]
        xe = bbox[1]
        if xb is None:
            xb = x[0]
        if xe is None:
            xe = x[-1]
        t = concatenate(([xb] * (k + 1), t, [xe] * (k + 1)))
        n = len(t)
        if not alltrue(t[k + 1:n - k] - t[k:n - k - 1] > 0, axis=0):
            raise ValueError('Interior knots t must satisfy Schoenberg-Whitney conditions')
        data = dfitpack.fpcurfm1(x, y, k, t, w=w, xb=xb, xe=xe)
        self._data = data[:-3] + (None, None, data[-1])
        self._reset_class()
        return


class _BivariateSplineBase(object):
    """ Base class for Bivariate spline s(x,y) interpolation on the rectangle
    [xb,xe] x [yb, ye] calculated from a given set of data points
    (x,y,z).

    See Also
    --------
    bisplrep, bisplev : an older wrapping of FITPACK
    BivariateSpline :
        implementation of bivariate spline interpolation on a plane grid
    SphereBivariateSpline :
        implementation of bivariate spline interpolation on a spherical grid
    """

    def get_residual(self):
        """ Return weighted sum of squared residuals of the spline
        approximation: sum ((w[i]*(z[i]-s(x[i],y[i])))**2,axis=0)
        """
        return self.fp

    def get_knots(self):
        """ Return a tuple (tx,ty) where tx,ty contain knots positions
        of the spline with respect to x-, y-variable, respectively.
        The position of interior and additional knots are given as
          t[k+1:-k-1] and t[:k+1]=b, t[-k-1:]=e, respectively.
        """
        return self.tck[:2]

    def get_coeffs(self):
        """ Return spline coefficients."""
        return self.tck[2]


_surfit_messages = {1: '\nThe required storage space exceeds the available storage space: nxest\nor nyest too small, or s too small.\nThe weighted least-squares spline corresponds to the current set of\nknots.', 
   2: '\nA theoretically impossible result was found during the iteration\nprocess for finding a smoothing spline with fp = s: s too small or\nbadly chosen eps.\nWeighted sum of squared residuals does not satisfy abs(fp-s)/s < tol.', 
   3: '\nthe maximal number of iterations maxit (set to 20 by the program)\nallowed for finding a smoothing spline with fp=s has been reached:\ns too small.\nWeighted sum of squared residuals does not satisfy abs(fp-s)/s < tol.', 
   4: '\nNo more knots can be added because the number of b-spline coefficients\n(nx-kx-1)*(ny-ky-1) already exceeds the number of data points m:\neither s or m too small.\nThe weighted least-squares spline corresponds to the current set of\nknots.', 
   5: '\nNo more knots can be added because the additional knot would (quasi)\ncoincide with an old one: s too small or too large a weight to an\ninaccurate data point.\nThe weighted least-squares spline corresponds to the current set of\nknots.', 
   10: '\nError on entry, no approximation returned. The following conditions\nmust hold:\nxb<=x[i]<=xe, yb<=y[i]<=ye, w[i]>0, i=0..m-1\nIf iopt==-1, then\n  xb<tx[kx+1]<tx[kx+2]<...<tx[nx-kx-2]<xe\n  yb<ty[ky+1]<ty[ky+2]<...<ty[ny-ky-2]<ye', 
   -3: '\nThe coefficients of the spline returned have been computed as the\nminimal norm least-squares solution of a (numerically) rank deficient\nsystem (deficiency=%i). If deficiency is large, the results may be\ninaccurate. Deficiency may strongly depend on the value of eps.'}

class BivariateSpline(_BivariateSplineBase):
    """
    Base class for bivariate splines.

    This describes a spline ``s(x, y)`` of degrees ``kx`` and ``ky`` on
    the rectangle ``[xb, xe] * [yb, ye]`` calculated from a given set
    of data points ``(x, y, z)``.

    To construct these splines, call either `SmoothBivariateSpline` or
    `LSQBivariateSpline`.

    See Also
    --------
    UnivariateSpline : a similar class for univariate spline interpolation
    SmoothBivariateSpline :
        to create a BivariateSpline through the given points
    LSQBivariateSpline :
        to create a BivariateSpline using weighted least-squares fitting
    SphereBivariateSpline :
        bivariate spline interpolation in spherical cooridinates
    bisplrep : older wrapping of FITPACK
    bisplev : older wrapping of FITPACK

    """

    def __call__(self, x, y, mth='array'):
        """ Evaluate spline at the grid points defined by the coordinate arrays
        x,y."""
        x = np.asarray(x)
        y = np.asarray(y)
        if x.size == 0 and y.size == 0:
            return array([])
        if mth == 'array':
            tx, ty, c = self.tck[:3]
            kx, ky = self.degrees
            z, ier = dfitpack.bispev(tx, ty, c, kx, ky, x, y)
            if not ier == 0:
                raise ValueError('Error code returned by bispev: %s' % ier)
            return z
        raise NotImplementedError('unknown method mth=%s' % mth)

    def ev(self, xi, yi):
        """
        Evaluate spline at points (x[i], y[i]), i=0,...,len(x)-1
        """
        tx, ty, c = self.tck[:3]
        kx, ky = self.degrees
        zi, ier = dfitpack.bispeu(tx, ty, c, kx, ky, xi, yi)
        if not ier == 0:
            raise ValueError('Error code returned by bispeu: %s' % ier)
        return zi

    def integral(self, xa, xb, ya, yb):
        """
        Evaluate the integral of the spline over area [xa,xb] x [ya,yb].

        Parameters
        ----------
        xa, xb : float
            The end-points of the x integration interval.
        ya, yb : float
            The end-points of the y integration interval.

        Returns
        -------
        integ : float
            The value of the resulting integral.

        """
        tx, ty, c = self.tck[:3]
        kx, ky = self.degrees
        return dfitpack.dblint(tx, ty, c, kx, ky, xa, xb, ya, yb)


class SmoothBivariateSpline(BivariateSpline):
    """
    Smooth bivariate spline approximation.

    Parameters
    ----------
    x, y, z : array_like
        1-D sequences of data points (order is not important).
    w : array_like, optional
        Positive 1-D sequence of weights, of same length as `x`, `y` and `z`.
    bbox : array_like, optional
        Sequence of length 4 specifying the boundary of the rectangular
        approximation domain.  By default,
        ``bbox=[min(x,tx),max(x,tx), min(y,ty),max(y,ty)]``.
    kx, ky : ints, optional
        Degrees of the bivariate spline. Default is 3.
    s : float, optional
        Positive smoothing factor defined for estimation condition:
        ``sum((w[i]*(z[i]-s(x[i], y[i])))**2, axis=0) <= s``
        Default ``s=len(w)`` which should be a good value if ``1/w[i]`` is an
        estimate of the standard deviation of ``z[i]``.
    eps : float, optional
        A threshold for determining the effective rank of an over-determined
        linear system of equations. `eps` should have a value between 0 and 1,
        the default is 1e-16.

    See Also
    --------
    bisplrep : an older wrapping of FITPACK
    bisplev : an older wrapping of FITPACK
    UnivariateSpline : a similar class for univariate spline interpolation
    LSQUnivariateSpline : to create a BivariateSpline using weighted

    Notes
    -----
    The length of `x`, `y` and `z` should be at least ``(kx+1) * (ky+1)``.

    """

    def __init__(self, x, y, z, w=None, bbox=[None] * 4, kx=3, ky=3, s=None, eps=None):
        xb, xe, yb, ye = bbox
        nx, tx, ny, ty, c, fp, wrk1, ier = dfitpack.surfit_smth(x, y, z, w, xb, xe, yb, ye, kx, ky, s=s, eps=eps, lwrk2=1)
        if ier in (0, -1, -2):
            pass
        else:
            message = _surfit_messages.get(ier, 'ier=%s' % ier)
            warnings.warn(message)
        self.fp = fp
        self.tck = (tx[:nx], ty[:ny], c[:(nx - kx - 1) * (ny - ky - 1)])
        self.degrees = (kx, ky)


class LSQBivariateSpline(BivariateSpline):
    """
    Weighted least-squares bivariate spline approximation.

    Parameters
    ----------
    x, y, z : array_like
        1-D sequences of data points (order is not important).
    tx, ty : array_like
        Strictly ordered 1-D sequences of knots coordinates.
    w : array_like, optional
        Positive 1-D array of weights, of the same length as `x`, `y` and `z`.
    bbox : (4,) array_like, optional
        Sequence of length 4 specifying the boundary of the rectangular
        approximation domain.  By default,
        ``bbox=[min(x,tx),max(x,tx), min(y,ty),max(y,ty)]``.
    kx, ky : ints, optional
        Degrees of the bivariate spline. Default is 3.
    s : float, optional
        Positive smoothing factor defined for estimation condition:
        ``sum((w[i]*(z[i]-s(x[i], y[i])))**2, axis=0) <= s``
        Default ``s=len(w)`` which should be a good value if ``1/w[i]`` is an
        estimate of the standard deviation of ``z[i]``.
    eps : float, optional
        A threshold for determining the effective rank of an over-determined
        linear system of equations. `eps` should have a value between 0 and 1,
        the default is 1e-16.

    See Also
    --------
    bisplrep : an older wrapping of FITPACK
    bisplev : an older wrapping of FITPACK
    UnivariateSpline : a similar class for univariate spline interpolation
    SmoothBivariateSpline : create a smoothing BivariateSpline

    Notes
    -----
    The length of `x`, `y` and `z` should be at least ``(kx+1) * (ky+1)``.

    """

    def __init__(self, x, y, z, tx, ty, w=None, bbox=[None] * 4, kx=3, ky=3, eps=None):
        nx = 2 * kx + 2 + len(tx)
        ny = 2 * ky + 2 + len(ty)
        tx1 = zeros((nx,), float)
        ty1 = zeros((ny,), float)
        tx1[(kx + 1):(nx - kx - 1)] = tx
        ty1[(ky + 1):(ny - ky - 1)] = ty
        xb, xe, yb, ye = bbox
        tx1, ty1, c, fp, ier = dfitpack.surfit_lsq(x, y, z, tx1, ty1, w, xb, xe, yb, ye, kx, ky, eps, lwrk2=1)
        if ier > 10:
            tx1, ty1, c, fp, ier = dfitpack.surfit_lsq(x, y, z, tx1, ty1, w, xb, xe, yb, ye, kx, ky, eps, lwrk2=ier)
        if ier in (0, -1, -2):
            pass
        else:
            if ier < -2:
                deficiency = (nx - kx - 1) * (ny - ky - 1) + ier
                message = _surfit_messages.get(-3) % deficiency
            else:
                message = _surfit_messages.get(ier, 'ier=%s' % ier)
            warnings.warn(message)
        self.fp = fp
        self.tck = (tx1, ty1, c)
        self.degrees = (kx, ky)


class RectBivariateSpline(BivariateSpline):
    """
    Bivariate spline approximation over a rectangular mesh.

    Can be used for both smoothing and interpolating data.

    Parameters
    ----------
    x,y : array_like
        1-D arrays of coordinates in strictly ascending order.
    z : array_like
        2-D array of data with shape (x.size,y.size).
    bbox : array_like, optional
        Sequence of length 4 specifying the boundary of the rectangular
        approximation domain.  By default,
        ``bbox=[min(x,tx),max(x,tx), min(y,ty),max(y,ty)]``.
    kx, ky : ints, optional
        Degrees of the bivariate spline. Default is 3.
    s : float, optional
        Positive smoothing factor defined for estimation condition:
        ``sum((w[i]*(z[i]-s(x[i], y[i])))**2, axis=0) <= s``
        Default is ``s=0``, which is for interpolation.

    See Also
    --------
    SmoothBivariateSpline : a smoothing bivariate spline for scattered data
    bisplrep : an older wrapping of FITPACK
    bisplev : an older wrapping of FITPACK
    UnivariateSpline : a similar class for univariate spline interpolation

    """

    def __init__(self, x, y, z, bbox=[
 None] * 4, kx=3, ky=3, s=0):
        x, y = ravel(x), ravel(y)
        if not all(diff(x) > 0.0):
            raise TypeError('x must be strictly increasing')
        if not all(diff(y) > 0.0):
            raise TypeError('y must be strictly increasing')
        if not (x.min() == x[0] and x.max() == x[-1]):
            raise TypeError('x must be strictly ascending')
        if not (y.min() == y[0] and y.max() == y[-1]):
            raise TypeError('y must be strictly ascending')
        if not x.size == z.shape[0]:
            raise TypeError('x dimension of z must have same number of elements as x')
        if not y.size == z.shape[1]:
            raise TypeError('y dimension of z must have same number of elements as y')
        z = ravel(z)
        xb, xe, yb, ye = bbox
        nx, tx, ny, ty, c, fp, ier = dfitpack.regrid_smth(x, y, z, xb, xe, yb, ye, kx, ky, s)
        if ier not in (0, -1, -2):
            msg = _surfit_messages.get(ier, 'ier=%s' % ier)
            raise ValueError(msg)
        self.fp = fp
        self.tck = (tx[:nx], ty[:ny], c[:(nx - kx - 1) * (ny - ky - 1)])
        self.degrees = (kx, ky)


_spherefit_messages = _surfit_messages.copy()
_spherefit_messages[10] = '\nERROR. On entry, the input data are controlled on validity. The following\n       restrictions must be satisfied:\n            -1<=iopt<=1,  m>=2, ntest>=8 ,npest >=8, 0<eps<1,\n            0<=teta(i)<=pi, 0<=phi(i)<=2*pi, w(i)>0, i=1,...,m\n            lwrk1 >= 185+52*v+10*u+14*u*v+8*(u-1)*v**2+8*m\n            kwrk >= m+(ntest-7)*(npest-7)\n            if iopt=-1: 8<=nt<=ntest , 9<=np<=npest\n                        0<tt(5)<tt(6)<...<tt(nt-4)<pi\n                        0<tp(5)<tp(6)<...<tp(np-4)<2*pi\n            if iopt>=0: s>=0\n            if one of these conditions is found to be violated,control\n            is immediately repassed to the calling program. in that\n            case there is no approximation returned.'
_spherefit_messages[-3] = '\nWARNING. The coefficients of the spline returned have been computed as the\n         minimal norm least-squares solution of a (numerically) rank\n         deficient system (deficiency=%i, rank=%i). Especially if the rank\n         deficiency, which is computed by 6+(nt-8)*(np-7)+ier, is large,\n         the results may be inaccurate. They could also seriously depend on\n         the value of eps.'

class SphereBivariateSpline(_BivariateSplineBase):
    """
    Bivariate spline s(x,y) of degrees 3 on a sphere, calculated from a
    given set of data points (theta,phi,r).

    .. versionadded:: 0.11.0

    See Also
    --------
    bisplrep, bisplev : an older wrapping of FITPACK
    UnivariateSpline : a similar class for univariate spline interpolation
    SmoothUnivariateSpline :
        to create a BivariateSpline through the given points
    LSQUnivariateSpline :
        to create a BivariateSpline using weighted least-squares fitting
    """

    def __call__(self, theta, phi):
        """ Evaluate the spline at the grid ponts defined by the coordinate
        arrays theta, phi. """
        theta = np.asarray(theta)
        phi = np.asarray(phi)
        if theta.size == 0 and phi.size == 0:
            return array([])
        if theta.min() < 0.0 or theta.max() > np.pi:
            raise ValueError('requested theta out of bounds.')
        if phi.min() < 0.0 or phi.max() > 2.0 * np.pi:
            raise ValueError('requested phi out of bounds.')
        tx, ty, c = self.tck[:3]
        kx, ky = self.degrees
        z, ier = dfitpack.bispev(tx, ty, c, kx, ky, theta, phi)
        if not ier == 0:
            raise ValueError('Error code returned by bispev: %s' % ier)
        return z

    def ev(self, thetai, phii):
        """ Evaluate the spline at the points (theta[i], phi[i]),
        i=0,...,len(theta)-1
        """
        thetai = np.asarray(thetai)
        phii = np.asarray(phii)
        if thetai.size == 0 and phii.size == 0:
            return array([])
        if thetai.min() < 0.0 or thetai.max() > np.pi:
            raise ValueError('requested thetai out of bounds.')
        if phii.min() < 0.0 or phii.max() > 2.0 * np.pi:
            raise ValueError('requested phii out of bounds.')
        tx, ty, c = self.tck[:3]
        kx, ky = self.degrees
        zi, ier = dfitpack.bispeu(tx, ty, c, kx, ky, thetai, phii)
        if not ier == 0:
            raise ValueError('Error code returned by bispeu: %s' % ier)
        return zi


class SmoothSphereBivariateSpline(SphereBivariateSpline):
    """
    Smooth bivariate spline approximation in spherical coordinates.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    theta, phi, r : array_like
        1-D sequences of data points (order is not important). Coordinates
        must be given in radians. Theta must lie within the interval (0, pi),
        and phi must lie within the interval (0, 2pi).
    w : array_like, optional
        Positive 1-D sequence of weights.
    s : float, optional
        Positive smoothing factor defined for estimation condition:
        ``sum((w(i)*(r(i) - s(theta(i), phi(i))))**2, axis=0) <= s``
        Default ``s=len(w)`` which should be a good value if 1/w[i] is an
        estimate of the standard deviation of r[i].
    eps : float, optional
        A threshold for determining the effective rank of an over-determined
        linear system of equations. `eps` should have a value between 0 and 1,
        the default is 1e-16.

    Notes
    -----
    For more information, see the FITPACK_ site about this function.

    .. _FITPACK: http://www.netlib.org/dierckx/sphere.f

    Examples
    --------
    Suppose we have global data on a coarse grid (the input data does not
    have to be on a grid):

    >>> theta = np.linspace(0., np.pi, 7)
    >>> phi = np.linspace(0., 2*np.pi, 9)
    >>> data = np.empty((theta.shape[0], phi.shape[0]))
    >>> data[:,0], data[0,:], data[-1,:] = 0., 0., 0.
    >>> data[1:-1,1], data[1:-1,-1] = 1., 1.
    >>> data[1,1:-1], data[-2,1:-1] = 1., 1.
    >>> data[2:-2,2], data[2:-2,-2] = 2., 2.
    >>> data[2,2:-2], data[-3,2:-2] = 2., 2.
    >>> data[3,3:-2] = 3.
    >>> data = np.roll(data, 4, 1)

    We need to set up the interpolator object

    >>> lats, lons = np.meshgrid(theta, phi)
    >>> from scipy.interpolate import SmoothSphereBivariateSpline
    >>> lut = SmoothSphereBivariateSpline(lats.ravel(), lons.ravel(),
                                         data.T.ravel(),s=3.5)

    As a first test, we'll see what the algorithm returns when run on the
    input coordinates

    >>> data_orig = lut(theta, phi)

    Finally we interpolate the data to a finer grid

    >>> fine_lats = np.linspace(0., np.pi, 70)
    >>> fine_lons = np.linspace(0., 2 * np.pi, 90)

    >>> data_smth = lut(fine_lats, fine_lons)

    >>> fig = plt.figure()
    >>> ax1 = fig.add_subplot(131)
    >>> ax1.imshow(data, interpolation='nearest')
    >>> ax2 = fig.add_subplot(132)
    >>> ax2.imshow(data_orig, interpolation='nearest')
    >>> ax3 = fig.add_subplot(133)
    >>> ax3.imshow(data_smth, interpolation='nearest')
    >>> plt.show()

    """

    def __init__(self, theta, phi, r, w=None, s=0.0, eps=1e-16):
        if np.issubclass_(w, float):
            w = ones(len(theta)) * w
        nt_, tt_, np_, tp_, c, fp, ier = dfitpack.spherfit_smth(theta, phi, r, w=w, s=s, eps=eps)
        if ier not in (0, -1, -2):
            message = _spherefit_messages.get(ier, 'ier=%s' % ier)
            raise ValueError(message)
        self.fp = fp
        self.tck = (tt_[:nt_], tp_[:np_], c[:(nt_ - 4) * (np_ - 4)])
        self.degrees = (3, 3)


class LSQSphereBivariateSpline(SphereBivariateSpline):
    """
    Weighted least-squares bivariate spline approximation in spherical
    coordinates.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    theta, phi, r : array_like
        1-D sequences of data points (order is not important). Coordinates
        must be given in radians. Theta must lie within the interval (0, pi),
        and phi must lie within the interval (0, 2pi).
    tt, tp : array_like
        Strictly ordered 1-D sequences of knots coordinates.
        Coordinates must satisfy ``0 < tt[i] < pi``, ``0 < tp[i] < 2*pi``.
    w : array_like, optional
        Positive 1-D sequence of weights, of the same length as `theta`, `phi`
        and `r`.
    eps : float, optional
        A threshold for determining the effective rank of an over-determined
        linear system of equations. `eps` should have a value between 0 and 1,
        the default is 1e-16.

    Notes
    -----
    For more information, see the FITPACK_ site about this function.

    .. _FITPACK: http://www.netlib.org/dierckx/sphere.f

    Examples
    --------
    Suppose we have global data on a coarse grid (the input data does not
    have to be on a grid):

    >>> theta = np.linspace(0., np.pi, 7)
    >>> phi = np.linspace(0., 2*np.pi, 9)
    >>> data = np.empty((theta.shape[0], phi.shape[0]))
    >>> data[:,0], data[0,:], data[-1,:] = 0., 0., 0.
    >>> data[1:-1,1], data[1:-1,-1] = 1., 1.
    >>> data[1,1:-1], data[-2,1:-1] = 1., 1.
    >>> data[2:-2,2], data[2:-2,-2] = 2., 2.
    >>> data[2,2:-2], data[-3,2:-2] = 2., 2.
    >>> data[3,3:-2] = 3.
    >>> data = np.roll(data, 4, 1)

    We need to set up the interpolator object. Here, we must also specify the
    coordinates of the knots to use.

    >>> lats, lons = np.meshgrid(theta, phi)
    >>> knotst, knotsp = theta.copy(), phi.copy()
    >>> knotst[0] += .0001
    >>> knotst[-1] -= .0001
    >>> knotsp[0] += .0001
    >>> knotsp[-1] -= .0001
    >>> from scipy.interpolate import LSQSphereBivariateSpline
    >>> lut = LSQSphereBivariateSpline(lats.ravel(), lons.ravel(),
                                       data.T.ravel(),knotst,knotsp)

    As a first test, we'll see what the algorithm returns when run on the
    input coordinates

    >>> data_orig = lut(theta, phi)

    Finally we interpolate the data to a finer grid

    >>> fine_lats = np.linspace(0., np.pi, 70)
    >>> fine_lons = np.linspace(0., 2*np.pi, 90)

    >>> data_lsq = lut(fine_lats, fine_lons)

    >>> fig = plt.figure()
    >>> ax1 = fig.add_subplot(131)
    >>> ax1.imshow(data, interpolation='nearest')
    >>> ax2 = fig.add_subplot(132)
    >>> ax2.imshow(data_orig, interpolation='nearest')
    >>> ax3 = fig.add_subplot(133)
    >>> ax3.imshow(data_lsq, interpolation='nearest')
    >>> plt.show()

    """

    def __init__(self, theta, phi, r, tt, tp, w=None, eps=1e-16):
        if np.issubclass_(w, float):
            w = ones(len(theta)) * w
        nt_, np_ = 8 + len(tt), 8 + len(tp)
        tt_, tp_ = zeros((nt_,), float), zeros((np_,), float)
        tt_[4:(-4)], tp_[4:(-4)] = tt, tp
        tt_[(-4):], tp_[(-4):] = np.pi, 2.0 * np.pi
        tt_, tp_, c, fp, ier = dfitpack.spherfit_lsq(theta, phi, r, tt_, tp_, w=w, eps=eps)
        if ier < -2:
            deficiency = 6 + (nt_ - 8) * (np_ - 7) + ier
            message = _spherefit_messages.get(-3) % (deficiency, -ier)
            warnings.warn(message)
        elif ier not in (0, -1, -2):
            message = _spherefit_messages.get(ier, 'ier=%s' % ier)
            raise ValueError(message)
        self.fp = fp
        self.tck = (tt_, tp_, c)
        self.degrees = (3, 3)


_spfit_messages = _surfit_messages.copy()
_spfit_messages[10] = '\nERROR: on entry, the input data are controlled on validity\n       the following restrictions must be satisfied.\n          -1<=iopt(1)<=1, 0<=iopt(2)<=1, 0<=iopt(3)<=1,\n          -1<=ider(1)<=1, 0<=ider(2)<=1, ider(2)=0 if iopt(2)=0.\n          -1<=ider(3)<=1, 0<=ider(4)<=1, ider(4)=0 if iopt(3)=0.\n          mu >= mumin (see above), mv >= 4, nuest >=8, nvest >= 8,\n          kwrk>=5+mu+mv+nuest+nvest,\n          lwrk >= 12+nuest*(mv+nvest+3)+nvest*24+4*mu+8*mv+max(nuest,mv+nvest)\n          0< u(i-1)<u(i)< pi,i=2,..,mu,\n          -pi<=v(1)< pi, v(1)<v(i-1)<v(i)<v(1)+2*pi, i=3,...,mv\n          if iopt(1)=-1: 8<=nu<=min(nuest,mu+6+iopt(2)+iopt(3))\n                         0<tu(5)<tu(6)<...<tu(nu-4)< pi\n                         8<=nv<=min(nvest,mv+7)\n                         v(1)<tv(5)<tv(6)<...<tv(nv-4)<v(1)+2*pi\n                         the schoenberg-whitney conditions, i.e. there must be\n                         subset of grid co-ordinates uu(p) and vv(q) such that\n                            tu(p) < uu(p) < tu(p+4) ,p=1,...,nu-4\n                            (iopt(2)=1 and iopt(3)=1 also count for a uu-value\n                            tv(q) < vv(q) < tv(q+4) ,q=1,...,nv-4\n                            (vv(q) is either a value v(j) or v(j)+2*pi)\n          if iopt(1)>=0: s>=0\n          if s=0: nuest>=mu+6+iopt(2)+iopt(3), nvest>=mv+7\n       if one of these conditions is found to be violated,control is\n       immediately repassed to the calling program. in that case there is no\n       approximation returned.'

class RectSphereBivariateSpline(SphereBivariateSpline):
    """
    Bivariate spline approximation over a rectangular mesh on a sphere.

    Can be used for smoothing data.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    u : array_like
        1-D array of latitude coordinates in strictly ascending order.
        Coordinates must be given in radians and lie within the interval
        (0, pi).
    v : array_like
        1-D array of longitude coordinates in strictly ascending order.
        Coordinates must be given in radians, and must lie within (0, 2pi).
    r : array_like
        2-D array of data with shape ``(u.size, v.size)``.
    s : float, optional
        Positive smoothing factor defined for estimation condition
        (``s=0`` is for interpolation).
    pole_continuity : bool or (bool, bool), optional
        Order of continuity at the poles ``u=0`` (``pole_continuity[0]``) and
        ``u=pi`` (``pole_continuity[1]``).  The order of continuity at the pole
        will be 1 or 0 when this is True or False, respectively.
        Defaults to False.
    pole_values : float or (float, float), optional
        Data values at the poles ``u=0`` and ``u=pi``.  Either the whole
        parameter or each individual element can be None.  Defaults to None.
    pole_exact : bool or (bool, bool), optional
        Data value exactness at the poles ``u=0`` and ``u=pi``.  If True, the
        value is considered to be the right function value, and it will be
        fitted exactly. If False, the value will be considered to be a data
        value just like the other data values.  Defaults to False.
    pole_flat : bool or (bool, bool), optional
        For the poles at ``u=0`` and ``u=pi``, specify whether or not the
        approximation has vanishing derivatives.  Defaults to False.

    See Also
    --------
    RectBivariateSpline : bivariate spline approximation over a rectangular
        mesh

    Notes
    -----
    Currently, only the smoothing spline approximation (``iopt[0] = 0`` and
    ``iopt[0] = 1`` in the FITPACK routine) is supported.  The exact
    least-squares spline approximation is not implemented yet.

    When actually performing the interpolation, the requested `v` values must
    lie within the same length 2pi interval that the original `v` values were
    chosen from.

    For more information, see the FITPACK_ site about this function.

    .. _FITPACK: http://www.netlib.org/dierckx/spgrid.f

    Examples
    --------
    Suppose we have global data on a coarse grid

    >>> lats = np.linspace(10, 170, 9) * np.pi / 180.
    >>> lons = np.linspace(0, 350, 18) * np.pi / 180.
    >>> data = np.dot(np.atleast_2d(90. - np.linspace(-80., 80., 18)).T,
                      np.atleast_2d(180. - np.abs(np.linspace(0., 350., 9)))).T

    We want to interpolate it to a global one-degree grid

    >>> new_lats = np.linspace(1, 180, 180) * np.pi / 180
    >>> new_lons = np.linspace(1, 360, 360) * np.pi / 180
    >>> new_lats, new_lons = np.meshgrid(new_lats, new_lons)

    We need to set up the interpolator object

    >>> from scipy.interpolate import RectSphereBivariateSpline
    >>> lut = RectSphereBivariateSpline(lats, lons, data)

    Finally we interpolate the data.  The `RectSphereBivariateSpline` object
    only takes 1-D arrays as input, therefore we need to do some reshaping.

    >>> data_interp = lut.ev(new_lats.ravel(),
    ...                      new_lons.ravel()).reshape((360, 180)).T

    Looking at the original and the interpolated data, one can see that the
    interpolant reproduces the original data very well:

    >>> fig = plt.figure()
    >>> ax1 = fig.add_subplot(211)
    >>> ax1.imshow(data, interpolation='nearest')
    >>> ax2 = fig.add_subplot(212)
    >>> ax2.imshow(data_interp, interpolation='nearest')
    >>> plt.show()

    Chosing the optimal value of ``s`` can be a delicate task. Recommended
    values for ``s`` depend on the accuracy of the data values.  If the user
    has an idea of the statistical errors on the data, she can also find a
    proper estimate for ``s``. By assuming that, if she specifies the
    right ``s``, the interpolator will use a spline ``f(u,v)`` which exactly
    reproduces the function underlying the data, she can evaluate
    ``sum((r(i,j)-s(u(i),v(j)))**2)`` to find a good estimate for this ``s``.
    For example, if she knows that the statistical errors on her
    ``r(i,j)``-values are not greater than 0.1, she may expect that a good
    ``s`` should have a value not larger than ``u.size * v.size * (0.1)**2``.

    If nothing is known about the statistical error in ``r(i,j)``, ``s`` must
    be determined by trial and error.  The best is then to start with a very
    large value of ``s`` (to determine the least-squares polynomial and the
    corresponding upper bound ``fp0`` for ``s``) and then to progressively
    decrease the value of ``s`` (say by a factor 10 in the beginning, i.e.
    ``s = fp0 / 10, fp0 / 100, ...``  and more carefully as the approximation
    shows more detail) to obtain closer fits.

    The interpolation results for different values of ``s`` give some insight
    into this process:

    >>> fig2 = plt.figure()
    >>> s = [3e9, 2e9, 1e9, 1e8]
    >>> for ii in xrange(len(s)):
    >>>     lut = RectSphereBivariateSpline(lats, lons, data, s=s[ii])
    >>>     data_interp = lut.ev(new_lats.ravel(),
    ...                          new_lons.ravel()).reshape((360, 180)).T
    >>>     ax = fig2.add_subplot(2, 2, ii+1)
    >>>     ax.imshow(data_interp, interpolation='nearest')
    >>>     ax.set_title("s = %g" % s[ii])
    >>> plt.show()

    """

    def __init__(self, u, v, r, s=0.0, pole_continuity=False, pole_values=None, pole_exact=False, pole_flat=False):
        iopt = np.array([0, 0, 0], dtype=int)
        ider = np.array([-1, 0, -1, 0], dtype=int)
        if pole_values is None:
            pole_values = (None, None)
        elif isinstance(pole_values, (float, np.float32, np.float64)):
            pole_values = (
             pole_values, pole_values)
        if isinstance(pole_continuity, bool):
            pole_continuity = (
             pole_continuity, pole_continuity)
        if isinstance(pole_exact, bool):
            pole_exact = (
             pole_exact, pole_exact)
        if isinstance(pole_flat, bool):
            pole_flat = (
             pole_flat, pole_flat)
        r0, r1 = pole_values
        iopt[1:] = pole_continuity
        if r0 is None:
            ider[0] = -1
        else:
            ider[0] = pole_exact[0]
        if r1 is None:
            ider[2] = -1
        else:
            ider[2] = pole_exact[1]
        ider[1], ider[3] = pole_flat
        u, v = np.ravel(u), np.ravel(v)
        if not np.all(np.diff(u) > 0.0):
            raise TypeError('u must be strictly increasing')
        if not np.all(np.diff(v) > 0.0):
            raise TypeError('v must be strictly increasing')
        if not u.size == r.shape[0]:
            raise TypeError('u dimension of r must have same number of elements as u')
        if not v.size == r.shape[1]:
            raise TypeError('v dimension of r must have same number of elements as v')
        if pole_continuity[1] is False and pole_flat[1] is True:
            raise TypeError('if pole_continuity is False, so must be pole_flat')
        if pole_continuity[0] is False and pole_flat[0] is True:
            raise TypeError('if pole_continuity is False, so must be pole_flat')
        r = np.ravel(r)
        nu, tu, nv, tv, c, fp, ier = dfitpack.regrid_smth_spher(iopt, ider, u.copy(), v.copy(), r.copy(), r0, r1, s)
        if ier not in (0, -1, -2):
            msg = _spfit_messages.get(ier, 'ier=%s' % ier)
            raise ValueError(msg)
        self.fp = fp
        self.tck = (tu[:nu], tv[:nv], c[:(nu - 4) * (nv - 4)])
        self.degrees = (3, 3)
        return