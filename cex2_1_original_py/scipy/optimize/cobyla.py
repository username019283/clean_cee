# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\optimize\cobyla.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Interface to Constrained Optimization By Linear Approximation

Functions
---------
.. autosummary::
   :toctree: generated/

    fmin_cobyla

"""
from __future__ import division, print_function, absolute_import
import numpy as np
from scipy.lib.six import callable
from scipy.optimize import _cobyla
from .optimize import Result, _check_unknown_options
from warnings import warn
__all__ = [
 'fmin_cobyla']

def fmin_cobyla(func, x0, cons, args=(), consargs=None, rhobeg=1.0, rhoend=0.0001, iprint=1, maxfun=1000, disp=None):
    r"""
    Minimize a function using the Constrained Optimization BY Linear
    Approximation (COBYLA) method. This method wraps a FORTRAN
    implentation of the algorithm.

    Parameters
    ----------
    func : callable
        Function to minimize. In the form func(x, \*args).
    x0 : ndarray
        Initial guess.
    cons : sequence
        Constraint functions; must all be ``>=0`` (a single function
        if only 1 constraint). Each function takes the parameters `x`
        as its first argument.
    args : tuple
        Extra arguments to pass to function.
    consargs : tuple
        Extra arguments to pass to constraint functions (default of None means
        use same extra arguments as those passed to func).
        Use ``()`` for no extra arguments.
    rhobeg :
        Reasonable initial changes to the variables.
    rhoend :
        Final accuracy in the optimization (not precisely guaranteed). This
        is a lower bound on the size of the trust region.
    iprint : {0, 1, 2, 3}
        Controls the frequency of output; 0 implies no output.  Deprecated.
    disp : {0, 1, 2, 3}
        Over-rides the iprint interface.  Preferred.
    maxfun : int
        Maximum number of function evaluations.

    Returns
    -------
    x : ndarray
        The argument that minimises `f`.

    See also
    --------
    minimize: Interface to minimization algorithms for multivariate
        functions. See the 'COBYLA' `method` in particular.

    Notes
    -----
    This algorithm is based on linear approximations to the objective
    function and each constraint. We briefly describe the algorithm.

    Suppose the function is being minimized over k variables. At the
    jth iteration the algorithm has k+1 points v_1, ..., v_(k+1),
    an approximate solution x_j, and a radius RHO_j.
    (i.e. linear plus a constant) approximations to the objective
    function and constraint functions such that their function values
    agree with the linear approximation on the k+1 points v_1,.., v_(k+1).
    This gives a linear program to solve (where the linear approximations
    of the constraint functions are constrained to be non-negative).

    However the linear approximations are likely only good
    approximations near the current simplex, so the linear program is
    given the further requirement that the solution, which
    will become x_(j+1), must be within RHO_j from x_j. RHO_j only
    decreases, never increases. The initial RHO_j is rhobeg and the
    final RHO_j is rhoend. In this way COBYLA's iterations behave
    like a trust region algorithm.

    Additionally, the linear program may be inconsistent, or the
    approximation may give poor improvement. For details about
    how these issues are resolved, as well as how the points v_i are
    updated, refer to the source code or the references below.

    References
    ----------
    Powell M.J.D. (1994), "A direct search optimization method that models
    the objective and constraint functions by linear interpolation.", in
    Advances in Optimization and Numerical Analysis, eds. S. Gomez and
    J-P Hennart, Kluwer Academic (Dordrecht), pp. 51-67

    Powell M.J.D. (1998), "Direct search algorithms for optimization
    calculations", Acta Numerica 7, 287-336

    Powell M.J.D. (2007), "A view of algorithms for optimization without
    derivatives", Cambridge University Technical Report DAMTP 2007/NA03

    Examples
    --------
    Minimize the objective function f(x,y) = x*y subject
    to the constraints x**2 + y**2 < 1 and y > 0::

        >>> def objective(x):
        ...     return x[0]*x[1]
        ...
        >>> def constr1(x):
        ...     return 1 - (x[0]**2 + x[1]**2)
        ...
        >>> def constr2(x):
        ...     return x[1]
        ...
        >>> fmin_cobyla(objective, [0.0, 0.1], [constr1, constr2], rhoend=1e-7)

           Normal return from subroutine COBYLA

           NFVALS =   64   F =-5.000000E-01    MAXCV = 1.998401E-14
           X =-7.071069E-01   7.071067E-01
        array([-0.70710685,  0.70710671])

    The exact solution is (-sqrt(2)/2, sqrt(2)/2).

    """
    err = 'cons must be a sequence of callable functions or a single callable function.'
    try:
        m = len(cons)
    except TypeError:
        if callable(cons):
            m = 1
            cons = [cons]
        else:
            raise TypeError(err)

    for thisfunc in cons:
        if not callable(thisfunc):
            raise TypeError(err)

    if consargs is None:
        consargs = args
    con = tuple({'type': 'ineq', 'fun': c, 'args': consargs} for c in cons)
    if disp is not None:
        iprint = disp
    opts = {'rhobeg': rhobeg, 'tol': rhoend, 'iprint': iprint, 
       'disp': iprint != 0, 
       'maxiter': maxfun}
    return _minimize_cobyla(func, x0, args, constraints=con, **opts)['x']


def _minimize_cobyla(fun, x0, args=(), constraints=(), rhobeg=1.0, tol=0.0001, iprint=1, maxiter=1000, disp=False, **unknown_options):
    """
    Minimize a scalar function of one or more variables using the
    Constrained Optimization BY Linear Approximation (COBYLA) algorithm.

    Options for the COBYLA algorithm are:
        rhobeg : float
            Reasonable initial changes to the variables.
        tol : float
            Final accuracy in the optimization (not precisely guaranteed).
            This is a lower bound on the size of the trust region.
        disp : bool
            Set to True to print convergence messages. If False,
            `verbosity` is ignored as set to 0.
        maxiter : int
            Maximum number of function evaluations.

    This function is called by the `minimize` function with
    `method=COBYLA`. It is not supposed to be called directly.
    """
    _check_unknown_options(unknown_options)
    maxfun = maxiter
    rhoend = tol
    if not disp:
        iprint = 0
    if isinstance(constraints, dict):
        constraints = (
         constraints,)
    for ic, con in enumerate(constraints):
        try:
            ctype = con['type'].lower()
        except KeyError:
            raise KeyError('Constraint %d has no type defined.' % ic)
        except TypeError:
            raise TypeError('Constraints must be defined using a dictionary.')
        except AttributeError:
            raise TypeError("Constraint's type must be a string.")
        else:
            if ctype != 'ineq':
                raise ValueError("Constraints of type '%s' not handled by COBYLA." % con['type'])
            if 'fun' not in con:
                raise KeyError('Constraint %d has no function defined.' % ic)
            if 'args' not in con:
                con['args'] = ()

    m = len(constraints)

    def calcfc(x, con):
        f = fun(x, *args)
        for k, c in enumerate(constraints):
            con[k] = c['fun'](x, *c['args'])

        return f

    info = np.zeros(4, np.float64)
    xopt, info = _cobyla.minimize(calcfc, m=m, x=np.copy(x0), rhobeg=rhobeg, rhoend=rhoend, iprint=iprint, maxfun=maxfun, dinfo=info)
    return Result(x=xopt, status=int(info[0]), success=info[0] == 1, message={1: 'Optimization terminated successfully.', 2: 'Maximum number of function evaluations has been exceeded.', 
       3: 'Rounding errors are becoming damaging in COBYLA subroutine.'}.get(info[0], 'Unknown exit status.'), nfev=int(info[1]), fun=info[2], maxcv=info[3])


if __name__ == '__main__':
    from math import sqrt

    def fun(x):
        return x[0] * x[1]


    def cons(x):
        return 1 - x[0] ** 2 - x[1] ** 2


    x = fmin_cobyla(fun, [1.0, 1.0], cons, iprint=3, disp=1)
    print('\nTheoretical solution: %e, %e' % (1.0 / sqrt(2.0), -1.0 / sqrt(2.0)))