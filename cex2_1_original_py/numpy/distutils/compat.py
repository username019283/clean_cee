# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\compat.pyc
# Compiled at: 2013-04-07 07:04:04
"""Small modules to cope with python 2 vs 3 incompatibilities inside
numpy.distutils
"""
import sys

def get_exception():
    return sys.exc_info()[1]