# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\linalg\flapack.pyc
# Compiled at: 2013-02-16 13:27:30
"""
This module is deprecated -- use scipy.linalg.lapack instead
"""
from __future__ import division, print_function, absolute_import
from ._flapack import *
import numpy as _np

@_np.deprecate(old_name='scipy.linalg.flapack', new_name='scipy.linalg.lapack')
def _deprecate():
    pass


_deprecate()