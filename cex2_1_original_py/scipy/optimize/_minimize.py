# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\optimize\_minimize.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Unified interfaces to minimization algorithms.

Functions
---------
- minimize : minimization of a function of several variables.
- minimize_scalar : minimization of a function of one variable.
"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'minimize', 'minimize_scalar']
from warnings import warn
from numpy import any
from scipy.lib.six import callable
from .optimize import _minimize_neldermead, _minimize_powell, _minimize_cg, _minimize_bfgs, _minimize_newtoncg, _minimize_scalar_brent, _minimize_scalar_bounded, _minimize_scalar_golden, MemoizeJac
from .anneal import _minimize_anneal
from .lbfgsb import _minimize_lbfgsb
from .tnc import _minimize_tnc
from .cobyla import _minimize_cobyla
from .slsqp import _minimize_slsqp

def minimize(fun, x0, args=(), method='BFGS', jac=None, hess=None, hessp=None, bounds=None, constraints=(), tol=None, callback=None, options=None):
    """
    Minimization of scalar function of one or more variables.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    fun : callable
        Objective function.
    x0 : ndarray
        Initial guess.
    args : tuple, optional
        Extra arguments passed to the objective function and its
        derivatives (Jacobian, Hessian).
    method : str, optional
        Type of solver.  Should be one of

            - 'Nelder-Mead'
            - 'Powell'
            - 'CG'
            - 'BFGS'
            - 'Newton-CG'
            - 'Anneal'
            - 'L-BFGS-B'
            - 'TNC'
            - 'COBYLA'
            - 'SLSQP'

    jac : bool or callable, optional
        Jacobian of objective function. Only for CG, BFGS, Newton-CG.
        If `jac` is a Boolean and is True, `fun` is assumed to return the
        value of Jacobian along with the objective function. If False, the
        Jacobian will be estimated numerically.
        `jac` can also be a callable returning the Jacobian of the
        objective. In this case, it must accept the same arguments as `fun`.
    hess, hessp : callable, optional
        Hessian of objective function or Hessian of objective function
        times an arbitrary vector p.  Only for Newton-CG.
        Only one of `hessp` or `hess` needs to be given.  If `hess` is
        provided, then `hessp` will be ignored.  If neither `hess` nor
        `hessp` is provided, then the hessian product will be approximated
        using finite differences on `jac`. `hessp` must compute the Hessian
        times an arbitrary vector.
    bounds : sequence, optional
        Bounds for variables (only for L-BFGS-B, TNC, COBYLA and SLSQP).
        ``(min, max)`` pairs for each element in ``x``, defining
        the bounds on that parameter. Use None for one of ``min`` or
        ``max`` when there is no bound in that direction.
    constraints : dict or sequence of dict, optional
        Constraints definition (only for COBYLA and SLSQP).
        Each constraint is defined in a dictionary with fields:
            type : str
                Constraint type: 'eq' for equality, 'ineq' for inequality.
            fun : callable
                The function defining the constraint.
            jac : callable, optional
                The Jacobian of `fun` (only for SLSQP).
            args : sequence, optional
                Extra arguments to be passed to the function and Jacobian.
        Equality constraint means that the constraint function result is to
        be zero whereas inequality means that it is to be non-negative.
        Note that COBYLA only supports inequality constraints.
    tol : float, optional
        Tolerance for termination. For detailed control, use solver-specific
        options.
    options : dict, optional
        A dictionary of solver options. All methods accept the following
        generic options:
            maxiter : int
                Maximum number of iterations to perform.
            disp : bool
                Set to True to print convergence messages.
        For method-specific options, see `show_options('minimize', method)`.
    callback : callable, optional
        Called after each iteration, as ``callback(xk)``, where ``xk`` is the
        current parameter vector.

    Returns
    -------
    res : Result
        The optimization result represented as a ``Result`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the optimizer exited successfully and
        ``message`` which describes the cause of the termination. See
        `Result` for a description of other attributes.

    See also
    --------
    minimize_scalar: Interface to minimization algorithms for scalar
        univariate functions.

    Notes
    -----
    This section describes the available solvers that can be selected by the
    'method' parameter. The default method is *BFGS*.

    **Unconstrained minimization**

    Method *Nelder-Mead* uses the Simplex algorithm [1]_, [2]_. This
    algorithm has been successful in many applications but other algorithms
    using the first and/or second derivatives information might be preferred
    for their better performances and robustness in general.

    Method *Powell* is a modification of Powell's method [3]_, [4]_ which
    is a conjugate direction method. It performs sequential one-dimensional
    minimizations along each vector of the directions set (`direc` field in
    `options` and `info`), which is updated at each iteration of the main
    minimization loop. The function need not be differentiable, and no
    derivatives are taken.

    Method *CG* uses a nonlinear conjugate gradient algorithm by Polak and
    Ribiere, a variant of the Fletcher-Reeves method described in [5]_ pp.
    120-122. Only the first derivatives are used.

    Method *BFGS* uses the quasi-Newton method of Broyden, Fletcher,
    Goldfarb, and Shanno (BFGS) [5]_ pp. 136. It uses the first derivatives
    only. BFGS has proven good performance even for non-smooth
    optimizations

    Method *Newton-CG* uses a Newton-CG algorithm [5]_ pp. 168 (also known
    as the truncated Newton method). It uses a CG method to the compute the
    search direction. See also *TNC* method for a box-constrained
    minimization with a similar algorithm.

    Method *Anneal* uses simulated annealing, which is a probabilistic
    metaheuristic algorithm for global optimization. It uses no derivative
    information from the function being optimized.

    **Constrained minimization**

    Method *L-BFGS-B* uses the L-BFGS-B algorithm [6]_, [7]_ for bound
    constrained minimization.

    Method *TNC* uses a truncated Newton algorithm [5]_, [8]_ to minimize a
    function with variables subject to bounds. This algorithm is uses
    gradient information; it is also called Newton Conjugate-Gradient. It
    differs from the *Newton-CG* method described above as it wraps a C
    implementation and allows each variable to be given upper and lower
    bounds.

    Method *COBYLA* uses the Constrained Optimization BY Linear
    Approximation (COBYLA) method [9]_, [10]_, [11]_. The algorithm is
    based on linear approximations to the objective function and each
    constraint. The method wraps a FORTRAN implementation of the algorithm.

    Method *SLSQP* uses Sequential Least SQuares Programming to minimize a
    function of several variables with any combination of bounds, equality
    and inequality constraints. The method wraps the SLSQP Optimization
    subroutine originally implemented by Dieter Kraft [12]_.

    References
    ----------
    .. [1] Nelder, J A, and R Mead. 1965. A Simplex Method for Function
        Minimization. The Computer Journal 7: 308-13.
    .. [2] Wright M H. 1996. Direct search methods: Once scorned, now
        respectable, in Numerical Analysis 1995: Proceedings of the 1995
        Dundee Biennial Conference in Numerical Analysis (Eds. D F
        Griffiths and G A Watson). Addison Wesley Longman, Harlow, UK.
        191-208.
    .. [3] Powell, M J D. 1964. An efficient method for finding the minimum of
       a function of several variables without calculating derivatives. The
       Computer Journal 7: 155-162.
    .. [4] Press W, S A Teukolsky, W T Vetterling and B P Flannery.
       Numerical Recipes (any edition), Cambridge University Press.
    .. [5] Nocedal, J, and S J Wright. 2006. Numerical Optimization.
       Springer New York.
    .. [6] Byrd, R H and P Lu and J. Nocedal. 1995. A Limited Memory
       Algorithm for Bound Constrained Optimization. SIAM Journal on
       Scientific and Statistical Computing 16 (5): 1190-1208.
    .. [7] Zhu, C and R H Byrd and J Nocedal. 1997. L-BFGS-B: Algorithm
       778: L-BFGS-B, FORTRAN routines for large scale bound constrained
       optimization. ACM Transactions on Mathematical Software 23 (4):
       550-560.
    .. [8] Nash, S G. Newton-Type Minimization Via the Lanczos Method.
       1984. SIAM Journal of Numerical Analysis 21: 770-778.
    .. [9] Powell, M J D. A direct search optimization method that models
       the objective and constraint functions by linear interpolation.
       1994. Advances in Optimization and Numerical Analysis, eds. S. Gomez
       and J-P Hennart, Kluwer Academic (Dordrecht), 51-67.
    .. [10] Powell M J D. Direct search algorithms for optimization
       calculations. 1998. Acta Numerica 7: 287-336.
    .. [11] Powell M J D. A view of algorithms for optimization without
       derivatives. 2007.Cambridge University Technical Report DAMTP
       2007/NA03
    .. [12] Kraft, D. A software package for sequential quadratic
       programming. 1988. Tech. Rep. DFVLR-FB 88-28, DLR German Aerospace
       Center -- Institute for Flight Mechanics, Koln, Germany.

    Examples
    --------
    Let us consider the problem of minimizing the Rosenbrock function. This
    function (and its respective derivatives) is implemented in `rosen`
    (resp. `rosen_der`, `rosen_hess`) in the `scipy.optimize`.

    >>> from scipy.optimize import minimize, rosen, rosen_der

    A simple application of the *Nelder-Mead* method is:

    >>> x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    >>> res = minimize(rosen, x0, method='Nelder-Mead')
    >>> res.x
    [ 1.  1.  1.  1.  1.]

    Now using the *BFGS* algorithm, using the first derivative and a few
    options:

    >>> res = minimize(rosen, x0, method='BFGS', jac=rosen_der,
    ...                options={'gtol': 1e-6, 'disp': True})
    Optimization terminated successfully.
             Current function value: 0.000000
             Iterations: 52
             Function evaluations: 64
             Gradient evaluations: 64
    >>> res.x
    [ 1.  1.  1.  1.  1.]
    >>> print res.message
    Optimization terminated successfully.
    >>> res.hess
    [[ 0.00749589  0.01255155  0.02396251  0.04750988  0.09495377]
     [ 0.01255155  0.02510441  0.04794055  0.09502834  0.18996269]
     [ 0.02396251  0.04794055  0.09631614  0.19092151  0.38165151]
     [ 0.04750988  0.09502834  0.19092151  0.38341252  0.7664427 ]
     [ 0.09495377  0.18996269  0.38165151  0.7664427   1.53713523]]

    Next, consider a minimization problem with several constraints (namely
    Example 16.4 from [5]_). The objective function is:

    >>> fun = lambda x: (x[0] - 1)**2 + (x[1] - 2.5)**2

    There are three constraints defined as:

    >>> cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
    ...         {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
    ...         {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2})

    And variables must be positive, hence the following bounds:

    >>> bnds = ((0, None), (0, None))

    The optimization problem is solved using the SLSQP method as:

    >>> res = minimize(fun, (2, 0), method='SLSQP', bounds=bnds,
    ...                constraints=cons)

    It should converge to the theoretical solution (1.4 ,1.7).

    """
    meth = method.lower()
    if options is None:
        options = {}
    if meth in ('nelder-mead', 'powell', 'anneal', 'cobyla') and bool(jac):
        warn('Method %s does not use gradient information (jac).' % method, RuntimeWarning)
    if meth != 'newton-cg' and hess is not None:
        warn('Method %s does not use Hessian information (hess).' % method, RuntimeWarning)
    if meth in ('nelder-mead', 'powell', 'cg', 'bfgs', 'newton-cg') and (bounds is not None or any(constraints)):
        warn('Method %s cannot handle constraints nor bounds.' % method, RuntimeWarning)
    if meth in ('l-bfgs-b', 'tnc') and any(constraints):
        warn('Method %s cannot handle constraints.' % method, RuntimeWarning)
    if meth is 'cobyla' and bounds is not None:
        warn('Method %s cannot handle bounds.' % method, RuntimeWarning)
    if meth in ('anneal', 'cobyla', 'slsqp') and callback is not None:
        warn('Method %s does not support callback.' % method, RuntimeWarning)
    if meth in ('anneal', 'l-bfgs-b', 'tnc', 'cobyla', 'slsqp') and options.get('return_all', False):
        warn('Method %s does not support the return_all option.' % method, RuntimeWarning)
    if not callable(jac):
        if bool(jac):
            fun = MemoizeJac(fun)
            jac = fun.derivative
        else:
            jac = None
    if tol is not None:
        options = dict(options)
        if meth in ('nelder-mead', 'newton-cg', 'powell', 'tnc'):
            options.setdefault('xtol', tol)
        if meth in ('nelder-mead', 'powell', 'anneal', 'l-bfgs-b', 'tnc', 'slsqp'):
            options.setdefault('ftol', tol)
        if meth in ('bfgs', 'cg', 'l-bfgs-b', 'tnc'):
            options.setdefault('gtol', tol)
        if meth in ('cobyla', ):
            options.setdefault('tol', tol)
    if meth == 'nelder-mead':
        return _minimize_neldermead(fun, x0, args, callback, **options)
    else:
        if meth == 'powell':
            return _minimize_powell(fun, x0, args, callback, **options)
        if meth == 'cg':
            return _minimize_cg(fun, x0, args, jac, callback, **options)
        if meth == 'bfgs':
            return _minimize_bfgs(fun, x0, args, jac, callback, **options)
        if meth == 'newton-cg':
            return _minimize_newtoncg(fun, x0, args, jac, hess, hessp, callback, **options)
        if meth == 'anneal':
            return _minimize_anneal(fun, x0, args, **options)
        if meth == 'l-bfgs-b':
            return _minimize_lbfgsb(fun, x0, args, jac, bounds, callback=callback, **options)
        if meth == 'tnc':
            return _minimize_tnc(fun, x0, args, jac, bounds, callback=callback, **options)
        if meth == 'cobyla':
            return _minimize_cobyla(fun, x0, args, constraints, **options)
        if meth == 'slsqp':
            return _minimize_slsqp(fun, x0, args, jac, bounds, constraints, **options)
        raise ValueError('Unknown solver %s' % method)
        return


