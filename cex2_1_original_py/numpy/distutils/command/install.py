# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\command\install.pyc
# Compiled at: 2013-04-07 07:04:04
import sys
if 'setuptools' in sys.modules:
    import setuptools.command.install as old_install_mod
    have_setuptools = True
else:
    import distutils.command.install as old_install_mod
    have_setuptools = False
old_install = old_install_mod.install
from distutils.file_util import write_file

class install(old_install):
    sub_commands = old_install.sub_commands + [
     (
      'install_clib', (lambda x: True))]

    def finalize_options(self):
        old_install.finalize_options(self)
        self.install_lib = self.install_libbase

    def setuptools_run(self):
        """ The setuptools version of the .run() method.

        We must pull in the entire code so we can override the level used in the
        _getframe() call since we wrap this call by one more level.
        """
        if self.old_and_unmanageable or self.single_version_externally_managed:
            return old_install_mod._install.run(self)
        caller = sys._getframe(3)
        caller_module = caller.f_globals.get('__name__', '')
        caller_name = caller.f_code.co_name
        if caller_module != 'distutils.dist' or caller_name != 'run_commands':
            old_install_mod._install.run(self)
        else:
            self.do_egg_install()

    def run(self):
        if not have_setuptools:
            r = old_install.run(self)
        else:
            r = self.setuptools_run()
        if self.record:
            f = open(self.record, 'r')
            lines = []
            need_rewrite = False
            for l in f.readlines():
                l = l.rstrip()
                if ' ' in l:
                    need_rewrite = True
                    l = '"%s"' % l
                lines.append(l)

            f.close()
            if need_rewrite:
                self.execute(write_file, (
                 self.record, lines), "re-writing list of installed files to '%s'" % self.record)
        return r