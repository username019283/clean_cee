# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\optimize\optimize.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
__all__ = [
 'fmin', 'fmin_powell', 'fmin_bfgs', 'fmin_ncg', 'fmin_cg', 
 'fminbound', 
 'brent', 'golden', 'bracket', 'rosen', 'rosen_der', 
 'rosen_hess', 'rosen_hess_prod', 
 'brute', 'approx_fprime', 
 'line_search', 'check_grad', 'Result', 'show_options', 
 'OptimizeWarning']
__docformat__ = 'restructuredtext en'
import warnings, numpy
from scipy.lib.six import callable
from numpy import atleast_1d, eye, mgrid, argmin, zeros, shape, squeeze, vectorize, asarray, sqrt, Inf, asfarray, isinf
from .linesearch import line_search_BFGS, line_search_wolfe1, line_search_wolfe2, line_search_wolfe2 as line_search
_status_message = {'success': 'Optimization terminated successfully.', 'maxfev': 'Maximum number of function evaluations has been exceeded.', 
   'maxiter': 'Maximum number of iterations has been exceeded.', 
   'pr_loss': 'Desired error not necessarily achieved due to precision loss.'}

class MemoizeJac(object):
    """ Decorator that caches the value gradient of function each time it
    is called. """

    def __init__(self, fun):
        self.fun = fun
        self.jac = None
        self.x = None
        return

    def __call__(self, x, *args):
        self.x = numpy.asarray(x).copy()
        fg = self.fun(x, *args)
        self.jac = fg[1]
        return fg[0]

    def derivative(self, x, *args):
        if self.jac is not None and numpy.alltrue(x == self.x):
            return self.jac
        else:
            self(x, *args)
            return self.jac
            return


