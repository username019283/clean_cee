# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\linalg\dsolve\umfpack\umfpack.pyc
# Compiled at: 2013-02-16 13:27:32
"""
Interface to the UMFPACK library.

--
Author: Robert Cimrman
"""
from __future__ import division, print_function, absolute_import
import re, warnings
from scipy.lib.six import iteritems
import numpy as np, scipy.sparse as sp
try:
    from . import _umfpack as _um
except:
    _um = None

assumeSortedIndices = False

class UmfpackWarning(UserWarning):
    pass


def configure(**kwargs):
    """
    Valid keyword arguments with defaults (other ignored):
      assumeSortedIndices = False

    Umfpack requires a CSR/CSC matrix to have sorted column/row indices. If
    sure that the matrix fulfills this, pass assumeSortedIndices =
    True to gain some speed.
    """
    if 'assumeSortedIndices' in kwargs:
        globals()['assumeSortedIndices'] = kwargs['assumeSortedIndices']


def updateDictWithVars(adict, module, pattern, group=None):
    match = re.compile(pattern).match
    for name in [ ii for ii in vars(module).keys() if match(ii)
                ]:
        if group is not None:
            outName = match(name).group(group)
        else:
            outName = name
        adict[outName] = module.__dict__[name]

    return adict


umfControls = [
 'UMFPACK_PRL', 
 'UMFPACK_DENSE_ROW', 
 'UMFPACK_DENSE_COL', 
 'UMFPACK_BLOCK_SIZE', 
 'UMFPACK_STRATEGY', 
 'UMFPACK_2BY2_TOLERANCE', 
 'UMFPACK_FIXQ', 
 'UMFPACK_AMD_DENSE', 
 'UMFPACK_AGGRESSIVE', 
 'UMFPACK_PIVOT_TOLERANCE', 
 'UMFPACK_ALLOC_INIT', 
 'UMFPACK_SYM_PIVOT_TOLERANCE', 
 'UMFPACK_SCALE', 
 'UMFPACK_FRONT_ALLOC_INIT', 
 'UMFPACK_DROPTOL', 
 'UMFPACK_IRSTEP', 
 'UMFPACK_COMPILED_WITH_BLAS', 
 'UMFPACK_COMPILED_FOR_MATLAB', 
 'UMFPACK_COMPILED_WITH_GETRUSAGE', 
 'UMFPACK_COMPILED_IN_DEBUG_MODE', 
 'UMFPACK_STRATEGY_AUTO', 
 'UMFPACK_STRATEGY_UNSYMMETRIC', 
 'UMFPACK_STRATEGY_2BY2', 
 'UMFPACK_STRATEGY_SYMMETRIC', 
 'UMFPACK_SCALE_NONE', 
 'UMFPACK_SCALE_SUM', 
 'UMFPACK_SCALE_MAX']
