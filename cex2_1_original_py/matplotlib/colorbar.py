# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\colorbar.pyc
# Compiled at: 2012-11-08 06:38:04
"""
Colorbar toolkit with two classes and a function:

    :class:`ColorbarBase`
        the base class with full colorbar drawing functionality.
        It can be used as-is to make a colorbar for a given colormap;
        a mappable object (e.g., image) is not needed.

    :class:`Colorbar`
        the derived class for use with images or contour plots.

    :func:`make_axes`
        a function for resizing an axes and adding a second axes
        suitable for a colorbar

The :meth:`~matplotlib.figure.Figure.colorbar` method uses :func:`make_axes`
and :class:`Colorbar`; the :func:`~matplotlib.pyplot.colorbar` function
is a thin wrapper over :meth:`~matplotlib.figure.Figure.colorbar`.

"""
from __future__ import print_function
import warnings, numpy as np, matplotlib as mpl, matplotlib.artist as martist, matplotlib.cbook as cbook, matplotlib.collections as collections, matplotlib.colors as colors, matplotlib.contour as contour, matplotlib.cm as cm, matplotlib.gridspec as gridspec, matplotlib.lines as lines, matplotlib.patches as mpatches, matplotlib.path as mpath, matplotlib.ticker as ticker
from matplotlib import docstring
make_axes_kw_doc = '\n\n    ============= ====================================================\n    Property      Description\n    ============= ====================================================\n    *orientation* vertical or horizontal\n    *fraction*    0.15; fraction of original axes to use for colorbar\n    *pad*         0.05 if vertical, 0.15 if horizontal; fraction\n                  of original axes between colorbar and new image axes\n    *shrink*      1.0; fraction by which to shrink the colorbar\n    *aspect*      20; ratio of long to short dimensions\n    *anchor*      (0.0, 0.5) if vertical; (0.5, 1.0) if horizontal;\n                  the anchor point of the colorbar axes\n    *panchor*     (1.0, 0.5) if vertical; (0.5, 0.0) if horizontal;\n                  the anchor point of the colorbar parent axes\n    ============= ====================================================\n\n'
colormap_kw_doc = "\n\n    ============  ====================================================\n    Property      Description\n    ============  ====================================================\n    *extend*      [ 'neither' | 'both' | 'min' | 'max' ]\n                  If not 'neither', make pointed end(s) for out-of-\n                  range values.  These are set for a given colormap\n                  using the colormap set_under and set_over methods.\n    *extendfrac*  [ *None* | 'auto' | length | lengths ]\n                  If set to *None*, both the minimum and maximum\n                  triangular colorbar extensions with have a length of\n                  5% of the interior colorbar length (this is the\n                  default setting). If set to 'auto', makes the\n                  triangular colorbar extensions the same lengths as\n                  the interior boxes (when *spacing* is set to\n                  'uniform') or the same lengths as the respective\n                  adjacent interior boxes (when *spacing* is set to\n                  'proportional'). If a scalar, indicates the length\n                  of both the minimum and maximum triangular colorbar\n                  extensions as a fraction of the interior colorbar\n                  length. A two-element sequence of fractions may also\n                  be given, indicating the lengths of the minimum and\n                  maximum colorbar extensions respectively as a\n                  fraction of the interior colorbar length.\n    *spacing*     [ 'uniform' | 'proportional' ]\n                  Uniform spacing gives each discrete color the same\n                  space; proportional makes the space proportional to\n                  the data interval.\n    *ticks*       [ None | list of ticks | Locator object ]\n                  If None, ticks are determined automatically from the\n                  input.\n    *format*      [ None | format string | Formatter object ]\n                  If None, the\n                  :class:`~matplotlib.ticker.ScalarFormatter` is used.\n                  If a format string is given, e.g. '%.3f', that is\n                  used. An alternative\n                  :class:`~matplotlib.ticker.Formatter` object may be\n                  given instead.\n    *drawedges*   [ False | True ] If true, draw lines at color\n                  boundaries.\n    ============  ====================================================\n\n    The following will probably be useful only in the context of\n    indexed colors (that is, when the mappable has norm=NoNorm()),\n    or other unusual circumstances.\n\n    ============   ===================================================\n    Property       Description\n    ============   ===================================================\n    *boundaries*   None or a sequence\n    *values*       None or a sequence which must be of length 1 less\n                   than the sequence of *boundaries*. For each region\n                   delimited by adjacent entries in *boundaries*, the\n                   color mapped to the corresponding value in values\n                   will be used.\n    ============   ===================================================\n\n"
colorbar_doc = '\n\nAdd a colorbar to a plot.\n\nFunction signatures for the :mod:`~matplotlib.pyplot` interface; all\nbut the first are also method signatures for the\n:meth:`~matplotlib.figure.Figure.colorbar` method::\n\n  colorbar(**kwargs)\n  colorbar(mappable, **kwargs)\n  colorbar(mappable, cax=cax, **kwargs)\n  colorbar(mappable, ax=ax, **kwargs)\n\narguments:\n\n  *mappable*\n    the :class:`~matplotlib.image.Image`,\n    :class:`~matplotlib.contour.ContourSet`, etc. to\n    which the colorbar applies; this argument is mandatory for the\n    :meth:`~matplotlib.figure.Figure.colorbar` method but optional for the\n    :func:`~matplotlib.pyplot.colorbar` function, which sets the\n    default to the current image.\n\nkeyword arguments:\n\n  *cax*\n    None | axes object into which the colorbar will be drawn\n  *ax*\n    None | parent axes object from which space for a new\n    colorbar axes will be stolen\n  *use_gridspec*\n    False | If *cax* is None, a new *cax* is created as an instance of\n    Axes. If *ax* is an instance of Subplot and *use_gridspec* is True,\n    *cax* is created as an instance of Subplot using the\n    grid_spec module.\n\n\nAdditional keyword arguments are of two kinds:\n\n  axes properties:\n%s\n  colorbar properties:\n%s\n\nIf *mappable* is a :class:`~matplotlib.contours.ContourSet`, its *extend*\nkwarg is included automatically.\n\nNote that the *shrink* kwarg provides a simple way to keep a vertical\ncolorbar, for example, from being taller than the axes of the mappable\nto which the colorbar is attached; but it is a manual method requiring\nsome trial and error. If the colorbar is too tall (or a horizontal\ncolorbar is too wide) use a smaller value of *shrink*.\n\nFor more precise control, you can manually specify the positions of\nthe axes objects in which the mappable and the colorbar are drawn.  In\nthis case, do not use any of the axes properties kwargs.\n\nIt is known that some vector graphics viewer (svg and pdf) renders white gaps\nbetween segments of the colorbar. This is due to bugs in the viewers not\nmatplotlib. As a workaround the colorbar can be rendered with overlapping\nsegments::\n\n    cbar = colorbar()\n    cbar.solids.set_edgecolor("face")\n    draw()\n\nHowever this has negative consequences in other circumstances. Particularly with\nsemi transparent images (alpha < 1) and colorbar extensions and is not enabled\nby default see (issue #1188).\n\nreturns:\n    :class:`~matplotlib.colorbar.Colorbar` instance; see also its base class,\n    :class:`~matplotlib.colorbar.ColorbarBase`.  Call the\n    :meth:`~matplotlib.colorbar.ColorbarBase.set_label` method\n    to label the colorbar.\n\n' % (make_axes_kw_doc, colormap_kw_doc)
docstring.interpd.update(colorbar_doc=colorbar_doc)