class Result(dict):
    """ Represents the optimization result.

    Attributes
    ----------
    x : ndarray
        The solution of the optimization.
    success : bool
        Whether or not the optimizer exited successfully.
    status : int
        Termination status of the optimizer. Its value depends on the
        underlying solver. Refer to `message` for details.
    message : str
        Description of the cause of the termination.
    fun, jac, hess : ndarray
        Values of objective function, Jacobian and Hessian (if available).
    nfev, njev, nhev : int
        Number of evaluations of the objective functions and of its
        Jacobian and Hessian.
    nit : int
        Number of iterations performed by the optimizer.
    maxcv : float
        The maximum constraint violation.

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return ('\n').join([ k.rjust(m) + ': ' + repr(v) for k, v in self.items()
                               ])
        return self.__class__.__name__ + '()'


class OptimizeWarning(UserWarning):
    pass


def _check_unknown_options(unknown_options):
    if unknown_options:
        msg = (', ').join(map(str, unknown_options.keys()))
        warnings.warn('Unknown solver options: %s' % msg, OptimizeWarning, 4)


def is_array_scalar(x):
    """Test whether `x` is either a scalar or an array scalar.

    """
    return len(atleast_1d(x) == 1)


_epsilon = sqrt(numpy.finfo(float).eps)

def vecnorm(x, ord=2):
    if ord == Inf:
        return numpy.amax(numpy.abs(x))
    else:
        if ord == -Inf:
            return numpy.amin(numpy.abs(x))
        return numpy.sum(numpy.abs(x) ** ord, axis=0) ** (1.0 / ord)


def rosen(x):
    """
    The Rosenbrock function.

    The function computed is::

        sum(100.0*(x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0

    Parameters
    ----------
    x : array_like
        1-D array of points at which the Rosenbrock function is to be computed.

    Returns
    -------
    f : float
        The value of the Rosenbrock function.

    See Also
    --------
    rosen_der, rosen_hess, rosen_hess_prod

    """
    x = asarray(x)
    return numpy.sum(100.0 * (x[1:] - x[:-1] ** 2.0) ** 2.0 + (1 - x[:-1]) ** 2.0, axis=0)


def rosen_der(x):
    """
    The derivative (i.e. gradient) of the Rosenbrock function.

    Parameters
    ----------
    x : array_like
        1-D array of points at which the derivative is to be computed.

    Returns
    -------
    rosen_der : (N,) ndarray
        The gradient of the Rosenbrock function at `x`.

    See Also
    --------
    rosen, rosen_hess, rosen_hess_prod

    """
    x = asarray(x)
    xm = x[1:-1]
    xm_m1 = x[:-2]
    xm_p1 = x[2:]
    der = numpy.zeros_like(x)
    der[1:(-1)] = 200 * (xm - xm_m1 ** 2) - 400 * (xm_p1 - xm ** 2) * xm - 2 * (1 - xm)
    der[0] = -400 * x[0] * (x[1] - x[0] ** 2) - 2 * (1 - x[0])
    der[-1] = 200 * (x[-1] - x[-2] ** 2)
    return der


def rosen_hess(x):
    """
    The Hessian matrix of the Rosenbrock function.

    Parameters
    ----------
    x : array_like
        1-D array of points at which the Hessian matrix is to be computed.

    Returns
    -------
    rosen_hess : ndarray
        The Hessian matrix of the Rosenbrock function at `x`.

    See Also
    --------
    rosen, rosen_der, rosen_hess_prod

    """
    x = atleast_1d(x)
    H = numpy.diag(-400 * x[:-1], 1) - numpy.diag(400 * x[:-1], -1)
    diagonal = numpy.zeros(len(x), dtype=x.dtype)
    diagonal[0] = 1200 * x[0] ** 2 - 400 * x[1] + 2
    diagonal[-1] = 200
    diagonal[1:(-1)] = 202 + 1200 * x[1:-1] ** 2 - 400 * x[2:]
    H = H + numpy.diag(diagonal)
    return H


def rosen_hess_prod(x, p):
    """
    Product of the Hessian matrix of the Rosenbrock function with a vector.

    Parameters
    ----------
    x : array_like
        1-D array of points at which the Hessian matrix is to be computed.
    p : array_like
        1-D array, the vector to be multiplied by the Hessian matrix.

    Returns
    -------
    rosen_hess_prod : ndarray
        The Hessian matrix of the Rosenbrock function at `x` multiplied
        by the vector `p`.

    See Also
    --------
    rosen, rosen_der, rosen_hess

    """
    x = atleast_1d(x)
    Hp = numpy.zeros(len(x), dtype=x.dtype)
    Hp[0] = (1200 * x[0] ** 2 - 400 * x[1] + 2) * p[0] - 400 * x[0] * p[1]
    Hp[1:(-1)] = -400 * x[:-2] * p[:-2] + (202 + 1200 * x[1:-1] ** 2 - 400 * x[2:]) * p[1:-1] - 400 * x[1:-1] * p[2:]
    Hp[-1] = -400 * x[-2] * p[-2] + 200 * p[-1]
    return Hp


def wrap_function(function, args):
    ncalls = [
     0]

    def function_wrapper(x):
        ncalls[0] += 1
        return function(x, *args)

    return (ncalls, function_wrapper)


def fmin(func, x0, args=(), xtol=0.0001, ftol=0.0001, maxiter=None, maxfun=None, full_output=0, disp=1, retall=0, callback=None):
    """
    Minimize a function using the downhill simplex algorithm.

    This algorithm only uses function values, not derivatives or second
    derivatives.

    Parameters
    ----------
    func : callable func(x,*args)
        The objective function to be minimized.
    x0 : ndarray
        Initial guess.
    args : tuple, optional
        Extra arguments passed to func, i.e. ``f(x,*args)``.
    callback : callable, optional
        Called after each iteration, as callback(xk), where xk is the
        current parameter vector.
    xtol : float, optional
        Relative error in xopt acceptable for convergence.
    ftol : number, optional
        Relative error in func(xopt) acceptable for convergence.
    maxiter : int, optional
        Maximum number of iterations to perform.
    maxfun : number, optional
        Maximum number of function evaluations to make.
    full_output : bool, optional
        Set to True if fopt and warnflag outputs are desired.
    disp : bool, optional
        Set to True to print convergence messages.
    retall : bool, optional
        Set to True to return list of solutions at each iteration.

    Returns
    -------
    xopt : ndarray
        Parameter that minimizes function.
    fopt : float
        Value of function at minimum: ``fopt = func(xopt)``.
    iter : int
        Number of iterations performed.
    funcalls : int
        Number of function calls made.
    warnflag : int
        1 : Maximum number of function evaluations made.
        2 : Maximum number of iterations reached.
    allvecs : list
        Solution at each iteration.

    See also
    --------
    minimize: Interface to minimization algorithms for multivariate
        functions. See the 'Nelder-Mead' `method` in particular.

    Notes
    -----
    Uses a Nelder-Mead simplex algorithm to find the minimum of function of
    one or more variables.

    This algorithm has a long history of successful use in applications.
    But it will usually be slower than an algorithm that uses first or
    second derivative information. In practice it can have poor
    performance in high-dimensional problems and is not robust to
    minimizing complicated functions. Additionally, there currently is no
    complete theory describing when the algorithm will successfully
    converge to the minimum, or how fast it will if it does.

    References
    ----------
    .. [1] Nelder, J.A. and Mead, R. (1965), "A simplex method for function
           minimization", The Computer Journal, 7, pp. 308-313

    .. [2] Wright, M.H. (1996), "Direct Search Methods: Once Scorned, Now
           Respectable", in Numerical Analysis 1995, Proceedings of the
           1995 Dundee Biennial Conference in Numerical Analysis, D.F.
           Griffiths and G.A. Watson (Eds.), Addison Wesley Longman,
           Harlow, UK, pp. 191-208.

    """
    opts = {'xtol': xtol, 'ftol': ftol, 
       'maxiter': maxiter, 
       'maxfev': maxfun, 
       'disp': disp, 
       'return_all': retall}
    res = _minimize_neldermead(func, x0, args, callback=callback, **opts)
    if full_output:
        retlist = (
         res['x'], res['fun'], res['nit'], res['nfev'], res['status'])
        if retall:
            retlist += (res['allvecs'],)
        return retlist
    if retall:
        return (res['x'], res['allvecs'])
    else:
        return res['x']


def _minimize_neldermead(func, x0, args=(), callback=None, xtol=0.0001, ftol=0.0001, maxiter=None, maxfev=None, disp=False, return_all=False, **unknown_options):
    """
    Minimization of scalar function of one or more variables using the
    Nelder-Mead algorithm.

    Options for the Nelder-Mead algorithm are:
        disp : bool
            Set to True to print convergence messages.
        xtol : float
            Relative error in solution `xopt` acceptable for convergence.
        ftol : float
            Relative error in ``fun(xopt)`` acceptable for convergence.
        maxiter : int
            Maximum number of iterations to perform.
        maxfev : int
            Maximum number of function evaluations to make.

    This function is called by the `minimize` function with
    `method=Nelder-Mead`. It is not supposed to be called directly.
    """
    _check_unknown_options(unknown_options)
    maxfun = maxfev
    retall = return_all
    fcalls, func = wrap_function(func, args)
    x0 = asfarray(x0).flatten()
    N = len(x0)
    rank = len(x0.shape)
    if not -1 < rank < 2:
        raise ValueError('Initial guess must be a scalar or rank-1 sequence.')
    if maxiter is None:
        maxiter = N * 200
    if maxfun is None:
        maxfun = N * 200
    rho = 1
    chi = 2
    psi = 0.5
    sigma = 0.5
    one2np1 = list(range(1, N + 1))
    if rank == 0:
        sim = numpy.zeros((N + 1,), dtype=x0.dtype)
    else:
        sim = numpy.zeros((N + 1, N), dtype=x0.dtype)
    fsim = numpy.zeros((N + 1,), float)
    sim[0] = x0
    if retall:
        allvecs = [
         sim[0]]
    fsim[0] = func(x0)
    nonzdelt = 0.05
    zdelt = 0.00025
    for k in range(0, N):
        y = numpy.array(x0, copy=True)
        if y[k] != 0:
            y[k] = (1 + nonzdelt) * y[k]
        else:
            y[k] = zdelt
        sim[k + 1] = y
        f = func(y)
        fsim[k + 1] = f

    ind = numpy.argsort(fsim)
    fsim = numpy.take(fsim, ind, 0)
    sim = numpy.take(sim, ind, 0)
    iterations = 1
    while fcalls[0] < maxfun and iterations < maxiter:
        if numpy.max(numpy.ravel(numpy.abs(sim[1:] - sim[0]))) <= xtol and numpy.max(numpy.abs(fsim[0] - fsim[1:])) <= ftol:
            break
        xbar = numpy.add.reduce(sim[:-1], 0) / N
        xr = (1 + rho) * xbar - rho * sim[-1]
        fxr = func(xr)
        doshrink = 0
        if fxr < fsim[0]:
            xe = (1 + rho * chi) * xbar - rho * chi * sim[-1]
            fxe = func(xe)
            if fxe < fxr:
                sim[-1] = xe
                fsim[-1] = fxe
            else:
                sim[-1] = xr
                fsim[-1] = fxr
        elif fxr < fsim[-2]:
            sim[-1] = xr
            fsim[-1] = fxr
        else:
            if fxr < fsim[-1]:
                xc = (1 + psi * rho) * xbar - psi * rho * sim[-1]
                fxc = func(xc)
                if fxc <= fxr:
                    sim[-1] = xc
                    fsim[-1] = fxc
                else:
                    doshrink = 1
            else:
                xcc = (1 - psi) * xbar + psi * sim[-1]
                fxcc = func(xcc)
                if fxcc < fsim[-1]:
                    sim[-1] = xcc
                    fsim[-1] = fxcc
                else:
                    doshrink = 1
            if doshrink:
                for j in one2np1:
                    sim[j] = sim[0] + sigma * (sim[j] - sim[0])
                    fsim[j] = func(sim[j])

        ind = numpy.argsort(fsim)
        sim = numpy.take(sim, ind, 0)
        fsim = numpy.take(fsim, ind, 0)
        if callback is not None:
            callback(sim[0])
        iterations += 1
        if retall:
            allvecs.append(sim[0])

    x = sim[0]
    fval = numpy.min(fsim)
    warnflag = 0
    if fcalls[0] >= maxfun:
        warnflag = 1
        msg = _status_message['maxfev']
        if disp:
            print('Warning: ' + msg)
    elif iterations >= maxiter:
        warnflag = 2
        msg = _status_message['maxiter']
        if disp:
            print('Warning: ' + msg)
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % iterations)
            print('         Function evaluations: %d' % fcalls[0])
    result = Result(fun=fval, nit=iterations, nfev=fcalls[0], status=warnflag, success=warnflag == 0, message=msg, x=x)
    if retall:
        result['allvecs'] = allvecs
    return result


def approx_fprime(xk, f, epsilon, *args):
    r"""Finite-difference approximation of the gradient of a scalar function.

    Parameters
    ----------
    xk : array_like
        The coordinate vector at which to determine the gradient of `f`.
    f : callable
        The function of which to determine the gradient (partial derivatives).
        Should take `xk` as first argument, other arguments to `f` can be
        supplied in ``*args``.  Should return a scalar, the value of the
        function at `xk`.
    epsilon : array_like
        Increment to `xk` to use for determining the function gradient.
        If a scalar, uses the same finite difference delta for all partial
        derivatives.  If an array, should contain one value per element of
        `xk`.
    \*args : args, optional
        Any other arguments that are to be passed to `f`.

    Returns
    -------
    grad : ndarray
        The partial derivatives of `f` to `xk`.

    See Also
    --------
    check_grad : Check correctness of gradient function against approx_fprime.

    Notes
    -----
    The function gradient is determined by the forward finite difference
    formula::

                 f(xk[i] + epsilon[i]) - f(xk[i])
        f'[i] = ---------------------------------
                            epsilon[i]

    The main use of `approx_fprime` is in scalar function optimizers like
    `fmin_bfgs`, to determine numerically the Jacobian of a function.

    Examples
    --------
    >>> from scipy import optimize
    >>> def func(x, c0, c1):
    ...     "Coordinate vector `x` should be an array of size two."
    ...     return c0 * x[0]**2 + c1*x[1]**2

    >>> x = np.ones(2)
    >>> c0, c1 = (1, 200)
    >>> eps = np.sqrt(np.finfo(np.float).eps)
    >>> optimize.approx_fprime(x, func, [eps, np.sqrt(200) * eps], c0, c1)
    array([   2.        ,  400.00004198])

    """
    f0 = f(*((xk,) + args))
    grad = numpy.zeros((len(xk),), float)
    ei = numpy.zeros((len(xk),), float)
    for k in range(len(xk)):
        ei[k] = 1.0
        d = epsilon * ei
        grad[k] = (f(*((xk + d,) + args)) - f0) / d[k]
        ei[k] = 0.0

    return grad


def check_grad(func, grad, x0, *args):
    r"""Check the correctness of a gradient function by comparing it against a
    (forward) finite-difference approximation of the gradient.

    Parameters
    ----------
    func : callable func(x0,*args)
        Function whose derivative is to be checked.
    grad : callable grad(x0, *args)
        Gradient of `func`.
    x0 : ndarray
        Points to check `grad` against forward difference approximation of grad
        using `func`.
    args : \*args, optional
        Extra arguments passed to `func` and `grad`.

    Returns
    -------
    err : float
        The square root of the sum of squares (i.e. the 2-norm) of the
        difference between ``grad(x0, *args)`` and the finite difference
        approximation of `grad` using func at the points `x0`.

    See Also
    --------
    approx_fprime

    """
    return sqrt(sum((grad(x0, *args) - approx_fprime(x0, func, _epsilon, *args)) ** 2))


def approx_fhess_p(x0, p, fprime, epsilon, *args):
    f2 = fprime(*((x0 + epsilon * p,) + args))
    f1 = fprime(*((x0,) + args))
    return (f2 - f1) / epsilon


def fmin_bfgs(f, x0, fprime=None, args=(), gtol=1e-05, norm=Inf, epsilon=_epsilon, maxiter=None, full_output=0, disp=1, retall=0, callback=None):
    """
    Minimize a function using the BFGS algorithm.

    Parameters
    ----------
    f : callable f(x,*args)
        Objective function to be minimized.
    x0 : ndarray
        Initial guess.
    fprime : callable f'(x,*args), optional
        Gradient of f.
    args : tuple, optional
        Extra arguments passed to f and fprime.
    gtol : float, optional
        Gradient norm must be less than gtol before succesful termination.
    norm : float, optional
        Order of norm (Inf is max, -Inf is min)
    epsilon : int or ndarray, optional
        If fprime is approximated, use this value for the step size.
    callback : callable, optional
        An optional user-supplied function to call after each
        iteration.  Called as callback(xk), where xk is the
        current parameter vector.
    maxiter : int, optional
        Maximum number of iterations to perform.
    full_output : bool, optional
        If True,return fopt, func_calls, grad_calls, and warnflag
        in addition to xopt.
    disp : bool, optional
        Print convergence message if True.
    retall : bool, optional
        Return a list of results at each iteration if True.

    Returns
    -------
    xopt : ndarray
        Parameters which minimize f, i.e. f(xopt) == fopt.
    fopt : float
        Minimum value.
    gopt : ndarray
        Value of gradient at minimum, f'(xopt), which should be near 0.
    Bopt : ndarray
        Value of 1/f''(xopt), i.e. the inverse hessian matrix.
    func_calls : int
        Number of function_calls made.
    grad_calls : int
        Number of gradient calls made.
    warnflag : integer
        1 : Maximum number of iterations exceeded.
        2 : Gradient and/or function calls not changing.
    allvecs  :  list
        Results at each iteration.  Only returned if retall is True.

    See also
    --------
    minimize: Interface to minimization algorithms for multivariate
        functions. See the 'BFGS' `method` in particular.

    Notes
    -----
    Optimize the function, f, whose gradient is given by fprime
    using the quasi-Newton method of Broyden, Fletcher, Goldfarb,
    and Shanno (BFGS)

    References
    ----------
    Wright, and Nocedal 'Numerical Optimization', 1999, pg. 198.

    """
    opts = {'gtol': gtol, 'norm': norm, 
       'eps': epsilon, 
       'disp': disp, 
       'maxiter': maxiter, 
       'return_all': retall}
    res = _minimize_bfgs(f, x0, args, fprime, callback=callback, **opts)
    if full_output:
        retlist = (
         res['x'], res['fun'], res['jac'], res['hess'],
         res['nfev'], res['njev'], res['status'])
        if retall:
            retlist += (res['allvecs'],)
        return retlist
    if retall:
        return (res['x'], res['allvecs'])
    else:
        return res['x']


def _minimize_bfgs(fun, x0, args=(), jac=None, callback=None, gtol=1e-05, norm=Inf, eps=_epsilon, maxiter=None, disp=False, return_all=False, **unknown_options):
    """
    Minimization of scalar function of one or more variables using the
    BFGS algorithm.

    Options for the BFGS algorithm are:
        disp : bool
            Set to True to print convergence messages.
        maxiter : int
            Maximum number of iterations to perform.
        gtol : float
            Gradient norm must be less than `gtol` before successful
            termination.
        norm : float
            Order of norm (Inf is max, -Inf is min).
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    This function is called by the `minimize` function with `method=BFGS`.
    It is not supposed to be called directly.
    """
    _check_unknown_options(unknown_options)
    f = fun
    fprime = jac
    epsilon = eps
    retall = return_all
    x0 = asarray(x0).flatten()
    if x0.ndim == 0:
        x0.shape = (1, )
    if maxiter is None:
        maxiter = len(x0) * 200
    func_calls, f = wrap_function(f, args)
    if fprime is None:
        grad_calls, myfprime = wrap_function(approx_fprime, (f, epsilon))
    else:
        grad_calls, myfprime = wrap_function(fprime, args)
    gfk = myfprime(x0)
    k = 0
    N = len(x0)
    I = numpy.eye(N, dtype=int)
    Hk = I
    old_fval = f(x0)
    old_old_fval = old_fval + 5000
    xk = x0
    if retall:
        allvecs = [
         x0]
    sk = [
     2 * gtol]
    warnflag = 0
    gnorm = vecnorm(gfk, ord=norm)
    while gnorm > gtol and k < maxiter:
        pk = -numpy.dot(Hk, gfk)
        alpha_k, fc, gc, old_fval2, old_old_fval2, gfkp1 = line_search_wolfe1(f, myfprime, xk, pk, gfk, old_fval, old_old_fval)
        if alpha_k is not None:
            old_fval = old_fval2
            old_old_fval = old_old_fval2
        else:
            alpha_k, fc, gc, old_fval, old_old_fval, gfkp1 = line_search_wolfe2(f, myfprime, xk, pk, gfk, old_fval, old_old_fval)
            if alpha_k is None:
                warnflag = 2
                break
        xkp1 = xk + alpha_k * pk
        if retall:
            allvecs.append(xkp1)
        sk = xkp1 - xk
        xk = xkp1
        if gfkp1 is None:
            gfkp1 = myfprime(xkp1)
        yk = gfkp1 - gfk
        gfk = gfkp1
        if callback is not None:
            callback(xk)
        k += 1
        gnorm = vecnorm(gfk, ord=norm)
        if gnorm <= gtol:
            break
        if not numpy.isfinite(old_fval):
            warnflag = 2
            break
        try:
            rhok = 1.0 / numpy.dot(yk, sk)
        except ZeroDivisionError:
            rhok = 1000.0
            if disp:
                print('Divide-by-zero encountered: rhok assumed large')

        if isinf(rhok):
            rhok = 1000.0
            if disp:
                print('Divide-by-zero encountered: rhok assumed large')
        A1 = I - sk[:, numpy.newaxis] * yk[numpy.newaxis, :] * rhok
        A2 = I - yk[:, numpy.newaxis] * sk[numpy.newaxis, :] * rhok
        Hk = numpy.dot(A1, numpy.dot(Hk, A2)) + rhok * sk[:, numpy.newaxis] * sk[numpy.newaxis, :]

    fval = old_fval
    if warnflag == 2:
        msg = _status_message['pr_loss']
        if disp:
            print('Warning: ' + msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    elif k >= maxiter:
        warnflag = 1
        msg = _status_message['maxiter']
        if disp:
            print('Warning: ' + msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    result = Result(fun=fval, jac=gfk, hess=Hk, nfev=func_calls[0], njev=grad_calls[0], status=warnflag, success=warnflag == 0, message=msg, x=xk)
    if retall:
        result['allvecs'] = allvecs
    return result


def fmin_cg(f, x0, fprime=None, args=(), gtol=1e-05, norm=Inf, epsilon=_epsilon, maxiter=None, full_output=0, disp=1, retall=0, callback=None):
    """
    Minimize a function using a nonlinear conjugate gradient algorithm.

    Parameters
    ----------
    f : callable, ``f(x, *args)``
        Objective function to be minimized.  Here `x` must be a 1-D array of
        the variables that are to be changed in the search for a minimum, and
        `args` are the other (fixed) parameters of `f`.
    x0 : ndarray
        A user-supplied initial estimate of `xopt`, the optimal value of `x`.
        It must be a 1-D array of values.
    fprime : callable, ``fprime(x, *args)``, optional
        A function that returns the gradient of `f` at `x`. Here `x` and `args`
        are as described above for `f`. The returned value must be a 1-D array.
        Defaults to None, in which case the gradient is approximated
        numerically (see `epsilon`, below).
    args : tuple, optional
        Parameter values passed to `f` and `fprime`. Must be supplied whenever
        additional fixed parameters are needed to completely specify the
        functions `f` and `fprime`.
    gtol : float, optional
        Stop when the norm of the gradient is less than `gtol`.
    norm : float, optional
        Order to use for the norm of the gradient
        (``-np.Inf`` is min, ``np.Inf`` is max).
    epsilon : float or ndarray, optional
        Step size(s) to use when `fprime` is approximated numerically. Can be a
        scalar or a 1-D array.  Defaults to ``sqrt(eps)``, with eps the
        floating point machine precision.  Usually ``sqrt(eps)`` is about
        1.5e-8.
    maxiter : int, optional
        Maximum number of iterations to perform. Default is ``200 * len(x0)``.
    full_output : bool, optional
        If True, return `fopt`, `func_calls`, `grad_calls`, and `warnflag` in
        addition to `xopt`.  See the Returns section below for additional
        information on optional return values.
    disp : bool, optional
        If True, return a convergence message, followed by `xopt`.
    retall : bool, optional
        If True, add to the returned values the results of each iteration.
    callback : callable, optional
        An optional user-supplied function, called after each iteration.
        Called as ``callback(xk)``, where ``xk`` is the current value of `x0`.

    Returns
    -------
    xopt : ndarray
        Parameters which minimize f, i.e. ``f(xopt) == fopt``.
    fopt : float, optional
        Minimum value found, f(xopt).  Only returned if `full_output` is True.
    func_calls : int, optional
        The number of function_calls made.  Only returned if `full_output`
        is True.
    grad_calls : int, optional
        The number of gradient calls made. Only returned if `full_output` is
        True.
    warnflag : int, optional
        Integer value with warning status, only returned if `full_output` is
        True.

        0 : Success.

        1 : The maximum number of iterations was exceeded.

        2 : Gradient and/or function calls were not changing.  May indicate
            that precision was lost, i.e., the routine did not converge.

    allvecs : list of ndarray, optional
        List of arrays, containing the results at each iteration.
        Only returned if `retall` is True.

    See Also
    --------
    minimize : common interface to all `scipy.optimize` algorithms for
               unconstrained and constrained minimization of multivariate
               functions.  It provides an alternative way to call
               ``fmin_cg``, by specifying ``method='CG'``.

    Notes
    -----
    This conjugate gradient algorithm is based on that of Polak and Ribiere
    [1]_.

    Conjugate gradient methods tend to work better when:

    1. `f` has a unique global minimizing point, and no local minima or
       other stationary points,
    2. `f` is, at least locally, reasonably well approximated by a
       quadratic function of the variables,
    3. `f` is continuous and has a continuous gradient,
    4. `fprime` is not too large, e.g., has a norm less than 1000,
    5. The initial guess, `x0`, is reasonably close to `f` 's global
       minimizing point, `xopt`.

    References
    ----------
    .. [1] Wright & Nocedal, "Numerical Optimization", 1999, pp. 120-122.

    Examples
    --------
    Example 1: seek the minimum value of the expression
    ``a*u**2 + b*u*v + c*v**2 + d*u + e*v + f`` for given values
    of the parameters and an initial guess ``(u, v) = (0, 0)``.

    >>> args = (2, 3, 7, 8, 9, 10)  # parameter values
    >>> def f(x, *args):
    ...     u, v = x
    ...     a, b, c, d, e, f = args
    ...     return a*u**2 + b*u*v + c*v**2 + d*u + e*v + f
    >>> def gradf(x, *args):
    ...     u, v = x
    ...     a, b, c, d, e, f = args
    ...     gu = 2*a*u + b*v + d     # u-component of the gradient
    ...     gv = b*u + 2*c*v + e     # v-component of the gradient
    ...     return np.asarray((gu, gv))
    >>> x0 = np.asarray((0, 0))  # Initial guess.
    >>> from scipy import optimize
    >>> res1 = optimize.fmin_cg(f, x0, fprime=gradf, args=args)
    >>> print 'res1 = ', res1
    Optimization terminated successfully.
             Current function value: 1.617021
             Iterations: 2
             Function evaluations: 5
             Gradient evaluations: 5
    res1 =  [-1.80851064 -0.25531915]

    Example 2: solve the same problem using the `minimize` function.
    (This `myopts` dictionary shows all of the available options,
    although in practice only non-default values would be needed.
    The returned value will be a dictionary.)

    >>> opts = {'maxiter' : None,    # default value.
    ...         'disp' : True,    # non-default value.
    ...         'gtol' : 1e-5,    # default value.
    ...         'norm' : np.inf,  # default value.
    ...         'eps' : 1.4901161193847656e-08}  # default value.
    >>> res2 = optimize.minimize(f, x0, jac=gradf, args=args,
    ...                          method='CG', options=opts)
    Optimization terminated successfully.
            Current function value: 1.617021
            Iterations: 2
            Function evaluations: 5
            Gradient evaluations: 5
    >>> res2.x  # minimum found
    array([-1.80851064 -0.25531915])

    """
    opts = {'gtol': gtol, 'norm': norm, 
       'eps': epsilon, 
       'disp': disp, 
       'maxiter': maxiter, 
       'return_all': retall}
    res = _minimize_cg(f, x0, args, fprime, callback=callback, **opts)
    if full_output:
        retlist = (
         res['x'], res['fun'], res['nfev'], res['njev'], res['status'])
        if retall:
            retlist += (res['allvecs'],)
        return retlist
    if retall:
        return (res['x'], res['allvecs'])
    else:
        return res['x']


def _minimize_cg(fun, x0, args=(), jac=None, callback=None, gtol=1e-05, norm=Inf, eps=_epsilon, maxiter=None, disp=False, return_all=False, **unknown_options):
    """
    Minimization of scalar function of one or more variables using the
    conjugate gradient algorithm.

    Options for the conjugate gradient algorithm are:
        disp : bool
            Set to True to print convergence messages.
        maxiter : int
            Maximum number of iterations to perform.
        gtol : float
            Gradient norm must be less than `gtol` before successful
            termination.
        norm : float
            Order of norm (Inf is max, -Inf is min).
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    This function is called by the `minimize` function with `method=CG`. It
    is not supposed to be called directly.
    """
    _check_unknown_options(unknown_options)
    f = fun
    fprime = jac
    epsilon = eps
    retall = return_all
    x0 = asarray(x0).flatten()
    if maxiter is None:
        maxiter = len(x0) * 200
    func_calls, f = wrap_function(f, args)
    if fprime is None:
        grad_calls, myfprime = wrap_function(approx_fprime, (f, epsilon))
    else:
        grad_calls, myfprime = wrap_function(fprime, args)
    gfk = myfprime(x0)
    k = 0
    N = len(x0)
    xk = x0
    old_fval = f(xk)
    old_old_fval = old_fval + 5000
    if retall:
        allvecs = [
         xk]
    sk = [
     2 * gtol]
    warnflag = 0
    pk = -gfk
    gnorm = vecnorm(gfk, ord=norm)
    while gnorm > gtol and k < maxiter:
        deltak = numpy.dot(gfk, gfk)
        old_fval_backup = old_fval
        old_old_fval_backup = old_old_fval
        alpha_k, fc, gc, old_fval, old_old_fval, gfkp1 = line_search_wolfe1(f, myfprime, xk, pk, gfk, old_fval, old_old_fval, c2=0.4)
        if alpha_k is None:
            alpha_k, fc, gc, old_fval, old_old_fval, gfkp1 = line_search_wolfe2(f, myfprime, xk, pk, gfk, old_fval_backup, old_old_fval_backup)
            if alpha_k is None or alpha_k == 0:
                warnflag = 2
                break
        xk = xk + alpha_k * pk
        if retall:
            allvecs.append(xk)
        if gfkp1 is None:
            gfkp1 = myfprime(xk)
        yk = gfkp1 - gfk
        beta_k = max(0, numpy.dot(yk, gfkp1) / deltak)
        pk = -gfkp1 + beta_k * pk
        gfk = gfkp1
        gnorm = vecnorm(gfk, ord=norm)
        if callback is not None:
            callback(xk)
        k += 1

    fval = old_fval
    if warnflag == 2:
        msg = _status_message['pr_loss']
        if disp:
            print('Warning: ' + msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    elif k >= maxiter:
        warnflag = 1
        msg = _status_message['maxiter']
        if disp:
            print('Warning: ' + msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % func_calls[0])
            print('         Gradient evaluations: %d' % grad_calls[0])
    result = Result(fun=fval, jac=gfk, nfev=func_calls[0], njev=grad_calls[0], status=warnflag, success=warnflag == 0, message=msg, x=xk)
    if retall:
        result['allvecs'] = allvecs
    return result


def fmin_ncg(f, x0, fprime, fhess_p=None, fhess=None, args=(), avextol=1e-05, epsilon=_epsilon, maxiter=None, full_output=0, disp=1, retall=0, callback=None):
    """
    Unconstrained minimization of a function using the Newton-CG method.

    Parameters
    ----------
    f : callable ``f(x, *args)``
        Objective function to be minimized.
    x0 : ndarray
        Initial guess.
    fprime : callable ``f'(x, *args)``
        Gradient of f.
    fhess_p : callable ``fhess_p(x, p, *args)``, optional
        Function which computes the Hessian of f times an
        arbitrary vector, p.
    fhess : callable ``fhess(x, *args)``, optional
        Function to compute the Hessian matrix of f.
    args : tuple, optional
        Extra arguments passed to f, fprime, fhess_p, and fhess
        (the same set of extra arguments is supplied to all of
        these functions).
    epsilon : float or ndarray, optional
        If fhess is approximated, use this value for the step size.
    callback : callable, optional
        An optional user-supplied function which is called after
        each iteration.  Called as callback(xk), where xk is the
        current parameter vector.
    avextol : float, optional
        Convergence is assumed when the average relative error in
        the minimizer falls below this amount.
    maxiter : int, optional
        Maximum number of iterations to perform.
    full_output : bool, optional
        If True, return the optional outputs.
    disp : bool, optional
        If True, print convergence message.
    retall : bool, optional
        If True, return a list of results at each iteration.

    Returns
    -------
    xopt : ndarray
        Parameters which minimizer f, i.e. ``f(xopt) == fopt``.
    fopt : float
        Value of the function at xopt, i.e. ``fopt = f(xopt)``.
    fcalls : int
        Number of function calls made.
    gcalls : int
        Number of gradient calls made.
    hcalls : int
        Number of hessian calls made.
    warnflag : int
        Warnings generated by the algorithm.
        1 : Maximum number of iterations exceeded.
    allvecs : list
        The result at each iteration, if retall is True (see below).

    See also
    --------
    minimize: Interface to minimization algorithms for multivariate
        functions. See the 'Newton-CG' `method` in particular.

    Notes
    -----
    Only one of `fhess_p` or `fhess` need to be given.  If `fhess`
    is provided, then `fhess_p` will be ignored.  If neither `fhess`
    nor `fhess_p` is provided, then the hessian product will be
    approximated using finite differences on `fprime`. `fhess_p`
    must compute the hessian times an arbitrary vector. If it is not
    given, finite-differences on `fprime` are used to compute
    it.

    Newton-CG methods are also called truncated Newton methods. This
    function differs from scipy.optimize.fmin_tnc because

    1. scipy.optimize.fmin_ncg is written purely in python using numpy
        and scipy while scipy.optimize.fmin_tnc calls a C function.
    2. scipy.optimize.fmin_ncg is only for unconstrained minimization
        while scipy.optimize.fmin_tnc is for unconstrained minimization
        or box constrained minimization. (Box constraints give
        lower and upper bounds for each variable seperately.)

    References
    ----------
    Wright & Nocedal, 'Numerical Optimization', 1999, pg. 140.

    """
    opts = {'xtol': avextol, 'eps': epsilon, 
       'maxiter': maxiter, 
       'disp': disp, 
       'return_all': retall}
    res = _minimize_newtoncg(f, x0, args, fprime, fhess, fhess_p, callback=callback, **opts)
    if full_output:
        retlist = (
         res['x'], res['fun'], res['nfev'], res['njev'],
         res['nhev'], res['status'])
        if retall:
            retlist += (res['allvecs'],)
        return retlist
    if retall:
        return (res['x'], res['allvecs'])
    else:
        return res['x']


def _minimize_newtoncg(fun, x0, args=(), jac=None, hess=None, hessp=None, callback=None, xtol=1e-05, eps=_epsilon, maxiter=None, disp=False, return_all=False, **unknown_options):
    """
    Minimization of scalar function of one or more variables using the
    Newton-CG algorithm.

    Options for the Newton-CG algorithm are:
        disp : bool
            Set to True to print convergence messages.
        xtol : float
            Average relative error in solution `xopt` acceptable for
            convergence.
        maxiter : int
            Maximum number of iterations to perform.
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    This function is called by the `minimize` function with
    `method=Newton-CG`. It is not supposed to be called directly.

    Also note that the `jac` parameter (Jacobian) is required.
    """
    _check_unknown_options(unknown_options)
    if jac is None:
        raise ValueError('Jacobian is required for Newton-CG method')
    f = fun
    fprime = jac
    fhess_p = hessp
    fhess = hess
    avextol = xtol
    epsilon = eps
    retall = return_all
    x0 = asarray(x0).flatten()
    fcalls, f = wrap_function(f, args)
    gcalls, fprime = wrap_function(fprime, args)
    hcalls = 0
    if maxiter is None:
        maxiter = len(x0) * 200
    xtol = len(x0) * avextol
    update = [2 * xtol]
    xk = x0
    if retall:
        allvecs = [
         xk]
    k = 0
    old_fval = f(x0)
    while numpy.add.reduce(numpy.abs(update)) > xtol and k < maxiter:
        b = -fprime(xk)
        maggrad = numpy.add.reduce(numpy.abs(b))
        eta = numpy.min([0.5, numpy.sqrt(maggrad)])
        termcond = eta * maggrad
        xsupi = zeros(len(x0), dtype=x0.dtype)
        ri = -b
        psupi = -ri
        i = 0
        dri0 = numpy.dot(ri, ri)
        if fhess is not None:
            A = fhess(*((xk,) + args))
            hcalls = hcalls + 1
        while numpy.add.reduce(numpy.abs(ri)) > termcond:
            if fhess is None:
                if fhess_p is None:
                    Ap = approx_fhess_p(xk, psupi, fprime, epsilon)
                else:
                    Ap = fhess_p(xk, psupi, *args)
                    hcalls = hcalls + 1
            else:
                Ap = numpy.dot(A, psupi)
            Ap = asarray(Ap).squeeze()
            curv = numpy.dot(psupi, Ap)
            if 0 <= curv <= 3 * numpy.finfo(numpy.float64).eps:
                break
            elif curv < 0:
                if i > 0:
                    break
                else:
                    xsupi = xsupi + dri0 / curv * psupi
                    break
            alphai = dri0 / curv
            xsupi = xsupi + alphai * psupi
            ri = ri + alphai * Ap
            dri1 = numpy.dot(ri, ri)
            betai = dri1 / dri0
            psupi = -ri + betai * psupi
            i = i + 1
            dri0 = dri1

        pk = xsupi
        gfk = -b
        alphak, fc, gc, old_fval = line_search_BFGS(f, xk, pk, gfk, old_fval)
        update = alphak * pk
        xk = xk + update
        if callback is not None:
            callback(xk)
        if retall:
            allvecs.append(xk)
        k += 1

    fval = old_fval
    if k >= maxiter:
        warnflag = 1
        msg = _status_message['maxiter']
        if disp:
            print('Warning: ' + msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % fcalls[0])
            print('         Gradient evaluations: %d' % gcalls[0])
            print('         Hessian evaluations: %d' % hcalls)
    else:
        warnflag = 0
        msg = _status_message['success']
        if disp:
            print(msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % k)
            print('         Function evaluations: %d' % fcalls[0])
            print('         Gradient evaluations: %d' % gcalls[0])
            print('         Hessian evaluations: %d' % hcalls)
    result = Result(fun=fval, jac=gfk, nfev=fcalls[0], njev=gcalls[0], nhev=hcalls, status=warnflag, success=warnflag == 0, message=msg, x=xk)
    if retall:
        result['allvecs'] = allvecs
    return result


def fminbound(func, x1, x2, args=(), xtol=1e-05, maxfun=500, full_output=0, disp=1):
    """Bounded minimization for scalar functions.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to be minimized (must accept and return scalars).
    x1, x2 : float or array scalar
        The optimization bounds.
    args : tuple, optional
        Extra arguments passed to function.
    xtol : float, optional
        The convergence tolerance.
    maxfun : int, optional
        Maximum number of function evaluations allowed.
    full_output : bool, optional
        If True, return optional outputs.
    disp : int, optional
        If non-zero, print messages.
            0 : no message printing.
            1 : non-convergence notification messages only.
            2 : print a message on convergence too.
            3 : print iteration results.

    Returns
    -------
    xopt : ndarray
        Parameters (over given interval) which minimize the
        objective function.
    fval : number
        The function value at the minimum point.
    ierr : int
        An error flag (0 if converged, 1 if maximum number of
        function calls reached).
    numfunc : int
      The number of function calls made.

    See also
    --------
    minimize_scalar: Interface to minimization algorithms for scalar
        univariate functions. See the 'Bounded' `method` in particular.

    Notes
    -----
    Finds a local minimizer of the scalar function `func` in the
    interval x1 < xopt < x2 using Brent's method.  (See `brent`
    for auto-bracketing).

    """
    options = {'xtol': xtol, 'maxiter': maxfun, 
       'disp': disp}
    res = _minimize_scalar_bounded(func, (x1, x2), args, **options)
    if full_output:
        return (res['x'], res['fun'], res['status'], res['nfev'])
    else:
        return res['x']


def _minimize_scalar_bounded(func, bounds, args=(), xtol=1e-05, maxiter=500, disp=0, **unknown_options):
    _check_unknown_options(unknown_options)
    maxfun = maxiter
    if len(bounds) != 2:
        raise ValueError('bounds must have two elements.')
    x1, x2 = bounds
    if not (is_array_scalar(x1) and is_array_scalar(x2)):
        raise ValueError('Optimisation bounds must be scalars or array scalars.')
    if x1 > x2:
        raise ValueError('The lower bound exceeds the upper bound.')
    flag = 0
    header = ' Func-count     x          f(x)          Procedure'
    step = '       initial'
    sqrt_eps = sqrt(2.2e-16)
    golden_mean = 0.5 * (3.0 - sqrt(5.0))
    a, b = x1, x2
    fulc = a + golden_mean * (b - a)
    nfc, xf = fulc, fulc
    rat = e = 0.0
    x = xf
    fx = func(x, *args)
    num = 1
    fmin_data = (1, xf, fx)
    ffulc = fnfc = fx
    xm = 0.5 * (a + b)
    tol1 = sqrt_eps * numpy.abs(xf) + xtol / 3.0
    tol2 = 2.0 * tol1
    if disp > 2:
        print(' ')
        print(header)
        print('%5.0f   %12.6g %12.6g %s' % (fmin_data + (step,)))
    while numpy.abs(xf - xm) > tol2 - 0.5 * (b - a):
        golden = 1
        if numpy.abs(e) > tol1:
            golden = 0
            r = (xf - nfc) * (fx - ffulc)
            q = (xf - fulc) * (fx - fnfc)
            p = (xf - fulc) * q - (xf - nfc) * r
            q = 2.0 * (q - r)
            if q > 0.0:
                p = -p
            q = numpy.abs(q)
            r = e
            e = rat
            if numpy.abs(p) < numpy.abs(0.5 * q * r) and p > q * (a - xf) and p < q * (b - xf):
                rat = (p + 0.0) / q
                x = xf + rat
                step = '       parabolic'
                if x - a < tol2 or b - x < tol2:
                    si = numpy.sign(xm - xf) + (xm - xf == 0)
                    rat = tol1 * si
            else:
                golden = 1
        if golden:
            if xf >= xm:
                e = a - xf
            else:
                e = b - xf
            rat = golden_mean * e
            step = '       golden'
        si = numpy.sign(rat) + (rat == 0)
        x = xf + si * numpy.max([numpy.abs(rat), tol1])
        fu = func(x, *args)
        num += 1
        fmin_data = (num, x, fu)
        if disp > 2:
            print('%5.0f   %12.6g %12.6g %s' % (fmin_data + (step,)))
        if fu <= fx:
            if x >= xf:
                a = xf
            else:
                b = xf
            fulc, ffulc = nfc, fnfc
            nfc, fnfc = xf, fx
            xf, fx = x, fu
        else:
            if x < xf:
                a = x
            else:
                b = x
            if fu <= fnfc or nfc == xf:
                fulc, ffulc = nfc, fnfc
                nfc, fnfc = x, fu
            elif fu <= ffulc or fulc == xf or fulc == nfc:
                fulc, ffulc = x, fu
        xm = 0.5 * (a + b)
        tol1 = sqrt_eps * numpy.abs(xf) + xtol / 3.0
        tol2 = 2.0 * tol1
        if num >= maxfun:
            flag = 1
            break

    fval = fx
    if disp > 0:
        _endprint(x, flag, fval, maxfun, xtol, disp)
    result = Result(fun=fval, status=flag, success=flag == 0, message={0: 'Solution found.', 1: 'Maximum number of function calls reached.'}.get(flag, ''), x=xf, nfev=num)
    return result


class Brent():

    def __init__(self, func, args=(), tol=1.48e-08, maxiter=500, full_output=0):
        self.func = func
        self.args = args
        self.tol = tol
        self.maxiter = maxiter
        self._mintol = 1e-11
        self._cg = 0.381966
        self.xmin = None
        self.fval = None
        self.iter = 0
        self.funcalls = 0
        return

    def set_bracket(self, brack=None):
        self.brack = brack

    def get_bracket_info(self):
        func = self.func
        args = self.args
        brack = self.brack
        if brack is None:
            xa, xb, xc, fa, fb, fc, funcalls = bracket(func, args=args)
        elif len(brack) == 2:
            xa, xb, xc, fa, fb, fc, funcalls = bracket(func, xa=brack[0], xb=brack[1], args=args)
        elif len(brack) == 3:
            xa, xb, xc = brack
            if xa > xc:
                dum = xa
                xa = xc
                xc = dum
            if not (xa < xb and xb < xc):
                raise ValueError('Not a bracketing interval.')
            fa = func(*((xa,) + args))
            fb = func(*((xb,) + args))
            fc = func(*((xc,) + args))
            if not (fb < fa and fb < fc):
                raise ValueError('Not a bracketing interval.')
            funcalls = 3
        else:
            raise ValueError('Bracketing interval must be length 2 or 3 sequence.')
        return (
         xa, xb, xc, fa, fb, fc, funcalls)

    def optimize(self):
        func = self.func
        xa, xb, xc, fa, fb, fc, funcalls = self.get_bracket_info()
        _mintol = self._mintol
        _cg = self._cg
        x = w = v = xb
        fw = fv = fx = func(*((x,) + self.args))
        if xa < xc:
            a = xa
            b = xc
        else:
            a = xc
            b = xa
        deltax = 0.0
        funcalls = 1
        iter = 0
        while iter < self.maxiter:
            tol1 = self.tol * numpy.abs(x) + _mintol
            tol2 = 2.0 * tol1
            xmid = 0.5 * (a + b)
            if numpy.abs(x - xmid) < tol2 - 0.5 * (b - a):
                xmin = x
                fval = fx
                break
            if numpy.abs(deltax) <= tol1:
                if x >= xmid:
                    deltax = a - x
                else:
                    deltax = b - x
                rat = _cg * deltax
            else:
                tmp1 = (x - w) * (fx - fv)
                tmp2 = (x - v) * (fx - fw)
                p = (x - v) * tmp2 - (x - w) * tmp1
                tmp2 = 2.0 * (tmp2 - tmp1)
                if tmp2 > 0.0:
                    p = -p
                tmp2 = numpy.abs(tmp2)
                dx_temp = deltax
                deltax = rat
                if p > tmp2 * (a - x) and p < tmp2 * (b - x) and numpy.abs(p) < numpy.abs(0.5 * tmp2 * dx_temp):
                    rat = p * 1.0 / tmp2
                    u = x + rat
                    if u - a < tol2 or b - u < tol2:
                        if xmid - x >= 0:
                            rat = tol1
                        else:
                            rat = -tol1
                else:
                    if x >= xmid:
                        deltax = a - x
                    else:
                        deltax = b - x
                    rat = _cg * deltax
            if numpy.abs(rat) < tol1:
                if rat >= 0:
                    u = x + tol1
                else:
                    u = x - tol1
            else:
                u = x + rat
            fu = func(*((u,) + self.args))
            funcalls += 1
            if fu > fx:
                if u < x:
                    a = u
                else:
                    b = u
                if fu <= fw or w == x:
                    v = w
                    w = u
                    fv = fw
                    fw = fu
                elif fu <= fv or v == x or v == w:
                    v = u
                    fv = fu
            else:
                if u >= x:
                    a = x
                else:
                    b = x
                v = w
                w = x
                x = u
                fv = fw
                fw = fx
                fx = fu
            iter += 1

        self.xmin = x
        self.fval = fx
        self.iter = iter
        self.funcalls = funcalls

    def get_result(self, full_output=False):
        if full_output:
            return (self.xmin, self.fval, self.iter, self.funcalls)
        else:
            return self.xmin


def brent(func, args=(), brack=None, tol=1.48e-08, full_output=0, maxiter=500):
    """
    Given a function of one-variable and a possible bracketing interval,
    return the minimum of the function isolated to a fractional precision of
    tol.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function.
    args
        Additional arguments (if present).
    brack : tuple
        Triple (a,b,c) where (a<b<c) and func(b) <
        func(a),func(c).  If bracket consists of two numbers (a,c)
        then they are assumed to be a starting interval for a
        downhill bracket search (see `bracket`); it doesn't always
        mean that the obtained solution will satisfy a<=x<=c.
    tol : float
        Stop if between iteration change is less than `tol`.
    full_output : bool
        If True, return all output args (xmin, fval, iter,
        funcalls).
    maxiter : int
        Maximum number of iterations in solution.

    Returns
    -------
    xmin : ndarray
        Optimum point.
    fval : float
        Optimum value.
    iter : int
        Number of iterations.
    funcalls : int
        Number of objective function evaluations made.

    See also
    --------
    minimize_scalar: Interface to minimization algorithms for scalar
        univariate functions. See the 'Brent' `method` in particular.

    Notes
    -----
    Uses inverse parabolic interpolation when possible to speed up
    convergence of golden section method.

    """
    options = {'xtol': tol, 'maxiter': maxiter}
    res = _minimize_scalar_brent(func, brack, args, **options)
    if full_output:
        return (res['x'], res['fun'], res['nit'], res['nfev'])
    else:
        return res['x']


def _minimize_scalar_brent(func, brack=None, args=(), xtol=1.48e-08, maxiter=500, **unknown_options):
    _check_unknown_options(unknown_options)
    tol = xtol
    brent = Brent(func=func, args=args, tol=tol, full_output=True, maxiter=maxiter)
    brent.set_bracket(brack)
    brent.optimize()
    x, fval, nit, nfev = brent.get_result(full_output=True)
    return Result(fun=fval, x=x, nit=nit, nfev=nfev)


def golden(func, args=(), brack=None, tol=_epsilon, full_output=0):
    """
    Return the minimum of a function of one variable.

    Given a function of one variable and a possible bracketing interval,
    return the minimum of the function isolated to a fractional precision of
    tol.

    Parameters
    ----------
    func : callable func(x,*args)
        Objective function to minimize.
    args : tuple
        Additional arguments (if present), passed to func.
    brack : tuple
        Triple (a,b,c), where (a<b<c) and func(b) <
        func(a),func(c).  If bracket consists of two numbers (a,
        c), then they are assumed to be a starting interval for a
        downhill bracket search (see `bracket`); it doesn't always
        mean that obtained solution will satisfy a<=x<=c.
    tol : float
        x tolerance stop criterion
    full_output : bool
        If True, return optional outputs.

    See also
    --------
    minimize_scalar: Interface to minimization algorithms for scalar
        univariate functions. See the 'Golden' `method` in particular.

    Notes
    -----
    Uses analog of bisection method to decrease the bracketed
    interval.

    """
    options = {'xtol': tol}
    res = _minimize_scalar_golden(func, brack, args, **options)
    if full_output:
        return (res['x'], res['fun'], res['nfev'])
    else:
        return res['x']


def _minimize_scalar_golden(func, brack=None, args=(), xtol=_epsilon, **unknown_options):
    _check_unknown_options(unknown_options)
    tol = xtol
    if brack is None:
        xa, xb, xc, fa, fb, fc, funcalls = bracket(func, args=args)
    else:
        if len(brack) == 2:
            xa, xb, xc, fa, fb, fc, funcalls = bracket(func, xa=brack[0], xb=brack[1], args=args)
        elif len(brack) == 3:
            xa, xb, xc = brack
            if xa > xc:
                dum = xa
                xa = xc
                xc = dum
            if not (xa < xb and xb < xc):
                raise ValueError('Not a bracketing interval.')
            fa = func(*((xa,) + args))
            fb = func(*((xb,) + args))
            fc = func(*((xc,) + args))
            if not (fb < fa and fb < fc):
                raise ValueError('Not a bracketing interval.')
            funcalls = 3
        else:
            raise ValueError('Bracketing interval must be length 2 or 3 sequence.')
        _gR = 0.61803399
        _gC = 1.0 - _gR
        x3 = xc
        x0 = xa
        if numpy.abs(xc - xb) > numpy.abs(xb - xa):
            x1 = xb
            x2 = xb + _gC * (xc - xb)
        else:
            x2 = xb
            x1 = xb - _gC * (xb - xa)
        f1 = func(*((x1,) + args))
        f2 = func(*((x2,) + args))
        funcalls += 2
        while numpy.abs(x3 - x0) > tol * (numpy.abs(x1) + numpy.abs(x2)):
            if f2 < f1:
                x0 = x1
                x1 = x2
                x2 = _gR * x1 + _gC * x3
                f1 = f2
                f2 = func(*((x2,) + args))
            else:
                x3 = x2
                x2 = x1
                x1 = _gR * x2 + _gC * x0
                f2 = f1
                f1 = func(*((x1,) + args))
            funcalls += 1

    if f1 < f2:
        xmin = x1
        fval = f1
    else:
        xmin = x2
        fval = f2
    return Result(fun=fval, nfev=funcalls, x=xmin)


def bracket(func, xa=0.0, xb=1.0, args=(), grow_limit=110.0, maxiter=1000):
    """
    Bracket the minimum of the function.

    Given a function and distinct initial points, search in the
    downhill direction (as defined by the initital points) and return
    new points xa, xb, xc that bracket the minimum of the function
    f(xa) > f(xb) < f(xc). It doesn't always mean that obtained
    solution will satisfy xa<=x<=xb

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to minimize.
    xa, xb : float, optional
        Bracketing interval. Defaults `xa` to 0.0, and `xb` to 1.0.
    args : tuple, optional
        Additional arguments (if present), passed to `func`.
    grow_limit : float, optional
        Maximum grow limit.  Defaults to 110.0
    maxiter : int, optional
        Maximum number of iterations to perform. Defaults to 1000.

    Returns
    -------
    xa, xb, xc : float
        Bracket.
    fa, fb, fc : float
        Objective function values in bracket.
    funcalls : int
        Number of function evaluations made.

    """
    _gold = 1.618034
    _verysmall_num = 1e-21
    fa = func(*((xa,) + args))
    fb = func(*((xb,) + args))
    if fa < fb:
        dum = xa
        xa = xb
        xb = dum
        dum = fa
        fa = fb
        fb = dum
    xc = xb + _gold * (xb - xa)
    fc = func(*((xc,) + args))
    funcalls = 3
    iter = 0
    while fc < fb:
        tmp1 = (xb - xa) * (fb - fc)
        tmp2 = (xb - xc) * (fb - fa)
        val = tmp2 - tmp1
        if numpy.abs(val) < _verysmall_num:
            denom = 2.0 * _verysmall_num
        else:
            denom = 2.0 * val
        w = xb - ((xb - xc) * tmp2 - (xb - xa) * tmp1) / denom
        wlim = xb + grow_limit * (xc - xb)
        if iter > maxiter:
            raise RuntimeError('Too many iterations.')
        iter += 1
        if (w - xc) * (xb - w) > 0.0:
            fw = func(*((w,) + args))
            funcalls += 1
            if fw < fc:
                xa = xb
                xb = w
                fa = fb
                fb = fw
                return (
                 xa, xb, xc, fa, fb, fc, funcalls)
            if fw > fb:
                xc = w
                fc = fw
                return (xa, xb, xc, fa, fb, fc, funcalls)
            w = xc + _gold * (xc - xb)
            fw = func(*((w,) + args))
            funcalls += 1
        elif (w - wlim) * (wlim - xc) >= 0.0:
            w = wlim
            fw = func(*((w,) + args))
            funcalls += 1
        elif (w - wlim) * (xc - w) > 0.0:
            fw = func(*((w,) + args))
            funcalls += 1
            if fw < fc:
                xb = xc
                xc = w
                w = xc + _gold * (xc - xb)
                fb = fc
                fc = fw
                fw = func(*((w,) + args))
                funcalls += 1
        else:
            w = xc + _gold * (xc - xb)
            fw = func(*((w,) + args))
            funcalls += 1
        xa = xb
        xb = xc
        xc = w
        fa = fb
        fb = fc
        fc = fw

    return (
     xa, xb, xc, fa, fb, fc, funcalls)


def _linesearch_powell(func, p, xi, tol=0.001):
    """Line-search algorithm using fminbound.

    Find the minimium of the function ``func(x0+ alpha*direc)``.

    """

    def myfunc(alpha):
        return func(p + alpha * xi)

    alpha_min, fret, iter, num = brent(myfunc, full_output=1, tol=tol)
    xi = alpha_min * xi
    return (squeeze(fret), p + xi, xi)


def fmin_powell(func, x0, args=(), xtol=0.0001, ftol=0.0001, maxiter=None, maxfun=None, full_output=0, disp=1, retall=0, callback=None, direc=None):
    """
    Minimize a function using modified Powell's method. This method
    only uses function values, not derivatives.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to be minimized.
    x0 : ndarray
        Initial guess.
    args : tuple, optional
        Extra arguments passed to func.
    callback : callable, optional
        An optional user-supplied function, called after each
        iteration.  Called as ``callback(xk)``, where ``xk`` is the
        current parameter vector.
    direc : ndarray, optional
        Initial direction set.
    xtol : float, optional
        Line-search error tolerance.
    ftol : float, optional
        Relative error in ``func(xopt)`` acceptable for convergence.
    maxiter : int, optional
        Maximum number of iterations to perform.
    maxfun : int, optional
        Maximum number of function evaluations to make.
    full_output : bool, optional
        If True, fopt, xi, direc, iter, funcalls, and
        warnflag are returned.
    disp : bool, optional
        If True, print convergence messages.
    retall : bool, optional
        If True, return a list of the solution at each iteration.

    Returns
    -------
    xopt : ndarray
        Parameter which minimizes `func`.
    fopt : number
        Value of function at minimum: ``fopt = func(xopt)``.
    direc : ndarray
        Current direction set.
    iter : int
        Number of iterations.
    funcalls : int
        Number of function calls made.
    warnflag : int
        Integer warning flag:
            1 : Maximum number of function evaluations.
            2 : Maximum number of iterations.
    allvecs : list
        List of solutions at each iteration.

    See also
    --------
    minimize: Interface to unconstrained minimization algorithms for
        multivariate functions. See the 'Powell' `method` in particular.

    Notes
    -----
    Uses a modification of Powell's method to find the minimum of
    a function of N variables. Powell's method is a conjugate
    direction method.

    The algorithm has two loops. The outer loop
    merely iterates over the inner loop. The inner loop minimizes
    over each current direction in the direction set. At the end
    of the inner loop, if certain conditions are met, the direction
    that gave the largest decrease is dropped and replaced with
    the difference between the current estiamted x and the estimated
    x from the beginning of the inner-loop.

    The technical conditions for replacing the direction of greatest
    increase amount to checking that

    1. No further gain can be made along the direction of greatest increase
       from that iteration.
    2. The direction of greatest increase accounted for a large sufficient
       fraction of the decrease in the function value from that iteration of
       the inner loop.

    References
    ----------
    Powell M.J.D. (1964) An efficient method for finding the minimum of a
    function of several variables without calculating derivatives,
    Computer Journal, 7 (2):155-162.

    Press W., Teukolsky S.A., Vetterling W.T., and Flannery B.P.:
    Numerical Recipes (any edition), Cambridge University Press

    """
    opts = {'xtol': xtol, 'ftol': ftol, 
       'maxiter': maxiter, 
       'maxfev': maxfun, 
       'disp': disp, 
       'direc': direc, 
       'return_all': retall}
    res = _minimize_powell(func, x0, args, callback=callback, **opts)
    if full_output:
        retlist = (
         res['x'], res['fun'], res['direc'], res['nit'],
         res['nfev'], res['status'])
        if retall:
            retlist += (res['allvecs'],)
        return retlist
    if retall:
        return (res['x'], res['allvecs'])
    else:
        return res['x']


def _minimize_powell(func, x0, args=(), callback=None, xtol=0.0001, ftol=0.0001, maxiter=None, maxfev=None, disp=False, direc=None, return_all=False, **unknown_options):
    """
    Minimization of scalar function of one or more variables using the
    modified Powell algorithm.

    Options for the Powell algorithm are:
        disp : bool
            Set to True to print convergence messages.
        xtol : float
            Relative error in solution `xopt` acceptable for convergence.
        ftol : float
            Relative error in ``fun(xopt)`` acceptable for convergence.
        maxiter : int
            Maximum number of iterations to perform.
        maxfev : int
            Maximum number of function evaluations to make.
        direc : ndarray
            Initial set of direction vectors for the Powell method.

    This function is called by the `minimize` function with
    `method=Powell`. It is not supposed to be called directly.
    """
    _check_unknown_options(unknown_options)
    maxfun = maxfev
    retall = return_all
    fcalls, func = wrap_function(func, args)
    x = asarray(x0).flatten()
    if retall:
        allvecs = [
         x]
    N = len(x)
    rank = len(x.shape)
    if not -1 < rank < 2:
        raise ValueError('Initial guess must be a scalar or rank-1 sequence.')
    if maxiter is None:
        maxiter = N * 1000
    if maxfun is None:
        maxfun = N * 1000
    if direc is None:
        direc = eye(N, dtype=float)
    else:
        direc = asarray(direc, dtype=float)
    fval = squeeze(func(x))
    x1 = x.copy()
    iter = 0
    ilist = list(range(N))
    while True:
        fx = fval
        bigind = 0
        delta = 0.0
        for i in ilist:
            direc1 = direc[i]
            fx2 = fval
            fval, x, direc1 = _linesearch_powell(func, x, direc1, tol=xtol * 100)
            if fx2 - fval > delta:
                delta = fx2 - fval
                bigind = i

        iter += 1
        if callback is not None:
            callback(x)
        if retall:
            allvecs.append(x)
        if 2.0 * (fx - fval) <= ftol * (numpy.abs(fx) + numpy.abs(fval)) + 1e-20:
            break
        if fcalls[0] >= maxfun:
            break
        if iter >= maxiter:
            break
        direc1 = x - x1
        x2 = 2 * x - x1
        x1 = x.copy()
        fx2 = squeeze(func(x2))
        if fx > fx2:
            t = 2.0 * (fx + fx2 - 2.0 * fval)
            temp = fx - fval - delta
            t *= temp * temp
            temp = fx - fx2
            t -= delta * temp * temp
            if t < 0.0:
                fval, x, direc1 = _linesearch_powell(func, x, direc1, tol=xtol * 100)
                direc[bigind] = direc[-1]
                direc[-1] = direc1

    warnflag = 0
    if fcalls[0] >= maxfun:
        warnflag = 1
        msg = _status_message['maxfev']
        if disp:
            print('Warning: ' + msg)
    elif iter >= maxiter:
        warnflag = 2
        msg = _status_message['maxiter']
        if disp:
            print('Warning: ' + msg)
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print('         Current function value: %f' % fval)
            print('         Iterations: %d' % iter)
            print('         Function evaluations: %d' % fcalls[0])
    x = squeeze(x)
    result = Result(fun=fval, direc=direc, nit=iter, nfev=fcalls[0], status=warnflag, success=warnflag == 0, message=msg, x=x)
    if retall:
        result['allvecs'] = allvecs
    return result


def _endprint(x, flag, fval, maxfun, xtol, disp):
    if flag == 0:
        if disp > 1:
            print('\nOptimization terminated successfully;\nThe returned value satisfies the termination criteria\n(using xtol = ', xtol, ')')
    if flag == 1:
        if disp:
            print('\nMaximum number of function evaluations exceeded --- increase maxfun argument.\n')


def brute(func, ranges, args=(), Ns=20, full_output=0, finish=fmin, disp=False):
    """Minimize a function over a given range by brute force.

    Parameters
    ----------
    func : callable ``f(x,*args)``
        Objective function to be minimized.
    ranges : tuple
        Each element is a tuple of parameters or a slice object to
        be handed to ``numpy.mgrid``.
    args : tuple
        Extra arguments passed to function.
    Ns : int
        Default number of samples, if those are not provided.
    full_output : bool
        If True, return the evaluation grid.
    finish : callable, optional
        An optimization function that is called with the result of brute force
        minimization as initial guess.  `finish` should take the initial guess
        as positional argument, and take take `args`, `full_output` and `disp`
        as keyword arguments.  See Notes for more details.
    disp : bool, optional
        Set to True to print convergence messages.

    Returns
    -------
    x0 : ndarray
        Value of arguments to `func`, giving minimum over the grid.
    fval : int
        Function value at minimum.
    grid : tuple
        Representation of the evaluation grid.  It has the same
        length as x0.
    Jout : ndarray
        Function values over grid:  ``Jout = func(*grid)``.

    Notes
    -----
    The range is respected by the brute force minimization, but if the `finish`
    keyword specifies another optimization function (including the default
    `fmin`), the returned value may still be (just) outside the range.  In
    order to ensure the range is specified, use ``finish=None``.

    """
    N = len(ranges)
    if N > 40:
        raise ValueError('Brute Force not possible with more than 40 variables.')
    lrange = list(ranges)
    for k in range(N):
        if type(lrange[k]) is not type(slice(None)):
            if len(lrange[k]) < 3:
                lrange[k] = tuple(lrange[k]) + (complex(Ns),)
            lrange[k] = slice(*lrange[k])

    if N == 1:
        lrange = lrange[0]

    def _scalarfunc(*params):
        params = squeeze(asarray(params))
        return func(params, *args)

    vecfunc = vectorize(_scalarfunc)
    grid = mgrid[lrange]
    if N == 1:
        grid = (
         grid,)
    Jout = vecfunc(*grid)
    Nshape = shape(Jout)
    indx = argmin(Jout.ravel(), axis=-1)
    Nindx = zeros(N, int)
    xmin = zeros(N, float)
    for k in range(N - 1, -1, -1):
        thisN = Nshape[k]
        Nindx[k] = indx % Nshape[k]
        indx = indx // thisN

    for k in range(N):
        xmin[k] = grid[k][tuple(Nindx)]

    Jmin = Jout[tuple(Nindx)]
    if N == 1:
        grid = grid[0]
        xmin = xmin[0]
    if callable(finish):
        vals = finish(func, xmin, args=args, full_output=1, disp=disp)
        xmin = vals[0]
        Jmin = vals[1]
        if vals[-1] > 0:
            if disp:
                print('Warning: Final optimization did not succeed')
    if full_output:
        return (xmin, Jmin, grid, Jout)
    else:
        return xmin
        return


def show_options(solver, method=None):
    """
    Show documentation for additional options of optimization solvers.

    These are method-specific options that can be supplied through the
    ``options`` dict.

    Parameters
    ----------
    solver : str
        Type of optimization solver. One of {`minimize`, `root`}.
    method : str, optional
        If not given, shows all methods of the specified solver. Otherwise,
        show only the options for the specified method. Valid values
        corresponds to methods' names of respective solver (e.g. 'BFGS' for
        'minimize').

    Notes
    -----

    ** minimize options

    * BFGS options:
        gtol : float
            Gradient norm must be less than `gtol` before successful
            termination.
        norm : float
            Order of norm (Inf is max, -Inf is min).
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    * Nelder-Mead options:
        xtol : float
            Relative error in solution `xopt` acceptable for convergence.
        ftol : float
            Relative error in ``fun(xopt)`` acceptable for convergence.
        maxfev : int
            Maximum number of function evaluations to make.

    * Newton-CG options:
        xtol : float
            Average relative error in solution `xopt` acceptable for
            convergence.
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    * CG options:
        gtol : float
            Gradient norm must be less than `gtol` before successful
            termination.
        norm : float
            Order of norm (Inf is max, -Inf is min).
        eps : float or ndarray
            If `jac` is approximated, use this value for the step size.

    * Powell options:
        xtol : float
            Relative error in solution `xopt` acceptable for convergence.
        ftol : float
            Relative error in ``fun(xopt)`` acceptable for convergence.
        maxfev : int
            Maximum number of function evaluations to make.
        direc : ndarray
            Initial set of direction vectors for the Powell method.

    * Anneal options:
        ftol : float
            Relative error in ``fun(x)`` acceptable for convergence.
        schedule : str
            Annealing schedule to use. One of: 'fast', 'cauchy' or
            'boltzmann'.
        T0 : float
            Initial Temperature (estimated as 1.2 times the largest
            cost-function deviation over random points in the range).
        Tf : float
            Final goal temperature.
        maxfev : int
            Maximum number of function evaluations to make.
        maxaccept : int
            Maximum changes to accept.
        boltzmann : float
            Boltzmann constant in acceptance test (increase for less
            stringent test at each temperature).
        learn_rate : float
            Scale constant for adjusting guesses.
        quench, m, n : float
            Parameters to alter fast_sa schedule.
        lower, upper : float or ndarray
            Lower and upper bounds on `x`.
        dwell : int
            The number of times to search the space at each temperature.

    * L-BFGS-B options:
        ftol : float
            The iteration stops when ``(f^k -
            f^{k+1})/max{|f^k|,|f^{k+1}|,1} <= ftol``.
        gtol : float
            The iteration will stop when ``max{|proj g_i | i = 1, ..., n}
            <= gtol`` where ``pg_i`` is the i-th component of the
            projected gradient.
        maxcor : int
            The maximum number of variable metric corrections used to
            define the limited memory matrix. (The limited memory BFGS
            method does not store the full hessian but uses this many terms
            in an approximation to it.)
        maxiter : int
            Maximum number of function evaluations.

    * TNC options:
        ftol : float
            Precision goal for the value of f in the stoping criterion.
            If ftol < 0.0, ftol is set to 0.0 defaults to -1.
        xtol : float
            Precision goal for the value of x in the stopping
            criterion (after applying x scaling factors).  If xtol <
            0.0, xtol is set to sqrt(machine_precision).  Defaults to
            -1.
        gtol : float
            Precision goal for the value of the projected gradient in
            the stopping criterion (after applying x scaling factors).
            If gtol < 0.0, gtol is set to 1e-2 * sqrt(accuracy).
            Setting it to 0.0 is not recommended.  Defaults to -1.
        scale : list of floats
            Scaling factors to apply to each variable.  If None, the
            factors are up-low for interval bounded variables and
            1+|x] fo the others.  Defaults to None
        offset : float
            Value to substract from each variable.  If None, the
            offsets are (up+low)/2 for interval bounded variables
            and x for the others.
        maxCGit : int
            Maximum number of hessian*vector evaluations per main
            iteration.  If maxCGit == 0, the direction chosen is
            -gradient if maxCGit < 0, maxCGit is set to
            max(1,min(50,n/2)).  Defaults to -1.
        maxiter : int
            Maximum number of function evaluation.  if None, `maxiter` is
            set to max(100, 10*len(x0)).  Defaults to None.
        eta : float
            Severity of the line search. if < 0 or > 1, set to 0.25.
            Defaults to -1.
        stepmx : float
            Maximum step for the line search.  May be increased during
            call.  If too small, it will be set to 10.0.  Defaults to 0.
        accuracy : float
            Relative precision for finite difference calculations.  If
            <= machine_precision, set to sqrt(machine_precision).
            Defaults to 0.
        minfev : float
            Minimum function value estimate.  Defaults to 0.
        rescale : float
            Scaling factor (in log10) used to trigger f value
            rescaling.  If 0, rescale at each iteration.  If a large
            value, never rescale.  If < 0, rescale is set to 1.3.

    * COBYLA options:
        tol : float
            Final accuracy in the optimization (not precisely guaranteed).
            This is a lower bound on the size of the trust region.
        rhobeg : float
            Reasonable initial changes to the variables.
        maxfev : int
            Maximum number of function evaluations.

    * SLSQP options:
        ftol : float
            Precision goal for the value of f in the stopping criterion.
        eps : float
            Step size used for numerical approximation of the jacobian.
        maxiter : int
            Maximum number of iterations.

    ** root options

    * hybrd options:
        col_deriv : bool
            Specify whether the Jacobian function computes derivatives down
            the columns (faster, because there is no transpose operation).
        xtol : float
            The calculation will terminate if the relative error between
            two consecutive iterates is at most `xtol`.
        maxfev : int
            The maximum number of calls to the function. If zero, then
            ``100*(N+1)`` is the maximum where N is the number of elements
            in `x0`.
        band : sequence
            If set to a two-sequence containing the number of sub- and
            super-diagonals within the band of the Jacobi matrix, the
            Jacobi matrix is considered banded (only for ``fprime=None``).
        epsfcn : float
            A suitable step length for the forward-difference approximation
            of the Jacobian (for ``fprime=None``). If `epsfcn` is less than
            the machine precision, it is assumed that the relative errors
            in the functions are of the order of the machine precision.
        factor : float
            A parameter determining the initial step bound (``factor * ||
            diag * x||``).  Should be in the interval ``(0.1, 100)``.
        diag : sequence
            N positive entries that serve as a scale factors for the
            variables.

    * LM options:
        col_deriv : bool
            non-zero to specify that the Jacobian function computes derivatives
            down the columns (faster, because there is no transpose operation).
        ftol : float
            Relative error desired in the sum of squares.
        xtol : float
            Relative error desired in the approximate solution.
        gtol : float
            Orthogonality desired between the function vector and the columns
            of the Jacobian.
        maxfev : int
            The maximum number of calls to the function. If zero, then
            100*(N+1) is the maximum where N is the number of elements in x0.
        epsfcn : float
            A suitable step length for the forward-difference approximation of
            the Jacobian (for Dfun=None). If epsfcn is less than the machine
            precision, it is assumed that the relative errors in the functions
            are of the order of the machine precision.
        factor : float
            A parameter determining the initial step bound
            (``factor * || diag * x||``). Should be in interval ``(0.1, 100)``.
        diag : sequence
            N positive entries that serve as a scale factors for the variables.

    * Broyden1 options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    Initial guess for the Jacobian is (-1/alpha).
                reduction_method : str or tuple, optional
                    Method used in ensuring that the rank of the Broyden
                    matrix stays low. Can either be a string giving the
                    name of the method, or a tuple of the form ``(method,
                    param1, param2, ...)`` that gives the name of the
                    method and values for additional parameters.

                    Methods available:
                        - ``restart``: drop all matrix columns. Has no
                            extra parameters.
                        - ``simple``: drop oldest matrix column. Has no
                            extra parameters.
                        - ``svd``: keep only the most significant SVD
                            components.
                          Extra parameters:
                              - ``to_retain`: number of SVD components to
                                  retain when rank reduction is done.
                                  Default is ``max_rank - 2``.
                max_rank : int, optional
                    Maximum rank for the Broyden matrix.
                    Default is infinity (ie., no rank reduction).

    * Broyden2 options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    Initial guess for the Jacobian is (-1/alpha).
                reduction_method : str or tuple, optional
                    Method used in ensuring that the rank of the Broyden
                    matrix stays low. Can either be a string giving the
                    name of the method, or a tuple of the form ``(method,
                    param1, param2, ...)`` that gives the name of the
                    method and values for additional parameters.

                    Methods available:
                        - ``restart``: drop all matrix columns. Has no
                            extra parameters.
                        - ``simple``: drop oldest matrix column. Has no
                            extra parameters.
                        - ``svd``: keep only the most significant SVD
                            components.
                          Extra parameters:
                              - ``to_retain`: number of SVD components to
                                  retain when rank reduction is done.
                                  Default is ``max_rank - 2``.
                max_rank : int, optional
                    Maximum rank for the Broyden matrix.
                    Default is infinity (ie., no rank reduction).

    * Anderson options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    Initial guess for the Jacobian is (-1/alpha).
                M : float, optional
                    Number of previous vectors to retain. Defaults to 5.
                w0 : float, optional
                    Regularization parameter for numerical stability.
                    Compared to unity, good values of the order of 0.01.

    * LinearMixing options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    initial guess for the jacobian is (-1/alpha).

    * DiagBroyden options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    initial guess for the jacobian is (-1/alpha).

    * ExcitingMixing options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                alpha : float, optional
                    Initial Jacobian approximation is (-1/alpha).
                alphamax : float, optional
                    The entries of the diagonal Jacobian are kept in the range
                    ``[alpha, alphamax]``.

    * Krylov options:
        nit : int, optional
            Number of iterations to make. If omitted (default), make as many
            as required to meet tolerances.
        disp : bool, optional
            Print status to stdout on every iteration.
        maxiter : int, optional
            Maximum number of iterations to make. If more are needed to
            meet convergence, `NoConvergence` is raised.
        ftol : float, optional
            Relative tolerance for the residual. If omitted, not used.
        fatol : float, optional
            Absolute tolerance (in max-norm) for the residual.
            If omitted, default is 6e-6.
        xtol : float, optional
            Relative minimum step size. If omitted, not used.
        xatol : float, optional
            Absolute minimum step size, as determined from the Jacobian
            approximation. If the step size is smaller than this, optimization
            is terminated as successful. If omitted, not used.
        tol_norm : function(vector) -> scalar, optional
            Norm to use in convergence check. Default is the maximum norm.
        line_search : {None, 'armijo' (default), 'wolfe'}, optional
            Which type of a line search to use to determine the step size in
            the direction given by the Jacobian approximation. Defaults to
            'armijo'.
        jac_options : dict, optional
            Options for the respective Jacobian approximation.
                rdiff : float, optional
                    Relative step size to use in numerical differentiation.
                method : {'lgmres', 'gmres', 'bicgstab', 'cgs', 'minres'} or
                    function
                    Krylov method to use to approximate the Jacobian.
                    Can be a string, or a function implementing the same
                    interface as the iterative solvers in
                    `scipy.sparse.linalg`.

                    The default is `scipy.sparse.linalg.lgmres`.
                inner_M : LinearOperator or InverseJacobian
                    Preconditioner for the inner Krylov iteration.
                    Note that you can use also inverse Jacobians as (adaptive)
                    preconditioners. For example,

                    >>> jac = BroydenFirst()
                    >>> kjac = KrylovJacobian(inner_M=jac.inverse).

                    If the preconditioner has a method named 'update', it will
                    be called as ``update(x, f)`` after each nonlinear step,
                    with ``x`` giving the current point, and ``f`` the current
                    function value.
                inner_tol, inner_maxiter, ...
                    Parameters to pass on to the "inner" Krylov solver.
                    See `scipy.sparse.linalg.gmres` for details.
                outer_k : int, optional
                    Size of the subspace kept across LGMRES nonlinear
                    iterations.

                    See `scipy.sparse.linalg.lgmres` for details.

    """
    solver = solver.lower()
    if solver not in ('minimize', 'root'):
        raise ValueError('Unknown solver.')
    solver_header = ' ' * 4 + solver + '\n' + ' ' * 4 + '~' * len(solver)
    notes_header = 'Notes\n    -----'
    all_doc = show_options.__doc__.split(notes_header)[1:]
    solvers_doc = [ s.strip() for s in show_options.__doc__.split('** ')[1:]
                  ]
    solver_doc = [ s for s in solvers_doc if s.lower().startswith(solver)
                 ]
    if method is None:
        doc = solver_doc
    else:
        doc = solver_doc[0].split('* ')[1:]
        doc = [ s.strip() for s in doc ]
        doc = [ s for s in doc if s.lower().startswith(method.lower()) ]
    print(('\n').join(doc))
    return


def main():
    import time
    times = []
    algor = []
    x0 = [
     0.8, 1.2, 0.7]
    print('Nelder-Mead Simplex')
    print('===================')
    start = time.time()
    x = fmin(rosen, x0)
    print(x)
    times.append(time.time() - start)
    algor.append('Nelder-Mead Simplex\t')
    print()
    print('Powell Direction Set Method')
    print('===========================')
    start = time.time()
    x = fmin_powell(rosen, x0)
    print(x)
    times.append(time.time() - start)
    algor.append('Powell Direction Set Method.')
    print()
    print('Nonlinear CG')
    print('============')
    start = time.time()
    x = fmin_cg(rosen, x0, fprime=rosen_der, maxiter=200)
    print(x)
    times.append(time.time() - start)
    algor.append('Nonlinear CG     \t')
    print()
    print('BFGS Quasi-Newton')
    print('=================')
    start = time.time()
    x = fmin_bfgs(rosen, x0, fprime=rosen_der, maxiter=80)
    print(x)
    times.append(time.time() - start)
    algor.append('BFGS Quasi-Newton\t')
    print()
    print('BFGS approximate gradient')
    print('=========================')
    start = time.time()
    x = fmin_bfgs(rosen, x0, gtol=0.0001, maxiter=100)
    print(x)
    times.append(time.time() - start)
    algor.append('BFGS without gradient\t')
    print()
    print('Newton-CG with Hessian product')
    print('==============================')
    start = time.time()
    x = fmin_ncg(rosen, x0, rosen_der, fhess_p=rosen_hess_prod, maxiter=80)
    print(x)
    times.append(time.time() - start)
    algor.append('Newton-CG with hessian product')
    print()
    print('Newton-CG with full Hessian')
    print('===========================')
    start = time.time()
    x = fmin_ncg(rosen, x0, rosen_der, fhess=rosen_hess, maxiter=80)
    print(x)
    times.append(time.time() - start)
    algor.append('Newton-CG with full hessian')
    print()
    print('\nMinimizing the Rosenbrock function of order 3\n')
    print(' Algorithm \t\t\t       Seconds')
    print('===========\t\t\t      =========')
    for k in range(len(algor)):
        print(algor[k], '\t -- ', times[k])


if __name__ == '__main__':
    main()