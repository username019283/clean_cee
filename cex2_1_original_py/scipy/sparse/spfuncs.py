# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\spfuncs.pyc
# Compiled at: 2013-02-16 13:27:32
""" Functions that operate on sparse matrices
"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'count_blocks', 'estimate_blocksize']
from .csr import isspmatrix_csr, csr_matrix
from .csc import isspmatrix_csc
from .sparsetools import csr_count_blocks

def extract_diagonal(A):
    raise NotImplementedError('use .diagonal() instead')


def estimate_blocksize(A, efficiency=0.7):
    """Attempt to determine the blocksize of a sparse matrix

    Returns a blocksize=(r,c) such that
        - A.nnz / A.tobsr( (r,c) ).nnz > efficiency
    """
    if not (isspmatrix_csr(A) or isspmatrix_csc(A)):
        A = csr_matrix(A)
    if A.nnz == 0:
        return (1, 1)
    if not 0 < efficiency < 1.0:
        raise ValueError('efficiency must satisfy 0.0 < efficiency < 1.0')
    high_efficiency = (1.0 + efficiency) / 2.0
    nnz = float(A.nnz)
    M, N = A.shape
    if M % 2 == 0 and N % 2 == 0:
        e22 = nnz / (4 * count_blocks(A, (2, 2)))
    else:
        e22 = 0.0
    if M % 3 == 0 and N % 3 == 0:
        e33 = nnz / (9 * count_blocks(A, (3, 3)))
    else:
        e33 = 0.0
    if e22 > high_efficiency and e33 > high_efficiency:
        e66 = nnz / (36 * count_blocks(A, (6, 6)))
        if e66 > efficiency:
            return (6, 6)
        return (3, 3)
    else:
        if M % 4 == 0 and N % 4 == 0:
            e44 = nnz / (16 * count_blocks(A, (4, 4)))
        else:
            e44 = 0.0
        if e44 > efficiency:
            return (4, 4)
        if e33 > efficiency:
            return (3, 3)
        if e22 > efficiency:
            return (2, 2)
        return (1, 1)


def count_blocks(A, blocksize):
    """For a given blocksize=(r,c) count the number of occupied
    blocks in a sparse matrix A
    """
    r, c = blocksize
    if r < 1 or c < 1:
        raise ValueError('r and c must be positive')
    if isspmatrix_csr(A):
        M, N = A.shape
        return csr_count_blocks(M, N, r, c, A.indptr, A.indices)
    else:
        if isspmatrix_csc(A):
            return count_blocks(A.T, (c, r))
        return count_blocks(csr_matrix(A), blocksize)