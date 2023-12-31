# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\collections.pyc
# Compiled at: 2012-11-08 06:38:04
"""
Classes for the efficient drawing of large collections of objects that
share most properties, e.g. a large number of line segments or
polygons.

The classes are not meant to be as flexible as their single element
counterparts (e.g. you may not be able to select all line styles) but
they are meant to be fast for common use cases (e.g. a large set of solid
line segemnts)
"""
from __future__ import print_function
import warnings, numpy as np, numpy.ma as ma, matplotlib as mpl, matplotlib.cbook as cbook, matplotlib.colors as mcolors, matplotlib.cm as cm
from matplotlib import docstring
import matplotlib.transforms as transforms, matplotlib.artist as artist
from matplotlib.artist import allow_rasterization
import matplotlib.backend_bases as backend_bases, matplotlib.path as mpath, matplotlib.mlab as mlab

class Collection(artist.Artist, cm.ScalarMappable):
    """
    Base class for Collections.  Must be subclassed to be usable.

    All properties in a collection must be sequences or scalars;
    if scalars, they will be converted to sequences.  The
    property of the ith element of the collection is::

      prop[i % len(props)]

    Keyword arguments and default values:

        * *edgecolors*: None
        * *facecolors*: None
        * *linewidths*: None
        * *antialiaseds*: None
        * *offsets*: None
        * *transOffset*: transforms.IdentityTransform()
        * *offset_position*: 'screen' (default) or 'data'
        * *norm*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)
        * *cmap*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)
        * *hatch*: None

    *offsets* and *transOffset* are used to translate the patch after
    rendering (default no offsets).  If offset_position is 'screen'
    (default) the offset is applied after the master transform has
    been applied, that is, the offsets are in screen coordinates.  If
    offset_position is 'data', the offset is applied before the master
    transform, i.e., the offsets are in data coordinates.

    If any of *edgecolors*, *facecolors*, *linewidths*, *antialiaseds*
    are None, they default to their :data:`matplotlib.rcParams` patch
    setting, in sequence form.

    The use of :class:`~matplotlib.cm.ScalarMappable` is optional.  If
    the :class:`~matplotlib.cm.ScalarMappable` matrix _A is not None
    (ie a call to set_array has been made), at draw time a call to
    scalar mappable will be made to set the face colors.
    """
    _offsets = np.array([], np.float_)
    _offsets.shape = (0, 2)
    _transOffset = transforms.IdentityTransform()
    _transforms = []
    zorder = 1

    def __init__(self, edgecolors=None, facecolors=None, linewidths=None, linestyles='solid', antialiaseds=None, offsets=None, transOffset=None, norm=None, cmap=None, pickradius=5.0, hatch=None, urls=None, offset_position='screen', **kwargs):
        """
        Create a Collection

        %(Collection)s
        """
        artist.Artist.__init__(self)
        cm.ScalarMappable.__init__(self, norm, cmap)
        self.set_edgecolor(edgecolors)
        self.set_facecolor(facecolors)
        self.set_linewidth(linewidths)
        self.set_linestyle(linestyles)
        self.set_antialiased(antialiaseds)
        self.set_pickradius(pickradius)
        self.set_urls(urls)
        self.set_hatch(hatch)
        self.set_offset_position(offset_position)
        self._uniform_offsets = None
        self._offsets = np.array([], np.float_)
        self._offsets.shape = (0, 2)
        if offsets is not None:
            offsets = np.asanyarray(offsets)
            offsets.shape = (-1, 2)
            if transOffset is not None:
                self._offsets = offsets
                self._transOffset = transOffset
            else:
                self._uniform_offsets = offsets
        self.update(kwargs)
        self._paths = None
        return

    @staticmethod
    def _get_value(val):
        try:
            return (
             float(val),)
        except TypeError:
            if cbook.iterable(val) and len(val):
                try:
                    float(val[0])
                except (TypeError, ValueError):
                    pass
                else:
                    return val

        raise TypeError('val must be a float or nonzero sequence of floats')

    @staticmethod
    def _get_bool(val):
        if not cbook.iterable(val):
            val = (
             val,)
        try:
            bool(val[0])
        except (TypeError, IndexError):
            raise TypeError('val must be a bool or nonzero sequence of them')

        return val

    def get_paths(self):
        return self._paths

    def set_paths(self):
        raise NotImplementedError

    def get_transforms(self):
        return self._transforms

    def get_offset_transform(self):
        t = self._transOffset
        if not isinstance(t, transforms.Transform) and hasattr(t, '_as_mpl_transform'):
            t = t._as_mpl_transform(self.axes)
        return t

    def get_datalim(self, transData):
        transform = self.get_transform()
        transOffset = self.get_offset_transform()
        offsets = self._offsets
        paths = self.get_paths()
        if not transform.is_affine:
            paths = [ transform.transform_path_non_affine(p) for p in paths ]
            transform = transform.get_affine()
        if not transOffset.is_affine:
            offsets = transOffset.transform_non_affine(offsets)
            transOffset = transOffset.get_affine()
        offsets = np.asanyarray(offsets, np.float_)
        if np.ma.isMaskedArray(offsets):
            offsets = offsets.filled(np.nan)
        offsets.shape = (-1, 2)
        result = mpath.get_path_collection_extents(transform.frozen(), paths, self.get_transforms(), offsets, transOffset.frozen())
        result = result.inverse_transformed(transData)
        return result

    def get_window_extent(self, renderer):
        bbox = self.get_datalim(transforms.IdentityTransform())
        return bbox

    def _prepare_points(self):
        """Point prep for drawing and hit testing"""
        transform = self.get_transform()
        transOffset = self.get_offset_transform()
        offsets = self._offsets
        paths = self.get_paths()
        if self.have_units():
            paths = []
            for path in self.get_paths():
                vertices = path.vertices
                xs, ys = vertices[:, 0], vertices[:, 1]
                xs = self.convert_xunits(xs)
                ys = self.convert_yunits(ys)
                paths.append(mpath.Path(zip(xs, ys), path.codes))

            if offsets.size > 0:
                xs = self.convert_xunits(offsets[:, 0])
                ys = self.convert_yunits(offsets[:, 1])
                offsets = zip(xs, ys)
        offsets = np.asanyarray(offsets, np.float_)
        offsets.shape = (-1, 2)
        if not transform.is_affine:
            paths = [ transform.transform_path_non_affine(path) for path in paths ]
            transform = transform.get_affine()
        if not transOffset.is_affine:
            offsets = transOffset.transform_non_affine(offsets)
            transOffset = transOffset.get_affine()
        if np.ma.isMaskedArray(offsets):
            offsets = offsets.filled(np.nan)
        return (
         transform, transOffset, offsets, paths)

    @allow_rasterization
    def draw(self, renderer):
        if not self.get_visible():
            return
        renderer.open_group(self.__class__.__name__, self.get_gid())
        self.update_scalarmappable()
        transform, transOffset, offsets, paths = self._prepare_points()
        gc = renderer.new_gc()
        self._set_gc_clip(gc)
        gc.set_snap(self.get_snap())
        if self._hatch:
            gc.set_hatch(self._hatch)
        renderer.draw_path_collection(gc, transform.frozen(), paths, self.get_transforms(), offsets, transOffset, self.get_facecolor(), self.get_edgecolor(), self._linewidths, self._linestyles, self._antialiaseds, self._urls, self._offset_position)
        gc.restore()
        renderer.close_group(self.__class__.__name__)

    def set_pickradius(self, pr):
        self._pickradius = pr

    def get_pickradius(self):
        return self._pickradius

    def contains(self, mouseevent):
        """
        Test whether the mouse event occurred in the collection.

        Returns True | False, ``dict(ind=itemlist)``, where every
        item in itemlist contains the event.
        """
        if callable(self._contains):
            return self._contains(self, mouseevent)
        if not self.get_visible():
            return (False, {})
        if self._picker is True:
            pickradius = self._pickradius
        else:
            try:
                pickradius = float(self._picker)
            except TypeError:
                warnings.warn('Collection picker %s could not be converted to float' % self._picker)
                pickradius = self._pickradius

        transform, transOffset, offsets, paths = self._prepare_points()
        ind = mpath.point_in_path_collection(mouseevent.x, mouseevent.y, pickradius, transform.frozen(), paths, self.get_transforms(), offsets, transOffset, pickradius <= 0)
        return (
         len(ind) > 0, dict(ind=ind))

    def set_urls(self, urls):
        if urls is None:
            self._urls = [
             None]
        else:
            self._urls = urls
        return

    def get_urls(self):
        return self._urls

    def set_hatch(self, hatch):
        r"""
        Set the hatching pattern

        *hatch* can be one of::

          /   - diagonal hatching
          \   - back diagonal
          |   - vertical
          -   - horizontal
          +   - crossed
          x   - crossed diagonal
          o   - small circle
          O   - large circle
          .   - dots
          *   - stars

        Letters can be combined, in which case all the specified
        hatchings are done.  If same letter repeats, it increases the
        density of hatching of that pattern.

        Hatching is supported in the PostScript, PDF, SVG and Agg
        backends only.

        Unlike other properties such as linewidth and colors, hatching
        can only be specified for the collection as a whole, not separately
        for each member.

        ACCEPTS: [ '/' | '\\' | '|' | '-' | '+' | 'x' | 'o' | 'O' | '.' | '*' ]
        """
        self._hatch = hatch

    def get_hatch(self):
        """Return the current hatching pattern"""
        return self._hatch

    def set_offsets(self, offsets):
        """
        Set the offsets for the collection.  *offsets* can be a scalar
        or a sequence.

        ACCEPTS: float or sequence of floats
        """
        offsets = np.asanyarray(offsets, np.float_)
        offsets.shape = (-1, 2)
        if self._uniform_offsets is None:
            self._offsets = offsets
        else:
            self._uniform_offsets = offsets
        return

    def get_offsets(self):
        """
        Return the offsets for the collection.
        """
        if self._uniform_offsets is None:
            return self._offsets
        else:
            return self._uniform_offsets
            return

    def set_offset_position(self, offset_position):
        """
        Set how offsets are applied.  If *offset_position* is 'screen'
        (default) the offset is applied after the master transform has
        been applied, that is, the offsets are in screen coordinates.
        If offset_position is 'data', the offset is applied before the
        master transform, i.e., the offsets are in data coordinates.
        """
        if offset_position not in ('screen', 'data'):
            raise ValueError("offset_position must be 'screen' or 'data'")
        self._offset_position = offset_position

    def get_offset_position(self):
        """
        Returns how offsets are applied for the collection.  If
        *offset_position* is 'screen', the offset is applied after the
        master transform has been applied, that is, the offsets are in
        screen coordinates.  If offset_position is 'data', the offset
        is applied before the master transform, i.e., the offsets are
        in data coordinates.
        """
        return self._offset_position

    def set_linewidth(self, lw):
        """
        Set the linewidth(s) for the collection.  *lw* can be a scalar
        or a sequence; if it is a sequence the patches will cycle
        through the sequence

        ACCEPTS: float or sequence of floats
        """
        if lw is None:
            lw = mpl.rcParams['patch.linewidth']
        self._linewidths = self._get_value(lw)
        return

    def set_linewidths(self, lw):
        """alias for set_linewidth"""
        return self.set_linewidth(lw)

    def set_lw(self, lw):
        """alias for set_linewidth"""
        return self.set_linewidth(lw)

    def set_linestyle(self, ls):
        """
        Set the linestyle(s) for the collection.

        ACCEPTS: ['solid' | 'dashed', 'dashdot', 'dotted' |
        (offset, on-off-dash-seq) ]
        """
        try:
            dashd = backend_bases.GraphicsContextBase.dashd
            if cbook.is_string_like(ls):
                if ls in dashd:
                    dashes = [
                     dashd[ls]]
                else:
                    if ls in cbook.ls_mapper:
                        dashes = [
                         dashd[cbook.ls_mapper[ls]]]
                    else:
                        raise ValueError()
            elif cbook.iterable(ls):
                try:
                    dashes = []
                    for x in ls:
                        if cbook.is_string_like(x):
                            if x in dashd:
                                dashes.append(dashd[x])
                            else:
                                if x in cbook.ls_mapper:
                                    dashes.append(dashd[cbook.ls_mapper[x]])
                                else:
                                    raise ValueError()
                        elif cbook.iterable(x) and len(x) == 2:
                            dashes.append(x)
                        else:
                            raise ValueError()

                except ValueError:
                    if len(ls) == 2:
                        dashes = ls
                    else:
                        raise ValueError()

            else:
                raise ValueError()
        except ValueError:
            raise ValueError('Do not know how to convert %s to dashes' % ls)

        self._linestyles = dashes

    def set_linestyles(self, ls):
        """alias for set_linestyle"""
        return self.set_linestyle(ls)

    def set_dashes(self, ls):
        """alias for set_linestyle"""
        return self.set_linestyle(ls)

    def set_antialiased(self, aa):
        """
        Set the antialiasing state for rendering.

        ACCEPTS: Boolean or sequence of booleans
        """
        if aa is None:
            aa = mpl.rcParams['patch.antialiased']
        self._antialiaseds = self._get_bool(aa)
        return

    def set_antialiaseds(self, aa):
        """alias for set_antialiased"""
        return self.set_antialiased(aa)

    def set_color(self, c):
        """
        Set both the edgecolor and the facecolor.

        ACCEPTS: matplotlib color arg or sequence of rgba tuples

        .. seealso::

            :meth:`set_facecolor`, :meth:`set_edgecolor`
               For setting the edge or face color individually.
        """
        self.set_facecolor(c)
        self.set_edgecolor(c)

    def set_facecolor(self, c):
        """
        Set the facecolor(s) of the collection.  *c* can be a
        matplotlib color arg (all patches have same color), or a
        sequence of rgba tuples; if it is a sequence the patches will
        cycle through the sequence.

        If *c* is 'none', the patch will not be filled.

        ACCEPTS: matplotlib color arg or sequence of rgba tuples
        """
        self._is_filled = True
        try:
            if c.lower() == 'none':
                self._is_filled = False
        except AttributeError:
            pass

        if c is None:
            c = mpl.rcParams['patch.facecolor']
        self._facecolors_original = c
        self._facecolors = mcolors.colorConverter.to_rgba_array(c, self._alpha)
        return

    def set_facecolors(self, c):
        """alias for set_facecolor"""
        return self.set_facecolor(c)

    def get_facecolor(self):
        return self._facecolors

    get_facecolors = get_facecolor

    def get_edgecolor(self):
        if self._edgecolors == 'face':
            return self.get_facecolors()
        else:
            return self._edgecolors

    get_edgecolors = get_edgecolor

    def set_edgecolor(self, c):
        """
        Set the edgecolor(s) of the collection. *c* can be a
        matplotlib color arg (all patches have same color), or a
        sequence of rgba tuples; if it is a sequence the patches will
        cycle through the sequence.

        If *c* is 'face', the edge color will always be the same as
        the face color.  If it is 'none', the patch boundary will not
        be drawn.

        ACCEPTS: matplotlib color arg or sequence of rgba tuples
        """
        self._is_stroked = True
        try:
            if c.lower() == 'none':
                self._is_stroked = False
        except AttributeError:
            pass

        try:
            if c.lower() == 'face':
                self._edgecolors = 'face'
                self._edgecolors_original = 'face'
                return
        except AttributeError:
            pass

        if c is None:
            c = mpl.rcParams['patch.edgecolor']
        self._edgecolors_original = c
        self._edgecolors = mcolors.colorConverter.to_rgba_array(c, self._alpha)
        return

    def set_edgecolors(self, c):
        """alias for set_edgecolor"""
        return self.set_edgecolor(c)

    def set_alpha(self, alpha):
        """
        Set the alpha tranparencies of the collection.  *alpha* must be
        a float or *None*.

        ACCEPTS: float or None
        """
        if alpha is not None:
            try:
                float(alpha)
            except TypeError:
                raise TypeError('alpha must be a float or None')

        artist.Artist.set_alpha(self, alpha)
        try:
            self._facecolors = mcolors.colorConverter.to_rgba_array(self._facecolors_original, self._alpha)
        except (AttributeError, TypeError, IndexError):
            pass

        try:
            if self._edgecolors_original != 'face':
                self._edgecolors = mcolors.colorConverter.to_rgba_array(self._edgecolors_original, self._alpha)
        except (AttributeError, TypeError, IndexError):
            pass

        return

    def get_linewidths(self):
        return self._linewidths

    get_linewidth = get_linewidths

    def get_linestyles(self):
        return self._linestyles

    get_dashes = get_linestyle = get_linestyles

    def update_scalarmappable(self):
        """
        If the scalar mappable array is not none, update colors
        from scalar data
        """
        if self._A is None:
            return
        else:
            if self._A.ndim > 1:
                raise ValueError('Collections can only map rank 1 arrays')
            if not self.check_update('array'):
                return
            if self._is_filled:
                self._facecolors = self.to_rgba(self._A, self._alpha)
            elif self._is_stroked:
                self._edgecolors = self.to_rgba(self._A, self._alpha)
            return

    def update_from(self, other):
        """copy properties from other to self"""
        artist.Artist.update_from(self, other)
        self._antialiaseds = other._antialiaseds
        self._edgecolors_original = other._edgecolors_original
        self._edgecolors = other._edgecolors
        self._facecolors_original = other._facecolors_original
        self._facecolors = other._facecolors
        self._linewidths = other._linewidths
        self._linestyles = other._linestyles
        self._pickradius = other._pickradius
        self._hatch = other._hatch
        self._A = other._A
        self.norm = other.norm
        self.cmap = other.cmap


