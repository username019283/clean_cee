# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_qtagg.pyc
# Compiled at: 2012-10-30 18:11:14
"""
Render to qt from agg
"""
from __future__ import division, print_function
import os, sys, matplotlib
from matplotlib import verbose
from matplotlib.figure import Figure
from backend_agg import FigureCanvasAgg
from backend_qt import qt, FigureManagerQT, FigureCanvasQT, show, draw_if_interactive, backend_version, NavigationToolbar2QT
DEBUG = False

def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    if DEBUG:
        print('backend_qtagg.new_figure_manager')
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasQTAgg(figure)
    return FigureManagerQTAgg(canvas, num)


class NavigationToolbar2QTAgg(NavigationToolbar2QT):

    def _get_canvas(self, fig):
        return FigureCanvasQTAgg(fig)


class FigureManagerQTAgg(FigureManagerQT):

    def _get_toolbar(self, canvas, parent):
        if matplotlib.rcParams['toolbar'] == 'classic':
            print('Classic toolbar is not yet supported')
        elif matplotlib.rcParams['toolbar'] == 'toolbar2':
            toolbar = NavigationToolbar2QTAgg(canvas, parent)
        else:
            toolbar = None
        return toolbar


class FigureCanvasQTAgg(FigureCanvasAgg, FigureCanvasQT):
    """
    The canvas the figure renders into.  Calls the draw and print fig
    methods, creates the renderers, etc...

    Public attribute

      figure - A Figure instance
   """

    def __init__(self, figure):
        if DEBUG:
            print('FigureCanvasQtAgg: ', figure)
        FigureCanvasQT.__init__(self, figure)
        FigureCanvasAgg.__init__(self, figure)
        self.drawRect = False
        self.rect = []
        self.replot = True
        self.pixmap = qt.QPixmap()

    def resizeEvent(self, e):
        FigureCanvasQT.resizeEvent(self, e)

    def drawRectangle(self, rect):
        self.rect = rect
        self.drawRect = True
        self.repaint(False)

    def paintEvent(self, e):
        """
        Draw to the Agg backend and then copy the image to the qt.drawable.
        In Qt, all drawing should be done inside of here when a widget is
        shown onscreen.
        """
        FigureCanvasQT.paintEvent(self, e)
        if DEBUG:
            print('FigureCanvasQtAgg.paintEvent: ', self, self.get_width_height())
        p = qt.QPainter(self)
        if type(self.replot) is bool:
            if self.replot:
                FigureCanvasAgg.draw(self)
                if qt.QImage.systemByteOrder() == qt.QImage.LittleEndian:
                    stringBuffer = self.renderer._renderer.tostring_bgra()
                else:
                    stringBuffer = self.renderer._renderer.tostring_argb()
                qImage = qt.QImage(stringBuffer, self.renderer.width, self.renderer.height, 32, None, 0, qt.QImage.IgnoreEndian)
                self.pixmap.convertFromImage(qImage, qt.QPixmap.Color)
            p.drawPixmap(qt.QPoint(0, 0), self.pixmap)
            if self.drawRect:
                p.setPen(qt.QPen(qt.Qt.black, 1, qt.Qt.DotLine))
                p.drawRect(self.rect[0], self.rect[1], self.rect[2], self.rect[3])
        else:
            bbox = self.replot
            l, b, r, t = bbox.extents
            w = int(r) - int(l)
            h = int(t) - int(b)
            reg = self.copy_from_bbox(bbox)
            stringBuffer = reg.to_string_argb()
            qImage = qt.QImage(stringBuffer, w, h, 32, None, 0, qt.QImage.IgnoreEndian)
            self.pixmap.convertFromImage(qImage, qt.QPixmap.Color)
            p.drawPixmap(qt.QPoint(l, self.renderer.height - t), self.pixmap)
        p.end()
        self.replot = False
        self.drawRect = False
        return

    def draw(self):
        """
        Draw the figure when xwindows is ready for the update
        """
        if DEBUG:
            print('FigureCanvasQtAgg.draw', self)
        self.replot = True
        FigureCanvasAgg.draw(self)
        self.repaint(False)

    def blit(self, bbox=None):
        """
        Blit the region in bbox
        """
        self.replot = bbox
        self.repaint(False)

    def print_figure(self, *args, **kwargs):
        FigureCanvasAgg.print_figure(self, *args, **kwargs)
        self.draw()