# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\__init__.pyc
# Compiled at: 2013-04-07 07:04:04
"""
NumPy
=====

Provides
  1. An array object of arbitrary homogeneous items
  2. Fast mathematical operations over arrays
  3. Linear Algebra, Fourier Transforms, Random Number Generation

How to use the documentation
----------------------------
Documentation is available in two forms: docstrings provided
with the code, and a loose standing reference guide, available from
`the NumPy homepage <http://www.scipy.org>`_.

We recommend exploring the docstrings using
`IPython <http://ipython.scipy.org>`_, an advanced Python shell with
TAB-completion and introspection capabilities.  See below for further
instructions.

The docstring examples assume that `numpy` has been imported as `np`::

  >>> import numpy as np

Code snippets are indicated by three greater-than signs::

  >>> x = 42
  >>> x = x + 1

Use the built-in ``help`` function to view a function's docstring::

  >>> help(np.sort)
  ... # doctest: +SKIP

For some objects, ``np.info(obj)`` may provide additional help.  This is
particularly true if you see the line "Help on ufunc object:" at the top
of the help() page.  Ufuncs are implemented in C, not Python, for speed.
The native Python help() does not know how to view their help, but our
np.info() function does.

To search for documents containing a keyword, do::

  >>> np.lookfor('keyword')
  ... # doctest: +SKIP

General-purpose documents like a glossary and help on the basic concepts
of numpy are available under the ``doc`` sub-module::

  >>> from numpy import doc
  >>> help(doc)
  ... # doctest: +SKIP

Available subpackages
---------------------
doc
    Topical documentation on broadcasting, indexing, etc.
lib
    Basic functions used by several sub-packages.
random
    Core Random Tools
linalg
    Core Linear Algebra Tools
fft
    Core FFT routines
polynomial
    Polynomial tools
testing
    Numpy testing tools
f2py
    Fortran to Python Interface Generator.
distutils
    Enhancements to distutils with support for
    Fortran compilers support and more.

Utilities
---------
test
    Run numpy unittests
show_config
    Show numpy build configuration
dual
    Overwrite certain functions with high-performance Scipy tools
matlib
    Make everything matrices.
__version__
    Numpy version string

Viewing documentation using IPython
-----------------------------------
Start IPython with the NumPy profile (``ipython -p numpy``), which will
import `numpy` under the alias `np`.  Then, use the ``cpaste`` command to
paste examples into the shell.  To see which functions are available in
`numpy`, type ``np.<TAB>`` (where ``<TAB>`` refers to the TAB key), or use
``np.*cos*?<ENTER>`` (where ``<ENTER>`` refers to the ENTER key) to narrow
down the list.  To view the docstring for a function, use
``np.cos?<ENTER>`` (to view the docstring) and ``np.cos??<ENTER>`` (to view
the source code).

Copies vs. in-place operation
-----------------------------
Most of the functions in `numpy` return a copy of the array argument
(e.g., `np.sort`).  In-place versions of these functions are often
available as array methods, i.e. ``x = np.array([1,2,3]); x.sort()``.
Exceptions to this rule are documented.

"""
try:
    __NUMPY_SETUP__
except NameError:
    __NUMPY_SETUP__ = False

if __NUMPY_SETUP__:
    import sys as _sys
    _sys.stderr.write('Running from numpy source directory.\n')
    del _sys
else:
    try:
        from numpy.__config__ import show as show_config
    except ImportError:
        msg = 'Error importing numpy: you should not try to import numpy from\n        its source directory; please exit the numpy source tree, and relaunch\n        your python intepreter from there.'
        raise ImportError(msg)

    from version import git_revision as __git_revision__
    from version import version as __version__
    from _import_tools import PackageLoader

    def pkgload(*packages, **options):
        loader = PackageLoader(infunc=True)
        return loader(*packages, **options)


    import add_newdocs
    __all__ = [
     'add_newdocs']
    pkgload.__doc__ = PackageLoader.__call__.__doc__
    from testing import Tester
    test = Tester().test
    bench = Tester().bench
    import core
    from .core import *
    import compat, lib
    from .lib import *
    import linalg, fft, polynomial, random, ctypeslib, ma, matrixlib as _mat
    from .matrixlib import *
    from __builtin__ import bool, int, long, float, complex, object, unicode, str
    from core import round, abs, max, min
    __all__.extend(['__version__', 'pkgload', 'PackageLoader',
     'show_config'])
    __all__.extend(core.__all__)
    __all__.extend(_mat.__all__)
    __all__.extend(lib.__all__)
    __all__.extend(['linalg', 'fft', 'random', 'ctypeslib', 'ma'])
    import warnings
    warnings.filterwarnings('ignore', message='numpy.dtype size changed')
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')