# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\io\arff\__init__.pyc
# Compiled at: 2013-02-16 13:27:30
'''
Module to read ARFF files, which are the standard data format for WEKA.

ARFF is a text file format which support numerical, string and data values.
The format can also represent missing data and sparse data.

See the `WEKA website
<http://weka.wikispaces.com/ARFF>`_
for more details about arff format and available datasets.

Examples
--------

>>> from scipy.io import arff
>>> from cStringIO import StringIO
>>> content = """
... @relation foo
... @attribute width  numeric
... @attribute height numeric
... @attribute color  {red,green,blue,yellow,black}
... @data
... 5.0,3.25,blue
... 4.5,3.75,green
... 3.0,4.00,red
... """
>>> f = StringIO(content)
>>> data, meta = arff.loadarff(f)
>>> data
array([(5.0, 3.25, 'blue'), (4.5, 3.75, 'green'), (3.0, 4.0, 'red')],
      dtype=[('width', '<f8'), ('height', '<f8'), ('color', '|S6')])
>>> meta
Dataset: foo
        width's type is numeric
        height's type is numeric
        color's type is nominal, range is ('red', 'green', 'blue', 'yellow', 'black')

'''
from __future__ import division, print_function, absolute_import
from ...arffread import *
from . import arffread
__all__ = arffread.__all__
from numpy.testing import Tester
test = Tester().test