umfInfo = [
 'UMFPACK_STATUS', 
 'UMFPACK_NROW', 
 'UMFPACK_NCOL', 
 'UMFPACK_NZ', 
 'UMFPACK_SIZE_OF_UNIT', 
 'UMFPACK_SIZE_OF_INT', 
 'UMFPACK_SIZE_OF_LONG', 
 'UMFPACK_SIZE_OF_POINTER', 
 'UMFPACK_SIZE_OF_ENTRY', 
 'UMFPACK_NDENSE_ROW', 
 'UMFPACK_NEMPTY_ROW', 
 'UMFPACK_NDENSE_COL', 
 'UMFPACK_NEMPTY_COL', 
 'UMFPACK_SYMBOLIC_DEFRAG', 
 'UMFPACK_SYMBOLIC_PEAK_MEMORY', 
 'UMFPACK_SYMBOLIC_SIZE', 
 'UMFPACK_SYMBOLIC_TIME', 
 'UMFPACK_SYMBOLIC_WALLTIME', 
 'UMFPACK_STRATEGY_USED', 
 'UMFPACK_ORDERING_USED', 
 'UMFPACK_QFIXED', 
 'UMFPACK_DIAG_PREFERRED', 
 'UMFPACK_PATTERN_SYMMETRY', 
 'UMFPACK_NZ_A_PLUS_AT', 
 'UMFPACK_NZDIAG', 
 'UMFPACK_SYMMETRIC_LUNZ', 
 'UMFPACK_SYMMETRIC_FLOPS', 
 'UMFPACK_SYMMETRIC_NDENSE', 
 'UMFPACK_SYMMETRIC_DMAX', 
 'UMFPACK_2BY2_NWEAK', 
 'UMFPACK_2BY2_UNMATCHED', 
 'UMFPACK_2BY2_PATTERN_SYMMETRY', 
 'UMFPACK_2BY2_NZ_PA_PLUS_PAT', 
 'UMFPACK_2BY2_NZDIAG', 
 'UMFPACK_COL_SINGLETONS', 
 'UMFPACK_ROW_SINGLETONS', 
 'UMFPACK_N2', 
 'UMFPACK_S_SYMMETRIC', 
 'UMFPACK_NUMERIC_SIZE_ESTIMATE', 
 'UMFPACK_PEAK_MEMORY_ESTIMATE', 
 'UMFPACK_FLOPS_ESTIMATE', 
 'UMFPACK_LNZ_ESTIMATE', 
 'UMFPACK_UNZ_ESTIMATE', 
 'UMFPACK_VARIABLE_INIT_ESTIMATE', 
 'UMFPACK_VARIABLE_PEAK_ESTIMATE', 
 'UMFPACK_VARIABLE_FINAL_ESTIMATE', 
 'UMFPACK_MAX_FRONT_SIZE_ESTIMATE', 
 'UMFPACK_MAX_FRONT_NROWS_ESTIMATE', 
 'UMFPACK_MAX_FRONT_NCOLS_ESTIMATE', 
 'UMFPACK_NUMERIC_SIZE', 
 'UMFPACK_PEAK_MEMORY', 
 'UMFPACK_FLOPS', 
 'UMFPACK_LNZ', 
 'UMFPACK_UNZ', 
 'UMFPACK_VARIABLE_INIT', 
 'UMFPACK_VARIABLE_PEAK', 
 'UMFPACK_VARIABLE_FINAL', 
 'UMFPACK_MAX_FRONT_SIZE', 
 'UMFPACK_MAX_FRONT_NROWS', 
 'UMFPACK_MAX_FRONT_NCOLS', 
 'UMFPACK_NUMERIC_DEFRAG', 
 'UMFPACK_NUMERIC_REALLOC', 
 'UMFPACK_NUMERIC_COSTLY_REALLOC', 
 'UMFPACK_COMPRESSED_PATTERN', 
 'UMFPACK_LU_ENTRIES', 
 'UMFPACK_NUMERIC_TIME', 
 'UMFPACK_UDIAG_NZ', 
 'UMFPACK_RCOND', 
 'UMFPACK_WAS_SCALED', 
 'UMFPACK_RSMIN', 
 'UMFPACK_RSMAX', 
 'UMFPACK_UMIN', 
 'UMFPACK_UMAX', 
 'UMFPACK_ALLOC_INIT_USED', 
 'UMFPACK_FORCED_UPDATES', 
 'UMFPACK_NUMERIC_WALLTIME', 
 'UMFPACK_NOFF_DIAG', 
 'UMFPACK_ALL_LNZ', 
 'UMFPACK_ALL_UNZ', 
 'UMFPACK_NZDROPPED', 
 'UMFPACK_IR_TAKEN', 
 'UMFPACK_IR_ATTEMPTED', 
 'UMFPACK_OMEGA1', 
 'UMFPACK_OMEGA2', 
 'UMFPACK_SOLVE_FLOPS', 
 'UMFPACK_SOLVE_TIME', 
 'UMFPACK_SOLVE_WALLTIME', 
 'UMFPACK_ORDERING_COLAMD', 
 'UMFPACK_ORDERING_AMD', 
 'UMFPACK_ORDERING_GIVEN']
