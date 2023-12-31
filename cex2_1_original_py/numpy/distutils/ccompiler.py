# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\ccompiler.pyc
# Compiled at: 2013-04-07 07:04:04
import re, os, sys, types
from copy import copy
from distutils.ccompiler import *
from distutils import ccompiler
from distutils.errors import DistutilsExecError, DistutilsModuleError, DistutilsPlatformError
from distutils.sysconfig import customize_compiler
from distutils.version import LooseVersion
from numpy.distutils import log
from numpy.distutils.exec_command import exec_command
from numpy.distutils.misc_util import cyg2win32, is_sequence, mingw32, quote_args, msvc_on_amd64
from numpy.distutils.compat import get_exception

def replace_method(klass, method_name, func):
    if sys.version_info[0] < 3:
        m = types.MethodType(func, None, klass)
    else:
        m = lambda self, *args, **kw: func(self, *args, **kw)
    setattr(klass, method_name, m)
    return


def CCompiler_spawn(self, cmd, display=None):
    """
    Execute a command in a sub-process.

    Parameters
    ----------
    cmd : str
        The command to execute.
    display : str or sequence of str, optional
        The text to add to the log file kept by `numpy.distutils`.
        If not given, `display` is equal to `cmd`.

    Returns
    -------
    None

    Raises
    ------
    DistutilsExecError
        If the command failed, i.e. the exit status was not 0.

    """
    if display is None:
        display = cmd
        if is_sequence(display):
            display = (' ').join(list(display))
    log.info(display)
    s, o = exec_command(cmd)
    if s:
        if is_sequence(cmd):
            cmd = (' ').join(list(cmd))
        try:
            print o
        except UnicodeError:
            pass

        if re.search('Too many open files', o):
            msg = '\nTry rerunning setup command until build succeeds.'
        else:
            msg = ''
        raise DistutilsExecError('Command "%s" failed with exit status %d%s' % (cmd, s, msg))
    return


replace_method(CCompiler, 'spawn', CCompiler_spawn)

def CCompiler_object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
    """
    Return the name of the object files for the given source files.

    Parameters
    ----------
    source_filenames : list of str
        The list of paths to source files. Paths can be either relative or
        absolute, this is handled transparently.
    strip_dir : bool, optional
        Whether to strip the directory from the returned paths. If True,
        the file name prepended by `output_dir` is returned. Default is False.
    output_dir : str, optional
        If given, this path is prepended to the returned paths to the
        object files.

    Returns
    -------
    obj_names : list of str
        The list of paths to the object files corresponding to the source
        files in `source_filenames`.

    """
    if output_dir is None:
        output_dir = ''
    obj_names = []
    for src_name in source_filenames:
        base, ext = os.path.splitext(os.path.normpath(src_name))
        base = os.path.splitdrive(base)[1]
        base = base[os.path.isabs(base):]
        if base.startswith('..'):
            i = base.rfind('..') + 2
            d = base[:i]
            d = os.path.basename(os.path.abspath(d))
            base = d + base[i:]
        if ext not in self.src_extensions:
            raise UnknownFileError("unknown file type '%s' (from '%s')" % (ext, src_name))
        if strip_dir:
            base = os.path.basename(base)
        obj_name = os.path.join(output_dir, base + self.obj_extension)
        obj_names.append(obj_name)

    return obj_names


replace_method(CCompiler, 'object_filenames', CCompiler_object_filenames)

def CCompiler_compile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
    """
    Compile one or more source files.

    Please refer to the Python distutils API reference for more details.

    Parameters
    ----------
    sources : list of str
        A list of filenames
    output_dir : str, optional
        Path to the output directory.
    macros : list of tuples
        A list of macro definitions.
    include_dirs : list of str, optional
        The directories to add to the default include file search path for
        this compilation only.
    debug : bool, optional
        Whether or not to output debug symbols in or alongside the object
        file(s).
    extra_preargs, extra_postargs : ?
        Extra pre- and post-arguments.
    depends : list of str, optional
        A list of file names that all targets depend on.

    Returns
    -------
    objects : list of str
        A list of object file names, one per source file `sources`.

    Raises
    ------
    CompileError
        If compilation fails.

    """
    if not sources:
        return []
    else:
        if sys.version_info[0] < 3:
            from fcompiler import FCompiler
        else:
            from numpy.distutils.fcompiler import FCompiler
        if isinstance(self, FCompiler):
            display = []
            for fc in ['f77', 'f90', 'fix']:
                fcomp = getattr(self, 'compiler_' + fc)
                if fcomp is None:
                    continue
                display.append('Fortran %s compiler: %s' % (fc, (' ').join(fcomp)))

            display = ('\n').join(display)
        else:
            ccomp = self.compiler_so
            display = 'C compiler: %s\n' % ((' ').join(ccomp),)
        log.info(display)
        macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
        display = "compile options: '%s'" % (' ').join(cc_args)
        if extra_postargs:
            display += "\nextra options: '%s'" % (' ').join(extra_postargs)
        log.info(display)
        if isinstance(self, FCompiler):
            objects_to_build = build.keys()
            for obj in objects:
                if obj in objects_to_build:
                    src, ext = build[obj]
                    if self.compiler_type == 'absoft':
                        obj = cyg2win32(obj)
                        src = cyg2win32(src)
                    self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        else:
            for obj, (src, ext) in build.items():
                self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        return objects


