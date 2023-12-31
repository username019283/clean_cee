# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\testing\nosetester.pyc
# Compiled at: 2013-04-07 07:04:04
"""
Nose test running.

This module implements ``test()`` and ``bench()`` functions for NumPy modules.

"""
import os, sys, warnings, numpy.testing.utils

def get_package_name(filepath):
    """
    Given a path where a package is installed, determine its name.

    Parameters
    ----------
    filepath : str
        Path to a file. If the determination fails, "numpy" is returned.

    Examples
    --------
    >>> np.testing.nosetester.get_package_name('nonsense')
    'numpy'

    """
    fullpath = filepath[:]
    pkg_name = []
    while 'site-packages' in filepath or 'dist-packages' in filepath:
        filepath, p2 = os.path.split(filepath)
        if p2 in ('site-packages', 'dist-packages'):
            break
        pkg_name.append(p2)

    if not pkg_name:
        if 'scipy' in fullpath:
            return 'scipy'
        else:
            return 'numpy'

    pkg_name.reverse()
    if pkg_name[0].endswith('.egg'):
        pkg_name.pop(0)
    return ('.').join(pkg_name)


def import_nose():
    """ Import nose only when needed.
    """
    fine_nose = True
    minimum_nose_version = (0, 10, 0)
    try:
        import nose
        from nose.tools import raises
    except ImportError:
        fine_nose = False

    if nose.__versioninfo__ < minimum_nose_version:
        fine_nose = False
    if not fine_nose:
        msg = 'Need nose >= %d.%d.%d for tests - see http://somethingaboutorange.com/mrl/projects/nose' % minimum_nose_version
        raise ImportError(msg)
    return nose


def run_module_suite(file_to_run=None):
    if file_to_run is None:
        f = sys._getframe(1)
        file_to_run = f.f_locals.get('__file__', None)
        if file_to_run is None:
            raise AssertionError
    import_nose().run(argv=['', file_to_run])
    return


