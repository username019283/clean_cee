# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\Standalone\arpack_oo.pyc
# Compiled at: 2012-12-08 11:04:59
from openopt.kernel.baseSolver import baseSolver
from openopt.kernel.nonOptMisc import Vstack
from scipy.sparse.linalg import eigs

class arpack(baseSolver):
    __name__ = 'arpack'
    __license__ = 'BSD'
    __authors__ = ''
    __alg__ = ''
    __info__ = '    '
    __optionalDataThatCanBeHandled__ = [
     'M']
    _canHandleScipySparse = True

    def __solver__(self, p):
        A = p.C
        M = p.M
        if p._goal == 'all':
            p.err('You should change prob "goal" argument, solver arpack can search at most n-2 eigenvectors')
        if p.N > A.shape[0] - 2:
            p.err('solver arpack can find at most n-2 eigenvalues, where n is height of matrix')
        eigenvalues, eigenvectors = eigs(A, k=p.N, M=M, sigma=None, which='LM', v0=None, ncv=None, maxiter=None, tol=p.xtol, return_eigenvectors=True)
        p.xf = p.xk = Vstack((eigenvalues, eigenvectors))
        p.eigenvalues = eigenvalues
        p.eigenvectors = eigenvectors
        p.ff = 0
        return