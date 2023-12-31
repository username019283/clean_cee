# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\linalg\special_matrices.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
import math, numpy as np
from scipy.misc import comb
from scipy.lib.six.moves import xrange
__all__ = [
 'tri', 'tril', 'triu', 'toeplitz', 'circulant', 'hankel', 
 'hadamard', 
 'leslie', 'all_mat', 'kron', 'block_diag', 'companion', 
 'hilbert', 'invhilbert', 
 'pascal']

def tri(N, M=None, k=0, dtype=None):
    """
    Construct (N, M) matrix filled with ones at and below the k-th diagonal.

    The matrix has A[i,j] == 1 for i <= j + k

    Parameters
    ----------
    N : integer
        The size of the first dimension of the matrix.
    M : integer or None
        The size of the second dimension of the matrix. If `M` is None,
        `M = N` is assumed.
    k : integer
        Number of subdiagonal below which matrix is filled with ones.
        `k` = 0 is the main diagonal, `k` < 0 subdiagonal and `k` > 0
        superdiagonal.
    dtype : dtype
        Data type of the matrix.

    Returns
    -------
    tri : (N, M) ndarray
        Tri matrix.

    Examples
    --------
    >>> from scipy.linalg import tri
    >>> tri(3, 5, 2, dtype=int)
    array([[1, 1, 1, 0, 0],
           [1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1]])
    >>> tri(3, 5, -1, dtype=int)
    array([[0, 0, 0, 0, 0],
           [1, 0, 0, 0, 0],
           [1, 1, 0, 0, 0]])

    """
    if M is None:
        M = N
    if type(M) == type('d'):
        dtype = M
        M = N
    m = np.greater_equal(np.subtract.outer(np.arange(N), np.arange(M)), -k)
    if dtype is None:
        return m
    else:
        return m.astype(dtype)
        return


def tril(m, k=0):
    """
    Make a copy of a matrix with elements above the k-th diagonal zeroed.

    Parameters
    ----------
    m : array_like
        Matrix whose elements to return
    k : integer
        Diagonal above which to zero elements.
        `k` == 0 is the main diagonal, `k` < 0 subdiagonal and
        `k` > 0 superdiagonal.

    Returns
    -------
    tril : ndarray
        Return is the same shape and type as `m`.

    Examples
    --------
    >>> from scipy.linalg import tril
    >>> tril([[1,2,3],[4,5,6],[7,8,9],[10,11,12]], -1)
    array([[ 0,  0,  0],
           [ 4,  0,  0],
           [ 7,  8,  0],
           [10, 11, 12]])

    """
    m = np.asarray(m)
    out = tri(m.shape[0], m.shape[1], k=k, dtype=m.dtype.char) * m
    return out


def triu(m, k=0):
    """
    Make a copy of a matrix with elements below the k-th diagonal zeroed.

    Parameters
    ----------
    m : array_like
        Matrix whose elements to return
    k : int, optional
        Diagonal below which to zero elements.
        `k` == 0 is the main diagonal, `k` < 0 subdiagonal and
        `k` > 0 superdiagonal.

    Returns
    -------
    triu : ndarray
        Return matrix with zeroed elements below the k-th diagonal and has
        same shape and type as `m`.

    Examples
    --------
    >>> from scipy.linalg import triu
    >>> triu([[1,2,3],[4,5,6],[7,8,9],[10,11,12]], -1)
    array([[ 1,  2,  3],
           [ 4,  5,  6],
           [ 0,  8,  9],
           [ 0,  0, 12]])

    """
    m = np.asarray(m)
    out = (1 - tri(m.shape[0], m.shape[1], k - 1, m.dtype.char)) * m
    return out


