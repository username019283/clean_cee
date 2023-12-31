# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\optimize\zeros.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
import warnings
from . import _zeros
from numpy import finfo, sign, sqrt
_iter = 100
_xtol = 1e-12
_rtol = finfo(float).eps * 2
__all__ = [
 'newton', 'bisect', 'ridder', 'brentq', 'brenth']
CONVERGED = 'converged'
SIGNERR = 'sign error'
CONVERR = 'convergence error'
flag_map = {0: CONVERGED, -1: SIGNERR, -2: CONVERR}

class RootResults(object):

    def __init__(self, root, iterations, function_calls, flag):
        self.root = root
        self.iterations = iterations
        self.function_calls = function_calls
        self.converged = flag == 0
        try:
            self.flag = flag_map[flag]
        except KeyError:
            self.flag = 'unknown error %d' % (flag,)


def results_c(full_output, r):
    if full_output:
        x, funcalls, iterations, flag = r
        results = RootResults(root=x, iterations=iterations, function_calls=funcalls, flag=flag)
        return (
         x, results)
    else:
        return r


def newton(func, x0, fprime=None, args=(), tol=1.48e-08, maxiter=50, fprime2=None):
    """
    Find a zero using the Newton-Raphson or secant method.

    Find a zero of the function `func` given a nearby starting point `x0`.
    The Newton-Raphson method is used if the derivative `fprime` of `func`
    is provided, otherwise the secant method is used.  If the second order
    derivate `fprime2` of `func` is provided, parabolic Halley's method
    is used.

    Parameters
    ----------
    func : function
        The function whose zero is wanted. It must be a function of a
        single variable of the form f(x,a,b,c...), where a,b,c... are extra
        arguments that can be passed in the `args` parameter.
    x0 : float
        An initial estimate of the zero that should be somewhere near the
        actual zero.
    fprime : function, optional
        The derivative of the function when available and convenient. If it
        is None (default), then the secant method is used.
    args : tuple, optional
        Extra arguments to be used in the function call.
    tol : float, optional
        The allowable error of the zero value.
    maxiter : int, optional
        Maximum number of iterations.
    fprime2 : function, optional
        The second order derivative of the function when available and
        convenient. If it is None (default), then the normal Newton-Raphson
        or the secant method is used. If it is given, parabolic Halley's
        method is used.

    Returns
    -------
    zero : float
        Estimated location where function is zero.

    See Also
    --------
    brentq, brenth, ridder, bisect
    fsolve : find zeroes in n dimensions.

    Notes
    -----
    The convergence rate of the Newton-Raphson method is quadratic,
    the Halley method is cubic, and the secant method is
    sub-quadratic.  This means that if the function is well behaved
    the actual error in the estimated zero is approximately the square
    (cube for Halley) of the requested tolerance up to roundoff
    error. However, the stopping criterion used here is the step size
    and there is no guarantee that a zero has been found. Consequently
    the result should be verified. Safer algorithms are brentq,
    brenth, ridder, and bisect, but they all require that the root
    first be bracketed in an interval where the function changes
    sign. The brentq algorithm is recommended for general use in one
    dimensional problems when such an interval has been found.

    """
    if fprime is not None:
        p0 = 1.0 * x0
        fder2 = 0
        for iter in range(maxiter):
            myargs = (
             p0,) + args
            fder = fprime(*myargs)
            if fder == 0:
                msg = 'derivative was zero.'
                warnings.warn(msg, RuntimeWarning)
                return p0
            fval = func(*myargs)
            if fprime2 is not None:
                fder2 = fprime2(*myargs)
            if fder2 == 0:
                p = p0 - fval / fder
            else:
                discr = fder ** 2 - 2 * fval * fder2
                if discr < 0:
                    p = p0 - fder / fder2
                else:
                    p = p0 - 2 * fval / (fder + sign(fder) * sqrt(discr))
            if abs(p - p0) < tol:
                return p
            p0 = p

    else:
        p0 = x0
        if x0 >= 0:
            p1 = x0 * 1.0001 + 0.0001
        else:
            p1 = x0 * 1.0001 - 0.0001
        q0 = func(*((p0,) + args))
        q1 = func(*((p1,) + args))
        for iter in range(maxiter):
            if q1 == q0:
                if p1 != p0:
                    msg = 'Tolerance of %s reached' % (p1 - p0)
                    warnings.warn(msg, RuntimeWarning)
                return (p1 + p0) / 2.0
            p = p1 - q1 * (p1 - p0) / (q1 - q0)
            if abs(p - p1) < tol:
                return p
            p0 = p1
            q0 = q1
            p1 = p
            q1 = func(*((p1,) + args))

    msg = 'Failed to converge after %d iterations, value is %s' % (maxiter, p)
    raise RuntimeError(msg)
    return


