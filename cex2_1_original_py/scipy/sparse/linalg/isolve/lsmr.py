# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\linalg\isolve\lsmr.pyc
# Compiled at: 2013-02-16 13:27:32
"""
Copyright (C) 2010 David Fong and Michael Saunders

LSMR uses an iterative method.

07 Jun 2010: Documentation updated
03 Jun 2010: First release version in Python

David Chin-lung Fong            clfong@stanford.edu
Institute for Computational and Mathematical Engineering
Stanford University

Michael Saunders                saunders@stanford.edu
Systems Optimization Laboratory
Dept of MS&E, Stanford University.

"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'lsmr']
from numpy import zeros, infty
from numpy.linalg import norm
from math import sqrt
from scipy.sparse.linalg.interface import aslinearoperator
from .lsqr import _sym_ortho

def lsmr(A, b, damp=0.0, atol=1e-06, btol=1e-06, conlim=100000000.0, maxiter=None, show=False):
    """Iterative solver for least-squares problems.

    lsmr solves the system of linear equations ``Ax = b``. If the system
    is inconsistent, it solves the least-squares problem ``min ||b - Ax||_2``.
    A is a rectangular matrix of dimension m-by-n, where all cases are
    allowed: m = n, m > n, or m < n. B is a vector of length m.
    The matrix A may be dense or sparse (usually sparse).

    .. versionadded:: 0.11.0

    Parameters
    ----------
    A : {matrix, sparse matrix, ndarray, LinearOperator}
        Matrix A in the linear system.
    b : (m,) ndarray
        Vector b in the linear system.
    damp : float
        Damping factor for regularized least-squares. `lsmr` solves
        the regularized least-squares problem::

         min ||(b) - (  A   )x||
             ||(0)   (damp*I) ||_2

        where damp is a scalar.  If damp is None or 0, the system
        is solved without regularization.
    atol, btol : float
        Stopping tolerances. `lsmr` continues iterations until a
        certain backward error estimate is smaller than some quantity
        depending on atol and btol.  Let ``r = b - Ax`` be the
        residual vector for the current approximate solution ``x``.
        If ``Ax = b`` seems to be consistent, ``lsmr`` terminates
        when ``norm(r) <= atol * norm(A) * norm(x) + btol * norm(b)``.
        Otherwise, lsmr terminates when ``norm(A^{T} r) <=
        atol * norm(A) * norm(r)``.  If both tolerances are 1.0e-6 (say),
        the final ``norm(r)`` should be accurate to about 6
        digits. (The final x will usually have fewer correct digits,
        depending on ``cond(A)`` and the size of LAMBDA.)  If `atol`
        or `btol` is None, a default value of 1.0e-6 will be used.
        Ideally, they should be estimates of the relative error in the
        entries of A and B respectively.  For example, if the entries
        of `A` have 7 correct digits, set atol = 1e-7. This prevents
        the algorithm from doing unnecessary work beyond the
        uncertainty of the input data.
    conlim : float
        `lsmr` terminates if an estimate of ``cond(A)`` exceeds
        `conlim`.  For compatible systems ``Ax = b``, conlim could be
        as large as 1.0e+12 (say).  For least-squares problems,
        `conlim` should be less than 1.0e+8. If `conlim` is None, the
        default value is 1e+8.  Maximum precision can be obtained by
        setting ``atol = btol = conlim = 0``, but the number of
        iterations may then be excessive.
    maxiter : int
        `lsmr` terminates if the number of iterations reaches
        `maxiter`.  The default is ``maxiter = min(m, n)``.  For
        ill-conditioned systems, a larger value of `maxiter` may be
        needed.
    show : bool
        Print iterations logs if ``show=True``.

    Returns
    -------
    x : ndarray of float
        Least-square solution returned.
    istop : int
        istop gives the reason for stopping::

          istop   = 0 means x=0 is a solution.
                  = 1 means x is an approximate solution to A*x = B,
                      according to atol and btol.
                  = 2 means x approximately solves the least-squares problem
                      according to atol.
                  = 3 means COND(A) seems to be greater than CONLIM.
                  = 4 is the same as 1 with atol = btol = eps (machine
                      precision)
                  = 5 is the same as 2 with atol = eps.
                  = 6 is the same as 3 with CONLIM = 1/eps.
                  = 7 means ITN reached maxiter before the other stopping
                      conditions were satisfied.

    itn : int
        Number of iterations used.
    normr : float
        ``norm(b-Ax)``
    normar : float
        ``norm(A^T (b - Ax))``
    norma : float
        ``norm(A)``
    conda : float
        Condition number of A.
    normx : float
        ``norm(x)``

    References
    ----------
    .. [1] D. C.-L. Fong and M. A. Saunders,
           "LSMR: An iterative algorithm for sparse least-squares problems",
           SIAM J. Sci. Comput., vol. 33, pp. 2950-2971, 2011.
           http://arxiv.org/abs/1006.0758
    .. [2] LSMR Software, http://www.stanford.edu/~clfong/lsmr.html

    """
    A = aslinearoperator(A)
    b = b.squeeze()
    msg = ('The exact solution is  x = 0                              ', 'Ax - b is small enough, given atol, btol                  ',
           'The least-squares solution is good enough, given atol     ', 'The estimate of cond(Abar) has exceeded conlim            ',
           'Ax - b is small enough for this machine                   ', 'The least-squares solution is good enough for this machine',
           'Cond(Abar) seems to be too large for this machine         ', 'The iteration limit has been reached                      ')
    hdg1 = '   itn      x(1)       norm r    norm Ar'
    hdg2 = ' compatible   LS      norm A   cond A'
    pfreq = 20
    pcount = 0
    m, n = A.shape
    minDim = min([m, n])
    if maxiter is None:
        maxiter = minDim
    if show:
        print(' ')
        print('LSMR            Least-squares solution of  Ax = b\n')
        print('The matrix A has %8g rows  and %8g cols' % (m, n))
        print('damp = %20.14e\n' % damp)
        print('atol = %8.2e                 conlim = %8.2e\n' % (atol, conlim))
        print('btol = %8.2e             maxiter = %8g\n' % (btol, maxiter))
    u = b
    beta = norm(u)
    v = zeros(n)
    alpha = 0
    if beta > 0:
        u = 1 / beta * u
        v = A.rmatvec(u)
        alpha = norm(v)
    if alpha > 0:
        v = 1 / alpha * v
    itn = 0
    zetabar = alpha * beta
    alphabar = alpha
    rho = 1
    rhobar = 1
    cbar = 1
    sbar = 0
    h = v.copy()
    hbar = zeros(n)
    x = zeros(n)
    betadd = beta
    betad = 0
    rhodold = 1
    tautildeold = 0
    thetatilde = 0
    zeta = 0
    d = 0
    normA2 = alpha * alpha
    maxrbar = 0
    minrbar = 1e+100
    normA = sqrt(normA2)
    condA = 1
    normx = 0
    normb = beta
    istop = 0
    ctol = 0
    if conlim > 0:
        ctol = 1 / conlim
    normr = beta
    normar = alpha * beta
    if normar == 0:
        if show:
            print(msg[0])
        return (x, istop, itn, normr, normar, normA, condA, normx)
    else:
        if show:
            print(' ')
            print(hdg1, hdg2)
            test1 = 1
            test2 = alpha / beta
            str1 = '%6g %12.5e' % (itn, x[0])
            str2 = ' %10.3e %10.3e' % (normr, normar)
            str3 = '  %8.1e %8.1e' % (test1, test2)
            print(('').join([str1, str2, str3]))
        while itn < maxiter:
            itn = itn + 1
            u = A.matvec(v) - alpha * u
            beta = norm(u)
            if beta > 0:
                u = 1 / beta * u
                v = A.rmatvec(u) - beta * v
                alpha = norm(v)
                if alpha > 0:
                    v = 1 / alpha * v
            chat, shat, alphahat = _sym_ortho(alphabar, damp)
            rhoold = rho
            c, s, rho = _sym_ortho(alphahat, beta)
            thetanew = s * alpha
            alphabar = c * alpha
            rhobarold = rhobar
            zetaold = zeta
            thetabar = sbar * rho
            rhotemp = cbar * rho
            cbar, sbar, rhobar = _sym_ortho(cbar * rho, thetanew)
            zeta = cbar * zetabar
            zetabar = -sbar * zetabar
            hbar = h - thetabar * rho / (rhoold * rhobarold) * hbar
            x = x + zeta / (rho * rhobar) * hbar
            h = v - thetanew / rho * h
            betaacute = chat * betadd
            betacheck = -shat * betadd
            betahat = c * betaacute
            betadd = -s * betaacute
            thetatildeold = thetatilde
            ctildeold, stildeold, rhotildeold = _sym_ortho(rhodold, thetabar)
            thetatilde = stildeold * rhobar
            rhodold = ctildeold * rhobar
            betad = -stildeold * betad + ctildeold * betahat
            tautildeold = (zetaold - thetatildeold * tautildeold) / rhotildeold
            taud = (zeta - thetatilde * tautildeold) / rhodold
            d = d + betacheck * betacheck
            normr = sqrt(d + (betad - taud) ** 2 + betadd * betadd)
            normA2 = normA2 + beta * beta
            normA = sqrt(normA2)
            normA2 = normA2 + alpha * alpha
            maxrbar = max(maxrbar, rhobarold)
            if itn > 1:
                minrbar = min(minrbar, rhobarold)
            condA = max(maxrbar, rhotemp) / min(minrbar, rhotemp)
            normar = abs(zetabar)
            normx = norm(x)
            test1 = normr / normb
            if normA * normr != 0:
                test2 = normar / (normA * normr)
            else:
                test2 = infty
            test3 = 1 / condA
            t1 = test1 / (1 + normA * normx / normb)
            rtol = btol + atol * normA * normx / normb
            if itn >= maxiter:
                istop = 7
            if 1 + test3 <= 1:
                istop = 6
            if 1 + test2 <= 1:
                istop = 5
            if 1 + t1 <= 1:
                istop = 4
            if test3 <= ctol:
                istop = 3
            if test2 <= atol:
                istop = 2
            if test1 <= rtol:
                istop = 1
            if show:
                if n <= 40 or itn <= 10 or itn >= maxiter - 10 or itn % 10 == 0 or test3 <= 1.1 * ctol or test2 <= 1.1 * atol or test1 <= 1.1 * rtol or istop != 0:
                    if pcount >= pfreq:
                        pcount = 0
                        print(' ')
                        print(hdg1, hdg2)
                    pcount = pcount + 1
                    str1 = '%6g %12.5e' % (itn, x[0])
                    str2 = ' %10.3e %10.3e' % (normr, normar)
                    str3 = '  %8.1e %8.1e' % (test1, test2)
                    str4 = ' %8.1e %8.1e' % (normA, condA)
                    print(('').join([str1, str2, str3, str4]))
            if istop > 0:
                break

        if show:
            print(' ')
            print('LSMR finished')
            print(msg[istop])
            print('istop =%8g    normr =%8.1e' % (istop, normr))
            print('    normA =%8.1e    normAr =%8.1e' % (normA, normar))
            print('itn   =%8g    condA =%8.1e' % (itn, condA))
            print('    normx =%8.1e' % normx)
            print(str1, str2)
            print(str3, str4)
        return (x, istop, itn, normr, normar, normA, condA, normx)