# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\lib\index_tricks.pyc
# Compiled at: 2013-04-07 07:04:04
__all__ = [
 'ravel_multi_index', 
 'unravel_index', 
 'mgrid', 
 'ogrid', 
 'r_', 
 'c_', 's_', 
 'index_exp', 'ix_', 
 'ndenumerate', 'ndindex', 
 'fill_diagonal', 
 'diag_indices', 'diag_indices_from']
import sys, numpy.core.numeric as _nx
from numpy.core.numeric import asarray, ScalarType, array, alltrue, cumprod, arange
from numpy.core.numerictypes import find_common_type
import math, function_base, numpy.matrixlib as matrix
from function_base import diff
from numpy.lib._compiled_base import ravel_multi_index, unravel_index
makemat = matrix.matrix

def ix_(*args):
    """
    Construct an open mesh from multiple sequences.

    This function takes N 1-D sequences and returns N outputs with N
    dimensions each, such that the shape is 1 in all but one dimension
    and the dimension with the non-unit shape value cycles through all
    N dimensions.

    Using `ix_` one can quickly construct index arrays that will index
    the cross product. ``a[np.ix_([1,3],[2,5])]`` returns the array
    ``[[a[1,2] a[1,5]], [a[3,2] a[3,5]]]``.

    Parameters
    ----------
    args : 1-D sequences

    Returns
    -------
    out : tuple of ndarrays
        N arrays with N dimensions each, with N the number of input
        sequences. Together these arrays form an open mesh.

    See Also
    --------
    ogrid, mgrid, meshgrid

    Examples
    --------
    >>> a = np.arange(10).reshape(2, 5)
    >>> a
    array([[0, 1, 2, 3, 4],
           [5, 6, 7, 8, 9]])
    >>> ixgrid = np.ix_([0,1], [2,4])
    >>> ixgrid
    (array([[0],
           [1]]), array([[2, 4]]))
    >>> ixgrid[0].shape, ixgrid[1].shape
    ((2, 1), (1, 2))
    >>> a[ixgrid]
    array([[2, 4],
           [7, 9]])

    """
    out = []
    nd = len(args)
    baseshape = [1] * nd
    for k in range(nd):
        new = _nx.asarray(args[k])
        if new.ndim != 1:
            raise ValueError('Cross index must be 1 dimensional')
        if issubclass(new.dtype.type, _nx.bool_):
            new = new.nonzero()[0]
        baseshape[k] = len(new)
        new = new.reshape(tuple(baseshape))
        out.append(new)
        baseshape[k] = 1

    return tuple(out)