def bisect(f, a, b, args=(), xtol=_xtol, rtol=_rtol, maxiter=_iter, full_output=False, disp=True):
    """
    Find root of a function within an interval.

    Basic bisection routine to find a zero of the function `f` between the
    arguments `a` and `b`. `f(a)` and `f(b)` can not have the same signs.
    Slow but sure.

    Parameters
    ----------
    f : function
        Python function returning a number.  `f` must be continuous, and
        f(a) and f(b) must have opposite signs.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    xtol : number, optional
        The routine converges when a root is known to lie within `xtol` of the
        value return. Should be >= 0.  The routine modifies this to take into
        account the relative precision of doubles.
    maxiter : number, optional
        if convergence is not achieved in `maxiter` iterations, and error is
        raised.  Must be >= 0.
    args : tuple, optional
        containing extra arguments for the function `f`.
        `f` is called by ``apply(f, (x)+args)``.
    full_output : bool, optional
        If `full_output` is False, the root is returned.  If `full_output` is
        True, the return value is ``(x, r)``, where x is the root, and r is
        a `RootResults` object.
    disp : bool, optional
        If True, raise RuntimeError if the algorithm didn't converge.

    Returns
    -------
    x0 : float
        Zero of `f` between `a` and `b`.
    r : RootResults (present if ``full_output = True``)
        Object containing information about the convergence.  In particular,
        ``r.converged`` is True if the routine converged.

    See Also
    --------
    brentq, brenth, bisect, newton
    fixed_point : scalar fixed-point finder
    fsolve : n-dimensional root-finding

    """
    if type(args) != type(()):
        args = (
         args,)
    r = _zeros._bisect(f, a, b, xtol, maxiter, args, full_output, disp)
    return results_c(full_output, r)


def ridder(f, a, b, args=(), xtol=_xtol, rtol=_rtol, maxiter=_iter, full_output=False, disp=True):
    """
    Find a root of a function in an interval.

    Parameters
    ----------
    f : function
        Python function returning a number.  f must be continuous, and f(a) and
        f(b) must have opposite signs.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    xtol : number, optional
        The routine converges when a root is known to lie within xtol of the
        value return. Should be >= 0.  The routine modifies this to take into
        account the relative precision of doubles.
    maxiter : number, optional
        if convergence is not achieved in maxiter iterations, and error is
        raised.  Must be >= 0.
    args : tuple, optional
        containing extra arguments for the function `f`.
        `f` is called by ``apply(f, (x)+args)``.
    full_output : bool, optional
        If `full_output` is False, the root is returned.  If `full_output` is
        True, the return value is ``(x, r)``, where `x` is the root, and `r` is
        a RootResults object.
    disp : bool, optional
        If True, raise RuntimeError if the algorithm didn't converge.

    Returns
    -------
    x0 : float
        Zero of `f` between `a` and `b`.
    r : RootResults (present if ``full_output = True``)
        Object containing information about the convergence.
        In particular, ``r.converged`` is True if the routine converged.

    See Also
    --------
    brentq, brenth, bisect, newton : one-dimensional root-finding
    fixed_point : scalar fixed-point finder

    Notes
    -----
    Uses [Ridders1979]_ method to find a zero of the function `f` between the
    arguments `a` and `b`. Ridders' method is faster than bisection, but not
    generally as fast as the Brent rountines. [Ridders1979]_ provides the
    classic description and source of the algorithm. A description can also be
    found in any recent edition of Numerical Recipes.

    The routine used here diverges slightly from standard presentations in
    order to be a bit more careful of tolerance.

    References
    ----------
    .. [Ridders1979]
       Ridders, C. F. J. "A New Algorithm for Computing a
       Single Root of a Real Continuous Function."
       IEEE Trans. Circuits Systems 26, 979-980, 1979.

    """
    if type(args) != type(()):
        args = (
         args,)
    r = _zeros._ridder(f, a, b, xtol, maxiter, args, full_output, disp)
    return results_c(full_output, r)


