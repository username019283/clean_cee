# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\colors.pyc
# Compiled at: 2012-11-08 06:38:04
"""
A module for converting numbers or color arguments to *RGB* or *RGBA*

*RGB* and *RGBA* are sequences of, respectively, 3 or 4 floats in the
range 0-1.

This module includes functions and classes for color specification
conversions, and for mapping numbers to colors in a 1-D array of colors called
a colormap. Colormapping typically involves two steps: a data array is first
mapped onto the range 0-1 using an instance of :class:`Normalize` or of a
subclass; then this number in the 0-1 range is mapped to a color using an
instance of a subclass of :class:`Colormap`.  Two are provided here:
:class:`LinearSegmentedColormap`, which is used to generate all the built-in
colormap instances, but is also useful for making custom colormaps, and
:class:`ListedColormap`, which is used for generating a custom colormap from a
list of color specifications.

The module also provides a single instance, *colorConverter*, of the
:class:`ColorConverter` class providing methods for converting single
color specifications or sequences of them to *RGB* or *RGBA*.

Commands which take color arguments can use several formats to specify
the colors.  For the basic builtin colors, you can use a single letter

    - b: blue
    - g: green
    - r: red
    - c: cyan
    - m: magenta
    - y: yellow
    - k: black
    - w: white

Gray shades can be given as a string encoding a float in the 0-1
range, e.g.::

    color = '0.75'

For a greater range of colors, you have two options.  You can specify
the color using an html hex string, as in::

      color = '#eeefff'

or you can pass an *R* , *G* , *B* tuple, where each of *R* , *G* , *B*
are in the range [0,1].

Finally, legal html names for colors, like 'red', 'burlywood' and
'chartreuse' are supported.
"""
from __future__ import print_function, division
import re, numpy as np
from numpy import ma
import matplotlib.cbook as cbook
parts = np.__version__.split('.')
NP_MAJOR, NP_MINOR = map(int, parts[:2])
NP_CLIP_OUT = NP_MAJOR >= 1 and NP_MINOR >= 2
cnames = {'aliceblue': '#F0F8FF', 
   'antiquewhite': '#FAEBD7', 
   'aqua': '#00FFFF', 
   'aquamarine': '#7FFFD4', 
   'azure': '#F0FFFF', 
   'beige': '#F5F5DC', 
   'bisque': '#FFE4C4', 
   'black': '#000000', 
   'blanchedalmond': '#FFEBCD', 
   'blue': '#0000FF', 
   'blueviolet': '#8A2BE2', 
   'brown': '#A52A2A', 
   'burlywood': '#DEB887', 
   'cadetblue': '#5F9EA0', 
   'chartreuse': '#7FFF00', 
   'chocolate': '#D2691E', 
   'coral': '#FF7F50', 
   'cornflowerblue': '#6495ED', 
   'cornsilk': '#FFF8DC', 
   'crimson': '#DC143C', 
   'cyan': '#00FFFF', 
   'darkblue': '#00008B', 
   'darkcyan': '#008B8B', 
   'darkgoldenrod': '#B8860B', 
   'darkgray': '#A9A9A9', 
   'darkgreen': '#006400', 
   'darkkhaki': '#BDB76B', 
   'darkmagenta': '#8B008B', 
   'darkolivegreen': '#556B2F', 
   'darkorange': '#FF8C00', 
   'darkorchid': '#9932CC', 
   'darkred': '#8B0000', 
   'darksalmon': '#E9967A', 
   'darkseagreen': '#8FBC8F', 
   'darkslateblue': '#483D8B', 
   'darkslategray': '#2F4F4F', 
   'darkturquoise': '#00CED1', 
   'darkviolet': '#9400D3', 
   'deeppink': '#FF1493', 
   'deepskyblue': '#00BFFF', 
   'dimgray': '#696969', 
   'dodgerblue': '#1E90FF', 
   'firebrick': '#B22222', 
   'floralwhite': '#FFFAF0', 
   'forestgreen': '#228B22', 
   'fuchsia': '#FF00FF', 
   'gainsboro': '#DCDCDC', 
   'ghostwhite': '#F8F8FF', 
   'gold': '#FFD700', 
   'goldenrod': '#DAA520', 
   'gray': '#808080', 
   'green': '#008000', 
   'greenyellow': '#ADFF2F', 
   'honeydew': '#F0FFF0', 
   'hotpink': '#FF69B4', 
   'indianred': '#CD5C5C', 
   'indigo': '#4B0082', 
   'ivory': '#FFFFF0', 
   'khaki': '#F0E68C', 
   'lavender': '#E6E6FA', 
   'lavenderblush': '#FFF0F5', 
   'lawngreen': '#7CFC00', 
   'lemonchiffon': '#FFFACD', 
   'lightblue': '#ADD8E6', 
   'lightcoral': '#F08080', 
   'lightcyan': '#E0FFFF', 
   'lightgoldenrodyellow': '#FAFAD2', 
   'lightgreen': '#90EE90', 
   'lightgray': '#D3D3D3', 
   'lightpink': '#FFB6C1', 
   'lightsalmon': '#FFA07A', 
   'lightseagreen': '#20B2AA', 
   'lightskyblue': '#87CEFA', 
   'lightslategray': '#778899', 
   'lightsteelblue': '#B0C4DE', 
   'lightyellow': '#FFFFE0', 
   'lime': '#00FF00', 
   'limegreen': '#32CD32', 
   'linen': '#FAF0E6', 
   'magenta': '#FF00FF', 
   'maroon': '#800000', 
   'mediumaquamarine': '#66CDAA', 
   'mediumblue': '#0000CD', 
   'mediumorchid': '#BA55D3', 
   'mediumpurple': '#9370DB', 
   'mediumseagreen': '#3CB371', 
   'mediumslateblue': '#7B68EE', 
   'mediumspringgreen': '#00FA9A', 
   'mediumturquoise': '#48D1CC', 
   'mediumvioletred': '#C71585', 
   'midnightblue': '#191970', 
   'mintcream': '#F5FFFA', 
   'mistyrose': '#FFE4E1', 
   'moccasin': '#FFE4B5', 
   'navajowhite': '#FFDEAD', 
   'navy': '#000080', 
   'oldlace': '#FDF5E6', 
   'olive': '#808000', 
   'olivedrab': '#6B8E23', 
   'orange': '#FFA500', 
   'orangered': '#FF4500', 
   'orchid': '#DA70D6', 
   'palegoldenrod': '#EEE8AA', 
   'palegreen': '#98FB98', 
   'palevioletred': '#AFEEEE', 
   'papayawhip': '#FFEFD5', 
   'peachpuff': '#FFDAB9', 
   'peru': '#CD853F', 
   'pink': '#FFC0CB', 
   'plum': '#DDA0DD', 
   'powderblue': '#B0E0E6', 
   'purple': '#800080', 
   'red': '#FF0000', 
   'rosybrown': '#BC8F8F', 
   'royalblue': '#4169E1', 
   'saddlebrown': '#8B4513', 
   'salmon': '#FA8072', 
   'sandybrown': '#FAA460', 
   'seagreen': '#2E8B57', 
   'seashell': '#FFF5EE', 
   'sienna': '#A0522D', 
   'silver': '#C0C0C0', 
   'skyblue': '#87CEEB', 
   'slateblue': '#6A5ACD', 
   'slategray': '#708090', 
   'snow': '#FFFAFA', 
   'springgreen': '#00FF7F', 
   'steelblue': '#4682B4', 
   'tan': '#D2B48C', 
   'teal': '#008080', 
   'thistle': '#D8BFD8', 
   'tomato': '#FF6347', 
   'turquoise': '#40E0D0', 
   'violet': '#EE82EE', 
   'wheat': '#F5DEB3', 
   'white': '#FFFFFF', 
   'whitesmoke': '#F5F5F5', 
   'yellow': '#FFFF00', 
   'yellowgreen': '#9ACD32'}