def toeplitz(c, r=None):
    """
    Construct a Toeplitz matrix.

    The Toeplitz matrix has constant diagonals, with c as its first column
    and r as its first row.  If r is not given, ``r == conjugate(c)`` is
    assumed.

    Parameters
    ----------
    c : array_like
        First column of the matrix.  Whatever the actual shape of `c`, it
        will be converted to a 1-D array.
    r : array_like
        First row of the matrix. If None, ``r = conjugate(c)`` is assumed;
        in this case, if c[0] is real, the result is a Hermitian matrix.
        r[0] is ignored; the first row of the returned matrix is
        ``[c[0], r[1:]]``.  Whatever the actual shape of `r`, it will be
        converted to a 1-D array.

    Returns
    -------
    A : (len(c), len(r)) ndarray
        The Toeplitz matrix. Dtype is the same as ``(c[0] + r[0]).dtype``.

    See also
    --------
    circulant : circulant matrix
    hankel : Hankel matrix

    Notes
    -----
    The behavior when `c` or `r` is a scalar, or when `c` is complex and
    `r` is None, was changed in version 0.8.0.  The behavior in previous
    versions was undocumented and is no longer supported.

    Examples
    --------
    >>> from scipy.linalg import toeplitz
    >>> toeplitz([1,2,3], [1,4,5,6])
    array([[1, 4, 5, 6],
           [2, 1, 4, 5],
           [3, 2, 1, 4]])
    >>> toeplitz([1.0, 2+3j, 4-1j])
    array([[ 1.+0.j,  2.-3.j,  4.+1.j],
           [ 2.+3.j,  1.+0.j,  2.-3.j],
           [ 4.-1.j,  2.+3.j,  1.+0.j]])

    """
    c = np.asarray(c).ravel()
    if r is None:
        r = c.conjugate()
    else:
        r = np.asarray(r).ravel()
    vals = np.concatenate((r[-1:0:-1], c))
    a, b = np.ogrid[0:len(c), len(r) - 1:-1:-1]
    indx = a + b
    return vals[indx]


def circulant(c):
    """
    Construct a circulant matrix.

    Parameters
    ----------
    c : (N,) array_like
        1-D array, the first column of the matrix.

    Returns
    -------
    A : (N, N) ndarray
        A circulant matrix whose first column is `c`.

    See also
    --------
    toeplitz : Toeplitz matrix
    hankel : Hankel matrix

    Notes
    -----
    .. versionadded:: 0.8.0

    Examples
    --------
    >>> from scipy.linalg import circulant
    >>> circulant([1, 2, 3])
    array([[1, 3, 2],
           [2, 1, 3],
           [3, 2, 1]])

    """
    c = np.asarray(c).ravel()
    a, b = np.ogrid[0:len(c), 0:-len(c):-1]
    indx = a + b
    return c[indx]


def hankel(c, r=None):
    """
    Construct a Hankel matrix.

    The Hankel matrix has constant anti-diagonals, with `c` as its
    first column and `r` as its last row.  If `r` is not given, then
    `r = zeros_like(c)` is assumed.

    Parameters
    ----------
    c : array_like
        First column of the matrix.  Whatever the actual shape of `c`, it
        will be converted to a 1-D array.
    r : array_like
        Last row of the matrix. If None, ``r = zeros_like(c)`` is assumed.
        r[0] is ignored; the last row of the returned matrix is
        ``[c[-1], r[1:]]``.  Whatever the actual shape of `r`, it will be
        converted to a 1-D array.

    Returns
    -------
    A : (len(c), len(r)) ndarray
        The Hankel matrix. Dtype is the same as ``(c[0] + r[0]).dtype``.

    See also
    --------
    toeplitz : Toeplitz matrix
    circulant : circulant matrix

    Examples
    --------
    >>> from scipy.linalg import hankel
    >>> hankel([1, 17, 99])
    array([[ 1, 17, 99],
           [17, 99,  0],
           [99,  0,  0]])
    >>> hankel([1,2,3,4], [4,7,7,8,9])
    array([[1, 2, 3, 4, 7],
           [2, 3, 4, 7, 7],
           [3, 4, 7, 7, 8],
           [4, 7, 7, 8, 9]])

    """
    c = np.asarray(c).ravel()
    if r is None:
        r = np.zeros_like(c)
    else:
        r = np.asarray(r).ravel()
    vals = np.concatenate((c, r[1:]))
    a, b = np.ogrid[0:len(c), 0:len(r)]
    indx = a + b
    return vals[indx]


def hadamard(n, dtype=int):
    """
    Construct a Hadamard matrix.

    Constructs an n-by-n Hadamard matrix, using Sylvester's
    construction.  `n` must be a power of 2.

    Parameters
    ----------
    n : int
        The order of the matrix.  `n` must be a power of 2.
    dtype : numpy dtype
        The data type of the array to be constructed.

    Returns
    -------
    H : (n, n) ndarray
        The Hadamard matrix.

    Notes
    -----
    .. versionadded:: 0.8.0

    Examples
    --------
    >>> from scipy.linalg import hadamard
    >>> hadamard(2, dtype=complex)
    array([[ 1.+0.j,  1.+0.j],
           [ 1.+0.j, -1.-0.j]])
    >>> hadamard(4)
    array([[ 1,  1,  1,  1],
           [ 1, -1,  1, -1],
           [ 1,  1, -1, -1],
           [ 1, -1, -1,  1]])

    """
    if n < 1:
        lg2 = 0
    else:
        lg2 = int(math.log(n, 2))
    if 2 ** lg2 != n:
        raise ValueError('n must be an positive integer, and n must be a power of 2')
    H = np.array([[1]], dtype=dtype)
    for i in range(0, lg2):
        H = np.vstack((np.hstack((H, H)), np.hstack((H, -H))))

    return H