docstring.interpd.update(Collection='    Valid Collection keyword arguments:\n\n        * *edgecolors*: None\n        * *facecolors*: None\n        * *linewidths*: None\n        * *antialiaseds*: None\n        * *offsets*: None\n        * *transOffset*: transforms.IdentityTransform()\n        * *norm*: None (optional for\n          :class:`matplotlib.cm.ScalarMappable`)\n        * *cmap*: None (optional for\n          :class:`matplotlib.cm.ScalarMappable`)\n\n    *offsets* and *transOffset* are used to translate the patch after\n    rendering (default no offsets)\n\n    If any of *edgecolors*, *facecolors*, *linewidths*, *antialiaseds*\n    are None, they default to their :data:`matplotlib.rcParams` patch\n    setting, in sequence form.\n')

class PathCollection(Collection):
    """
    This is the most basic :class:`Collection` subclass.
    """

    @docstring.dedent_interpd
    def __init__(self, paths, sizes=None, **kwargs):
        """
        *paths* is a sequence of :class:`matplotlib.path.Path`
        instances.

        %(Collection)s
        """
        Collection.__init__(self, **kwargs)
        self.set_paths(paths)
        self._sizes = sizes

    def set_paths(self, paths):
        self._paths = paths

    def get_paths(self):
        return self._paths

    def get_sizes(self):
        return self._sizes

    @allow_rasterization
    def draw(self, renderer):
        if self._sizes is not None:
            self._transforms = [ transforms.Affine2D().scale(np.sqrt(x) * self.figure.dpi / 72.0) for x in self._sizes
                               ]
        return Collection.draw(self, renderer)