for k, v in cnames.items():
    if k.find('gray') >= 0:
        k = k.replace('gray', 'grey')
        cnames[k] = v

def is_color_like(c):
    """Return *True* if *c* can be converted to *RGB*"""
    try:
        colorConverter.to_rgb(c)
        return True
    except ValueError:
        return False


def rgb2hex(rgb):
    """Given an rgb or rgba sequence of 0-1 floats, return the hex string"""
    return '#%02x%02x%02x' % tuple([ np.round(val * 255) for val in rgb[:3] ])


hexColorPattern = re.compile('\\A#[a-fA-F0-9]{6}\\Z')

def hex2color(s):
    """
    Take a hex string *s* and return the corresponding rgb 3-tuple
    Example: #efefef -> (0.93725, 0.93725, 0.93725)
    """
    if not isinstance(s, basestring):
        raise TypeError('hex2color requires a string argument')
    if hexColorPattern.match(s) is None:
        raise ValueError('invalid hex color string "%s"' % s)
    return tuple([ int(n, 16) / 255.0 for n in (s[1:3], s[3:5], s[5:7]) ])


class ColorConverter(object):
    """
    Provides methods for converting color specifications to *RGB* or *RGBA*

    Caching is used for more efficient conversion upon repeated calls
    with the same argument.

    Ordinarily only the single instance instantiated in this module,
    *colorConverter*, is needed.
    """
    colors = {'b': (0.0, 0.0, 1.0), 
       'g': (0.0, 0.5, 0.0), 
       'r': (1.0, 0.0, 0.0), 
       'c': (0.0, 0.75, 0.75), 
       'm': (0.75, 0, 0.75), 
       'y': (0.75, 0.75, 0), 
       'k': (0.0, 0.0, 0.0), 
       'w': (1.0, 1.0, 1.0)}
    cache = {}

    def to_rgb(self, arg):
        """
        Returns an *RGB* tuple of three floats from 0-1.

        *arg* can be an *RGB* or *RGBA* sequence or a string in any of
        several forms:

            1) a letter from the set 'rgbcmykw'
            2) a hex color string, like '#00FFFF'
            3) a standard name, like 'aqua'
            4) a float, like '0.4', indicating gray on a 0-1 scale

        if *arg* is *RGBA*, the *A* will simply be discarded.
        """
        try:
            return self.cache[arg]
        except KeyError:
            pass
        except TypeError:
            arg = tuple(arg)
            try:
                return self.cache[arg]
            except KeyError:
                pass
            except TypeError:
                raise ValueError('to_rgb: arg "%s" is unhashable even inside a tuple' % (
                 str(arg),))

        try:
            if cbook.is_string_like(arg):
                argl = arg.lower()
                color = self.colors.get(argl, None)
                if color is None:
                    str1 = cnames.get(argl, argl)
                    if str1.startswith('#'):
                        color = hex2color(str1)
                    else:
                        fl = float(argl)
                        if fl < 0 or fl > 1:
                            raise ValueError('gray (string) must be in range 0-1')
                        color = tuple([fl] * 3)
            elif cbook.iterable(arg):
                if len(arg) > 4 or len(arg) < 3:
                    raise ValueError('sequence length is %d; must be 3 or 4' % len(arg))
                color = tuple(arg[:3])
                if [ x for x in color if float(x) < 0 or x > 1 ]:
                    raise ValueError('number in rbg sequence outside 0-1 range')
            else:
                raise ValueError('cannot convert argument to rgb sequence')
            self.cache[arg] = color
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError('to_rgb: Invalid rgb arg "%s"\n%s' % (str(arg), exc))

        return color

    def to_rgba(self, arg, alpha=None):
        """
        Returns an *RGBA* tuple of four floats from 0-1.

        For acceptable values of *arg*, see :meth:`to_rgb`.
        In addition, if *arg* is "none" (case-insensitive),
        then (0,0,0,0) will be returned.
        If *arg* is an *RGBA* sequence and *alpha* is not *None*,
        *alpha* will replace the original *A*.
        """
        try:
            if arg.lower() == 'none':
                return (0.0, 0.0, 0.0, 0.0)
        except AttributeError:
            pass

        try:
            if not cbook.is_string_like(arg) and cbook.iterable(arg):
                if len(arg) == 4:
                    if [ x for x in arg if float(x) < 0 or x > 1 ]:
                        raise ValueError('number in rbga sequence outside 0-1 range')
                    if alpha is None:
                        return tuple(arg)
                    if alpha < 0.0 or alpha > 1.0:
                        raise ValueError('alpha must be in range 0-1')
                    return (arg[0], arg[1], arg[2], alpha)
                r, g, b = arg[:3]
                if [ x for x in (r, g, b) if float(x) < 0 or x > 1 ]:
                    raise ValueError('number in rbg sequence outside 0-1 range')
            else:
                r, g, b = self.to_rgb(arg)
            if alpha is None:
                alpha = 1.0
            return (
             r, g, b, alpha)
        except (TypeError, ValueError) as exc:
            raise ValueError('to_rgba: Invalid rgba arg "%s"\n%s' % (str(arg), exc))

        return

    def to_rgba_array(self, c, alpha=None):
        """
        Returns a numpy array of *RGBA* tuples.

        Accepts a single mpl color spec or a sequence of specs.

        Special case to handle "no color": if *c* is "none" (case-insensitive),
        then an empty array will be returned.  Same for an empty list.
        """
        try:
            nc = len(c)
        except TypeError:
            raise ValueError('Cannot convert argument type %s to rgba array' % type(c))

        try:
            if nc == 0 or c.lower() == 'none':
                return np.zeros((0, 4), dtype=np.float)
        except AttributeError:
            pass

        try:
            return np.array([self.to_rgba(c, alpha)], dtype=np.float)
        except ValueError:
            if isinstance(c, np.ndarray):
                if c.ndim != 2 and c.dtype.kind not in 'SU':
                    raise ValueError('Color array must be two-dimensional')
                if c.ndim == 2 and c.shape[1] == 4 and c.dtype.kind == 'f':
                    if (c.ravel() > 1).any() or (c.ravel() < 0).any():
                        raise ValueError('number in rgba sequence is outside 0-1 range')
                    result = np.asarray(c, np.float)
                    if alpha is not None:
                        if alpha > 1 or alpha < 0:
                            raise ValueError('alpha must be in 0-1 range')
                        result[:, 3] = alpha
                    return result
            result = np.zeros((nc, 4), dtype=np.float)
            for i, cc in enumerate(c):
                result[i] = self.to_rgba(cc, alpha)

            return result

        return


