# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\command\config.pyc
# Compiled at: 2013-04-07 07:04:04
import os, signal, warnings, sys
from distutils.command.config import config as old_config
from distutils.command.config import LANG_EXT
from distutils import log
from distutils.file_util import copy_file
from distutils.ccompiler import CompileError, LinkError
import distutils
from numpy.distutils.exec_command import exec_command
from numpy.distutils.mingw32ccompiler import generate_manifest
from numpy.distutils.command.autodist import check_inline, check_compiler_gcc4
from numpy.distutils.compat import get_exception
LANG_EXT['f77'] = '.f'
LANG_EXT['f90'] = '.f90'

class config(old_config):
    old_config.user_options += [
     ('fcompiler=', None, 'specify the Fortran compiler type')]

    def initialize_options(self):
        self.fcompiler = None
        old_config.initialize_options(self)
        return

    def try_run(self, body, headers=None, include_dirs=None, libraries=None, library_dirs=None, lang='c'):
        warnings.warn('\n+++++++++++++++++++++++++++++++++++++++++++++++++\nUsage of try_run is deprecated: please do not \nuse it anymore, and avoid configuration checks \ninvolving running executable on the target machine.\n+++++++++++++++++++++++++++++++++++++++++++++++++\n', DeprecationWarning)
        return old_config.try_run(self, body, headers, include_dirs, libraries, library_dirs, lang)

    def _check_compiler(self):
        old_config._check_compiler(self)
        from numpy.distutils.fcompiler import FCompiler, new_fcompiler
        if sys.platform == 'win32' and self.compiler.compiler_type == 'msvc':
            if not self.compiler.initialized:
                try:
                    self.compiler.initialize()
                except IOError:
                    e = get_exception()
                    msg = 'Could not initialize compiler instance: do you have Visual Studio\ninstalled ? If you are trying to build with mingw, please use python setup.py\nbuild -c mingw32 instead ). If you have Visual Studio installed, check it is\ncorrectly installed, and the right version (VS 2008 for python 2.6, VS 2003 for\n2.5, etc...). Original exception was: %s, and the Compiler\nclass was %s\n============================================================================' % (
                     e, self.compiler.__class__.__name__)
                    print '============================================================================'
                    raise distutils.errors.DistutilsPlatformError(msg)

        if not isinstance(self.fcompiler, FCompiler):
            self.fcompiler = new_fcompiler(compiler=self.fcompiler, dry_run=self.dry_run, force=1, c_compiler=self.compiler)
            if self.fcompiler is not None:
                self.fcompiler.customize(self.distribution)
                if self.fcompiler.get_version():
                    self.fcompiler.customize_cmd(self)
                    self.fcompiler.show_customization()
        return

    def _wrap_method(self, mth, lang, args):
        from distutils.ccompiler import CompileError
        from distutils.errors import DistutilsExecError
        save_compiler = self.compiler
        if lang in ('f77', 'f90'):
            self.compiler = self.fcompiler
        try:
            ret = mth(*((self,) + args))
        except (DistutilsExecError, CompileError):
            msg = str(get_exception())
            self.compiler = save_compiler
            raise CompileError

        self.compiler = save_compiler
        return ret

    def _compile(self, body, headers, include_dirs, lang):
        return self._wrap_method(old_config._compile, lang, (
         body, headers, include_dirs, lang))

    def _link(self, body, headers, include_dirs, libraries, library_dirs, lang):
        if self.compiler.compiler_type == 'msvc':
            libraries = (libraries or [])[:]
            library_dirs = (library_dirs or [])[:]
            if lang in ('f77', 'f90'):
                lang = 'c'
                if self.fcompiler:
                    for d in self.fcompiler.library_dirs or []:
                        if d.startswith('/usr/lib'):
                            s, o = exec_command(['cygpath', '-w', d], use_tee=False)
                            if not s:
                                d = o
                        library_dirs.append(d)

                    for libname in self.fcompiler.libraries or []:
                        if libname not in libraries:
                            libraries.append(libname)

            for libname in libraries:
                if libname.startswith('msvc'):
                    continue
                fileexists = False
                for libdir in library_dirs or []:
                    libfile = os.path.join(libdir, '%s.lib' % libname)
                    if os.path.isfile(libfile):
                        fileexists = True
                        break

                if fileexists:
                    continue
                fileexists = False
                for libdir in library_dirs:
                    libfile = os.path.join(libdir, 'lib%s.a' % libname)
                    if os.path.isfile(libfile):
                        libfile2 = os.path.join(libdir, '%s.lib' % libname)
                        copy_file(libfile, libfile2)
                        self.temp_files.append(libfile2)
                        fileexists = True
                        break

                if fileexists:
                    continue
                log.warn('could not find library %r in directories %s' % (
                 libname, library_dirs))

        elif self.compiler.compiler_type == 'mingw32':
            generate_manifest(self)
        return self._wrap_method(old_config._link, lang, (
         body, headers, include_dirs,
         libraries, library_dirs, lang))

    def check_header(self, header, include_dirs=None, library_dirs=None, lang='c'):
        self._check_compiler()
        return self.try_compile('/* we need a dummy line to make distutils happy */', [
         header], include_dirs)

    def check_decl(self, symbol, headers=None, include_dirs=None):
        self._check_compiler()
        body = '\nint main()\n{\n#ifndef %s\n    (void) %s;\n#endif\n    ;\n    return 0;\n}' % (symbol, symbol)
        return self.try_compile(body, headers, include_dirs)

    def check_macro_true(self, symbol, headers=None, include_dirs=None):
        self._check_compiler()
        body = '\nint main()\n{\n#if %s\n#else\n#error false or undefined macro\n#endif\n    ;\n    return 0;\n}' % (symbol,)
        return self.try_compile(body, headers, include_dirs)

    def check_type(self, type_name, headers=None, include_dirs=None, library_dirs=None):
        """Check type availability. Return True if the type can be compiled,
        False otherwise"""
        self._check_compiler()
        body = '\nint main() {\n  if ((%(name)s *) 0)\n    return 0;\n  if (sizeof (%(name)s))\n    return 0;\n}\n' % {'name': type_name}
        st = False
        try:
            try:
                self._compile(body % {'type': type_name}, headers, include_dirs, 'c')
                st = True
            except distutils.errors.CompileError:
                st = False

        finally:
            self._clean()

        return st

    def check_type_size(self, type_name, headers=None, include_dirs=None, library_dirs=None, expected=None):
        """Check size of a given type."""
        self._check_compiler()
        body = '\ntypedef %(type)s npy_check_sizeof_type;\nint main ()\n{\n    static int test_array [1 - 2 * !(((long) (sizeof (npy_check_sizeof_type))) >= 0)];\n    test_array [0] = 0\n\n    ;\n    return 0;\n}\n'
        self._compile(body % {'type': type_name}, headers, include_dirs, 'c')
        self._clean()
        if expected:
            body = '\ntypedef %(type)s npy_check_sizeof_type;\nint main ()\n{\n    static int test_array [1 - 2 * !(((long) (sizeof (npy_check_sizeof_type))) == %(size)s)];\n    test_array [0] = 0\n\n    ;\n    return 0;\n}\n'
            for size in expected:
                try:
                    self._compile(body % {'type': type_name, 'size': size}, headers, include_dirs, 'c')
                    self._clean()
                    return size
                except CompileError:
                    pass

        body = '\ntypedef %(type)s npy_check_sizeof_type;\nint main ()\n{\n    static int test_array [1 - 2 * !(((long) (sizeof (npy_check_sizeof_type))) <= %(size)s)];\n    test_array [0] = 0\n\n    ;\n    return 0;\n}\n'
        low = 0
        mid = 0
        while True:
            try:
                self._compile(body % {'type': type_name, 'size': mid}, headers, include_dirs, 'c')
                self._clean()
                break
            except CompileError:
                low = mid + 1
                mid = 2 * mid + 1

        high = mid
        while low != high:
            mid = (high - low) // 2 + low
            try:
                self._compile(body % {'type': type_name, 'size': mid}, headers, include_dirs, 'c')
                self._clean()
                high = mid
            except CompileError:
                low = mid + 1

        return low

    def check_func(self, func, headers=None, include_dirs=None, libraries=None, library_dirs=None, decl=False, call=False, call_args=None):
        self._check_compiler()
        body = []
        if decl:
            body.append('int %s (void);' % func)
        body.append('#ifdef _MSC_VER')
        body.append('#pragma function(%s)' % func)
        body.append('#endif')
        body.append('int main (void) {')
        if call:
            if call_args is None:
                call_args = ''
            body.append('  %s(%s);' % (func, call_args))
        else:
            body.append('  %s;' % func)
        body.append('  return 0;')
        body.append('}')
        body = ('\n').join(body) + '\n'
        return self.try_link(body, headers, include_dirs, libraries, library_dirs)

    def check_funcs_once(self, funcs, headers=None, include_dirs=None, libraries=None, library_dirs=None, decl=False, call=False, call_args=None):
        """Check a list of functions at once.

        This is useful to speed up things, since all the functions in the funcs
        list will be put in one compilation unit.

        Arguments
        ---------
        funcs: seq
            list of functions to test
        include_dirs : seq
            list of header paths
        libraries : seq
            list of libraries to link the code snippet to
        libraru_dirs : seq
            list of library paths
        decl : dict
            for every (key, value), the declaration in the value will be
            used for function in key. If a function is not in the
            dictionay, no declaration will be used.
        call : dict
            for every item (f, value), if the value is True, a call will be
            done to the function f.
        """
        self._check_compiler()
        body = []
        if decl:
            for f, v in decl.items():
                if v:
                    body.append('int %s (void);' % f)

        body.append('#ifdef _MSC_VER')
        for func in funcs:
            body.append('#pragma function(%s)' % func)

        body.append('#endif')
        body.append('int main (void) {')
        if call:
            for f in funcs:
                if f in call and call[f]:
                    if not (call_args and f in call_args and call_args[f]):
                        args = ''
                    else:
                        args = call_args[f]
                    body.append('  %s(%s);' % (f, args))
                else:
                    body.append('  %s;' % f)

        else:
            for f in funcs:
                body.append('  %s;' % f)

        body.append('  return 0;')
        body.append('}')
        body = ('\n').join(body) + '\n'
        return self.try_link(body, headers, include_dirs, libraries, library_dirs)

    def check_inline(self):
        """Return the inline keyword recognized by the compiler, empty string
        otherwise."""
        return check_inline(self)

    def check_compiler_gcc4(self):
        """Return True if the C compiler is gcc >= 4."""
        return check_compiler_gcc4(self)

    def get_output(self, body, headers=None, include_dirs=None, libraries=None, library_dirs=None, lang='c'):
        """Try to compile, link to an executable, and run a program
        built from 'body' and 'headers'. Returns the exit status code
        of the program and its output.
        """
        warnings.warn('\n+++++++++++++++++++++++++++++++++++++++++++++++++\nUsage of get_output is deprecated: please do not \nuse it anymore, and avoid configuration checks \ninvolving running executable on the target machine.\n+++++++++++++++++++++++++++++++++++++++++++++++++\n', DeprecationWarning)
        from distutils.ccompiler import CompileError, LinkError
        self._check_compiler()
        exitcode, output = (255, '')
        try:
            grabber = GrabStdout()
            try:
                src, obj, exe = self._link(body, headers, include_dirs, libraries, library_dirs, lang)
                grabber.restore()
            except:
                output = grabber.data
                grabber.restore()
                raise

            exe = os.path.join('.', exe)
            exitstatus, output = exec_command(exe, execute_in='.')
            if hasattr(os, 'WEXITSTATUS'):
                exitcode = os.WEXITSTATUS(exitstatus)
                if os.WIFSIGNALED(exitstatus):
                    sig = os.WTERMSIG(exitstatus)
                    log.error('subprocess exited with signal %d' % (sig,))
                    if sig == signal.SIGINT:
                        raise KeyboardInterrupt
            else:
                exitcode = exitstatus
            log.info('success!')
        except (CompileError, LinkError):
            log.info('failure.')

        self._clean()
        return (exitcode, output)


class GrabStdout(object):

    def __init__(self):
        self.sys_stdout = sys.stdout
        self.data = ''
        sys.stdout = self

    def write(self, data):
        self.sys_stdout.write(data)
        self.data += data

    def flush(self):
        self.sys_stdout.flush()

    def restore(self):
        sys.stdout = self.sys_stdout