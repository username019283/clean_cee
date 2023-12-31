# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: setuptools\command\bdist_egg.pyc
# Compiled at: 2009-10-19 15:35:44
"""setuptools.command.bdist_egg

Build .egg distributions"""
import sys, os, marshal
from setuptools import Command
from distutils.dir_util import remove_tree, mkpath
from distutils.sysconfig import get_python_version, get_python_lib
from distutils import log
from distutils.errors import DistutilsSetupError
from pkg_resources import get_build_platform, Distribution, ensure_directory
from pkg_resources import EntryPoint
from types import CodeType
from setuptools.extension import Library

def strip_module(filename):
    if '.' in filename:
        filename = os.path.splitext(filename)[0]
    if filename.endswith('module'):
        filename = filename[:-6]
    return filename


def write_stub(resource, pyfile):
    f = open(pyfile, 'w')
    f.write(('\n').join([
     'def __bootstrap__():',
     '   global __bootstrap__, __loader__, __file__',
     '   import sys, pkg_resources, imp',
     '   __file__ = pkg_resources.resource_filename(__name__,%r)' % resource,
     '   __loader__ = None; del __bootstrap__, __loader__',
     '   imp.load_dynamic(__name__,__file__)',
     '__bootstrap__()',
     '']))
    f.close()


NS_PKG_STUB = '__import__("pkg_resources").declare_namespace(__name__)'

