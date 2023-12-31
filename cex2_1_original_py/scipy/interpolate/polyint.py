# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\interpolate\polyint.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
import numpy as np
from scipy.misc import factorial
from scipy.lib.six.moves import xrange
__all__ = [
 'KroghInterpolator', 'krogh_interpolate', 'BarycentricInterpolator', 
 'barycentric_interpolate', 
 'PiecewisePolynomial', 
 'piecewise_polynomial_interpolate', 'approximate_taylor_polynomial', 
 'PchipInterpolator', 
 'pchip_interpolate', 'pchip']

def _isscalar(x):
    """Check whether x is if a scalar type, or 0-dim"""
    return np.isscalar(x) or hasattr(x, 'shape') and x.shape == ()


class _Interpolator1D(object):
    """
    Common features in univariate interpolation

    Deal with input data type and interpolation axis rolling.  The
    actual interpolator can assume the y-data is of shape (n, r) where
    `n` is the number of x-points, and `r` the number of variables,
    and use self.dtype as the y-data type.
    """

    def __init__(self, xi=None, yi=None, axis=None):
        self._y_axis = axis
        self._y_extra_shape = None
        self.dtype = None
        if yi is not None:
            self._set_yi(yi, xi=xi, axis=axis)
        return

    def __call__(self, x):
        """
        Evaluate the interpolant

        Parameters
        ----------
        x : array-like
            Points to evaluate the interpolant at.

        Returns
        -------
        y : array-like
            Interpolated values. Shape is determined by replacing
            the interpolation axis in the original array with the shape of x.

        """
        x, x_shape = self._prepare_x(x)
        y = self._evaluate(x)
        return self._finish_y(y, x_shape)

    def _prepare_x(self, x):
        """Reshape input x array to 1-D"""
        x = np.asarray(x)
        x_shape = x.shape
        return (x.ravel(), x_shape)

    def _finish_y(self, y, x_shape):
        """Reshape interpolated y back to n-d array similar to initial y"""
        y = y.reshape(x_shape + self._y_extra_shape)
        if self._y_axis != 0 and x_shape != ():
            nx = len(x_shape)
            ny = len(self._y_extra_shape)
            s = list(range(nx, nx + self._y_axis)) + list(range(nx)) + list(range(nx + self._y_axis, nx + ny))
            y = y.transpose(s)
        return y

    def _reshape_yi(self, yi, check=False):
        yi = np.rollaxis(np.asarray(yi), self._y_axis)
        if check and yi.shape[1:] != self._y_extra_shape:
            ok_shape = '%r + (N,) + %r' % (self._y_extra_shape[-self._y_axis:],
             self._y_extra_shape[:-self._y_axis])
            raise ValueError('Data must be of shape %s' % ok_shape)
        return yi.reshape((yi.shape[0], -1))

    def _set_yi(self, yi, xi=None, axis=None):
        if axis is None:
            axis = self._y_axis
        if axis is None:
            raise ValueError('no interpolation axis specified')
        yi = np.asarray(yi)
        shape = yi.shape
        if shape == ():
            shape = (1, )
        if xi is not None and shape[axis] != len(xi):
            raise ValueError('x and y arrays must be equal in length along interpolation axis.')
        self._y_axis = axis % yi.ndim
        self._y_extra_shape = yi.shape[:self._y_axis] + yi.shape[self._y_axis + 1:]
        self.dtype = None
        self._set_dtype(yi.dtype)
        return

    def _set_dtype(self, dtype, union=False):
        if np.issubdtype(dtype, np.complexfloating) or np.issubdtype(self.dtype, np.complexfloating):
            self.dtype = np.complex_
        elif not union or self.dtype != np.complex_:
            self.dtype = np.float_


