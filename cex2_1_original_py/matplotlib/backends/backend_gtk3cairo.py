# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_gtk3cairo.pyc
# Compiled at: 2012-10-30 18:11:14
import backend_gtk3, backend_cairo
from matplotlib.figure import Figure

class RendererGTK3Cairo(backend_cairo.RendererCairo):

    def set_context(self, ctx):
        self.gc.ctx = ctx


class FigureCanvasGTK3Cairo(backend_gtk3.FigureCanvasGTK3, backend_cairo.FigureCanvasCairo):

    def __init__(self, figure):
        backend_gtk3.FigureCanvasGTK3.__init__(self, figure)

    def _renderer_init(self):
        """use cairo renderer"""
        self._renderer = RendererGTK3Cairo(self.figure.dpi)

    def _render_figure(self, width, height):
        self._renderer.set_width_height(width, height)
        self.figure.draw(self._renderer)

    def on_draw_event(self, widget, ctx):
        """ GtkDrawable draw event, like expose_event in GTK 2.X
        """
        self._renderer.set_context(ctx)
        allocation = self.get_allocation()
        x, y, w, h = (allocation.x, allocation.y, allocation.width, allocation.height)
        self._render_figure(w, h)
        return False


class FigureManagerGTK3Cairo(backend_gtk3.FigureManagerGTK3):
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
    canvas = FigureCanvasGTK3Cairo(figure)
    manager = FigureManagerGTK3Cairo(canvas, num)
    return manager


FigureManager = FigureManagerGTK3Cairo
show = backend_gtk3.show