def _set_ticks_on_axis_warn(*args, **kw):
    warnings.warn('Use the colorbar set_ticks() method instead.')


class ColorbarBase(cm.ScalarMappable):
    """
    Draw a colorbar in an existing axes.

    This is a base class for the :class:`Colorbar` class, which is the
    basis for the :func:`~matplotlib.pyplot.colorbar` function and the
    :meth:`~matplotlib.figure.Figure.colorbar` method, which are the
    usual ways of creating a colorbar.

    It is also useful by itself for showing a colormap.  If the *cmap*
    kwarg is given but *boundaries* and *values* are left as None,
    then the colormap will be displayed on a 0-1 scale. To show the
    under- and over-value colors, specify the *norm* as::

        colors.Normalize(clip=False)

    To show the colors versus index instead of on the 0-1 scale,
    use::

        norm=colors.NoNorm.

    Useful attributes:

        :attr:`ax`
            the Axes instance in which the colorbar is drawn

        :attr:`lines`
            a list of LineCollection if lines were drawn, otherwise
            an empty list

        :attr:`dividers`
            a LineCollection if *drawedges* is True, otherwise None

    Useful public methods are :meth:`set_label` and :meth:`add_lines`.

    """
    _slice_dict = {'neither': slice(0, None), 'both': slice(1, -1), 
       'min': slice(1, None), 
       'max': slice(0, -1)}

    def __init__(self, ax, cmap=None, norm=None, alpha=None, values=None, boundaries=None, orientation='vertical', extend='neither', spacing='uniform', ticks=None, format=None, drawedges=False, filled=True, extendfrac=None):
        self.ax = ax
        self._patch_ax()
        if cmap is None:
            cmap = cm.get_cmap()
        if norm is None:
            norm = colors.Normalize()
        self.alpha = alpha
        cm.ScalarMappable.__init__(self, cmap=cmap, norm=norm)
        self.values = values
        self.boundaries = boundaries
        self.extend = extend
        self._inside = self._slice_dict[extend]
        self.spacing = spacing
        self.orientation = orientation
        self.drawedges = drawedges
        self.filled = filled
        self.extendfrac = extendfrac
        self.solids = None
        self.lines = list()
        self.outline = None
        self.patch = None
        self.dividers = None
        self.set_label('')
        if cbook.iterable(ticks):
            self.locator = ticker.FixedLocator(ticks, nbins=len(ticks))
        else:
            self.locator = ticks
        if format is None:
            if isinstance(self.norm, colors.LogNorm):
                self.formatter = ticker.LogFormatterMathtext()
            else:
                self.formatter = ticker.ScalarFormatter()
        elif cbook.is_string_like(format):
            self.formatter = ticker.FormatStrFormatter(format)
        else:
            self.formatter = format
        self.config_axis()
        self.draw_all()
        return

    def _extend_lower(self):
        """Returns whether the lower limit is open ended."""
        return self.extend in ('both', 'min')

    def _extend_upper(self):
        """Returns whether the uper limit is open ended."""
        return self.extend in ('both', 'max')

    def _patch_ax(self):
        self.ax.set_xticks = _set_ticks_on_axis_warn
        self.ax.set_yticks = _set_ticks_on_axis_warn

    def draw_all(self):
        """
        Calculate any free parameters based on the current cmap and norm,
        and do all the drawing.
        """
        self._process_values()
        self._find_range()
        X, Y = self._mesh()
        C = self._values[:, np.newaxis]
        self._config_axes(X, Y)
        if self.filled:
            self._add_solids(X, Y, C)

    def config_axis(self):
        ax = self.ax
        if self.orientation == 'vertical':
            ax.xaxis.set_ticks([])
            ax.yaxis.set_label_position('right')
            ax.yaxis.set_ticks_position('right')
        else:
            ax.yaxis.set_ticks([])
            ax.xaxis.set_label_position('bottom')
        self._set_label()

    def update_ticks(self):
        """
        Force the update of the ticks and ticklabels. This must be
        called whenever the tick locator and/or tick formatter changes.
        """
        ax = self.ax
        ticks, ticklabels, offset_string = self._ticker()
        if self.orientation == 'vertical':
            ax.yaxis.set_ticks(ticks)
            ax.set_yticklabels(ticklabels)
            ax.yaxis.get_major_formatter().set_offset_string(offset_string)
        else:
            ax.xaxis.set_ticks(ticks)
            ax.set_xticklabels(ticklabels)
            ax.xaxis.get_major_formatter().set_offset_string(offset_string)

    def set_ticks(self, ticks, update_ticks=True):
        """
        set tick locations. Tick locations are updated immediately unless update_ticks is
        *False*. To manually update the ticks, call *update_ticks* method explicitly.
        """
        if cbook.iterable(ticks):
            self.locator = ticker.FixedLocator(ticks, nbins=len(ticks))
        else:
            self.locator = ticks
        if update_ticks:
            self.update_ticks()

    def set_ticklabels(self, ticklabels, update_ticks=True):
        """
        set tick labels. Tick labels are updated immediately unless update_ticks is
        *False*. To manually update the ticks, call *update_ticks* method explicitly.
        """
        if isinstance(self.locator, ticker.FixedLocator):
            self.formatter = ticker.FixedFormatter(ticklabels)
            if update_ticks:
                self.update_ticks()
        else:
            warnings.warn('set_ticks() must have been called.')

    def _config_axes(self, X, Y):
        """
        Make an axes patch and outline.
        """
        ax = self.ax
        ax.set_frame_on(False)
        ax.set_navigate(False)
        xy = self._outline(X, Y)
        ax.update_datalim(xy)
        ax.set_xlim(*ax.dataLim.intervalx)
        ax.set_ylim(*ax.dataLim.intervaly)
        if self.outline is not None:
            self.outline.remove()
        self.outline = lines.Line2D(xy[:, 0], xy[:, 1], color=mpl.rcParams['axes.edgecolor'], linewidth=mpl.rcParams['axes.linewidth'])
        ax.add_artist(self.outline)
        self.outline.set_clip_box(None)
        self.outline.set_clip_path(None)
        c = mpl.rcParams['axes.facecolor']
        if self.patch is not None:
            self.patch.remove()
        self.patch = mpatches.Polygon(xy, edgecolor=c, facecolor=c, linewidth=0.01, zorder=-1)
        ax.add_artist(self.patch)
        self.update_ticks()
        return

    def _set_label(self):
        if self.orientation == 'vertical':
            self.ax.set_ylabel(self._label, **self._labelkw)
        else:
            self.ax.set_xlabel(self._label, **self._labelkw)

    def set_label(self, label, **kw):
        """
        Label the long axis of the colorbar
        """
        self._label = '%s' % (label,)
        self._labelkw = kw
        self._set_label()

    def _outline(self, X, Y):
        """
        Return *x*, *y* arrays of colorbar bounding polygon,
        taking orientation into account.
        """
        N = X.shape[0]
        ii = [0, 1, N - 2, N - 1, 2 * N - 1, 2 * N - 2, N + 1, N, 0]
        x = np.take(np.ravel(np.transpose(X)), ii)
        y = np.take(np.ravel(np.transpose(Y)), ii)
        x = x.reshape((len(x), 1))
        y = y.reshape((len(y), 1))
        if self.orientation == 'horizontal':
            return np.hstack((y, x))
        return np.hstack((x, y))

    def _edges(self, X, Y):
        """
        Return the separator line segments; helper for _add_solids.
        """
        N = X.shape[0]
        if self.orientation == 'vertical':
            return [ zip(X[i], Y[i]) for i in xrange(1, N - 1) ]
        else:
            return [ zip(Y[i], X[i]) for i in xrange(1, N - 1) ]

    def _add_solids(self, X, Y, C):
        """
        Draw the colors using :meth:`~matplotlib.axes.Axes.pcolormesh`;
        optionally add separators.
        """
        if self.orientation == 'vertical':
            args = (
             X, Y, C)
        else:
            args = (
             np.transpose(Y), np.transpose(X), np.transpose(C))
        kw = dict(cmap=self.cmap, norm=self.norm, alpha=self.alpha, edgecolors='None')
        _hold = self.ax.ishold()
        self.ax.hold(True)
        col = self.ax.pcolormesh(*args, **kw)
        self.ax.hold(_hold)
        if self.solids is not None:
            self.solids.remove()
        self.solids = col
        if self.dividers is not None:
            self.dividers.remove()
            self.dividers = None
        if self.drawedges:
            self.dividers = collections.LineCollection(self._edges(X, Y), colors=(
             mpl.rcParams['axes.edgecolor'],), linewidths=(
             0.5 * mpl.rcParams['axes.linewidth'],))
            self.ax.add_collection(self.dividers)
        return

    def add_lines(self, levels, colors, linewidths, erase=True):
        """
        Draw lines on the colorbar.

        *colors* and *linewidths* must be scalars or
        sequences the same length as *levels*.

        Set *erase* to False to add lines without first
        removing any previously added lines.
        """
        y = self._locate(levels)
        nlevs = len(levels)
        igood = (y < 1.001) & (y > -0.001)
        y = y[igood]
        if cbook.iterable(colors):
            colors = np.asarray(colors)[igood]
        if cbook.iterable(linewidths):
            linewidths = np.asarray(linewidths)[igood]
        N = len(y)
        x = np.array([0.0, 1.0])
        X, Y = np.meshgrid(x, y)
        if self.orientation == 'vertical':
            xy = [ zip(X[i], Y[i]) for i in xrange(N) ]
        else:
            xy = [ zip(Y[i], X[i]) for i in xrange(N) ]
        col = collections.LineCollection(xy, linewidths=linewidths)
        if erase and self.lines:
            for lc in self.lines:
                lc.remove()

            self.lines = []
        self.lines.append(col)
        col.set_color(colors)
        self.ax.add_collection(col)

    def _ticker(self):
        """
        Return two sequences: ticks (colorbar data locations)
        and ticklabels (strings).
        """
        locator = self.locator
        formatter = self.formatter
        if locator is None:
            if self.boundaries is None:
                if isinstance(self.norm, colors.NoNorm):
                    nv = len(self._values)
                    base = 1 + int(nv / 10)
                    locator = ticker.IndexLocator(base=base, offset=0)
                elif isinstance(self.norm, colors.BoundaryNorm):
                    b = self.norm.boundaries
                    locator = ticker.FixedLocator(b, nbins=10)
                else:
                    if isinstance(self.norm, colors.LogNorm):
                        locator = ticker.LogLocator()
                    else:
                        locator = ticker.MaxNLocator()
            else:
                b = self._boundaries[self._inside]
                locator = ticker.FixedLocator(b, nbins=10)
        if isinstance(self.norm, colors.NoNorm):
            intv = (
             self._values[0], self._values[-1])
        else:
            intv = (
             self.vmin, self.vmax)
        locator.create_dummy_axis(minpos=intv[0])
        formatter.create_dummy_axis(minpos=intv[0])
        locator.set_view_interval(*intv)
        locator.set_data_interval(*intv)
        formatter.set_view_interval(*intv)
        formatter.set_data_interval(*intv)
        b = np.array(locator())
        ticks = self._locate(b)
        inrange = (ticks > -0.001) & (ticks < 1.001)
        ticks = ticks[inrange]
        b = b[inrange]
        formatter.set_locs(b)
        ticklabels = [ formatter(t, i) for i, t in enumerate(b) ]
        offset_string = formatter.get_offset()
        return (ticks, ticklabels, offset_string)

    def _process_values(self, b=None):
        """
        Set the :attr:`_boundaries` and :attr:`_values` attributes
        based on the input boundaries and values.  Input boundaries
        can be *self.boundaries* or the argument *b*.
        """
        if b is None:
            b = self.boundaries
        if b is not None:
            self._boundaries = np.asarray(b, dtype=float)
            if self.values is None:
                self._values = 0.5 * (self._boundaries[:-1] + self._boundaries[1:])
                if isinstance(self.norm, colors.NoNorm):
                    self._values = (self._values + 1e-05).astype(np.int16)
                return
            self._values = np.array(self.values)
            return
        else:
            if self.values is not None:
                self._values = np.array(self.values)
                if self.boundaries is None:
                    b = np.zeros(len(self.values) + 1, 'd')
                    b[1:(-1)] = 0.5 * (self._values[:-1] - self._values[1:])
                    b[0] = 2.0 * b[1] - b[2]
                    b[-1] = 2.0 * b[-2] - b[-3]
                    self._boundaries = b
                    return
                self._boundaries = np.array(self.boundaries)
                return
            if isinstance(self.norm, colors.NoNorm):
                b = self._uniform_y(self.cmap.N + 1) * self.cmap.N - 0.5
                v = np.zeros((len(b) - 1,), dtype=np.int16)
                v[self._inside] = np.arange(self.cmap.N, dtype=np.int16)
                if self._extend_lower():
                    v[0] = -1
                if self._extend_upper():
                    v[-1] = self.cmap.N
                self._boundaries = b
                self._values = v
                return
            if isinstance(self.norm, colors.BoundaryNorm):
                b = list(self.norm.boundaries)
                if self._extend_lower():
                    b = [
                     b[0] - 1] + b
                if self._extend_upper():
                    b = b + [b[-1] + 1]
                b = np.array(b)
                v = np.zeros((len(b) - 1,), dtype=float)
                bi = self.norm.boundaries
                v[self._inside] = 0.5 * (bi[:-1] + bi[1:])
                if self._extend_lower():
                    v[0] = b[0] - 1
                if self._extend_upper():
                    v[-1] = b[-1] + 1
                self._boundaries = b
                self._values = v
                return
            if not self.norm.scaled():
                self.norm.vmin = 0
                self.norm.vmax = 1
            b = self.norm.inverse(self._uniform_y(self.cmap.N + 1))
            if self._extend_lower():
                b[0] = b[0] - 1
            if self._extend_upper():
                b[-1] = b[-1] + 1
            self._process_values(b)
            return

    def _find_range(self):
        """
        Set :attr:`vmin` and :attr:`vmax` attributes to the first and
        last boundary excluding extended end boundaries.
        """
        b = self._boundaries[self._inside]
        self.vmin = b[0]
        self.vmax = b[-1]

    def _central_N(self):
        """number of boundaries **before** extension of ends"""
        nb = len(self._boundaries)
        if self.extend == 'both':
            nb -= 2
        elif self.extend in ('min', 'max'):
            nb -= 1
        return nb

    def _extended_N(self):
        """
        Based on the colormap and extend variable, return the
        number of boundaries.
        """
        N = self.cmap.N + 1
        if self.extend == 'both':
            N += 2
        elif self.extend in ('min', 'max'):
            N += 1
        return N

    def _get_extension_lengths(self, frac, automin, automax, default=0.05):
        """
        Get the lengths of colorbar extensions.

        A helper method for _uniform_y and _proportional_y.
        """
        extendlength = np.array([default, default])
        if isinstance(frac, str):
            if frac.lower() == 'auto':
                extendlength[0] = automin
                extendlength[1] = automax
            else:
                raise ValueError('invalid value for extendfrac')
        elif frac is not None:
            try:
                extendlength[:] = frac
                if np.isnan(extendlength).any():
                    raise ValueError()
            except (TypeError, ValueError):
                raise ValueError('invalid value for extendfrac')

        return extendlength

    def _uniform_y(self, N):
        """
        Return colorbar data coordinates for *N* uniformly
        spaced boundaries, plus ends if required.
        """
        if self.extend == 'neither':
            y = np.linspace(0, 1, N)
        else:
            automin = automax = 1.0 / (N - 1.0)
            extendlength = self._get_extension_lengths(self.extendfrac, automin, automax, default=0.05)
            if self.extend == 'both':
                y = np.zeros(N + 2, 'd')
                y[0] = 0.0 - extendlength[0]
                y[-1] = 1.0 + extendlength[1]
            elif self.extend == 'min':
                y = np.zeros(N + 1, 'd')
                y[0] = 0.0 - extendlength[0]
            else:
                y = np.zeros(N + 1, 'd')
                y[-1] = 1.0 + extendlength[1]
            y[self._inside] = np.linspace(0, 1, N)
        return y

    def _proportional_y(self):
        """
        Return colorbar data coordinates for the boundaries of
        a proportional colorbar.
        """
        if isinstance(self.norm, colors.BoundaryNorm):
            b = self._boundaries[self._inside]
            y = self._boundaries - self._boundaries[0]
            y = y / (self._boundaries[-1] - self._boundaries[0])
        else:
            y = self.norm(self._boundaries.copy())
        if self.extend == 'min':
            clen = y[-1] - y[1]
            automin = (y[2] - y[1]) / clen
            automax = (y[-1] - y[-2]) / clen
        elif self.extend == 'max':
            clen = y[-2] - y[0]
            automin = (y[1] - y[0]) / clen
            automax = (y[-2] - y[-3]) / clen
        else:
            clen = y[-2] - y[1]
            automin = (y[2] - y[1]) / clen
            automax = (y[-2] - y[-3]) / clen
        extendlength = self._get_extension_lengths(self.extendfrac, automin, automax, default=0.05)
        if self.extend in ('both', 'min'):
            y[0] = 0.0 - extendlength[0]
        if self.extend in ('both', 'max'):
            y[-1] = 1.0 + extendlength[1]
        yi = y[self._inside]
        norm = colors.Normalize(yi[0], yi[-1])
        y[self._inside] = norm(yi)
        return y

    def _mesh(self):
        """
        Return X,Y, the coordinate arrays for the colorbar pcolormesh.
        These are suitable for a vertical colorbar; swapping and
        transposition for a horizontal colorbar are done outside
        this function.
        """
        x = np.array([0.0, 1.0])
        if self.spacing == 'uniform':
            y = self._uniform_y(self._central_N())
        else:
            y = self._proportional_y()
        self._y = y
        X, Y = np.meshgrid(x, y)
        if self._extend_lower():
            X[0, :] = 0.5
        if self._extend_upper():
            X[-1, :] = 0.5
        return (
         X, Y)

    def _locate(self, x):
        """
        Given a set of color data values, return their
        corresponding colorbar data coordinates.
        """
        if isinstance(self.norm, (colors.NoNorm, colors.BoundaryNorm)):
            b = self._boundaries
            xn = x
        else:
            b = self.norm(self._boundaries, clip=False).filled()
            xn = self.norm(x, clip=False).filled()
        y = self._y
        N = len(b)
        ii = np.searchsorted(b, xn)
        i0 = ii - 1
        itop = ii == N
        ibot = ii == 0
        i0[itop] -= 1
        ii[itop] -= 1
        i0[ibot] += 1
        ii[ibot] += 1
        db = np.take(b, ii) - np.take(b, i0)
        dy = np.take(y, ii) - np.take(y, i0)
        z = np.take(y, i0) + (xn - np.take(b, i0)) * dy / db
        return z

    def set_alpha(self, alpha):
        self.alpha = alpha