if _um:
    umfDefines = updateDictWithVars({}, _um, 'UMFPACK_.*')
    locals().update(umfDefines)
    umfStatus = {UMFPACK_OK: 'UMFPACK_OK', 
       UMFPACK_WARNING_singular_matrix: 'UMFPACK_WARNING_singular_matrix', 
       UMFPACK_WARNING_determinant_underflow: 'UMFPACK_WARNING_determinant_underflow', 
       UMFPACK_WARNING_determinant_overflow: 'UMFPACK_WARNING_determinant_overflow', 
       UMFPACK_ERROR_out_of_memory: 'UMFPACK_ERROR_out_of_memory', 
       UMFPACK_ERROR_invalid_Numeric_object: 'UMFPACK_ERROR_invalid_Numeric_object', 
       UMFPACK_ERROR_invalid_Symbolic_object: 'UMFPACK_ERROR_invalid_Symbolic_object', 
       UMFPACK_ERROR_argument_missing: 'UMFPACK_ERROR_argument_missing', 
       UMFPACK_ERROR_n_nonpositive: 'UMFPACK_ERROR_n_nonpositive', 
       UMFPACK_ERROR_invalid_matrix: 'UMFPACK_ERROR_invalid_matrix', 
       UMFPACK_ERROR_different_pattern: 'UMFPACK_ERROR_different_pattern', 
       UMFPACK_ERROR_invalid_system: 'UMFPACK_ERROR_invalid_system', 
       UMFPACK_ERROR_invalid_permutation: 'UMFPACK_ERROR_invalid_permutation', 
       UMFPACK_ERROR_internal_error: 'UMFPACK_ERROR_internal_error', 
       UMFPACK_ERROR_file_IO: 'UMFPACK_ERROR_file_IO'}
    umfSys = [
     UMFPACK_A, 
     UMFPACK_At, 
     UMFPACK_Aat, 
     UMFPACK_Pt_L, 
     UMFPACK_L, 
     UMFPACK_Lt_P, 
     UMFPACK_Lat_P, 
     UMFPACK_Lt, 
     UMFPACK_U_Qt, 
     UMFPACK_U, 
     UMFPACK_Q_Ut, 
     UMFPACK_Q_Uat, 
     UMFPACK_Ut, 
     UMFPACK_Uat]
    umfSys_transposeMap = [
     {UMFPACK_A: UMFPACK_At, UMFPACK_At: UMFPACK_A, 
        UMFPACK_Aat: UMFPACK_A},
     {UMFPACK_A: UMFPACK_Aat, UMFPACK_Aat: UMFPACK_A}]
umfFamilyTypes = {'di': int, 'dl': int, 'zi': int, 'zl': int}
umfRealTypes = ('di', 'dl')
umfComplexTypes = ('zi', 'zl')

class Struct(object):

    def __init__(self, **kwargs):
        if kwargs:
            self.__dict__.update(kwargs)

    def __str__(self):
        ss = '%s\n' % self.__class__
        for key, val in iteritems(self.__dict__):
            if issubclass(self.__dict__[key].__class__, Struct):
                ss += '  %s:\n    %s\n' % (key, self.__dict__[key].__class__)
            else:
                aux = '\n' + str(val)
                aux = aux.replace('\n', '\n    ')
                ss += '  %s:\n%s\n' % (key, aux[1:])

        return ss.rstrip()