class bdist_egg(Command):
    description = 'create an "egg" distribution'
    user_options = [
     ('bdist-dir=', 'b', 'temporary directory for creating the distribution'),
     (
      'plat-name=', 'p',
      'platform name to embed in generated filenames (default: %s)' % get_build_platform()),
     ('exclude-source-files', None, 'remove all .py files from the generated egg'),
     (
      'keep-temp', 'k',
      'keep the pseudo-installation tree around after ' + 'creating the distribution archive'),
     ('dist-dir=', 'd', 'directory to put final built distributions in'),
     ('skip-build', None, 'skip rebuilding everything (for testing/debugging)')]
    boolean_options = [
     'keep-temp', 'skip-build', 'exclude-source-files']

    def initialize_options(self):
        self.bdist_dir = None
        self.plat_name = None
        self.keep_temp = 0
        self.dist_dir = None
        self.skip_build = 0
        self.egg_output = None
        self.exclude_source_files = None
        return

    def finalize_options(self):
        ei_cmd = self.ei_cmd = self.get_finalized_command('egg_info')
        self.egg_info = ei_cmd.egg_info
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'egg')
        if self.plat_name is None:
            self.plat_name = get_build_platform()
        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))
        if self.egg_output is None:
            basename = Distribution(None, None, ei_cmd.egg_name, ei_cmd.egg_version, get_python_version(), self.distribution.has_ext_modules() and self.plat_name).egg_name()
            self.egg_output = os.path.join(self.dist_dir, basename + '.egg')
        return

    def do_install_data(self):
        self.get_finalized_command('install').install_lib = self.bdist_dir
        site_packages = os.path.normcase(os.path.realpath(get_python_lib()))
        old, self.distribution.data_files = self.distribution.data_files, []
        for item in old:
            if isinstance(item, tuple) and len(item) == 2:
                if os.path.isabs(item[0]):
                    realpath = os.path.realpath(item[0])
                    normalized = os.path.normcase(realpath)
                    if normalized == site_packages or normalized.startswith(site_packages + os.sep):
                        item = (realpath[len(site_packages) + 1:], item[1])
            self.distribution.data_files.append(item)

        try:
            log.info('installing package data to %s' % self.bdist_dir)
            self.call_command('install_data', force=0, root=None)
        finally:
            self.distribution.data_files = old

        return

    def get_outputs(self):
        return [self.egg_output]

    def call_command(self, cmdname, **kw):
        """Invoke reinitialized command `cmdname` with keyword args"""
        for dirname in INSTALL_DIRECTORY_ATTRS:
            kw.setdefault(dirname, self.bdist_dir)

        kw.setdefault('skip_build', self.skip_build)
        kw.setdefault('dry_run', self.dry_run)
        cmd = self.reinitialize_command(cmdname, **kw)
        self.run_command(cmdname)
        return cmd

    def run(self):
        self.run_command('egg_info')
        log.info('installing library code to %s' % self.bdist_dir)
        instcmd = self.get_finalized_command('install')
        old_root = instcmd.root
        instcmd.root = None
        if self.distribution.has_c_libraries() and not self.skip_build:
            self.run_command('build_clib')
        cmd = self.call_command('install_lib', warn_dir=0)
        instcmd.root = old_root
        all_outputs, ext_outputs = self.get_ext_outputs()
        self.stubs = []
        to_compile = []
        for p, ext_name in enumerate(ext_outputs):
            filename, ext = os.path.splitext(ext_name)
            pyfile = os.path.join(self.bdist_dir, strip_module(filename) + '.py')
            self.stubs.append(pyfile)
            log.info('creating stub loader for %s' % ext_name)
            if not self.dry_run:
                write_stub(os.path.basename(ext_name), pyfile)
            to_compile.append(pyfile)
            ext_outputs[p] = ext_name.replace(os.sep, '/')

        to_compile.extend(self.make_init_files())
        if to_compile:
            cmd.byte_compile(to_compile)
        if self.distribution.data_files:
            self.do_install_data()
        archive_root = self.bdist_dir
        egg_info = os.path.join(archive_root, 'EGG-INFO')
        self.mkpath(egg_info)
        if self.distribution.scripts:
            script_dir = os.path.join(egg_info, 'scripts')
            log.info('installing scripts to %s' % script_dir)
            self.call_command('install_scripts', install_dir=script_dir, no_ep=1)
        self.copy_metadata_to(egg_info)
        native_libs = os.path.join(egg_info, 'native_libs.txt')
        if all_outputs:
            log.info('writing %s' % native_libs)
            if not self.dry_run:
                ensure_directory(native_libs)
                libs_file = open(native_libs, 'wt')
                libs_file.write(('\n').join(all_outputs))
                libs_file.write('\n')
                libs_file.close()
        elif os.path.isfile(native_libs):
            log.info('removing %s' % native_libs)
            if not self.dry_run:
                os.unlink(native_libs)
        write_safety_flag(os.path.join(archive_root, 'EGG-INFO'), self.zip_safe())
        if os.path.exists(os.path.join(self.egg_info, 'depends.txt')):
            log.warn("WARNING: 'depends.txt' will not be used by setuptools 0.6!\nUse the install_requires/extras_require setup() args instead.")
        if self.exclude_source_files:
            self.zap_pyfiles()
        make_zipfile(self.egg_output, archive_root, verbose=self.verbose, dry_run=self.dry_run, mode=self.gen_header())
        if not self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)
        getattr(self.distribution, 'dist_files', []).append((
         'bdist_egg', get_python_version(), self.egg_output))
        return

    def zap_pyfiles(self):
        log.info('Removing .py files from temporary directory')
        for base, dirs, files in walk_egg(self.bdist_dir):
            for name in files:
                if name.endswith('.py'):
                    path = os.path.join(base, name)
                    log.debug('Deleting %s', path)
                    os.unlink(path)

    def zip_safe(self):
        safe = getattr(self.distribution, 'zip_safe', None)
        if safe is not None:
            return safe
        else:
            log.warn('zip_safe flag not set; analyzing archive contents...')
            return analyze_egg(self.bdist_dir, self.stubs)

    def make_init_files(self):
        """Create missing package __init__ files"""
        init_files = []
        for base, dirs, files in walk_egg(self.bdist_dir):
            if base == self.bdist_dir:
                continue
            for name in files:
                if name.endswith('.py'):
                    if '__init__.py' not in files:
                        pkg = base[len(self.bdist_dir) + 1:].replace(os.sep, '.')
                        if self.distribution.has_contents_for(pkg):
                            log.warn('Creating missing __init__.py for %s', pkg)
                            filename = os.path.join(base, '__init__.py')
                            if not self.dry_run:
                                f = open(filename, 'w')
                                f.write(NS_PKG_STUB)
                                f.close()
                            init_files.append(filename)
                    break
            else:
                dirs[:] = []

        return init_files

    def gen_header(self):
        epm = EntryPoint.parse_map(self.distribution.entry_points or '')
        ep = epm.get('setuptools.installation', {}).get('eggsecutable')
        if ep is None:
            return 'w'
        else:
            if not ep.attrs or ep.extras:
                raise DistutilsSetupError("eggsecutable entry point (%r) cannot have 'extras' or refer to a module" % (
                 ep,))
            pyver = sys.version[:3]
            pkg = ep.module_name
            full = ('.').join(ep.attrs)
            base = ep.attrs[0]
            basename = os.path.basename(self.egg_output)
            header = '#!/bin/sh\nif [ `basename $0` = "%(basename)s" ]\nthen exec python%(pyver)s -c "import sys, os; sys.path.insert(0, os.path.abspath(\'$0\')); from %(pkg)s import %(base)s; sys.exit(%(full)s())" "$@"\nelse\n  echo $0 is not the correct name for this egg file.\n  echo Please rename it back to %(basename)s and try again.\n  exec false\nfi\n' % locals()
            if not self.dry_run:
                mkpath(os.path.dirname(self.egg_output), dry_run=self.dry_run)
                f = open(self.egg_output, 'w')
                f.write(header)
                f.close()
            return 'a'

    def copy_metadata_to(self, target_dir):
        prefix = os.path.join(self.egg_info, '')
        for path in self.ei_cmd.filelist.files:
            if path.startswith(prefix):
                target = os.path.join(target_dir, path[len(prefix):])
                ensure_directory(target)
                self.copy_file(path, target)

    def get_ext_outputs(self):
        """Get a list of relative paths to C extensions in the output distro"""
        all_outputs = []
        ext_outputs = []
        paths = {self.bdist_dir: ''}
        for base, dirs, files in os.walk(self.bdist_dir):
            for filename in files:
                if os.path.splitext(filename)[1].lower() in NATIVE_EXTENSIONS:
                    all_outputs.append(paths[base] + filename)

            for filename in dirs:
                paths[os.path.join(base, filename)] = paths[base] + filename + '/'

        if self.distribution.has_ext_modules():
            build_cmd = self.get_finalized_command('build_ext')
            for ext in build_cmd.extensions:
                if isinstance(ext, Library):
                    continue
                fullname = build_cmd.get_ext_fullname(ext.name)
                filename = build_cmd.get_ext_filename(fullname)
                if not os.path.basename(filename).startswith('dl-'):
                    if os.path.exists(os.path.join(self.bdist_dir, filename)):
                        ext_outputs.append(filename)

        return (
         all_outputs, ext_outputs)


