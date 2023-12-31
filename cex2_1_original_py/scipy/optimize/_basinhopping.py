# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\optimize\_basinhopping.pyc
# Compiled at: 2013-02-16 13:27:30
"""
basinhopping: The basinhopping global optimization algorithm
"""
from __future__ import division, print_function, absolute_import
import numpy as np
from numpy import cos, sin
import scipy.optimize, collections
__all__ = [
 'basinhopping']

class Storage(object):

    def __init__(self, x, f):
        """
        Class used to store the lowest energy structure
        """
        self._add(x, f)

    def _add(self, x, f):
        self.x = np.copy(x)
        self.f = f

    def update(self, x, f):
        if f < self.f:
            self._add(x, f)
            return True
        else:
            return False

    def get_lowest(self):
        return (self.x, self.f)


class BasinHoppingRunner(object):

    def __init__(self, x0, minimizer, step_taking, accept_tests, disp=False):
        self.x = np.copy(x0)
        self.minimizer = minimizer
        self.step_taking = step_taking
        self.accept_tests = accept_tests
        self.disp = disp
        self.nstep = 0
        minres = minimizer(self.x)
        self.x = np.copy(minres.x)
        self.energy = minres.fun
        if self.disp:
            print('basinhopping step %d: f %g' % (self.nstep, self.energy))
        self.storage = Storage(self.x, self.energy)
        self.res = scipy.optimize.Result()
        if hasattr(minres, 'nfev'):
            self.res.nfev = minres.nfev
        if hasattr(minres, 'njev'):
            self.res.njev = minres.njev
        if hasattr(minres, 'nhev'):
            self.res.nhev = minres.nhev

    def _monte_carlo_step(self):
        x_after_step = np.copy(self.x)
        x_after_step = self.step_taking(x_after_step)
        minres = self.minimizer(x_after_step)
        x_after_quench = minres.x
        energy_after_quench = minres.fun
        if hasattr(minres, 'success'):
            if not minres.success and self.disp:
                print('warning: basinhoppping: local minimization failure')
        if hasattr(minres, 'nfev'):
            self.res.nfev += minres.nfev
        if hasattr(minres, 'njev'):
            self.res.njev += minres.njev
        if hasattr(minres, 'nhev'):
            self.res.nhev += minres.nhev
        accept = True
        for test in self.accept_tests:
            testres = test(f_new=energy_after_quench, x_new=x_after_quench, f_old=self.energy, x_old=self.x)
            if isinstance(testres, bool):
                if not testres:
                    accept = False
            elif isinstance(testres, str):
                if testres == 'force accept':
                    accept = True
                    break
                else:
                    raise ValueError("accept test must return bool or string 'force accept'. Type is", type(testres))
            else:
                raise ValueError("accept test must return bool or string 'force accept'. Type is", type(testres))

        if hasattr(self.step_taking, 'report'):
            self.step_taking.report(accept, f_new=energy_after_quench, x_new=x_after_quench, f_old=self.energy, x_old=self.x)
        return (x_after_quench, energy_after_quench, accept)

    def one_cycle(self):
        self.nstep += 1
        new_global_min = False
        xtrial, energy_trial, accept = self._monte_carlo_step()
        if accept:
            self.energy = energy_trial
            self.x = np.copy(xtrial)
            new_global_min = self.storage.update(self.x, self.energy)
        if self.disp:
            self.print_report(energy_trial, accept)
            if new_global_min:
                print('found new global minimum on step %d with function value %g' % (
                 self.nstep, self.energy))
        self.xtrial = xtrial
        self.energy_trial = energy_trial
        self.accept = accept
        return new_global_min

    def print_report(self, energy_trial, accept):
        xlowest, energy_lowest = self.storage.get_lowest()
        print('basinhopping step %d: f %g trial_f %g accepted %d  lowest_f %g' % (
         self.nstep, self.energy, energy_trial,
         accept, energy_lowest))


