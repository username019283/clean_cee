# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\command\build_src.pyc
# Compiled at: 2013-04-07 07:04:04
""" Build swig, f2py, pyrex sources.
"""
import os, re, sys, shlex, copy
from distutils.command import build_ext
from distutils.dep_util import newer_group, newer
from distutils.util import get_platform
from distutils.errors import DistutilsError, DistutilsSetupError

def have_pyrex():
    try:
        import Pyrex.Compiler.Main
        return True
    except ImportError:
        return False


from numpy.distutils import log
from numpy.distutils.misc_util import fortran_ext_match, appendpath, is_string, is_sequence, get_cmd
from numpy.distutils.from_template import process_file as process_f_file
from numpy.distutils.conv_template import process_file as process_c_file

def subst_vars(target, source, d):
    """Substitute any occurence of @foo@ by d['foo'] from source file into
    target."""
    var = re.compile('@([a-zA-Z_]+)@')
    fs = open(source, 'r')
    try:
        ft = open(target, 'w')
        try:
            for l in fs.readlines():
                m = var.search(l)
                if m:
                    ft.write(l.replace('@%s@' % m.group(1), d[m.group(1)]))
                else:
                    ft.write(l)

        finally:
            ft.close()

    finally:
        fs.close()


class build_src(build_ext.build_ext):
    description = 'build sources from SWIG, F2PY files or a function'
    user_options = [
     ('build-src=', 'd', 'directory to "build" sources to'),
     ('f2py-opts=', None, 'list of f2py command line options'),
     ('swig=', None, 'path to the SWIG executable'),
     ('swig-opts=', None, 'list of SWIG command line options'),
     ('swig-cpp', None, 'make SWIG create C++ files (default is autodetected from sources)'),
     ('f2pyflags=', None, 'additional flags to f2py (use --f2py-opts= instead)'),
     ('swigflags=', None, 'additional flags to swig (use --swig-opts= instead)'),
     ('force', 'f', 'forcibly build everything (ignore file timestamps)'),
     (
      'inplace', 'i',
      'ignore build-lib and put compiled extensions into the source ' + 'directory alongside your pure Python modules')]
    boolean_options = [
     'force', 'inplace']
    help_options = []

    def initialize_options(self):
        self.extensions = None
        self.package = None
        self.py_modules = None
        self.py_modules_dict = None
        self.build_src = None
        self.build_lib = None
        self.build_base = None
        self.force = None
        self.inplace = None
        self.package_dir = None
        self.f2pyflags = None
        self.f2py_opts = None
        self.swigflags = None
        self.swig_opts = None
        self.swig_cpp = None
        self.swig = None
        return

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_base'), ('build_lib',
                                                                           'build_lib'), ('force',
                                                                                          'force'))
        if self.package is None:
            self.package = self.distribution.ext_package
        self.extensions = self.distribution.ext_modules
        self.libraries = self.distribution.libraries or []
        self.py_modules = self.distribution.py_modules or []
        self.data_files = self.distribution.data_files or []
        if self.build_src is None:
            plat_specifier = '.%s-%s' % (get_platform(), sys.version[0:3])
            self.build_src = os.path.join(self.build_base, 'src' + plat_specifier)
        self.py_modules_dict = {}
        if self.f2pyflags:
            if self.f2py_opts:
                log.warn('ignoring --f2pyflags as --f2py-opts already used')
            else:
                self.f2py_opts = self.f2pyflags
            self.f2pyflags = None
        if self.f2py_opts is None:
            self.f2py_opts = []
        else:
            self.f2py_opts = shlex.split(self.f2py_opts)
        if self.swigflags:
            if self.swig_opts:
                log.warn('ignoring --swigflags as --swig-opts already used')
            else:
                self.swig_opts = self.swigflags
            self.swigflags = None
        if self.swig_opts is None:
            self.swig_opts = []
        else:
            self.swig_opts = shlex.split(self.swig_opts)
        build_ext = self.get_finalized_command('build_ext')
        if self.inplace is None:
            self.inplace = build_ext.inplace
        if self.swig_cpp is None:
            self.swig_cpp = build_ext.swig_cpp
        for c in ['swig', 'swig_opt']:
            o = '--' + c.replace('_', '-')
            v = getattr(build_ext, c, None)
            if v:
                if getattr(self, c):
                    log.warn('both build_src and build_ext define %s option' % o)
                else:
                    log.info('using "%s=%s" option from build_ext command' % (o, v))
                    setattr(self, c, v)

        return

    def run(self):
        log.info('build_src')
        if not (self.extensions or self.libraries):
            return
        self.build_sources()

    def build_sources(self):
        if self.inplace:
            self.get_package_dir = self.get_finalized_command('build_py').get_package_dir
        self.build_py_modules_sources()
        for libname_info in self.libraries:
            self.build_library_sources(*libname_info)

        if self.extensions:
            self.check_extensions_list(self.extensions)
            for ext in self.extensions:
                self.build_extension_sources(ext)

        self.build_data_files_sources()
        self.build_npy_pkg_config()

    def build_data_files_sources(self):
        if not self.data_files:
            return
        else:
            log.info('building data_files sources')
            from numpy.distutils.misc_util import get_data_files
            new_data_files = []
            for data in self.data_files:
                if isinstance(data, str):
                    new_data_files.append(data)
                elif isinstance(data, tuple):
                    d, files = data
                    if self.inplace:
                        build_dir = self.get_package_dir(('.').join(d.split(os.sep)))
                    else:
                        build_dir = os.path.join(self.build_src, d)
                    funcs = filter((lambda f: hasattr(f, '__call__')), files)
                    files = filter((lambda f: not hasattr(f, '__call__')), files)
                    for f in funcs:
                        if f.func_code.co_argcount == 1:
                            s = f(build_dir)
                        else:
                            s = f()
                        if s is not None:
                            if isinstance(s, list):
                                files.extend(s)
                            else:
                                if isinstance(s, str):
                                    files.append(s)
                                else:
                                    raise TypeError(repr(s))

                    filenames = get_data_files((d, files))
                    new_data_files.append((d, filenames))
                else:
                    raise TypeError(repr(data))

            self.data_files[:] = new_data_files
            return

    def _build_npy_pkg_config(self, info, gd):
        import shutil
        template, install_dir, subst_dict = info
        template_dir = os.path.dirname(template)
        for k, v in gd.items():
            subst_dict[k] = v

        if self.inplace == 1:
            generated_dir = os.path.join(template_dir, install_dir)
        else:
            generated_dir = os.path.join(self.build_src, template_dir, install_dir)
        generated = os.path.basename(os.path.splitext(template)[0])
        generated_path = os.path.join(generated_dir, generated)
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
        subst_vars(generated_path, template, subst_dict)
        full_install_dir = os.path.join(template_dir, install_dir)
        return (full_install_dir, generated_path)

    def build_npy_pkg_config(self):
        log.info('build_src: building npy-pkg config files')
        install_cmd = copy.copy(get_cmd('install'))
        if not install_cmd.finalized == 1:
            install_cmd.finalize_options()
        build_npkg = False
        gd = {}
        if self.inplace == 1:
            top_prefix = '.'
            build_npkg = True
        elif hasattr(install_cmd, 'install_libbase'):
            top_prefix = install_cmd.install_libbase
            build_npkg = True
        if build_npkg:
            for pkg, infos in self.distribution.installed_pkg_config.items():
                pkg_path = self.distribution.package_dir[pkg]
                prefix = os.path.join(os.path.abspath(top_prefix), pkg_path)
                d = {'prefix': prefix}
                for info in infos:
                    install_dir, generated = self._build_npy_pkg_config(info, d)
                    self.distribution.data_files.append((install_dir,
                     [
                      generated]))

    def build_py_modules_sources(self):
        if not self.py_modules:
            return
        else:
            log.info('building py_modules sources')
            new_py_modules = []
            for source in self.py_modules:
                if is_sequence(source) and len(source) == 3:
                    package, module_base, source = source
                    if self.inplace:
                        build_dir = self.get_package_dir(package)
                    else:
                        build_dir = os.path.join(self.build_src, os.path.join(*package.split('.')))
                    if hasattr(source, '__call__'):
                        target = os.path.join(build_dir, module_base + '.py')
                        source = source(target)
                    if source is None:
                        continue
                    modules = [
                     (
                      package, module_base, source)]
                    if package not in self.py_modules_dict:
                        self.py_modules_dict[package] = []
                    self.py_modules_dict[package] += modules
                else:
                    new_py_modules.append(source)

            self.py_modules[:] = new_py_modules
            return

    def build_library_sources(self, lib_name, build_info):
        sources = list(build_info.get('sources', []))
        if not sources:
            return
        log.info('building library "%s" sources' % lib_name)
        sources = self.generate_sources(sources, (lib_name, build_info))
        sources = self.template_sources(sources, (lib_name, build_info))
        sources, h_files = self.filter_h_files(sources)
        if h_files:
            log.info('%s - nothing done with h_files = %s', self.package, h_files)
        build_info['sources'] = sources

    def build_extension_sources(self, ext):
        sources = list(ext.sources)
        log.info('building extension "%s" sources' % ext.name)
        fullname = self.get_ext_fullname(ext.name)
        modpath = fullname.split('.')
        package = ('.').join(modpath[0:-1])
        if self.inplace:
            self.ext_target_dir = self.get_package_dir(package)
        sources = self.generate_sources(sources, ext)
        sources = self.template_sources(sources, ext)
        sources = self.swig_sources(sources, ext)
        sources = self.f2py_sources(sources, ext)
        sources = self.pyrex_sources(sources, ext)
        sources, py_files = self.filter_py_files(sources)
        if package not in self.py_modules_dict:
            self.py_modules_dict[package] = []
        modules = []
        for f in py_files:
            module = os.path.splitext(os.path.basename(f))[0]
            modules.append((package, module, f))

        self.py_modules_dict[package] += modules
        sources, h_files = self.filter_h_files(sources)
        if h_files:
            log.info('%s - nothing done with h_files = %s', package, h_files)
        ext.sources = sources

    def generate_sources(self, sources, extension):
        new_sources = []
        func_sources = []
        for source in sources:
            if is_string(source):
                new_sources.append(source)
            else:
                func_sources.append(source)

        if not func_sources:
            return new_sources
        if self.inplace and not is_sequence(extension):
            build_dir = self.ext_target_dir
        else:
            if is_sequence(extension):
                name = extension[0]
            else:
                name = extension.name
            build_dir = os.path.join(*([self.build_src] + name.split('.')[:-1]))
        self.mkpath(build_dir)
        for func in func_sources:
            source = func(extension, build_dir)
            if not source:
                continue
            if is_sequence(source):
                [ log.info("  adding '%s' to sources." % (s,)) for s in source ]
                new_sources.extend(source)
            else:
                log.info("  adding '%s' to sources." % (source,))
                new_sources.append(source)

        return new_sources

    def filter_py_files(self, sources):
        return self.filter_files(sources, ['.py'])

    def filter_h_files(self, sources):
        return self.filter_files(sources, ['.h', '.hpp', '.inc'])

    def filter_files(self, sources, exts=[]):
        new_sources = []
        files = []
        for source in sources:
            base, ext = os.path.splitext(source)
            if ext in exts:
                files.append(source)
            else:
                new_sources.append(source)

        return (
         new_sources, files)

    def template_sources(self, sources, extension):
        new_sources = []
        if is_sequence(extension):
            depends = extension[1].get('depends')
            include_dirs = extension[1].get('include_dirs')
        else:
            depends = extension.depends
            include_dirs = extension.include_dirs
        for source in sources:
            base, ext = os.path.splitext(source)
            if ext == '.src':
                if self.inplace:
                    target_dir = os.path.dirname(base)
                else:
                    target_dir = appendpath(self.build_src, os.path.dirname(base))
                self.mkpath(target_dir)
                target_file = os.path.join(target_dir, os.path.basename(base))
                if self.force or newer_group([source] + depends, target_file):
                    if _f_pyf_ext_match(base):
                        log.info('from_template:> %s' % target_file)
                        outstr = process_f_file(source)
                    else:
                        log.info('conv_template:> %s' % target_file)
                        outstr = process_c_file(source)
                    fid = open(target_file, 'w')
                    fid.write(outstr)
                    fid.close()
                if _header_ext_match(target_file):
                    d = os.path.dirname(target_file)
                    if d not in include_dirs:
                        log.info("  adding '%s' to include_dirs." % d)
                        include_dirs.append(d)
                new_sources.append(target_file)
            else:
                new_sources.append(source)

        return new_sources

    def pyrex_sources(self, sources, extension):
        new_sources = []
        ext_name = extension.name.split('.')[-1]
        for source in sources:
            base, ext = os.path.splitext(source)
            if ext == '.pyx':
                target_file = self.generate_a_pyrex_source(base, ext_name, source, extension)
                new_sources.append(target_file)
            else:
                new_sources.append(source)

        return new_sources

    def generate_a_pyrex_source(self, base, ext_name, source, extension):
        if self.inplace or not have_pyrex():
            target_dir = os.path.dirname(base)
        else:
            target_dir = appendpath(self.build_src, os.path.dirname(base))
        target_file = os.path.join(target_dir, ext_name + '.c')
        depends = [source] + extension.depends
        if self.force or newer_group(depends, target_file, 'newer'):
            if have_pyrex():
                import Pyrex.Compiler.Main
                log.info('pyrexc:> %s' % target_file)
                self.mkpath(target_dir)
                options = Pyrex.Compiler.Main.CompilationOptions(defaults=Pyrex.Compiler.Main.default_options, include_path=extension.include_dirs, output_file=target_file)
                pyrex_result = Pyrex.Compiler.Main.compile(source, options=options)
                if pyrex_result.num_errors != 0:
                    raise DistutilsError('%d errors while compiling %r with Pyrex' % (
                     pyrex_result.num_errors, source))
            else:
                if os.path.isfile(target_file):
                    log.warn('Pyrex required for compiling %r but not available, using old target %r' % (
                     source, target_file))
                else:
                    raise DistutilsError('Pyrex required for compiling %r but notavailable' % (
                     source,))
        return target_file

    def f2py_sources(self, sources, extension):
        new_sources = []
        f2py_sources = []
        f_sources = []
        f2py_targets = {}
        target_dirs = []
        ext_name = extension.name.split('.')[-1]
        skip_f2py = 0
        for source in sources:
            base, ext = os.path.splitext(source)
            if ext == '.pyf':
                if self.inplace:
                    target_dir = os.path.dirname(base)
                else:
                    target_dir = appendpath(self.build_src, os.path.dirname(base))
                if os.path.isfile(source):
                    name = get_f2py_modulename(source)
                    if name != ext_name:
                        raise DistutilsSetupError('mismatch of extension names: %s provides %r but expected %r' % (
                         source, name, ext_name))
                    target_file = os.path.join(target_dir, name + 'module.c')
                else:
                    log.debug("  source %s does not exist: skipping f2py'ing." % source)
                    name = ext_name
                    skip_f2py = 1
                    target_file = os.path.join(target_dir, name + 'module.c')
                    if not os.path.isfile(target_file):
                        log.warn('  target %s does not exist:\n   Assuming %smodule.c was generated with "build_src --inplace" command.' % (
                         target_file, name))
                        target_dir = os.path.dirname(base)
                        target_file = os.path.join(target_dir, name + 'module.c')
                        if not os.path.isfile(target_file):
                            raise DistutilsSetupError('%r missing' % (target_file,))
                        log.info('   Yes! Using %r as up-to-date target.' % target_file)
                target_dirs.append(target_dir)
                f2py_sources.append(source)
                f2py_targets[source] = target_file
                new_sources.append(target_file)
            elif fortran_ext_match(ext):
                f_sources.append(source)
            else:
                new_sources.append(source)

        if not (f2py_sources or f_sources):
            return new_sources
        for d in target_dirs:
            self.mkpath(d)

        f2py_options = extension.f2py_options + self.f2py_opts
        if self.distribution.libraries:
            for name, build_info in self.distribution.libraries:
                if name in extension.libraries:
                    f2py_options.extend(build_info.get('f2py_options', []))

        log.info('f2py options: %s' % f2py_options)
        if f2py_sources:
            if len(f2py_sources) != 1:
                raise DistutilsSetupError('only one .pyf file is allowed per extension module but got more: %r' % (
                 f2py_sources,))
            source = f2py_sources[0]
            target_file = f2py_targets[source]
            target_dir = os.path.dirname(target_file) or '.'
            depends = [source] + extension.depends
            if (self.force or newer_group(depends, target_file, 'newer')) and not skip_f2py:
                log.info('f2py: %s' % source)
                import numpy.f2py
                numpy.f2py.run_main(f2py_options + [
                 '--build-dir', target_dir, source])
            else:
                log.debug("  skipping '%s' f2py interface (up-to-date)" % source)
        else:
            if is_sequence(extension):
                name = extension[0]
            else:
                name = extension.name
            target_dir = os.path.join(*([self.build_src] + name.split('.')[:-1]))
            target_file = os.path.join(target_dir, ext_name + 'module.c')
            new_sources.append(target_file)
            depends = f_sources + extension.depends
            if (self.force or newer_group(depends, target_file, 'newer')) and not skip_f2py:
                log.info('f2py:> %s' % target_file)
                self.mkpath(target_dir)
                import numpy.f2py
                numpy.f2py.run_main(f2py_options + ['--lower', '--build-dir', target_dir] + ['-m', ext_name] + f_sources)
            else:
                log.debug("  skipping f2py fortran files for '%s' (up-to-date)" % target_file)
        if not os.path.isfile(target_file):
            raise DistutilsError('f2py target file %r not generated' % (target_file,))
        target_c = os.path.join(self.build_src, 'fortranobject.c')
        target_h = os.path.join(self.build_src, 'fortranobject.h')
        log.info("  adding '%s' to sources." % target_c)
        new_sources.append(target_c)
        if self.build_src not in extension.include_dirs:
            log.info("  adding '%s' to include_dirs." % self.build_src)
            extension.include_dirs.append(self.build_src)
        if not skip_f2py:
            import numpy.f2py
            d = os.path.dirname(numpy.f2py.__file__)
            source_c = os.path.join(d, 'src', 'fortranobject.c')
            source_h = os.path.join(d, 'src', 'fortranobject.h')
            if newer(source_c, target_c) or newer(source_h, target_h):
                self.mkpath(os.path.dirname(target_c))
                self.copy_file(source_c, target_c)
                self.copy_file(source_h, target_h)
        else:
            if not os.path.isfile(target_c):
                raise DistutilsSetupError('f2py target_c file %r not found' % (target_c,))
            if not os.path.isfile(target_h):
                raise DistutilsSetupError('f2py target_h file %r not found' % (target_h,))
            for name_ext in ['-f2pywrappers.f', '-f2pywrappers2.f90']:
                filename = os.path.join(target_dir, ext_name + name_ext)
                if os.path.isfile(filename):
                    log.info("  adding '%s' to sources." % filename)
                    f_sources.append(filename)

        return new_sources + f_sources

    def swig_sources(self, sources, extension):
        new_sources = []
        swig_sources = []
        swig_targets = {}
        target_dirs = []
        py_files = []
        target_ext = '.c'
        if '-c++' in extension.swig_opts:
            typ = 'c++'
            is_cpp = True
            extension.swig_opts.remove('-c++')
        else:
            if self.swig_cpp:
                typ = 'c++'
                is_cpp = True
            else:
                typ = None
                is_cpp = False
            skip_swig = 0
            ext_name = extension.name.split('.')[-1]
            for source in sources:
                base, ext = os.path.splitext(source)
                if ext == '.i':
                    if self.inplace:
                        target_dir = os.path.dirname(base)
                        py_target_dir = self.ext_target_dir
                    else:
                        target_dir = appendpath(self.build_src, os.path.dirname(base))
                        py_target_dir = target_dir
                    if os.path.isfile(source):
                        name = get_swig_modulename(source)
                        if name != ext_name[1:]:
                            raise DistutilsSetupError('mismatch of extension names: %s provides %r but expected %r' % (
                             source, name, ext_name[1:]))
                        if typ is None:
                            typ = get_swig_target(source)
                            is_cpp = typ == 'c++'
                            if is_cpp:
                                target_ext = '.cpp'
                        else:
                            typ2 = get_swig_target(source)
                            if typ2 is None:
                                log.warn('source %r does not define swig target, assuming %s swig target' % (
                                 source, typ))
                                if is_cpp:
                                    target_ext = '.cpp'
                            elif typ != typ2:
                                log.warn('expected %r but source %r defines %r swig target' % (
                                 typ, source, typ2))
                                if typ2 == 'c++':
                                    log.warn('resetting swig target to c++ (some targets may have .c extension)')
                                    is_cpp = True
                                    target_ext = '.cpp'
                                else:
                                    log.warn('assuming that %r has c++ swig target' % source)
                        target_file = os.path.join(target_dir, '%s_wrap%s' % (
                         name, target_ext))
                    else:
                        log.warn("  source %s does not exist: skipping swig'ing." % source)
                        name = ext_name[1:]
                        skip_swig = 1
                        target_file = _find_swig_target(target_dir, name)
                        if not os.path.isfile(target_file):
                            log.warn('  target %s does not exist:\n   Assuming %s_wrap.{c,cpp} was generated with "build_src --inplace" command.' % (
                             target_file, name))
                            target_dir = os.path.dirname(base)
                            target_file = _find_swig_target(target_dir, name)
                            if not os.path.isfile(target_file):
                                raise DistutilsSetupError('%r missing' % (target_file,))
                            log.warn('   Yes! Using %r as up-to-date target.' % target_file)
                    target_dirs.append(target_dir)
                    new_sources.append(target_file)
                    py_files.append(os.path.join(py_target_dir, name + '.py'))
                    swig_sources.append(source)
                    swig_targets[source] = new_sources[-1]
                else:
                    new_sources.append(source)

        if not swig_sources:
            return new_sources
        else:
            if skip_swig:
                return new_sources + py_files
            for d in target_dirs:
                self.mkpath(d)

            swig = self.swig or self.find_swig()
            swig_cmd = [swig, '-python'] + extension.swig_opts
            if is_cpp:
                swig_cmd.append('-c++')
            for d in extension.include_dirs:
                swig_cmd.append('-I' + d)

            for source in swig_sources:
                target = swig_targets[source]
                depends = [source] + extension.depends
                if self.force or newer_group(depends, target, 'newer'):
                    log.info('%s: %s' % (
                     os.path.basename(swig) + (is_cpp and '++' or ''), source))
                    self.spawn(swig_cmd + self.swig_opts + [-o, target, -outdir, py_target_dir, source])
                else:
                    log.debug("  skipping '%s' swig interface (up-to-date)" % source)

            return new_sources + py_files


