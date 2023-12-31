# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\cm.pyc
# Compiled at: 2012-11-08 06:38:04
"""
This module provides a large set of colormaps, functions for
registering new colormaps and for getting a colormap by name,
and a mixin class for adding color mapping functionality.

"""
from __future__ import print_function, division
import os, numpy as np
from numpy import ma
import matplotlib as mpl, matplotlib.colors as colors, matplotlib.cbook as cbook
from matplotlib._cm import datad
from matplotlib._cm import cubehelix
cmap_d = dict()

def _reverser(f):

    def freversed(x):
        return f(1 - x)

    return freversed


def revcmap(data):
    """Can only handle specification *data* in dictionary format."""
    data_r = {}
    for key, val in data.iteritems():
        if callable(val):
            valnew = _reverser(val)
        else:
            valnew = [ (1.0 - x, y1, y0) for x, y0, y1 in reversed(val) ]
        data_r[key] = valnew

    return data_r


def _reverse_cmap_spec(spec):
    """Reverses cmap specification *spec*, can handle both dict and tuple
    type specs."""
    if 'red' in spec:
        return revcmap(spec)
    else:
        revspec = list(reversed(spec))
        if len(revspec[0]) == 2:
            revspec = [ (1.0 - a, b) for a, b in revspec ]
        return revspec


def _generate_cmap(name, lutsize):
    """Generates the requested cmap from it's name *name*.  The lut size is
    *lutsize*."""
    spec = datad[name]
    if 'red' in spec:
        return colors.LinearSegmentedColormap(name, spec, lutsize)
    else:
        return colors.LinearSegmentedColormap.from_list(name, spec, lutsize)


LUTSIZE = mpl.rcParams['image.lut']
_cmapnames = datad.keys()
for cmapname in _cmapnames:
    spec = datad[cmapname]
    spec_reversed = _reverse_cmap_spec(spec)
    datad[cmapname + '_r'] = spec_reversed

for cmapname in datad.iterkeys():
    cmap_d[cmapname] = _generate_cmap(cmapname, LUTSIZE)

locals().update(cmap_d)

def register_cmap(name=None, cmap=None, data=None, lut=None):
    """
    Add a colormap to the set recognized by :func:`get_cmap`.

    It can be used in two ways::

        register_cmap(name='swirly', cmap=swirly_cmap)

        register_cmap(name='choppy', data=choppydata, lut=128)

    In the first case, *cmap* must be a :class:`colors.Colormap`
    instance.  The *name* is optional; if absent, the name will
    be the :attr:`name` attribute of the *cmap*.

    In the second case, the three arguments are passed to
    the :class:`colors.LinearSegmentedColormap` initializer,
    and the resulting colormap is registered.

    """
    if name is None:
        try:
            name = cmap.name
        except AttributeError:
            raise ValueError('Arguments must include a name or a Colormap')

    if not cbook.is_string_like(name):
        raise ValueError('Colormap name must be a string')
    if isinstance(cmap, colors.Colormap):
        cmap_d[name] = cmap
        return
    else:
        if lut is None:
            lut = mpl.rcParams['image.lut']
        cmap = colors.LinearSegmentedColormap(name, data, lut)
        cmap_d[name] = cmap
        return


def get_cmap(name=None, lut=None):
    """
    Get a colormap instance, defaulting to rc values if *name* is None.

    Colormaps added with :func:`register_cmap` take precedence over
    builtin colormaps.

    If *name* is a :class:`colors.Colormap` instance, it will be
    returned.

    If *lut* is not None it must be an integer giving the number of
    entries desired in the lookup table, and *name* must be a
    standard mpl colormap name with a corresponding data dictionary
    in *datad*.
    """
    if name is None:
        name = mpl.rcParams['image.cmap']
    if isinstance(name, colors.Colormap):
        return name
    else:
        if name in cmap_d:
            if lut is None:
                return cmap_d[name]
            if name in datad:
                return _generate_cmap(name, lut)
        raise ValueError('Colormap %s is not recognized' % name)
        return


