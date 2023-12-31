# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\command\build_clib.pyc
# Compiled at: 2013-04-07 07:04:04
""" Modified version of build_clib that handles fortran source files.
"""
import os
from glob import glob
import shutil
from distutils.command.build_clib import build_clib as old_build_clib
from distutils.errors import DistutilsSetupError, DistutilsError, DistutilsFileError
from numpy.distutils import log
from distutils.dep_util import newer_group
from numpy.distutils.misc_util import filter_sources, has_f_sources, has_cxx_sources, all_strings, get_lib_source_files, is_sequence, get_numpy_include_dirs
_l = old_build_clib.user_options
for _i in range(len(_l)):
    if _l[_i][0] in ('build-clib', 'build-temp'):
        _l[_i] = (
         _l[_i][0] + '=',) + _l[_i][1:]

class build_clib(old_build_clib):
    description = 'build C/C++/F libraries used by Python extensions'
    user_options = old_build_clib.user_options + [
     ('fcompiler=', None, 'specify the Fortran compiler type'),
     ('inplace', 'i', 'Build in-place')]
    boolean_options = old_build_clib.boolean_options + ['inplace']

    def initialize_options(self):
        old_build_clib.initialize_options(self)
        self.fcompiler = None
        self.inplace = 0
        return

    def have_f_sources(self):
        for lib_name, build_info in self.libraries:
            if has_f_sources(build_info.get('sources', [])):
                return True

        return False

    def have_cxx_sources(self):
        for lib_name, build_info in self.libraries:
            if has_cxx_sources(build_info.get('sources', [])):
                return True

        return False

    def run(self):
        if not self.libraries:
            return
        else:
            languages = []
            self.run_command('build_src')
            for lib_name, build_info in self.libraries:
                l = build_info.get('language', None)
                if l and l not in languages:
                    languages.append(l)

            from distutils.ccompiler import new_compiler
            self.compiler = new_compiler(compiler=self.compiler, dry_run=self.dry_run, force=self.force)
            self.compiler.customize(self.distribution, need_cxx=self.have_cxx_sources())
            libraries = self.libraries
            self.libraries = None
            self.compiler.customize_cmd(self)
            self.libraries = libraries
            self.compiler.show_customization()
            if self.have_f_sources():
                from numpy.distutils.fcompiler import new_fcompiler
                self._f_compiler = new_fcompiler(compiler=self.fcompiler, verbose=self.verbose, dry_run=self.dry_run, force=self.force, requiref90='f90' in languages, c_compiler=self.compiler)
                if self._f_compiler is not None:
                    self._f_compiler.customize(self.distribution)
                    libraries = self.libraries
                    self.libraries = None
                    self._f_compiler.customize_cmd(self)
                    self.libraries = libraries
                    self._f_compiler.show_customization()
            else:
                self._f_compiler = None
            self.build_libraries(self.libraries)
            if self.inplace:
                for l in self.distribution.installed_libraries:
                    libname = self.compiler.library_filename(l.name)
                    source = os.path.join(self.build_clib, libname)
                    target = os.path.join(l.target_dir, libname)
                    self.mkpath(l.target_dir)
                    shutil.copy(source, target)

            return

    def get_source_files(self):
        self.check_library_list(self.libraries)
        filenames = []
        for lib in self.libraries:
            filenames.extend(get_lib_source_files(lib))

        return filenames

    def build_libraries(self, libraries):
        for lib_name, build_info in libraries:
            self.build_a_library(build_info, lib_name, libraries)

    def build_a_library(self, build_info, lib_name, libraries):
        compiler = self.compiler
        fcompiler = self._f_compiler
        sources = build_info.get('sources')
        if sources is None or not is_sequence(sources):
            raise DistutilsSetupError(("in 'libraries' option (library '%s'), " + "'sources' must be present and must be " + 'a list of source filenames') % lib_name)
        sources = list(sources)
        c_sources, cxx_sources, f_sources, fmodule_sources = filter_sources(sources)
        requiref90 = not not fmodule_sources or build_info.get('language', 'c') == 'f90'
        source_languages = []
        if c_sources:
            source_languages.append('c')
        if cxx_sources:
            source_languages.append('c++')
        if requiref90:
            source_languages.append('f90')
        elif f_sources:
            source_languages.append('f77')
        build_info['source_languages'] = source_languages
        lib_file = compiler.library_filename(lib_name, output_dir=self.build_clib)
        depends = sources + build_info.get('depends', [])
        if not (self.force or newer_group(depends, lib_file, 'newer')):
            log.debug("skipping '%s' library (up-to-date)", lib_name)
            return
        else:
            log.info("building '%s' library", lib_name)
            config_fc = build_info.get('config_fc', {})
            if fcompiler is not None and config_fc:
                log.info('using additional config_fc from setup script for fortran compiler: %s' % (
                 config_fc,))
                from numpy.distutils.fcompiler import new_fcompiler
                fcompiler = new_fcompiler(compiler=fcompiler.compiler_type, verbose=self.verbose, dry_run=self.dry_run, force=self.force, requiref90=requiref90, c_compiler=self.compiler)
                if fcompiler is not None:
                    dist = self.distribution
                    base_config_fc = dist.get_option_dict('config_fc').copy()
                    base_config_fc.update(config_fc)
                    fcompiler.customize(base_config_fc)
            if (f_sources or fmodule_sources) and fcompiler is None:
                raise DistutilsError('library %s has Fortran sources but no Fortran compiler found' % lib_name)
            if fcompiler is not None:
                fcompiler.extra_f77_compile_args = build_info.get('extra_f77_compile_args') or []
                fcompiler.extra_f90_compile_args = build_info.get('extra_f90_compile_args') or []
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            if include_dirs is None:
                include_dirs = []
            extra_postargs = build_info.get('extra_compiler_args') or []
            include_dirs.extend(get_numpy_include_dirs())
            module_dirs = build_info.get('module_dirs') or []
            module_build_dir = os.path.dirname(lib_file)
            if requiref90:
                self.mkpath(module_build_dir)
            if compiler.compiler_type == 'msvc':
                c_sources += cxx_sources
                cxx_sources = []
            objects = []
            if c_sources:
                log.info('compiling C sources')
                objects = compiler.compile(c_sources, output_dir=self.build_temp, macros=macros, include_dirs=include_dirs, debug=self.debug, extra_postargs=extra_postargs)
            if cxx_sources:
                log.info('compiling C++ sources')
                cxx_compiler = compiler.cxx_compiler()
                cxx_objects = cxx_compiler.compile(cxx_sources, output_dir=self.build_temp, macros=macros, include_dirs=include_dirs, debug=self.debug, extra_postargs=extra_postargs)
                objects.extend(cxx_objects)
            if f_sources or fmodule_sources:
                extra_postargs = []
                f_objects = []
                if requiref90:
                    if fcompiler.module_dir_switch is None:
                        existing_modules = glob('*.mod')
                    extra_postargs += fcompiler.module_options(module_dirs, module_build_dir)
                if fmodule_sources:
                    log.info('compiling Fortran 90 module sources')
                    f_objects += fcompiler.compile(fmodule_sources, output_dir=self.build_temp, macros=macros, include_dirs=include_dirs, debug=self.debug, extra_postargs=extra_postargs)
                if requiref90 and self._f_compiler.module_dir_switch is None:
                    for f in glob('*.mod'):
                        if f in existing_modules:
                            continue
                        t = os.path.join(module_build_dir, f)
                        if os.path.abspath(f) == os.path.abspath(t):
                            continue
                        if os.path.isfile(t):
                            os.remove(t)
                        try:
                            self.move_file(f, module_build_dir)
                        except DistutilsFileError:
                            log.warn('failed to move %r to %r' % (
                             f, module_build_dir))

                if f_sources:
                    log.info('compiling Fortran sources')
                    f_objects += fcompiler.compile(f_sources, output_dir=self.build_temp, macros=macros, include_dirs=include_dirs, debug=self.debug, extra_postargs=extra_postargs)
            else:
                f_objects = []
            objects.extend(f_objects)
            compiler.create_static_lib(objects, lib_name, output_dir=self.build_clib, debug=self.debug)
            clib_libraries = build_info.get('libraries', [])
            for lname, binfo in libraries:
                if lname in clib_libraries:
                    clib_libraries.extend(binfo[1].get('libraries', []))

            if clib_libraries:
                build_info['libraries'] = clib_libraries
            return