replace_method(CCompiler, 'compile', CCompiler_compile)

def CCompiler_customize_cmd(self, cmd, ignore=()):
    """
    Customize compiler using distutils command.

    Parameters
    ----------
    cmd : class instance
        An instance inheriting from `distutils.cmd.Command`.
    ignore : sequence of str, optional
        List of `CCompiler` commands (without ``'set_'``) that should not be
        altered. Strings that are checked for are:
        ``('include_dirs', 'define', 'undef', 'libraries', 'library_dirs',
        'rpath', 'link_objects')``.

    Returns
    -------
    None

    """
    log.info('customize %s using %s' % (self.__class__.__name__,
     cmd.__class__.__name__))

    def allow(attr):
        return getattr(cmd, attr, None) is not None and attr not in ignore

    if allow('include_dirs'):
        self.set_include_dirs(cmd.include_dirs)
    if allow('define'):
        for name, value in cmd.define:
            self.define_macro(name, value)

    if allow('undef'):
        for macro in cmd.undef:
            self.undefine_macro(macro)

    if allow('libraries'):
        self.set_libraries(self.libraries + cmd.libraries)
    if allow('library_dirs'):
        self.set_library_dirs(self.library_dirs + cmd.library_dirs)
    if allow('rpath'):
        self.set_runtime_library_dirs(cmd.rpath)
    if allow('link_objects'):
        self.set_link_objects(cmd.link_objects)


replace_method(CCompiler, 'customize_cmd', CCompiler_customize_cmd)

def _compiler_to_string(compiler):
    props = []
    mx = 0
    keys = compiler.executables.keys()
    for key in ['version', 'libraries', 'library_dirs', 
     'object_switch', 'compile_switch', 
     'include_dirs', 
     'define', 'undef', 'rpath', 'link_objects']:
        if key not in keys:
            keys.append(key)

    for key in keys:
        if hasattr(compiler, key):
            v = getattr(compiler, key)
            mx = max(mx, len(key))
            props.append((key, repr(v)))

    lines = []
    format = '%-' + repr(mx + 1) + 's = %s'
    for prop in props:
        lines.append(format % prop)

    return ('\n').join(lines)


def CCompiler_show_customization(self):
    """
    Print the compiler customizations to stdout.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Notes
    -----
    Printing is only done if the distutils log threshold is < 2.

    """
    try:
        self.get_version()
    except:
        pass

    if log._global_log.threshold < 2:
        print '*' * 80
        print self.__class__
        print _compiler_to_string(self)
        print '*' * 80


replace_method(CCompiler, 'show_customization', CCompiler_show_customization)

def CCompiler_customize(self, dist, need_cxx=0):
    """
    Do any platform-specific customization of a compiler instance.

    This method calls `distutils.sysconfig.customize_compiler` for
    platform-specific customization, as well as optionally remove a flag
    to suppress spurious warnings in case C++ code is being compiled.

    Parameters
    ----------
    dist : object
        This parameter is not used for anything.
    need_cxx : bool, optional
        Whether or not C++ has to be compiled. If so (True), the
        ``"-Wstrict-prototypes"`` option is removed to prevent spurious
        warnings. Default is False.

    Returns
    -------
    None

    Notes
    -----
    All the default options used by distutils can be extracted with::

      from distutils import sysconfig
      sysconfig.get_config_vars('CC', 'CXX', 'OPT', 'BASECFLAGS',
                                'CCSHARED', 'LDSHARED', 'SO')

    """
    log.info('customize %s' % self.__class__.__name__)
    customize_compiler(self)
    if need_cxx:
        try:
            self.compiler_so.remove('-Wstrict-prototypes')
        except (AttributeError, ValueError):
            pass

        if hasattr(self, 'compiler') and 'cc' in self.compiler[0]:
            if not self.compiler_cxx:
                if self.compiler[0].startswith('gcc'):
                    a, b = ('gcc', 'g++')
                else:
                    a, b = ('cc', 'c++')
                self.compiler_cxx = [
                 self.compiler[0].replace(a, b)] + self.compiler[1:]
        else:
            if hasattr(self, 'compiler'):
                log.warn('#### %s #######' % (self.compiler,))
            log.warn('Missing compiler_cxx fix for ' + self.__class__.__name__)