def minimize_scalar(fun, bracket=None, bounds=None, args=(), method='brent', tol=None, options=None):
    """
    Minimization of scalar function of one variable.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    fun : callable
        Objective function.
        Scalar function, must return a scalar.
    bracket : sequence, optional
        For methods 'brent' and 'golden', `bracket` defines the bracketing
        interval and can either have three items `(a, b, c)` so that `a < b
        < c` and `fun(b) < fun(a), fun(c)` or two items `a` and `c` which
        are assumed to be a starting interval for a downhill bracket search
        (see `bracket`); it doesn't always mean that the obtained solution
        will satisfy `a <= x <= c`.
    bounds : sequence, optional
        For method 'bounded', `bounds` is mandatory and must have two items
        corresponding to the optimization bounds.
    args : tuple, optional
        Extra arguments passed to the objective function.
    method : str, optional
        Type of solver.  Should be one of

            - 'Brent'
            - 'Bounded'
            - 'Golden'
    tol : float, optional
        Tolerance for termination. For detailed control, use solver-specific
        options.
    options : dict, optional
        A dictionary of solver options.
            xtol : float
                Relative error in solution `xopt` acceptable for
                convergence.
            maxiter : int
                Maximum number of iterations to perform.
            disp : bool
                Set to True to print convergence messages.

    Returns
    -------
    res : Result
        The optimization result represented as a ``Result`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the optimizer exited successfully and
        ``message`` which describes the cause of the termination. See
        `Result` for a description of other attributes.

    See also
    --------
    minimize: Interface to minimization algorithms for scalar multivariate
        functions.

    Notes
    -----
    This section describes the available solvers that can be selected by the
    'method' parameter. The default method is *Brent*.

    Method *Brent* uses Brent's algorithm to find a local minimum.
    The algorithm uses inverse parabolic interpolation when possible to
    speed up convergence of the golden section method.

    Method *Golden* uses the golden section search technique. It uses
    analog of the bisection method to decrease the bracketed interval. It
    is usually preferable to use the *Brent* method.

    Method *Bounded* can perform bounded minimization. It uses the Brent
    method to find a local minimum in the interval x1 < xopt < x2.

    Examples
    --------
    Consider the problem of minimizing the following function.

    >>> def f(x):
    ...     return (x - 2) * x * (x + 2)**2

    Using the *Brent* method, we find the local minimum as:

    >>> from scipy.optimize import minimize_scalar
    >>> res = minimize_scalar(f)
    >>> res.x
    1.28077640403

    Using the *Bounded* method, we find a local minimum with specified
    bounds as:

    >>> res = minimize_scalar(f, bounds=(-3, -1), method='bounded')
    >>> res.x
    -2.0000002026

    """
    meth = method.lower()
    if options is None:
        options = {}
    if tol is not None:
        options = dict(options)
        options.setdefault('xtol', tol)
    if meth == 'brent':
        return _minimize_scalar_brent(fun, bracket, args, **options)
    else:
        if meth == 'bounded':
            if bounds is None:
                raise ValueError('The `bounds` parameter is mandatory for method `bounded`.')
            return _minimize_scalar_bounded(fun, bounds, args, **options)
        if meth == 'golden':
            return _minimize_scalar_golden(fun, bracket, args, **options)
        raise ValueError('Unknown solver %s' % method)
        return