colorConverter = ColorConverter()

def makeMappingArray(N, data, gamma=1.0):
    """Create an *N* -element 1-d lookup table

    *data* represented by a list of x,y0,y1 mapping correspondences.
    Each element in this list represents how a value between 0 and 1
    (inclusive) represented by x is mapped to a corresponding value
    between 0 and 1 (inclusive). The two values of y are to allow
    for discontinuous mapping functions (say as might be found in a
    sawtooth) where y0 represents the value of y for values of x
    <= to that given, and y1 is the value to be used for x > than
    that given). The list must start with x=0, end with x=1, and
    all values of x must be in increasing order. Values between
    the given mapping points are determined by simple linear interpolation.

    Alternatively, data can be a function mapping values between 0 - 1
    to 0 - 1.

    The function returns an array "result" where ``result[x*(N-1)]``
    gives the closest value for values of x between 0 and 1.
    """
    if callable(data):
        xind = np.linspace(0, 1, N) ** gamma
        lut = np.clip(np.array(data(xind), dtype=np.float), 0, 1)
        return lut
    try:
        adata = np.array(data)
    except:
        raise TypeError('data must be convertable to an array')

    shape = adata.shape
    if len(shape) != 2 and shape[1] != 3:
        raise ValueError('data must be nx3 format')
    x = adata[:, 0]
    y0 = adata[:, 1]
    y1 = adata[:, 2]
    if x[0] != 0.0 or x[-1] != 1.0:
        raise ValueError('data mapping points must start with x=0. and end with x=1')
    if np.sometrue(np.sort(x) - x):
        raise ValueError('data mapping points must have x in increasing order')
    x = x * (N - 1)
    lut = np.zeros((N,), np.float)
    xind = (N - 1) * np.linspace(0, 1, N) ** gamma
    ind = np.searchsorted(x, xind)[1:-1]
    lut[1:(-1)] = (xind[1:-1] - x[ind - 1]) / (x[ind] - x[ind - 1]) * (y0[ind] - y1[ind - 1]) + y1[ind - 1]
    lut[0] = y1[0]
    lut[-1] = y0[-1]
    np.clip(lut, 0.0, 1.0)
    return lut


