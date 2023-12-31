# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: setuptools\command\develop.pyc
# Compiled at: 2008-02-15 13:29:24
from setuptools.command.easy_install import easy_install
from distutils.util import convert_path
from pkg_resources import Distribution, PathMetadata, normalize_path
from distutils import log
from distutils.errors import *
import sys, os, setuptools, glob

class develop(easy_install):
    """Set up package for development"""
    description = "install package in 'development mode'"
    user_options = easy_install.user_options + [
     ('uninstall', 'u', 'Uninstall this source package'),
     ('egg-path=', None, 'Set the path to be used in the .egg-link file')]
    boolean_options = easy_install.boolean_options + ['uninstall']
    command_consumes_arguments = False

    def run(self):
        if self.uninstall:
            self.multi_version = True
            self.uninstall_link()
        else:
            self.install_for_development()
        self.warn_deprecated_options()

    def initialize_options(self):
        self.uninstall = None
        self.egg_path = None
        easy_install.initialize_options(self)
        self.setup_path = None
        self.always_copy_from = '.'
        return

    def finalize_options(self):
        ei = self.get_finalized_command('egg_info')
        if ei.broken_egg_info:
            raise DistutilsError("Please rename %r to %r before using 'develop'" % (
             ei.egg_info, ei.broken_egg_info))
        self.args = [ei.egg_name]
        easy_install.finalize_options(self)
        self.package_index.scan(glob.glob('*.egg'))
        self.egg_link = os.path.join(self.install_dir, ei.egg_name + '.egg-link')
        self.egg_base = ei.egg_base
        if self.egg_path is None:
            self.egg_path = os.path.abspath(ei.egg_base)
        target = normalize_path(self.egg_base)
        if normalize_path(os.path.join(self.install_dir, self.egg_path)) != target:
            raise DistutilsOptionError('--egg-path must be a relative path from the install directory to ' + target)
        self.dist = Distribution(target, PathMetadata(target, os.path.abspath(ei.egg_info)), project_name=ei.egg_name)
        p = self.egg_base.replace(os.sep, '/')
        if p != os.curdir:
            p = '../' * (p.count('/') + 1)
        self.setup_path = p
        p = normalize_path(os.path.join(self.install_dir, self.egg_path, p))
        if p != normalize_path(os.curdir):
            raise DistutilsOptionError("Can't get a consistent path to setup script from installation directory", p, normalize_path(os.curdir))
        return

    def install_for_development(self):
        self.run_command('egg_info')
        self.reinitialize_command('build_ext', inplace=1)
        self.run_command('build_ext')
        self.install_site_py()
        if setuptools.bootstrap_install_from:
            self.easy_install(setuptools.bootstrap_install_from)
            setuptools.bootstrap_install_from = None
        log.info('Creating %s (link to %s)', self.egg_link, self.egg_base)
        if not self.dry_run:
            f = open(self.egg_link, 'w')
            f.write(self.egg_path + '\n' + self.setup_path)
            f.close()
        self.process_distribution(None, self.dist, not self.no_deps)
        return

    def uninstall_link(self):
        if os.path.exists(self.egg_link):
            log.info('Removing %s (link to %s)', self.egg_link, self.egg_base)
            contents = [ line.rstrip() for line in file(self.egg_link) ]
            if contents not in ([self.egg_path], [self.egg_path, self.setup_path]):
                log.warn('Link points to %s: uninstall aborted', contents)
                return
            if not self.dry_run:
                os.unlink(self.egg_link)
        if not self.dry_run:
            self.update_pth(self.dist)
        if self.distribution.scripts:
            log.warn('Note: you must uninstall or replace scripts manually!')

    def install_egg_scripts(self, dist):
        if dist is not self.dist:
            return easy_install.install_egg_scripts(self, dist)
        self.install_wrapper_scripts(dist)
        for script_name in self.distribution.scripts or []:
            script_path = os.path.abspath(convert_path(script_name))
            script_name = os.path.basename(script_path)
            f = open(script_path, 'rU')
            script_text = f.read()
            f.close()
            self.install_script(dist, script_name, script_text, script_path)