class UmfpackContext(Struct):

    def __init__(self, family='di', **kwargs):
        """
        Arguments:

        family  .. family of UMFPACK functions ('di', 'dl', 'zi', 'zl')

        Keyword arguments:

        maxCond .. if extimated condition number is greater than maxCond,
                   a warning is issued (default: 1e12)"""
        if _um is None:
            raise ImportError('Scipy was built without UMFPACK support. You need to install the UMFPACK library and header files before building scipy.')
        self.maxCond = 1000000000000.0
        Struct.__init__(self, **kwargs)
        if family not in umfFamilyTypes.keys():
            raise TypeError('wrong family: %s' % family)
        self.family = family
        self.control = np.zeros((UMFPACK_CONTROL,), dtype=np.double)
        self.info = np.zeros((UMFPACK_INFO,), dtype=np.double)
        self._symbolic = None
        self._numeric = None
        self.mtx = None
        self.isReal = self.family in umfRealTypes
        pattern = 'umfpack_' + family + '_(.*)'
        fn = updateDictWithVars({}, _um, pattern, group=1)
        self.funs = Struct(**fn)
        self.funs.defaults(self.control)
        self.control[UMFPACK_PRL] = 3
        return

    def __del__(self):
        self.free()

    def strControl(self):
        maxLen = max([ len(name) for name in umfControls ])
        format = '%%-%ds : %%d' % maxLen
        aux = [ format % (name, self.control[umfDefines[name]]) for name in umfControls if name in umfDefines
              ]
        return ('\n').join(aux)

    def strInfo(self):
        maxLen = max([ len(name) for name in umfInfo ])
        format = '%%-%ds : %%d' % maxLen
        aux = [ format % (name, self.info[umfDefines[name]]) for name in umfInfo if name in umfDefines
              ]
        return ('\n').join(aux)

    def _getIndx(self, mtx):
        if sp.isspmatrix_csc(mtx):
            indx = mtx.indices
            self.isCSR = 0
        elif sp.isspmatrix_csr(mtx):
            indx = mtx.indices
            self.isCSR = 1
        else:
            raise TypeError('must be a CSC/CSR matrix (is %s)' % mtx.__class__)
        if self.family[1] == 'i':
            if indx.dtype != np.dtype('i') or mtx.indptr.dtype != np.dtype('i'):
                raise ValueError('matrix must have int indices')
        elif indx.dtype != np.dtype('l') or mtx.indptr.dtype != np.dtype('l'):
            raise ValueError('matrix must have long indices')
        if self.isReal:
            if mtx.data.dtype != np.dtype('f8'):
                raise ValueError('matrix must have float64 values')
        elif mtx.data.dtype != np.dtype('c16'):
            raise ValueError('matrix must have complex128 values')
        return indx

    def symbolic(self, mtx):
        """Symbolic object (symbolic LU decomposition) computation for a given
        sparsity pattern."""
        self.free_symbolic()
        indx = self._getIndx(mtx)
        if not assumeSortedIndices:
            mtx.sort_indices()
        if self.isReal:
            status, self._symbolic = self.funs.symbolic(mtx.shape[0], mtx.shape[1], mtx.indptr, indx, mtx.data, self.control, self.info)
        else:
            real, imag = mtx.data.real.copy(), mtx.data.imag.copy()
            status, self._symbolic = self.funs.symbolic(mtx.shape[0], mtx.shape[1], mtx.indptr, indx, real, imag, self.control, self.info)
        if status != UMFPACK_OK:
            raise RuntimeError('%s failed with %s' % (self.funs.symbolic,
             umfStatus[status]))
        self.mtx = mtx

    def numeric(self, mtx):
        """Numeric object (LU decomposition) computation using the
        symbolic decomposition. The symbolic decomposition is (re)computed
        if necessary."""
        self.free_numeric()
        if self._symbolic is None:
            self.symbolic(mtx)
        indx = self._getIndx(mtx)
        failCount = 0
        while 1:
            if self.isReal:
                status, self._numeric = self.funs.numeric(mtx.indptr, indx, mtx.data, self._symbolic, self.control, self.info)
            else:
                real, imag = mtx.data.real.copy(), mtx.data.imag.copy()
                status, self._numeric = self.funs.numeric(mtx.indptr, indx, real, imag, self._symbolic, self.control, self.info)
            if status != UMFPACK_OK:
                if status == UMFPACK_WARNING_singular_matrix:
                    warnings.warn('Singular matrix', UmfpackWarning)
                    break
                else:
                    if status in (UMFPACK_ERROR_different_pattern,
                     UMFPACK_ERROR_invalid_Symbolic_object):
                        warnings.warn('Recomputing symbolic', UmfpackWarning)
                        self.symbolic(mtx)
                        failCount += 1
                    else:
                        failCount += 100
            else:
                break
            if failCount >= 2:
                raise RuntimeError('%s failed with %s' % (self.funs.numeric,
                 umfStatus[status]))

        return

    def report_symbolic(self):
        """Print information about the symbolic object. Output depends on
        self.control[UMFPACK_PRL]."""
        self.funs.report_symbolic(self._symbolic, self.control)

    def report_numeric(self):
        """Print information about the numeric object. Output depends on
        self.control[UMFPACK_PRL]."""
        self.funs.report_numeric(self._numeric, self.control)

    def report_control(self):
        """Print control values."""
        self.funs.report_control(self.control)

    def report_info(self):
        """Print all status information. Output depends on
        self.control[UMFPACK_PRL]."""
        self.funs.report_info(self.control, self.info)

    def free_symbolic(self):
        if self._symbolic is not None:
            self.funs.free_symbolic(self._symbolic)
            self._symbolic = None
            self.mtx = None
        return

    def free_numeric(self):
        if self._numeric is not None:
            self.funs.free_numeric(self._numeric)
            self._numeric = None
            self.free_symbolic()
        return

    def free(self):
        self.free_symbolic()
        self.free_numeric()

    def solve(self, sys, mtx, rhs, autoTranspose=False):
        """
        Solution of system of linear equation using the Numeric object.

        Arguments:
                sys - one of UMFPACK system description constants, like
                      UMFPACK_A, UMFPACK_At, see umfSys list and UMFPACK
                      docs
                mtx - sparse matrix (CSR or CSC)
                rhs - right hand side vector
                autoTranspose - automatically changes 'sys' to the
                      transposed type, if 'mtx' is in CSR, since UMFPACK
                      assumes CSC internally
        """
        if sys not in umfSys:
            raise ValueError('sys must be in' % umfSys)
        if autoTranspose and self.isCSR:
            if self.family in umfRealTypes:
                ii = 0
            else:
                ii = 1
            if sys in umfSys_transposeMap[ii]:
                sys = umfSys_transposeMap[ii][sys]
            else:
                raise RuntimeError('autoTranspose ambiguous, switch it off')
        if self._numeric is not None:
            if self.mtx is not mtx:
                raise ValueError('must be called with same matrix as numeric()')
        else:
            raise RuntimeError('numeric() not called')
        indx = self._getIndx(mtx)
        if self.isReal:
            rhs = rhs.astype(np.float64)
            sol = np.zeros((mtx.shape[1],), dtype=np.float64)
            status = self.funs.solve(sys, mtx.indptr, indx, mtx.data, sol, rhs, self._numeric, self.control, self.info)
        else:
            rhs = rhs.astype(np.complex128)
            sol = np.zeros((mtx.shape[1],), dtype=np.complex128)
            mreal, mimag = mtx.data.real.copy(), mtx.data.imag.copy()
            sreal, simag = sol.real.copy(), sol.imag.copy()
            rreal, rimag = rhs.real.copy(), rhs.imag.copy()
            status = self.funs.solve(sys, mtx.indptr, indx, mreal, mimag, sreal, simag, rreal, rimag, self._numeric, self.control, self.info)
            sol.real, sol.imag = sreal, simag
        if status != UMFPACK_OK:
            if status == UMFPACK_WARNING_singular_matrix:
                warnings.warn('Zeroing nan and inf entries...', UmfpackWarning)
                sol[~np.isfinite(sol)] = 0.0
            else:
                raise RuntimeError('%s failed with %s' % (self.funs.solve,
                 umfStatus[status]))
        econd = 1.0 / self.info[UMFPACK_RCOND]
        if econd > self.maxCond:
            msg = '(almost) singular matrix! ' + '(estimated cond. number: %.2e)' % econd
            warnings.warn(msg, UmfpackWarning)
        return sol

    def linsolve(self, sys, mtx, rhs, autoTranspose=False):
        """
        One-shot solution of system of linear equation. Reuses Numeric object
        if possible.

        Arguments:
                sys - one of UMFPACK system description constants, like
                      UMFPACK_A, UMFPACK_At, see umfSys list and UMFPACK
                      docs
                mtx - sparse matrix (CSR or CSC)
                rhs - right hand side vector
                autoTranspose - automatically changes 'sys' to the
                      transposed type, if 'mtx' is in CSR, since UMFPACK
                      assumes CSC internally
        """
        if sys not in umfSys:
            raise ValueError('sys must be in' % umfSys)
        if self._numeric is None:
            self.numeric(mtx)
        elif self.mtx is not mtx:
            self.numeric(mtx)
        sol = self.solve(sys, mtx, rhs, autoTranspose)
        self.free_numeric()
        return sol

    def __call__(self, sys, mtx, rhs, autoTranspose=False):
        """
        Uses solve() or linsolve() depending on the presence of the Numeric
        object.

        Arguments:
                sys - one of UMFPACK system description constants, like
                      UMFPACK_A, UMFPACK_At, see umfSys list and UMFPACK
                      docs
                mtx - sparse matrix (CSR or CSC)
                rhs - right hand side vector
                autoTranspose - automatically changes 'sys' to the
                      transposed type, if 'mtx' is in CSR, since UMFPACK
                      assumes CSC internally
        """
        if self._numeric is not None:
            return self.solve(sys, mtx, rhs, autoTranspose)
        else:
            return self.linsolve(sys, mtx, rhs, autoTranspose)
            return

    def lu(self, mtx):
        """
        Returns an LU decomposition of an m-by-n matrix in the form
        (L, U, P, Q, R, do_recip):

            L - Lower triangular m-by-min(m,n) CSR matrix
            U - Upper triangular min(m,n)-by-n CSC matrix
            P - Vector of row permuations
            Q - Vector of column permuations
            R - Vector of diagonal row scalings
            do_recip - boolean

        For a given matrix A, the decomposition satisfies:
                LU = PRAQ        when do_recip is true
                LU = P(R^-1)AQ   when do_recip is false
        """
        mtx = mtx.tocsc()
        self.numeric(mtx)
        status, lnz, unz, n_row, n_col, nz_udiag = self.funs.get_lunz(self._numeric)
        if status != UMFPACK_OK:
            raise RuntimeError('%s failed with %s' % (self.funs.get_lunz,
             umfStatus[status]))
        i_type = mtx.indptr.dtype
        Lp = np.zeros((n_row + 1,), dtype=i_type)
        Lj = np.zeros((lnz,), dtype=i_type)
        Lx = np.zeros((lnz,), dtype=np.double)
        Up = np.zeros((n_col + 1,), dtype=i_type)
        Ui = np.zeros((unz,), dtype=i_type)
        Ux = np.zeros((unz,), dtype=np.double)
        P = np.zeros((n_row,), dtype=i_type)
        Q = np.zeros((n_col,), dtype=i_type)
        Dx = np.zeros((min(n_row, n_col),), dtype=np.double)
        Rs = np.zeros((n_row,), dtype=np.double)
        if self.isReal:
            status, do_recip = self.funs.get_numeric(Lp, Lj, Lx, Up, Ui, Ux, P, Q, Dx, Rs, self._numeric)
            if status != UMFPACK_OK:
                raise RuntimeError('%s failed with %s' % (
                 self.funs.get_numeric, umfStatus[status]))
            L = sp.csr_matrix((Lx, Lj, Lp), (n_row, min(n_row, n_col)))
            U = sp.csc_matrix((Ux, Ui, Up), (min(n_row, n_col), n_col))
            R = Rs
            return (
             L, U, P, Q, R, bool(do_recip))
        else:
            Lz = np.zeros((lnz,), dtype=np.double)
            Uz = np.zeros((unz,), dtype=np.double)
            Dz = np.zeros((min(n_row, n_col),), dtype=np.double)
            status, do_recip = self.funs.get_numeric(Lp, Lj, Lx, Lz, Up, Ui, Ux, Uz, P, Q, Dx, Dz, Rs, self._numeric)
            if status != UMFPACK_OK:
                raise RuntimeError('%s failed with %s' % (
                 self.funs.get_numeric, umfStatus[status]))
            Lxz = np.zeros((lnz,), dtype=np.complex128)
            Uxz = np.zeros((unz,), dtype=np.complex128)
            Dxz = np.zeros((min(n_row, n_col),), dtype=np.complex128)
            Lxz.real, Lxz.imag = Lx, Lz
            Uxz.real, Uxz.imag = Ux, Uz
            Dxz.real, Dxz.imag = Dx, Dz
            L = sp.csr_matrix((Lxz, Lj, Lp), (n_row, min(n_row, n_col)))
            U = sp.csc_matrix((Uxz, Ui, Up), (min(n_row, n_col), n_col))
            R = Rs
            return (
             L, U, P, Q, R, bool(do_recip))