class AdaptiveStepsize(object):
    """
    Class to implement adaptive stepsize.

    This class wraps the step taking class and modifies the stepsize to
    ensure the true acceptance rate is as close as possible to the target.

    Parameters
    ----------
    takestep : callable
        The step taking routine.  Must contain modifiable attribute
        takestep.stepsize
    accept_rate : float, optional
        The target step acceptance rate
    interval : int, optional
        Interval for how often to update the stepsize
    factor : float, optional
        The step size is multiplied or divided by this factor upon each
        update.
    verbose : bool, optional
        Print information about each update

    """

    def __init__(self, takestep, accept_rate=0.5, interval=50, factor=0.9, verbose=True):
        self.takestep = takestep
        self.target_accept_rate = accept_rate
        self.interval = interval
        self.factor = factor
        self.verbose = verbose
        self.nstep = 0
        self.nstep_tot = 0
        self.naccept = 0

    def __call__(self, x):
        return self.take_step(x)

    def _adjust_step_size(self):
        old_stepsize = self.takestep.stepsize
        accept_rate = float(self.naccept) / self.nstep
        if accept_rate > self.target_accept_rate:
            self.takestep.stepsize /= self.factor
        else:
            self.takestep.stepsize *= self.factor
        if self.verbose:
            print('adaptive stepsize: acceptance rate %f target %f new stepsize %g old stepsize %g' % (
             accept_rate,
             self.target_accept_rate, self.takestep.stepsize,
             old_stepsize))

    def take_step(self, x):
        self.nstep += 1
        self.nstep_tot += 1
        if self.nstep % self.interval == 0:
            self._adjust_step_size()
        return self.takestep(x)

    def report(self, accept, **kwargs):
        """called by basinhopping to report the result of the step"""
        if accept:
            self.naccept += 1


class RandomDisplacement(object):
    """
    Add a random displacement of maximum size, stepsize, to the coordinates

    update x inplace
    """

    def __init__(self, stepsize=0.5):
        self.stepsize = stepsize

    def __call__(self, x):
        x += np.random.uniform(-self.stepsize, self.stepsize, np.shape(x))
        return x


class MinimizerWrapper(object):
    """
    wrap a minimizer function as a minimizer class
    """

    def __init__(self, minimizer, func=None, **kwargs):
        self.minimizer = minimizer
        self.func = func
        self.kwargs = kwargs

    def __call__(self, x0):
        if self.func is None:
            return self.minimizer(x0, **self.kwargs)
        else:
            return self.minimizer(self.func, x0, **self.kwargs)
            return


class Metropolis(object):
    """
    Metropolis acceptance criterion
    """

    def __init__(self, T):
        self.beta = 1.0 / T

    def accept_reject(self, energy_new, energy_old):
        w = min(1.0, np.exp(-(energy_new - energy_old) * self.beta))
        rand = np.random.rand()
        return w >= rand

    def __call__(self, **kwargs):
        """
        f_new and f_old are mandatory in kwargs
        """
        return bool(self.accept_reject(kwargs['f_new'], kwargs['f_old']))