class nd_grid(object):
    """
    Construct a multi-dimensional "meshgrid".

    ``grid = nd_grid()`` creates an instance which will return a mesh-grid
    when indexed.  The dimension and number of the output arrays are equal
    to the number of indexing dimensions.  If the step length is not a
    complex number, then the stop is not inclusive.

    However, if the step length is a **complex number** (e.g. 5j), then the
    integer part of its magnitude is interpreted as specifying the
    number of points to create between the start and stop values, where
    the stop value **is inclusive**.

    If instantiated with an argument of ``sparse=True``, the mesh-grid is
    open (or not fleshed out) so that only one-dimension of each returned
    argument is greater than 1.

    Parameters
    ----------
    sparse : bool, optional
        Whether the grid is sparse or not. Default is False.

    Notes
    -----
    Two instances of `nd_grid` are made available in the NumPy namespace,
    `mgrid` and `ogrid`::

        mgrid = nd_grid(sparse=False)
        ogrid = nd_grid(sparse=True)

    Users should use these pre-defined instances instead of using `nd_grid`
    directly.

    Examples
    --------
    >>> mgrid = np.lib.index_tricks.nd_grid()
    >>> mgrid[0:5,0:5]
    array([[[0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4]],
           [[0, 1, 2, 3, 4],
            [0, 1, 2, 3, 4],
            [0, 1, 2, 3, 4],
            [0, 1, 2, 3, 4],
            [0, 1, 2, 3, 4]]])
    >>> mgrid[-1:1:5j]
    array([-1. , -0.5,  0. ,  0.5,  1. ])

    >>> ogrid = np.lib.index_tricks.nd_grid(sparse=True)
    >>> ogrid[0:5,0:5]
    [array([[0],
            [1],
            [2],
            [3],
            [4]]), array([[0, 1, 2, 3, 4]])]

    """

    def __init__(self, sparse=False):
        self.sparse = sparse

    def __getitem__(self, key):
        try:
            size = []
            typ = int
            for k in range(len(key)):
                step = key[k].step
                start = key[k].start
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                if isinstance(step, complex):
                    size.append(int(abs(step)))
                    typ = float
                else:
                    size.append(math.ceil((key[k].stop - start) / (step * 1.0)))
                if isinstance(step, float) or isinstance(start, float) or isinstance(key[k].stop, float):
                    typ = float

            if self.sparse:
                nn = map((lambda x, t: _nx.arange(x, dtype=t)), size, (
                 typ,) * len(size))
            else:
                nn = _nx.indices(size, typ)
            for k in range(len(size)):
                step = key[k].step
                start = key[k].start
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                if isinstance(step, complex):
                    step = int(abs(step))
                    if step != 1:
                        step = (key[k].stop - start) / float(step - 1)
                nn[k] = nn[k] * step + start

            if self.sparse:
                slobj = [
                 _nx.newaxis] * len(size)
                for k in range(len(size)):
                    slobj[k] = slice(None, None)
                    nn[k] = nn[k][slobj]
                    slobj[k] = _nx.newaxis

            return nn
        except (IndexError, TypeError):
            step = key.step
            stop = key.stop
            start = key.start
            if start is None:
                start = 0
            if isinstance(step, complex):
                step = abs(step)
                length = int(step)
                if step != 1:
                    step = (key.stop - start) / float(step - 1)
                stop = key.stop + step
                return _nx.arange(0, length, 1, float) * step + start
            return _nx.arange(start, stop, step)

        return

    def __getslice__(self, i, j):
        return _nx.arange(i, j)

    def __len__(self):
        return 0


mgrid = nd_grid(sparse=False)
ogrid = nd_grid(sparse=True)
mgrid.__doc__ = None
ogrid.__doc__ = None