class PolyCollection(Collection):

    @docstring.dedent_interpd
    def __init__(self, verts, sizes=None, closed=True, **kwargs):
        """
        *verts* is a sequence of ( *verts0*, *verts1*, ...) where
        *verts_i* is a sequence of *xy* tuples of vertices, or an
        equivalent :mod:`numpy` array of shape (*nv*, 2).

        *sizes* is *None* (default) or a sequence of floats that
        scale the corresponding *verts_i*.  The scaling is applied
        before the Artist master transform; if the latter is an identity
        transform, then the overall scaling is such that if
        *verts_i* specify a unit square, then *sizes_i* is the area
        of that square in points^2.
        If len(*sizes*) < *nv*, the additional values will be
        taken cyclically from the array.

        *closed*, when *True*, will explicitly close the polygon.

        %(Collection)s
        """
        Collection.__init__(self, **kwargs)
        self._sizes = sizes
        self.set_verts(verts, closed)

    def set_verts(self, verts, closed=True):
        """This allows one to delay initialization of the vertices."""
        if np.ma.isMaskedArray(verts):
            verts = verts.astype(np.float_).filled(np.nan)
        if closed:
            self._paths = []
            for xy in verts:
                if len(xy):
                    if np.ma.isMaskedArray(xy):
                        xy = np.ma.concatenate([xy, np.zeros((1, 2))])
                    else:
                        xy = np.asarray(xy)
                        xy = np.concatenate([xy, np.zeros((1, 2))])
                    codes = np.empty(xy.shape[0], dtype=mpath.Path.code_type)
                    codes[:] = mpath.Path.LINETO
                    codes[0] = mpath.Path.MOVETO
                    codes[-1] = mpath.Path.CLOSEPOLY
                    self._paths.append(mpath.Path(xy, codes))
                else:
                    self._paths.append(mpath.Path(xy))

        else:
            self._paths = [ mpath.Path(xy) for xy in verts ]

    set_paths = set_verts

    @allow_rasterization
    def draw(self, renderer):
        if self._sizes is not None:
            self._transforms = [ transforms.Affine2D().scale(np.sqrt(x) * self.figure.dpi / 72.0) for x in self._sizes
                               ]
        return Collection.draw(self, renderer)