class _Interpolator1DWithDerivatives(_Interpolator1D):

    def derivatives(self, x, der=None):
        """
        Evaluate many derivatives of the polynomial at the point x

        Produce an array of all derivative values at the point x.

        Parameters
        ----------
        x : array-like
            Point or points at which to evaluate the derivatives

        der : None or integer
            How many derivatives to extract; None for all potentially
            nonzero derivatives (that is a number equal to the number
            of points). This number includes the function value as 0th
            derivative.

        Returns
        -------
        d : ndarray
            Array with derivatives; d[j] contains the j-th derivative.
            Shape of d[j] is determined by replacing the interpolation
            axis in the original array with the shape of x.

        Examples
        --------
        >>> KroghInterpolator([0,0,0],[1,2,3]).derivatives(0)
        array([1.0,2.0,3.0])
        >>> KroghInterpolator([0,0,0],[1,2,3]).derivatives([0,0])
        array([[1.0,1.0],
               [2.0,2.0],
               [3.0,3.0]])

        """
        x, x_shape = self._prepare_x(x)
        y = self._evaluate_derivatives(x, der)
        y = y.reshape((y.shape[0],) + x_shape + self._y_extra_shape)
        if self._y_axis != 0 and x_shape != ():
            nx = len(x_shape)
            ny = len(self._y_extra_shape)
            s = [
             0] + list(range(nx + 1, nx + self._y_axis + 1)) + list(range(1, nx + 1)) + list(range(nx + 1 + self._y_axis, nx + ny + 1))
            y = y.transpose(s)
        return y

    def derivative(self, x, der=1):
        """
        Evaluate one derivative of the polynomial at the point x

        Parameters
        ----------
        x : array-like
            Point or points at which to evaluate the derivatives

        der : integer, optional
            Which derivative to extract. This number includes the
            function value as 0th derivative.

        Returns
        -------
        d : ndarray
            Derivative interpolated at the x-points.  Shape of d is
            determined by replacing the interpolation axis in the
            original array with the shape of x.

        Notes
        -----
        This is computed by evaluating all derivatives up to the desired
        one (using self.derivatives()) and then discarding the rest.

        """
        x, x_shape = self._prepare_x(x)
        y = self._evaluate_derivatives(x, der + 1)
        return self._finish_y(y[der], x_shape)


