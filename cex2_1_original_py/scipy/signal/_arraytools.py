# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\signal\_arraytools.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Functions for acting on a axis of an array.
"""
from __future__ import division, print_function, absolute_import
import numpy as np

def axis_slice(a, start=None, stop=None, step=None, axis=-1):
    """Take a slice along axis 'axis' from 'a'.

    Parameters
    ----------
    a : numpy.ndarray
        The array to be sliced.
    start, stop, step : int or None
        The slice parameters.
    axis : int
        The axis of `a` to be sliced.

    Examples
    --------
    >>> a = array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> axis_slice(a, start=0, stop=1, axis=1)
    array([[1],
           [4],
           [7]])
    >>> axis_slice(a, start=1, axis=0)
    array([[4, 5, 6],
           [7, 8, 9]])

    Notes
    -----
    The keyword arguments start, stop and step are used by calling
    slice(start, stop, step).  This implies axis_slice() does not
    handle its arguments the exacty the same as indexing.  To select
    a single index k, for example, use
        axis_slice(a, start=k, stop=k+1)
    In this case, the length of the axis 'axis' in the result will
    be 1; the trivial dimension is not removed. (Use numpy.squeeze()
    to remove trivial axes.)
    """
    a_slice = [
     slice(None)] * a.ndim
    a_slice[axis] = slice(start, stop, step)
    b = a[a_slice]
    return b


def axis_reverse(a, axis=-1):
    """Reverse the 1-d slices of `a` along axis `axis`.

    Returns axis_slice(a, step=-1, axis=axis).
    """
    return axis_slice(a, step=-1, axis=axis)


def odd_ext(x, n, axis=-1):
    """Generate a new ndarray by making an odd extension of x along an axis.

    Parameters
    ----------
    x : ndarray
        The array to be extended.
    n : int
        The number of elements by which to extend x at each end of the axis.
    axis : int
        The axis along which to extend x.  Default is -1.

    Examples
    --------
    >>> a = array([[1.0,2.0,3.0,4.0,5.0], [0.0, 1.0, 4.0, 9.0, 16.0]])
    >>> _odd_ext(a, 2)
    array([[-1.,  0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.],
           [-4., -1,   0.,  1.,  4.,  9., 16., 23., 28.]])
    """
    if n < 1:
        return x
    if n > x.shape[axis] - 1:
        raise ValueError(('The extension length n (%d) is too big. ' + 'It must not exceed x.shape[axis]-1, which is %d.') % (
         n, x.shape[axis] - 1))
    left_end = axis_slice(x, start=0, stop=1, axis=axis)
    left_ext = axis_slice(x, start=n, stop=0, step=-1, axis=axis)
    right_end = axis_slice(x, start=-1, axis=axis)
    right_ext = axis_slice(x, start=-2, stop=-(n + 2), step=-1, axis=axis)
    ext = np.concatenate((2 * left_end - left_ext,
     x,
     2 * right_end - right_ext), axis=axis)
    return ext


def even_ext(x, n, axis=-1):
    """Create an ndarray that is an even extension of x along an axis.

    Parameters
    ----------
    x : ndarray
        The array to be extended.
    n : int
        The number of elements by which to extend x at each end of the axis.
    axis : int
        The axis along which to extend x.  Default is -1.

    Examples
    --------
    >>> a = array([[1.0,2.0,3.0,4.0,5.0], [0.0, 1.0, 4.0, 9.0, 16.0]])
    >>> _even_ext(a, 2)
    array([[  3.,   2.,   1.,   2.,   3.,   4.,   5.,   4.,   3.],
           [  4.,   1.,   0.,   1.,   4.,   9.,  16.,   9.,   4.]])
    """
    if n < 1:
        return x
    if n > x.shape[axis] - 1:
        raise ValueError(('The extension length n (%d) is too big. ' + 'It must not exceed x.shape[axis]-1, which is %d.') % (
         n, x.shape[axis] - 1))
    left_ext = axis_slice(x, start=n, stop=0, step=-1, axis=axis)
    right_ext = axis_slice(x, start=-2, stop=-(n + 2), step=-1, axis=axis)
    ext = np.concatenate((left_ext,
     x,
     right_ext), axis=axis)
    return ext


def const_ext(x, n, axis=-1):
    """Create an ndarray that is a constant extension of x along an axis.

    The extension repeats the values at the first and last element of
    the axis.

    Parameters
    ----------
    x : ndarray
        The array to be extended.
    n : int
        The number of elements by which to extend x at each end of the axis.
    axis : int
        The axis along which to extend x.  Default is -1.

    Examples
    --------
    >>> a = array([[1.0,2.0,3.0,4.0,5.0], [0.0, 1.0, 4.0, 9.0, 16.0]])
    >>> _const_ext(a, 2)
    array([[  1.,   1.,   1.,   2.,   3.,   4.,   5.,   5.,   5.],
           [  0.,   0.,   0.,   1.,   4.,   9.,  16.,  16.,  16.]])
    """
    if n < 1:
        return x
    left_end = axis_slice(x, start=0, stop=1, axis=axis)
    ones_shape = [1] * x.ndim
    ones_shape[axis] = n
    ones = np.ones(ones_shape, dtype=x.dtype)
    left_ext = ones * left_end
    right_end = axis_slice(x, start=-1, axis=axis)
    right_ext = ones * right_end
    ext = np.concatenate((left_ext,
     x,
     right_ext), axis=axis)
    return ext