class Colormap(object):
    """Base class for all scalar to rgb mappings

        Important methods:

            * :meth:`set_bad`
            * :meth:`set_under`
            * :meth:`set_over`
    """

    def __init__(self, name, N=256):
        """
        Public class attributes:
        :attr:`N` : number of rgb quantization levels
        :attr:`name` : name of colormap

        """
        self.name = name
        self.N = N
        self._rgba_bad = (0.0, 0.0, 0.0, 0.0)
        self._rgba_under = None
        self._rgba_over = None
        self._i_under = N
        self._i_over = N + 1
        self._i_bad = N + 2
        self._isinit = False
        return

    def __call__(self, X, alpha=None, bytes=False):
        """
        *X* is either a scalar or an array (of any dimension).
        If scalar, a tuple of rgba values is returned, otherwise
        an array with the new shape = oldshape+(4,). If the X-values
        are integers, then they are used as indices into the array.
        If they are floating point, then they must be in the
        interval (0.0, 1.0).
        Alpha must be a scalar between 0 and 1, or None.
        If bytes is False, the rgba values will be floats on a
        0-1 scale; if True, they will be uint8, 0-255.
        """
        if not self._isinit:
            self._init()
        mask_bad = None
        if not cbook.iterable(X):
            vtype = 'scalar'
            xa = np.array([X])
        else:
            vtype = 'array'
            xma = ma.array(X, copy=True)
            mask_bad = xma.mask
            xa = xma.filled()
            del xma
        if not xa.dtype.isnative:
            xa = xa.byteswap().newbyteorder()
        if xa.dtype.kind == 'f':
            vals = np.array([1, 0], dtype=xa.dtype)
            almost_one = np.nextafter(*vals)
            cbook._putmask(xa, xa == 1.0, almost_one)
            xa *= self.N
            if NP_CLIP_OUT:
                np.clip(xa, -1, self.N, out=xa)
            else:
                xa = np.clip(xa, -1, self.N)
            cbook._putmask(xa, xa < 0.0, -1)
            xa = xa.astype(int)
        cbook._putmask(xa, xa > self.N - 1, self._i_over)
        cbook._putmask(xa, xa < 0, self._i_under)
        if mask_bad is not None:
            if mask_bad.shape == xa.shape:
                cbook._putmask(xa, mask_bad, self._i_bad)
            elif mask_bad:
                xa.fill(self._i_bad)
        if bytes:
            lut = (self._lut * 255).astype(np.uint8)
        else:
            lut = self._lut.copy()
        if alpha is not None:
            alpha = min(alpha, 1.0)
            alpha = max(alpha, 0.0)
            if bytes:
                alpha = int(alpha * 255)
            if (lut[-1] == 0).all():
                lut[:-1, -1] = alpha
            else:
                lut[:, -1] = alpha
        rgba = np.empty(shape=xa.shape + (4, ), dtype=lut.dtype)
        lut.take(xa, axis=0, mode='clip', out=rgba)
        if vtype == 'scalar':
            rgba = tuple(rgba[0, :])
        return rgba

    def set_bad(self, color='k', alpha=None):
        """Set color to be used for masked values.
        """
        self._rgba_bad = colorConverter.to_rgba(color, alpha)
        if self._isinit:
            self._set_extremes()

    def set_under(self, color='k', alpha=None):
        """Set color to be used for low out-of-range values.
           Requires norm.clip = False
        """
        self._rgba_under = colorConverter.to_rgba(color, alpha)
        if self._isinit:
            self._set_extremes()

    def set_over(self, color='k', alpha=None):
        """Set color to be used for high out-of-range values.
           Requires norm.clip = False
        """
        self._rgba_over = colorConverter.to_rgba(color, alpha)
        if self._isinit:
            self._set_extremes()

    def _set_extremes(self):
        if self._rgba_under:
            self._lut[self._i_under] = self._rgba_under
        else:
            self._lut[self._i_under] = self._lut[0]
        if self._rgba_over:
            self._lut[self._i_over] = self._rgba_over
        else:
            self._lut[self._i_over] = self._lut[self.N - 1]
        self._lut[self._i_bad] = self._rgba_bad

    def _init(self):
        """Generate the lookup table, self._lut"""
        raise NotImplementedError('Abstract class only')

    def is_gray(self):
        if not self._isinit:
            self._init()
        return np.alltrue(self._lut[:, 0] == self._lut[:, 1]) and np.alltrue(self._lut[:, 0] == self._lut[:, 2])


