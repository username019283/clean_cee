# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_agg.pyc
# Compiled at: 2012-10-30 18:11:14
"""
An agg http://antigrain.com/ backend

Features that are implemented

 * capstyles and join styles
 * dashes
 * linewidth
 * lines, rectangles, ellipses
 * clipping to a rectangle
 * output to RGBA and PNG
 * alpha blending
 * DPI scaling properly - everything scales properly (dashes, linewidths, etc)
 * draw polygon
 * freetype2 w/ ft2font

TODO:

  * allow save to file handle

  * integrate screen dpi w/ ppi and text
"""
from __future__ import division
import threading, numpy as np
from matplotlib import verbose, rcParams
from matplotlib.backend_bases import RendererBase, FigureManagerBase, FigureCanvasBase
from matplotlib.cbook import is_string_like, maxdict
from matplotlib.figure import Figure
from matplotlib.font_manager import findfont
from matplotlib.ft2font import FT2Font, LOAD_FORCE_AUTOHINT, LOAD_NO_HINTING, LOAD_DEFAULT, LOAD_NO_AUTOHINT
from matplotlib.mathtext import MathTextParser
from matplotlib.path import Path
from matplotlib.transforms import Bbox, BboxBase
from matplotlib.backends._backend_agg import RendererAgg as _RendererAgg
from matplotlib import _png
backend_version = 'v2.2'

def get_hinting_flag():
    mapping = {True: LOAD_FORCE_AUTOHINT, 
       False: LOAD_NO_HINTING, 
       'either': LOAD_DEFAULT, 
       'native': LOAD_NO_AUTOHINT, 
       'auto': LOAD_FORCE_AUTOHINT, 
       'none': LOAD_NO_HINTING}
    return mapping[rcParams['text.hinting']]