class BrokenBarHCollection(PolyCollection):
    """
    A collection of horizontal bars spanning *yrange* with a sequence of
    *xranges*.
    """

    @docstring.dedent_interpd
    def __init__(self, xranges, yrange, **kwargs):
        """
        *xranges*
            sequence of (*xmin*, *xwidth*)

        *yrange*
            *ymin*, *ywidth*

        %(Collection)s
        """
        ymin, ywidth = yrange
        ymax = ymin + ywidth
        verts = [ [(xmin, ymin), (xmin, ymax), (xmin + xwidth, ymax), (xmin + xwidth, ymin), (xmin, ymin)] for xmin, xwidth in xranges ]
        PolyCollection.__init__(self, verts, **kwargs)

    @staticmethod
    def span_where(x, ymin, ymax, where, **kwargs):
        """
        Create a BrokenBarHCollection to plot horizontal bars from
        over the regions in *x* where *where* is True.  The bars range
        on the y-axis from *ymin* to *ymax*

        A :class:`BrokenBarHCollection` is returned.  *kwargs* are
        passed on to the collection.
        """
        xranges = []
        for ind0, ind1 in mlab.contiguous_regions(where):
            xslice = x[ind0:ind1]
            if not len(xslice):
                continue
            xranges.append((xslice[0], xslice[-1] - xslice[0]))

        collection = BrokenBarHCollection(xranges, [ymin, ymax - ymin], **kwargs)
        return collection