class Colorbar(ColorbarBase):
    """
    This class connects a :class:`ColorbarBase` to a
    :class:`~matplotlib.cm.ScalarMappable` such as a
    :class:`~matplotlib.image.AxesImage` generated via
    :meth:`~matplotlib.axes.Axes.imshow`.

    It is not intended to be instantiated directly; instead,
    use :meth:`~matplotlib.figure.Figure.colorbar` or
    :func:`~matplotlib.pyplot.colorbar` to make your colorbar.

    """

    def __init__(self, ax, mappable, **kw):
        mappable.autoscale_None()
        self.mappable = mappable
        kw['cmap'] = mappable.cmap
        kw['norm'] = mappable.norm
        if isinstance(mappable, contour.ContourSet):
            CS = mappable
            kw['alpha'] = mappable.get_alpha()
            kw['boundaries'] = CS._levels
            kw['values'] = CS.cvalues
            kw['extend'] = CS.extend
            kw.setdefault('ticks', ticker.FixedLocator(CS.levels, nbins=10))
            kw['filled'] = CS.filled
            ColorbarBase.__init__(self, ax, **kw)
            if not CS.filled:
                self.add_lines(CS)
        else:
            if isinstance(mappable, martist.Artist):
                kw['alpha'] = mappable.get_alpha()
            ColorbarBase.__init__(self, ax, **kw)

    def on_mappable_changed(self, mappable):
        """
        Updates this colorbar to match the mappable's properties.

        Typically this is automatically registered as an event handler
        by :func:`colorbar_factory` and should not be called manually.

        """
        self.set_cmap(mappable.get_cmap())
        self.set_clim(mappable.get_clim())
        self.update_normal(mappable)

    def add_lines(self, CS, erase=True):
        """
        Add the lines from a non-filled
        :class:`~matplotlib.contour.ContourSet` to the colorbar.

        Set *erase* to False if these lines should be added to
        any pre-existing lines.
        """
        if not isinstance(CS, contour.ContourSet) or CS.filled:
            raise ValueError('add_lines is only for a ContourSet of lines')
        tcolors = [ c[0] for c in CS.tcolors ]
        tlinewidths = [ t[0] for t in CS.tlinewidths ]
        ColorbarBase.add_lines(self, CS.levels, tcolors, tlinewidths, erase=erase)

    def update_normal(self, mappable):
        """
        update solid, lines, etc. Unlike update_bruteforce, it does
        not clear the axes.  This is meant to be called when the image
        or contour plot to which this colorbar belongs is changed.
        """
        self.draw_all()
        if isinstance(self.mappable, contour.ContourSet):
            CS = self.mappable
            if not CS.filled:
                self.add_lines(CS)

    def update_bruteforce(self, mappable):
        """
        Destroy and rebuild the colorbar.  This is
        intended to become obsolete, and will probably be
        deprecated and then removed.  It is not called when
        the pyplot.colorbar function or the Figure.colorbar
        method are used to create the colorbar.

        """
        self.ax.cla()
        self.outline = None
        self.patch = None
        self.solids = None
        self.lines = list()
        self.dividers = None
        self.set_alpha(mappable.get_alpha())
        self.cmap = mappable.cmap
        self.norm = mappable.norm
        self.config_axis()
        self.draw_all()
        if isinstance(self.mappable, contour.ContourSet):
            CS = self.mappable
            if not CS.filled:
                self.add_lines(CS)
        return


