# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\spines.pyc
# Compiled at: 2012-10-30 18:11:14
from __future__ import division, print_function
import matplotlib
rcParams = matplotlib.rcParams
import matplotlib.artist as martist
from matplotlib.artist import allow_rasterization
from matplotlib import docstring
import matplotlib.transforms as mtransforms, matplotlib.lines as mlines, matplotlib.patches as mpatches, matplotlib.path as mpath, matplotlib.cbook as cbook, numpy as np, warnings

class Spine(mpatches.Patch):
    """an axis spine -- the line noting the data area boundaries

    Spines are the lines connecting the axis tick marks and noting the
    boundaries of the data area. They can be placed at arbitrary
    positions. See function:`~matplotlib.spines.Spine.set_position`
    for more information.

    The default position is ``('outward',0)``.

    Spines are subclasses of class:`~matplotlib.patches.Patch`, and
    inherit much of their behavior.

    Spines draw a line or a circle, depending if
    function:`~matplotlib.spines.Spine.set_patch_line` or
    function:`~matplotlib.spines.Spine.set_patch_circle` has been
    called. Line-like is the default.

    """

    def __str__(self):
        return 'Spine'

    @docstring.dedent_interpd
    def __init__(self, axes, spine_type, path, **kwargs):
        """
        - *axes* : the Axes instance containing the spine
        - *spine_type* : a string specifying the spine type
        - *path* : the path instance used to draw the spine

        Valid kwargs are:
        %(Patch)s
        """
        super(Spine, self).__init__(**kwargs)
        self.axes = axes
        self.set_figure(self.axes.figure)
        self.spine_type = spine_type
        self.set_facecolor('none')
        self.set_edgecolor(rcParams['axes.edgecolor'])
        self.set_linewidth(rcParams['axes.linewidth'])
        self.axis = None
        self.set_zorder(2.5)
        self.set_transform(self.axes.transData)
        self._bounds = None
        self._smart_bounds = False
        self._position = None
        assert isinstance(path, matplotlib.path.Path)
        self._path = path
        self._patch_type = 'line'
        self._patch_transform = mtransforms.IdentityTransform()
        return

    def set_smart_bounds(self, value):
        """set the spine and associated axis to have smart bounds"""
        self._smart_bounds = value
        if self.spine_type in ('left', 'right'):
            self.axes.yaxis.set_smart_bounds(value)
        elif self.spine_type in ('top', 'bottom'):
            self.axes.xaxis.set_smart_bounds(value)

    def get_smart_bounds(self):
        """get whether the spine has smart bounds"""
        return self._smart_bounds

    def set_patch_circle(self, center, radius):
        """set the spine to be circular"""
        self._patch_type = 'circle'
        self._center = center
        self._width = radius * 2
        self._height = radius * 2
        self._angle = 0
        self.set_transform(self.axes.transAxes)

    def set_patch_line(self):
        """set the spine to be linear"""
        self._patch_type = 'line'

    def _recompute_transform(self):
        """NOTE: This cannot be called until after this has been added
                 to an Axes, otherwise unit conversion will fail. This
                 maxes it very important to call the accessor method and
                 not directly access the transformation member variable.
        """
        assert self._patch_type == 'circle'
        center = (self.convert_xunits(self._center[0]),
         self.convert_yunits(self._center[1]))
        width = self.convert_xunits(self._width)
        height = self.convert_yunits(self._height)
        self._patch_transform = mtransforms.Affine2D().scale(width * 0.5, height * 0.5).rotate_deg(self._angle).translate(*center)

    def get_patch_transform(self):
        if self._patch_type == 'circle':
            self._recompute_transform()
            return self._patch_transform
        else:
            return super(Spine, self).get_patch_transform()

    def get_path(self):
        return self._path

    def _ensure_position_is_set(self):
        if self._position is None:
            self._position = ('outward', 0.0)
            self.set_position(self._position)
        return

    def register_axis(self, axis):
        """register an axis

        An axis should be registered with its corresponding spine from
        the Axes instance. This allows the spine to clear any axis
        properties when needed.
        """
        self.axis = axis
        if self.axis is not None:
            self.axis.cla()
        return

    def cla(self):
        """Clear the current spine"""
        self._position = None
        if self.axis is not None:
            self.axis.cla()
        return

    def is_frame_like(self):
        """return True if directly on axes frame

        This is useful for determining if a spine is the edge of an
        old style MPL plot. If so, this function will return True.
        """
        self._ensure_position_is_set()
        position = self._position
        if cbook.is_string_like(position):
            if position == 'center':
                position = ('axes', 0.5)
            elif position == 'zero':
                position = ('data', 0)
        assert len(position) == 2, 'position should be 2-tuple'
        position_type, amount = position
        if position_type == 'outward' and amount == 0:
            return True
        else:
            return False

    def _adjust_location(self):
        """automatically set spine bounds to the view interval"""
        if self.spine_type == 'circle':
            return
        else:
            if self._bounds is None:
                if self.spine_type in ('left', 'right'):
                    low, high = self.axes.viewLim.intervaly
                elif self.spine_type in ('top', 'bottom'):
                    low, high = self.axes.viewLim.intervalx
                else:
                    raise ValueError('unknown spine spine_type: %s' % self.spine_type)
                if self._smart_bounds:
                    if low > high:
                        low, high = high, low
                    viewlim_low = low
                    viewlim_high = high
                    del low
                    del high
                    if self.spine_type in ('left', 'right'):
                        datalim_low, datalim_high = self.axes.dataLim.intervaly
                        ticks = self.axes.get_yticks()
                    elif self.spine_type in ('top', 'bottom'):
                        datalim_low, datalim_high = self.axes.dataLim.intervalx
                        ticks = self.axes.get_xticks()
                    ticks = list(ticks)
                    ticks.sort()
                    ticks = np.array(ticks)
                    if datalim_low > datalim_high:
                        datalim_low, datalim_high = datalim_high, datalim_low
                    if datalim_low < viewlim_low:
                        low = viewlim_low
                    else:
                        cond = (ticks <= datalim_low) & (ticks >= viewlim_low)
                        tickvals = ticks[cond]
                        if len(tickvals):
                            low = tickvals[-1]
                        else:
                            low = datalim_low
                        low = max(low, viewlim_low)
                    if datalim_high > viewlim_high:
                        high = viewlim_high
                    else:
                        cond = (ticks >= datalim_high) & (ticks <= viewlim_high)
                        tickvals = ticks[cond]
                        if len(tickvals):
                            high = tickvals[0]
                        else:
                            high = datalim_high
                        high = min(high, viewlim_high)
            else:
                low, high = self._bounds
            v1 = self._path.vertices
            assert v1.shape == (2, 2), 'unexpected vertices shape'
            if self.spine_type in ('left', 'right'):
                v1[(0, 1)] = low
                v1[(1, 1)] = high
            elif self.spine_type in ('bottom', 'top'):
                v1[(0, 0)] = low
                v1[(1, 0)] = high
            else:
                raise ValueError('unable to set bounds for spine "%s"' % spine_type)
            return

    @allow_rasterization
    def draw(self, renderer):
        self._adjust_location()
        return super(Spine, self).draw(renderer)

    def _calc_offset_transform(self):
        """calculate the offset transform performed by the spine"""
        self._ensure_position_is_set()
        position = self._position
        if cbook.is_string_like(position):
            if position == 'center':
                position = ('axes', 0.5)
            elif position == 'zero':
                position = ('data', 0)
        assert len(position) == 2, 'position should be 2-tuple'
        position_type, amount = position
        assert position_type in ('axes', 'outward', 'data')
        if position_type == 'outward':
            if amount == 0:
                self._spine_transform = ('identity', mtransforms.IdentityTransform())
            elif self.spine_type in ('left', 'right', 'top', 'bottom'):
                offset_vec = {'left': (-1, 0), 'right': (1, 0), 'bottom': (0, -1), 
                   'top': (0, 1)}[self.spine_type]
                offset_x = amount * offset_vec[0] / 72.0
                offset_y = amount * offset_vec[1] / 72.0
                self._spine_transform = ('post',
                 mtransforms.ScaledTranslation(offset_x, offset_y, self.figure.dpi_scale_trans))
            else:
                warnings.warn('unknown spine type "%s": no spine offset performed' % self.spine_type)
                self._spine_transform = ('identity', mtransforms.IdentityTransform())
        elif position_type == 'axes':
            if self.spine_type in ('left', 'right'):
                self._spine_transform = (
                 'pre',
                 mtransforms.Affine2D.from_values(0, 0, 0, 1, amount, 0))
            elif self.spine_type in ('bottom', 'top'):
                self._spine_transform = (
                 'pre',
                 mtransforms.Affine2D.from_values(1, 0, 0, 0, 0, amount))
            else:
                warnings.warn('unknown spine type "%s": no spine offset performed' % self.spine_type)
                self._spine_transform = ('identity', mtransforms.IdentityTransform())
        elif position_type == 'data':
            if self.spine_type in ('left', 'right'):
                self._spine_transform = (
                 'data',
                 mtransforms.Affine2D().translate(amount, 0))
            elif self.spine_type in ('bottom', 'top'):
                self._spine_transform = (
                 'data',
                 mtransforms.Affine2D().translate(0, amount))
            else:
                warnings.warn('unknown spine type "%s": no spine offset performed' % self.spine_type)
                self._spine_transform = ('identity', mtransforms.IdentityTransform())

    def set_position(self, position):
        """set the position of the spine

        Spine position is specified by a 2 tuple of (position type,
        amount). The position types are:

        * 'outward' : place the spine out from the data area by the
          specified number of points. (Negative values specify placing the
          spine inward.)

        * 'axes' : place the spine at the specified Axes coordinate (from
          0.0-1.0).

        * 'data' : place the spine at the specified data coordinate.

        Additionally, shorthand notations define a special positions:

        * 'center' -> ('axes',0.5)
        * 'zero' -> ('data', 0.0)

        """
        if position in ('center', 'zero'):
            pass
        else:
            assert len(position) == 2, "position should be 'center' or 2-tuple"
            assert position[0] in ('outward', 'axes', 'data')
        self._position = position
        self._calc_offset_transform()
        t = self.get_spine_transform()
        if self.spine_type in ('left', 'right'):
            t2 = mtransforms.blended_transform_factory(t, self.axes.transData)
        elif self.spine_type in ('bottom', 'top'):
            t2 = mtransforms.blended_transform_factory(self.axes.transData, t)
        self.set_transform(t2)
        if self.axis is not None:
            self.axis.cla()
        return

    def get_position(self):
        """get the spine position"""
        self._ensure_position_is_set()
        return self._position

    def get_spine_transform(self):
        """get the spine transform"""
        self._ensure_position_is_set()
        what, how = self._spine_transform
        if what == 'data':
            data_xform = self.axes.transScale + (how + self.axes.transLimits + self.axes.transAxes)
            if self.spine_type in ('left', 'right'):
                result = mtransforms.blended_transform_factory(data_xform, self.axes.transData)
            elif self.spine_type in ('top', 'bottom'):
                result = mtransforms.blended_transform_factory(self.axes.transData, data_xform)
            else:
                raise ValueError('unknown spine spine_type: %s' % self.spine_type)
            return result
        if self.spine_type in ('left', 'right'):
            base_transform = self.axes.get_yaxis_transform(which='grid')
        else:
            if self.spine_type in ('top', 'bottom'):
                base_transform = self.axes.get_xaxis_transform(which='grid')
            else:
                raise ValueError('unknown spine spine_type: %s' % self.spine_type)
            if what == 'identity':
                return base_transform
            if what == 'post':
                return base_transform + how
            if what == 'pre':
                return how + base_transform
        raise ValueError('unknown spine_transform type: %s' % what)

    def set_bounds(self, low, high):
        """Set the bounds of the spine."""
        if self.spine_type == 'circle':
            raise ValueError('set_bounds() method incompatible with circular spines')
        self._bounds = (
         low, high)

    def get_bounds(self):
        """Get the bounds of the spine."""
        return self._bounds

    @classmethod
    def linear_spine(cls, axes, spine_type, **kwargs):
        """
        (staticmethod) Returns a linear :class:`Spine`.
        """
        if spine_type == 'left':
            path = mpath.Path([(0.0, 13), (0.0, 13)])
        elif spine_type == 'right':
            path = mpath.Path([(1.0, 13), (1.0, 13)])
        elif spine_type == 'bottom':
            path = mpath.Path([(13, 0.0), (13, 0.0)])
        elif spine_type == 'top':
            path = mpath.Path([(13, 1.0), (13, 1.0)])
        else:
            raise ValueError('unable to make path for spine "%s"' % spine_type)
        result = cls(axes, spine_type, path, **kwargs)
        return result

    @classmethod
    def circular_spine(cls, axes, center, radius, **kwargs):
        """
        (staticmethod) Returns a circular :class:`Spine`.
        """
        path = mpath.Path.unit_circle()
        spine_type = 'circle'
        result = cls(axes, spine_type, path, **kwargs)
        result.set_patch_circle(center, radius)
        return result

    def set_color(self, c):
        """
        Set the edgecolor.

        ACCEPTS: matplotlib color arg or sequence of rgba tuples

        .. seealso::

            :meth:`set_facecolor`, :meth:`set_edgecolor`
               For setting the edge or face color individually.
        """
        self.set_edgecolor(c)