class RegularPolyCollection(Collection):
    """Draw a collection of regular polygons with *numsides*."""
    _path_generator = mpath.Path.unit_regular_polygon

    @docstring.dedent_interpd
    def __init__(self, numsides, rotation=0, sizes=(1, ), **kwargs):
        """
        *numsides*
            the number of sides of the polygon

        *rotation*
            the rotation of the polygon in radians

        *sizes*
            gives the area of the circle circumscribing the
            regular polygon in points^2

        %(Collection)s

        Example: see :file:`examples/dynamic_collection.py` for
        complete example::

            offsets = np.random.rand(20,2)
            facecolors = [cm.jet(x) for x in np.random.rand(20)]
            black = (0,0,0,1)

            collection = RegularPolyCollection(
                numsides=5, # a pentagon
                rotation=0, sizes=(50,),
                facecolors = facecolors,
                edgecolors = (black,),
                linewidths = (1,),
                offsets = offsets,
                transOffset = ax.transData,
                )
        """
        Collection.__init__(self, **kwargs)
        self._sizes = sizes
        self._numsides = numsides
        self._paths = [self._path_generator(numsides)]
        self._rotation = rotation
        self.set_transform(transforms.IdentityTransform())

    @allow_rasterization
    def draw(self, renderer):
        self._transforms = [ transforms.Affine2D().rotate(-self._rotation).scale(np.sqrt(x) * self.figure.dpi / 72.0 / np.sqrt(np.pi)) for x in self._sizes
                           ]
        return Collection.draw(self, renderer)

    def get_numsides(self):
        return self._numsides

    def get_rotation(self):
        return self._rotation

    def get_sizes(self):
        return self._sizes


class StarPolygonCollection(RegularPolyCollection):
    """
    Draw a collection of regular stars with *numsides* points."""
    _path_generator = mpath.Path.unit_regular_star


class AsteriskPolygonCollection(RegularPolyCollection):
    """
    Draw a collection of regular asterisks with *numsides* points."""
    _path_generator = mpath.Path.unit_regular_asterisk


class LineCollection(Collection):
    """
    All parameters must be sequences or scalars; if scalars, they will
    be converted to sequences.  The property of the ith line
    segment is::

       prop[i % len(props)]

    i.e., the properties cycle if the ``len`` of props is less than the
    number of segments.
    """
    zorder = 2

    def __init__(self, segments, linewidths=None, colors=None, antialiaseds=None, linestyles='solid', offsets=None, transOffset=None, norm=None, cmap=None, pickradius=5, **kwargs):
        """
        *segments*
            a sequence of (*line0*, *line1*, *line2*), where::

                linen = (x0, y0), (x1, y1), ... (xm, ym)

            or the equivalent numpy array with two columns. Each line
            can be a different length.

        *colors*
            must be a sequence of RGBA tuples (eg arbitrary color
            strings, etc, not allowed).

        *antialiaseds*
            must be a sequence of ones or zeros

        *linestyles* [ 'solid' | 'dashed' | 'dashdot' | 'dotted' ]
            a string or dash tuple. The dash tuple is::

                (offset, onoffseq),

            where *onoffseq* is an even length tuple of on and off ink
            in points.

        If *linewidths*, *colors*, or *antialiaseds* is None, they
        default to their rcParams setting, in sequence form.

        If *offsets* and *transOffset* are not None, then
        *offsets* are transformed by *transOffset* and applied after
        the segments have been transformed to display coordinates.

        If *offsets* is not None but *transOffset* is None, then the
        *offsets* are added to the segments before any transformation.
        In this case, a single offset can be specified as::

            offsets=(xo,yo)

        and this value will be added cumulatively to each successive
        segment, so as to produce a set of successively offset curves.

        *norm*
            None (optional for :class:`matplotlib.cm.ScalarMappable`)
        *cmap*
            None (optional for :class:`matplotlib.cm.ScalarMappable`)

        *pickradius* is the tolerance for mouse clicks picking a line.
        The default is 5 pt.

        The use of :class:`~matplotlib.cm.ScalarMappable` is optional.
        If the :class:`~matplotlib.cm.ScalarMappable` array
        :attr:`~matplotlib.cm.ScalarMappable._A` is not None (ie a call to
        :meth:`~matplotlib.cm.ScalarMappable.set_array` has been made), at
        draw time a call to scalar mappable will be made to set the colors.
        """
        if colors is None:
            colors = mpl.rcParams['lines.color']
        if linewidths is None:
            linewidths = (mpl.rcParams['lines.linewidth'],)
        if antialiaseds is None:
            antialiaseds = (mpl.rcParams['lines.antialiased'],)
        self.set_linestyles(linestyles)
        colors = mcolors.colorConverter.to_rgba_array(colors)
        Collection.__init__(self, edgecolors=colors, facecolors='none', linewidths=linewidths, linestyles=linestyles, antialiaseds=antialiaseds, offsets=offsets, transOffset=transOffset, norm=norm, cmap=cmap, pickradius=pickradius, **kwargs)
        self.set_segments(segments)
        return

    def set_segments(self, segments):
        if segments is None:
            return
        else:
            _segments = []
            for seg in segments:
                if not np.ma.isMaskedArray(seg):
                    seg = np.asarray(seg, np.float_)
                _segments.append(seg)

            if self._uniform_offsets is not None:
                _segments = self._add_offsets(_segments)
            self._paths = [ mpath.Path(seg) for seg in _segments ]
            return

    set_verts = set_segments
    set_paths = set_segments

    def _add_offsets(self, segs):
        offsets = self._uniform_offsets
        Nsegs = len(segs)
        Noffs = offsets.shape[0]
        if Noffs == 1:
            for i in range(Nsegs):
                segs[i] = segs[i] + i * offsets

        else:
            for i in range(Nsegs):
                io = i % Noffs
                segs[i] = segs[i] + offsets[io:io + 1]

        return segs

    def set_color(self, c):
        """
        Set the color(s) of the line collection.  *c* can be a
        matplotlib color arg (all patches have same color), or a
        sequence or rgba tuples; if it is a sequence the patches will
        cycle through the sequence.

        ACCEPTS: matplotlib color arg or sequence of rgba tuples
        """
        self.set_edgecolor(c)

    def color(self, c):
        """
        Set the color(s) of the line collection.  *c* can be a
        matplotlib color arg (all patches have same color), or a
        sequence or rgba tuples; if it is a sequence the patches will
        cycle through the sequence

        ACCEPTS: matplotlib color arg or sequence of rgba tuples
        """
        warnings.warn('LineCollection.color deprecated; use set_color instead')
        return self.set_color(c)

    def get_color(self):
        return self._edgecolors

    get_colors = get_color


