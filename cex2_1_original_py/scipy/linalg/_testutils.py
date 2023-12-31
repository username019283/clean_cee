# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\linalg\_testutils.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
import numpy as np

class _FakeMatrix(object):

    def __init__(self, data):
        self._data = data
        self.__array_interface__ = data.__array_interface__


class _FakeMatrix2(object):

    def __init__(self, data):
        self._data = data

    def __array__(self):
        return self._data


def _get_array(shape, dtype):
    """
    Get a test array of given shape and data type.
    Returned NxN matrices are posdef, and 2xN are banded-posdef.

    """
    if len(shape) == 2 and shape[0] == 2:
        x = np.zeros(shape, dtype=dtype)
        x[0, 1:] = -1
        x[1] = 2
        return x
    else:
        if len(shape) == 2 and shape[0] == shape[1]:
            x = np.zeros(shape, dtype=dtype)
            j = np.arange(shape[0])
            x[(j, j)] = 2
            x[(j[:-1], j[:-1] + 1)] = -1
            x[(j[:-1] + 1, j[:-1])] = -1
            return x
        np.random.seed(1234)
        return np.random.randn(*shape).astype(dtype)


def _id(x):
    return x


def assert_no_overwrite(call, shapes, dtypes=None):
    """
    Test that a call does not overwrite its input arguments
    """
    if dtypes is None:
        dtypes = [
         np.float32, np.float64, np.complex64, np.complex128]
    for dtype in dtypes:
        for order in ['C', 'F']:
            for faker in [_id, _FakeMatrix, _FakeMatrix2]:
                orig_inputs = [ _get_array(s, dtype) for s in shapes ]
                inputs = [ faker(x.copy(order)) for x in orig_inputs ]
                call(*inputs)
                msg = 'call modified inputs [%r, %r]' % (dtype, faker)
                for a, b in zip(inputs, orig_inputs):
                    np.testing.assert_equal(a, b, err_msg=msg)

    return