NATIVE_EXTENSIONS = dict.fromkeys(('.dll .so .dylib .pyd').split())

def walk_egg(egg_dir):
    """Walk an unpacked egg's contents, skipping the metadata directory"""
    walker = os.walk(egg_dir)
    base, dirs, files = walker.next()
    if 'EGG-INFO' in dirs:
        dirs.remove('EGG-INFO')
    yield (
     base, dirs, files)
    for bdf in walker:
        yield bdf


def analyze_egg(egg_dir, stubs):
    for flag, fn in safety_flags.items():
        if os.path.exists(os.path.join(egg_dir, 'EGG-INFO', fn)):
            return flag

    if not can_scan():
        return False
    safe = True
    for base, dirs, files in walk_egg(egg_dir):
        for name in files:
            if name.endswith('.py') or name.endswith('.pyw'):
                continue
            elif name.endswith('.pyc') or name.endswith('.pyo'):
                safe = scan_module(egg_dir, base, name, stubs) and safe

    return safe


def write_safety_flag(egg_dir, safe):
    for flag, fn in safety_flags.items():
        fn = os.path.join(egg_dir, fn)
        if os.path.exists(fn):
            if safe is None or bool(safe) != flag:
                os.unlink(fn)
        elif safe is not None and bool(safe) == flag:
            f = open(fn, 'wb')
            f.write('\n')
            f.close()

    return