class CircleCollection(Collection):
    """
    A collection of circles, drawn using splines.
    """

    @docstring.dedent_interpd
    def __init__(self, sizes, **kwargs):
        """
        *sizes*
            Gives the area of the circle in points^2

        %(Collection)s
        """
        Collection.__init__(self, **kwargs)
        self._sizes = sizes
        self.set_transform(transforms.IdentityTransform())
        self._paths = [mpath.Path.unit_circle()]

    def get_sizes(self):
        """return sizes of circles"""
        return self._sizes

    @allow_rasterization
    def draw(self, renderer):
        self._transforms = [ transforms.Affine2D().scale(np.sqrt(x) * self.figure.dpi / 72.0 / np.sqrt(np.pi)) for x in self._sizes
                           ]
        return Collection.draw(self, renderer)


class EllipseCollection(Collection):
    """
    A collection of ellipses, drawn using splines.
    """

    @docstring.dedent_interpd
    def __init__(self, widths, heights, angles, units='points', **kwargs):
        """
        *widths*: sequence
            lengths of first axes (e.g., major axis lengths)

        *heights*: sequence
            lengths of second axes

        *angles*: sequence
            angles of first axes, degrees CCW from the X-axis

        *units*: ['points' | 'inches' | 'dots' | 'width' | 'height'
        | 'x' | 'y' | 'xy']

            units in which majors and minors are given; 'width' and
            'height' refer to the dimensions of the axes, while 'x'
            and 'y' refer to the *offsets* data units. 'xy' differs
            from all others in that the angle as plotted varies with
            the aspect ratio, and equals the specified angle only when
            the aspect ratio is unity.  Hence it behaves the same as
            the :class:`~matplotlib.patches.Ellipse` with
            axes.transData as its transform.

        Additional kwargs inherited from the base :class:`Collection`:

        %(Collection)s
        """
        Collection.__init__(self, **kwargs)
        self._widths = 0.5 * np.asarray(widths).ravel()
        self._heights = 0.5 * np.asarray(heights).ravel()
        self._angles = np.asarray(angles).ravel() * (np.pi / 180.0)
        self._units = units
        self.set_transform(transforms.IdentityTransform())
        self._transforms = []
        self._paths = [mpath.Path.unit_circle()]

    def _set_transforms(self):
        """
        Calculate transforms immediately before drawing.
        """
        self._transforms = []
        ax = self.axes
        fig = self.figure
        if self._units == 'xy':
            sc = 1
        else:
            if self._units == 'x':
                sc = ax.bbox.width / ax.viewLim.width
            else:
                if self._units == 'y':
                    sc = ax.bbox.height / ax.viewLim.height
                else:
                    if self._units == 'inches':
                        sc = fig.dpi
                    else:
                        if self._units == 'points':
                            sc = fig.dpi / 72.0
                        else:
                            if self._units == 'width':
                                sc = ax.bbox.width
                            else:
                                if self._units == 'height':
                                    sc = ax.bbox.height
                                elif self._units == 'dots':
                                    sc = 1.0
                                else:
                                    raise ValueError('unrecognized units: %s' % self._units)
            _affine = transforms.Affine2D
            for x, y, a in zip(self._widths, self._heights, self._angles):
                trans = _affine().scale(x * sc, y * sc).rotate(a)
                self._transforms.append(trans)

        if self._units == 'xy':
            m = ax.transData.get_affine().get_matrix().copy()
            m[:2, 2:] = 0
            self.set_transform(_affine(m))

    @allow_rasterization
    def draw(self, renderer):
        self._set_transforms()
        Collection.draw(self, renderer)