class LinearSegmentedColormap(Colormap):
    """Colormap objects based on lookup tables using linear segments.

    The lookup table is generated using linear interpolation for each
    primary color, with the 0-1 domain divided into any number of
    segments.
    """

    def __init__(self, name, segmentdata, N=256, gamma=1.0):
        """Create color map from linear mapping segments

        segmentdata argument is a dictionary with a red, green and blue
        entries. Each entry should be a list of *x*, *y0*, *y1* tuples,
        forming rows in a table. Entries for alpha are optional.

        Example: suppose you want red to increase from 0 to 1 over
        the bottom half, green to do the same over the middle half,
        and blue over the top half.  Then you would use::

            cdict = {'red':   [(0.0,  0.0, 0.0),
                               (0.5,  1.0, 1.0),
                               (1.0,  1.0, 1.0)],

                     'green': [(0.0,  0.0, 0.0),
                               (0.25, 0.0, 0.0),
                               (0.75, 1.0, 1.0),
                               (1.0,  1.0, 1.0)],

                     'blue':  [(0.0,  0.0, 0.0),
                               (0.5,  0.0, 0.0),
                               (1.0,  1.0, 1.0)]}

        Each row in the table for a given color is a sequence of
        *x*, *y0*, *y1* tuples.  In each sequence, *x* must increase
        monotonically from 0 to 1.  For any input value *z* falling
        between *x[i]* and *x[i+1]*, the output value of a given color
        will be linearly interpolated between *y1[i]* and *y0[i+1]*::

            row i:   x  y0  y1
                           /
                          /
            row i+1: x  y0  y1

        Hence y0 in the first row and y1 in the last row are never used.

        .. seealso::

               :meth:`LinearSegmentedColormap.from_list`
               Static method; factory function for generating a
               smoothly-varying LinearSegmentedColormap.

               :func:`makeMappingArray`
               For information about making a mapping array.
        """
        self.monochrome = False
        Colormap.__init__(self, name, N)
        self._segmentdata = segmentdata
        self._gamma = gamma

    def _init(self):
        self._lut = np.ones((self.N + 3, 4), np.float)
        self._lut[:-3, 0] = makeMappingArray(self.N, self._segmentdata['red'], self._gamma)
        self._lut[:-3, 1] = makeMappingArray(self.N, self._segmentdata['green'], self._gamma)
        self._lut[:-3, 2] = makeMappingArray(self.N, self._segmentdata['blue'], self._gamma)
        if 'alpha' in self._segmentdata:
            self._lut[:-3, 3] = makeMappingArray(self.N, self._segmentdata['alpha'], 1)
        self._isinit = True
        self._set_extremes()

    def set_gamma(self, gamma):
        """
        Set a new gamma value and regenerate color map.
        """
        self._gamma = gamma
        self._init()

    @staticmethod
    def from_list(name, colors, N=256, gamma=1.0):
        """
        Make a linear segmented colormap with *name* from a sequence
        of *colors* which evenly transitions from colors[0] at val=0
        to colors[-1] at val=1.  *N* is the number of rgb quantization
        levels.
        Alternatively, a list of (value, color) tuples can be given
        to divide the range unevenly.
        """
        if not cbook.iterable(colors):
            raise ValueError('colors must be iterable')
        if cbook.iterable(colors[0]) and len(colors[0]) == 2 and not cbook.is_string_like(colors[0]):
            vals, colors = zip(*colors)
        else:
            vals = np.linspace(0.0, 1.0, len(colors))
        cdict = dict(red=[], green=[], blue=[], alpha=[])
        for val, color in zip(vals, colors):
            r, g, b, a = colorConverter.to_rgba(color)
            cdict['red'].append((val, r, r))
            cdict['green'].append((val, g, g))
            cdict['blue'].append((val, b, b))
            cdict['alpha'].append((val, a, a))

        return LinearSegmentedColormap(name, cdict, N, gamma)


