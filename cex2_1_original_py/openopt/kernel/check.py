# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\kernel\check.pyc
# Compiled at: 2012-12-08 11:04:59
__docformat__ = 'restructuredtext en'
from numpy import isfinite, any, asarray

def check(p):
    """
    this func is called from runProbSolver(), you don't need to call the one
    """
    nErrors = 0
    if p.allowedGoals is not None and p.goal is not None and p.goal not in p.allowedGoals:
        p.err('goal ' + p.goal + ' is not available for the ' + p.probType + ' class (at least not implemented yet)')
    for fn in p._optionalData:
        attr = getattr(p, fn, None)
        if attr is None or isinstance(attr, (list, tuple)) and len(attr) == 0 or fn in p.solver.__optionalDataThatCanBeHandled__:
            continue
        if fn == 'Qc' or callable(attr) and getattr(p.userProvided, fn) or type(attr) in (set, dict, list, tuple) and len(attr) != 0 or not callable(attr) and asarray(attr).size > 0 and any(isfinite(attr)):
            p.err('the solver ' + p.solver.__name__ + ' cannot handle ' + "'" + fn + "' data")

    return nErrors