class KroghInterpolator(_Interpolator1DWithDerivatives):
    """
    Interpolating polynomial for a set of points.

    The polynomial passes through all the pairs (xi,yi). One may
    additionally specify a number of derivatives at each point xi;
    this is done by repeating the value xi and specifying the
    derivatives as successive yi values.

    Allows evaluation of the polynomial and all its derivatives.
    For reasons of numerical stability, this function does not compute
    the coefficients of the polynomial, although they can be obtained
    by evaluating all the derivatives.

    Parameters
    ----------
    xi : array-like, length N
        Known x-coordinates. Must be sorted in increasing order.
    yi : array-like
        Known y-coordinates. When an xi occurs two or more times in
        a row, the corresponding yi's represent derivative values.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Notes
    -----
    Be aware that the algorithms implemented here are not necessarily
    the most numerically stable known. Moreover, even in a world of
    exact computation, unless the x coordinates are chosen very
    carefully - Chebyshev zeros (e.g. cos(i*pi/n)) are a good choice -
    polynomial interpolation itself is a very ill-conditioned process
    due to the Runge phenomenon. In general, even with well-chosen
    x values, degrees higher than about thirty cause problems with
    numerical instability in this code.

    Based on [1]_.

    References
    ----------
    .. [1] Krogh, "Efficient Algorithms for Polynomial Interpolation
        and Numerical Differentiation", 1970.

    Examples
    --------
    To produce a polynomial that is zero at 0 and 1 and has
    derivative 2 at 0, call

    >>> KroghInterpolator([0,0,1],[0,2,0])

    This constructs the quadratic 2*X**2-2*X. The derivative condition
    is indicated by the repeated zero in the xi array; the corresponding
    yi values are 0, the function value, and 2, the derivative value.

    For another example, given xi, yi, and a derivative ypi for each
    point, appropriate arrays can be constructed as:

    >>> xi_k, yi_k = np.repeat(xi, 2), np.ravel(np.dstack((yi,ypi)))
    >>> KroghInterpolator(xi_k, yi_k)

    To produce a vector-valued polynomial, supply a higher-dimensional
    array for yi:

    >>> KroghInterpolator([0,1],[[2,3],[4,5]])

    This constructs a linear polynomial giving (2,3) at 0 and (4,5) at 1.

    """

    def __init__(self, xi, yi, axis=0):
        _Interpolator1DWithDerivatives.__init__(self, xi, yi, axis)
        self.xi = np.asarray(xi)
        self.yi = self._reshape_yi(yi)
        self.n, self.r = self.yi.shape
        c = np.zeros((self.n + 1, self.r), dtype=self.dtype)
        c[0] = self.yi[0]
        Vk = np.zeros((self.n, self.r), dtype=self.dtype)
        for k in xrange(1, self.n):
            s = 0
            while s <= k and xi[k - s] == xi[k]:
                s += 1

            s -= 1
            Vk[0] = self.yi[k] / float(factorial(s))
            for i in xrange(k - s):
                if xi[i] == xi[k]:
                    raise ValueError("Elements if `xi` can't be equal.")
                if s == 0:
                    Vk[i + 1] = (c[i] - Vk[i]) / (xi[i] - xi[k])
                else:
                    Vk[i + 1] = (Vk[i + 1] - Vk[i]) / (xi[i] - xi[k])

            c[k] = Vk[k - s]

        self.c = c

    def _evaluate(self, x):
        pi = 1
        p = np.zeros((len(x), self.r), dtype=self.dtype)
        p += self.c[0, np.newaxis, :]
        for k in range(1, self.n):
            w = x - self.xi[k - 1]
            pi = w * pi
            p += pi[:, np.newaxis] * self.c[k]

        return p

    def _evaluate_derivatives(self, x, der=None):
        n = self.n
        r = self.r
        if der is None:
            der = self.n
        pi = np.zeros((n, len(x)))
        w = np.zeros((n, len(x)))
        pi[0] = 1
        p = np.zeros((len(x), self.r))
        p += self.c[0, np.newaxis, :]
        for k in xrange(1, n):
            w[k - 1] = x - self.xi[k - 1]
            pi[k] = w[k - 1] * pi[k - 1]
            p += pi[k, :, np.newaxis] * self.c[k]

        cn = np.zeros((max(der, n + 1), len(x), r), dtype=self.dtype)
        cn[:n + 1, :, :] += self.c[:n + 1, np.newaxis, :]
        cn[0] = p
        for k in xrange(1, n):
            for i in xrange(1, n - k + 1):
                pi[i] = w[k + i - 1] * pi[i - 1] + pi[i]
                cn[k] = cn[k] + pi[i, :, np.newaxis] * cn[k + i]

            cn[k] *= factorial(k)

        cn[n, :, :] = 0
        return cn[:der]


def krogh_interpolate(xi, yi, x, der=0, axis=0):
    """
    Convenience function for polynomial interpolation.

    See `KroghInterpolator` for more details.

    Parameters
    ----------
    xi : array_like
        Known x-coordinates.
    yi : array_like
        Known y-coordinates, of shape ``(xi.size, R)``.  Interpreted as
        vectors of length R, or scalars if R=1.
    x : array_like
        Point or points at which to evaluate the derivatives.
    der : int or list
        How many derivatives to extract; None for all potentially
        nonzero derivatives (that is a number equal to the number
        of points), or a list of derivatives to extract. This number
        includes the function value as 0th derivative.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Returns
    -------
    d : ndarray
        If the interpolator's values are R-dimensional then the
        returned array will be the number of derivatives by N by R.
        If `x` is a scalar, the middle dimension will be dropped; if
        the `yi` are scalars then the last dimension will be dropped.

    See Also
    --------
    KroghInterpolator

    Notes
    -----
    Construction of the interpolating polynomial is a relatively expensive
    process. If you want to evaluate it repeatedly consider using the class
    KroghInterpolator (which is what this function uses).

    """
    P = KroghInterpolator(xi, yi, axis=axis)
    if der == 0:
        return P(x)
    else:
        if _isscalar(der):
            return P.derivative(x, der=der)
        return P.derivatives(x, der=np.amax(der) + 1)[der]