class PatchCollection(Collection):
    """
    A generic collection of patches.

    This makes it easier to assign a color map to a heterogeneous
    collection of patches.

    This also may improve plotting speed, since PatchCollection will
    draw faster than a large number of patches.
    """

    def __init__(self, patches, match_original=False, **kwargs):
        """
        *patches*
            a sequence of Patch objects.  This list may include
            a heterogeneous assortment of different patch types.

        *match_original*
            If True, use the colors and linewidths of the original
            patches.  If False, new colors may be assigned by
            providing the standard collection arguments, facecolor,
            edgecolor, linewidths, norm or cmap.

        If any of *edgecolors*, *facecolors*, *linewidths*,
        *antialiaseds* are None, they default to their
        :data:`matplotlib.rcParams` patch setting, in sequence form.

        The use of :class:`~matplotlib.cm.ScalarMappable` is optional.
        If the :class:`~matplotlib.cm.ScalarMappable` matrix _A is not
        None (ie a call to set_array has been made), at draw time a
        call to scalar mappable will be made to set the face colors.
        """
        if match_original:

            def determine_facecolor(patch):
                if patch.get_fill():
                    return patch.get_facecolor()
                return [
                 0, 0, 0, 0]

            facecolors = [ determine_facecolor(p) for p in patches ]
            edgecolors = [ p.get_edgecolor() for p in patches ]
            linewidths = [ p.get_linewidth() for p in patches ]
            linestyles = [ p.get_linestyle() for p in patches ]
            antialiaseds = [ p.get_antialiased() for p in patches ]
            Collection.__init__(self, edgecolors=edgecolors, facecolors=facecolors, linewidths=linewidths, linestyles=linestyles, antialiaseds=antialiaseds)
        else:
            Collection.__init__(self, **kwargs)
        self.set_paths(patches)

    def set_paths(self, patches):
        paths = [ p.get_transform().transform_path(p.get_path()) for p in patches
                ]
        self._paths = paths


class TriMesh(Collection):
    """
    Class for the efficient drawing of a triangular mesh using
    Gouraud shading.

    A triangular mesh is a :class:`~matplotlib.tri.Triangulation`
    object.
    """

    def __init__(self, triangulation, **kwargs):
        Collection.__init__(self, **kwargs)
        self._triangulation = triangulation
        self._shading = 'gouraud'
        self._is_filled = True
        self._bbox = transforms.Bbox.unit()
        xy = np.hstack((triangulation.x.reshape(-1, 1),
         triangulation.y.reshape(-1, 1)))
        self._bbox.update_from_data_xy(xy)

    def get_paths(self):
        if self._paths is None:
            self.set_paths()
        return self._paths

    def set_paths(self):
        self._paths = self.convert_mesh_to_paths(self._triangulation)

    @staticmethod
    def convert_mesh_to_paths(tri):
        """
        Converts a given mesh into a sequence of
        :class:`matplotlib.path.Path` objects for easier rendering by
        backends that do not directly support meshes.

        This function is primarily of use to backend implementers.
        """
        Path = mpath.Path
        triangles = tri.get_masked_triangles()
        verts = np.concatenate((tri.x[triangles][(..., np.newaxis)],
         tri.y[triangles][(..., np.newaxis)]), axis=2)
        return [ Path(x) for x in verts ]

    @allow_rasterization
    def draw(self, renderer):
        if not self.get_visible():
            return
        renderer.open_group(self.__class__.__name__)
        transform = self.get_transform()
        tri = self._triangulation
        triangles = tri.get_masked_triangles()
        verts = np.concatenate((tri.x[triangles][(..., np.newaxis)],
         tri.y[triangles][(..., np.newaxis)]), axis=2)
        self.update_scalarmappable()
        colors = self._facecolors[triangles]
        gc = renderer.new_gc()
        self._set_gc_clip(gc)
        gc.set_linewidth(self.get_linewidth()[0])
        renderer.draw_gouraud_triangles(gc, verts, colors, transform.frozen())
        gc.restore()
        renderer.close_group(self.__class__.__name__)