class AxisConcatenator(object):
    """
    Translates slice objects to concatenation along an axis.

    For detailed documentation on usage, see `r_`.

    """

    def _retval(self, res):
        if self.matrix:
            oldndim = res.ndim
            res = makemat(res)
            if oldndim == 1 and self.col:
                res = res.T
        self.axis = self._axis
        self.matrix = self._matrix
        self.col = 0
        return res

    def __init__(self, axis=0, matrix=False, ndmin=1, trans1d=-1):
        self._axis = axis
        self._matrix = matrix
        self.axis = axis
        self.matrix = matrix
        self.col = 0
        self.trans1d = trans1d
        self.ndmin = ndmin

    def __getitem__(self, key):
        trans1d = self.trans1d
        ndmin = self.ndmin
        if isinstance(key, str):
            frame = sys._getframe().f_back
            mymat = matrix.bmat(key, frame.f_globals, frame.f_locals)
            return mymat
        else:
            if type(key) is not tuple:
                key = (
                 key,)
            objs = []
            scalars = []
            arraytypes = []
            scalartypes = []
            for k in range(len(key)):
                scalar = False
                if type(key[k]) is slice:
                    step = key[k].step
                    start = key[k].start
                    stop = key[k].stop
                    if start is None:
                        start = 0
                    if step is None:
                        step = 1
                    if isinstance(step, complex):
                        size = int(abs(step))
                        newobj = function_base.linspace(start, stop, num=size)
                    else:
                        newobj = _nx.arange(start, stop, step)
                    if ndmin > 1:
                        newobj = array(newobj, copy=False, ndmin=ndmin)
                        if trans1d != -1:
                            newobj = newobj.swapaxes(-1, trans1d)
                elif isinstance(key[k], str):
                    if k != 0:
                        raise ValueError('special directives must be the first entry.')
                    key0 = key[0]
                    if key0 in 'rc':
                        self.matrix = True
                        self.col = key0 == 'c'
                        continue
                    if ',' in key0:
                        vec = key0.split(',')
                        try:
                            self.axis, ndmin = [ int(x) for x in vec[:2] ]
                            if len(vec) == 3:
                                trans1d = int(vec[2])
                            continue
                        except:
                            raise ValueError('unknown special directive')

                    try:
                        self.axis = int(key[k])
                        continue
                    except (ValueError, TypeError):
                        raise ValueError('unknown special directive')

                elif type(key[k]) in ScalarType:
                    newobj = array(key[k], ndmin=ndmin)
                    scalars.append(k)
                    scalar = True
                    scalartypes.append(newobj.dtype)
                else:
                    newobj = key[k]
                    if ndmin > 1:
                        tempobj = array(newobj, copy=False, subok=True)
                        newobj = array(newobj, copy=False, subok=True, ndmin=ndmin)
                        if trans1d != -1 and tempobj.ndim < ndmin:
                            k2 = ndmin - tempobj.ndim
                            if trans1d < 0:
                                trans1d += k2 + 1
                            defaxes = range(ndmin)
                            k1 = trans1d
                            axes = defaxes[:k1] + defaxes[k2:] + defaxes[k1:k2]
                            newobj = newobj.transpose(axes)
                        del tempobj
                objs.append(newobj)
                if not scalar and isinstance(newobj, _nx.ndarray):
                    arraytypes.append(newobj.dtype)

            final_dtype = find_common_type(arraytypes, scalartypes)
            if final_dtype is not None:
                for k in scalars:
                    objs[k] = objs[k].astype(final_dtype)

            res = _nx.concatenate(tuple(objs), axis=self.axis)
            return self._retval(res)

    def __getslice__(self, i, j):
        res = _nx.arange(i, j)
        return self._retval(res)

    def __len__(self):
        return 0


class RClass(AxisConcatenator):
    """
    Translates slice objects to concatenation along the first axis.

    This is a simple way to build up arrays quickly. There are two use cases.

    1. If the index expression contains comma separated arrays, then stack
       them along their first axis.
    2. If the index expression contains slice notation or scalars then create
       a 1-D array with a range indicated by the slice notation.

    If slice notation is used, the syntax ``start:stop:step`` is equivalent
    to ``np.arange(start, stop, step)`` inside of the brackets. However, if
    ``step`` is an imaginary number (i.e. 100j) then its integer portion is
    interpreted as a number-of-points desired and the start and stop are
    inclusive. In other words ``start:stop:stepj`` is interpreted as
    ``np.linspace(start, stop, step, endpoint=1)`` inside of the brackets.
    After expansion of slice notation, all comma separated sequences are
    concatenated together.

    Optional character strings placed as the first element of the index
    expression can be used to change the output. The strings 'r' or 'c' result
    in matrix output. If the result is 1-D and 'r' is specified a 1 x N (row)
    matrix is produced. If the result is 1-D and 'c' is specified, then a N x 1
    (column) matrix is produced. If the result is 2-D then both provide the
    same matrix result.

    A string integer specifies which axis to stack multiple comma separated
    arrays along. A string of two comma-separated integers allows indication
    of the minimum number of dimensions to force each entry into as the
    second integer (the axis to concatenate along is still the first integer).

    A string with three comma-separated integers allows specification of the
    axis to concatenate along, the minimum number of dimensions to force the
    entries to, and which axis should contain the start of the arrays which
    are less than the specified number of dimensions. In other words the third
    integer allows you to specify where the 1's should be placed in the shape
    of the arrays that have their shapes upgraded. By default, they are placed
    in the front of the shape tuple. The third argument allows you to specify
    where the start of the array should be instead. Thus, a third argument of
    '0' would place the 1's at the end of the array shape. Negative integers
    specify where in the new shape tuple the last dimension of upgraded arrays
    should be placed, so the default is '-1'.

    Parameters
    ----------
    Not a function, so takes no parameters

    Returns
    -------
    A concatenated ndarray or matrix.

    See Also
    --------
    concatenate : Join a sequence of arrays together.
    c_ : Translates slice objects to concatenation along the second axis.

    Examples
    --------
    >>> np.r_[np.array([1,2,3]), 0, 0, np.array([4,5,6])]
    array([1, 2, 3, 0, 0, 4, 5, 6])
    >>> np.r_[-1:1:6j, [0]*3, 5, 6]
    array([-1. , -0.6, -0.2,  0.2,  0.6,  1. ,  0. ,  0. ,  0. ,  5. ,  6. ])

    String integers specify the axis to concatenate along or the minimum
    number of dimensions to force entries into.

    >>> a = np.array([[0, 1, 2], [3, 4, 5]])
    >>> np.r_['-1', a, a] # concatenate along last axis
    array([[0, 1, 2, 0, 1, 2],
           [3, 4, 5, 3, 4, 5]])
    >>> np.r_['0,2', [1,2,3], [4,5,6]] # concatenate along first axis, dim>=2
    array([[1, 2, 3],
           [4, 5, 6]])

    >>> np.r_['0,2,0', [1,2,3], [4,5,6]]
    array([[1],
           [2],
           [3],
           [4],
           [5],
           [6]])
    >>> np.r_['1,2,0', [1,2,3], [4,5,6]]
    array([[1, 4],
           [2, 5],
           [3, 6]])

    Using 'r' or 'c' as a first string argument creates a matrix.

    >>> np.r_['r',[1,2,3], [4,5,6]]
    matrix([[1, 2, 3, 4, 5, 6]])

    """

    def __init__(self):
        AxisConcatenator.__init__(self, 0)