def brentq(f, a, b, args=(), xtol=_xtol, rtol=_rtol, maxiter=_iter, full_output=False, disp=True):
    """
    Find a root of a function in given interval.

    Return float, a zero of `f` between `a` and `b`.  `f` must be a continuous
    function, and [a,b] must be a sign changing interval.

    Description:
    Uses the classic Brent (1973) method to find a zero of the function `f` on
    the sign changing interval [a , b].  Generally considered the best of the
    rootfinding routines here.  It is a safe version of the secant method that
    uses inverse quadratic extrapolation.  Brent's method combines root
    bracketing, interval bisection, and inverse quadratic interpolation.  It is
    sometimes known as the van Wijngaarden-Deker-Brent method.  Brent (1973)
    claims convergence is guaranteed for functions computable within [a,b].

    [Brent1973]_ provides the classic description of the algorithm.  Another
    description can be found in a recent edition of Numerical Recipes, including
    [PressEtal1992]_.  Another description is at
    http://mathworld.wolfram.com/BrentsMethod.html.  It should be easy to
    understand the algorithm just by reading our code.  Our code diverges a bit
    from standard presentations: we choose a different formula for the
    extrapolation step.

    Parameters
    ----------
    f : function
        Python function returning a number.  f must be continuous, and f(a) and
        f(b) must have opposite signs.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    xtol : number, optional
        The routine converges when a root is known to lie within xtol of the
        value return. Should be >= 0.  The routine modifies this to take into
        account the relative precision of doubles.
    maxiter : number, optional
        if convergence is not achieved in maxiter iterations, and error is
        raised.  Must be >= 0.
    args : tuple, optional
        containing extra arguments for the function `f`.
        `f` is called by ``apply(f, (x)+args)``.
    full_output : bool, optional
        If `full_output` is False, the root is returned.  If `full_output` is
        True, the return value is ``(x, r)``, where `x` is the root, and `r` is
        a RootResults object.
    disp : bool, optional
        If True, raise RuntimeError if the algorithm didn't converge.

    Returns
    -------
    x0 : float
        Zero of `f` between `a` and `b`.
    r : RootResults (present if ``full_output = True``)
        Object containing information about the convergence.  In particular,
        ``r.converged`` is True if the routine converged.

    See Also
    --------
    multivariate local optimizers
      `fmin`, `fmin_powell`, `fmin_cg`, `fmin_bfgs`, `fmin_ncg`
    nonlinear least squares minimizer
      `leastsq`
    constrained multivariate optimizers
      `fmin_l_bfgs_b`, `fmin_tnc`, `fmin_cobyla`
    global optimizers
      `anneal`, `basinhopping`, `brute`
    local scalar minimizers
      `fminbound`, `brent`, `golden`, `bracket`
    n-dimensional root-finding
      `fsolve`
    one-dimensional root-finding
      `brentq`, `brenth`, `ridder`, `bisect`, `newton`
    scalar fixed-point finder
      `fixed_point`

    Notes
    -----
    `f` must be continuous.  f(a) and f(b) must have opposite signs.

    References
    ----------
    .. [Brent1973]
       Brent, R. P.,
       *Algorithms for Minimization Without Derivatives*.
       Englewood Cliffs, NJ: Prentice-Hall, 1973. Ch. 3-4.

    .. [PressEtal1992]
       Press, W. H.; Flannery, B. P.; Teukolsky, S. A.; and Vetterling, W. T.
       *Numerical Recipes in FORTRAN: The Art of Scientific Computing*, 2nd ed.
       Cambridge, England: Cambridge University Press, pp. 352-355, 1992.
       Section 9.3:  "Van Wijngaarden-Dekker-Brent Method."

    """
    if type(args) != type(()):
        args = (
         args,)
    r = _zeros._brentq(f, a, b, xtol, maxiter, args, full_output, disp)
    return results_c(full_output, r)


def brenth(f, a, b, args=(), xtol=_xtol, rtol=_rtol, maxiter=_iter, full_output=False, disp=True):
    """Find root of f in [a,b].

    A variation on the classic Brent routine to find a zero of the function f
    between the arguments a and b that uses hyperbolic extrapolation instead of
    inverse quadratic extrapolation. There was a paper back in the 1980's ...
    f(a) and f(b) can not have the same signs. Generally on a par with the
    brent routine, but not as heavily tested.  It is a safe version of the
    secant method that uses hyperbolic extrapolation. The version here is by
    Chuck Harris.

    Parameters
    ----------
    f : function
        Python function returning a number.  f must be continuous, and f(a) and
        f(b) must have opposite signs.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    xtol : number, optional
        The routine converges when a root is known to lie within xtol of the
        value return. Should be >= 0.  The routine modifies this to take into
        account the relative precision of doubles.
    maxiter : number, optional
        if convergence is not achieved in maxiter iterations, and error is
        raised.  Must be >= 0.
    args : tuple, optional
        containing extra arguments for the function `f`.
        `f` is called by ``apply(f, (x)+args)``.
    full_output : bool, optional
        If `full_output` is False, the root is returned.  If `full_output` is
        True, the return value is ``(x, r)``, where `x` is the root, and `r` is
        a RootResults object.
    disp : bool, optional
        If True, raise RuntimeError if the algorithm didn't converge.

    Returns
    -------
    x0 : float
        Zero of `f` between `a` and `b`.
    r : RootResults (present if ``full_output = True``)
        Object containing information about the convergence.  In particular,
        ``r.converged`` is True if the routine converged.

    See Also
    --------
    fmin, fmin_powell, fmin_cg,
           fmin_bfgs, fmin_ncg : multivariate local optimizers

    leastsq : nonlinear least squares minimizer

    fmin_l_bfgs_b, fmin_tnc, fmin_cobyla : constrained multivariate optimizers

    anneal, brute : global optimizers

    fminbound, brent, golden, bracket : local scalar minimizers

    fsolve : n-dimensional root-finding

    brentq, brenth, ridder, bisect, newton : one-dimensional root-finding

    fixed_point : scalar fixed-point finder

    """
    if type(args) != type(()):
        args = (
         args,)
    r = _zeros._brenth(f, a, b, xtol, maxiter, args, full_output, disp)
    return results_c(full_output, r)