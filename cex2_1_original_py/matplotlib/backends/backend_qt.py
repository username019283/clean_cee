# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_qt.pyc
# Compiled at: 2012-10-30 18:11:14
from __future__ import division, print_function
import math, os, sys, warnings
warnings.warn('QT3-based backends are deprecated and will be removed after the v1.2.x release. Use the equivalent QT4 backend instead.', DeprecationWarning)
import matplotlib
from matplotlib import verbose
from matplotlib.cbook import is_string_like, onetrue
from matplotlib.backend_bases import RendererBase, GraphicsContextBase, FigureManagerBase, FigureCanvasBase, NavigationToolbar2, cursors
from matplotlib.backend_bases import ShowBase
from matplotlib._pylab_helpers import Gcf
from matplotlib.figure import Figure
from matplotlib.mathtext import MathTextParser
from matplotlib.widgets import SubplotTool
try:
    import qt
except ImportError:
    raise ImportError('Qt backend requires pyqt to be installed. NOTE: QT3-based backends will not work in Python 3.')

backend_version = '0.9.1'

def fn_name():
    return sys._getframe(1).f_code.co_name


DEBUG = False
cursord = {cursors.MOVE: qt.Qt.PointingHandCursor, 
   cursors.HAND: qt.Qt.WaitCursor, 
   cursors.POINTER: qt.Qt.ArrowCursor, 
   cursors.SELECT_REGION: qt.Qt.CrossCursor}

def draw_if_interactive():
    """
    Is called after every pylab drawing command
    """
    if matplotlib.is_interactive():
        figManager = Gcf.get_active()
        if figManager != None:
            figManager.canvas.draw()
    return


def _create_qApp():
    """
    Only one qApp can exist at a time, so check before creating one
    """
    global qApp
    if qt.QApplication.startingUp():
        if DEBUG:
            print('Starting up QApplication')
        qApp = qt.QApplication([' '])
        qt.QObject.connect(qApp, qt.SIGNAL('lastWindowClosed()'), qApp, qt.SLOT('quit()'))
        _create_qApp.qAppCreatedHere = True


_create_qApp.qAppCreatedHere = False

class Show(ShowBase):

    def mainloop(self):
        if _create_qApp.qAppCreatedHere:
            qt.qApp.exec_loop()


show = Show()

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
    canvas = FigureCanvasQT(figure)
    manager = FigureManagerQT(canvas, num)
    return manager


class FigureCanvasQT(qt.QWidget, FigureCanvasBase):
    keyvald = {qt.Qt.Key_Control: 'control', qt.Qt.Key_Shift: 'shift', 
       qt.Qt.Key_Alt: 'alt'}
    buttond = {1: 1, 2: 3, 4: 2}

    def __init__(self, figure):
        if DEBUG:
            print('FigureCanvasQt: ', figure)
        _create_qApp()
        qt.QWidget.__init__(self, None, 'QWidget figure')
        FigureCanvasBase.__init__(self, figure)
        self.figure = figure
        self.setMouseTracking(True)
        w, h = self.get_width_height()
        self.resize(w, h)
        return

    def enterEvent(self, event):
        FigureCanvasBase.enter_notify_event(self, event)

    def leaveEvent(self, event):
        FigureCanvasBase.leave_notify_event(self, event)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = self.figure.bbox.height - event.pos().y()
        button = self.buttond[event.button()]
        FigureCanvasBase.button_press_event(self, x, y, button)
        if DEBUG:
            print('button pressed:', event.button())

    def mouseDoubleClickEvent(self, event):
        x = event.pos().x()
        y = self.figure.bbox.height - event.pos().y()
        button = self.buttond[event.button()]
        FigureCanvasBase.button_press_event(self, x, y, button, dblclick=True)
        if DEBUG:
            print('button doubleclicked:', event.button())

    def mouseMoveEvent(self, event):
        x = event.x()
        y = self.figure.bbox.height - event.y()
        FigureCanvasBase.motion_notify_event(self, x, y)
        if DEBUG:
            print('mouse move')

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = self.figure.bbox.height - event.y()
        button = self.buttond[event.button()]
        FigureCanvasBase.button_release_event(self, x, y, button)
        if DEBUG:
            print('button released')

    def keyPressEvent(self, event):
        key = self._get_key(event)
        FigureCanvasBase.key_press_event(self, key)
        if DEBUG:
            print('key press', key)

    def keyReleaseEvent(self, event):
        key = self._get_key(event)
        FigureCanvasBase.key_release_event(self, key)
        if DEBUG:
            print('key release', key)

    def resizeEvent(self, event):
        if DEBUG:
            print('resize (%d x %d)' % (event.size().width(), event.size().height()))
        qt.QWidget.resizeEvent(self, event)
        w = event.size().width()
        h = event.size().height()
        if DEBUG:
            print('FigureCanvasQt.resizeEvent(', w, ',', h, ')')
        dpival = self.figure.dpi
        winch = w / dpival
        hinch = h / dpival
        self.figure.set_size_inches(winch, hinch)
        self.draw()

    def resize(self, w, h):
        qt.QWidget.resize(self, w, h)
        pixelPerInch = self.figure.dpi
        wInch = w / pixelPerInch
        hInch = h / pixelPerInch
        self.figure.set_size_inches(wInch, hInch)
        self.draw()

    def sizeHint(self):
        w, h = self.get_width_height()
        return qt.QSize(w, h)

    def minumumSizeHint(self):
        return qt.QSize(10, 10)

    def _get_key(self, event):
        if event.key() < 256:
            key = event.text().latin1()
        elif event.key() in self.keyvald:
            key = self.keyvald[event.key()]
        else:
            key = None
        return key

    def flush_events(self):
        qt.qApp.processEvents()

    def start_event_loop(self, timeout):
        FigureCanvasBase.start_event_loop_default(self, timeout)

    start_event_loop.__doc__ = FigureCanvasBase.start_event_loop_default.__doc__

    def stop_event_loop(self):
        FigureCanvasBase.stop_event_loop_default(self)

    stop_event_loop.__doc__ = FigureCanvasBase.stop_event_loop_default.__doc__


