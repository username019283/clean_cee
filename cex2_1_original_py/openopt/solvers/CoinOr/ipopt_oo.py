# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\CoinOr\ipopt_oo.pyc
# Compiled at: 2012-12-08 11:04:59
from numpy import *
import re
from openopt.kernel.baseSolver import baseSolver
from openopt.kernel.nonOptMisc import Vstack, Find, isspmatrix
try:
    import pyipopt
    pyipoptInstalled = True
except:
    pyipoptInstalled = False

class ipopt(baseSolver):
    __name__ = 'ipopt'
    __license__ = 'CPL'
    __authors__ = 'Carl Laird (Carnegie Mellon University) and Andreas Wachter'
    __alg__ = 'A. Wachter and L. T. Biegler, On the Implementation of a Primal-Dual Interior Point Filter Line Search Algorithm for Large-Scale Nonlinear Programming, Mathematical Programming 106(1), pp. 25-57, 2006 '
    __homepage__ = 'http://www.coin-or.org/'
    __info__ = 'requires pyipopt made by Eric Xu You'
    __optionalDataThatCanBeHandled__ = ['A', 'Aeq', 'b', 'beq', 'lb', 'ub', 'c', 'h']
    _canHandleScipySparse = True
    optFile = 'auto'
    options = ''

    def __init__(self):
        pass

    def __solver__(self, p):
        if not pyipoptInstalled:
            p.err('you should have pyipopt installed')
        nvar = p.n
        x_L = p.lb
        x_U = p.ub
        ncon = p.nc + p.nh + p.b.size + p.beq.size
        g_L, g_U = zeros(ncon), zeros(ncon)
        g_L[:(p.nc)] = -inf
        g_L[(p.nc + p.nh):(p.nc + p.nh + p.b.size)] = -inf
        if p.isFDmodel:
            r = []
            if p.nc != 0:
                r.append(p._getPattern(p.user.c))
            if p.nh != 0:
                r.append(p._getPattern(p.user.h))
            if p.nb != 0:
                r.append(p.A)
            if p.nbeq != 0:
                r.append(p.Aeq)
            if len(r) > 0:
                if all([ isinstance(elem, ndarray) for elem in r ]):
                    r = vstack(r)
                else:
                    r = Vstack(r)
                    if isspmatrix(r):
                        from scipy import __version__
                        if __version__.startswith('0.7.3') or __version__.startswith('0.7.2') or __version__.startswith('0.7.1') or __version__.startswith('0.7.0'):
                            p.pWarn('updating scipy to version >= 0.7.4 is very recommended for the problem with the solver IPOPT')
            else:
                r = array([])
            if isspmatrix(r):
                I, J, _ = Find(r)
                I, J = array(I, int64), array(J, int64)
            elif isinstance(r, ndarray):
                if r.size == 0:
                    I, J = array([], dtype=int64), array([], dtype=int64)
                else:
                    I, J = where(r)
            else:
                p.disp('unimplemented type:%s' % str(type(r)))
            nnzj = len(I)
        else:
            I, J = where(ones((ncon, p.n)))
            nnzj = ncon * p.n

        def eval_g(x):
            r = array(())
            if p.userProvided.c:
                r = p.c(x)
            if p.userProvided.h:
                r = hstack((r, p.h(x)))
            r = hstack((r, p._get_AX_Less_B_residuals(x), p._get_AeqX_eq_Beq_residuals(x)))
            return r

        def eval_jac_g(x, flag, userdata=(
 I, J)):
            I, J = userdata
            if flag and p.isFDmodel:
                return (I, J)
            else:
                r = []
                if p.userProvided.c:
                    r.append(p.dc(x))
                if p.userProvided.h:
                    r.append(p.dh(x))
                if p.nb != 0:
                    r.append(p.A)
                if p.nbeq != 0:
                    r.append(p.Aeq)
                if any([ isspmatrix(elem) for elem in r ]):
                    r = Vstack([ atleast_2d(elem) if elem.ndim < 2 else elem for elem in r ])
                elif len(r) != 0:
                    r = vstack(r)
                if p.isFDmodel:
                    if isspmatrix(r):
                        R = r.tocsr()
                        R = R[(I, J)]
                    else:
                        R = r[(I, J)]
                    if isspmatrix(R):
                        return R.A
                    if isinstance(R, ndarray):
                        return R
                    p.err('bug in OpenOpt-ipopt connection, inform OpenOpt developers, type(R) = %s' % type(R))
                if flag:
                    return (
                     I, J)
                if isspmatrix(r):
                    r = r.A
                return r.flatten()

        nnzh = 0

        def eval_h(lagrange, obj_factor, flag):
            return

        nlp = pyipopt.create(nvar, x_L, x_U, ncon, g_L, g_U, nnzj, nnzh, p.f, p.df, eval_g, eval_jac_g)
        if self.optFile == 'auto':
            lines = [
             '# generated automatically by OpenOpt\n', 'print_level 0\n']
            lines.append('tol ' + str(p.ftol) + '\n')
            lines.append('constr_viol_tol ' + str(p.contol) + '\n')
            lines.append('max_iter ' + str(min(15000, p.maxIter)) + '\n')
            if self.options != '':
                for s in re.split(',|;', self.options):
                    lines.append(s.strip().replace('=', ' ', 1) + '\n')

            if p.nc == 0:
                lines.append('jac_d_constant yes\n')
            if p.nh == 0:
                lines.append('jac_c_constant yes\n')
            if p.castFrom.lower() in ('lp', 'qp', 'llsp'):
                lines.append('hessian_constant yes\n')
            ipopt_opt_file = open('ipopt.opt', 'w')
            ipopt_opt_file.writelines(lines)
            ipopt_opt_file.close()
        try:
            x, zl, zu, obj = nlp.solve(p.x0)[:4]
            if p.point(p.xk).betterThan(p.point(x)):
                obj = p.fk
                p.xk = p.xk.copy()
            else:
                p.xk, p.fk = x.copy(), obj
            if p.istop == 0:
                p.istop = 1000
        finally:
            nlp.close()