class ListedColormap(Colormap):
    """Colormap object generated from a list of colors.

    This may be most useful when indexing directly into a colormap,
    but it can also be used to generate special colormaps for ordinary
    mapping.
    """

    def __init__(self, colors, name='from_list', N=None):
        """
        Make a colormap from a list of colors.

        *colors*
            a list of matplotlib color specifications,
            or an equivalent Nx3  or Nx4 floating point array
            (*N* rgb or rgba values)
        *name*
            a string to identify the colormap
        *N*
            the number of entries in the map.  The default is *None*,
            in which case there is one colormap entry for each
            element in the list of colors.  If::

                N < len(colors)

            the list will be truncated at *N*.  If::

                N > len(colors)

            the list will be extended by repetition.
        """
        self.colors = colors
        self.monochrome = False
        if N is None:
            N = len(self.colors)
        elif cbook.is_string_like(self.colors):
            self.colors = [
             self.colors] * N
            self.monochrome = True
        elif cbook.iterable(self.colors):
            self.colors = list(self.colors)
            if len(self.colors) == 1:
                self.monochrome = True
            if len(self.colors) < N:
                self.colors = list(self.colors) * N
            del self.colors[N:]
        else:
            try:
                gray = float(self.colors)
            except TypeError:
                pass
            else:
                self.colors = [
                 gray] * N

            self.monochrome = True
        Colormap.__init__(self, name, N)
        return

    def _init(self):
        rgba = colorConverter.to_rgba_array(self.colors)
        self._lut = np.zeros((self.N + 3, 4), np.float)
        self._lut[:(-3)] = rgba
        self._isinit = True
        self._set_extremes()


class Normalize(object):
    """
    Normalize a given value to the 0-1 range
    """

    def __init__(self, vmin=None, vmax=None, clip=False):
        """
        If *vmin* or *vmax* is not given, they are taken from the input's
        minimum and maximum value respectively.  If *clip* is *True* and
        the given value falls outside the range, the returned value
        will be 0 or 1, whichever is closer. Returns 0 if::

            vmin==vmax

        Works with scalars or arrays, including masked arrays.  If
        *clip* is *True*, masked values are set to 1; otherwise they
        remain masked.  Clipping silently defeats the purpose of setting
        the over, under, and masked colors in the colormap, so it is
        likely to lead to surprises; therefore the default is
        *clip* = *False*.
        """
        self.vmin = vmin
        self.vmax = vmax
        self.clip = clip

    @staticmethod
    def process_value(value):
        """
        Homogenize the input *value* for easy and efficient normalization.

        *value* can be a scalar or sequence.

        Returns *result*, *is_scalar*, where *result* is a
        masked array matching *value*.  Float dtypes are preserved;
        integer types with two bytes or smaller are converted to
        np.float32, and larger types are converted to np.float.
        Preserving float32 when possible, and using in-place operations,
        can greatly improve speed for large arrays.

        Experimental; we may want to add an option to force the
        use of float32.
        """
        if cbook.iterable(value):
            is_scalar = False
            result = ma.asarray(value)
            if result.dtype.kind == 'f':
                if isinstance(value, np.ndarray):
                    result = result.copy()
            else:
                if result.dtype.itemsize > 2:
                    result = result.astype(np.float)
                else:
                    result = result.astype(np.float32)
        else:
            is_scalar = True
            result = ma.array([value]).astype(np.float)
        return (
         result, is_scalar)

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip
        result, is_scalar = self.process_value(value)
        self.autoscale_None(result)
        vmin, vmax = self.vmin, self.vmax
        if vmin > vmax:
            raise ValueError('minvalue must be less than or equal to maxvalue')
        elif vmin == vmax:
            result.fill(0)
        else:
            vmin = float(vmin)
            vmax = float(vmax)
            if clip:
                mask = ma.getmask(result)
                result = ma.array(np.clip(result.filled(vmax), vmin, vmax), mask=mask)
            resdat = result.data
            resdat -= vmin
            resdat /= vmax - vmin
            result = np.ma.array(resdat, mask=result.mask, copy=False)
        if is_scalar:
            result = result[0]
        return result

    def inverse(self, value):
        if not self.scaled():
            raise ValueError('Not invertible until scaled')
        vmin = float(self.vmin)
        vmax = float(self.vmax)
        if cbook.iterable(value):
            val = ma.asarray(value)
            return vmin + val * (vmax - vmin)
        else:
            return vmin + value * (vmax - vmin)

    def autoscale(self, A):
        """
        Set *vmin*, *vmax* to min, max of *A*.
        """
        self.vmin = ma.min(A)
        self.vmax = ma.max(A)

    def autoscale_None(self, A):
        """ autoscale only None-valued vmin or vmax"""
        if self.vmin is None:
            self.vmin = ma.min(A)
        if self.vmax is None:
            self.vmax = ma.max(A)
        return

    def scaled(self):
        """return true if vmin and vmax set"""
        return self.vmin is not None and self.vmax is not None


