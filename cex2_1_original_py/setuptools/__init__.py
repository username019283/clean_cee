# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: setuptools\__init__.pyc
# Compiled at: 2010-07-06 22:09:14
"""Extensions to the 'distutils' for large or complex distributions"""
from setuptools.extension import Extension, Library
from setuptools.dist import Distribution, Feature, _get_unpatched
import distutils.core, setuptools.command
from setuptools.depends import Require
from distutils.core import Command as _Command
from distutils.util import convert_path
import os.path
__version__ = '0.6c11'
__all__ = [
 'setup', 'Distribution', 'Feature', 'Command', 'Extension', 'Require', 
 'find_packages']
bootstrap_install_from = None

def find_packages(where='.', exclude=()):
    """Return a list all Python packages found within directory 'where'

    'where' should be supplied as a "cross-platform" (i.e. URL-style) path; it
    will be converted to the appropriate local path syntax.  'exclude' is a
    sequence of package names to exclude; '*' can be used as a wildcard in the
    names, such that 'foo.*' will exclude all subpackages of 'foo' (but not
    'foo' itself).
    """
    out = []
    stack = [
     (
      convert_path(where), '')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if '.' not in name and os.path.isdir(fn) and os.path.isfile(os.path.join(fn, '__init__.py')):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))

    for pat in list(exclude) + ['ez_setup']:
        from fnmatch import fnmatchcase
        out = [ item for item in out if not fnmatchcase(item, pat) ]

    return out


setup = distutils.core.setup
_Command = _get_unpatched(_Command)

class Command(_Command):
    __doc__ = _Command.__doc__
    command_consumes_arguments = False

    def __init__(self, dist, **kw):
        _Command.__init__(self, dist)
        for k, v in kw.items():
            setattr(self, k, v)

    def reinitialize_command(self, command, reinit_subcommands=0, **kw):
        cmd = _Command.reinitialize_command(self, command, reinit_subcommands)
        for k, v in kw.items():
            setattr(cmd, k, v)

        return cmd


import distutils.core
distutils.core.Command = Command

def findall(dir=os.curdir):
    """Find all files under 'dir' and return the list of full filenames
    (relative to 'dir').
    """
    all_files = []
    for base, dirs, files in os.walk(dir):
        if base == os.curdir or base.startswith(os.curdir + os.sep):
            base = base[2:]
        if base:
            files = [ os.path.join(base, f) for f in files ]
        all_files.extend(filter(os.path.isfile, files))

    return all_files


import distutils.filelist
distutils.filelist.findall = findall