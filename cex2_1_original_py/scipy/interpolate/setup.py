# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\interpolate\setup.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
from os.path import join

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('interpolate', parent_package, top_path)
    config.add_library('fitpack', sources=[
     join('fitpack', '*.f')])
    config.add_extension('interpnd', sources=[
     'interpnd.c'])
    config.add_extension('_fitpack', sources=[
     'src/_fitpackmodule.c'], libraries=[
     'fitpack'], depends=[
     'src/__fitpack.h', 'src/multipack.h'])
    config.add_extension('dfitpack', sources=[
     'src/fitpack.pyf'], libraries=[
     'fitpack'])
    config.add_extension('_interpolate', sources=[
     'src/_interpolate.cpp'], include_dirs=[
     'src'], depends=[
     'src/interpolate.h'])
    config.add_data_dir('tests')
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())