@docstring.Substitution(make_axes_kw_doc)
def make_axes(parent, **kw):
    """
    Resize and reposition a parent axes, and return a child
    axes suitable for a colorbar::

        cax, kw = make_axes(parent, **kw)

    Keyword arguments may include the following (with defaults):

        *orientation*
            'vertical'  or 'horizontal'

    %s

    All but the first of these are stripped from the input kw set.

    Returns (cax, kw), the child axes and the reduced kw dictionary.
    """
    orientation = kw.setdefault('orientation', 'vertical')
    fraction = kw.pop('fraction', 0.15)
    shrink = kw.pop('shrink', 1.0)
    aspect = kw.pop('aspect', 20)
    pb = parent.get_position(original=True).frozen()
    if orientation == 'vertical':
        pad = kw.pop('pad', 0.05)
        x1 = 1.0 - fraction
        pb1, pbx, pbcb = pb.splitx(x1 - pad, x1)
        pbcb = pbcb.shrunk(1.0, shrink).anchored('C', pbcb)
        anchor = kw.pop('anchor', (0.0, 0.5))
        panchor = kw.pop('panchor', (1.0, 0.5))
    else:
        pad = kw.pop('pad', 0.15)
        pbcb, pbx, pb1 = pb.splity(fraction, fraction + pad)
        pbcb = pbcb.shrunk(shrink, 1.0).anchored('C', pbcb)
        aspect = 1.0 / aspect
        anchor = kw.pop('anchor', (0.5, 1.0))
        panchor = kw.pop('panchor', (0.5, 0.0))
    parent.set_position(pb1)
    parent.set_anchor(panchor)
    fig = parent.get_figure()
    cax = fig.add_axes(pbcb)
    cax.set_aspect(aspect, anchor=anchor, adjustable='box')
    return (cax, kw)