replace_method(CCompiler, 'customize', CCompiler_customize)

def simple_version_match(pat='[-.\\d]+', ignore='', start=''):
    r"""
    Simple matching of version numbers, for use in CCompiler and FCompiler.

    Parameters
    ----------
    pat : str, optional
        A regular expression matching version numbers.
        Default is ``r'[-.\d]+'``.
    ignore : str, optional
        A regular expression matching patterns to skip.
        Default is ``''``, in which case nothing is skipped.
    start : str, optional
        A regular expression matching the start of where to start looking
        for version numbers.
        Default is ``''``, in which case searching is started at the
        beginning of the version string given to `matcher`.

    Returns
    -------
    matcher : callable
        A function that is appropriate to use as the ``.version_match``
        attribute of a `CCompiler` class. `matcher` takes a single parameter,
        a version string.

    """

    def matcher(self, version_string):
        version_string = version_string.replace('\n', ' ')
        pos = 0
        if start:
            m = re.match(start, version_string)
            if not m:
                return None
            pos = m.end()
        while 1:
            m = re.search(pat, version_string[pos:])
            if not m:
                return None
            if ignore and re.match(ignore, m.group(0)):
                pos = m.end()
                continue
            break

        return m.group(0)

    return matcher


def CCompiler_get_version(self, force=False, ok_status=[0]):
    """
    Return compiler version, or None if compiler is not available.

    Parameters
    ----------
    force : bool, optional
        If True, force a new determination of the version, even if the
        compiler already has a version attribute. Default is False.
    ok_status : list of int, optional
        The list of status values returned by the version look-up process
        for which a version string is returned. If the status value is not
        in `ok_status`, None is returned. Default is ``[0]``.

    Returns
    -------
    version : str or None
        Version string, in the format of `distutils.version.LooseVersion`.

    """
    if not force and hasattr(self, 'version'):
        return self.version
    else:
        self.find_executables()
        try:
            version_cmd = self.version_cmd
        except AttributeError:
            return

        if not version_cmd or not version_cmd[0]:
            return
        try:
            matcher = self.version_match
        except AttributeError:
            try:
                pat = self.version_pattern
            except AttributeError:
                return

            def matcher(version_string):
                m = re.match(pat, version_string)
                if not m:
                    return None
                else:
                    version = m.group('version')
                    return version

        status, output = exec_command(version_cmd, use_tee=0)
        version = None
        if status in ok_status:
            version = matcher(output)
            if version:
                version = LooseVersion(version)
        self.version = version
        return version


replace_method(CCompiler, 'get_version', CCompiler_get_version)

def CCompiler_cxx_compiler(self):
    """
    Return the C++ compiler.

    Parameters
    ----------
    None

    Returns
    -------
    cxx : class instance
        The C++ compiler, as a `CCompiler` instance.

    """
    if self.compiler_type == 'msvc':
        return self
    cxx = copy(self)
    cxx.compiler_so = [cxx.compiler_cxx[0]] + cxx.compiler_so[1:]
    if sys.platform.startswith('aix') and 'ld_so_aix' in cxx.linker_so[0]:
        cxx.linker_so = [cxx.linker_so[0], cxx.compiler_cxx[0]] + cxx.linker_so[2:]
    else:
        cxx.linker_so = [
         cxx.compiler_cxx[0]] + cxx.linker_so[1:]
    return cxx


replace_method(CCompiler, 'cxx_compiler', CCompiler_cxx_compiler)
compiler_class['intel'] = ('intelccompiler', 'IntelCCompiler', 'Intel C Compiler for 32-bit applications')
compiler_class['intele'] = ('intelccompiler', 'IntelItaniumCCompiler', 'Intel C Itanium Compiler for Itanium-based applications')
compiler_class['intelem'] = ('intelccompiler', 'IntelEM64TCCompiler', 'Intel C Compiler for 64-bit applications')
compiler_class['pathcc'] = ('pathccompiler', 'PathScaleCCompiler', 'PathScale Compiler for SiCortex-based applications')
ccompiler._default_compilers += (('linux.*', 'intel'),
 ('linux.*', 'intele'),
 ('linux.*', 'intelem'),
 ('linux.*', 'pathcc'))