r_ = RClass()

class CClass(AxisConcatenator):
    """
    Translates slice objects to concatenation along the second axis.

    This is short-hand for ``np.r_['-1,2,0', index expression]``, which is
    useful because of its common occurrence. In particular, arrays will be
    stacked along their last axis after being upgraded to at least 2-D with
    1's post-pended to the shape (column vectors made out of 1-D arrays).

    For detailed documentation, see `r_`.

    Examples
    --------
    >>> np.c_[np.array([[1,2,3]]), 0, 0, np.array([[4,5,6]])]
    array([[1, 2, 3, 0, 0, 4, 5, 6]])

    """

    def __init__(self):
        AxisConcatenator.__init__(self, -1, ndmin=2, trans1d=0)


c_ = CClass()

class ndenumerate(object):
    """
    Multidimensional index iterator.

    Return an iterator yielding pairs of array coordinates and values.

    Parameters
    ----------
    a : ndarray
      Input array.

    See Also
    --------
    ndindex, flatiter

    Examples
    --------
    >>> a = np.array([[1, 2], [3, 4]])
    >>> for index, x in np.ndenumerate(a):
    ...     print index, x
    (0, 0) 1
    (0, 1) 2
    (1, 0) 3
    (1, 1) 4

    """

    def __init__(self, arr):
        self.iter = asarray(arr).flat

    def next(self):
        """
        Standard iterator method, returns the index tuple and array value.

        Returns
        -------
        coords : tuple of ints
            The indices of the current iteration.
        val : scalar
            The array element of the current iteration.

        """
        return (
         self.iter.coords, self.iter.next())

    def __iter__(self):
        return self