safety_flags = {True: 'zip-safe', 
   False: 'not-zip-safe'}

def scan_module(egg_dir, base, name, stubs):
    """Check whether module possibly uses unsafe-for-zipfile stuff"""
    filename = os.path.join(base, name)
    if filename[:-1] in stubs:
        return True
    pkg = base[len(egg_dir) + 1:].replace(os.sep, '.')
    module = pkg + (pkg and '.' or '') + os.path.splitext(name)[0]
    f = open(filename, 'rb')
    f.read(8)
    code = marshal.load(f)
    f.close()
    safe = True
    symbols = dict.fromkeys(iter_symbols(code))
    for bad in ['__file__', '__path__']:
        if bad in symbols:
            log.warn('%s: module references %s', module, bad)
            safe = False

    if 'inspect' in symbols:
        for bad in ['getsource', 'getabsfile', 'getsourcefile', 'getfilegetsourcelines', 
         'findsource', 
         'getcomments', 'getframeinfo', 
         'getinnerframes', 
         'getouterframes', 'stack', 'trace']:
            if bad in symbols:
                log.warn('%s: module MAY be using inspect.%s', module, bad)
                safe = False

    if '__name__' in symbols and '__main__' in symbols and '.' not in module:
        if sys.version[:3] == '2.4':
            log.warn("%s: top-level module may be 'python -m' script", module)
            safe = False
    return safe


def iter_symbols(code):
    """Yield names and strings used by `code` and its nested code objects"""
    for name in code.co_names:
        yield name

    for const in code.co_consts:
        if isinstance(const, basestring):
            yield const
        elif isinstance(const, CodeType):
            for name in iter_symbols(const):
                yield name


def can_scan():
    if not sys.platform.startswith('java') and sys.platform != 'cli':
        return True
    log.warn('Unable to analyze compiled code on this platform.')
    log.warn("Please ask the author to include a 'zip_safe' setting (either True or False) in the package's setup.py")


INSTALL_DIRECTORY_ATTRS = [
 'install_lib', 'install_dir', 'install_data', 'install_base']

def make_zipfile(zip_filename, base_dir, verbose=0, dry_run=0, compress=None, mode='w'):
    """Create a zip file from all the files under 'base_dir'.  The output
    zip file will be named 'base_dir' + ".zip".  Uses either the "zipfile"
    Python module (if available) or the InfoZIP "zip" utility (if installed
    and found on the default search path).  If neither tool is available,
    raises DistutilsExecError.  Returns the name of the output zip file.
    """
    import zipfile
    mkpath(os.path.dirname(zip_filename), dry_run=dry_run)
    log.info("creating '%s' and adding '%s' to it", zip_filename, base_dir)

    def visit(z, dirname, names):
        for name in names:
            path = os.path.normpath(os.path.join(dirname, name))
            if os.path.isfile(path):
                p = path[len(base_dir) + 1:]
                if not dry_run:
                    z.write(path, p)
                log.debug("adding '%s'" % p)

    if compress is None:
        compress = sys.version >= '2.4'
    compression = [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED][bool(compress)]
    if not dry_run:
        z = zipfile.ZipFile(zip_filename, mode, compression=compression)
        os.path.walk(base_dir, visit, z)
        z.close()
    else:
        os.path.walk(base_dir, visit, None)
    return zip_filename