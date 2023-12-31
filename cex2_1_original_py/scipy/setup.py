# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\setup.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('scipy', parent_package, top_path)
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
    config.add_subpackage('_build_utils')
    config.make_config_py()
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())