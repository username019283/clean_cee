# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\sparsetools\setup.pyc
# Compiled at: 2013-02-16 13:27:32
from __future__ import division, print_function, absolute_import

def configuration(parent_package='', top_path=None):
    import numpy
    from numpy.distutils.misc_util import Configuration
    config = Configuration('sparsetools', parent_package, top_path)
    for fmt in ['csr', 'csc', 'coo', 'bsr', 'dia', 'csgraph']:
        sources = [fmt + '_wrap.cxx']
        depends = [fmt + '.h']
        config.add_extension('_' + fmt, sources=sources, define_macros=[
         ('__STDC_FORMAT_MACROS', 1)], depends=depends)

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())