def basinhopping(func, x0, niter=100, T=1.0, stepsize=0.5, minimizer_kwargs=None, take_step=None, accept_test=None, callback=None, interval=50, disp=False, niter_success=None):
    """
    Find the global minimum of a function using the basin-hopping algorithm

    .. versionadded:: 0.12.0

    Parameters
    ----------
    func : callable ``f(x, *args)``
        Function to be optimized.  ``args`` can be passed as an optional item
        in the dict ``minimizer_kwargs``
    x0 : ndarray
        Initial guess.
    niter : integer, optional
        The number of basin hopping iterations
    T : float, optional
        The "temperature" parameter for the accept or reject criterion.  Higher
        "temperatures" mean that larger jumps in function value will be
        accepted.  For best results ``T`` should be comparable to the
        separation
        (in function value) between local minima.
    stepsize : float, optional
        initial step size for use in the random displacement.
    minimizer_kwargs : dict, optional
        Extra keyword arguments to be passed to the minimizer
        ``scipy.optimize.minimize()`` Some important options could be:
            method : str
                The minimization method (e.g. ``"L-BFGS-B"``)
            args : tuple
                Extra arguments passed to the objective function (``func``) and
                its derivatives (Jacobian, Hessian).

    take_step : callable ``take_step(x)``, optional
        Replace the default step taking routine with this routine.  The default
        step taking routine is a random displacement of the coordinates, but
        other step taking algorithms may be better for some systems.
        ``take_step`` can optionally have the attribute ``take_step.stepsize``.
        If this attribute exists, then ``basinhopping`` will adjust
        ``take_step.stepsize`` in order to try to optimize the global minimum
        search.
    accept_test : callable, ``accept_test(f_new=f_new, x_new=x_new, f_old=fold, x_old=x_old)``, optional
        Define a test which will be used to judge whether or not to accept the
        step.  This will be used in addition to the Metropolis test based on
        "temperature" ``T``.  The acceptable return values are ``True``,
        ``False``, or ``"force accept"``.  If the latter, then this will
        override any other tests in order to accept the step.  This can be
        used, for example, to forcefully escape from a local minimum that
        ``basinhopping`` is trapped in.
    callback : callable, ``callback(x, f, accept)``, optional
        A callback function which will be called for all minimum found.  ``x``
        and ``f`` are the coordinates and function value of the trial minima,
        and ``accept`` is whether or not that minima was accepted.  This can be
        used, for example, to save the lowest N minima found.  Also,
        ``callback`` can be used to specify a user defined stop criterion by
        optionally returning ``True`` to stop the ``basinhopping`` routine.
    interval : integer, optional
        interval for how often to update the ``stepsize``
    disp : bool, optional
        Set to ``True`` to print status messages
    niter_success : integer, optional
        Stop the run if the global minimum candidate remains the same for this
        number of iterations.

    Returns
    -------
    res : Result
        The optimization result represented as a ``Result`` object.  Important
        attributes are: ``x`` the solution array, ``fun`` the value of the
        function at the solution, and ``message`` which describes the cause of
        the termination. See `Result` for a description of other attributes.

    See Also
    --------
    minimize :
        The local minimization function called once for each basinhopping step.
        ``minimizer_kwargs`` is passed to this routine.

    Notes
    -----
    Basin-hopping is a stochastic algorithm which attempts to find the global
    minimum of a smooth scalar function of one or more variables [1]_ [2]_ [3]_
    [4]_.  The algorithm in its current form was described by David Wales and
    Jonathan Doye [2]_ http://www-wales.ch.cam.ac.uk/.

    The algorithm is iterative with each cycle composed of the following
    features

    1) random perturbation of the coordinates

    2) local minimization

    3) accept or reject the new coordinates based on the minimized function
       value

    The acceptance test used here is the Metropolis criterion of standard Monte
    Carlo algorithms, although there are many other possibilities [3]_.

    This global minimization method has been shown to be extremely efficient
    for a wide variety of problems in physics and chemistry.  It is
    particularly useful when the function has many minima separated by large
    barriers. See the Cambridge Cluster Database
    http://www-wales.ch.cam.ac.uk/CCD.html for databases of molecular systems
    that have been optimized primarily using basin-hopping.  This database
    includes minimization problems exceeding 300 degrees of freedom.

    See the free software program GMIN (http://www-wales.ch.cam.ac.uk/GMIN) for
    a Fortran implementation of basin-hopping.  This implementation has many
    different variations of the procedure described above, including more
    advanced step taking algorithms and alternate acceptance criterion.

    For stochastic global optimization there is no way to determine if the true
    global minimum has actually been found. Instead, as a consistency check,
    the algorithm can be run from a number of different random starting points
    to ensure the lowest minimum found in each example has converged to the
    global minimum.  For this reason ``basinhopping`` will by default simply
    run for the number of iterations ``niter`` and return the lowest minimum
    found.  It is left to the user to ensure that this is in fact the global
    minimum.

    Choosing ``stepsize``:  This is a crucial parameter in ``basinhopping`` and
    depends on the problem being solved.  Ideally it should be comparable to
    the typical separation between local minima of the function being
    optimized.  ``basinhopping`` will, by default, adjust ``stepsize`` to find
    an optimal value, but this may take many iterations.  You will get quicker
    results if you set a sensible value for ``stepsize``.

    Choosing ``T``: The parameter ``T`` is the temperature used in the
    metropolis criterion.  Basinhopping steps are accepted with probability
    ``1`` if ``func(xnew) < func(xold)``, or otherwise with probability::

        exp( -(func(xnew) - func(xold)) / T )

    So, for best results, ``T`` should to be comparable to the typical
    difference in function value between between local minima

    References
    ----------
    .. [1] Wales, David J. 2003, Energy Landscapes, Cambridge University Press,
        Cambridge, UK.
    .. [2] Wales, D J, and Doye J P K, Global Optimization by Basin-Hopping and
        the Lowest Energy Structures of Lennard-Jones Clusters Containing up to
        110 Atoms.  Journal of Physical Chemistry A, 1997, 101, 5111.
    .. [3] Li, Z. and Scheraga, H. A., Monte Carlo-minimization approach to the
        multiple-minima problem in protein folding, Proc. Natl. Acad. Sci. USA,
        1987, 84, 6611.
    .. [4] Wales, D. J. and Scheraga, H. A., Global optimization of clusters,
        crystals, and biomolecules, Science, 1999, 285, 1368.

    Examples
    --------
    The following example is a one-dimensional minimization problem,  with many
    local minima superimposed on a parabola.

    >>> func = lambda x: cos(14.5 * x - 0.3) + (x + 0.2) * x
    >>> x0=[1.]

    Basinhopping, internally, uses a local minimization algorithm.  We will use
    the parameter ``minimizer_kwargs`` to tell basinhopping which algorithm to
    use and how to set up that minimizer.  This parameter will be passed to
    ``scipy.optimize.minimize()``.

    >>> minimizer_kwargs = {"method": "BFGS"}
    >>> ret = basinhopping(func, x0, minimizer_kwargs=minimizer_kwargs,
    ...                    niter=200)
    >>> print("global minimum: x = %.4f, f(x0) = %.4f" % (ret.x, ret.fun))
    global minimum: x = -0.1951, f(x0) = -1.0009

    Next consider a two-dimensional minimization problem. Also, this time we
    will use gradient information to significantly speed up the search.

    >>> def func2d(x):
    ...     f = cos(14.5 * x[0] - 0.3) + (x[1] + 0.2) * x[1] + (x[0] +
    ...                                                         0.2) * x[0]
    ...     df = np.zeros(2)
    ...     df[0] = -14.5 * sin(14.5 * x[0] - 0.3) + 2. * x[0] + 0.2
    ...     df[1] = 2. * x[1] + 0.2
    ...     return f, df

    We'll also use a different local minimization algorithm.  Also we must tell
    the minimizer that our function returns both energy and gradient (jacobian)

    >>> minimizer_kwargs = {"method":"L-BFGS-B", "jac":True}
    >>> x0 = [1.0, 1.0]
    >>> ret = basinhopping(func2d, x0, minimizer_kwargs=minimizer_kwargs,
    ...                    niter=200)
    >>> print("global minimum: x = [%.4f, %.4f], f(x0) = %.4f" % (ret.x[0],
    ...                                                           ret.x[1],
    ...                                                           ret.fun))
    global minimum: x = [-0.1951, -0.1000], f(x0) = -1.0109

    Here is an example using a custom step taking routine.  Imagine you want
    the first coordinate to take larger steps then the rest of the coordinates.
    This can be implemented like so:

    >>> class MyTakeStep(object):
    ...    def __init__(self, stepsize=0.5):
    ...        self.stepsize = stepsize
    ...    def __call__(self, x):
    ...        s = self.stepsize
    ...        x[0] += np.random.uniform(-2.*s, 2.*s)
    ...        x[1:] += np.random.uniform(-s, s, x[1:].shape)
    ...        return x

    Since ``MyTakeStep.stepsize`` exists basinhopping will adjust the magnitude
    of ``stepsize`` to optimize the search.  We'll use the same 2-D function as
    before

    >>> mytakestep = MyTakeStep()
    >>> ret = basinhopping(func2d, x0, minimizer_kwargs=minimizer_kwargs,
    ...                    niter=200, take_step=mytakestep)
    >>> print("global minimum: x = [%.4f, %.4f], f(x0) = %.4f" % (ret.x[0],
    ...                                                           ret.x[1],
    ...                                                           ret.fun))
    global minimum: x = [-0.1951, -0.1000], f(x0) = -1.0109

    Now let's do an example using a custom callback function which prints the
    value of every minimum found

    >>> def print_fun(x, f, accepted):
    ...         print("at minima %.4f accepted %d" % (f, int(accepted)))

    We'll run it for only 10 basinhopping steps this time.

    >>> np.random.seed(1)
    >>> ret = basinhopping(func2d, x0, minimizer_kwargs=minimizer_kwargs,
    ...                    niter=10, callback=print_fun)
    at minima 0.4159 accepted 1
    at minima -0.9073 accepted 1
    at minima -0.1021 accepted 1
    at minima -0.1021 accepted 1
    at minima 0.9102 accepted 1
    at minima 0.9102 accepted 1
    at minima 2.2945 accepted 0
    at minima -0.1021 accepted 1
    at minima -1.0109 accepted 1
    at minima -1.0109 accepted 1

    The minima at -1.0109 is actually the global minimum, found already on the
    8th iteration.

    Now let's implement bounds on the problem using a custom ``accept_test``:

    >>> class MyBounds(object):
    ...     def __init__(self, xmax=[1.1,1.1], xmin=[-1.1,-1.1] ):
    ...         self.xmax = np.array(xmax)
    ...         self.xmin = np.array(xmin)
    ...     def __call__(self, **kwargs):
    ...         x = kwargs["x_new"]
    ...         tmax = bool(np.all(x <= self.xmax))
    ...         tmin = bool(np.all(x >= self.xmin))
    ...         return tmax and tmin

    >>> mybounds = MyBounds()
    >>> ret = basinhopping(func2d, x0, minimizer_kwargs=minimizer_kwargs,
    ...                    niter=10, accept_test=mybounds)

    """
    x0 = np.array(x0)
    if minimizer_kwargs is None:
        minimizer_kwargs = dict()
    wrapped_minimizer = MinimizerWrapper(scipy.optimize.minimize, func, **minimizer_kwargs)
    if take_step is not None:
        if not isinstance(take_step, collections.Callable):
            raise TypeError('take_step must be callable')
        if hasattr(take_step, 'stepsize'):
            take_step_wrapped = AdaptiveStepsize(take_step, interval=interval, verbose=disp)
        else:
            take_step_wrapped = take_step
    else:
        displace = RandomDisplacement(stepsize=stepsize)
        take_step_wrapped = AdaptiveStepsize(displace, interval=interval, verbose=disp)
    if accept_test is not None:
        if not isinstance(accept_test, collections.Callable):
            raise TypeError('accept_test must be callable')
        accept_tests = [
         accept_test]
    else:
        accept_tests = []
    metropolis = Metropolis(T)
    accept_tests.append(metropolis)
    if niter_success is None:
        niter_success = niter + 2
    bh = BasinHoppingRunner(x0, wrapped_minimizer, take_step_wrapped, accept_tests, disp=disp)
    count = 0
    message = ['requested number of basinhopping iterations completed successfully']
    for i in range(niter):
        new_global_min = bh.one_cycle()
        if isinstance(callback, collections.Callable):
            val = callback(bh.xtrial, bh.energy_trial, bh.accept)
            if val is not None:
                if val:
                    message = [
                     'callback function requested stop early byreturning True']
                    break
        count += 1
        if new_global_min:
            count = 0
        elif count > niter_success:
            message = [
             'success condition satisfied']
            break

    lowest = bh.storage.get_lowest()
    res = bh.res
    res.x = np.copy(lowest[0])
    res.fun = lowest[1]
    res.message = message
    res.nit = i + 1
    return res