def leslie(f, s):
    """
    Create a Leslie matrix.

    Given the length n array of fecundity coefficients `f` and the length
    n-1 array of survival coefficents `s`, return the associated Leslie matrix.

    Parameters
    ----------
    f : (N,) array_like
        The "fecundity" coefficients.
    s : (N-1,) array_like
        The "survival" coefficients, has to be 1-D.  The length of `s`
        must be one less than the length of `f`, and it must be at least 1.

    Returns
    -------
    L : (N, N) ndarray
        The array is zero except for the first row,
        which is `f`, and the first sub-diagonal, which is `s`.
        The data-type of the array will be the data-type of ``f[0]+s[0]``.

    Notes
    -----
    .. versionadded:: 0.8.0

    The Leslie matrix is used to model discrete-time, age-structured
    population growth [1]_ [2]_. In a population with `n` age classes, two sets
    of parameters define a Leslie matrix: the `n` "fecundity coefficients",
    which give the number of offspring per-capita produced by each age
    class, and the `n` - 1 "survival coefficients", which give the
    per-capita survival rate of each age class.

    References
    ----------
    .. [1] P. H. Leslie, On the use of matrices in certain population
           mathematics, Biometrika, Vol. 33, No. 3, 183--212 (Nov. 1945)
    .. [2] P. H. Leslie, Some further notes on the use of matrices in
           population mathematics, Biometrika, Vol. 35, No. 3/4, 213--245
           (Dec. 1948)

    Examples
    --------
    >>> from scipy.linalg import leslie
    >>> leslie([0.1, 2.0, 1.0, 0.1], [0.2, 0.8, 0.7])
    array([[ 0.1,  2. ,  1. ,  0.1],
           [ 0.2,  0. ,  0. ,  0. ],
           [ 0. ,  0.8,  0. ,  0. ],
           [ 0. ,  0. ,  0.7,  0. ]])

    """
    f = np.atleast_1d(f)
    s = np.atleast_1d(s)
    if f.ndim != 1:
        raise ValueError('Incorrect shape for f.  f must be one-dimensional')
    if s.ndim != 1:
        raise ValueError('Incorrect shape for s.  s must be one-dimensional')
    if f.size != s.size + 1:
        raise ValueError('Incorrect lengths for f and s.  The length of s must be one less than the length of f.')
    if s.size == 0:
        raise ValueError('The length of s must be at least 1.')
    tmp = f[0] + s[0]
    n = f.size
    a = np.zeros((n, n), dtype=tmp.dtype)
    a[0] = f
    a[(list(range(1, n)), list(range(0, n - 1)))] = s
    return a


def all_mat(*args):
    return list(map(np.matrix, args))


def kron(a, b):
    """
    Kronecker product.

    The result is the block matrix::

        a[0,0]*b    a[0,1]*b  ... a[0,-1]*b
        a[1,0]*b    a[1,1]*b  ... a[1,-1]*b
        ...
        a[-1,0]*b   a[-1,1]*b ... a[-1,-1]*b

    Parameters
    ----------
    a : (M, N) ndarray
        Input array
    b : (P, Q) ndarray
        Input array

    Returns
    -------
    A : (M*P, N*Q) ndarray
        Kronecker product of `a` and `b`.

    Examples
    --------
    >>> from numpy import array
    >>> from scipy.linalg import kron
    >>> kron(array([[1,2],[3,4]]), array([[1,1,1]]))
    array([[1, 1, 1, 2, 2, 2],
           [3, 3, 3, 4, 4, 4]])

    """
    if not a.flags['CONTIGUOUS']:
        a = np.reshape(a, a.shape)
    if not b.flags['CONTIGUOUS']:
        b = np.reshape(b, b.shape)
    o = np.outer(a, b)
    o = o.reshape(a.shape + b.shape)
    return np.concatenate(np.concatenate(o, axis=1), axis=1)