class FigureManagerQT(FigureManagerBase):
    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The qt.QToolBar
    window      : The qt.QMainWindow
    """

    def __init__(self, canvas, num):
        if DEBUG:
            print('FigureManagerQT.%s' % fn_name())
        FigureManagerBase.__init__(self, canvas, num)
        self.canvas = canvas
        self.window = qt.QMainWindow(None, None, qt.Qt.WDestructiveClose)
        self.window.closeEvent = self._widgetCloseEvent
        centralWidget = qt.QWidget(self.window)
        self.canvas.reparent(centralWidget, qt.QPoint(0, 0))
        self.canvas.setFocusPolicy(qt.QWidget.ClickFocus)
        self.canvas.setFocus()
        self.set_window_title('Figure %d' % num)
        self.window._destroying = False
        self.toolbar = self._get_toolbar(self.canvas, centralWidget)
        self.layout = qt.QVBoxLayout(centralWidget)
        self.layout.addWidget(self.canvas, 1)
        if self.toolbar:
            self.layout.addWidget(self.toolbar, 0)
        self.window.setCentralWidget(centralWidget)
        w = self.canvas.width()
        h = self.canvas.height()
        if self.toolbar:
            h += self.toolbar.height() + 4
        self.window.resize(w, h)
        if matplotlib.is_interactive():
            self.window.show()

        def notify_axes_change(fig):
            if self.toolbar != None:
                self.toolbar.update()
            return

        self.canvas.figure.add_axobserver(notify_axes_change)
        return

    def _widgetclosed(self):
        if self.window._destroying:
            return
        self.window._destroying = True
        Gcf.destroy(self.num)

    def _widgetCloseEvent(self, event):
        self._widgetclosed()
        qt.QWidget.closeEvent(self.window, event)

    def _get_toolbar(self, canvas, parent):
        if matplotlib.rcParams['toolbar'] == 'classic':
            print('Classic toolbar is not yet supported')
        elif matplotlib.rcParams['toolbar'] == 'toolbar2':
            toolbar = NavigationToolbar2QT(canvas, parent)
        else:
            toolbar = None
        return toolbar

    def resize(self, width, height):
        """set the canvas size in pixels"""
        self.window.resize(width, height)

    def show(self):
        self.window.show()

    def destroy(self, *args):
        if self.window._destroying:
            return
        self.window._destroying = True
        if self.toolbar:
            self.toolbar.destroy()
        if DEBUG:
            print('destroy figure manager')
        self.window.close(True)

    def get_window_title(self):
        return str(self.window.caption())

    def set_window_title(self, title):
        self.window.setCaption(title)


class NavigationToolbar2QT(NavigationToolbar2, qt.QWidget):

    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.buttons = {}
        qt.QWidget.__init__(self, parent)
        self.layout = qt.QHBoxLayout(self)
        self.layout.setMargin(2)
        NavigationToolbar2.__init__(self, canvas)

    def _init_toolbar(self):
        basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text == None:
                self.layout.addSpacing(8)
                continue
            fname = os.path.join(basedir, image_file + '.ppm')
            image = qt.QPixmap()
            image.load(fname)
            button = qt.QPushButton(qt.QIconSet(image), '', self)
            qt.QToolTip.add(button, tooltip_text)
            self.buttons[text] = button
            margin = 4
            button.setFixedSize(image.width() + margin, image.height() + margin)
            qt.QObject.connect(button, qt.SIGNAL('clicked()'), getattr(self, callback))
            self.layout.addWidget(button)

        self.buttons['Pan'].setToggleButton(True)
        self.buttons['Zoom'].setToggleButton(True)
        self.locLabel = qt.QLabel('', self)
        self.locLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.locLabel.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Ignored))
        self.layout.addWidget(self.locLabel, 1)
        self.adj_window = None
        return

    def destroy(self):
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is not None:
                qt.QObject.disconnect(self.buttons[text], qt.SIGNAL('clicked()'), getattr(self, callback))

        return

    def pan(self, *args):
        self.buttons['Zoom'].setOn(False)
        NavigationToolbar2.pan(self, *args)

    def zoom(self, *args):
        self.buttons['Pan'].setOn(False)
        NavigationToolbar2.zoom(self, *args)

    def dynamic_update(self):
        self.canvas.draw()

    def set_message(self, s):
        self.locLabel.setText(s)

    def set_cursor(self, cursor):
        if DEBUG:
            print('Set cursor', cursor)
        qt.QApplication.restoreOverrideCursor()
        qt.QApplication.setOverrideCursor(qt.QCursor(cursord[cursor]))

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0
        w = abs(x1 - x0)
        h = abs(y1 - y0)
        rect = [ int(val) for val in (min(x0, x1), min(y0, y1), w, h) ]
        self.canvas.drawRectangle(rect)

    def configure_subplots(self):
        self.adj_window = qt.QMainWindow(None, None, qt.Qt.WDestructiveClose)
        win = self.adj_window
        win.setCaption('Subplot Configuration Tool')
        toolfig = Figure(figsize=(6, 3))
        toolfig.subplots_adjust(top=0.9)
        w = int(toolfig.bbox.width)
        h = int(toolfig.bbox.height)
        canvas = self._get_canvas(toolfig)
        tool = SubplotTool(self.canvas.figure, toolfig)
        centralWidget = qt.QWidget(win)
        canvas.reparent(centralWidget, qt.QPoint(0, 0))
        win.setCentralWidget(centralWidget)
        layout = qt.QVBoxLayout(centralWidget)
        layout.addWidget(canvas, 1)
        win.resize(w, h)
        canvas.setFocus()
        win.show()
        return

    def _get_canvas(self, fig):
        return FigureCanvasQT(fig)

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = filetypes.items()
        sorted_filetypes.sort()
        default_filetype = self.canvas.get_default_filetype()
        start = self.canvas.get_default_filename()
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = (' ').join([ '*.%s' % ext for ext in exts ])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)

        filters = (';;').join(filters)
        fname = qt.QFileDialog.getSaveFileName(start, filters, self, 'Save image', 'Choose a filename to save to', selectedFilter)
        if fname:
            try:
                self.canvas.print_figure(unicode(fname))
            except Exception as e:
                qt.QMessageBox.critical(self, 'Error saving file', str(e), qt.QMessageBox.Ok, qt.QMessageBox.NoButton)

        return

    def set_history_buttons(self):
        canBackward = self._views._pos > 0
        canForward = self._views._pos < len(self._views._elements) - 1
        self.buttons['Back'].setEnabled(canBackward)
        self.buttons['Forward'].setEnabled(canForward)


try:
    qt.window_set_default_icon_from_file(os.path.join(matplotlib.rcParams['datapath'], 'images', 'matplotlib.svg'))
except:
    verbose.report('Could not load matplotlib icon: %s' % sys.exc_info()[1])

def error_msg_qt(msg, parent=None):
    if not is_string_like(msg):
        msg = (',').join(map(str, msg))
    qt.QMessageBox.warning(None, 'Matplotlib', msg, qt.QMessageBox.Ok)
    return


def exception_handler(type, value, tb):
    """Handle uncaught exceptions
    It does not catch SystemExit
    """
    msg = ''
    if hasattr(value, 'filename') and value.filename != None:
        msg = value.filename + ': '
    if hasattr(value, 'strerror') and value.strerror != None:
        msg += value.strerror
    else:
        msg += str(value)
    if len(msg):
        error_msg_qt(msg)
    return


FigureManager = FigureManagerQT