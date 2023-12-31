# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\UkrOpt\goldenSection_oo.pyc
# Compiled at: 2012-12-08 11:04:59
from openopt.kernel.baseSolver import baseSolver
from openopt.kernel.setDefaultIterFuncs import SMALL_DELTA_X, IS_MAX_ITER_REACHED, SMALL_DELTA_F
from numpy import nan, diff, copy

class goldenSection(baseSolver):
    __name__ = 'goldenSection'
    __optionalDataThatCanBeHandled__ = ['lb', 'ub']
    __license__ = 'BSD'
    __authors__ = 'Dmitrey'
    __alg__ = 'golden section'
    __info__ = '1-dimensional minimizer for finite box-bound problems'
    __isIterPointAlwaysFeasible__ = lambda self, p: True
    useOOiterfcn = True
    rightLocalization = 0
    leftLocalization = 0
    rightBorderForLocalization = None
    leftBorderForLocalization = None

    def __init__(self):
        pass

    def __solver__(self, p):
        if p.n != 1:
            p.err('the solver ' + self.__name__ + ' can handle singe-variable problems only')
        if not p.__isFiniteBoxBounded__():
            p.err('the solver ' + self.__name__ + ' requires finite lower and upper bounds')
        if SMALL_DELTA_X in p.kernelIterFuncs.keys():
            p.kernelIterFuncs.pop(SMALL_DELTA_X)
        a, b, f = copy(p.lb), copy(p.ub), p.f
        if self.rightBorderForLocalization is None:
            self.rightBorderForLocalization = p.ub
        if self.leftBorderForLocalization is None:
            self.leftBorderForLocalization = p.lb
        if self.leftLocalization * (b - self.leftBorderForLocalization) > b - a:
            p.istop, p.msg = (23, 'right localization has been reached (objFunc evaluation is skipped)')
        elif self.rightLocalization * (a - self.rightBorderForLocalization) > b - a:
            p.istop, p.msg = (24, 'left localization has been reached (objFunc evaluation is skipped)')
        if p.istop:
            p.xk, p.fk = 0.5 * (a + b), nan
            return
        else:
            s1 = 0.3819660112501051
            s2 = 0.6180339887498949
            x1 = a + s1 * (b - a)
            x2 = a + s2 * (b - a)
            y1, y2 = f(x1), f(x2)
            for i in range(p.maxIter):
                p.xk, p.fk = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                if y1 <= y2:
                    xmin, ymin = x1, y1
                    b, x2 = x2, x1
                    x1 = a + s1 * (b - a)
                    y2, y1 = y1, f(x1)
                else:
                    xmin, ymin = x2, y2
                    a, x1 = x1, x2
                    x2 = a + s2 * (b - a)
                    y1, y2 = y2, f(x2)
                if self.useOOiterfcn:
                    p.iterfcn()
                if i > 4 and max(p.iterValues.f[-4:]) < min(p.iterValues.f[-4:]) + p.ftol:
                    p.xf, p.ff = xmin, ymin
                    p.istop, p.msg = SMALL_DELTA_F, '|| F[k] - F[k-1] || < ftol'
                elif -p.xtol < b - a < p.xtol:
                    p.xf, p.ff = xmin, ymin
                    p.istop, p.msg = SMALL_DELTA_X, '|| X[k] - X[k-1] || < xtol'
                elif self.leftLocalization * (b - self.leftBorderForLocalization) > b - a:
                    p.istop, p.msg = (25, 'right localization has been reached')
                elif self.rightLocalization * (a - self.rightBorderForLocalization) > b - a:
                    p.istop, p.msg = (26, 'left localization has been reached')
                if y2 > y1:
                    p.special.leftXOptBorder = a
                    p.special.rightXOptBorder = x2
                else:
                    p.special.leftXOptBorder = x1
                    p.special.rightXOptBorder = b
                if p.istop:
                    return

            p.istop, p.msg = IS_MAX_ITER_REACHED, 'Max Iter has been reached'
            return