def _test_func2d_nograd(x):
    f = cos(14.5 * x[0] - 0.3) + (x[1] + 0.2) * x[1] + (x[0] + 0.2) * x[0] + 1.010876184442655
    return f


def _test_func2d(x):
    f = cos(14.5 * x[0] - 0.3) + (x[0] + 0.2) * x[0] + cos(14.5 * x[1] - 0.3) + (x[1] + 0.2) * x[1] + x[0] * x[1] + 1.963879482144252
    df = np.zeros(2)
    df[0] = -14.5 * sin(14.5 * x[0] - 0.3) + 2.0 * x[0] + 0.2 + x[1]
    df[1] = -14.5 * sin(14.5 * x[1] - 0.3) + 2.0 * x[1] + 0.2 + x[0]
    return (f, df)


if __name__ == '__main__':
    print('\n\nminimize a 2d function without gradient')
    kwargs = {'method': 'L-BFGS-B'}
    x0 = np.array([1.0, 1.0])
    scipy.optimize.minimize(_test_func2d_nograd, x0, **kwargs)
    ret = basinhopping(_test_func2d_nograd, x0, minimizer_kwargs=kwargs, niter=200, disp=False)
    print('minimum expected at  func([-0.195, -0.1]) = 0.0')
    print(ret)
    print('\n\ntry a harder 2d problem')
    kwargs = {'method': 'L-BFGS-B', 'jac': True}
    x0 = np.array([1.0, 1.0])
    ret = basinhopping(_test_func2d, x0, minimizer_kwargs=kwargs, niter=200, disp=False)
    print('minimum expected at ~, func([-0.19415263, -0.19415263]) = 0')
    print(ret)