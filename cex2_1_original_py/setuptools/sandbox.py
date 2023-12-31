# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: setuptools\sandbox.pyc
# Compiled at: 2010-07-06 22:09:14
import os, sys, __builtin__, tempfile, operator, pkg_resources
_os = sys.modules[os.name]
_open = open
_file = file
from distutils.errors import DistutilsError
from pkg_resources import working_set
__all__ = [
 'AbstractSandbox', 'DirectorySandbox', 'SandboxViolation', 'run_setup']

def run_setup(setup_script, args):
    """Run a distutils setup script, sandboxed in its directory"""
    old_dir = os.getcwd()
    save_argv = sys.argv[:]
    save_path = sys.path[:]
    setup_dir = os.path.abspath(os.path.dirname(setup_script))
    temp_dir = os.path.join(setup_dir, 'temp')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    save_tmp = tempfile.tempdir
    save_modules = sys.modules.copy()
    pr_state = pkg_resources.__getstate__()
    try:
        tempfile.tempdir = temp_dir
        os.chdir(setup_dir)
        try:
            sys.argv[:] = [
             setup_script] + list(args)
            sys.path.insert(0, setup_dir)
            working_set.__init__()
            working_set.callbacks.append((lambda dist: dist.activate()))
            DirectorySandbox(setup_dir).run((lambda : execfile('setup.py', {'__file__': setup_script, '__name__': '__main__'})))
        except SystemExit as v:
            if v.args and v.args[0]:
                raise

    finally:
        pkg_resources.__setstate__(pr_state)
        sys.modules.update(save_modules)
        for key in list(sys.modules):
            if key not in save_modules:
                del sys.modules[key]

        os.chdir(old_dir)
        sys.path[:] = save_path
        sys.argv[:] = save_argv
        tempfile.tempdir = save_tmp


class AbstractSandbox:
    """Wrap 'os' module and 'open()' builtin for virtualizing setup scripts"""
    _active = False

    def __init__(self):
        self._attrs = [ name for name in dir(_os) if not name.startswith('_') and hasattr(self, name)
                      ]

    def _copy(self, source):
        for name in self._attrs:
            setattr(os, name, getattr(source, name))

    def run(self, func):
        """Run 'func' under os sandboxing"""
        try:
            self._copy(self)
            __builtin__.file = self._file
            __builtin__.open = self._open
            self._active = True
            return func()
        finally:
            self._active = False
            __builtin__.open = _file
            __builtin__.file = _open
            self._copy(_os)

    def _mk_dual_path_wrapper(name):
        original = getattr(_os, name)

        def wrap(self, src, dst, *args, **kw):
            if self._active:
                src, dst = self._remap_pair(name, src, dst, *args, **kw)
            return original(src, dst, *args, **kw)

        return wrap

    for name in ['rename', 'link', 'symlink']:
        if hasattr(_os, name):
            locals()[name] = _mk_dual_path_wrapper(name)

    def _mk_single_path_wrapper(name, original=None):
        original = original or getattr(_os, name)

        def wrap(self, path, *args, **kw):
            if self._active:
                path = self._remap_input(name, path, *args, **kw)
            return original(path, *args, **kw)

        return wrap

    _open = _mk_single_path_wrapper('open', _open)
    _file = _mk_single_path_wrapper('file', _file)
    for name in [
     'stat', 'listdir', 'chdir', 'open', 'chmod', 'chown', 'mkdir', 
     'remove', 
     'unlink', 'rmdir', 'utime', 'lchown', 'chroot', 'lstat', 
     'startfile', 
     'mkfifo', 'mknod', 'pathconf', 'access']:
        if hasattr(_os, name):
            locals()[name] = _mk_single_path_wrapper(name)

    def _mk_single_with_return(name):
        original = getattr(_os, name)

        def wrap(self, path, *args, **kw):
            if self._active:
                path = self._remap_input(name, path, *args, **kw)
                return self._remap_output(name, original(path, *args, **kw))
            return original(path, *args, **kw)

        return wrap

    for name in ['readlink', 'tempnam']:
        if hasattr(_os, name):
            locals()[name] = _mk_single_with_return(name)

    def _mk_query(name):
        original = getattr(_os, name)

        def wrap(self, *args, **kw):
            retval = original(*args, **kw)
            if self._active:
                return self._remap_output(name, retval)
            return retval

        return wrap

    for name in ['getcwd', 'tmpnam']:
        if hasattr(_os, name):
            locals()[name] = _mk_query(name)

    def _validate_path(self, path):
        """Called to remap or validate any path, whether input or output"""
        return path

    def _remap_input(self, operation, path, *args, **kw):
        """Called for path inputs"""
        return self._validate_path(path)

    def _remap_output(self, operation, path):
        """Called for path outputs"""
        return self._validate_path(path)

    def _remap_pair(self, operation, src, dst, *args, **kw):
        """Called for path pairs like rename, link, and symlink operations"""
        return (
         self._remap_input((operation + '-from'), src, *args, **kw),
         self._remap_input((operation + '-to'), dst, *args, **kw))