class LogNorm(Normalize):
    """
    Normalize a given value to the 0-1 range on a log scale
    """

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip
        result, is_scalar = self.process_value(value)
        result = ma.masked_less_equal(result, 0, copy=False)
        self.autoscale_None(result)
        vmin, vmax = self.vmin, self.vmax
        if vmin > vmax:
            raise ValueError('minvalue must be less than or equal to maxvalue')
        elif vmin <= 0:
            raise ValueError('values must all be positive')
        elif vmin == vmax:
            result.fill(0)
        else:
            if clip:
                mask = ma.getmask(result)
                result = ma.array(np.clip(result.filled(vmax), vmin, vmax), mask=mask)
            resdat = result.data
            mask = result.mask
            if mask is np.ma.nomask:
                mask = resdat <= 0
            else:
                mask |= resdat <= 0
            cbook._putmask(resdat, mask, 1)
            np.log(resdat, resdat)
            resdat -= np.log(vmin)
            resdat /= np.log(vmax) - np.log(vmin)
            result = np.ma.array(resdat, mask=mask, copy=False)
        if is_scalar:
            result = result[0]
        return result

    def inverse(self, value):
        if not self.scaled():
            raise ValueError('Not invertible until scaled')
        vmin, vmax = self.vmin, self.vmax
        if cbook.iterable(value):
            val = ma.asarray(value)
            return vmin * ma.power(vmax / vmin, val)
        else:
            return vmin * pow(vmax / vmin, value)

    def autoscale(self, A):
        """
        Set *vmin*, *vmax* to min, max of *A*.
        """
        A = ma.masked_less_equal(A, 0, copy=False)
        self.vmin = ma.min(A)
        self.vmax = ma.max(A)

    def autoscale_None(self, A):
        """ autoscale only None-valued vmin or vmax"""
        if self.vmin is not None and self.vmax is not None:
            return
        else:
            A = ma.masked_less_equal(A, 0, copy=False)
            if self.vmin is None:
                self.vmin = ma.min(A)
            if self.vmax is None:
                self.vmax = ma.max(A)
            return


class BoundaryNorm(Normalize):
    """
    Generate a colormap index based on discrete intervals.

    Unlike :class:`Normalize` or :class:`LogNorm`,
    :class:`BoundaryNorm` maps values to integers instead of to the
    interval 0-1.

    Mapping to the 0-1 interval could have been done via
    piece-wise linear interpolation, but using integers seems
    simpler, and reduces the number of conversions back and forth
    between integer and floating point.
    """

    def __init__(self, boundaries, ncolors, clip=False):
        """
        *boundaries*
            a monotonically increasing sequence
        *ncolors*
            number of colors in the colormap to be used

        If::

            b[i] <= v < b[i+1]

        then v is mapped to color j;
        as i varies from 0 to len(boundaries)-2,
        j goes from 0 to ncolors-1.

        Out-of-range values are mapped to -1 if low and ncolors
        if high; these are converted to valid indices by
        :meth:`Colormap.__call__` .
        """
        self.clip = clip
        self.vmin = boundaries[0]
        self.vmax = boundaries[-1]
        self.boundaries = np.asarray(boundaries)
        self.N = len(self.boundaries)
        self.Ncmap = ncolors
        if self.N - 1 == self.Ncmap:
            self._interp = False
        else:
            self._interp = True

    def __call__(self, x, clip=None):
        if clip is None:
            clip = self.clip
        x = ma.asarray(x)
        mask = ma.getmaskarray(x)
        xx = x.filled(self.vmax + 1)
        if clip:
            np.clip(xx, self.vmin, self.vmax)
        iret = np.zeros(x.shape, dtype=np.int16)
        for i, b in enumerate(self.boundaries):
            iret[xx >= b] = i

        if self._interp:
            scalefac = float(self.Ncmap - 1) / (self.N - 2)
            iret = (iret * scalefac).astype(np.int16)
        iret[xx < self.vmin] = -1
        iret[xx >= self.vmax] = self.Ncmap
        ret = ma.array(iret, mask=mask)
        if ret.shape == () and not mask:
            ret = int(ret)
        return ret

    def inverse(self, value):
        return ValueError('BoundaryNorm is not invertible')


class NoNorm(Normalize):
    """
    Dummy replacement for Normalize, for the case where we
    want to use indices directly in a
    :class:`~matplotlib.cm.ScalarMappable` .
    """

    def __call__(self, value, clip=None):
        return value

    def inverse(self, value):
        return value


normalize = Normalize
no_norm = NoNorm

def rgb_to_hsv(arr):
    """
    convert rgb values in a numpy array to hsv values
    input and output arrays should have shape (M,N,3)
    """
    out = np.zeros_like(arr)
    arr_max = arr.max(-1)
    ipos = arr_max > 0
    delta = arr.ptp(-1)
    s = np.zeros_like(delta)
    s[ipos] = delta[ipos] / arr_max[ipos]
    ipos = delta > 0
    idx = (arr[:, :, 0] == arr_max) & ipos
    out[(idx, 0)] = (arr[(idx, 1)] - arr[(idx, 2)]) / delta[idx]
    idx = (arr[:, :, 1] == arr_max) & ipos
    out[(idx, 0)] = 2.0 + (arr[(idx, 2)] - arr[(idx, 0)]) / delta[idx]
    idx = (arr[:, :, 2] == arr_max) & ipos
    out[(idx, 0)] = 4.0 + (arr[(idx, 0)] - arr[(idx, 1)]) / delta[idx]
    out[:, :, 0] = out[:, :, 0] / 6.0 % 1.0
    out[:, :, 1] = s
    out[:, :, 2] = arr_max
    return out