def approximate_taylor_polynomial(f, x, degree, scale, order=None):
    """
    Estimate the Taylor polynomial of f at x by polynomial fitting.

    Parameters
    ----------
    f : callable
        The function whose Taylor polynomial is sought. Should accept
        a vector of `x` values.
    x : scalar
        The point at which the polynomial is to be evaluated.
    degree : int
        The degree of the Taylor polynomial
    scale : scalar
        The width of the interval to use to evaluate the Taylor polynomial.
        Function values spread over a range this wide are used to fit the
        polynomial. Must be chosen carefully.
    order : int or None, optional
        The order of the polynomial to be used in the fitting; `f` will be
        evaluated ``order+1`` times. If None, use `degree`.

    Returns
    -------
    p : poly1d instance
        The Taylor polynomial (translated to the origin, so that
        for example p(0)=f(x)).

    Notes
    -----
    The appropriate choice of "scale" is a trade-off; too large and the
    function differs from its Taylor polynomial too much to get a good
    answer, too small and round-off errors overwhelm the higher-order terms.
    The algorithm used becomes numerically unstable around order 30 even
    under ideal circumstances.

    Choosing order somewhat larger than degree may improve the higher-order
    terms.

    """
    if order is None:
        order = degree
    n = order + 1
    xs = scale * np.cos(np.linspace(0, np.pi, n, endpoint=n % 1)) + x
    P = KroghInterpolator(xs, f(xs))
    d = P.derivatives(x, der=degree + 1)
    return np.poly1d((d / factorial(np.arange(degree + 1)))[::-1])


class BarycentricInterpolator(_Interpolator1D):
    """The interpolating polynomial for a set of points

    Constructs a polynomial that passes through a given set of points.
    Allows evaluation of the polynomial, efficient changing of the y
    values to be interpolated, and updating by adding more x values.
    For reasons of numerical stability, this function does not compute
    the coefficients of the polynomial.

    The values yi need to be provided before the function is
    evaluated, but none of the preprocessing depends on them, so rapid
    updates are possible.

    Parameters
    ----------
    xi : array-like
        1-d array of x coordinates of the points the polynomial
        should pass through
    yi : array-like
        The y coordinates of the points the polynomial should pass through.
        If None, the y values will be supplied later via the `set_y` method.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Notes
    -----
    This class uses a "barycentric interpolation" method that treats
    the problem as a special case of rational function interpolation.
    This algorithm is quite stable, numerically, but even in a world of
    exact computation, unless the x coordinates are chosen very
    carefully - Chebyshev zeros (e.g. cos(i*pi/n)) are a good choice -
    polynomial interpolation itself is a very ill-conditioned process
    due to the Runge phenomenon.

    Based on Berrut and Trefethen 2004, "Barycentric Lagrange Interpolation".

    """

    def __init__(self, xi, yi=None, axis=0):
        _Interpolator1D.__init__(self, xi, yi, axis)
        self.xi = np.asarray(xi)
        self.set_yi(yi)
        self.n = len(self.xi)
        self.wi = np.zeros(self.n)
        self.wi[0] = 1
        for j in xrange(1, self.n):
            self.wi[:j] *= self.xi[j] - self.xi[:j]
            self.wi[j] = np.multiply.reduce(self.xi[:j] - self.xi[j])

        self.wi **= -1

    def set_yi(self, yi, axis=None):
        """
        Update the y values to be interpolated

        The barycentric interpolation algorithm requires the calculation
        of weights, but these depend only on the xi. The yi can be changed
        at any time.

        Parameters
        ----------
        yi : array_like
            The y coordinates of the points the polynomial should pass through.
            If None, the y values will be supplied later.
        axis : int, optional
            Axis in the yi array corresponding to the x-coordinate values.

        """
        if yi is None:
            self.yi = None
            return
        else:
            self._set_yi(yi, xi=self.xi, axis=axis)
            self.yi = self._reshape_yi(yi)
            self.n, self.r = self.yi.shape
            return

    def add_xi(self, xi, yi=None):
        """
        Add more x values to the set to be interpolated

        The barycentric interpolation algorithm allows easy updating by
        adding more points for the polynomial to pass through.

        Parameters
        ----------
        xi : array_like
            The x coordinates of the points that the polynomial should pass
            through.
        yi : array_like, optional
            The y coordinates of the points the polynomial should pass through.
            Should have shape ``(xi.size, R)``; if R > 1 then the polynomial is
            vector-valued.
            If `yi` is not given, the y values will be supplied later. `yi` should
            be given if and only if the interpolator has y values specified.

        """
        if yi is not None:
            if self.yi is None:
                raise ValueError('No previous yi value to update!')
            yi = self._reshape_yi(yi, check=True)
            self.yi = np.vstack((self.yi, yi))
        else:
            if self.yi is not None:
                raise ValueError('No update to yi provided!')
            old_n = self.n
            self.xi = np.concatenate((self.xi, xi))
            self.n = len(self.xi)
            self.wi **= -1
            old_wi = self.wi
            self.wi = np.zeros(self.n)
            self.wi[:old_n] = old_wi
            for j in xrange(old_n, self.n):
                self.wi[:j] *= self.xi[j] - self.xi[:j]
                self.wi[j] = np.multiply.reduce(self.xi[:j] - self.xi[j])

        self.wi **= -1
        return

    def __call__(self, x):
        """Evaluate the interpolating polynomial at the points x

        Parameters
        ----------
        x : array-like
            Points to evaluate the interpolant at.

        Returns
        -------
        y : array-like
            Interpolated values. Shape is determined by replacing
            the interpolation axis in the original array with the shape of x.

        Notes
        -----
        Currently the code computes an outer product between x and the
        weights, that is, it constructs an intermediate array of size
        N by len(x), where N is the degree of the polynomial.
        """
        return _Interpolator1D.__call__(self, x)

    def _evaluate(self, x):
        if x.size == 0:
            p = np.zeros((0, self.r), dtype=self.dtype)
        else:
            c = x[(..., np.newaxis)] - self.xi
            z = c == 0
            c[z] = 1
            c = self.wi / c
            p = np.dot(c, self.yi) / np.sum(c, axis=-1)[(..., np.newaxis)]
            r = np.nonzero(z)
            if len(r) == 1:
                if len(r[0]) > 0:
                    p = self.yi[r[0][0]]
            else:
                p[r[:-1]] = self.yi[r[-1]]
        return p


