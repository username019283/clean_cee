# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\setupscons.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
from os.path import join as pjoin

def configuration(parent_package='', top_path=None, setup_name='setupscons.py'):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.misc_util import scons_generate_config_py
    pkgname = 'scipy'
    config = Configuration(pkgname, parent_package, top_path, setup_name='setupscons.py')
    config.add_subpackage('cluster')
    config.add_subpackage('constants')
    config.add_subpackage('fftpack')
    config.add_subpackage('integrate')
    config.add_subpackage('interpolate')
    config.add_subpackage('io')
    config.add_subpackage('lib')
    config.add_subpackage('linalg')
    config.add_subpackage('misc')
    config.add_subpackage('odr')
    config.add_subpackage('optimize')
    config.add_subpackage('signal')
    config.add_subpackage('sparse')
    config.add_subpackage('spatial')
    config.add_subpackage('special')
    config.add_subpackage('stats')
    config.add_subpackage('ndimage')
    config.add_subpackage('weave')

    def add_config(*args, **kw):
        if kw['scons_cmd'].inplace:
            target = pjoin(kw['pkg_name'], '__config__.py')
        else:
            target = pjoin(kw['scons_cmd'].build_lib, kw['pkg_name'], '__config__.py')
        scons_generate_config_py(target)

    config.add_sconscript(None, post_hook=add_config)
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())