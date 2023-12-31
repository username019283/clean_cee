# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\markers.pyc
# Compiled at: 2012-10-30 18:11:14
"""
This module contains functions to handle markers.  Used by both the
marker functionality of `~matplotlib.axes.Axes.plot` and
`~matplotlib.axes.Axes.scatter`.
"""
import textwrap, numpy as np
from cbook import is_math_text, is_string_like, is_numlike, iterable
import docstring
from matplotlib import rcParams
from path import Path
from transforms import IdentityTransform, Affine2D
TICKLEFT, TICKRIGHT, TICKUP, TICKDOWN, CARETLEFT, CARETRIGHT, CARETUP, CARETDOWN = range(8)

class MarkerStyle():
    style_table = "\n============================== ===============================================\nmarker                         description\n============================== ===============================================\n%s\n``'$...$'``                    render the string using mathtext.\n*verts*                        a list of (x, y) pairs used for Path vertices.\npath                           a :class:`~matplotlib.path.Path` instance.\n(*numsides*, *style*, *angle*) see below\n============================== ===============================================\n\nThe marker can also be a tuple (*numsides*, *style*, *angle*), which\nwill create a custom, regular symbol.\n\n    *numsides*:\n      the number of sides\n\n    *style*:\n      the style of the regular symbol:\n\n      =====   =============================================\n      Value   Description\n      =====   =============================================\n      0       a regular polygon\n      1       a star-like symbol\n      2       an asterisk\n      3       a circle (*numsides* and *angle* is ignored)\n      =====   =============================================\n\n    *angle*:\n      the angle of rotation of the symbol, in degrees\n\nFor backward compatibility, the form (*verts*, 0) is also accepted,\nbut it is equivalent to just *verts* for giving a raw set of vertices\nthat define the shape.\n"
    accepts = "ACCEPTS: [ %s | ``'$...$'`` | *tuple* | *Nx2 array* ]"
    markers = {'.': 'point', 
       ',': 'pixel', 
       'o': 'circle', 
       'v': 'triangle_down', 
       '^': 'triangle_up', 
       '<': 'triangle_left', 
       '>': 'triangle_right', 
       '1': 'tri_down', 
       '2': 'tri_up', 
       '3': 'tri_left', 
       '4': 'tri_right', 
       '8': 'octagon', 
       's': 'square', 
       'p': 'pentagon', 
       '*': 'star', 
       'h': 'hexagon1', 
       'H': 'hexagon2', 
       '+': 'plus', 
       'x': 'x', 
       'D': 'diamond', 
       'd': 'thin_diamond', 
       '|': 'vline', 
       '_': 'hline', 
       TICKLEFT: 'tickleft', 
       TICKRIGHT: 'tickright', 
       TICKUP: 'tickup', 
       TICKDOWN: 'tickdown', 
       CARETLEFT: 'caretleft', 
       CARETRIGHT: 'caretright', 
       CARETUP: 'caretup', 
       CARETDOWN: 'caretdown', 
       'None': 'nothing', 
       None: 'nothing', 
       ' ': 'nothing', 
       '': 'nothing'}
    filled_markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd')
    fillstyles = ('full', 'left', 'right', 'bottom', 'top', 'none')
    _half_fillstyles = ('left', 'right', 'bottom', 'top')
    _point_size_reduction = 0.5

    def __init__(self, marker=None, fillstyle='full'):
        self._fillstyle = fillstyle
        self.set_marker(marker)
        self.set_fillstyle(fillstyle)

    def __getstate__(self):
        d = self.__dict__.copy()
        d.pop('_marker_function')
        return d

    def __setstate__(self, statedict):
        self.__dict__ = statedict
        self.set_marker(self._marker)
        self._recache()

    def _recache(self):
        self._path = Path(np.empty((0, 2)))
        self._transform = IdentityTransform()
        self._alt_path = None
        self._alt_transform = None
        self._snap_threshold = None
        self._joinstyle = 'round'
        self._capstyle = 'butt'
        self._filled = True
        self._marker_function()
        return

    def __nonzero__(self):
        return bool(len(self._path.vertices))

    def is_filled(self):
        return self._filled

    def get_fillstyle(self):
        return self._fillstyle

    def set_fillstyle(self, fillstyle):
        assert fillstyle in self.fillstyles
        self._fillstyle = fillstyle
        self._recache()

    def get_joinstyle(self):
        return self._joinstyle

    def get_capstyle(self):
        return self._capstyle

    def get_marker(self):
        return self._marker

    def set_marker(self, marker):
        if iterable(marker) and len(marker) in (2, 3) and marker[1] in (0, 1, 2, 3):
            self._marker_function = self._set_tuple_marker
        elif isinstance(marker, np.ndarray):
            self._marker_function = self._set_vertices
        elif marker in self.markers:
            self._marker_function = getattr(self, '_set_' + self.markers[marker])
        elif is_string_like(marker) and is_math_text(marker):
            self._marker_function = self._set_mathtext_path
        elif isinstance(marker, Path):
            self._marker_function = self._set_path_marker
        else:
            try:
                _ = Path(marker)
                self._marker_function = self._set_vertices
            except ValueError:
                raise ValueError(('Unrecognized marker style {}').format(marker))

        self._marker = marker
        self._recache()

    def get_path(self):
        return self._path

    def get_transform(self):
        return self._transform.frozen()

    def get_alt_path(self):
        return self._alt_path

    def get_alt_transform(self):
        return self._alt_transform.frozen()

    def get_snap_threshold(self):
        return self._snap_threshold

    def _set_nothing(self):
        self._filled = False

    def _set_custom_marker(self, path):
        verts = path.vertices
        rescale = max(np.max(np.abs(verts[:, 0])), np.max(np.abs(verts[:, 1])))
        self._transform = Affine2D().scale(1.0 / rescale)
        self._path = path

    def _set_path_marker(self):
        self._set_custom_marker(self._marker)

    def _set_vertices(self):
        verts = self._marker
        marker = Path(verts)
        self._set_custom_marker(marker)

    def _set_tuple_marker(self):
        marker = self._marker
        if is_numlike(marker[0]):
            if len(marker) == 2:
                numsides, rotation = marker[0], 0.0
            elif len(marker) == 3:
                numsides, rotation = marker[0], marker[2]
            symstyle = marker[1]
            if symstyle == 0:
                self._path = Path.unit_regular_polygon(numsides)
                self._joinstyle = 'miter'
            elif symstyle == 1:
                self._path = Path.unit_regular_star(numsides)
                self._joinstyle = 'bevel'
            elif symstyle == 2:
                self._path = Path.unit_regular_asterisk(numsides)
                self._filled = False
                self._joinstyle = 'bevel'
            elif symstyle == 3:
                self._path = Path.unit_circle()
            self._transform = Affine2D().scale(0.5).rotate_deg(rotation)
        else:
            verts = np.asarray(marker[0])
            path = Path(verts)
            self._set_custom_marker(path)

    def _set_mathtext_path(self):
        """
        Draws mathtext markers '$...$' using TextPath object.

        Submitted by tcb
        """
        from matplotlib.text import TextPath
        from matplotlib.font_manager import FontProperties
        props = FontProperties(size=1.0)
        text = TextPath(xy=(0, 0), s=self.get_marker(), fontproperties=props, usetex=rcParams['text.usetex'])
        if len(text.vertices) == 0:
            return
        xmin, ymin = text.vertices.min(axis=0)
        xmax, ymax = text.vertices.max(axis=0)
        width = xmax - xmin
        height = ymax - ymin
        max_dim = max(width, height)
        self._transform = Affine2D().translate(-xmin + 0.5 * -width, -ymin + 0.5 * -height).scale(1.0 / max_dim)
        self._path = text
        self._snap = False

    def _half_fill(self):
        fs = self.get_fillstyle()
        result = fs in self._half_fillstyles
        return result

    def _set_circle(self, reduction=1.0):
        self._transform = Affine2D().scale(0.5 * reduction)
        self._snap_threshold = 6.0
        fs = self.get_fillstyle()
        if not self._half_fill():
            self._path = Path.unit_circle()
        else:
            if fs == 'bottom':
                rotate = 270.0
            elif fs == 'top':
                rotate = 90.0
            elif fs == 'left':
                rotate = 180.0
            else:
                rotate = 0.0
            self._path = self._alt_path = Path.unit_circle_righthalf()
            self._transform.rotate_deg(rotate)
            self._alt_transform = self._transform.frozen().rotate_deg(180.0)

    def _set_pixel(self):
        self._path = Path.unit_rectangle()
        self._transform = Affine2D().translate(-0.49999, -0.49999)
        self._snap_threshold = None
        return

    def _set_point(self):
        self._set_circle(reduction=self._point_size_reduction)

    _triangle_path = Path([
     [
      0.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [0.0, 1.0]], [
     Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    _triangle_path_u = Path([
     [
      0.0, 1.0], [-3 / 5.0, -1 / 5.0], [3 / 5.0, -1 / 5.0], [0.0, 1.0]], [
     Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    _triangle_path_d = Path([
     [
      -3 / 5.0, -1 / 5.0], [3 / 5.0, -1 / 5.0], [1.0, -1.0], [-1.0, -1.0], [-3 / 5.0, -1 / 5.0]], [
     Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    _triangle_path_l = Path([
     [
      0.0, 1.0], [0.0, -1.0], [-1.0, -1.0], [0.0, 1.0]], [
     Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    _triangle_path_r = Path([
     [
      0.0, 1.0], [0.0, -1.0], [1.0, -1.0], [0.0, 1.0]], [
     Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])

    def _set_triangle(self, rot, skip):
        self._transform = Affine2D().scale(0.5, 0.5).rotate_deg(rot)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        if not self._half_fill():
            self._path = self._triangle_path
        else:
            mpaths = [
             self._triangle_path_u,
             self._triangle_path_l,
             self._triangle_path_d,
             self._triangle_path_r]
            if fs == 'top':
                self._path = mpaths[(0 + skip) % 4]
                self._alt_path = mpaths[(2 + skip) % 4]
            elif fs == 'bottom':
                self._path = mpaths[(2 + skip) % 4]
                self._alt_path = mpaths[(0 + skip) % 4]
            elif fs == 'left':
                self._path = mpaths[(1 + skip) % 4]
                self._alt_path = mpaths[(3 + skip) % 4]
            else:
                self._path = mpaths[(3 + skip) % 4]
                self._alt_path = mpaths[(1 + skip) % 4]
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_triangle_up(self):
        return self._set_triangle(0.0, 0)

    def _set_triangle_down(self):
        return self._set_triangle(180.0, 2)

    def _set_triangle_left(self):
        return self._set_triangle(90.0, 3)

    def _set_triangle_right(self):
        return self._set_triangle(270.0, 1)

    def _set_square(self):
        self._transform = Affine2D().translate(-0.5, -0.5)
        self._snap_threshold = 2.0
        fs = self.get_fillstyle()
        if not self._half_fill():
            self._path = Path.unit_rectangle()
        else:
            if fs == 'bottom':
                rotate = 0.0
            elif fs == 'top':
                rotate = 180.0
            elif fs == 'left':
                rotate = 270.0
            else:
                rotate = 90.0
            self._path = Path([[0.0, 0.0], [1.0, 0.0], [1.0, 0.5], [0.0, 0.5], [0.0, 0.0]])
            self._alt_path = Path([[0.0, 0.5], [1.0, 0.5], [1.0, 1.0], [0.0, 1.0], [0.0, 0.5]])
            self._transform.rotate_deg(rotate)
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_diamond(self):
        self._transform = Affine2D().translate(-0.5, -0.5).rotate_deg(45)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        if not self._half_fill():
            self._path = Path.unit_rectangle()
        else:
            self._path = Path([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]])
            self._alt_path = Path([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
            if fs == 'bottom':
                rotate = 270.0
            elif fs == 'top':
                rotate = 90.0
            elif fs == 'left':
                rotate = 180.0
            else:
                rotate = 0.0
            self._transform.rotate_deg(rotate)
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_thin_diamond(self):
        self._set_diamond()
        self._transform.scale(0.6, 1.0)

    def _set_pentagon(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 5.0
        polypath = Path.unit_regular_polygon(5)
        fs = self.get_fillstyle()
        if not self._half_fill():
            self._path = polypath
        else:
            verts = polypath.vertices
            y = (1 + np.sqrt(5)) / 4.0
            top = Path([verts[0], verts[1], verts[4], verts[0]])
            bottom = Path([verts[1], verts[2], verts[3], verts[4], verts[1]])
            left = Path([verts[0], verts[1], verts[2], [0, -y], verts[0]])
            right = Path([verts[0], verts[4], verts[3], [0, -y], verts[0]])
            if fs == 'top':
                mpath, mpath_alt = top, bottom
            elif fs == 'bottom':
                mpath, mpath_alt = bottom, top
            elif fs == 'left':
                mpath, mpath_alt = left, right
            else:
                mpath, mpath_alt = right, left
            self._path = mpath
            self._alt_path = mpath_alt
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_star(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        polypath = Path.unit_regular_star(5, innerCircle=0.381966)
        if not self._half_fill():
            self._path = polypath
        else:
            verts = polypath.vertices
            top = Path(np.vstack((verts[0:4, :], verts[7:10, :], verts[0])))
            bottom = Path(np.vstack((verts[3:8, :], verts[3])))
            left = Path(np.vstack((verts[0:6, :], verts[0])))
            right = Path(np.vstack((verts[0], verts[5:10, :], verts[0])))
            if fs == 'top':
                mpath, mpath_alt = top, bottom
            elif fs == 'bottom':
                mpath, mpath_alt = bottom, top
            elif fs == 'left':
                mpath, mpath_alt = left, right
            else:
                mpath, mpath_alt = right, left
            self._path = mpath
            self._alt_path = mpath_alt
            self._alt_transform = self._transform
        self._joinstyle = 'bevel'

    def _set_hexagon1(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        polypath = Path.unit_regular_polygon(6)
        if not self._half_fill():
            self._path = polypath
        else:
            verts = polypath.vertices
            x = np.abs(np.cos(5 * np.pi / 6.0))
            top = Path(np.vstack(([-x, 0], verts[(1, 0, 5), :], [x, 0])))
            bottom = Path(np.vstack(([-x, 0], verts[2:5, :], [x, 0])))
            left = Path(verts[(0, 1, 2, 3), :])
            right = Path(verts[(0, 5, 4, 3), :])
            if fs == 'top':
                mpath, mpath_alt = top, bottom
            elif fs == 'bottom':
                mpath, mpath_alt = bottom, top
            elif fs == 'left':
                mpath, mpath_alt = left, right
            else:
                mpath, mpath_alt = right, left
            self._path = mpath
            self._alt_path = mpath_alt
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_hexagon2(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(30)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        polypath = Path.unit_regular_polygon(6)
        if not self._half_fill():
            self._path = polypath
        else:
            verts = polypath.vertices
            x, y = np.sqrt(3) / 4, 3 / 4.0
            top = Path(verts[(1, 0, 5, 4, 1), :])
            bottom = Path(verts[(1, 2, 3, 4), :])
            left = Path(np.vstack(([x, y], verts[(0, 1, 2), :], [-x, -y], [x, y])))
            right = Path(np.vstack(([x, y], verts[(5, 4, 3), :], [-x, -y])))
            if fs == 'top':
                mpath, mpath_alt = top, bottom
            elif fs == 'bottom':
                mpath, mpath_alt = bottom, top
            elif fs == 'left':
                mpath, mpath_alt = left, right
            else:
                mpath, mpath_alt = right, left
            self._path = mpath
            self._alt_path = mpath_alt
            self._alt_transform = self._transform
        self._joinstyle = 'miter'

    def _set_octagon(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 5.0
        fs = self.get_fillstyle()
        polypath = Path.unit_regular_polygon(8)
        if not self._half_fill():
            self._transform.rotate_deg(22.5)
            self._path = polypath
        else:
            x = np.sqrt(2.0) / 4.0
            half = Path([[0, -1], [0, 1], [-x, 1], [-1, x],
             [
              -1, -x], [-x, -1], [0, -1]])
            if fs == 'bottom':
                rotate = 90.0
            elif fs == 'top':
                rotate = 270.0
            elif fs == 'right':
                rotate = 180.0
            else:
                rotate = 0.0
            self._transform.rotate_deg(rotate)
            self._path = self._alt_path = half
            self._alt_transform = self._transform.frozen().rotate_deg(180.0)
        self._joinstyle = 'miter'

    _line_marker_path = Path([[0.0, -1.0], [0.0, 1.0]])

    def _set_vline(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._line_marker_path

    def _set_hline(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(90)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._line_marker_path

    _tickhoriz_path = Path([[0.0, 0.0], [1.0, 0.0]])

    def _set_tickleft(self):
        self._transform = Affine2D().scale(-1.0, 1.0)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._tickhoriz_path

    def _set_tickright(self):
        self._transform = Affine2D().scale(1.0, 1.0)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._tickhoriz_path

    _tickvert_path = Path([[-0.0, 0.0], [-0.0, 1.0]])

    def _set_tickup(self):
        self._transform = Affine2D().scale(1.0, 1.0)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._tickvert_path

    def _set_tickdown(self):
        self._transform = Affine2D().scale(1.0, -1.0)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._tickvert_path

    _plus_path = Path([[-1.0, 0.0], [1.0, 0.0],
     [
      0.0, -1.0], [0.0, 1.0]], [
     Path.MOVETO, Path.LINETO,
     Path.MOVETO, Path.LINETO])

    def _set_plus(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 1.0
        self._filled = False
        self._path = self._plus_path

    _tri_path = Path([[0.0, 0.0], [0.0, -1.0],
     [
      0.0, 0.0], [0.8, 0.5],
     [
      0.0, 0.0], [-0.8, 0.5]], [
     Path.MOVETO, Path.LINETO,
     Path.MOVETO, Path.LINETO,
     Path.MOVETO, Path.LINETO])

    def _set_tri_down(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 5.0
        self._filled = False
        self._path = self._tri_path

    def _set_tri_up(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(90)
        self._snap_threshold = 5.0
        self._filled = False
        self._path = self._tri_path

    def _set_tri_left(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(270)
        self._snap_threshold = 5.0
        self._filled = False
        self._path = self._tri_path

    def _set_tri_right(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(180)
        self._snap_threshold = 5.0
        self._filled = False
        self._path = self._tri_path

    _caret_path = Path([[-1.0, 1.5], [0.0, 0.0], [1.0, 1.5]])

    def _set_caretdown(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 3.0
        self._filled = False
        self._path = self._caret_path
        self._joinstyle = 'miter'

    def _set_caretup(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(180)
        self._snap_threshold = 3.0
        self._filled = False
        self._path = self._caret_path
        self._joinstyle = 'miter'

    def _set_caretleft(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(270)
        self._snap_threshold = 3.0
        self._filled = False
        self._path = self._caret_path
        self._joinstyle = 'miter'

    def _set_caretright(self):
        self._transform = Affine2D().scale(0.5).rotate_deg(90)
        self._snap_threshold = 3.0
        self._filled = False
        self._path = self._caret_path
        self._joinstyle = 'miter'

    _x_path = Path([[-1.0, -1.0], [1.0, 1.0],
     [
      -1.0, 1.0], [1.0, -1.0]], [
     Path.MOVETO, Path.LINETO,
     Path.MOVETO, Path.LINETO])

    def _set_x(self):
        self._transform = Affine2D().scale(0.5)
        self._snap_threshold = 3.0
        self._filled = False
        self._path = self._x_path


_styles = [ (repr(x), y) for x, y in MarkerStyle.markers.items() ]
_styles.sort(key=(lambda x: x[1]))
MarkerStyle.style_table = MarkerStyle.style_table % ('\n').join([ '%-30s %-33s' % ('``%s``' % x, y) for x, y in _styles ])
MarkerStyle.accepts = textwrap.fill(MarkerStyle.accepts % (' | ').join([ '``%s``' % x for x, y in _styles ]))
docstring.interpd.update(MarkerTable=MarkerStyle.style_table)
docstring.interpd.update(MarkerAccepts=MarkerStyle.accepts)