def barycentric_interpolate(xi, yi, x, axis=0):
    """
    Convenience function for polynomial interpolation.

    Constructs a polynomial that passes through a given set of points,
    then evaluates the polynomial. For reasons of numerical stability,
    this function does not compute the coefficients of the polynomial.

    This function uses a "barycentric interpolation" method that treats
    the problem as a special case of rational function interpolation.
    This algorithm is quite stable, numerically, but even in a world of
    exact computation, unless the `x` coordinates are chosen very
    carefully - Chebyshev zeros (e.g. cos(i*pi/n)) are a good choice -
    polynomial interpolation itself is a very ill-conditioned process
    due to the Runge phenomenon.

    Parameters
    ----------
    xi : array_like
        1-d array of x coordinates of the points the polynomial should
        pass through
    yi : array_like
        The y coordinates of the points the polynomial should pass through.
    x : scalar or array_like
        Points to evaluate the interpolator at.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Returns
    -------
    y : scalar or array_like
        Interpolated values. Shape is determined by replacing
        the interpolation axis in the original array with the shape of x.

    See Also
    --------
    BarycentricInterpolator

    Notes
    -----
    Construction of the interpolation weights is a relatively slow process.
    If you want to call this many times with the same xi (but possibly
    varying yi or x) you should use the class `BarycentricInterpolator`.
    This is what this function uses internally.

    """
    return BarycentricInterpolator(xi, yi, axis=axis)(x)


