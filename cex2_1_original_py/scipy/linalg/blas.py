# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\linalg\blas.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Low-level BLAS functions
========================

This module contains low-level functions from the BLAS library.

.. versionadded:: 0.12.0

.. warning::

   These functions do little to no error checking.
   It is possible to cause crashes by mis-using them,
   so prefer using the higher-level routines in `scipy.linalg`.

Finding functions
=================

.. autosummary::

   get_blas_funcs
   find_best_blas_type

All functions
=============

.. autosummary::
   :toctree: generated/

   caxpy
   ccopy
   cdotc
   cdotu
   cgemm
   cgemv
   cgerc
   cgeru
   chemv
   crotg
   cscal
   csrot
   csscal
   cswap
   ctrmv
   dasum
   daxpy
   dcopy
   ddot
   dgemm
   dgemv
   dger
   dnrm2
   drot
   drotg
   drotm
   drotmg
   dscal
   dswap
   dsymv
   dtrmv
   dzasum
   dznrm2
   icamax
   idamax
   isamax
   izamax
   sasum
   saxpy
   scasum
   scnrm2
   scopy
   sdot
   sgemm
   sgemv
   sger
   snrm2
   srot
   srotg
   srotm
   srotmg
   sscal
   sswap
   ssymv
   strmv
   zaxpy
   zcopy
   zdotc
   zdotu
   zdrot
   zdscal
   zgemm
   zgemv
   zgerc
   zgeru
   zhemv
   zrotg
   zscal
   zswap
   ztrmv

"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'get_blas_funcs', 'find_best_blas_type']
import numpy as _np
from scipy.linalg import _fblas
try:
    from scipy.linalg import _cblas
except ImportError:
    _cblas = None

empty_module = None
from .scipy.linalg._fblas import *
del empty_module
from scipy.lib._util import DeprecatedImport as _DeprecatedImport
cblas = _DeprecatedImport('scipy.linalg.blas.cblas', 'scipy.linalg.blas')
fblas = _DeprecatedImport('scipy.linalg.blas.fblas', 'scipy.linalg.blas')
_type_conv = {'f': 's', 'd': 'd', 'F': 'c', 'D': 'z', 'G': 'z'}
_blas_alias = {'cnrm2': 'scnrm2', 'znrm2': 'dznrm2', 'cdot': 'cdotc', 
   'zdot': 'zdotc', 'cger': 'cgerc', 
   'zger': 'zgerc', 'sdotc': 'sdot', 
   'sdotu': 'sdot', 'ddotc': 'ddot', 
   'ddotu': 'ddot'}

def find_best_blas_type(arrays=(), dtype=None):
    """Find best-matching BLAS/LAPACK type.

    Arrays are used to determine the optimal prefix of BLAS routines.

    Parameters
    ----------
    arrays : sequency of ndarrays, optional
        Arrays can be given to determine optiomal prefix of BLAS
        routines. If not given, double-precision routines will be
        used, otherwise the most generic type in arrays will be used.
    dtype : str or dtype, optional
        Data-type specifier. Not used if `arrays` is non-empty.

    Returns
    -------
    prefix : str
        BLAS/LAPACK prefix character.
    dtype : dtype
        Inferred Numpy data type.
    prefer_fortran : bool
        Whether to prefer Fortran order routines over C order.

    """
    dtype = _np.dtype(dtype)
    prefer_fortran = False
    if arrays:
        dtypes = [ ar.dtype for ar in arrays ]
        dtype = _np.find_common_type(dtypes, ())
        try:
            index = dtypes.index(dtype)
        except ValueError:
            index = 0

        if arrays[index].flags['FORTRAN']:
            prefer_fortran = True
    prefix = _type_conv.get(dtype.char, 'd')
    return (
     prefix, dtype, prefer_fortran)


def _get_funcs(names, arrays, dtype, lib_name, fmodule, cmodule, fmodule_name, cmodule_name, alias):
    """
    Return available BLAS/LAPACK functions.

    Used also in lapack.py. See get_blas_funcs for docstring.
    """
    funcs = []
    unpack = False
    dtype = _np.dtype(dtype)
    module1 = (cmodule, cmodule_name)
    module2 = (fmodule, fmodule_name)
    if isinstance(names, str):
        names = (
         names,)
        unpack = True
    prefix, dtype, prefer_fortran = find_best_blas_type(arrays, dtype)
    if prefer_fortran:
        module1, module2 = module2, module1
    for i, name in enumerate(names):
        func_name = prefix + name
        func_name = alias.get(func_name, func_name)
        func = getattr(module1[0], func_name, None)
        module_name = module1[1]
        if func is None:
            func = getattr(module2[0], func_name, None)
            module_name = module2[1]
        if func is None:
            raise ValueError('%s function %s could not be found' % (lib_name, func_name))
        func.module_name, func.typecode = module_name, prefix
        func.dtype = dtype
        func.prefix = prefix
        funcs.append(func)

    if unpack:
        return funcs[0]
    else:
        return funcs
        return


def get_blas_funcs(names, arrays=(), dtype=None):
    """Return available BLAS function objects from names.

    Arrays are used to determine the optimal prefix of BLAS routines.

    Parameters
    ----------
    names : str or sequence of str
        Name(s) of BLAS functions withouth type prefix.

    arrays : sequency of ndarrays, optional
        Arrays can be given to determine optiomal prefix of BLAS
        routines. If not given, double-precision routines will be
        used, otherwise the most generic type in arrays will be used.

    dtype : str or dtype, optional
        Data-type specifier. Not used if `arrays` is non-empty.

    Returns
    -------
    funcs : list
        List containing the found function(s).

    Notes
    -----
    This routines automatically chooses between Fortran/C
    interfaces. Fortran code is used whenever possible for arrays with
    column major order. In all other cases, C code is preferred.

    In BLAS, the naming convention is that all functions start with a
    type prefix, which depends on the type of the principal
    matrix. These can be one of {'s', 'd', 'c', 'z'} for the numpy
    types {float32, float64, complex64, complex128} respectively.
    The code and the dtype are stored in attributes `typecode` and `dtype`
    of the returned functions.
    """
    return _get_funcs(names, arrays, dtype, 'BLAS', _fblas, _cblas, 'fblas', 'cblas', _blas_alias)