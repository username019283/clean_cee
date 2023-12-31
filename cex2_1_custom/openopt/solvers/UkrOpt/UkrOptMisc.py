# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\UkrOpt\UkrOptMisc.pyc
# Compiled at: 2012-12-08 11:04:59
from numpy import concatenate, vstack, hstack, inf, ones, zeros, diag, dot, abs, where, max, min
from openopt import NLP, LLSP
from openopt.kernel.ooMisc import norm
from openopt.kernel.setDefaultIterFuncs import IS_MAX_ITER_REACHED
funcDirectionValue = lambda alpha, func, x, direction: func(x + alpha * direction)

def funcDirectionValueWithMaxConstraintLimit(alpha, func, x, direction, maxConstrLimit, p):
    xx = x + alpha * direction
    mc = p.getMaxResidual(xx)
    if mc > maxConstrLimit:
        return 1e+150 * mc
    else:
        return func(xx)


def getConstrDirection(p, x, regularization=1e-07):
    c, dc, h, dh, df = (p.c(x), p.dc(x), p.h(x), p.dh(x), p.df(x))
    A, Aeq = vstack((dc, p.A)), vstack((dh, p.Aeq))
    b = concatenate((-c, p.b - p.matmult(p.A, x)))
    beq = concatenate((-h, p.beq - p.matmult(p.Aeq, x)))
    lb = p.lb - x
    ub = p.ub - x
    nC = b.size
    if A.size == 0:
        A_LLS = hstack((zeros((nC, p.n)), diag(ones(nC))))
    else:
        A_LLS = hstack((A, diag(ones(nC))))
    if Aeq.size == 0:
        Awhole_LLS = vstack((A_LLS, hstack((diag(regularization * ones(p.n)), zeros((p.n, nC))))))
    else:
        Aeq_LLS = hstack((Aeq, zeros((beq.size, nC))))
        Awhole_LLS = vstack((Aeq_LLS, A_LLS, hstack((diag(regularization * ones(p.n)), zeros((p.n, nC))))))
    if p.getMaxResidual(x) > p.contol:
        dump_x = -p.getMaxConstrGradient(x)
    else:
        dump_x = -df
    bwhole_LLS = concatenate((beq, b, dump_x))
    lb_LLS = hstack((lb, zeros(nC)))
    ub_LLS = hstack((ub, inf * ones(nC)))
    p_sp = LLSP(Awhole_LLS, bwhole_LLS, lb=lb_LLS, ub=ub_LLS, iprint=-1)
    r_sp = p_sp.solve('BVLS', BVLS_inf=1e+30)
    return r_sp.xf[:p.n]


class DirectionOptimPoint:

    def __init__(self):
        pass


def getDirectionOptimPoint(p, func, x, direction, forwardMultiplier=2.0, maxiter=150, xtol=None, maxConstrLimit=None, alpha_lb=0, alpha_ub=inf, rightLocalization=0, leftLocalization=0, rightBorderForLocalization=0, leftBorderForLocalization=None):
    if all(direction == 0):
        p.err('nonzero direction is required')
    if maxConstrLimit is None:
        lsFunc = funcDirectionValue
        args = (func, x, direction)
    else:
        lsFunc = funcDirectionValueWithMaxConstraintLimit
        args = (func, x, direction, maxConstrLimit, p)
    prev_alpha, new_alpha = alpha_lb, min(alpha_lb + 0.5, alpha_ub)
    prev_val = lsFunc(prev_alpha, *args)
    for i in range(p.maxLineSearch):
        if lsFunc(new_alpha, *args) > prev_val or new_alpha == alpha_ub:
            break
        else:
            if i != 0:
                prev_alpha = min(alpha_lb, new_alpha)
            new_alpha *= forwardMultiplier

    if i == p.maxLineSearch - 1:
        p.debugmsg('getDirectionOptimPoint: maxLineSearch is exeeded')
    lb, ub = prev_alpha, new_alpha
    if xtol is None:
        xtol = p.xtol / 2.0
    p_LS = NLP(lsFunc, x0=0, lb=lb, ub=ub, iprint=-1, args=args, xtol=xtol, maxIter=maxiter, contol=p.contol)
    r = p_LS.solve('goldenSection', useOOiterfcn=False, rightLocalization=rightLocalization, leftLocalization=leftLocalization, rightBorderForLocalization=rightBorderForLocalization, leftBorderForLocalization=leftBorderForLocalization)
    if r.istop == IS_MAX_ITER_REACHED:
        p.warn('getDirectionOptimPoint: max iter has been exceeded')
    alpha_opt = r.special.rightXOptBorder
    R = DirectionOptimPoint()
    R.leftAlphaOptBorder = r.special.leftXOptBorder
    R.leftXOptBorder = x + R.leftAlphaOptBorder * direction
    R.rightAlphaOptBorder = r.special.rightXOptBorder
    R.rightXOptBorder = x + R.rightAlphaOptBorder * direction
    R.x = x + alpha_opt * direction
    R.alpha = alpha_opt
    R.evalsF = r.evals['f'] + i
    return R