def block_diag(*arrs):
    """
    Create a block diagonal matrix from provided arrays.

    Given the inputs `A`, `B` and `C`, the output will have these
    arrays arranged on the diagonal::

        [[A, 0, 0],
         [0, B, 0],
         [0, 0, C]]

    Parameters
    ----------
    A, B, C, ... : array_like, up to 2-D
        Input arrays.  A 1-D array or array_like sequence of length `n`is
        treated as a 2-D array with shape ``(1,n)``.

    Returns
    -------
    D : ndarray
        Array with `A`, `B`, `C`, ... on the diagonal.  `D` has the
        same dtype as `A`.

    Notes
    -----
    If all the input arrays are square, the output is known as a
    block diagonal matrix.

    Examples
    --------
    >>> from scipy.linalg import block_diag
    >>> A = [[1, 0],
    ...      [0, 1]]
    >>> B = [[3, 4, 5],
    ...      [6, 7, 8]]
    >>> C = [[7]]
    >>> block_diag(A, B, C)
    [[1 0 0 0 0 0]
     [0 1 0 0 0 0]
     [0 0 3 4 5 0]
     [0 0 6 7 8 0]
     [0 0 0 0 0 7]]
    >>> block_diag(1.0, [2, 3], [[4, 5], [6, 7]])
    array([[ 1.,  0.,  0.,  0.,  0.],
           [ 0.,  2.,  3.,  0.,  0.],
           [ 0.,  0.,  0.,  4.,  5.],
           [ 0.,  0.,  0.,  6.,  7.]])

    """
    if arrs == ():
        arrs = ([],)
    arrs = [ np.atleast_2d(a) for a in arrs ]
    bad_args = [ k for k in range(len(arrs)) if arrs[k].ndim > 2 ]
    if bad_args:
        raise ValueError('arguments in the following positions have dimension greater than 2: %s' % bad_args)
    shapes = np.array([ a.shape for a in arrs ])
    out = np.zeros(np.sum(shapes, axis=0), dtype=arrs[0].dtype)
    r, c = (0, 0)
    for i, (rr, cc) in enumerate(shapes):
        out[r:r + rr, c:c + cc] = arrs[i]
        r += rr
        c += cc

    return out


def companion(a):
    """
    Create a companion matrix.

    Create the companion matrix [1]_ associated with the polynomial whose
    coefficients are given in `a`.

    Parameters
    ----------
    a : (N,) array_like
        1-D array of polynomial coefficients.  The length of `a` must be
        at least two, and ``a[0]`` must not be zero.

    Returns
    -------
    c : (N-1, N-1) ndarray
        The first row of `c` is ``-a[1:]/a[0]``, and the first
        sub-diagonal is all ones.  The data-type of the array is the same
        as the data-type of ``1.0*a[0]``.

    Raises
    ------
    ValueError
        If any of the following are true: a) ``a.ndim != 1``;
        b) ``a.size < 2``; c) ``a[0] == 0``.

    Notes
    -----
    .. versionadded:: 0.8.0

    References
    ----------
    .. [1] R. A. Horn & C. R. Johnson, *Matrix Analysis*.  Cambridge, UK:
        Cambridge University Press, 1999, pp. 146-7.

    Examples
    --------
    >>> from scipy.linalg import companion
    >>> companion([1, -10, 31, -30])
    array([[ 10., -31.,  30.],
           [  1.,   0.,   0.],
           [  0.,   1.,   0.]])

    """
    a = np.atleast_1d(a)
    if a.ndim != 1:
        raise ValueError('Incorrect shape for `a`.  `a` must be one-dimensional.')
    if a.size < 2:
        raise ValueError('The length of `a` must be at least 2.')
    if a[0] == 0:
        raise ValueError('The first coefficient in `a` must not be zero.')
    first_row = -a[1:] / (1.0 * a[0])
    n = a.size
    c = np.zeros((n - 1, n - 1), dtype=first_row.dtype)
    c[0] = first_row
    c[(list(range(1, n - 1)), list(range(0, n - 2)))] = 1
    return c


def hilbert(n):
    """
    Create a Hilbert matrix of order `n`.

    Returns the `n` by `n` array with entries `h[i,j] = 1 / (i + j + 1)`.

    Parameters
    ----------
    n : int
        The size of the array to create.

    Returns
    -------
    h : (n, n) ndarray
        The Hilbert matrix.

    See Also
    --------
    invhilbert : Compute the inverse of a Hilbert matrix.

    Notes
    -----
    .. versionadded:: 0.10.0

    Examples
    --------
    >>> from scipy.linalg import hilbert
    >>> hilbert(3)
    array([[ 1.        ,  0.5       ,  0.33333333],
           [ 0.5       ,  0.33333333,  0.25      ],
           [ 0.33333333,  0.25      ,  0.2       ]])

    """
    values = 1.0 / (1.0 + np.arange(2 * n - 1))
    h = hankel(values[:n], r=values[n - 1:])
    return h


