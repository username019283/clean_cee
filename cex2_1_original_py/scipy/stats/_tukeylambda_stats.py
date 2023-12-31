# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\stats\_tukeylambda_stats.pyc
# Compiled at: 2013-02-16 13:27:32
from __future__ import division, print_function, absolute_import
import numpy as np
from numpy import array, poly1d
from scipy.interpolate import interp1d
from scipy.special import beta
_tukeylambda_var_pc = [
 3.289868133696453, 0.7306125098871127, 
 -0.5370742306855439, 0.17292046290190008, 
 -0.02371146284628187]
_tukeylambda_var_qc = [1.0, 3.683605511659861, 4.184152498888124, 
 1.7660926747377275, 0.2643989311168465]
_tukeylambda_var_p = poly1d(_tukeylambda_var_pc[::-1])
_tukeylambda_var_q = poly1d(_tukeylambda_var_qc[::-1])

def tukeylambda_variance(lam):
    """Variance of the Tukey Lambda distribution.

    Parameters
    ----------
    lam : array_like
        The lambda values at which to compute the variance.

    Returns
    -------
    v : ndarray
        The variance.  For lam < -0.5, the variance is not defined, so
        np.nan is returned.  For lam = 0.5, np.inf is returned.

    Notes
    -----
    In an interval around lambda=0, this function uses the [4,4] Pade
    approximation to compute the variance.  Otherwise it uses the standard
    formula (http://en.wikipedia.org/wiki/Tukey_lambda_distribution).  The
    Pade approximation is used because the standard formula has a removable
    discontinuity at lambda = 0, and does not produce accurate numerical
    results near lambda = 0.
    """
    lam = np.asarray(lam)
    shp = lam.shape
    lam = np.atleast_1d(lam).astype(np.float64)
    threshold = 0.075
    low_mask = lam < -0.5
    neghalf_mask = lam == -0.5
    small_mask = np.abs(lam) < threshold
    reg_mask = ~(low_mask | neghalf_mask | small_mask)
    small = lam[small_mask]
    reg = lam[reg_mask]
    v = np.empty_like(lam)
    v[low_mask] = np.nan
    v[neghalf_mask] = np.inf
    if small.size > 0:
        v[small_mask] = _tukeylambda_var_p(small) / _tukeylambda_var_q(small)
    if reg.size > 0:
        v[reg_mask] = 2.0 / reg ** 2 * (1.0 / (1.0 + 2 * reg) - beta(reg + 1, reg + 1))
    v.shape = shp
    return v


_tukeylambda_kurt_pc = [
 1.2, -5.853465139719495, -22.653447381131077, 
 0.20601184383406815, 4.59796302262789]
_tukeylambda_kurt_qc = [1.0, 7.171149192233599, 12.96663094361842, 
 0.43075235247853005, -2.789746758009912]
_tukeylambda_kurt_p = poly1d(_tukeylambda_kurt_pc[::-1])
_tukeylambda_kurt_q = poly1d(_tukeylambda_kurt_qc[::-1])

def tukeylambda_kurtosis(lam):
    """Kurtosis of the Tukey Lambda distribution.

    Parameters
    ----------
    lam : array_like
        The lambda values at which to compute the variance.

    Returns
    -------
    v : ndarray
        The variance.  For lam < -0.25, the variance is not defined, so
        np.nan is returned.  For lam = 0.25, np.inf is returned.

    """
    lam = np.asarray(lam)
    shp = lam.shape
    lam = np.atleast_1d(lam).astype(np.float64)
    threshold = 0.055
    low_mask = lam < -0.25
    negqrtr_mask = lam == -0.25
    small_mask = np.abs(lam) < threshold
    reg_mask = ~(low_mask | negqrtr_mask | small_mask)
    small = lam[small_mask]
    reg = lam[reg_mask]
    k = np.empty_like(lam)
    k[low_mask] = np.nan
    k[negqrtr_mask] = np.inf
    if small.size > 0:
        k[small_mask] = _tukeylambda_kurt_p(small) / _tukeylambda_kurt_q(small)
    if reg.size > 0:
        numer = 1.0 / (4 * reg + 1) - 4 * beta(3 * reg + 1, reg + 1) + 3 * beta(2 * reg + 1, 2 * reg + 1)
        denom = 2 * (1.0 / (2 * reg + 1) - beta(reg + 1, reg + 1)) ** 2
        k[reg_mask] = numer / denom - 3
    k.shape = shp
    return k