class RendererAgg(RendererBase):
    """
    The renderer handles all the drawing primitives using a graphics
    context instance that controls the colors/styles
    """
    debug = 1
    lock = threading.RLock()
    _fontd = maxdict(50)

    def __init__(self, width, height, dpi):
        verbose.report('RendererAgg.__init__', 'debug-annoying')
        RendererBase.__init__(self)
        self.texd = maxdict(50)
        self.dpi = dpi
        self.width = width
        self.height = height
        verbose.report('RendererAgg.__init__ width=%s, height=%s' % (width, height), 'debug-annoying')
        self._renderer = _RendererAgg(int(width), int(height), dpi, debug=False)
        self._filter_renderers = []
        verbose.report('RendererAgg.__init__ _RendererAgg done', 'debug-annoying')
        self._update_methods()
        self.mathtext_parser = MathTextParser('Agg')
        self.bbox = Bbox.from_bounds(0, 0, self.width, self.height)
        verbose.report('RendererAgg.__init__ done', 'debug-annoying')

    def _get_hinting_flag(self):
        if rcParams['text.hinting']:
            return LOAD_FORCE_AUTOHINT
        else:
            return LOAD_NO_HINTING

    def draw_markers(self, *kl, **kw):
        return self._renderer.draw_markers(*kl, **kw)

    def draw_path_collection(self, *kl, **kw):
        return self._renderer.draw_path_collection(*kl, **kw)

    def _update_methods(self):
        self.draw_quad_mesh = self._renderer.draw_quad_mesh
        self.draw_gouraud_triangle = self._renderer.draw_gouraud_triangle
        self.draw_gouraud_triangles = self._renderer.draw_gouraud_triangles
        self.draw_image = self._renderer.draw_image
        self.copy_from_bbox = self._renderer.copy_from_bbox
        self.tostring_rgba_minimized = self._renderer.tostring_rgba_minimized

    def draw_path(self, gc, path, transform, rgbFace=None):
        """
        Draw the path
        """
        nmax = rcParams['agg.path.chunksize']
        npts = path.vertices.shape[0]
        if nmax > 100 and npts > nmax and path.should_simplify and rgbFace is None and gc.get_hatch() is None:
            nch = np.ceil(npts / float(nmax))
            chsize = int(np.ceil(npts / nch))
            i0 = np.arange(0, npts, chsize)
            i1 = np.zeros_like(i0)
            i1[:(-1)] = i0[1:] - 1
            i1[-1] = npts
            for ii0, ii1 in zip(i0, i1):
                v = path.vertices[ii0:ii1, :]
                c = path.codes
                if c is not None:
                    c = c[ii0:ii1]
                    c[0] = Path.MOVETO
                p = Path(v, c)
                self._renderer.draw_path(gc, p, transform, rgbFace)

        else:
            self._renderer.draw_path(gc, path, transform, rgbFace)
        return

    def draw_mathtext(self, gc, x, y, s, prop, angle):
        """
        Draw the math text using matplotlib.mathtext
        """
        verbose.report('RendererAgg.draw_mathtext', 'debug-annoying')
        ox, oy, width, height, descent, font_image, used_characters = self.mathtext_parser.parse(s, self.dpi, prop)
        x = int(x) + ox
        y = int(y) - oy
        self._renderer.draw_text_image(font_image, x, y + 1, angle, gc)

    def draw_text(self, gc, x, y, s, prop, angle, ismath):
        """
        Render the text
        """
        verbose.report('RendererAgg.draw_text', 'debug-annoying')
        if ismath:
            return self.draw_mathtext(gc, x, y, s, prop, angle)
        else:
            flags = get_hinting_flag()
            font = self._get_agg_font(prop)
            if font is None:
                return
            if len(s) == 1 and ord(s) > 127:
                font.load_char(ord(s), flags=flags)
            else:
                font.set_text(s, 0, flags=flags)
            font.draw_glyphs_to_bitmap(antialiased=rcParams['text.antialiased'])
            self._renderer.draw_text_image(font.get_image(), int(x), int(y) + 1, angle, gc)
            return

    def get_text_width_height_descent(self, s, prop, ismath):
        """
        get the width and height in display coords of the string s
        with FontPropertry prop

        # passing rgb is a little hack to make cacheing in the
        # texmanager more efficient.  It is not meant to be used
        # outside the backend
        """
        if rcParams['text.usetex']:
            size = prop.get_size_in_points()
            texmanager = self.get_texmanager()
            fontsize = prop.get_size_in_points()
            w, h, d = texmanager.get_text_width_height_descent(s, fontsize, renderer=self)
            return (
             w, h, d)
        if ismath:
            ox, oy, width, height, descent, fonts, used_characters = self.mathtext_parser.parse(s, self.dpi, prop)
            return (
             width, height, descent)
        flags = get_hinting_flag()
        font = self._get_agg_font(prop)
        font.set_text(s, 0.0, flags=flags)
        w, h = font.get_width_height()
        d = font.get_descent()
        w /= 64.0
        h /= 64.0
        d /= 64.0
        return (w, h, d)

    def draw_tex(self, gc, x, y, s, prop, angle):
        size = prop.get_size_in_points()
        texmanager = self.get_texmanager()
        key = (s, size, self.dpi, angle, texmanager.get_font_config())
        im = self.texd.get(key)
        if im is None:
            Z = texmanager.get_grey(s, size, self.dpi)
            Z = np.array(Z * 255.0, np.uint8)
        self._renderer.draw_text_image(Z, x, y, angle, gc)
        return

    def get_canvas_width_height(self):
        """return the canvas width and height in display coords"""
        return (
         self.width, self.height)

    def _get_agg_font(self, prop):
        """
        Get the font for text instance t, cacheing for efficiency
        """
        verbose.report('RendererAgg._get_agg_font', 'debug-annoying')
        key = hash(prop)
        font = RendererAgg._fontd.get(key)
        if font is None:
            fname = findfont(prop)
            font = RendererAgg._fontd.get(fname)
            if font is None:
                font = FT2Font(str(fname), hinting_factor=rcParams['text.hinting_factor'])
                RendererAgg._fontd[fname] = font
            RendererAgg._fontd[key] = font
        font.clear()
        size = prop.get_size_in_points()
        font.set_size(size, self.dpi)
        return font

    def points_to_pixels(self, points):
        """
        convert point measures to pixes using dpi and the pixels per
        inch of the display
        """
        verbose.report('RendererAgg.points_to_pixels', 'debug-annoying')
        return points * self.dpi / 72.0

    def tostring_rgb(self):
        verbose.report('RendererAgg.tostring_rgb', 'debug-annoying')
        return self._renderer.tostring_rgb()

    def tostring_argb(self):
        verbose.report('RendererAgg.tostring_argb', 'debug-annoying')
        return self._renderer.tostring_argb()

    def buffer_rgba(self):
        verbose.report('RendererAgg.buffer_rgba', 'debug-annoying')
        return self._renderer.buffer_rgba()

    def clear(self):
        self._renderer.clear()

    def option_image_nocomposite(self):
        return True

    def option_scale_image(self):
        """
        agg backend support arbitrary scaling of image.
        """
        return True

    def restore_region(self, region, bbox=None, xy=None):
        """
        Restore the saved region. If bbox (instance of BboxBase, or
        its extents) is given, only the region specified by the bbox
        will be restored. *xy* (a tuple of two floasts) optionally
        specifies the new position (the LLC of the original region,
        not the LLC of the bbox) where the region will be restored.

        >>> region = renderer.copy_from_bbox()
        >>> x1, y1, x2, y2 = region.get_extents()
        >>> renderer.restore_region(region, bbox=(x1+dx, y1, x2, y2),
                                    xy=(x1-dx, y1))

        """
        if bbox is not None or xy is not None:
            if bbox is None:
                x1, y1, x2, y2 = region.get_extents()
            elif isinstance(bbox, BboxBase):
                x1, y1, x2, y2 = bbox.extents
            else:
                x1, y1, x2, y2 = bbox
            if xy is None:
                ox, oy = x1, y1
            else:
                ox, oy = xy
            self._renderer.restore_region2(region, x1, y1, x2, y2, ox, oy)
        else:
            self._renderer.restore_region(region)
        return

    def start_filter(self):
        """
        Start filtering. It simply create a new canvas (the old one is saved).
        """
        self._filter_renderers.append(self._renderer)
        self._renderer = _RendererAgg(int(self.width), int(self.height), self.dpi)
        self._update_methods()

    def stop_filter(self, post_processing):
        """
        Save the plot in the current canvas as a image and apply
        the *post_processing* function.

           def post_processing(image, dpi):
             # ny, nx, depth = image.shape
             # image (numpy array) has RGBA channels and has a depth of 4.
             ...
             # create a new_image (numpy array of 4 channels, size can be
             # different). The resulting image may have offsets from
             # lower-left corner of the original image
             return new_image, offset_x, offset_y

        The saved renderer is restored and the returned image from
        post_processing is plotted (using draw_image) on it.
        """
        from matplotlib._image import fromarray
        width, height = int(self.width), int(self.height)
        buffer, bounds = self._renderer.tostring_rgba_minimized()
        l, b, w, h = bounds
        self._renderer = self._filter_renderers.pop()
        self._update_methods()
        if w > 0 and h > 0:
            img = np.fromstring(buffer, np.uint8)
            img, ox, oy = post_processing(img.reshape((h, w, 4)) / 255.0, self.dpi)
            image = fromarray(img, 1)
            image.flipud_out()
            gc = self.new_gc()
            self._renderer.draw_image(gc, l + ox, height - b - h + oy, image)


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    verbose.report('backend_agg.new_figure_manager', 'debug-annoying')
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasAgg(figure)
    manager = FigureManagerBase(canvas, num)
    return manager