def invhilbert(n, exact=False):
    """
    Compute the inverse of the Hilbert matrix of order `n`.

    The entries in the inverse of a Hilbert matrix are integers.  When `n`
    is greater than 14, some entries in the inverse exceed the upper limit
    of 64 bit integers.  The `exact` argument provides two options for
    dealing with these large integers.

    Parameters
    ----------
    n : int
        The order of the Hilbert matrix.
    exact : bool
        If False, the data type of the array that is returned is np.float64,
        and the array is an approximation of the inverse.
        If True, the array is the exact integer inverse array.  To represent
        the exact inverse when n > 14, the returned array is an object array
        of long integers.  For n <= 14, the exact inverse is returned as an
        array with data type np.int64.

    Returns
    -------
    invh : (n, n) ndarray
        The data type of the array is np.float64 if `exact` is False.
        If `exact` is True, the data type is either np.int64 (for n <= 14)
        or object (for n > 14).  In the latter case, the objects in the
        array will be long integers.

    See Also
    --------
    hilbert : Create a Hilbert matrix.

    Notes
    -----
    .. versionadded:: 0.10.0

    Examples
    --------
    >>> from scipy.linalg import invhilbert
    >>> invhilbert(4)
    array([[   16.,  -120.,   240.,  -140.],
           [ -120.,  1200., -2700.,  1680.],
           [  240., -2700.,  6480., -4200.],
           [ -140.,  1680., -4200.,  2800.]])
    >>> invhilbert(4, exact=True)
    array([[   16,  -120,   240,  -140],
           [ -120,  1200, -2700,  1680],
           [  240, -2700,  6480, -4200],
           [ -140,  1680, -4200,  2800]], dtype=int64)
    >>> invhilbert(16)[7,7]
    4.2475099528537506e+19
    >>> invhilbert(16, exact=True)[7,7]
    42475099528537378560L

    """
    if exact:
        if n > 14:
            dtype = object
        else:
            dtype = np.int64
    else:
        dtype = np.float64
    invh = np.empty((n, n), dtype=dtype)
    for i in xrange(n):
        for j in xrange(0, i + 1):
            s = i + j
            invh[(i, j)] = (-1) ** s * (s + 1) * comb(n + i, n - j - 1, exact) * comb(n + j, n - i - 1, exact) * comb(s, i, exact) ** 2
            if i != j:
                invh[(j, i)] = invh[(i, j)]

    return invh


def pascal(n, kind='symmetric', exact=True):
    """
    Returns the n x n Pascal matrix.

    The Pascal matrix is a matrix containing the binomial coefficients as
    its elements.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    n : int
        The size of the matrix to create; that is, the result is an n x n
        matrix.
    kind : str, optional
        Must be one of 'symmetric', 'lower', or 'upper'.
        Default is 'symmetric'.
    exact : bool, optional
        If `exact` is True, the result is either an array of type
        numpy.uint64 (if n <= 35) or an object array of Python long integers.
        If `exact` is False, the coefficients in the matrix are computed using
        `scipy.misc.comb` with `exact=False`.  The result will be a floating
        point array, and the values in the array will not be the exact
        coefficients, but this version is much faster than `exact=True`.

    Returns
    -------
    p : (n, n) ndarray
        The Pascal matrix.

    Notes
    -----
    See http://en.wikipedia.org/wiki/Pascal_matrix for more information
    about Pascal matrices.

    Examples
    --------
    >>> from scipy.linalg import pascal
    >>> pascal(4)
    array([[ 1,  1,  1,  1],
           [ 1,  2,  3,  4],
           [ 1,  3,  6, 10],
           [ 1,  4, 10, 20]], dtype=uint64)
    >>> pascal(4, kind='lower')
    array([[1, 0, 0, 0],
           [1, 1, 0, 0],
           [1, 2, 1, 0],
           [1, 3, 3, 1]], dtype=uint64)
    >>> pascal(50)[-1, -1]
    25477612258980856902730428600L
    >>> from scipy.misc import comb
    >>> comb(98, 49, exact=True)
    25477612258980856902730428600L

    """
    if kind not in ('symmetric', 'lower', 'upper'):
        raise ValueError("kind must be 'symmetric', 'lower', or 'upper'")
    if exact:
        if n > 35:
            L_n = np.empty((n, n), dtype=object)
            L_n.fill(0)
        else:
            L_n = np.zeros((n, n), dtype=np.uint64)
        for i in range(n):
            for j in range(i + 1):
                L_n[(i, j)] = comb(i, j, exact=True)

    else:
        L_n = comb(*np.ogrid[:n, :n])
    if kind is 'lower':
        p = L_n
    elif kind is 'upper':
        p = L_n.T
    else:
        p = np.dot(L_n, L_n.T)
    return p