class ScalarMappable:
    """
    This is a mixin class to support scalar -> RGBA mapping.  Handles
    normalization and colormapping
    """

    def __init__(self, norm=None, cmap=None):
        """
        *norm* is an instance of :class:`colors.Normalize` or one of
        its subclasses, used to map luminance to 0-1. *cmap* is a
        :mod:`cm` colormap instance, for example :data:`cm.jet`
        """
        self.callbacksSM = cbook.CallbackRegistry()
        if cmap is None:
            cmap = get_cmap()
        if norm is None:
            norm = colors.Normalize()
        self._A = None
        self.norm = norm
        self.cmap = get_cmap(cmap)
        self.colorbar = None
        self.update_dict = {'array': False}
        return

    def set_colorbar(self, im, ax):
        """set the colorbar image and axes associated with mappable"""
        self.colorbar = (
         im, ax)

    def to_rgba(self, x, alpha=None, bytes=False):
        """
        Return a normalized rgba array corresponding to *x*.

        In the normal case, *x* is a 1-D or 2-D sequence of scalars, and
        the corresponding ndarray of rgba values will be returned,
        based on the norm and colormap set for this ScalarMappable.

        There is one special case, for handling images that are already
        rgb or rgba, such as might have been read from an image file.
        If *x* is an ndarray with 3 dimensions,
        and the last dimension is either 3 or 4, then it will be
        treated as an rgb or rgba array, and no mapping will be done.
        If the last dimension is 3, the *alpha* kwarg (defaulting to 1)
        will be used to fill in the transparency.  If the last dimension
        is 4, the *alpha* kwarg is ignored; it does not
        replace the pre-existing alpha.  A ValueError will be raised
        if the third dimension is other than 3 or 4.

        In either case, if *bytes* is *False* (default), the rgba
        array will be floats in the 0-1 range; if it is *True*,
        the returned rgba array will be uint8 in the 0 to 255 range.

        Note: this method assumes the input is well-behaved; it does
        not check for anomalies such as *x* being a masked rgba
        array, or being an integer type other than uint8, or being
        a floating point rgba array with values outside the 0-1 range.
        """
        try:
            if x.ndim == 3:
                if x.shape[2] == 3:
                    if alpha is None:
                        alpha = 1
                    if x.dtype == np.uint8:
                        alpha = np.uint8(alpha * 255)
                    m, n = x.shape[:2]
                    xx = np.empty(shape=(m, n, 4), dtype=x.dtype)
                    xx[:, :, :3] = x
                    xx[:, :, 3] = alpha
                elif x.shape[2] == 4:
                    xx = x
                else:
                    raise ValueError('third dimension must be 3 or 4')
                if bytes and xx.dtype != np.uint8:
                    xx = (xx * 255).astype(np.uint8)
                if not bytes and xx.dtype == np.uint8:
                    xx = xx.astype(float) / 255
                return xx
        except AttributeError:
            pass

        x = ma.asarray(x)
        x = self.norm(x)
        x = self.cmap(x, alpha=alpha, bytes=bytes)
        return x

    def set_array(self, A):
        """Set the image array from numpy array *A*"""
        self._A = A
        self.update_dict['array'] = True

    def get_array(self):
        """Return the array"""
        return self._A

    def get_cmap(self):
        """return the colormap"""
        return self.cmap

    def get_clim(self):
        """return the min, max of the color limits for image scaling"""
        return (
         self.norm.vmin, self.norm.vmax)

    def set_clim(self, vmin=None, vmax=None):
        """
        set the norm limits for image scaling; if *vmin* is a length2
        sequence, interpret it as ``(vmin, vmax)`` which is used to
        support setp

        ACCEPTS: a length 2 sequence of floats
        """
        if vmin is not None and vmax is None and cbook.iterable(vmin) and len(vmin) == 2:
            vmin, vmax = vmin
        if vmin is not None:
            self.norm.vmin = vmin
        if vmax is not None:
            self.norm.vmax = vmax
        self.changed()
        return

    def set_cmap(self, cmap):
        """
        set the colormap for luminance data

        ACCEPTS: a colormap or registered colormap name
        """
        cmap = get_cmap(cmap)
        self.cmap = cmap
        self.changed()

    def set_norm(self, norm):
        """set the normalization instance"""
        if norm is None:
            norm = colors.Normalize()
        self.norm = norm
        self.changed()
        return

    def autoscale(self):
        """
        Autoscale the scalar limits on the norm instance using the
        current array
        """
        if self._A is None:
            raise TypeError('You must first set_array for mappable')
        self.norm.autoscale(self._A)
        self.changed()
        return

    def autoscale_None(self):
        """
        Autoscale the scalar limits on the norm instance using the
        current array, changing only limits that are None
        """
        if self._A is None:
            raise TypeError('You must first set_array for mappable')
        self.norm.autoscale_None(self._A)
        self.changed()
        return

    def add_checker(self, checker):
        """
        Add an entry to a dictionary of boolean flags
        that are set to True when the mappable is changed.
        """
        self.update_dict[checker] = False

    def check_update(self, checker):
        """
        If mappable has changed since the last check,
        return True; else return False
        """
        if self.update_dict[checker]:
            self.update_dict[checker] = False
            return True
        return False

    def changed(self):
        """
        Call this whenever the mappable is changed to notify all the
        callbackSM listeners to the 'changed' signal
        """
        self.callbacksSM.process('changed', self)
        for key in self.update_dict:
            self.update_dict[key] = True