class QuadMesh(Collection):
    """
    Class for the efficient drawing of a quadrilateral mesh.

    A quadrilateral mesh consists of a grid of vertices. The
    dimensions of this array are (*meshWidth* + 1, *meshHeight* +
    1). Each vertex in the mesh has a different set of "mesh
    coordinates" representing its position in the topology of the
    mesh. For any values (*m*, *n*) such that 0 <= *m* <= *meshWidth*
    and 0 <= *n* <= *meshHeight*, the vertices at mesh coordinates
    (*m*, *n*), (*m*, *n* + 1), (*m* + 1, *n* + 1), and (*m* + 1, *n*)
    form one of the quadrilaterals in the mesh. There are thus
    (*meshWidth* * *meshHeight*) quadrilaterals in the mesh.  The mesh
    need not be regular and the polygons need not be convex.

    A quadrilateral mesh is represented by a (2 x ((*meshWidth* + 1) *
    (*meshHeight* + 1))) numpy array *coordinates*, where each row is
    the *x* and *y* coordinates of one of the vertices.  To define the
    function that maps from a data point to its corresponding color,
    use the :meth:`set_cmap` method.  Each of these arrays is indexed in
    row-major order by the mesh coordinates of the vertex (or the mesh
    coordinates of the lower left vertex, in the case of the
    colors).

    For example, the first entry in *coordinates* is the
    coordinates of the vertex at mesh coordinates (0, 0), then the one
    at (0, 1), then at (0, 2) .. (0, meshWidth), (1, 0), (1, 1), and
    so on.

    *shading* may be 'flat', or 'gouraud'
    """

    def __init__(self, meshWidth, meshHeight, coordinates, antialiased=True, shading='flat', **kwargs):
        Collection.__init__(self, **kwargs)
        self._meshWidth = meshWidth
        self._meshHeight = meshHeight
        self._coordinates = coordinates
        self._antialiased = antialiased
        self._shading = shading
        self._bbox = transforms.Bbox.unit()
        self._bbox.update_from_data_xy(coordinates.reshape((
         (meshWidth + 1) * (meshHeight + 1), 2)))
        self._coordinates = self._coordinates.reshape((meshHeight + 1, meshWidth + 1, 2))
        self._coordinates = np.array(self._coordinates, np.float_)

    def get_paths(self):
        if self._paths is None:
            self.set_paths()
        return self._paths

    def set_paths(self):
        self._paths = self.convert_mesh_to_paths(self._meshWidth, self._meshHeight, self._coordinates)

    @staticmethod
    def convert_mesh_to_paths(meshWidth, meshHeight, coordinates):
        """
        Converts a given mesh into a sequence of
        :class:`matplotlib.path.Path` objects for easier rendering by
        backends that do not directly support quadmeshes.

        This function is primarily of use to backend implementers.
        """
        Path = mpath.Path
        if ma.isMaskedArray(coordinates):
            c = coordinates.data
        else:
            c = coordinates
        points = np.concatenate((
         c[0:-1, 0:-1],
         c[0:-1, 1:],
         c[1:, 1:],
         c[1:, 0:-1],
         c[0:-1, 0:-1]), axis=2)
        points = points.reshape((meshWidth * meshHeight, 5, 2))
        return [ Path(x) for x in points ]

    def convert_mesh_to_triangles(self, meshWidth, meshHeight, coordinates):
        """
        Converts a given mesh into a sequence of triangles, each point
        with its own color.  This is useful for experiments using
        `draw_qouraud_triangle`.
        """
        Path = mpath.Path
        if ma.isMaskedArray(coordinates):
            p = coordinates.data
        else:
            p = coordinates
        p_a = p[0:-1, 0:-1]
        p_b = p[0:-1, 1:]
        p_c = p[1:, 1:]
        p_d = p[1:, 0:-1]
        p_center = (p_a + p_b + p_c + p_d) / 4.0
        triangles = np.concatenate((
         p_a, p_b, p_center,
         p_b, p_c, p_center,
         p_c, p_d, p_center,
         p_d, p_a, p_center), axis=2)
        triangles = triangles.reshape((meshWidth * meshHeight * 4, 3, 2))
        c = self.get_facecolor().reshape((meshHeight + 1, meshWidth + 1, 4))
        c_a = c[0:-1, 0:-1]
        c_b = c[0:-1, 1:]
        c_c = c[1:, 1:]
        c_d = c[1:, 0:-1]
        c_center = (c_a + c_b + c_c + c_d) / 4.0
        colors = np.concatenate((
         c_a, c_b, c_center,
         c_b, c_c, c_center,
         c_c, c_d, c_center,
         c_d, c_a, c_center), axis=2)
        colors = colors.reshape((meshWidth * meshHeight * 4, 3, 4))
        return (
         triangles, colors)

    def get_datalim(self, transData):
        return self._bbox

    @allow_rasterization
    def draw(self, renderer):
        if not self.get_visible():
            return
        renderer.open_group(self.__class__.__name__, self.get_gid())
        transform = self.get_transform()
        transOffset = self.get_offset_transform()
        offsets = self._offsets
        if self.have_units():
            if len(self._offsets):
                xs = self.convert_xunits(self._offsets[:0])
                ys = self.convert_yunits(self._offsets[:1])
                offsets = zip(xs, ys)
        offsets = np.asarray(offsets, np.float_)
        offsets.shape = (-1, 2)
        self.update_scalarmappable()
        if not transform.is_affine:
            coordinates = self._coordinates.reshape((
             self._coordinates.shape[0] * self._coordinates.shape[1],
             2))
            coordinates = transform.transform(coordinates)
            coordinates = coordinates.reshape(self._coordinates.shape)
            transform = transforms.IdentityTransform()
        else:
            coordinates = self._coordinates
        if not transOffset.is_affine:
            offsets = transOffset.transform_non_affine(offsets)
            transOffset = transOffset.get_affine()
        gc = renderer.new_gc()
        self._set_gc_clip(gc)
        gc.set_linewidth(self.get_linewidth()[0])
        if self._shading == 'gouraud':
            triangles, colors = self.convert_mesh_to_triangles(self._meshWidth, self._meshHeight, coordinates)
            renderer.draw_gouraud_triangles(gc, triangles, colors, transform.frozen())
        else:
            renderer.draw_quad_mesh(gc, transform.frozen(), self._meshWidth, self._meshHeight, coordinates, offsets, transOffset, self.get_facecolor(), self._antialiased, self.get_edgecolors())
        gc.restore()
        renderer.close_group(self.__class__.__name__)


patchstr = artist.kwdoc(Collection)
for k in ('QuadMesh', 'TriMesh', 'PolyCollection', 'BrokenBarHCollection',
 'RegularPolyCollection', 'PathCollection',
 'StarPolygonCollection', 'PatchCollection',
 'CircleCollection', 'Collection'):
    docstring.interpd.update({k: patchstr})

docstring.interpd.update(LineCollection=artist.kwdoc(LineCollection))