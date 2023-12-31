# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\linalg\decomp_lu.pyc
# Compiled at: 2013-02-16 13:27:30
"""LU decomposition functions."""
from __future__ import division, print_function, absolute_import
from warnings import warn
from numpy import asarray, asarray_chkfinite
from .misc import _datacopied
from .lapack import get_lapack_funcs
from .flinalg import get_flinalg_funcs
__all__ = [
 'lu', 'lu_solve', 'lu_factor']

def lu_factor(a, overwrite_a=False, check_finite=True):
    """
    Compute pivoted LU decomposition of a matrix.

    The decomposition is::

        A = P L U

    where P is a permutation matrix, L lower triangular with unit
    diagonal elements, and U upper triangular.

    Parameters
    ----------
    a : (M, M) array_like
        Matrix to decompose
    overwrite_a : boolean
        Whether to overwrite data in A (may increase performance)
    check_finite : boolean, optional
        Whether to check the input matrixes contain only finite numbers.
        Disabling may give a performance gain, but may result to problems
        (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns
    -------
    lu : (N, N) ndarray
        Matrix containing U in its upper triangle, and L in its lower triangle.
        The unit diagonal elements of L are not stored.
    piv : (N,) ndarray
        Pivot indices representing the permutation matrix P:
        row i of matrix was interchanged with row piv[i].

    See also
    --------
    lu_solve : solve an equation system using the LU factorization of a matrix

    Notes
    -----
    This is a wrapper to the ``*GETRF`` routines from LAPACK.

    """
    if check_finite:
        a1 = asarray_chkfinite(a)
    else:
        a1 = asarray(a)
    if len(a1.shape) != 2 or a1.shape[0] != a1.shape[1]:
        raise ValueError('expected square matrix')
    overwrite_a = overwrite_a or _datacopied(a1, a)
    getrf, = get_lapack_funcs(('getrf', ), (a1,))
    lu, piv, info = getrf(a1, overwrite_a=overwrite_a)
    if info < 0:
        raise ValueError('illegal value in %d-th argument of internal getrf (lu_factor)' % -info)
    if info > 0:
        warn('Diagonal number %d is exactly zero. Singular matrix.' % info, RuntimeWarning)
    return (
     lu, piv)


def lu_solve(lu_and_piv, b, trans=0, overwrite_b=False, check_finite=True):
    """Solve an equation system, a x = b, given the LU factorization of a

    Parameters
    ----------
    (lu, piv)
        Factorization of the coefficient matrix a, as given by lu_factor
    b : array
        Right-hand side
    trans : {0, 1, 2}
        Type of system to solve:

        =====  =========
        trans  system
        =====  =========
        0      a x   = b
        1      a^T x = b
        2      a^H x = b
        =====  =========
    check_finite : boolean, optional
        Whether to check the input matrixes contain only finite numbers.
        Disabling may give a performance gain, but may result to problems
        (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns
    -------
    x : array
        Solution to the system

    See also
    --------
    lu_factor : LU factorize a matrix

    """
    lu, piv = lu_and_piv
    if check_finite:
        b1 = asarray_chkfinite(b)
    else:
        b1 = asarray(b)
    overwrite_b = overwrite_b or _datacopied(b1, b)
    if lu.shape[0] != b1.shape[0]:
        raise ValueError('incompatible dimensions.')
    getrs, = get_lapack_funcs(('getrs', ), (lu, b1))
    x, info = getrs(lu, piv, b1, trans=trans, overwrite_b=overwrite_b)
    if info == 0:
        return x
    raise ValueError('illegal value in %d-th argument of internal gesv|posv' % -info)


def lu(a, permute_l=False, overwrite_a=False, check_finite=True):
    """
    Compute pivoted LU decompostion of a matrix.

    The decomposition is::

        A = P L U

    where P is a permutation matrix, L lower triangular with unit
    diagonal elements, and U upper triangular.

    Parameters
    ----------
    a : (M, N) array_like
        Array to decompose
    permute_l : bool
        Perform the multiplication P*L  (Default: do not permute)
    overwrite_a : bool
        Whether to overwrite data in a (may improve performance)
    check_finite : boolean, optional
        Whether to check the input matrixes contain only finite numbers.
        Disabling may give a performance gain, but may result to problems
        (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns
    -------
    **(If permute_l == False)**

    p : (M, M) ndarray
        Permutation matrix
    l : (M, K) ndarray
        Lower triangular or trapezoidal matrix with unit diagonal.
        K = min(M, N)
    u : (K, N) ndarray
        Upper triangular or trapezoidal matrix

    **(If permute_l == True)**

    pl : (M, K) ndarray
        Permuted L matrix.
        K = min(M, N)
    u : (K, N) ndarray
        Upper triangular or trapezoidal matrix

    Notes
    -----
    This is a LU factorization routine written for Scipy.

    """
    if check_finite:
        a1 = asarray_chkfinite(a)
    else:
        a1 = asarray(a)
    if len(a1.shape) != 2:
        raise ValueError('expected matrix')
    overwrite_a = overwrite_a or _datacopied(a1, a)
    flu, = get_flinalg_funcs(('lu', ), (a1,))
    p, l, u, info = flu(a1, permute_l=permute_l, overwrite_a=overwrite_a)
    if info < 0:
        raise ValueError('illegal value in %d-th argument of internal lu.getrf' % -info)
    if permute_l:
        return (l, u)
    return (
     p, l, u)