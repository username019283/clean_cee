# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\geomutils.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = 'Utility functions for geometrical operations.'

def normalizeTRBL(p):
    """
    Useful for interpreting short descriptions of paddings, borders, margin, etc.
    Expects a single value or a tuple of length 2 to 4.
    Returns a tuple representing (clockwise) the value(s) applied to the 4 sides of a rectangle:
    If a single value is given, that value is applied to all four sides.
    If two or three values are given, the missing values are taken from the opposite side(s).
    If four values are given they are returned unchanged.

    >>> normalizeTRBL(1)
    (1, 1, 1, 1)
    >>> normalizeTRBL((1, 1.2))
    (1, 1.2, 1, 1.2)
    >>> normalizeTRBL((1, 1.2, 0))
    (1, 1.2, 0, 1.2)
    >>> normalizeTRBL((1, 1.2, 0, 8))
    (1, 1.2, 0, 8)
    """
    if not isinstance(p, (tuple, list)):
        return (p,) * 4
    l = len(p)
    if l < 2 or l > 4:
        raise ValueError('A padding must have between 2 and 4 values but got %d.' % l)
    return tuple(p) + tuple([ p[i - 2] for i in range(l, 4) ])