_f_pyf_ext_match = re.compile('.*[.](f90|f95|f77|for|ftn|f|pyf)\\Z', re.I).match
_header_ext_match = re.compile('.*[.](inc|h|hpp)\\Z', re.I).match
_swig_module_name_match = re.compile('\\s*%module\\s*(.*\\(\\s*package\\s*=\\s*"(?P<package>[\\w_]+)".*\\)|)\\s*(?P<name>[\\w_]+)', re.I).match
_has_c_header = re.compile('-[*]-\\s*c\\s*-[*]-', re.I).search
_has_cpp_header = re.compile('-[*]-\\s*c[+][+]\\s*-[*]-', re.I).search

def get_swig_target(source):
    f = open(source, 'r')
    result = None
    line = f.readline()
    if _has_cpp_header(line):
        result = 'c++'
    if _has_c_header(line):
        result = 'c'
    f.close()
    return result


def get_swig_modulename(source):
    f = open(source, 'r')
    f_readlines = getattr(f, 'xreadlines', f.readlines)
    name = None
    for line in f_readlines():
        m = _swig_module_name_match(line)
        if m:
            name = m.group('name')
            break

    f.close()
    return name


def _find_swig_target(target_dir, name):
    for ext in ['.cpp', '.c']:
        target = os.path.join(target_dir, '%s_wrap%s' % (name, ext))
        if os.path.isfile(target):
            break

    return target


_f2py_module_name_match = re.compile('\\s*python\\s*module\\s*(?P<name>[\\w_]+)', re.I).match
_f2py_user_module_name_match = re.compile('\\s*python\\s*module\\s*(?P<name>[\\w_]*?__user__[\\w_]*)', re.I).match

def get_f2py_modulename(source):
    name = None
    f = open(source)
    f_readlines = getattr(f, 'xreadlines', f.readlines)
    for line in f_readlines():
        m = _f2py_module_name_match(line)
        if m:
            if _f2py_user_module_name_match(line):
                continue
            name = m.group('name')
            break

    f.close()
    return name