class NoseTester(object):
    """
    Nose test runner.

    This class is made available as numpy.testing.Tester, and a test function
    is typically added to a package's __init__.py like so::

      from numpy.testing import Tester
      test = Tester().test

    Calling this test function finds and runs all tests associated with the
    package and all its sub-packages.

    Attributes
    ----------
    package_path : str
        Full path to the package to test.
    package_name : str
        Name of the package to test.

    Parameters
    ----------
    package : module, str or None, optional
        The package to test. If a string, this should be the full path to
        the package. If None (default), `package` is set to the module from
        which `NoseTester` is initialized.
    raise_warnings : str or sequence of warnings, optional
        This specifies which warnings to configure as 'raise' instead
        of 'warn' during the test execution.  Valid strings are:

          - "develop" : equals ``(DeprecationWarning, RuntimeWarning)``
          - "release" : equals ``()``, don't raise on any warnings.

        See Notes for more details.

    Notes
    -----
    The default for `raise_warnings` is
    ``(DeprecationWarning, RuntimeWarning)`` for the master branch of NumPy,
    and ``()`` for maintenance branches and released versions.  The purpose
    of this switching behavior is to catch as many warnings as possible
    during development, but not give problems for packaging of released
    versions.

    """
    excludes = [
     'f2py_ext', 
     'f2py_f90_ext', 
     'gen_ext', 
     'pyrex_ext', 
     'swig_ext']

    def __init__(self, package=None, raise_warnings='release'):
        package_name = None
        if package is None:
            f = sys._getframe(1)
            package_path = f.f_locals.get('__file__', None)
            assert not package_path is None
            package_path = os.path.dirname(package_path)
            package_name = f.f_locals.get('__name__', None)
        elif isinstance(package, type(os)):
            package_path = os.path.dirname(package.__file__)
            package_name = getattr(package, '__name__', None)
        else:
            package_path = str(package)
        self.package_path = package_path
        if package_name is None:
            package_name = get_package_name(package_path)
        self.package_name = package_name
        self.raise_warnings = raise_warnings
        return

    def _test_argv(self, label, verbose, extra_argv):
        """ Generate argv for nosetest command

        Parameters
        ----------
        label : {'fast', 'full', '', attribute identifier}, optional
            see ``test`` docstring
        verbose : int, optional
            Verbosity value for test outputs, in the range 1-10. Default is 1.
        extra_argv : list, optional
            List with any extra arguments to pass to nosetests.

        Returns
        -------
        argv : list
            command line arguments that will be passed to nose
        """
        argv = [
         __file__, self.package_path, '-s']
        if label and label != 'full':
            if not isinstance(label, basestring):
                raise TypeError('Selection label should be a string')
            if label == 'fast':
                label = 'not slow'
            argv += ['-A', label]
        argv += ['--verbosity', str(verbose)]
        if extra_argv:
            argv += extra_argv
        return argv

    def _show_system_info(self):
        nose = import_nose()
        import numpy
        print 'NumPy version %s' % numpy.__version__
        npdir = os.path.dirname(numpy.__file__)
        print 'NumPy is installed in %s' % npdir
        if 'scipy' in self.package_name:
            import scipy
            print 'SciPy version %s' % scipy.__version__
            spdir = os.path.dirname(scipy.__file__)
            print 'SciPy is installed in %s' % spdir
        pyversion = sys.version.replace('\n', '')
        print 'Python version %s' % pyversion
        print 'nose version %d.%d.%d' % nose.__versioninfo__

    def _get_custom_doctester(self):
        """ Return instantiated plugin for doctests

        Allows subclassing of this class to override doctester

        A return value of None means use the nose builtin doctest plugin
        """
        from noseclasses import NumpyDoctest
        return NumpyDoctest()

    def prepare_test_args(self, label='fast', verbose=1, extra_argv=None, doctests=False, coverage=False):
        """
        Run tests for module using nose.

        This method does the heavy lifting for the `test` method. It takes all
        the same arguments, for details see `test`.

        See Also
        --------
        test

        """
        import_nose()
        argv = self._test_argv(label, verbose, extra_argv)
        for ename in self.excludes:
            argv += ['--exclude', ename]

        if coverage:
            argv += ['--cover-package=%s' % self.package_name, '--with-coverage',
             '--cover-tests', '--cover-erase']
        import nose.plugins.builtin
        from noseclasses import KnownFailure, Unplugger
        plugins = [KnownFailure()]
        plugins += [ p() for p in nose.plugins.builtin.plugins ]
        doctest_argv = '--with-doctest' in argv
        if doctests == False and doctest_argv:
            doctests = True
        plug = self._get_custom_doctester()
        if plug is None:
            if doctests and not doctest_argv:
                argv += ['--with-doctest']
        else:
            if doctest_argv:
                argv.remove('--with-doctest')
            plugins += [Unplugger('doctest'), plug]
            if doctests:
                argv += ['--with-' + plug.name]
        return (
         argv, plugins)

    def test(self, label='fast', verbose=1, extra_argv=None, doctests=False, coverage=False, raise_warnings=None):
        """
        Run tests for module using nose.

        Parameters
        ----------
        label : {'fast', 'full', '', attribute identifier}, optional
            Identifies the tests to run. This can be a string to pass to
            the nosetests executable with the '-A' option, or one of several
            special values.  Special values are:
            * 'fast' - the default - which corresponds to the ``nosetests -A``
              option of 'not slow'.
            * 'full' - fast (as above) and slow tests as in the
              'no -A' option to nosetests - this is the same as ''.
            * None or '' - run all tests.
            attribute_identifier - string passed directly to nosetests as '-A'.
        verbose : int, optional
            Verbosity value for test outputs, in the range 1-10. Default is 1.
        extra_argv : list, optional
            List with any extra arguments to pass to nosetests.
        doctests : bool, optional
            If True, run doctests in module. Default is False.
        coverage : bool, optional
            If True, report coverage of NumPy code. Default is False.
            (This requires the `coverage module:
             <http://nedbatchelder.com/code/modules/coverage.html>`_).
        raise_warnings : str or sequence of warnings, optional
            This specifies which warnings to configure as 'raise' instead
            of 'warn' during the test execution.  Valid strings are:

              - "develop" : equals ``(DeprecationWarning, RuntimeWarning)``
              - "release" : equals ``()``, don't raise on any warnings.

        Returns
        -------
        result : object
            Returns the result of running the tests as a
            ``nose.result.TextTestResult`` object.

        Notes
        -----
        Each NumPy module exposes `test` in its namespace to run all tests for it.
        For example, to run all tests for numpy.lib:

        >>> np.lib.test() #doctest: +SKIP

        Examples
        --------
        >>> result = np.lib.test() #doctest: +SKIP
        Running unit tests for numpy.lib
        ...
        Ran 976 tests in 3.933s

        OK

        >>> result.errors #doctest: +SKIP
        []
        >>> result.knownfail #doctest: +SKIP
        []
        """
        verbose = min(verbose, 3)
        import utils
        utils.verbose = verbose
        if doctests:
            print 'Running unit tests and doctests for %s' % self.package_name
        else:
            print 'Running unit tests for %s' % self.package_name
        self._show_system_info()
        import doctest
        doctest.master = None
        if raise_warnings is None:
            raise_warnings = self.raise_warnings
        _warn_opts = dict(develop=(DeprecationWarning, RuntimeWarning), release=())
        if raise_warnings in _warn_opts.keys():
            raise_warnings = _warn_opts[raise_warnings]
        warn_ctx = numpy.testing.utils.WarningManager()
        warn_ctx.__enter__()
        warnings.resetwarnings()
        warnings.filterwarnings('always', category=DeprecationWarning)
        for warningtype in raise_warnings:
            warnings.filterwarnings('error', category=warningtype)

        warnings.filterwarnings('ignore', message='Not importing directory')
        warnings.filterwarnings('ignore', message='numpy.dtype size changed')
        warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
        try:
            from noseclasses import NumpyTestProgram
            argv, plugins = self.prepare_test_args(label, verbose, extra_argv, doctests, coverage)
            t = NumpyTestProgram(argv=argv, exit=False, plugins=plugins)
        finally:
            warn_ctx.__exit__()

        return t.result

    def bench(self, label='fast', verbose=1, extra_argv=None):
        """
        Run benchmarks for module using nose.

        Parameters
        ----------
        label : {'fast', 'full', '', attribute identifier}, optional
            Identifies the benchmarks to run. This can be a string to pass to
            the nosetests executable with the '-A' option, or one of several
            special values.  Special values are:
            * 'fast' - the default - which corresponds to the ``nosetests -A``
              option of 'not slow'.
            * 'full' - fast (as above) and slow benchmarks as in the
              'no -A' option to nosetests - this is the same as ''.
            * None or '' - run all tests.
            attribute_identifier - string passed directly to nosetests as '-A'.
        verbose : int, optional
            Verbosity value for benchmark outputs, in the range 1-10. Default is 1.
        extra_argv : list, optional
            List with any extra arguments to pass to nosetests.

        Returns
        -------
        success : bool
            Returns True if running the benchmarks works, False if an error
            occurred.

        Notes
        -----
        Benchmarks are like tests, but have names starting with "bench" instead
        of "test", and can be found under the "benchmarks" sub-directory of the
        module.

        Each NumPy module exposes `bench` in its namespace to run all benchmarks
        for it.

        Examples
        --------
        >>> success = np.lib.bench() #doctest: +SKIP
        Running benchmarks for numpy.lib
        ...
        using 562341 items:
        unique:
        0.11
        unique1d:
        0.11
        ratio: 1.0
        nUnique: 56230 == 56230
        ...
        OK

        >>> success #doctest: +SKIP
        True

        """
        print 'Running benchmarks for %s' % self.package_name
        self._show_system_info()
        argv = self._test_argv(label, verbose, extra_argv)
        argv += ['--match', '(?:^|[\\\\b_\\\\.%s-])[Bb]ench' % os.sep]
        nose = import_nose()
        from noseclasses import Unplugger
        add_plugins = [
         Unplugger('doctest')]
        return nose.run(argv=argv, addplugins=add_plugins)