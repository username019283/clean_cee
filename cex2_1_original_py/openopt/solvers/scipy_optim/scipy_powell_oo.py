# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\scipy_optim\scipy_powell_oo.pyc
# Compiled at: 2012-12-08 11:04:59
from scipy.optimize import fmin_powell
from openopt.kernel.baseSolver import baseSolver
from openopt.kernel.ooMisc import isSolved

class scipy_powell(baseSolver):
    __name__ = 'scipy_powell'
    __license__ = 'BSD'
    __alg__ = ''
    __info__ = 'unconstrained NLP solver, cannot handle user-supplied gradient'
    iterfcnConnected = True

    def __init__(self):
        pass

    def __solver__(self, p):

        def iterfcn(x):
            p.xk, p.fk = x, p.f(x)
            p.iterfcn()
            iter = p.iter - 1
            if p.istop:
                raise isSolved

        try:
            iterfcn(p.x0)
            xf = fmin_powell(p.f, p.x0, xtol=p.xtol, ftol=p.ftol, disp=0, maxiter=p.maxIter, maxfun=p.maxFunEvals, callback=iterfcn)
        except isSolved:
            xf = p.xk

        ff = p.f(p.xk)
        p.xk = p.xf = xf
        p.fk = p.ff = ff
        p.istop = 1000
        p.iterfcn()