class PiecewisePolynomial(_Interpolator1DWithDerivatives):
    """Piecewise polynomial curve specified by points and derivatives

    This class represents a curve that is a piecewise polynomial. It
    passes through a list of points and has specified derivatives at
    each point. The degree of the polynomial may vary from segment to
    segment, as may the number of derivatives available. The degree
    should not exceed about thirty.

    Appending points to the end of the curve is efficient.

    Parameters
    ----------
    xi : array-like
        a sorted 1-d array of x-coordinates
    yi : array-like or list of array-likes
        yi[i][j] is the j-th derivative known at xi[i]   (for axis=0)
    orders : list of integers, or integer
        a list of polynomial orders, or a single universal order
    direction : {None, 1, -1}
        indicates whether the xi are increasing or decreasing
        +1 indicates increasing
        -1 indicates decreasing
        None indicates that it should be deduced from the first two xi
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Notes
    -----
    If orders is None, or orders[i] is None, then the degree of the
    polynomial segment is exactly the degree required to match all i
    available derivatives at both endpoints. If orders[i] is not None,
    then some derivatives will be ignored. The code will try to use an
    equal number of derivatives from each end; if the total number of
    derivatives needed is odd, it will prefer the rightmost endpoint. If
    not enough derivatives are available, an exception is raised.

    """

    def __init__(self, xi, yi, orders=None, direction=None, axis=0):
        _Interpolator1DWithDerivatives.__init__(self, axis=axis)
        if axis != 0:
            try:
                yi = np.asarray(yi)
            except ValueError:
                raise ValueError('If yi is a list, then axis must be 0')

            preslice = (slice(None, None, None),) * (axis % yi.ndim)
            slice0 = preslice + (0, )
            slice1 = preslice + (slice(1, None, None),)
        else:
            slice0 = 0
            slice1 = slice(1, None, None)
        yi0 = np.asarray(yi[slice0])
        self._set_yi(yi0)
        self.xi = [
         xi[0]]
        self.yi = [self._reshape_yi(yi0)]
        self.n = 1
        self.r = np.prod(self._y_extra_shape)
        self.direction = direction
        self.orders = []
        self.polynomials = []
        self.extend(xi[1:], yi[slice1], orders)
        return

    def _make_polynomial(self, x1, y1, x2, y2, order, direction):
        """Construct the interpolating polynomial object

        Deduces the number of derivatives to match at each end
        from order and the number of derivatives available. If
        possible it uses the same number of derivatives from
        each end; if the number is odd it tries to take the
        extra one from y2. In any case if not enough derivatives
        are available at one end or another it draws enough to
        make up the total from the other end.
        """
        n = order + 1
        n1 = min(n // 2, len(y1))
        n2 = min(n - n1, len(y2))
        n1 = min(n - n2, len(y1))
        if n1 + n2 != n:
            raise ValueError('Point %g has %d derivatives, point %g has %d derivatives, but order %d requested' % (x1, len(y1), x2, len(y2), order))
        if not (n1 <= len(y1) and n2 <= len(y2)):
            raise ValueError('`order` input incompatible with length y1 or y2.')
        xi = np.zeros(n)
        yi = np.zeros((n, self.r), dtype=self.dtype)
        xi[:n1] = x1
        yi[:n1] = y1[:n1].reshape((n1, self.r))
        xi[n1:] = x2
        yi[n1:] = y2[:n2].reshape((n2, self.r))
        return KroghInterpolator(xi, yi, axis=0)

    def append(self, xi, yi, order=None):
        """
        Append a single point with derivatives to the PiecewisePolynomial

        Parameters
        ----------
        xi : float
            Input
        yi : array_like
            `yi` is the list of derivatives known at `xi`
        order : integer or None
            a polynomial order, or instructions to use the highest
            possible order

        """
        yi = self._reshape_yi(yi, check=True)
        self._set_dtype(yi.dtype, union=True)
        if self.direction is None:
            self.direction = np.sign(xi - self.xi[-1])
        elif (xi - self.xi[-1]) * self.direction < 0:
            raise ValueError('x coordinates must be in the %d direction: %s' % (self.direction, self.xi))
        self.xi.append(xi)
        self.yi.append(yi)
        if order is None:
            n1 = len(self.yi[-2])
            n2 = len(self.yi[-1])
            n = n1 + n2
            order = n - 1
        self.orders.append(order)
        self.polynomials.append(self._make_polynomial(self.xi[-2], self.yi[-2], self.xi[-1], self.yi[-1], order, self.direction))
        self.n += 1
        return

    def extend(self, xi, yi, orders=None):
        """
        Extend the PiecewisePolynomial by a list of points

        Parameters
        ----------
        xi : array_like
            A sorted list of x-coordinates.
        yi : list of lists of length N1
            ``yi[i]`` (if ``axis == 0``) is the list of derivatives known
            at ``xi[i]``.
        orders : int or list of ints
            A list of polynomial orders, or a single universal order.
        direction : {None, 1, -1}
            Indicates whether the `xi` are increasing or decreasing.

                +1 indicates increasing

                -1 indicates decreasing

            None indicates that it should be deduced from the first two `xi`.

        """
        if self._y_axis == 0:
            for i in xrange(len(xi)):
                if orders is None or _isscalar(orders):
                    self.append(xi[i], yi[i], orders)
                else:
                    self.append(xi[i], yi[i], orders[i])

        else:
            preslice = (
             slice(None, None, None),) * self._y_axis
            for i in xrange(len(xi)):
                if orders is None or _isscalar(orders):
                    self.append(xi[i], yi[preslice + (i,)], orders)
                else:
                    self.append(xi[i], yi[preslice + (i,)], orders[i])

        return

    def _evaluate(self, x):
        if _isscalar(x):
            pos = np.clip(np.searchsorted(self.xi, x) - 1, 0, self.n - 2)
            y = self.polynomials[pos](x)
        else:
            m = len(x)
            pos = np.clip(np.searchsorted(self.xi, x) - 1, 0, self.n - 2)
            y = np.zeros((m, self.r), dtype=self.dtype)
            if y.size > 0:
                for i in xrange(self.n - 1):
                    c = pos == i
                    y[c] = self.polynomials[i](x[c])

        return y

    def _evaluate_derivatives(self, x, der=None):
        if der is None and self.polynomials:
            der = self.polynomials[0].n
        if _isscalar(x):
            pos = np.clip(np.searchsorted(self.xi, x) - 1, 0, self.n - 2)
            y = self.polynomials[pos].derivatives(x, der=der)
        else:
            m = len(x)
            pos = np.clip(np.searchsorted(self.xi, x) - 1, 0, self.n - 2)
            y = np.zeros((der, m, self.r), dtype=self.dtype)
            if y.size > 0:
                for i in xrange(self.n - 1):
                    c = pos == i
                    y[:, c] = self.polynomials[i].derivatives(x[c], der=der)

        return y


def piecewise_polynomial_interpolate(xi, yi, x, orders=None, der=0, axis=0):
    """
    Convenience function for piecewise polynomial interpolation.

    Parameters
    ----------
    xi : array_like
        A sorted list of x-coordinates.
    yi : list of lists
        ``yi[i]`` is the list of derivatives known at ``xi[i]``.
    x : scalar or array_like
        Coordinates at which to evalualte the polynomial.
    orders : int or list of ints, optional
        A list of polynomial orders, or a single universal order.
    der : int or list
        How many derivatives to extract; None for all potentially
        nonzero derivatives (that is a number equal to the number
        of points), or a list of derivatives to extract. This number
        includes the function value as 0th derivative.
    axis : int, optional
        Axis in the `yi` array corresponding to the x-coordinate values.

    Returns
    -------
    y : ndarray
        Interpolated values or derivatives. If multiple derivatives
        were requested, these are given along the first axis.

    See Also
    --------
    PiecewisePolynomial

    Notes
    -----
    If `orders` is None, or ``orders[i]`` is None, then the degree of the
    polynomial segment is exactly the degree required to match all i
    available derivatives at both endpoints.  If ``orders[i]`` is not None,
    then some derivatives will be ignored.  The code will try to use an
    equal number of derivatives from each end; if the total number of
    derivatives needed is odd, it will prefer the rightmost endpoint. If
    not enough derivatives are available, an exception is raised.

    Construction of these piecewise polynomials can be an expensive process;
    if you repeatedly evaluate the same polynomial, consider using the class
    PiecewisePolynomial (which is what this function does).

    """
    P = PiecewisePolynomial(xi, yi, orders, axis=axis)
    if der == 0:
        return P(x)
    else:
        if _isscalar(der):
            return P.derivative(x, der=der)
        return P.derivatives(x, der=np.amax(der) + 1)[der]


class PchipInterpolator(PiecewisePolynomial):
    """PCHIP 1-d monotonic cubic interpolation

    x and y are arrays of values used to approximate some function f,
    with ``y = f(x)``.  The interpolant uses monotonic cubic splines
    to find the value of new points.

    Parameters
    ----------
    x : ndarray
        A 1-D array of monotonically increasing real values.  `x` cannot
        include duplicate values (otherwise f is overspecified)
    y : ndarray
        A 1-D array of real values.  `y`'s length along the interpolation
        axis must be equal to the length of `x`.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    Notes
    -----
    Assumes x is sorted in monotonic order (e.g. ``x[1] > x[0]``).

    """

    def __init__(self, x, y, axis=0):
        x = np.asarray(x)
        y = np.asarray(y)
        axis = axis % y.ndim
        xp = x.reshape((x.shape[0],) + (1, ) * (y.ndim - 1))
        yp = np.rollaxis(y, axis)
        data = np.empty((yp.shape[0], 2) + yp.shape[1:], y.dtype)
        data[:, 0] = yp
        data[:, 1] = PchipInterpolator._find_derivatives(xp, yp)
        s = list(range(2, y.ndim + 1))
        s.insert(axis, 1)
        s.insert(axis, 0)
        data = data.transpose(s)
        PiecewisePolynomial.__init__(self, x, data, orders=3, direction=None, axis=axis)
        return

    @staticmethod
    def _edge_case(m0, d1, out):
        m0 = np.atleast_1d(m0)
        d1 = np.atleast_1d(d1)
        mask = (d1 != 0) & (m0 != 0)
        out[mask] = 1.0 / (1.0 / m0[mask] + 1.0 / d1[mask])

    @staticmethod
    def _find_derivatives(x, y):
        y_shape = y.shape
        if y.ndim == 1:
            x = x[:, None]
            y = y[:, None]
        hk = x[1:] - x[:-1]
        mk = (y[1:] - y[:-1]) / hk
        smk = np.sign(mk)
        condition = (smk[1:] != smk[:-1]) | (mk[1:] == 0) | (mk[:-1] == 0)
        w1 = 2 * hk[1:] + hk[:-1]
        w2 = hk[1:] + 2 * hk[:-1]
        whmean = 1.0 / (w1 + w2) * (w1 / mk[1:] + w2 / mk[:-1])
        dk = np.zeros_like(y)
        dk[1:-1][condition] = 0.0
        dk[1:-1][~condition] = 1.0 / whmean[~condition]
        PchipInterpolator._edge_case(mk[0], dk[1], dk[0])
        PchipInterpolator._edge_case(mk[-1], dk[-2], dk[-1])
        return dk.reshape(y_shape)


def pchip_interpolate(xi, yi, x, der=0, axis=0):
    """
    Convenience function for pchip interpolation.

    See `PchipInterpolator` for details.

    Parameters
    ----------
    xi : array_like
        A sorted list of x-coordinates, of length N.
    yi : list of lists
        yi[i] is the list of derivatives known at xi[i]. Of length N.
    x : scalar or array_like
        Of length M.
    der : integer or list
        How many derivatives to extract; None for all potentially
        nonzero derivatives (that is a number equal to the number
        of points), or a list of derivatives to extract. This number
        includes the function value as 0th derivative.
    axis : int, optional
        Axis in the yi array corresponding to the x-coordinate values.

    See Also
    --------
    PchipInterpolator

    Returns
    -------
    y : scalar or array_like
        The result, of length R or length M or M by R,

    """
    P = PchipInterpolator(xi, yi, axis=axis)
    if der == 0:
        return P(x)
    else:
        if _isscalar(der):
            return P.derivative(x, der=der)
        return P.derivatives(x, der=np.amax(der) + 1)[der]


pchip = PchipInterpolator