class FigureCanvasAgg(FigureCanvasBase):
    """
    The canvas the figure renders into.  Calls the draw and print fig
    methods, creates the renderers, etc...

    Public attribute

      figure - A Figure instance
    """

    def copy_from_bbox(self, bbox):
        renderer = self.get_renderer()
        return renderer.copy_from_bbox(bbox)

    def restore_region(self, region, bbox=None, xy=None):
        renderer = self.get_renderer()
        return renderer.restore_region(region, bbox, xy)

    def draw(self):
        """
        Draw the figure using the renderer
        """
        verbose.report('FigureCanvasAgg.draw', 'debug-annoying')
        self.renderer = self.get_renderer()
        RendererAgg.lock.acquire()
        try:
            self.figure.draw(self.renderer)
        finally:
            RendererAgg.lock.release()

    def get_renderer(self):
        l, b, w, h = self.figure.bbox.bounds
        key = (w, h, self.figure.dpi)
        try:
            (self._lastKey, self.renderer)
        except AttributeError:
            need_new_renderer = True
        else:
            need_new_renderer = self._lastKey != key

        if need_new_renderer:
            self.renderer = RendererAgg(w, h, self.figure.dpi)
            self._lastKey = key
        return self.renderer

    def tostring_rgb(self):
        verbose.report('FigureCanvasAgg.tostring_rgb', 'debug-annoying')
        return self.renderer.tostring_rgb()

    def tostring_argb(self):
        verbose.report('FigureCanvasAgg.tostring_argb', 'debug-annoying')
        return self.renderer.tostring_argb()

    def buffer_rgba(self):
        verbose.report('FigureCanvasAgg.buffer_rgba', 'debug-annoying')
        return self.renderer.buffer_rgba()

    def print_raw(self, filename_or_obj, *args, **kwargs):
        FigureCanvasAgg.draw(self)
        renderer = self.get_renderer()
        original_dpi = renderer.dpi
        renderer.dpi = self.figure.dpi
        if is_string_like(filename_or_obj):
            filename_or_obj = open(filename_or_obj, 'wb')
            close = True
        else:
            close = False
        try:
            renderer._renderer.write_rgba(filename_or_obj)
        finally:
            if close:
                filename_or_obj.close()

        renderer.dpi = original_dpi

    print_rgba = print_raw

    def print_png(self, filename_or_obj, *args, **kwargs):
        FigureCanvasAgg.draw(self)
        renderer = self.get_renderer()
        original_dpi = renderer.dpi
        renderer.dpi = self.figure.dpi
        if is_string_like(filename_or_obj):
            filename_or_obj = open(filename_or_obj, 'wb')
            close = True
        else:
            close = False
        try:
            _png.write_png(renderer._renderer.buffer_rgba(), renderer.width, renderer.height, filename_or_obj, self.figure.dpi)
        finally:
            if close:
                filename_or_obj.close()

        renderer.dpi = original_dpi

    def print_to_buffer(self):
        FigureCanvasAgg.draw(self)
        renderer = self.get_renderer()
        original_dpi = renderer.dpi
        renderer.dpi = self.figure.dpi
        result = (renderer._renderer.buffer_rgba(),
         (
          int(renderer.width), int(renderer.height)))
        renderer.dpi = original_dpi
        return result