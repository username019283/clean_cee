# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\tests\nlp1.pyc
# Compiled at: 2012-12-08 11:04:59
from numpy import cos, arange, ones, asarray, zeros, mat, array
from openopt import NLP

def test(complexity=0, **kwargs):
    n = 15 * (complexity + 1)
    x0 = 15 * cos(arange(n)) + 8
    f = lambda x: ((x - 15) ** 2).sum()
    df = lambda x: 2 * (x - 15)
    c = lambda x: [
     2 * x[0] ** 4 - 32, x[1] ** 2 + x[2] ** 2 - 8]

    def dc(x):
        r = zeros((len(c(x0)), n))
        r[(0, 0)] = 8 * x[0] ** 3
        r[(1, 1)] = 2 * x[1]
        r[(1, 2)] = 2 * x[2]
        return r

    hp = 2
    h1 = lambda x: (x[-1] - 13) ** hp
    h2 = lambda x: (x[-2] - 17) ** hp
    h = lambda x: [h1(x), h2(x)]

    def dh(x):
        r = zeros((2, n))
        r[(0, -1)] = hp * (x[-1] - 13) ** (hp - 1)
        r[(1, -2)] = hp * (x[-2] - 17) ** (hp - 1)
        return r

    lb = -8 * ones(n)
    ub = 15 * ones(n) + 8 * cos(arange(n))
    ind = 3
    A = zeros((2, n))
    A[0, ind:ind + 2] = 1
    A[1, ind + 2:ind + 4] = 1
    b = [15, 8]
    Aeq = zeros(n)
    Aeq[(ind + 4):(ind + 8)] = 1
    beq = 45
    colors = [
     'b', 'k', 'y', 'g', 'r']
    solvers = [
     'ralg', 'scipy_slsqp', 'ipopt']
    solvers = ['ralg', 'scipy_slsqp']
    solvers = ['ralg']
    solvers = ['r2']
    solvers = ['ralg', 'scipy_slsqp']
    for i, solver in enumerate(solvers):
        p = NLP(f, x0, df=df, c=c, h=h, dc=dc, dh=dh, lb=lb, ub=ub, A=A, b=b, Aeq=Aeq, beq=beq, maxIter=10000.0, show=(solver == solvers[-1]), color=colors[i], **kwargs)
        if not kwargs.has_key('iprint'):
            p.iprint = -1
        r = p.solve(solver)

    if r.istop > 0:
        return (True, r, p)
    else:
        return (
         False, r, p)


if __name__ == '__main__':
    isPassed, r, p = test(iprint=10, plot=0)
    assert isPassed