if sys.platform == 'win32':
    compiler_class['mingw32'] = ('mingw32ccompiler', 'Mingw32CCompiler', 'Mingw32 port of GNU C Compiler for Win32(for MSC built Python)')
    if mingw32():
        log.info('Setting mingw32 as default compiler for nt.')
        ccompiler._default_compilers = (('nt', 'mingw32'), ) + ccompiler._default_compilers
_distutils_new_compiler = new_compiler

def new_compiler(plat=None, compiler=None, verbose=0, dry_run=0, force=0):
    if plat is None:
        plat = os.name
    try:
        if compiler is None:
            compiler = get_default_compiler(plat)
        module_name, class_name, long_description = compiler_class[compiler]
    except KeyError:
        msg = "don't know how to compile C/C++ code on platform '%s'" % plat
        if compiler is not None:
            msg = msg + " with '%s' compiler" % compiler
        raise DistutilsPlatformError(msg)

    module_name = 'numpy.distutils.' + module_name
    try:
        __import__(module_name)
    except ImportError:
        msg = str(get_exception())
        log.info('%s in numpy.distutils; trying from distutils', str(msg))
        module_name = module_name[6:]
        try:
            __import__(module_name)
        except ImportError:
            msg = str(get_exception())
            raise DistutilsModuleError("can't compile C/C++ code: unable to load module '%s'" % module_name)

    try:
        module = sys.modules[module_name]
        klass = vars(module)[class_name]
    except KeyError:
        raise DistutilsModuleError(("can't compile C/C++ code: unable to find class '%s' " + "in module '%s'") % (class_name, module_name))

    compiler = klass(None, dry_run, force)
    log.debug('new_compiler returns %s' % klass)
    return compiler


ccompiler.new_compiler = new_compiler
_distutils_gen_lib_options = gen_lib_options

def gen_lib_options(compiler, library_dirs, runtime_library_dirs, libraries):
    library_dirs = quote_args(library_dirs)
    runtime_library_dirs = quote_args(runtime_library_dirs)
    r = _distutils_gen_lib_options(compiler, library_dirs, runtime_library_dirs, libraries)
    lib_opts = []
    for i in r:
        if is_sequence(i):
            lib_opts.extend(list(i))
        else:
            lib_opts.append(i)

    return lib_opts


ccompiler.gen_lib_options = gen_lib_options
for _cc in ['msvc', 'bcpp', 'cygwinc', 'emxc', 'unixc']:
    _m = sys.modules.get('distutils.' + _cc + 'compiler')
    if _m is not None:
        setattr(_m, 'gen_lib_options', gen_lib_options)

_distutils_gen_preprocess_options = gen_preprocess_options

def gen_preprocess_options(macros, include_dirs):
    include_dirs = quote_args(include_dirs)
    return _distutils_gen_preprocess_options(macros, include_dirs)


ccompiler.gen_preprocess_options = gen_preprocess_options
import re, string
_wordchars_re = re.compile('[^\\\\\\\'\\"%s ]*' % string.whitespace)
_squote_re = re.compile("'(?:[^'\\\\]|\\\\.)*'")
_dquote_re = re.compile('"(?:[^"\\\\]|\\\\.)*"')
_has_white_re = re.compile('\\s')

def split_quoted(s):
    s = s.strip()
    words = []
    pos = 0
    while s:
        m = _wordchars_re.match(s, pos)
        end = m.end()
        if end == len(s):
            words.append(s[:end])
            break
        if s[end] in string.whitespace:
            words.append(s[:end])
            s = s[end:].lstrip()
            pos = 0
        elif s[end] == '\\':
            s = s[:end] + s[end + 1:]
            pos = end + 1
        else:
            if s[end] == "'":
                m = _squote_re.match(s, end)
            elif s[end] == '"':
                m = _dquote_re.match(s, end)
            else:
                raise RuntimeError("this can't happen (bad char '%c')" % s[end])
            if m is None:
                raise ValueError('bad string (mismatched %s quotes?)' % s[end])
            beg, end = m.span()
            if _has_white_re.search(s[beg + 1:end - 1]):
                s = s[:beg] + s[beg + 1:end - 1] + s[end:]
                pos = m.end() - 2
            else:
                pos = m.end()
        if pos >= len(s):
            words.append(s)
            break

    return words


ccompiler.split_quoted = split_quoted
msvc_on_amd64()