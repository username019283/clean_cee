# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\interpolate\__init__.pyc
# Compiled at: 2013-02-16 13:27:30
"""
========================================
Interpolation (:mod:`scipy.interpolate`)
========================================

.. currentmodule:: scipy.interpolate

Sub-package for objects used in interpolation.

As listed below, this sub-package contains spline functions and classes,
one-dimensional and multi-dimensional (univariate and multivariate)
interpolation classes, Lagrange and Taylor polynomial interpolators, and
wrappers for `FITPACK <http://www.cisl.ucar.edu/softlib/FITPACK.html>`_
and DFITPACK functions.

Univariate interpolation
========================

.. autosummary::
   :toctree: generated/

   interp1d
   BarycentricInterpolator
   KroghInterpolator
   PiecewisePolynomial
   PchipInterpolator
   barycentric_interpolate
   krogh_interpolate
   piecewise_polynomial_interpolate
   pchip_interpolate

Multivariate interpolation
==========================

Unstructured data:

.. autosummary::
   :toctree: generated/

   griddata
   LinearNDInterpolator
   NearestNDInterpolator
   CloughTocher2DInterpolator
   Rbf
   interp2d

For data on a grid:

.. autosummary::

   RectBivariateSpline

.. seealso:: `scipy.ndimage.map_coordinates`

1-D Splines
===========

.. autosummary::
   :toctree: generated/

   UnivariateSpline
   InterpolatedUnivariateSpline
   LSQUnivariateSpline

The above univariate spline classes have the following methods:

.. autosummary::

   UnivariateSpline.__call__
   UnivariateSpline.derivatives
   UnivariateSpline.integral
   UnivariateSpline.roots
   UnivariateSpline.get_coeffs
   UnivariateSpline.get_knots
   UnivariateSpline.get_residual
   UnivariateSpline.set_smoothing_factor

Low-level interface to FITPACK functions:

.. autosummary::
   :toctree: generated/

   splrep
   splprep
   splev
   splint
   sproot
   spalde
   bisplrep
   bisplev

2-D Splines
===========

For data on a grid:

.. autosummary::
   :toctree: generated/

   RectBivariateSpline
   RectSphereBivariateSpline

For unstructured data:

.. autosummary::
   :toctree: generated/

   BivariateSpline
   SmoothBivariateSpline
   LSQBivariateSpline

Low-level interface to FITPACK functions:

.. autosummary::
   :toctree: generated/

   bisplrep
   bisplev

Additional tools
================

.. autosummary::
   :toctree: generated/

   lagrange
   approximate_taylor_polynomial

.. seealso::

   `scipy.ndimage.map_coordinates`,
   `scipy.ndimage.spline_filter`,
   `scipy.signal.resample`,
   `scipy.signal.bspline`,
   `scipy.signal.gauss_spline`,
   `scipy.signal.qspline1d`,
   `scipy.signal.cspline1d`,
   `scipy.signal.qspline1d_eval`,
   `scipy.signal.cspline1d_eval`,
   `scipy.signal.qspline2d`,
   `scipy.signal.cspline2d`.

"""
from __future__ import division, print_function, absolute_import
from ...interpolate import *
from ...fitpack import *
from ...fitpack2 import *
from .rbf import Rbf
from ...polyint import *
from ...ndgriddata import *
__all__ = [ s for s in dir() if not s.startswith('_') ]
from numpy.testing import Tester
test = Tester().test