@docstring.Substitution(make_axes_kw_doc)
def make_axes_gridspec(parent, **kw):
    """
    Resize and reposition a parent axes, and return a child axes
    suitable for a colorbar. This function is similar to
    make_axes. Prmary differences are

     * *make_axes_gridspec* should only be used with a subplot parent.

     * *make_axes* creates an instance of Axes. *make_axes_gridspec*
        creates an instance of Subplot.

     * *make_axes* updates the position of the
        parent. *make_axes_gridspec* replaces the grid_spec attribute
        of the parent with a new one.

    While this function is meant to be compatible with *make_axes*,
    there could be some minor differences.::

        cax, kw = make_axes_gridspec(parent, **kw)

    Keyword arguments may include the following (with defaults):

        *orientation*
            'vertical'  or 'horizontal'

    %s

    All but the first of these are stripped from the input kw set.

    Returns (cax, kw), the child axes and the reduced kw dictionary.
    """
    orientation = kw.setdefault('orientation', 'vertical')
    fraction = kw.pop('fraction', 0.15)
    shrink = kw.pop('shrink', 1.0)
    aspect = kw.pop('aspect', 20)
    x1 = 1.0 - fraction
    pad_s = (1.0 - shrink) * 0.5
    wh_ratios = [pad_s, shrink, pad_s]
    gs_from_subplotspec = gridspec.GridSpecFromSubplotSpec
    if orientation == 'vertical':
        pad = kw.pop('pad', 0.05)
        wh_space = 2 * pad / (1 - pad)
        gs = gs_from_subplotspec(1, 2, subplot_spec=parent.get_subplotspec(), wspace=wh_space, width_ratios=[
         x1 - pad, fraction])
        gs2 = gs_from_subplotspec(3, 1, subplot_spec=gs[1], hspace=0.0, height_ratios=wh_ratios)
        anchor = (0.0, 0.5)
        panchor = (1.0, 0.5)
    else:
        pad = kw.pop('pad', 0.15)
        wh_space = 2 * pad / (1 - pad)
        gs = gs_from_subplotspec(2, 1, subplot_spec=parent.get_subplotspec(), hspace=wh_space, height_ratios=[
         x1 - pad, fraction])
        gs2 = gs_from_subplotspec(1, 3, subplot_spec=gs[1], wspace=0.0, width_ratios=wh_ratios)
        aspect = 1.0 / aspect
        anchor = (0.5, 1.0)
        panchor = (0.5, 0.0)
    parent.set_subplotspec(gs[0])
    parent.update_params()
    parent.set_position(parent.figbox)
    parent.set_anchor(panchor)
    fig = parent.get_figure()
    cax = fig.add_subplot(gs2[1])
    cax.set_aspect(aspect, anchor=anchor, adjustable='box')
    return (cax, kw)