from numpy import arccos

def getAltitudeDirection(p, pointTop, point2, point3):
    b = point2 - pointTop
    c = point3 - pointTop
    alpha = dot(c, c - b) / norm(c - b) ** 2
    h = alpha * b + (1 - alpha) * c
    abh = arccos(dot(h, b) / norm(h) / norm(b))
    ach = arccos(dot(h, c) / norm(h) / norm(c))
    abc = arccos(dot(b, c) / norm(b) / norm(c))
    isInsideTriangle = abh + ach - abc <= 1e-08
    return (h, isInsideTriangle)


from openopt.kernel.setDefaultIterFuncs import IS_LINE_SEARCH_FAILED
from openopt.kernel.ooMisc import isSolved

def getBestPointAfterTurn(oldPoint, newPoint, altLinInEq=None, maxLS=3, maxDeltaX=None, maxDeltaF=None, sf=None, hs=None, new_bs=True, checkTurnByGradient=False):
    assert altLinInEq is not None
    p = oldPoint.p
    contol = p.contol
    altPoint = oldPoint.linePoint(0.5, newPoint)
    if maxLS is None:
        maxLS = p.maxLineSearch
    assert maxLS != 0
    if maxDeltaX is None:
        if p.iter != 0:
            maxDeltaX = 15000.0 * p.xtol
        else:
            maxDeltaX = 15.0 * p.xtol
    if maxDeltaF is None:
        maxDeltaF = 150 * p.ftol
    prev_prev_point = newPoint
    if checkTurnByGradient:
        direction = newPoint.x - oldPoint.x
        condNotBetter = lambda altPoint, prevPoint: dot(prevPoint._getDirection(p.solver.approach), direction) <= 0.0
        dType = 1
    else:
        condNotBetter = lambda altPoint, prevPoint: not altPoint.betterThan(prevPoint, altLinInEq=altLinInEq)
        dType = 2
    for ls in range(maxLS):
        altPoint, prevPoint = oldPoint.linePoint(0.5, altPoint), altPoint
        if sf is not None and sf(altPoint):
            p.debugmsg('Return by sf: ls = %d' % ls)
            return (
             altPoint, prevPoint, -1 - ls)
        if condNotBetter(altPoint, prevPoint):
            if new_bs:
                bestPoint, pointForDilation = prevPoint, prev_prev_point
                return (
                 bestPoint, pointForDilation, -1 - ls)
            else:
                return (
                 prev_prev_point, -1 - ls)

        prev_prev_point = prevPoint
        if p.norm(oldPoint.x - altPoint.x) < maxDeltaX:
            break
        rr = oldPoint.f() - altPoint.f()
        if (oldPoint.isFeas(True) or altPoint.isFeas(True)) and maxDeltaF / 32768 < abs(rr) < maxDeltaF:
            break
        if oldPoint.mr_alt() > contol and altPoint.mr_alt() > p.contol and altPoint.mr_alt() > 0.9 * oldPoint.mr():
            break

    if new_bs:
        bestPoint, pointForDilation = altPoint, prevPoint
        return (
         bestPoint, pointForDilation, -1 - ls)
    else:
        return (
         prev_prev_point, -1 - ls)
        return