class ndindex(object):
    """
    An N-dimensional iterator object to index arrays.

    Given the shape of an array, an `ndindex` instance iterates over
    the N-dimensional index of the array. At each iteration a tuple
    of indices is returned, the last dimension is iterated over first.

    Parameters
    ----------
    `*args` : ints
      The size of each dimension of the array.

    See Also
    --------
    ndenumerate, flatiter

    Examples
    --------
    >>> for index in np.ndindex(3, 2, 1):
    ...     print index
    (0, 0, 0)
    (0, 1, 0)
    (1, 0, 0)
    (1, 1, 0)
    (2, 0, 0)
    (2, 1, 0)

    """

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        self.nd = len(args)
        self.ind = [0] * self.nd
        self.index = 0
        self.maxvals = args
        tot = 1
        for k in range(self.nd):
            tot *= args[k]

        self.total = tot

    def _incrementone(self, axis):
        if axis < 0:
            return
        if self.ind[axis] < self.maxvals[axis] - 1:
            self.ind[axis] += 1
        else:
            self.ind[axis] = 0
            self._incrementone(axis - 1)

    def ndincr(self):
        """
        Increment the multi-dimensional index by one.

        `ndincr` takes care of the "wrapping around" of the axes.
        It is called by `ndindex.next` and not normally used directly.

        """
        self._incrementone(self.nd - 1)

    def next(self):
        """
        Standard iterator method, updates the index and returns the index tuple.

        Returns
        -------
        val : tuple of ints
            Returns a tuple containing the indices of the current iteration.

        """
        if self.index >= self.total:
            raise StopIteration
        val = tuple(self.ind)
        self.index += 1
        self.ndincr()
        return val

    def __iter__(self):
        return self


class IndexExpression(object):
    """
    A nicer way to build up index tuples for arrays.

    .. note::
       Use one of the two predefined instances `index_exp` or `s_`
       rather than directly using `IndexExpression`.

    For any index combination, including slicing and axis insertion,
    ``a[indices]`` is the same as ``a[np.index_exp[indices]]`` for any
    array `a`. However, ``np.index_exp[indices]`` can be used anywhere
    in Python code and returns a tuple of slice objects that can be
    used in the construction of complex index expressions.

    Parameters
    ----------
    maketuple : bool
        If True, always returns a tuple.

    See Also
    --------
    index_exp : Predefined instance that always returns a tuple:
       `index_exp = IndexExpression(maketuple=True)`.
    s_ : Predefined instance without tuple conversion:
       `s_ = IndexExpression(maketuple=False)`.

    Notes
    -----
    You can do all this with `slice()` plus a few special objects,
    but there's a lot to remember and this version is simpler because
    it uses the standard array indexing syntax.

    Examples
    --------
    >>> np.s_[2::2]
    slice(2, None, 2)
    >>> np.index_exp[2::2]
    (slice(2, None, 2),)

    >>> np.array([0, 1, 2, 3, 4])[np.s_[2::2]]
    array([2, 4])

    """

    def __init__(self, maketuple):
        self.maketuple = maketuple

    def __getitem__(self, item):
        if self.maketuple and type(item) != tuple:
            return (item,)
        else:
            return item


index_exp = IndexExpression(maketuple=True)
s_ = IndexExpression(maketuple=False)

