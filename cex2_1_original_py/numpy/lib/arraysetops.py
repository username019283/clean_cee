# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\lib\arraysetops.pyc
# Compiled at: 2013-04-07 07:04:04
"""
Set operations for 1D numeric arrays based on sorting.

:Contains:
  ediff1d,
  unique,
  intersect1d,
  setxor1d,
  in1d,
  union1d,
  setdiff1d

:Notes:

For floating point arrays, inaccurate results may appear due to usual round-off
and floating point comparison issues.

Speed could be gained in some operations by an implementation of
sort(), that can provide directly the permutation vectors, avoiding
thus calls to argsort().

To do: Optionally return indices analogously to unique for all functions.

:Author: Robert Cimrman
"""
__all__ = [
 'ediff1d', 'intersect1d', 'setxor1d', 'union1d', 'setdiff1d', 
 'unique', 
 'in1d']
import numpy as np
from numpy.lib.utils import deprecate

def ediff1d(ary, to_end=None, to_begin=None):
    """
    The differences between consecutive elements of an array.

    Parameters
    ----------
    ary : array_like
        If necessary, will be flattened before the differences are taken.
    to_end : array_like, optional
        Number(s) to append at the end of the returned differences.
    to_begin : array_like, optional
        Number(s) to prepend at the beginning of the returned differences.

    Returns
    -------
    ediff1d : ndarray
        The differences. Loosely, this is ``ary.flat[1:] - ary.flat[:-1]``.

    See Also
    --------
    diff, gradient

    Notes
    -----
    When applied to masked arrays, this function drops the mask information
    if the `to_begin` and/or `to_end` parameters are used.

    Examples
    --------
    >>> x = np.array([1, 2, 4, 7, 0])
    >>> np.ediff1d(x)
    array([ 1,  2,  3, -7])

    >>> np.ediff1d(x, to_begin=-99, to_end=np.array([88, 99]))
    array([-99,   1,   2,   3,  -7,  88,  99])

    The returned array is always 1D.

    >>> y = [[1, 2, 4], [1, 6, 24]]
    >>> np.ediff1d(y)
    array([ 1,  2, -3,  5, 18])

    """
    ary = np.asanyarray(ary).flat
    ed = ary[1:] - ary[:-1]
    arrays = [ed]
    if to_begin is not None:
        arrays.insert(0, to_begin)
    if to_end is not None:
        arrays.append(to_end)
    if len(arrays) != 1:
        ed = np.hstack(arrays)
    return ed


def unique(ar, return_index=False, return_inverse=False):
    """
    Find the unique elements of an array.

    Returns the sorted unique elements of an array. There are two optional
    outputs in addition to the unique elements: the indices of the input array
    that give the unique values, and the indices of the unique array that
    reconstruct the input array.

    Parameters
    ----------
    ar : array_like
        Input array. This will be flattened if it is not already 1-D.
    return_index : bool, optional
        If True, also return the indices of `ar` that result in the unique
        array.
    return_inverse : bool, optional
        If True, also return the indices of the unique array that can be used
        to reconstruct `ar`.

    Returns
    -------
    unique : ndarray
        The sorted unique values.
    unique_indices : ndarray, optional
        The indices of the first occurrences of the unique values in the
        (flattened) original array. Only provided if `return_index` is True.
    unique_inverse : ndarray, optional
        The indices to reconstruct the (flattened) original array from the
        unique array. Only provided if `return_inverse` is True.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> np.unique([1, 1, 2, 2, 3, 3])
    array([1, 2, 3])
    >>> a = np.array([[1, 1], [2, 3]])
    >>> np.unique(a)
    array([1, 2, 3])

    Return the indices of the original array that give the unique values:

    >>> a = np.array(['a', 'b', 'b', 'c', 'a'])
    >>> u, indices = np.unique(a, return_index=True)
    >>> u
    array(['a', 'b', 'c'],
           dtype='|S1')
    >>> indices
    array([0, 1, 3])
    >>> a[indices]
    array(['a', 'b', 'c'],
           dtype='|S1')

    Reconstruct the input array from the unique values:

    >>> a = np.array([1, 2, 6, 4, 2, 3, 2])
    >>> u, indices = np.unique(a, return_inverse=True)
    >>> u
    array([1, 2, 3, 4, 6])
    >>> indices
    array([0, 1, 4, 3, 1, 2, 1])
    >>> u[indices]
    array([1, 2, 6, 4, 2, 3, 2])

    """
    try:
        ar = ar.flatten()
    except AttributeError:
        if not return_inverse and not return_index:
            items = sorted(set(ar))
            return np.asarray(items)
        ar = np.asanyarray(ar).flatten()

    if ar.size == 0:
        if return_inverse and return_index:
            return (ar, np.empty(0, np.bool), np.empty(0, np.bool))
        else:
            if return_inverse or return_index:
                return (ar, np.empty(0, np.bool))
            return ar

    if return_inverse or return_index:
        if return_index:
            perm = ar.argsort(kind='mergesort')
        else:
            perm = ar.argsort()
        aux = ar[perm]
        flag = np.concatenate(([True], aux[1:] != aux[:-1]))
        if return_inverse:
            iflag = np.cumsum(flag) - 1
            iperm = perm.argsort()
            if return_index:
                return (aux[flag], perm[flag], iflag[iperm])
            return (aux[flag], iflag[iperm])
        else:
            return (
             aux[flag], perm[flag])
    else:
        ar.sort()
        flag = np.concatenate(([True], ar[1:] != ar[:-1]))
        return ar[flag]


