# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\ndimage\io.pyc
# Compiled at: 2013-02-16 13:27:30
from __future__ import division, print_function, absolute_import
__all__ = ['imread']
from numpy import array

def imread(fname, flatten=False):
    """
    Load an image from file.

    Parameters
    ----------
    fname : str
        Image file name, e.g. ``test.jpg``.
    flatten : bool, optional
        If true, convert the output to grey-scale. Default is False.

    Returns
    -------
    img_array : ndarray
        The different colour bands/channels are stored in the
        third dimension, such that a grey-image is MxN, an
        RGB-image MxNx3 and an RGBA-image MxNx4.

    Raises
    ------
    ImportError
        If the Python Imaging Library (PIL) can not be imported.

    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError('Could not import the Python Imaging Library (PIL) required to load image files.  Please refer to http://pypi.python.org/pypi/PIL/ for installation instructions.')

    fp = open(fname, 'rb')
    im = Image.open(fp)
    if flatten:
        im = im.convert('F')
    result = array(im)
    fp.close()
    return result