def hsv_to_rgb(hsv):
    """
    convert hsv values in a numpy array to rgb values
    both input and output arrays have shape (M,N,3)
    """
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    r = np.empty_like(h)
    g = np.empty_like(h)
    b = np.empty_like(h)
    i = (h * 6.0).astype(np.int)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    idx = i % 6 == 0
    r[idx] = v[idx]
    g[idx] = t[idx]
    b[idx] = p[idx]
    idx = i == 1
    r[idx] = q[idx]
    g[idx] = v[idx]
    b[idx] = p[idx]
    idx = i == 2
    r[idx] = p[idx]
    g[idx] = v[idx]
    b[idx] = t[idx]
    idx = i == 3
    r[idx] = p[idx]
    g[idx] = q[idx]
    b[idx] = v[idx]
    idx = i == 4
    r[idx] = t[idx]
    g[idx] = p[idx]
    b[idx] = v[idx]
    idx = i == 5
    r[idx] = v[idx]
    g[idx] = p[idx]
    b[idx] = q[idx]
    idx = s == 0
    r[idx] = v[idx]
    g[idx] = v[idx]
    b[idx] = v[idx]
    rgb = np.empty_like(hsv)
    rgb[:, :, 0] = r
    rgb[:, :, 1] = g
    rgb[:, :, 2] = b
    return rgb


class LightSource(object):
    """
    Create a light source coming from the specified azimuth and elevation.
    Angles are in degrees, with the azimuth measured
    clockwise from north and elevation up from the zero plane of the surface.
    The :meth:`shade` is used to produce rgb values for a shaded relief image
    given a data array.
    """

    def __init__(self, azdeg=315, altdeg=45, hsv_min_val=0, hsv_max_val=1, hsv_min_sat=1, hsv_max_sat=0):
        """
        Specify the azimuth (measured clockwise from south) and altitude
        (measured up from the plane of the surface) of the light source
        in degrees.

        The color of the resulting image will be darkened
        by moving the (s,v) values (in hsv colorspace) toward
        (hsv_min_sat, hsv_min_val) in the shaded regions, or
        lightened by sliding (s,v) toward
        (hsv_max_sat hsv_max_val) in regions that are illuminated.
        The default extremes are chose so that completely shaded points
        are nearly black (s = 1, v = 0) and completely illuminated points
        are nearly white (s = 0, v = 1).
        """
        self.azdeg = azdeg
        self.altdeg = altdeg
        self.hsv_min_val = hsv_min_val
        self.hsv_max_val = hsv_max_val
        self.hsv_min_sat = hsv_min_sat
        self.hsv_max_sat = hsv_max_sat

    def shade(self, data, cmap):
        """
        Take the input data array, convert to HSV values in the
        given colormap, then adjust those color values
        to given the impression of a shaded relief map with a
        specified light source.
        RGBA values are returned, which can then be used to
        plot the shaded image with imshow.
        """
        rgb0 = cmap((data - data.min()) / (data.max() - data.min()))
        rgb1 = self.shade_rgb(rgb0, elevation=data)
        rgb0[:, :, 0:3] = rgb1
        return rgb0

    def shade_rgb(self, rgb, elevation, fraction=1.0):
        """
        Take the input RGB array (ny*nx*3) adjust their color values
        to given the impression of a shaded relief map with a
        specified light source using the elevation (ny*nx).
        A new RGB array ((ny*nx*3)) is returned.
        """
        az = self.azdeg * np.pi / 180.0
        alt = self.altdeg * np.pi / 180.0
        dx, dy = np.gradient(elevation)
        slope = 0.5 * np.pi - np.arctan(np.hypot(dx, dy))
        aspect = np.arctan2(dx, dy)
        intensity = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(-az - aspect - 0.5 * np.pi)
        intensity = (intensity - intensity.min()) / (intensity.max() - intensity.min())
        intensity = (2.0 * intensity - 1.0) * fraction
        hsv = rgb_to_hsv(rgb[:, :, 0:3])
        hsv[:, :, 1] = np.where(np.logical_and(np.abs(hsv[:, :, 1]) > 1e-10, intensity > 0), (1.0 - intensity) * hsv[:, :, 1] + intensity * self.hsv_max_sat, hsv[:, :, 1])
        hsv[:, :, 2] = np.where(intensity > 0, (1.0 - intensity) * hsv[:, :, 2] + intensity * self.hsv_max_val, hsv[:, :, 2])
        hsv[:, :, 1] = np.where(np.logical_and(np.abs(hsv[:, :, 1]) > 1e-10, intensity < 0), (1.0 + intensity) * hsv[:, :, 1] - intensity * self.hsv_min_sat, hsv[:, :, 1])
        hsv[:, :, 2] = np.where(intensity < 0, (1.0 + intensity) * hsv[:, :, 2] - intensity * self.hsv_min_val, hsv[:, :, 2])
        hsv[:, :, 1:] = np.where(hsv[:, :, 1:] < 0.0, 0, hsv[:, :, 1:])
        hsv[:, :, 1:] = np.where(hsv[:, :, 1:] > 1.0, 1, hsv[:, :, 1:])
        return hsv_to_rgb(hsv)