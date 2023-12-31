# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_gtk3agg.pyc
# Compiled at: 2012-10-30 18:11:14
import cairo, numpy as np, sys, warnings, backend_agg, backend_gtk3
from matplotlib.figure import Figure
from matplotlib import transforms
if sys.version_info[0] >= 3:
    warnings.warn('The Gtk3Agg backend is not known to work on Python 3.x.')

class FigureCanvasGTK3Agg(backend_gtk3.FigureCanvasGTK3, backend_agg.FigureCanvasAgg):

    def __init__(self, figure):
        backend_gtk3.FigureCanvasGTK3.__init__(self, figure)
        self._bbox_queue = []

    def _renderer_init(self):
        pass

    def _render_figure(self, width, height):
        backend_agg.FigureCanvasAgg.draw(self)

    def on_draw_event(self, widget, ctx):
        """ GtkDrawable draw event, like expose_event in GTK 2.X
        """
        allocation = self.get_allocation()
        w, h = allocation.width, allocation.height
        if not len(self._bbox_queue):
            if self._need_redraw:
                self._render_figure(w, h)
                bbox_queue = [transforms.Bbox([[0, 0], [w, h]])]
            else:
                return
        else:
            bbox_queue = self._bbox_queue
        for bbox in bbox_queue:
            area = self.copy_from_bbox(bbox)
            buf = np.fromstring(area.to_string_argb(), dtype='uint8')
            x = int(bbox.x0)
            y = h - int(bbox.y1)
            width = int(bbox.x1) - int(bbox.x0)
            height = int(bbox.y1) - int(bbox.y0)
            image = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, width, height)
            ctx.set_source_surface(image, x, y)
            ctx.paint()

        if len(self._bbox_queue):
            self._bbox_queue = []
        return False

    def blit(self, bbox=None):
        self._bbox_queue.append(bbox)
        self.queue_draw()

    def print_png(self, filename, *args, **kwargs):
        agg = self.switch_backends(backend_agg.FigureCanvasAgg)
        return agg.print_png(filename, *args, **kwargs)


class FigureManagerGTK3Agg(backend_gtk3.FigureManagerGTK3):
    pass


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasGTK3Agg(figure)
    manager = FigureManagerGTK3Agg(canvas, num)
    return manager


FigureManager = FigureManagerGTK3Agg
show = backend_gtk3.show