class ColorbarPatch(Colorbar):
    """
    A Colorbar which is created using :class:`~matplotlib.patches.Patch`
    rather than the default :func:`~matplotlib.axes.pcolor`.

    It uses a list of Patch instances instead of a
    :class:`~matplotlib.collections.PatchCollection` because the
    latter does not allow the hatch pattern to vary among the
    members of the collection.
    """

    def __init__(self, ax, mappable, **kw):
        self.solids_patches = []
        Colorbar.__init__(self, ax, mappable, **kw)

    def _add_solids(self, X, Y, C):
        """
        Draw the colors using :class:`~matplotlib.patches.Patch`;
        optionally add separators.
        """
        _hold = self.ax.ishold()
        self.ax.hold(True)
        kw = {'alpha': self.alpha}
        n_segments = len(C)
        hatches = self.mappable.hatches * n_segments
        patches = []
        for i in xrange(len(X) - 1):
            val = C[i][0]
            hatch = hatches[i]
            xy = np.array([[X[i][0], Y[i][0]], [X[i][1], Y[i][0]],
             [
              X[i + 1][1], Y[i + 1][0]], [X[i + 1][0], Y[i + 1][1]]])
            if self.orientation == 'horizontal':
                xy = xy[..., ::-1]
            patch = mpatches.PathPatch(mpath.Path(xy), facecolor=self.cmap(self.norm(val)), hatch=hatch, edgecolor='none', linewidth=0, antialiased=False, **kw)
            self.ax.add_patch(patch)
            patches.append(patch)

        if self.solids_patches:
            for solid in self.solids_patches:
                solid.remove()

        self.solids_patches = patches
        if self.dividers is not None:
            self.dividers.remove()
            self.dividers = None
        if self.drawedges:
            self.dividers = collections.LineCollection(self._edges(X, Y), colors=(
             mpl.rcParams['axes.edgecolor'],), linewidths=(
             0.5 * mpl.rcParams['axes.linewidth'],))
            self.ax.add_collection(self.dividers)
        self.ax.hold(_hold)
        return


def colorbar_factory(cax, mappable, **kwargs):
    """
    Creates a colorbar on the given axes for the given mappable.

    Typically, for automatic colorbar placement given only a mappable use
    :meth:`~matplotlib.figure.Figure.colorbar`.

    """
    if isinstance(mappable, contour.ContourSet) and any([ hatch is not None for hatch in mappable.hatches ]):
        cb = ColorbarPatch(cax, mappable, **kwargs)
    else:
        cb = Colorbar(cax, mappable, **kwargs)
    mappable.callbacksSM.connect('changed', cb.on_mappable_changed)
    mappable.set_colorbar(cb, cax)
    return cb