def fill_diagonal(a, val, wrap=False):
    """Fill the main diagonal of the given array of any dimensionality.

    For an array `a` with ``a.ndim > 2``, the diagonal is the list of
    locations with indices ``a[i, i, ..., i]`` all identical. This function
    modifies the input array in-place, it does not return a value.

    Parameters
    ----------
    a : array, at least 2-D.
      Array whose diagonal is to be filled, it gets modified in-place.

    val : scalar
      Value to be written on the diagonal, its type must be compatible with
      that of the array a.

    wrap: bool For tall matrices in NumPy version up to 1.6.2, the
      diagonal "wrapped" after N columns. You can have this behavior
      with this option. This affect only tall matrices.

    See also
    --------
    diag_indices, diag_indices_from

    Notes
    -----
    .. versionadded:: 1.4.0

    This functionality can be obtained via `diag_indices`, but internally
    this version uses a much faster implementation that never constructs the
    indices and uses simple slicing.

    Examples
    --------
    >>> a = np.zeros((3, 3), int)
    >>> np.fill_diagonal(a, 5)
    >>> a
    array([[5, 0, 0],
           [0, 5, 0],
           [0, 0, 5]])

    The same function can operate on a 4-D array:

    >>> a = np.zeros((3, 3, 3, 3), int)
    >>> np.fill_diagonal(a, 4)

    We only show a few blocks for clarity:

    >>> a[0, 0]
    array([[4, 0, 0],
           [0, 0, 0],
           [0, 0, 0]])
    >>> a[1, 1]
    array([[0, 0, 0],
           [0, 4, 0],
           [0, 0, 0]])
    >>> a[2, 2]
    array([[0, 0, 0],
           [0, 0, 0],
           [0, 0, 4]])

    # tall matrices no wrap
    >>> a = np.zeros((5, 3),int)
    >>> fill_diagonal(a, 4)
    array([[4, 0, 0],
           [0, 4, 0],
           [0, 0, 4],
           [0, 0, 0],
           [0, 0, 0]])

    # tall matrices wrap
    >>> a = np.zeros((5, 3),int)
    >>> fill_diagonal(a, 4)
    array([[4, 0, 0],
           [0, 4, 0],
           [0, 0, 4],
           [0, 0, 0],
           [4, 0, 0]])

    # wide matrices
    >>> a = np.zeros((3, 5),int)
    >>> fill_diagonal(a, 4)
    array([[4, 0, 0, 0, 0],
           [0, 4, 0, 0, 0],
           [0, 0, 4, 0, 0]])

    """
    if a.ndim < 2:
        raise ValueError('array must be at least 2-d')
    end = None
    if a.ndim == 2:
        step = a.shape[1] + 1
        if not wrap:
            end = a.shape[1] * a.shape[1]
    else:
        if not alltrue(diff(a.shape) == 0):
            raise ValueError('All dimensions of input must be of equal length')
        step = 1 + cumprod(a.shape[:-1]).sum()
    a.flat[:end:step] = val
    return


def diag_indices(n, ndim=2):
    """
    Return the indices to access the main diagonal of an array.

    This returns a tuple of indices that can be used to access the main
    diagonal of an array `a` with ``a.ndim >= 2`` dimensions and shape
    (n, n, ..., n). For ``a.ndim = 2`` this is the usual diagonal, for
    ``a.ndim > 2`` this is the set of indices to access ``a[i, i, ..., i]``
    for ``i = [0..n-1]``.

    Parameters
    ----------
    n : int
      The size, along each dimension, of the arrays for which the returned
      indices can be used.

    ndim : int, optional
      The number of dimensions.

    See also
    --------
    diag_indices_from

    Notes
    -----
    .. versionadded:: 1.4.0

    Examples
    --------
    Create a set of indices to access the diagonal of a (4, 4) array:

    >>> di = np.diag_indices(4)
    >>> di
    (array([0, 1, 2, 3]), array([0, 1, 2, 3]))
    >>> a = np.arange(16).reshape(4, 4)
    >>> a
    array([[ 0,  1,  2,  3],
           [ 4,  5,  6,  7],
           [ 8,  9, 10, 11],
           [12, 13, 14, 15]])
    >>> a[di] = 100
    >>> a
    array([[100,   1,   2,   3],
           [  4, 100,   6,   7],
           [  8,   9, 100,  11],
           [ 12,  13,  14, 100]])

    Now, we create indices to manipulate a 3-D array:

    >>> d3 = np.diag_indices(2, 3)
    >>> d3
    (array([0, 1]), array([0, 1]), array([0, 1]))

    And use it to set the diagonal of an array of zeros to 1:

    >>> a = np.zeros((2, 2, 2), dtype=np.int)
    >>> a[d3] = 1
    >>> a
    array([[[1, 0],
            [0, 0]],
           [[0, 0],
            [0, 1]]])

    """
    idx = arange(n)
    return (idx,) * ndim


def diag_indices_from(arr):
    """
    Return the indices to access the main diagonal of an n-dimensional array.

    See `diag_indices` for full details.

    Parameters
    ----------
    arr : array, at least 2-D

    See Also
    --------
    diag_indices

    Notes
    -----
    .. versionadded:: 1.4.0

    """
    if not arr.ndim >= 2:
        raise ValueError('input array must be at least 2-d')
    if not alltrue(diff(arr.shape) == 0):
        raise ValueError('All dimensions of input must be of equal length')
    return diag_indices(arr.shape[0], arr.ndim)