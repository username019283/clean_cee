# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\kernel\NLLSP.pyc
# Compiled at: 2012-12-08 11:04:59
from baseProblem import NonLinProblem
from numpy import sum, dot, asfarray
import NLP

class NLLSP(NonLinProblem):
    _optionalData = [
     'lb', 'ub', 'A', 'Aeq', 'b', 'beq', 'c', 'h']
    showGoal = False
    goal = 'minimum'
    probType = 'NLLSP'
    allowedGoals = ['minimum', 'min']
    isObjFunValueASingleNumber = False
    expectedArgs = ['f', 'x0']

    def __init__(self, *args, **kwargs):
        NonLinProblem.__init__(self, *args, **kwargs)

    def objFuncMultiple2Single(self, fv):
        return (fv ** 2).sum()

    def nllsp2nlp(self, solver, **solver_params):
        ff = lambda x: sum(asfarray(self.f(x)) ** 2)
        p = NLP.NLP(ff, self.x0)
        self.inspire(p, sameConstraints=True)
        if self.userProvided.df:
            p.df = lambda x: dot(2 * asfarray(self.f(x)), asfarray(self.df(x, useSparse=False)))
        p.f = ff

        def nllsp_iterfcn(*args, **kwargs):
            p.primalIterFcn(*args, **kwargs)
            p.xk = self.xk
            p.fk = p.f(p.xk)
            p.rk = self.rk
            if self.istop != 0:
                p.istop = self.istop
            elif p.istop != 0:
                self.istop = p.istop

        p.primalIterFcn, p.iterfcn = self.iterfcn, nllsp_iterfcn
        self.iprint = -1
        p.show = False
        r = p.solve(solver, **solver_params)
        return r