def intersect1d(ar1, ar2, assume_unique=False):
    """
    Find the intersection of two arrays.

    Return the sorted, unique values that are in both of the input arrays.

    Parameters
    ----------
    ar1, ar2 : array_like
        Input arrays.
    assume_unique : bool
        If True, the input arrays are both assumed to be unique, which
        can speed up the calculation.  Default is False.

    Returns
    -------
    intersect1d : ndarray
        Sorted 1D array of common and unique elements.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> np.intersect1d([1, 3, 4, 3], [3, 1, 2, 1])
    array([1, 3])

    """
    if not assume_unique:
        ar1 = unique(ar1)
        ar2 = unique(ar2)
    aux = np.concatenate((ar1, ar2))
    aux.sort()
    return aux[:-1][aux[1:] == aux[:-1]]


def setxor1d(ar1, ar2, assume_unique=False):
    """
    Find the set exclusive-or of two arrays.

    Return the sorted, unique values that are in only one (not both) of the
    input arrays.

    Parameters
    ----------
    ar1, ar2 : array_like
        Input arrays.
    assume_unique : bool
        If True, the input arrays are both assumed to be unique, which
        can speed up the calculation.  Default is False.

    Returns
    -------
    setxor1d : ndarray
        Sorted 1D array of unique values that are in only one of the input
        arrays.

    Examples
    --------
    >>> a = np.array([1, 2, 3, 2, 4])
    >>> b = np.array([2, 3, 5, 7, 5])
    >>> np.setxor1d(a,b)
    array([1, 4, 5, 7])

    """
    if not assume_unique:
        ar1 = unique(ar1)
        ar2 = unique(ar2)
    aux = np.concatenate((ar1, ar2))
    if aux.size == 0:
        return aux
    aux.sort()
    flag = np.concatenate(([True], aux[1:] != aux[:-1], [True]))
    flag2 = flag[1:] == flag[:-1]
    return aux[flag2]


def in1d(ar1, ar2, assume_unique=False):
    """
    Test whether each element of a 1-D array is also present in a second array.

    Returns a boolean array the same length as `ar1` that is True
    where an element of `ar1` is in `ar2` and False otherwise.

    Parameters
    ----------
    ar1 : (M,) array_like
        Input array.
    ar2 : array_like
        The values against which to test each value of `ar1`.
    assume_unique : bool, optional
        If True, the input arrays are both assumed to be unique, which
        can speed up the calculation.  Default is False.

    Returns
    -------
    in1d : (M,) ndarray, bool
        The values `ar1[in1d]` are in `ar2`.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Notes
    -----
    `in1d` can be considered as an element-wise function version of the
    python keyword `in`, for 1-D sequences. ``in1d(a, b)`` is roughly
    equivalent to ``np.array([item in b for item in a])``.

    .. versionadded:: 1.4.0

    Examples
    --------
    >>> test = np.array([0, 1, 2, 5, 0])
    >>> states = [0, 2]
    >>> mask = np.in1d(test, states)
    >>> mask
    array([ True, False,  True, False,  True], dtype=bool)
    >>> test[mask]
    array([0, 2, 0])

    """
    ar1 = np.asarray(ar1).ravel()
    ar2 = np.asarray(ar2).ravel()
    if len(ar2) < 10 * len(ar1) ** 0.145:
        mask = np.zeros(len(ar1), dtype=np.bool)
        for a in ar2:
            mask |= ar1 == a

        return mask
    if not assume_unique:
        ar1, rev_idx = np.unique(ar1, return_inverse=True)
        ar2 = np.unique(ar2)
    ar = np.concatenate((ar1, ar2))
    order = ar.argsort(kind='mergesort')
    sar = ar[order]
    equal_adj = sar[1:] == sar[:-1]
    flag = np.concatenate((equal_adj, [False]))
    indx = order.argsort(kind='mergesort')[:len(ar1)]
    if assume_unique:
        return flag[indx]
    else:
        return flag[indx][rev_idx]


def union1d(ar1, ar2):
    """
    Find the union of two arrays.

    Return the unique, sorted array of values that are in either of the two
    input arrays.

    Parameters
    ----------
    ar1, ar2 : array_like
        Input arrays. They are flattened if they are not already 1D.

    Returns
    -------
    union1d : ndarray
        Unique, sorted union of the input arrays.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> np.union1d([-1, 0, 1], [-2, 0, 2])
    array([-2, -1,  0,  1,  2])

    """
    return unique(np.concatenate((ar1, ar2)))


def setdiff1d(ar1, ar2, assume_unique=False):
    """
    Find the set difference of two arrays.

    Return the sorted, unique values in `ar1` that are not in `ar2`.

    Parameters
    ----------
    ar1 : array_like
        Input array.
    ar2 : array_like
        Input comparison array.
    assume_unique : bool
        If True, the input arrays are both assumed to be unique, which
        can speed up the calculation.  Default is False.

    Returns
    -------
    setdiff1d : ndarray
        Sorted 1D array of values in `ar1` that are not in `ar2`.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> a = np.array([1, 2, 3, 2, 4, 1])
    >>> b = np.array([3, 4, 5, 6])
    >>> np.setdiff1d(a, b)
    array([1, 2])

    """
    if not assume_unique:
        ar1 = unique(ar1)
        ar2 = unique(ar2)
    aux = in1d(ar1, ar2, assume_unique=True)
    if aux.size == 0:
        return aux
    else:
        return np.asarray(ar1)[aux == 0]