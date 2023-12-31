# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_mixed.pyc
# Compiled at: 2012-10-30 18:11:14
from __future__ import print_function
from matplotlib._image import frombuffer
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.tight_bbox import process_figure_for_rasterizing

class MixedModeRenderer(object):
    """
    A helper class to implement a renderer that switches between
    vector and raster drawing.  An example may be a PDF writer, where
    most things are drawn with PDF vector commands, but some very
    complex objects, such as quad meshes, are rasterised and then
    output as images.
    """

    def __init__(self, figure, width, height, dpi, vector_renderer, raster_renderer_class=None, bbox_inches_restore=None):
        """
        figure: The figure instance.

        width: The width of the canvas in logical units

        height: The height of the canvas in logical units

        dpi: The dpi of the canvas

        vector_renderer: An instance of a subclass of RendererBase
        that will be used for the vector drawing.

        raster_renderer_class: The renderer class to use for the
        raster drawing.  If not provided, this will use the Agg
        backend (which is currently the only viable option anyway.)
        """
        if raster_renderer_class is None:
            raster_renderer_class = RendererAgg
        self._raster_renderer_class = raster_renderer_class
        self._width = width
        self._height = height
        self.dpi = dpi
        assert not vector_renderer.option_image_nocomposite()
        self._vector_renderer = vector_renderer
        self._raster_renderer = None
        self._rasterizing = 0
        self.figure = figure
        self._bbox_inches_restore = bbox_inches_restore
        self._set_current_renderer(vector_renderer)
        return

    _methods = ('\n        close_group draw_image draw_markers draw_path\n        draw_path_collection draw_quad_mesh draw_tex draw_text\n        finalize flipy get_canvas_width_height get_image_magnification\n        get_texmanager get_text_width_height_descent new_gc open_group\n        option_image_nocomposite points_to_pixels strip_math\n        start_filter stop_filter draw_gouraud_triangle\n        draw_gouraud_triangles option_scale_image\n        ').split()

    def _set_current_renderer(self, renderer):
        self._renderer = renderer
        for method in self._methods:
            if hasattr(renderer, method):
                setattr(self, method, getattr(renderer, method))

        renderer.start_rasterizing = self.start_rasterizing
        renderer.stop_rasterizing = self.stop_rasterizing

    def start_rasterizing(self):
        """
        Enter "raster" mode.  All subsequent drawing commands (until
        stop_rasterizing is called) will be drawn with the raster
        backend.

        If start_rasterizing is called multiple times before
        stop_rasterizing is called, this method has no effect.
        """
        self.figure.set_dpi(self.dpi)
        if self._bbox_inches_restore:
            r = process_figure_for_rasterizing(self.figure, self._bbox_inches_restore, mode='png')
            self._bbox_inches_restore = r
        if self._rasterizing == 0:
            self._raster_renderer = self._raster_renderer_class(self._width * self.dpi, self._height * self.dpi, self.dpi)
            self._set_current_renderer(self._raster_renderer)
        self._rasterizing += 1

    def stop_rasterizing(self):
        """
        Exit "raster" mode.  All of the drawing that was done since
        the last start_rasterizing command will be copied to the
        vector backend by calling draw_image.

        If stop_rasterizing is called multiple times before
        start_rasterizing is called, this method has no effect.
        """
        self._rasterizing -= 1
        if self._rasterizing == 0:
            self._set_current_renderer(self._vector_renderer)
            width, height = self._width * self.dpi, self._height * self.dpi
            buffer, bounds = self._raster_renderer.tostring_rgba_minimized()
            l, b, w, h = bounds
            if w > 0 and h > 0:
                image = frombuffer(buffer, w, h, True)
                image.is_grayscale = False
                image.flipud_out()
                gc = self._renderer.new_gc()
                self._renderer.draw_image(gc, float(l) / self.dpi * 72.0, (float(height) - b - h) / self.dpi * 72.0, image)
            self._raster_renderer = None
            self._rasterizing = False
        self.figure.set_dpi(72)
        if self._bbox_inches_restore:
            r = process_figure_for_rasterizing(self.figure, self._bbox_inches_restore, mode='pdf')
            self._bbox_inches_restore = r
        return