class DirectorySandbox(AbstractSandbox):
    """Restrict operations to a single subdirectory - pseudo-chroot"""
    write_ops = dict.fromkeys([
     'open', 'chmod', 'chown', 'mkdir', 'remove', 'unlink', 'rmdir', 
     'utime', 
     'lchown', 'chroot', 'mkfifo', 'mknod', 'tempnam'])

    def __init__(self, sandbox):
        self._sandbox = os.path.normcase(os.path.realpath(sandbox))
        self._prefix = os.path.join(self._sandbox, '')
        AbstractSandbox.__init__(self)

    def _violation(self, operation, *args, **kw):
        raise SandboxViolation(operation, args, kw)

    def _open(self, path, mode='r', *args, **kw):
        if mode not in ('r', 'rt', 'rb', 'rU', 'U') and not self._ok(path):
            self._violation('open', path, mode, *args, **kw)
        return _open(path, mode, *args, **kw)

    def tmpnam(self):
        self._violation('tmpnam')

    def _ok(self, path):
        active = self._active
        try:
            self._active = False
            realpath = os.path.normcase(os.path.realpath(path))
            if realpath == self._sandbox or realpath.startswith(self._prefix):
                return True
        finally:
            self._active = active

    def _remap_input(self, operation, path, *args, **kw):
        """Called for path inputs"""
        if operation in self.write_ops and not self._ok(path):
            self._violation(operation, os.path.realpath(path), *args, **kw)
        return path

    def _remap_pair(self, operation, src, dst, *args, **kw):
        """Called for path pairs like rename, link, and symlink operations"""
        if not self._ok(src) or not self._ok(dst):
            self._violation(operation, src, dst, *args, **kw)
        return (
         src, dst)

    def _file(self, path, mode='r', *args, **kw):
        if mode not in ('r', 'rt', 'rb', 'rU', 'U') and not self._ok(path):
            self._violation('file', path, mode, *args, **kw)
        return _file(path, mode, *args, **kw)

    def open(self, file, flags, mode=511):
        """Called for low-level os.open()"""
        if flags & WRITE_FLAGS and not self._ok(file):
            self._violation('os.open', file, flags, mode)
        return _os.open(file, flags, mode)


WRITE_FLAGS = reduce(operator.or_, [ getattr(_os, a, 0) for a in ('O_WRONLY O_RDWR O_APPEND O_CREAT O_TRUNC O_TEMPORARY').split()
                                   ])

class SandboxViolation(DistutilsError):
    """A setup script attempted to modify the filesystem outside the sandbox"""

    def __str__(self):
        return "SandboxViolation: %s%r %s\n\nThe package setup script has attempted to modify files on your system\nthat are not within the EasyInstall build area, and has been aborted.\n\nThis package cannot be safely installed by EasyInstall, and may not\nsupport alternate installation locations even if you run its setup\nscript by hand.  Please inform the package's author and the EasyInstall\nmaintainers to find out if a fix or workaround is available." % self.args