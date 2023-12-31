# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\base.pyc
# Compiled at: 2013-02-16 13:27:32
"""Base class for sparse matrices"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'spmatrix', 'isspmatrix', 'issparse', 
 'SparseWarning', 'SparseEfficiencyWarning']
import sys
from warnings import warn
import numpy as np
from scipy.lib.six.moves import xrange
from .sputils import isdense, isscalarlike, isintlike

class SparseWarning(Warning):
    pass


class SparseFormatWarning(SparseWarning):
    pass


class SparseEfficiencyWarning(SparseWarning):
    pass


_formats = {'csc': [0, 'Compressed Sparse Column'], 'csr': [
         1, 'Compressed Sparse Row'], 
   'dok': [
         2, 'Dictionary Of Keys'], 
   'lil': [
         3, 'LInked List'], 
   'dod': [
         4, 'Dictionary of Dictionaries'], 
   'sss': [
         5, 'Symmetric Sparse Skyline'], 
   'coo': [
         6, 'COOrdinate'], 
   'lba': [
         7, 'Linpack BAnded'], 
   'egd': [
         8, 'Ellpack-itpack Generalized Diagonal'], 
   'dia': [
         9, 'DIAgonal'], 
   'bsr': [
         10, 'Block Sparse Row'], 
   'msr': [
         11, 'Modified compressed Sparse Row'], 
   'bsc': [
         12, 'Block Sparse Column'], 
   'msc': [
         13, 'Modified compressed Sparse Column'], 
   'ssk': [
         14, 'Symmetric SKyline'], 
   'nsk': [
         15, 'Nonsymmetric SKyline'], 
   'jad': [
         16, 'JAgged Diagonal'], 
   'uss': [
         17, 'Unsymmetric Sparse Skyline'], 
   'vbr': [
         18, 'Variable Block Row'], 
   'und': [
         19, 'Undefined']}
MAXPRINT = 50

class spmatrix(object):
    """ This class provides a base class for all sparse matrices.  It
    cannot be instantiated.  Most of the work is provided by subclasses.
    """
    __array_priority__ = 10.1
    ndim = 2

    def __init__(self, maxprint=MAXPRINT):
        self.format = self.__class__.__name__[:3]
        self._shape = None
        if self.format == 'spm':
            raise ValueError('This class is not intended to be instantiated directly.')
        self.maxprint = maxprint
        return

    def set_shape(self, shape):
        shape = tuple(shape)
        if len(shape) != 2:
            raise ValueError('Only two-dimensional sparse arrays are supported.')
        try:
            shape = (
             int(shape[0]), int(shape[1]))
        except:
            raise TypeError('invalid shape')

        if not (shape[0] >= 1 and shape[1] >= 1):
            raise ValueError('invalid shape')
        if self._shape != shape and self._shape is not None:
            try:
                self = self.reshape(shape)
            except NotImplementedError:
                raise NotImplementedError('Reshaping not implemented for %s.' % self.__class__.__name__)

        self._shape = shape
        return

    def get_shape(self):
        return self._shape

    shape = property(fget=get_shape, fset=set_shape)

    def reshape(self, shape):
        raise NotImplementedError

    def astype(self, t):
        return self.tocsr().astype(t).asformat(self.format)

    def asfptype(self):
        """Upcast matrix to a floating point format (if necessary)"""
        fp_types = [
         'f', 'd', 'F', 'D']
        if self.dtype.char in fp_types:
            return self
        for fp_type in fp_types:
            if self.dtype <= np.dtype(fp_type):
                return self.astype(fp_type)

        raise TypeError('cannot upcast [%s] to a floating point format' % self.dtype.name)

    def __iter__(self):
        for r in xrange(self.shape[0]):
            yield self[r, :]

    def getmaxprint(self):
        try:
            maxprint = self.maxprint
        except AttributeError:
            maxprint = MAXPRINT

        return maxprint

    def getnnz(self):
        try:
            return self.nnz
        except AttributeError:
            raise AttributeError('nnz not defined')

    def getformat(self):
        try:
            format = self.format
        except AttributeError:
            format = 'und'

        return format

    def __repr__(self):
        nnz = self.getnnz()
        format = self.getformat()
        return "<%dx%d sparse matrix of type '%s'\n\twith %d stored elements in %s format>" % (self.shape + (self.dtype.type, nnz, _formats[format][1]))

    def __str__(self):
        maxprint = self.getmaxprint()
        A = self.tocoo()
        nnz = self.getnnz()

        def tostr(row, col, data):
            triples = zip(list(zip(row, col)), data)
            return ('\n').join([ '  %s\t%s' % t for t in triples ])

        if nnz > maxprint:
            half = maxprint // 2
            out = tostr(A.row[:half], A.col[:half], A.data[:half])
            out += '\n  :\t:\n'
            half = maxprint - maxprint // 2
            out += tostr(A.row[-half:], A.col[-half:], A.data[-half:])
        else:
            out = tostr(A.row, A.col, A.data)
        return out

    if sys.version_info[0] >= 3:

        def __bool__(self):
            return self.getnnz() > 0

    else:

        def __nonzero__(self):
            return self.getnnz() > 0

    def __len__(self):
        raise TypeError('sparse matrix length is ambiguous; use getnnz() or shape[0]')

    def asformat(self, format):
        """Return this matrix in a given sparse format

        Parameters
        ----------
        format : {string, None}
            desired sparse matrix format
                - None for no format conversion
                - "csr" for csr_matrix format
                - "csc" for csc_matrix format
                - "lil" for lil_matrix format
                - "dok" for dok_matrix format and so on

        """
        if format is None or format == self.format:
            return self
        return getattr(self, 'to' + format)()
        return

    def multiply(self, other):
        """Point-wise multiplication by another matrix
        """
        return self.tocsr().multiply(other)

    def dot(self, other):
        return self * other

    def __abs__(self):
        return abs(self.tocsr())

    def __add__(self, other):
        return self.tocsr().__add__(other)

    def __radd__(self, other):
        return self.tocsr().__radd__(other)

    def __sub__(self, other):
        return self.tocsr().__sub__(other)

    def __rsub__(self, other):
        return self.tocsr().__rsub__(other)

    def __mul__(self, other):
        """interpret other and call one of the following

        self._mul_scalar()
        self._mul_vector()
        self._mul_multivector()
        self._mul_sparse_matrix()
        """
        M, N = self.shape
        if other.__class__ is np.ndarray:
            if other.shape == (N,):
                return self._mul_vector(other)
            if other.shape == (N, 1):
                return self._mul_vector(other.ravel()).reshape(M, 1)
            if other.ndim == 2 and other.shape[0] == N:
                return self._mul_multivector(other)
        if isscalarlike(other):
            return self._mul_scalar(other)
        if issparse(other):
            if self.shape[1] != other.shape[0]:
                raise ValueError('dimension mismatch')
            return self._mul_sparse_matrix(other)
        try:
            other.shape
        except AttributeError:
            other = np.asanyarray(other)

        other = np.asanyarray(other)
        if other.ndim == 1 or other.ndim == 2 and other.shape[1] == 1:
            if other.shape != (N,) and other.shape != (N, 1):
                raise ValueError('dimension mismatch')
            result = self._mul_vector(np.ravel(other))
            if isinstance(other, np.matrix):
                result = np.asmatrix(result)
            if other.ndim == 2 and other.shape[1] == 1:
                result = result.reshape(-1, 1)
            return result
        if other.ndim == 2:
            if other.shape[0] != self.shape[1]:
                raise ValueError('dimension mismatch')
            result = self._mul_multivector(np.asarray(other))
            if isinstance(other, np.matrix):
                result = np.asmatrix(result)
            return result
        raise ValueError('could not interpret dimensions')

    def _mul_scalar(self, other):
        return self.tocsr()._mul_scalar(other)

    def _mul_vector(self, other):
        return self.tocsr()._mul_vector(other)

    def _mul_multivector(self, other):
        return self.tocsr()._mul_multivector(other)

    def _mul_sparse_matrix(self, other):
        return self.tocsr()._mul_sparse_matrix(other)

    def __rmul__(self, other):
        if isscalarlike(other):
            return self.__mul__(other)
        else:
            try:
                tr = other.transpose()
            except AttributeError:
                tr = np.asarray(other).transpose()

            return (self.transpose() * tr).transpose()

    def __truediv__(self, other):
        if isscalarlike(other):
            return self * (1.0 / other)
        else:
            return self.tocsr().__truediv__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __neg__(self):
        return -self.tocsr()

    def __iadd__(self, other):
        raise NotImplementedError

    def __isub__(self, other):
        raise NotImplementedError

    def __imul__(self, other):
        raise NotImplementedError

    def __idiv__(self, other):
        return self.__itruediv__(other)

    def __itruediv__(self, other):
        raise NotImplementedError

    def __pow__(self, other):
        if self.shape[0] != self.shape[1]:
            raise TypeError('matrix is not square')
        if isintlike(other):
            other = int(other)
            if other < 0:
                raise ValueError('exponent must be >= 0')
            if other == 0:
                from .construct import eye
                return eye(self.shape[0], dtype=self.dtype)
            if other == 1:
                return self.copy()
            result = self
            for i in range(1, other):
                result = result * self

            return result
        elif isscalarlike(other):
            raise ValueError('exponent must be an integer')
        else:
            raise NotImplementedError

    def __getattr__(self, attr):
        if attr == 'A':
            return self.toarray()
        if attr == 'T':
            return self.transpose()
        if attr == 'H':
            return self.getH()
        if attr == 'real':
            return self._real()
        if attr == 'imag':
            return self._imag()
        if attr == 'size':
            return self.getnnz()
        raise AttributeError(attr + ' not found')

    def transpose(self):
        return self.tocsr().transpose()

    def conj(self):
        return self.tocsr().conj()

    def conjugate(self):
        return self.conj()

    def getH(self):
        return self.transpose().conj()

    def _real(self):
        return self.tocsr()._real()

    def _imag(self):
        return self.tocsr()._imag()

    def nonzero(self):
        """nonzero indices

        Returns a tuple of arrays (row,col) containing the indices
        of the non-zero elements of the matrix.

        Examples
        --------
        >>> from scipy.sparse import csr_matrix
        >>> A = csr_matrix([[1,2,0],[0,0,3],[4,0,5]])
        >>> A.nonzero()
        (array([0, 0, 1, 2, 2]), array([0, 1, 2, 0, 2]))

        """
        A = self.tocoo()
        nz_mask = A.data != 0
        return (A.row[nz_mask], A.col[nz_mask])

    def getcol(self, j):
        """Returns a copy of column j of the matrix, as an (m x 1) sparse
        matrix (column vector).
        """
        from .csc import csc_matrix
        n = self.shape[1]
        if j < 0:
            j += n
        if j < 0 or j >= n:
            raise IndexError('index out of bounds')
        col_selector = csc_matrix(([1], [[j], [0]]), shape=(n, 1), dtype=self.dtype)
        return self * col_selector

    def getrow(self, i):
        """Returns a copy of row i of the matrix, as a (1 x n) sparse
        matrix (row vector).
        """
        from .csr import csr_matrix
        m = self.shape[0]
        if i < 0:
            i += m
        if i < 0 or i >= m:
            raise IndexError('index out of bounds')
        row_selector = csr_matrix(([1], [[0], [i]]), shape=(1, m), dtype=self.dtype)
        return row_selector * self

    def todense(self, order=None, out=None):
        """
        Return a dense matrix representation of this matrix.

        Parameters
        ----------
        order : {'C', 'F'}, optional
            Whether to store multi-dimensional data in C (row-major)
            or Fortran (column-major) order in memory. The default
            is 'None', indicating the NumPy default of C-ordered.
            Cannot be specified in conjunction with the `out`
            argument.

        out : ndarray, 2-dimensional, optional
            If specified, uses this array (or `numpy.matrix`) as the
            output buffer instead of allocating a new array to
            return. The provided array must have the same shape and
            dtype as the sparse matrix on which you are calling the
            method.

        Returns
        -------
        arr : numpy.matrix, 2-dimensional
            A NumPy matrix object with the same shape and containing
            the same data represented by the sparse matrix, with the
            requested memory order. If `out` was passed and was an
            array (rather than a `numpy.matrix`), it will be filled
            with the appropriate values and returned wrapped in a
            `numpy.matrix` object that shares the same memory.
        """
        return np.asmatrix(self.toarray(order=order, out=out))

    def toarray(self, order=None, out=None):
        """
        Return a dense ndarray representation of this matrix.

        Parameters
        ----------
        order : {'C', 'F'}, optional
            Whether to store multi-dimensional data in C (row-major)
            or Fortran (column-major) order in memory. The default
            is 'None', indicating the NumPy default of C-ordered.
            Cannot be specified in conjunction with the `out`
            argument.

        out : ndarray, 2-dimensional, optional
            If specified, uses this array as the output buffer
            instead of allocating a new array to return. The provided
            array must have the same shape and dtype as the sparse
            matrix on which you are calling the method. For most
            sparse types, `out` is required to be memory contiguous
            (either C or Fortran ordered).

        Returns
        -------
        arr : ndarray, 2-dimensional
            An array with the same shape and containing the same
            data represented by the sparse matrix, with the requested
            memory order. If `out` was passed, the same object is
            returned after being modified in-place to contain the
            appropriate values.
        """
        return self.tocoo().toarray(order=order, out=out)

    def todok(self):
        return self.tocoo().todok()

    def tocoo(self):
        return self.tocsr().tocoo()

    def tolil(self):
        return self.tocsr().tolil()

    def todia(self):
        return self.tocoo().todia()

    def tobsr(self, blocksize=None):
        return self.tocsr().tobsr(blocksize=blocksize)

    def copy(self):
        return self.__class__(self, copy=True)

    def sum(self, axis=None):
        """Sum the matrix over the given axis.  If the axis is None, sum
        over both rows and columns, returning a scalar.
        """
        m, n = self.shape
        if axis == 0:
            return np.asmatrix(np.ones((1, m), dtype=self.dtype)) * self
        else:
            if axis == 1:
                return self * np.asmatrix(np.ones((n, 1), dtype=self.dtype))
            if axis is None:
                return (self * np.asmatrix(np.ones((n, 1), dtype=self.dtype))).sum()
            raise ValueError('axis out of bounds')
            return

    def mean(self, axis=None):
        """Average the matrix over the given axis.  If the axis is None,
        average over both rows and columns, returning a scalar.
        """
        if axis == 0:
            mean = self.sum(0)
            mean *= 1.0 / self.shape[0]
            return mean
        else:
            if axis == 1:
                mean = self.sum(1)
                mean *= 1.0 / self.shape[1]
                return mean
            if axis is None:
                return self.sum(None) * 1.0 / (self.shape[0] * self.shape[1])
            raise ValueError('axis out of bounds')
            return

    def diagonal(self):
        """Returns the main diagonal of the matrix
        """
        return self.tocsr().diagonal()

    def setdiag(self, values, k=0):
        """Fills the diagonal elements {a_ii} with the values from the
        given sequence.  If k != 0, fills the off-diagonal elements
        {a_{i,i+k}} instead.

        values may have any length.  If the diagonal is longer than values,
        then the remaining diagonal entries will not be set.  If values if
        longer than the diagonal, then the remaining values are ignored.
        """
        M, N = self.shape
        if k > 0 and k >= N or k < 0 and -k >= M:
            raise ValueError('k exceedes matrix dimensions')
        if k < 0:
            max_index = min(M + k, N, len(values))
            for i, v in enumerate(values[:max_index]):
                self[(i - k, i)] = v

        else:
            max_index = min(M, N - k, len(values))
            for i, v in enumerate(values[:max_index]):
                self[(i, i + k)] = v

    def _process_toarray_args(self, order, out):
        if out is not None:
            if order is not None:
                raise ValueError('order cannot be specified if out is not None')
            if out.shape != self.shape or out.dtype != self.dtype:
                raise ValueError('out array must be same dtype and shape as sparse matrix')
            out[...] = 0.0
            return out
        else:
            return np.zeros(self.shape, dtype=self.dtype, order=order)
            return


def isspmatrix(x):
    return isinstance(x, spmatrix)


issparse = isspmatrix