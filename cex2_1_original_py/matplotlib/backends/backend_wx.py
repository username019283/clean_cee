# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_wx.pyc
# Compiled at: 2012-10-30 18:11:14
from __future__ import division, print_function
import sys, os, os.path, math, StringIO, weakref, warnings, numpy as np
_DEBUG = 5
if _DEBUG < 5:
    import traceback, pdb
_DEBUG_lvls = {1: 'Low ', 2: 'Med ', 3: 'High', 4: 'Error'}
if sys.version_info[0] >= 3:
    warnings.warn('The wx and wxagg backends have not been tested with Python 3.x', ImportWarning)
missingwx = 'Matplotlib backend_wx and backend_wxagg require wxPython >=2.8'
missingwxversion = 'Matplotlib backend_wx and backend_wxagg require wxversion, which was not found.'
if not hasattr(sys, 'frozen'):
    try:
        import wxversion
    except ImportError:
        raise ImportError(missingwxversion)

    try:
        _wx_ensure_failed = wxversion.AlreadyImportedError
    except AttributeError:
        _wx_ensure_failed = wxversion.VersionError

    try:
        wxversion.ensureMinimal('2.8')
    except _wx_ensure_failed:
        pass

try:
    import wx
    backend_version = wx.VERSION_STRING
except ImportError:
    raise ImportError(missingwx)

major, minor = [ int(n) for n in backend_version.split('.')[:2] ]
if major < 2 or major < 3 and minor < 8:
    print(' wxPython version %s was imported.' % backend_version)
    raise ImportError(missingwx)

def DEBUG_MSG(string, lvl=3, o=None):
    if lvl >= _DEBUG:
        cls = o.__class__
        print('%s- %s in %s' % (_DEBUG_lvls[lvl], string, cls))


def debug_on_error(type, value, tb):
    """Code due to Thomas Heller - published in Python Cookbook (O'Reilley)"""
    traceback.print_exc(type, value, tb)
    print()
    pdb.pm()


class fake_stderr():
    """Wx does strange things with stderr, as it makes the assumption that there
    is probably no console. This redirects stderr to the console, since we know
    that there is one!"""

    def write(self, msg):
        print('Stderr: %s\n\r' % msg)


if wx.VERSION_STRING >= '2.5':

    def bind(actor, event, action, **kw):
        actor.Bind(event, action, **kw)


else:

    def bind(actor, event, action, id=None):
        if id is not None:
            event(actor, id, action)
        else:
            event(actor, action)
        return


import matplotlib
from matplotlib import verbose
from matplotlib.backend_bases import RendererBase, GraphicsContextBase, FigureCanvasBase, FigureManagerBase, NavigationToolbar2, cursors, TimerBase
from matplotlib.backend_bases import ShowBase
from matplotlib._pylab_helpers import Gcf
from matplotlib.artist import Artist
from matplotlib.cbook import exception_to_str, is_string_like, is_writable_file_like
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.text import _process_text_args, Text
from matplotlib.transforms import Affine2D
from matplotlib.widgets import SubplotTool
from matplotlib import rcParams
PIXELS_PER_INCH = 75
IDLE_DELAY = 5

def error_msg_wx(msg, parent=None):
    """
    Signal an error condition -- in a GUI, popup a error dialog
    """
    dialog = wx.MessageDialog(parent=parent, message=msg, caption='Matplotlib backend_wx error', style=wx.OK | wx.CENTRE)
    dialog.ShowModal()
    dialog.Destroy()
    return


def raise_msg_to_str(msg):
    """msg is a return arg from a raise.  Join with new lines"""
    if not is_string_like(msg):
        msg = ('\n').join(map(str, msg))
    return msg


class TimerWx(TimerBase):
    """
    Subclass of :class:`backend_bases.TimerBase` that uses WxTimer events.

    Attributes:
    * interval: The time between timer events in milliseconds. Default
        is 1000 ms.
    * single_shot: Boolean flag indicating whether this timer should
        operate as single shot (run once and then stop). Defaults to False.
    * callbacks: Stores list of (func, args) tuples that will be called
        upon timer events. This list can be manipulated directly, or the
        functions add_callback and remove_callback can be used.
    """

    def __init__(self, parent, *args, **kwargs):
        TimerBase.__init__(self, *args, **kwargs)
        self.parent = parent
        self._timer = wx.Timer(self.parent, wx.NewId())
        self.parent.Bind(wx.EVT_TIMER, self._on_timer, self._timer)

    def _timer_start(self):
        self._timer.Start(self._interval, self._single)

    def _timer_stop(self):
        self._timer.Stop()

    def _timer_set_interval(self):
        self._timer_start()

    def _timer_set_single_shot(self):
        self._timer.start()

    def _on_timer(self, *args):
        TimerBase._on_timer(self)


class RendererWx(RendererBase):
    """
    The renderer handles all the drawing primitives using a graphics
    context instance that controls the colors/styles. It acts as the
    'renderer' instance used by many classes in the hierarchy.
    """
    fontweights = {100: wx.LIGHT, 
       200: wx.LIGHT, 
       300: wx.LIGHT, 
       400: wx.NORMAL, 
       500: wx.NORMAL, 
       600: wx.NORMAL, 
       700: wx.BOLD, 
       800: wx.BOLD, 
       900: wx.BOLD, 
       'ultralight': wx.LIGHT, 
       'light': wx.LIGHT, 
       'normal': wx.NORMAL, 
       'medium': wx.NORMAL, 
       'semibold': wx.NORMAL, 
       'bold': wx.BOLD, 
       'heavy': wx.BOLD, 
       'ultrabold': wx.BOLD, 
       'black': wx.BOLD}
    fontangles = {'italic': wx.ITALIC, 
       'normal': wx.NORMAL, 
       'oblique': wx.SLANT}
    fontnames = {'Sans': wx.SWISS, 'Roman': wx.ROMAN, 
       'Script': wx.SCRIPT, 
       'Decorative': wx.DECORATIVE, 
       'Modern': wx.MODERN, 
       'Courier': wx.MODERN, 
       'courier': wx.MODERN}

    def __init__(self, bitmap, dpi):
        """
        Initialise a wxWindows renderer instance.
        """
        DEBUG_MSG('__init__()', 1, self)
        if wx.VERSION_STRING < '2.8':
            raise RuntimeError('matplotlib no longer supports wxPython < 2.8 for the Wx backend.\nYou may, however, use the WxAgg backend.')
        self.width = bitmap.GetWidth()
        self.height = bitmap.GetHeight()
        self.bitmap = bitmap
        self.fontd = {}
        self.dpi = dpi
        self.gc = None
        return

    def flipy(self):
        return True

    def offset_text_height(self):
        return True

    def get_text_width_height_descent(self, s, prop, ismath):
        """
        get the width and height in display coords of the string s
        with FontPropertry prop
        """
        if ismath:
            s = self.strip_math(s)
        if self.gc is None:
            gc = self.new_gc()
        else:
            gc = self.gc
        gfx_ctx = gc.gfx_ctx
        font = self.get_wx_font(s, prop)
        gfx_ctx.SetFont(font, wx.BLACK)
        w, h, descent, leading = gfx_ctx.GetFullTextExtent(s)
        return (
         w, h, descent)

    def get_canvas_width_height(self):
        """return the canvas width and height in display coords"""
        return (
         self.width, self.height)

    def handle_clip_rectangle(self, gc):
        new_bounds = gc.get_clip_rectangle()
        if new_bounds is not None:
            new_bounds = new_bounds.bounds
        gfx_ctx = gc.gfx_ctx
        if gfx_ctx._lastcliprect != new_bounds:
            gfx_ctx._lastcliprect = new_bounds
            if new_bounds is None:
                gfx_ctx.ResetClip()
            else:
                gfx_ctx.Clip(new_bounds[0], self.height - new_bounds[1] - new_bounds[3], new_bounds[2], new_bounds[3])
        return

    @staticmethod
    def convert_path(gfx_ctx, path, transform):
        wxpath = gfx_ctx.CreatePath()
        for points, code in path.iter_segments(transform):
            if code == Path.MOVETO:
                wxpath.MoveToPoint(*points)
            elif code == Path.LINETO:
                wxpath.AddLineToPoint(*points)
            elif code == Path.CURVE3:
                wxpath.AddQuadCurveToPoint(*points)
            elif code == Path.CURVE4:
                wxpath.AddCurveToPoint(*points)
            elif code == Path.CLOSEPOLY:
                wxpath.CloseSubpath()

        return wxpath

    def draw_path(self, gc, path, transform, rgbFace=None):
        gc.select()
        self.handle_clip_rectangle(gc)
        gfx_ctx = gc.gfx_ctx
        transform = transform + Affine2D().scale(1.0, -1.0).translate(0.0, self.height)
        wxpath = self.convert_path(gfx_ctx, path, transform)
        if rgbFace is not None:
            gfx_ctx.SetBrush(wx.Brush(gc.get_wxcolour(rgbFace)))
            gfx_ctx.DrawPath(wxpath)
        else:
            gfx_ctx.StrokePath(wxpath)
        gc.unselect()
        return

    def draw_image(self, gc, x, y, im):
        bbox = gc.get_clip_rectangle()
        if bbox != None:
            l, b, w, h = bbox.bounds
        else:
            l = 0
            b = (0, )
            w = self.width
            h = self.height
        rows, cols, image_str = im.as_rgba_str()
        image_array = np.fromstring(image_str, np.uint8)
        image_array.shape = (rows, cols, 4)
        bitmap = wx.BitmapFromBufferRGBA(cols, rows, image_array)
        gc = self.get_gc()
        gc.select()
        gc.gfx_ctx.DrawBitmap(bitmap, int(l), int(self.height - b), int(w), int(-h))
        gc.unselect()
        return

    def draw_text(self, gc, x, y, s, prop, angle, ismath):
        """
        Render the matplotlib.text.Text instance
        None)
        """
        if ismath:
            s = self.strip_math(s)
        DEBUG_MSG('draw_text()', 1, self)
        gc.select()
        self.handle_clip_rectangle(gc)
        gfx_ctx = gc.gfx_ctx
        font = self.get_wx_font(s, prop)
        color = gc.get_wxcolour(gc.get_rgb())
        gfx_ctx.SetFont(font, color)
        w, h, d = self.get_text_width_height_descent(s, prop, ismath)
        x = int(x)
        y = int(y - h)
        if angle == 0.0:
            gfx_ctx.DrawText(s, x, y)
        else:
            rads = angle / 180.0 * math.pi
            xo = h * math.sin(rads)
            yo = h * math.cos(rads)
            gfx_ctx.DrawRotatedText(s, x - xo, y - yo, rads)
        gc.unselect()

    def new_gc(self):
        """
        Return an instance of a GraphicsContextWx, and sets the current gc copy
        """
        DEBUG_MSG('new_gc()', 2, self)
        self.gc = GraphicsContextWx(self.bitmap, self)
        self.gc.select()
        self.gc.unselect()
        return self.gc

    def get_gc(self):
        """
        Fetch the locally cached gc.
        """
        assert self.gc != None, 'gc must be defined'
        return self.gc

    def get_wx_font(self, s, prop):
        """
        Return a wx font.  Cache instances in a font dictionary for
        efficiency
        """
        DEBUG_MSG('get_wx_font()', 1, self)
        key = hash(prop)
        fontprop = prop
        fontname = fontprop.get_name()
        font = self.fontd.get(key)
        if font is not None:
            return font
        else:
            wxFontname = self.fontnames.get(fontname, wx.ROMAN)
            wxFacename = ''
            size = self.points_to_pixels(fontprop.get_size_in_points())
            font = wx.Font(int(size + 0.5), wxFontname, self.fontangles[fontprop.get_style()], self.fontweights[fontprop.get_weight()], False, wxFacename)
            self.fontd[key] = font
            return font

    def points_to_pixels(self, points):
        """
        convert point measures to pixes using dpi and the pixels per
        inch of the display
        """
        return points * (PIXELS_PER_INCH / 72.0 * self.dpi / 72.0)


class GraphicsContextWx(GraphicsContextBase):
    """
    The graphics context provides the color, line styles, etc...

    This class stores a reference to a wxMemoryDC, and a
    wxGraphicsContext that draws to it.  Creating a wxGraphicsContext
    seems to be fairly heavy, so these objects are cached based on the
    bitmap object that is passed in.

    The base GraphicsContext stores colors as a RGB tuple on the unit
    interval, eg, (0.5, 0.0, 1.0).  wxPython uses an int interval, but
    since wxPython colour management is rather simple, I have not chosen
    to implement a separate colour manager class.
    """
    _capd = {'butt': wx.CAP_BUTT, 'projecting': wx.CAP_PROJECTING, 
       'round': wx.CAP_ROUND}
    _joind = {'bevel': wx.JOIN_BEVEL, 'miter': wx.JOIN_MITER, 
       'round': wx.JOIN_ROUND}
    _dashd_wx = {'solid': wx.SOLID, 'dashed': wx.SHORT_DASH, 
       'dashdot': wx.DOT_DASH, 
       'dotted': wx.DOT}
    _cache = weakref.WeakKeyDictionary()

    def __init__(self, bitmap, renderer):
        GraphicsContextBase.__init__(self)
        DEBUG_MSG('__init__()', 1, self)
        dc, gfx_ctx = self._cache.get(bitmap, (None, None))
        if dc is None:
            dc = wx.MemoryDC()
            dc.SelectObject(bitmap)
            gfx_ctx = wx.GraphicsContext.Create(dc)
            gfx_ctx._lastcliprect = None
            self._cache[bitmap] = (dc, gfx_ctx)
        self.bitmap = bitmap
        self.dc = dc
        self.gfx_ctx = gfx_ctx
        self._pen = wx.Pen('BLACK', 1, wx.SOLID)
        gfx_ctx.SetPen(self._pen)
        self._style = wx.SOLID
        self.renderer = renderer
        return

    def select(self):
        """
        Select the current bitmap into this wxDC instance
        """
        if sys.platform == 'win32':
            self.dc.SelectObject(self.bitmap)
            self.IsSelected = True

    def unselect(self):
        """
        Select a Null bitmasp into this wxDC instance
        """
        if sys.platform == 'win32':
            self.dc.SelectObject(wx.NullBitmap)
            self.IsSelected = False

    def set_foreground(self, fg, isRGB=None):
        """
        Set the foreground color.  fg can be a matlab format string, a
        html hex color string, an rgb unit tuple, or a float between 0
        and 1.  In the latter case, grayscale is used.
        """
        DEBUG_MSG('set_foreground()', 1, self)
        self.select()
        GraphicsContextBase.set_foreground(self, fg, isRGB)
        self._pen.SetColour(self.get_wxcolour(self.get_rgb()))
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def set_graylevel(self, frac):
        """
        Set the foreground color.  fg can be a matlab format string, a
        html hex color string, an rgb unit tuple, or a float between 0
        and 1.  In the latter case, grayscale is used.
        """
        DEBUG_MSG('set_graylevel()', 1, self)
        self.select()
        GraphicsContextBase.set_graylevel(self, frac)
        self._pen.SetColour(self.get_wxcolour(self.get_rgb()))
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def set_linewidth(self, w):
        """
        Set the line width.
        """
        DEBUG_MSG('set_linewidth()', 1, self)
        self.select()
        if w > 0 and w < 1:
            w = 1
        GraphicsContextBase.set_linewidth(self, w)
        lw = int(self.renderer.points_to_pixels(self._linewidth))
        if lw == 0:
            lw = 1
        self._pen.SetWidth(lw)
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def set_capstyle(self, cs):
        """
        Set the capstyle as a string in ('butt', 'round', 'projecting')
        """
        DEBUG_MSG('set_capstyle()', 1, self)
        self.select()
        GraphicsContextBase.set_capstyle(self, cs)
        self._pen.SetCap(GraphicsContextWx._capd[self._capstyle])
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def set_joinstyle(self, js):
        """
        Set the join style to be one of ('miter', 'round', 'bevel')
        """
        DEBUG_MSG('set_joinstyle()', 1, self)
        self.select()
        GraphicsContextBase.set_joinstyle(self, js)
        self._pen.SetJoin(GraphicsContextWx._joind[self._joinstyle])
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def set_linestyle(self, ls):
        """
        Set the line style to be one of
        """
        DEBUG_MSG('set_linestyle()', 1, self)
        self.select()
        GraphicsContextBase.set_linestyle(self, ls)
        try:
            self._style = GraphicsContextWx._dashd_wx[ls]
        except KeyError:
            self._style = wx.LONG_DASH

        if wx.Platform == '__WXMSW__':
            self.set_linewidth(1)
        self._pen.SetStyle(self._style)
        self.gfx_ctx.SetPen(self._pen)
        self.unselect()

    def get_wxcolour(self, color):
        """return a wx.Colour from RGB format"""
        DEBUG_MSG('get_wx_color()', 1, self)
        if len(color) == 3:
            r, g, b = color
            r *= 255
            g *= 255
            b *= 255
            return wx.Colour(red=int(r), green=int(g), blue=int(b))
        else:
            r, g, b, a = color
            r *= 255
            g *= 255
            b *= 255
            a *= 255
            return wx.Colour(red=int(r), green=int(g), blue=int(b), alpha=int(a))


class FigureCanvasWx(FigureCanvasBase, wx.Panel):
    """
    The FigureCanvas contains the figure and does event handling.

    In the wxPython backend, it is derived from wxPanel, and (usually) lives
    inside a frame instantiated by a FigureManagerWx. The parent window probably
    implements a wx.Sizer to control the displayed control size - but we give a
    hint as to our preferred minimum size.
    """
    keyvald = {wx.WXK_CONTROL: 'control', 
       wx.WXK_SHIFT: 'shift', 
       wx.WXK_ALT: 'alt', 
       wx.WXK_LEFT: 'left', 
       wx.WXK_UP: 'up', 
       wx.WXK_RIGHT: 'right', 
       wx.WXK_DOWN: 'down', 
       wx.WXK_ESCAPE: 'escape', 
       wx.WXK_F1: 'f1', 
       wx.WXK_F2: 'f2', 
       wx.WXK_F3: 'f3', 
       wx.WXK_F4: 'f4', 
       wx.WXK_F5: 'f5', 
       wx.WXK_F6: 'f6', 
       wx.WXK_F7: 'f7', 
       wx.WXK_F8: 'f8', 
       wx.WXK_F9: 'f9', 
       wx.WXK_F10: 'f10', 
       wx.WXK_F11: 'f11', 
       wx.WXK_F12: 'f12', 
       wx.WXK_SCROLL: 'scroll_lock', 
       wx.WXK_PAUSE: 'break', 
       wx.WXK_BACK: 'backspace', 
       wx.WXK_RETURN: 'enter', 
       wx.WXK_INSERT: 'insert', 
       wx.WXK_DELETE: 'delete', 
       wx.WXK_HOME: 'home', 
       wx.WXK_END: 'end', 
       wx.WXK_PRIOR: 'pageup', 
       wx.WXK_NEXT: 'pagedown', 
       wx.WXK_PAGEUP: 'pageup', 
       wx.WXK_PAGEDOWN: 'pagedown', 
       wx.WXK_NUMPAD0: '0', 
       wx.WXK_NUMPAD1: '1', 
       wx.WXK_NUMPAD2: '2', 
       wx.WXK_NUMPAD3: '3', 
       wx.WXK_NUMPAD4: '4', 
       wx.WXK_NUMPAD5: '5', 
       wx.WXK_NUMPAD6: '6', 
       wx.WXK_NUMPAD7: '7', 
       wx.WXK_NUMPAD8: '8', 
       wx.WXK_NUMPAD9: '9', 
       wx.WXK_NUMPAD_ADD: '+', 
       wx.WXK_NUMPAD_SUBTRACT: '-', 
       wx.WXK_NUMPAD_MULTIPLY: '*', 
       wx.WXK_NUMPAD_DIVIDE: '/', 
       wx.WXK_NUMPAD_DECIMAL: 'dec', 
       wx.WXK_NUMPAD_ENTER: 'enter', 
       wx.WXK_NUMPAD_UP: 'up', 
       wx.WXK_NUMPAD_RIGHT: 'right', 
       wx.WXK_NUMPAD_DOWN: 'down', 
       wx.WXK_NUMPAD_LEFT: 'left', 
       wx.WXK_NUMPAD_PRIOR: 'pageup', 
       wx.WXK_NUMPAD_NEXT: 'pagedown', 
       wx.WXK_NUMPAD_PAGEUP: 'pageup', 
       wx.WXK_NUMPAD_PAGEDOWN: 'pagedown', 
       wx.WXK_NUMPAD_HOME: 'home', 
       wx.WXK_NUMPAD_END: 'end', 
       wx.WXK_NUMPAD_INSERT: 'insert', 
       wx.WXK_NUMPAD_DELETE: 'delete'}

    def __init__(self, parent, id, figure):
        """
        Initialise a FigureWx instance.

        - Initialise the FigureCanvasBase and wxPanel parents.
        - Set event handlers for:
          EVT_SIZE  (Resize event)
          EVT_PAINT (Paint event)
        """
        FigureCanvasBase.__init__(self, figure)
        l, b, w, h = figure.bbox.bounds
        w = int(math.ceil(w))
        h = int(math.ceil(h))
        wx.Panel.__init__(self, parent, id, size=wx.Size(w, h))

        def do_nothing(*args, **kwargs):
            warnings.warn('could not find a setinitialsize function for backend_wx; please report your wxpython version=%s to the matplotlib developers list' % backend_version)

        try:
            getattr(self, 'SetInitialSize')
        except AttributeError:
            self.SetInitialSize = getattr(self, 'SetBestFittingSize', do_nothing)

        if not hasattr(self, 'IsShownOnScreen'):
            self.IsShownOnScreen = getattr(self, 'IsVisible', (lambda *args: True))
        self.bitmap = wx.EmptyBitmap(w, h)
        DEBUG_MSG('__init__() - bitmap w:%d h:%d' % (w, h), 2, self)
        self._isDrawn = False
        bind(self, wx.EVT_SIZE, self._onSize)
        bind(self, wx.EVT_PAINT, self._onPaint)
        bind(self, wx.EVT_ERASE_BACKGROUND, self._onEraseBackground)
        bind(self, wx.EVT_KEY_DOWN, self._onKeyDown)
        bind(self, wx.EVT_KEY_UP, self._onKeyUp)
        bind(self, wx.EVT_RIGHT_DOWN, self._onRightButtonDown)
        bind(self, wx.EVT_RIGHT_DCLICK, self._onRightButtonDClick)
        bind(self, wx.EVT_RIGHT_UP, self._onRightButtonUp)
        bind(self, wx.EVT_MOUSEWHEEL, self._onMouseWheel)
        bind(self, wx.EVT_LEFT_DOWN, self._onLeftButtonDown)
        bind(self, wx.EVT_LEFT_DCLICK, self._onLeftButtonDClick)
        bind(self, wx.EVT_LEFT_UP, self._onLeftButtonUp)
        bind(self, wx.EVT_MOTION, self._onMotion)
        bind(self, wx.EVT_LEAVE_WINDOW, self._onLeave)
        bind(self, wx.EVT_ENTER_WINDOW, self._onEnter)
        bind(self, wx.EVT_IDLE, self._onIdle)
        bind(self, wx.EVT_MIDDLE_DOWN, self._onMiddleButtonDown)
        bind(self, wx.EVT_MIDDLE_DCLICK, self._onMiddleButtonDClick)
        bind(self, wx.EVT_MIDDLE_UP, self._onMiddleButtonUp)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.macros = {}
        self._printerData = None
        self._printerPageData = None
        self.printer_width = 5.5
        self.printer_margin = 0.5
        return

    def Destroy(self, *args, **kwargs):
        wx.Panel.Destroy(self, *args, **kwargs)

    def Copy_to_Clipboard(self, event=None):
        """copy bitmap of canvas to system clipboard"""
        bmp_obj = wx.BitmapDataObject()
        bmp_obj.SetBitmap(self.bitmap)
        if not wx.TheClipboard.IsOpened():
            open_success = wx.TheClipboard.Open()
            if open_success:
                wx.TheClipboard.SetData(bmp_obj)
                wx.TheClipboard.Close()
                wx.TheClipboard.Flush()

    def Printer_Init(self):
        """
        initialize printer settings using wx methods

        Deprecated.
        """
        warnings.warn('Printer* methods will be removed', DeprecationWarning)
        self.printerData = wx.PrintData()
        self.printerData.SetPaperId(wx.PAPER_LETTER)
        self.printerData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printerPageData = wx.PageSetupDialogData()
        self.printerPageData.SetMarginBottomRight((25, 25))
        self.printerPageData.SetMarginTopLeft((25, 25))
        self.printerPageData.SetPrintData(self.printerData)
        self.printer_width = 5.5
        self.printer_margin = 0.5

    def _get_printerData(self):
        if self._printerData is None:
            warnings.warn('Printer* methods will be removed', DeprecationWarning)
            self._printerData = wx.PrintData()
            self._printerData.SetPaperId(wx.PAPER_LETTER)
            self._printerData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        return self._printerData

    printerData = property(_get_printerData)

    def _get_printerPageData(self):
        if self._printerPageData is None:
            warnings.warn('Printer* methods will be removed', DeprecationWarning)
            self._printerPageData = wx.PageSetupDialogData()
            self._printerPageData.SetMarginBottomRight((25, 25))
            self._printerPageData.SetMarginTopLeft((25, 25))
            self._printerPageData.SetPrintData(self.printerData)
        return self._printerPageData

    printerPageData = property(_get_printerPageData)

    def Printer_Setup(self, event=None):
        """
        set up figure for printing.  The standard wx Printer
        Setup Dialog seems to die easily. Therefore, this setup
        simply asks for image width and margin for printing.
        Deprecated.
        """
        dmsg = 'Width of output figure in inches.\nThe current aspect ratio will be kept.'
        warnings.warn('Printer* methods will be removed', DeprecationWarning)
        dlg = wx.Dialog(self, -1, 'Page Setup for Printing', (-1, -1))
        df = dlg.GetFont()
        df.SetWeight(wx.NORMAL)
        df.SetPointSize(11)
        dlg.SetFont(df)
        x_wid = wx.TextCtrl(dlg, -1, value='%.2f' % self.printer_width, size=(70, -1))
        x_mrg = wx.TextCtrl(dlg, -1, value='%.2f' % self.printer_margin, size=(70,
                                                                               -1))
        sizerAll = wx.BoxSizer(wx.VERTICAL)
        sizerAll.Add(wx.StaticText(dlg, -1, dmsg), 0, wx.ALL | wx.EXPAND, 5)
        sizer = wx.FlexGridSizer(0, 3)
        sizerAll.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(wx.StaticText(dlg, -1, 'Figure Width'), 1, wx.ALIGN_LEFT | wx.ALL, 2)
        sizer.Add(x_wid, 1, wx.ALIGN_LEFT | wx.ALL, 2)
        sizer.Add(wx.StaticText(dlg, -1, 'in'), 1, wx.ALIGN_LEFT | wx.ALL, 2)
        sizer.Add(wx.StaticText(dlg, -1, 'Margin'), 1, wx.ALIGN_LEFT | wx.ALL, 2)
        sizer.Add(x_mrg, 1, wx.ALIGN_LEFT | wx.ALL, 2)
        sizer.Add(wx.StaticText(dlg, -1, 'in'), 1, wx.ALIGN_LEFT | wx.ALL, 2)
        btn = wx.Button(dlg, wx.ID_OK, ' OK ')
        btn.SetDefault()
        sizer.Add(btn, 1, wx.ALIGN_LEFT, 5)
        btn = wx.Button(dlg, wx.ID_CANCEL, ' CANCEL ')
        sizer.Add(btn, 1, wx.ALIGN_LEFT, 5)
        dlg.SetSizer(sizerAll)
        dlg.SetAutoLayout(True)
        sizerAll.Fit(dlg)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.printer_width = float(x_wid.GetValue())
                self.printer_margin = float(x_mrg.GetValue())
            except:
                pass

        if self.printer_width + self.printer_margin > 7.5:
            self.printerData.SetOrientation(wx.LANDSCAPE)
        else:
            self.printerData.SetOrientation(wx.PORTRAIT)
        dlg.Destroy()

    def Printer_Setup2(self, event=None):
        """
        set up figure for printing.  Using the standard wx Printer
        Setup Dialog.

        Deprecated.
        """
        warnings.warn('Printer* methods will be removed', DeprecationWarning)
        if hasattr(self, 'printerData'):
            data = wx.PageSetupDialogData()
            data.SetPrintData(self.printerData)
        else:
            data = wx.PageSetupDialogData()
        data.SetMarginTopLeft((15, 15))
        data.SetMarginBottomRight((15, 15))
        dlg = wx.PageSetupDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            tl = data.GetMarginTopLeft()
            br = data.GetMarginBottomRight()
        self.printerData = wx.PrintData(data.GetPrintData())
        dlg.Destroy()

    def Printer_Preview(self, event=None):
        """
        generate Print Preview with wx Print mechanism

        Deprecated.
        """
        warnings.warn('Printer* methods will be removed', DeprecationWarning)
        po1 = PrintoutWx(self, width=self.printer_width, margin=self.printer_margin)
        po2 = PrintoutWx(self, width=self.printer_width, margin=self.printer_margin)
        self.preview = wx.PrintPreview(po1, po2, self.printerData)
        if not self.preview.Ok():
            print('error with preview')
        self.preview.SetZoom(50)
        frameInst = self
        while not isinstance(frameInst, wx.Frame):
            frameInst = frameInst.GetParent()

        frame = wx.PreviewFrame(self.preview, frameInst, 'Preview')
        frame.Initialize()
        frame.SetPosition(self.GetPosition())
        frame.SetSize((850, 650))
        frame.Centre(wx.BOTH)
        frame.Show(True)
        self.gui_repaint()

    def Printer_Print(self, event=None):
        """
        Print figure using wx Print mechanism

        Deprecated.
        """
        warnings.warn('Printer* methods will be removed', DeprecationWarning)
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(self.printerData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = PrintoutWx(self, width=int(self.printer_width), margin=int(self.printer_margin))
        print_ok = printer.Print(self, printout, True)
        if wx.VERSION_STRING >= '2.5':
            if not print_ok and not printer.GetLastError() == wx.PRINTER_CANCELLED:
                wx.MessageBox('There was a problem printing.\n                Perhaps your current printer is not set correctly?', 'Printing', wx.OK)
        elif not print_ok:
            wx.MessageBox('There was a problem printing.\n                Perhaps your current printer is not set correctly?', 'Printing', wx.OK)
        printout.Destroy()
        self.gui_repaint()

    def draw_idle(self):
        """
        Delay rendering until the GUI is idle.
        """
        DEBUG_MSG('draw_idle()', 1, self)
        self._isDrawn = False
        if hasattr(self, '_idletimer'):
            self._idletimer.Restart(IDLE_DELAY)
        else:
            self._idletimer = wx.FutureCall(IDLE_DELAY, self._onDrawIdle)

    def _onDrawIdle(self, *args, **kwargs):
        if wx.GetApp().Pending():
            self._idletimer.Restart(IDLE_DELAY, *args, **kwargs)
        else:
            del self._idletimer
            if not self._isDrawn:
                self.draw(*args, **kwargs)

    def draw(self, drawDC=None):
        """
        Render the figure using RendererWx instance renderer, or using a
        previously defined renderer if none is specified.
        """
        DEBUG_MSG('draw()', 1, self)
        self.renderer = RendererWx(self.bitmap, self.figure.dpi)
        self.figure.draw(self.renderer)
        self._isDrawn = True
        self.gui_repaint(drawDC=drawDC)

    def new_timer(self, *args, **kwargs):
        """
        Creates a new backend-specific subclass of :class:`backend_bases.Timer`.
        This is useful for getting periodic events through the backend's native
        event loop. Implemented only for backends with GUIs.

        optional arguments:

        *interval*
          Timer interval in milliseconds
        *callbacks*
          Sequence of (func, args, kwargs) where func(*args, **kwargs) will
          be executed by the timer every *interval*.
        """
        return TimerWx(self, *args, **kwargs)

    def flush_events(self):
        wx.Yield()

    def start_event_loop(self, timeout=0):
        """
        Start an event loop.  This is used to start a blocking event
        loop so that interactive functions, such as ginput and
        waitforbuttonpress, can wait for events.  This should not be
        confused with the main GUI event loop, which is always running
        and has nothing to do with this.

        Call signature::

        start_event_loop(self,timeout=0)

        This call blocks until a callback function triggers
        stop_event_loop() or *timeout* is reached.  If *timeout* is
        <=0, never timeout.

        Raises RuntimeError if event loop is already running.
        """
        if hasattr(self, '_event_loop'):
            raise RuntimeError('Event loop already running')
        id = wx.NewId()
        timer = wx.Timer(self, id=id)
        if timeout > 0:
            timer.Start(timeout * 1000, oneShot=True)
            bind(self, wx.EVT_TIMER, self.stop_event_loop, id=id)
        self._event_loop = wx.EventLoop()
        self._event_loop.Run()
        timer.Stop()

    def stop_event_loop(self, event=None):
        """
        Stop an event loop.  This is used to stop a blocking event
        loop so that interactive functions, such as ginput and
        waitforbuttonpress, can wait for events.

        Call signature::

        stop_event_loop_default(self)
        """
        if hasattr(self, '_event_loop'):
            if self._event_loop.IsRunning():
                self._event_loop.Exit()
            del self._event_loop

    def _get_imagesave_wildcards(self):
        """return the wildcard string for the filesave dialog"""
        default_filetype = self.get_default_filetype()
        filetypes = self.get_supported_filetypes_grouped()
        sorted_filetypes = filetypes.items()
        sorted_filetypes.sort()
        wildcards = []
        extensions = []
        filter_index = 0
        for i, (name, exts) in enumerate(sorted_filetypes):
            ext_list = (';').join([ '*.%s' % ext for ext in exts ])
            extensions.append(exts[0])
            wildcard = '%s (%s)|%s' % (name, ext_list, ext_list)
            if default_filetype in exts:
                filter_index = i
            wildcards.append(wildcard)

        wildcards = ('|').join(wildcards)
        return (wildcards, extensions, filter_index)

    def gui_repaint(self, drawDC=None):
        """
        Performs update of the displayed image on the GUI canvas, using the
        supplied device context.  If drawDC is None, a ClientDC will be used to
        redraw the image.
        """
        DEBUG_MSG('gui_repaint()', 1, self)
        if self.IsShownOnScreen():
            if drawDC is None:
                drawDC = wx.ClientDC(self)
            drawDC.BeginDrawing()
            drawDC.DrawBitmap(self.bitmap, 0, 0)
            drawDC.EndDrawing()
        return

    filetypes = FigureCanvasBase.filetypes.copy()
    filetypes['bmp'] = 'Windows bitmap'
    filetypes['jpeg'] = 'JPEG'
    filetypes['jpg'] = 'JPEG'
    filetypes['pcx'] = 'PCX'
    filetypes['png'] = 'Portable Network Graphics'
    filetypes['tif'] = 'Tagged Image Format File'
    filetypes['tiff'] = 'Tagged Image Format File'
    filetypes['xpm'] = 'X pixmap'

    def print_figure(self, filename, *args, **kwargs):
        FigureCanvasBase.print_figure(self, filename, *args, **kwargs)
        if self._isDrawn:
            self.draw()

    def print_bmp(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_BMP, *args, **kwargs)

    def print_jpeg(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_JPEG, *args, **kwargs)

    print_jpg = print_jpeg

    def print_pcx(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_PCX, *args, **kwargs)

    def print_png(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_PNG, *args, **kwargs)

    def print_tiff(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_TIF, *args, **kwargs)

    print_tif = print_tiff

    def print_xpm(self, filename, *args, **kwargs):
        return self._print_image(filename, wx.BITMAP_TYPE_XPM, *args, **kwargs)

    def _print_image(self, filename, filetype, *args, **kwargs):
        origBitmap = self.bitmap
        l, b, width, height = self.figure.bbox.bounds
        width = int(math.ceil(width))
        height = int(math.ceil(height))
        self.bitmap = wx.EmptyBitmap(width, height)
        renderer = RendererWx(self.bitmap, self.figure.dpi)
        gc = renderer.new_gc()
        self.figure.draw(renderer)
        if is_string_like(filename):
            if not self.bitmap.SaveFile(filename, filetype):
                DEBUG_MSG('print_figure() file save error', 4, self)
                raise RuntimeError('Could not save figure to %s\n' % filename)
        elif is_writable_file_like(filename):
            if not self.bitmap.ConvertToImage().SaveStream(filename, filetype):
                DEBUG_MSG('print_figure() file save error', 4, self)
                raise RuntimeError('Could not save figure to %s\n' % filename)
        self.bitmap = origBitmap
        if self._isDrawn:
            self.draw()
        self.Refresh()

    def _onPaint(self, evt):
        """
        Called when wxPaintEvt is generated
        """
        DEBUG_MSG('_onPaint()', 1, self)
        drawDC = wx.PaintDC(self)
        if not self._isDrawn:
            self.draw(drawDC=drawDC)
        else:
            self.gui_repaint(drawDC=drawDC)
        evt.Skip()

    def _onEraseBackground(self, evt):
        """
        Called when window is redrawn; since we are blitting the entire
        image, we can leave this blank to suppress flicker.
        """
        pass

    def _onSize(self, evt):
        """
        Called when wxEventSize is generated.

        In this application we attempt to resize to fit the window, so it
        is better to take the performance hit and redraw the whole window.
        """
        DEBUG_MSG('_onSize()', 2, self)
        self._width, self._height = self.GetClientSize()
        self.bitmap = wx.EmptyBitmap(self._width, self._height)
        self._isDrawn = False
        if self._width <= 1 or self._height <= 1:
            return
        dpival = self.figure.dpi
        winch = self._width / dpival
        hinch = self._height / dpival
        self.figure.set_size_inches(winch, hinch)
        self.Refresh(eraseBackground=False)
        FigureCanvasBase.resize_event(self)

    def _get_key(self, evt):
        keyval = evt.m_keyCode
        if keyval in self.keyvald:
            key = self.keyvald[keyval]
        else:
            if keyval < 256:
                key = chr(keyval)
                if not evt.ShiftDown():
                    key = key.lower()
            else:
                key = None
            for meth, prefix in (
             [
              evt.AltDown, 'alt'],
             [
              evt.ControlDown, 'ctrl']):
                if meth():
                    key = ('{}+{}').format(prefix, key)

        return key

    def _onIdle(self, evt):
        """a GUI idle event"""
        evt.Skip()
        FigureCanvasBase.idle_event(self, guiEvent=evt)

    def _onKeyDown(self, evt):
        """Capture key press."""
        key = self._get_key(evt)
        evt.Skip()
        FigureCanvasBase.key_press_event(self, key, guiEvent=evt)

    def _onKeyUp(self, evt):
        """Release key."""
        key = self._get_key(evt)
        evt.Skip()
        FigureCanvasBase.key_release_event(self, key, guiEvent=evt)

    def _onRightButtonDown(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 3, guiEvent=evt)

    def _onRightButtonDClick(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 3, dblclick=True, guiEvent=evt)

    def _onRightButtonUp(self, evt):
        """End measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        if self.HasCapture():
            self.ReleaseMouse()
        FigureCanvasBase.button_release_event(self, x, y, 3, guiEvent=evt)

    def _onLeftButtonDown(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 1, guiEvent=evt)

    def _onLeftButtonDClick(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 1, dblclick=True, guiEvent=evt)

    def _onLeftButtonUp(self, evt):
        """End measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        if self.HasCapture():
            self.ReleaseMouse()
        FigureCanvasBase.button_release_event(self, x, y, 1, guiEvent=evt)

    def _onMiddleButtonDown(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 2, guiEvent=evt)

    def _onMiddleButtonDClick(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        self.CaptureMouse()
        FigureCanvasBase.button_press_event(self, x, y, 2, dblclick=True, guiEvent=evt)

    def _onMiddleButtonUp(self, evt):
        """End measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        if self.HasCapture():
            self.ReleaseMouse()
        FigureCanvasBase.button_release_event(self, x, y, 2, guiEvent=evt)

    def _onMouseWheel(self, evt):
        """Translate mouse wheel events into matplotlib events"""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        delta = evt.GetWheelDelta()
        rotation = evt.GetWheelRotation()
        rate = evt.GetLinesPerAction()
        step = rate * float(rotation) / delta
        evt.Skip()
        if wx.Platform == '__WXMAC__':
            if not hasattr(self, '_skipwheelevent'):
                self._skipwheelevent = True
            else:
                if self._skipwheelevent:
                    self._skipwheelevent = False
                    return
                self._skipwheelevent = True
        FigureCanvasBase.scroll_event(self, x, y, step, guiEvent=evt)

    def _onMotion(self, evt):
        """Start measuring on an axis."""
        x = evt.GetX()
        y = self.figure.bbox.height - evt.GetY()
        evt.Skip()
        FigureCanvasBase.motion_notify_event(self, x, y, guiEvent=evt)

    def _onLeave(self, evt):
        """Mouse has left the window."""
        evt.Skip()
        FigureCanvasBase.leave_notify_event(self, guiEvent=evt)

    def _onEnter(self, evt):
        """Mouse has entered the window."""
        FigureCanvasBase.enter_notify_event(self, guiEvent=evt)


def _create_wx_app():
    """
    Creates a wx.PySimpleApp instance if a wx.App has not been created.
    """
    wxapp = wx.GetApp()
    if wxapp is None:
        wxapp = wx.PySimpleApp()
        wxapp.SetExitOnFrameDelete(True)
        _create_wx_app.theWxApp = wxapp
    return


def draw_if_interactive():
    """
    This should be overriden in a windowing environment if drawing
    should be done in interactive python mode
    """
    DEBUG_MSG('draw_if_interactive()', 1, None)
    if matplotlib.is_interactive():
        figManager = Gcf.get_active()
        if figManager is not None:
            figManager.canvas.draw_idle()
    return


class Show(ShowBase):

    def mainloop(self):
        needmain = not wx.App.IsMainLoopRunning()
        if needmain:
            wxapp = wx.GetApp()
            if wxapp is not None:
                wxapp.MainLoop()
        return


show = Show()

def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    DEBUG_MSG('new_figure_manager()', 3, None)
    _create_wx_app()
    FigureClass = kwargs.pop('FigureClass', Figure)
    fig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, fig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    fig = figure
    frame = FigureFrameWx(num, fig)
    figmgr = frame.get_figure_manager()
    if matplotlib.is_interactive():
        figmgr.frame.Show()
    return figmgr


class FigureFrameWx(wx.Frame):

    def __init__(self, num, fig):
        if wx.Platform == '__WXMSW__':
            pos = wx.DefaultPosition
        else:
            pos = wx.Point(20, 20)
        l, b, w, h = fig.bbox.bounds
        wx.Frame.__init__(self, parent=None, id=-1, pos=pos, title='Figure %d' % num)
        DEBUG_MSG('__init__()', 1, self)
        self.num = num
        statbar = StatusBarWx(self)
        self.SetStatusBar(statbar)
        self.canvas = self.get_canvas(fig)
        self.canvas.SetInitialSize(wx.Size(fig.bbox.width, fig.bbox.height))
        self.canvas.SetFocus()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        self.toolbar = self._get_toolbar(statbar)
        if self.toolbar is not None:
            self.toolbar.Realize()
            if wx.Platform == '__WXMAC__':
                self.SetToolBar(self.toolbar)
            else:
                tw, th = self.toolbar.GetSizeTuple()
                fw, fh = self.canvas.GetSizeTuple()
                self.toolbar.SetSize(wx.Size(fw, th))
                self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.canvas.SetMinSize((2, 2))
        self.figmgr = FigureManagerWx(self.canvas, num, self)
        bind(self, wx.EVT_CLOSE, self._onClose)
        return

    def _get_toolbar(self, statbar):
        if rcParams['toolbar'] == 'classic':
            toolbar = NavigationToolbarWx(self.canvas, True)
        elif rcParams['toolbar'] == 'toolbar2':
            toolbar = NavigationToolbar2Wx(self.canvas)
            toolbar.set_status_bar(statbar)
        else:
            toolbar = None
        return toolbar

    def get_canvas(self, fig):
        return FigureCanvasWx(self, -1, fig)

    def get_figure_manager(self):
        DEBUG_MSG('get_figure_manager()', 1, self)
        return self.figmgr

    def _onClose(self, evt):
        DEBUG_MSG('onClose()', 1, self)
        self.canvas.close_event()
        self.canvas.stop_event_loop()
        Gcf.destroy(self.num)

    def GetToolBar(self):
        """Override wxFrame::GetToolBar as we don't have managed toolbar"""
        return self.toolbar

    def Destroy(self, *args, **kwargs):
        try:
            self.canvas.mpl_disconnect(self.toolbar._idDrag)
        except AttributeError:
            pass

        wx.Frame.Destroy(self, *args, **kwargs)
        if self.toolbar is not None:
            self.toolbar.Destroy()
        wxapp = wx.GetApp()
        if wxapp:
            wxapp.Yield()
        return True


class FigureManagerWx(FigureManagerBase):
    """
    This class contains the FigureCanvas and GUI frame

    It is instantiated by GcfWx whenever a new figure is created. GcfWx is
    responsible for managing multiple instances of FigureManagerWx.

    public attrs

    canvas - a FigureCanvasWx(wx.Panel) instance
    window - a wxFrame instance - http://www.lpthe.jussieu.fr/~zeitlin/wxWindows/docs/wxwin_wxframe.html#wxframe
    """

    def __init__(self, canvas, num, frame):
        DEBUG_MSG('__init__()', 1, self)
        FigureManagerBase.__init__(self, canvas, num)
        self.frame = frame
        self.window = frame
        self.tb = frame.GetToolBar()
        self.toolbar = self.tb

        def notify_axes_change(fig):
            """this will be called whenever the current axes is changed"""
            if self.tb != None:
                self.tb.update()
            return

        self.canvas.figure.add_axobserver(notify_axes_change)

    def show(self):
        self.frame.Show()

    def destroy(self, *args):
        DEBUG_MSG('destroy()', 1, self)
        self.frame.Destroy()
        wx.WakeUpIdle()

    def get_window_title(self):
        return self.window.GetTitle()

    def set_window_title(self, title):
        self.window.SetTitle(title)

    def resize(self, width, height):
        """Set the canvas size in pixels"""
        self.canvas.SetInitialSize(wx.Size(width, height))
        self.window.GetSizer().Fit(self.window)


_NTB_AXISMENU = wx.NewId()
_NTB_AXISMENU_BUTTON = wx.NewId()
_NTB_X_PAN_LEFT = wx.NewId()
_NTB_X_PAN_RIGHT = wx.NewId()
_NTB_X_ZOOMIN = wx.NewId()
_NTB_X_ZOOMOUT = wx.NewId()
_NTB_Y_PAN_UP = wx.NewId()
_NTB_Y_PAN_DOWN = wx.NewId()
_NTB_Y_ZOOMIN = wx.NewId()
_NTB_Y_ZOOMOUT = wx.NewId()
_NTB_SAVE = wx.NewId()
_NTB_CLOSE = wx.NewId()

def _load_bitmap(filename):
    """
    Load a bitmap file from the backends/images subdirectory in which the
    matplotlib library is installed. The filename parameter should not
    contain any path information as this is determined automatically.

    Returns a wx.Bitmap object
    """
    basedir = os.path.join(rcParams['datapath'], 'images')
    bmpFilename = os.path.normpath(os.path.join(basedir, filename))
    if not os.path.exists(bmpFilename):
        raise IOError('Could not find bitmap file "%s"; dying' % bmpFilename)
    bmp = wx.Bitmap(bmpFilename)
    return bmp


class MenuButtonWx(wx.Button):
    """
    wxPython does not permit a menu to be incorporated directly into a toolbar.
    This class simulates the effect by associating a pop-up menu with a button
    in the toolbar, and managing this as though it were a menu.
    """

    def __init__(self, parent):
        wx.Button.__init__(self, parent, _NTB_AXISMENU_BUTTON, 'Axes:        ', style=wx.BU_EXACTFIT)
        self._toolbar = parent
        self._menu = wx.Menu()
        self._axisId = []
        self._allId = wx.NewId()
        self._invertId = wx.NewId()
        self._menu.Append(self._allId, 'All', 'Select all axes', False)
        self._menu.Append(self._invertId, 'Invert', 'Invert axes selected', False)
        self._menu.AppendSeparator()
        bind(self, wx.EVT_BUTTON, self._onMenuButton, id=_NTB_AXISMENU_BUTTON)
        bind(self, wx.EVT_MENU, self._handleSelectAllAxes, id=self._allId)
        bind(self, wx.EVT_MENU, self._handleInvertAxesSelected, id=self._invertId)

    def Destroy(self):
        self._menu.Destroy()
        self.Destroy()

    def _onMenuButton(self, evt):
        """Handle menu button pressed."""
        x, y = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        self.PopupMenuXY(self._menu, x, y + h - 4)
        evt.Skip()

    def _handleSelectAllAxes(self, evt):
        """Called when the 'select all axes' menu item is selected."""
        if len(self._axisId) == 0:
            return
        for i in range(len(self._axisId)):
            self._menu.Check(self._axisId[i], True)

        self._toolbar.set_active(self.getActiveAxes())
        evt.Skip()

    def _handleInvertAxesSelected(self, evt):
        """Called when the invert all menu item is selected"""
        if len(self._axisId) == 0:
            return
        for i in range(len(self._axisId)):
            if self._menu.IsChecked(self._axisId[i]):
                self._menu.Check(self._axisId[i], False)
            else:
                self._menu.Check(self._axisId[i], True)

        self._toolbar.set_active(self.getActiveAxes())
        evt.Skip()

    def _onMenuItemSelected(self, evt):
        """Called whenever one of the specific axis menu items is selected"""
        current = self._menu.IsChecked(evt.GetId())
        if current:
            new = False
        else:
            new = True
        self._menu.Check(evt.GetId(), new)
        self._toolbar.set_active(self.getActiveAxes())
        evt.Skip()

    def updateAxes(self, maxAxis):
        """Ensures that there are entries for max_axis axes in the menu
        (selected by default)."""
        if maxAxis > len(self._axisId):
            for i in range(len(self._axisId) + 1, maxAxis + 1, 1):
                menuId = wx.NewId()
                self._axisId.append(menuId)
                self._menu.Append(menuId, 'Axis %d' % i, 'Select axis %d' % i, True)
                self._menu.Check(menuId, True)
                bind(self, wx.EVT_MENU, self._onMenuItemSelected, id=menuId)

        elif maxAxis < len(self._axisId):
            for menuId in self._axisId[maxAxis:]:
                self._menu.Delete(menuId)

            self._axisId = self._axisId[:maxAxis]
        self._toolbar.set_active(range(maxAxis))

    def getActiveAxes(self):
        """Return a list of the selected axes."""
        active = []
        for i in range(len(self._axisId)):
            if self._menu.IsChecked(self._axisId[i]):
                active.append(i)

        return active

    def updateButtonText(self, lst):
        """Update the list of selected axes in the menu button"""
        axis_txt = ''
        for e in lst:
            axis_txt += '%d,' % (e + 1)

        self.SetLabel('Axes: %s' % axis_txt[:-1])


cursord = {cursors.MOVE: wx.CURSOR_HAND, 
   cursors.HAND: wx.CURSOR_HAND, 
   cursors.POINTER: wx.CURSOR_ARROW, 
   cursors.SELECT_REGION: wx.CURSOR_CROSS}

class SubplotToolWX(wx.Frame):

    def __init__(self, targetfig):
        wx.Frame.__init__(self, None, -1, 'Configure subplots')
        toolfig = Figure((6, 3))
        canvas = FigureCanvasWx(self, -1, toolfig)
        figmgr = FigureManager(canvas, 1, self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        tool = SubplotTool(targetfig, toolfig)
        return


class NavigationToolbar2Wx(NavigationToolbar2, wx.ToolBar):

    def __init__(self, canvas):
        wx.ToolBar.__init__(self, canvas.GetParent(), -1)
        NavigationToolbar2.__init__(self, canvas)
        self.canvas = canvas
        self._idle = True
        self.statbar = None
        return

    def get_canvas(self, frame, fig):
        return FigureCanvasWx(frame, -1, fig)

    def _init_toolbar(self):
        DEBUG_MSG('_init_toolbar', 1, self)
        self._parent = self.canvas.GetParent()
        self.wx_ids = {}
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.AddSeparator()
                continue
            self.wx_ids[text] = wx.NewId()
            if text in ('Pan', 'Zoom'):
                self.AddCheckTool(self.wx_ids[text], _load_bitmap(image_file + '.png'), shortHelp=text, longHelp=tooltip_text)
            else:
                self.AddSimpleTool(self.wx_ids[text], _load_bitmap(image_file + '.png'), text, tooltip_text)
            bind(self, wx.EVT_TOOL, getattr(self, callback), id=self.wx_ids[text])

        self.Realize()
        return

    def zoom(self, *args):
        self.ToggleTool(self.wx_ids['Pan'], False)
        NavigationToolbar2.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self.wx_ids['Zoom'], False)
        NavigationToolbar2.pan(self, *args)

    def configure_subplots(self, evt):
        frame = wx.Frame(None, -1, 'Configure subplots')
        toolfig = Figure((6, 3))
        canvas = self.get_canvas(frame, toolfig)
        figmgr = FigureManager(canvas, 1, frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        frame.SetSizer(sizer)
        frame.Fit()
        tool = SubplotTool(self.canvas.figure, toolfig)
        frame.Show()
        return

    def save_figure(self, *args):
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = self.canvas.get_default_filename()
        dlg = wx.FileDialog(self._parent, 'Save to file', '', default_file, filetypes, wx.SAVE | wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(filter_index)
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            filename = dlg.GetFilename()
            DEBUG_MSG('Save file dir:%s name:%s' % (dirname, filename), 3, self)
            format = exts[dlg.GetFilterIndex()]
            basename, ext = os.path.splitext(filename)
            if ext.startswith('.'):
                ext = ext[1:]
            if ext in ('svg', 'pdf', 'ps', 'eps', 'png') and format != ext:
                warnings.warn('extension %s did not match the selected image type %s; going with %s' % (ext, format, ext), stacklevel=0)
                format = ext
            try:
                self.canvas.print_figure(os.path.join(dirname, filename), format=format)
            except Exception as e:
                error_msg_wx(str(e))

    def set_cursor(self, cursor):
        cursor = wx.StockCursor(cursord[cursor])
        self.canvas.SetCursor(cursor)

    def release(self, event):
        try:
            del self.lastrect
        except AttributeError:
            pass

    def dynamic_update(self):
        d = self._idle
        self._idle = False
        if d:
            self.canvas.draw()
            self._idle = True

    def draw_rubberband(self, event, x0, y0, x1, y1):
        """adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/189744"""
        canvas = self.canvas
        dc = wx.ClientDC(canvas)
        dc.SetLogicalFunction(wx.XOR)
        wbrush = wx.Brush(wx.Colour(255, 255, 255), wx.TRANSPARENT)
        wpen = wx.Pen(wx.Colour(200, 200, 200), 1, wx.SOLID)
        dc.SetBrush(wbrush)
        dc.SetPen(wpen)
        dc.ResetBoundingBox()
        dc.BeginDrawing()
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0
        if y1 < y0:
            y0, y1 = y1, y0
        if x1 < y0:
            x0, x1 = x1, x0
        w = x1 - x0
        h = y1 - y0
        rect = (
         int(x0), int(y0), int(w), int(h))
        try:
            lastrect = self.lastrect
        except AttributeError:
            pass
        else:
            dc.DrawRectangle(*lastrect)

        self.lastrect = rect
        dc.DrawRectangle(*rect)
        dc.EndDrawing()

    def set_status_bar(self, statbar):
        self.statbar = statbar

    def set_message(self, s):
        if self.statbar is not None:
            self.statbar.set_function(s)
        return

    def set_history_buttons(self):
        can_backward = self._views._pos > 0
        can_forward = self._views._pos < len(self._views._elements) - 1
        self.EnableTool(self.wx_ids['Back'], can_backward)
        self.EnableTool(self.wx_ids['Forward'], can_forward)


class NavigationToolbarWx(wx.ToolBar):

    def __init__(self, canvas, can_kill=False):
        wx.ToolBar.__init__(self, canvas.GetParent(), -1)
        DEBUG_MSG('__init__()', 1, self)
        self.canvas = canvas
        self._lastControl = None
        self._mouseOnButton = None
        self._parent = canvas.GetParent()
        self._NTB_BUTTON_HANDLER = {_NTB_X_PAN_LEFT: self.panx, 
           _NTB_X_PAN_RIGHT: self.panx, 
           _NTB_X_ZOOMIN: self.zoomx, 
           _NTB_X_ZOOMOUT: self.zoomy, 
           _NTB_Y_PAN_UP: self.pany, 
           _NTB_Y_PAN_DOWN: self.pany, 
           _NTB_Y_ZOOMIN: self.zoomy, 
           _NTB_Y_ZOOMOUT: self.zoomy}
        self._create_menu()
        self._create_controls(can_kill)
        self.Realize()
        return

    def _create_menu(self):
        """
        Creates the 'menu' - implemented as a button which opens a
        pop-up menu since wxPython does not allow a menu as a control
        """
        DEBUG_MSG('_create_menu()', 1, self)
        self._menu = MenuButtonWx(self)
        self.AddControl(self._menu)
        self.AddSeparator()

    def _create_controls(self, can_kill):
        """
        Creates the button controls, and links them to event handlers
        """
        DEBUG_MSG('_create_controls()', 1, self)
        self.SetToolBitmapSize(wx.Size(16, 16))
        self.AddSimpleTool(_NTB_X_PAN_LEFT, _load_bitmap('stock_left.xpm'), 'Left', 'Scroll left')
        self.AddSimpleTool(_NTB_X_PAN_RIGHT, _load_bitmap('stock_right.xpm'), 'Right', 'Scroll right')
        self.AddSimpleTool(_NTB_X_ZOOMIN, _load_bitmap('stock_zoom-in.xpm'), 'Zoom in', 'Increase X axis magnification')
        self.AddSimpleTool(_NTB_X_ZOOMOUT, _load_bitmap('stock_zoom-out.xpm'), 'Zoom out', 'Decrease X axis magnification')
        self.AddSeparator()
        self.AddSimpleTool(_NTB_Y_PAN_UP, _load_bitmap('stock_up.xpm'), 'Up', 'Scroll up')
        self.AddSimpleTool(_NTB_Y_PAN_DOWN, _load_bitmap('stock_down.xpm'), 'Down', 'Scroll down')
        self.AddSimpleTool(_NTB_Y_ZOOMIN, _load_bitmap('stock_zoom-in.xpm'), 'Zoom in', 'Increase Y axis magnification')
        self.AddSimpleTool(_NTB_Y_ZOOMOUT, _load_bitmap('stock_zoom-out.xpm'), 'Zoom out', 'Decrease Y axis magnification')
        self.AddSeparator()
        self.AddSimpleTool(_NTB_SAVE, _load_bitmap('stock_save_as.xpm'), 'Save', 'Save plot contents as images')
        self.AddSeparator()
        bind(self, wx.EVT_TOOL, self._onLeftScroll, id=_NTB_X_PAN_LEFT)
        bind(self, wx.EVT_TOOL, self._onRightScroll, id=_NTB_X_PAN_RIGHT)
        bind(self, wx.EVT_TOOL, self._onXZoomIn, id=_NTB_X_ZOOMIN)
        bind(self, wx.EVT_TOOL, self._onXZoomOut, id=_NTB_X_ZOOMOUT)
        bind(self, wx.EVT_TOOL, self._onUpScroll, id=_NTB_Y_PAN_UP)
        bind(self, wx.EVT_TOOL, self._onDownScroll, id=_NTB_Y_PAN_DOWN)
        bind(self, wx.EVT_TOOL, self._onYZoomIn, id=_NTB_Y_ZOOMIN)
        bind(self, wx.EVT_TOOL, self._onYZoomOut, id=_NTB_Y_ZOOMOUT)
        bind(self, wx.EVT_TOOL, self._onSave, id=_NTB_SAVE)
        bind(self, wx.EVT_TOOL_ENTER, self._onEnterTool, id=self.GetId())
        if can_kill:
            bind(self, wx.EVT_TOOL, self._onClose, id=_NTB_CLOSE)
        bind(self, wx.EVT_MOUSEWHEEL, self._onMouseWheel)

    def set_active(self, ind):
        """
        ind is a list of index numbers for the axes which are to be made active
        """
        DEBUG_MSG('set_active()', 1, self)
        self._ind = ind
        if ind != None:
            self._active = [ self._axes[i] for i in self._ind ]
        else:
            self._active = []
        self._menu.updateButtonText(ind)
        return

    def get_last_control(self):
        """Returns the identity of the last toolbar button pressed."""
        return self._lastControl

    def panx(self, direction):
        DEBUG_MSG('panx()', 1, self)
        for a in self._active:
            a.xaxis.pan(direction)

        self.canvas.draw()
        self.canvas.Refresh(eraseBackground=False)

    def pany(self, direction):
        DEBUG_MSG('pany()', 1, self)
        for a in self._active:
            a.yaxis.pan(direction)

        self.canvas.draw()
        self.canvas.Refresh(eraseBackground=False)

    def zoomx(self, in_out):
        DEBUG_MSG('zoomx()', 1, self)
        for a in self._active:
            a.xaxis.zoom(in_out)

        self.canvas.draw()
        self.canvas.Refresh(eraseBackground=False)

    def zoomy(self, in_out):
        DEBUG_MSG('zoomy()', 1, self)
        for a in self._active:
            a.yaxis.zoom(in_out)

        self.canvas.draw()
        self.canvas.Refresh(eraseBackground=False)

    def update(self):
        """
        Update the toolbar menu - called when (e.g.) a new subplot
        or axes are added
        """
        DEBUG_MSG('update()', 1, self)
        self._axes = self.canvas.figure.get_axes()
        self._menu.updateAxes(len(self._axes))

    def _do_nothing(self, d):
        """A NULL event handler - does nothing whatsoever"""
        pass

    def _onEnterTool(self, evt):
        toolId = evt.GetSelection()
        try:
            self.button_fn = self._NTB_BUTTON_HANDLER[toolId]
        except KeyError:
            self.button_fn = self._do_nothing

        evt.Skip()

    def _onLeftScroll(self, evt):
        self.panx(-1)
        evt.Skip()

    def _onRightScroll(self, evt):
        self.panx(1)
        evt.Skip()

    def _onXZoomIn(self, evt):
        self.zoomx(1)
        evt.Skip()

    def _onXZoomOut(self, evt):
        self.zoomx(-1)
        evt.Skip()

    def _onUpScroll(self, evt):
        self.pany(1)
        evt.Skip()

    def _onDownScroll(self, evt):
        self.pany(-1)
        evt.Skip()

    def _onYZoomIn(self, evt):
        self.zoomy(1)
        evt.Skip()

    def _onYZoomOut(self, evt):
        self.zoomy(-1)
        evt.Skip()

    def _onMouseEnterButton(self, button):
        self._mouseOnButton = button

    def _onMouseLeaveButton(self, button):
        if self._mouseOnButton == button:
            self._mouseOnButton = None
        return

    def _onMouseWheel(self, evt):
        if evt.GetWheelRotation() > 0:
            direction = 1
        else:
            direction = -1
        self.button_fn(direction)

    _onSave = NavigationToolbar2Wx.save_figure

    def _onClose(self, evt):
        self.GetParent().Destroy()


class StatusBarWx(wx.StatusBar):
    """
    A status bar is added to _FigureFrame to allow measurements and the
    previously selected scroll function to be displayed as a user
    convenience.
    """

    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusText('None', 1)

    def set_function(self, string):
        self.SetStatusText('%s' % string, 1)


class PrintoutWx(wx.Printout):
    """Simple wrapper around wx Printout class -- all the real work
    here is scaling the matplotlib canvas bitmap to the current
    printer's definition.
    """

    def __init__(self, canvas, width=5.5, margin=0.5, title='matplotlib'):
        wx.Printout.__init__(self, title=title)
        self.canvas = canvas
        self.width = width
        self.margin = margin

    def HasPage(self, page):
        return page == 1

    def GetPageInfo(self):
        return (1, 1, 1, 1)

    def OnPrintPage(self, page):
        self.canvas.draw()
        dc = self.GetDC()
        ppw, pph = self.GetPPIPrinter()
        pgw, pgh = self.GetPageSizePixels()
        dcw, dch = dc.GetSize()
        grw, grh = self.canvas.GetSizeTuple()
        bgcolor = self.canvas.figure.get_facecolor()
        fig_dpi = self.canvas.figure.dpi
        vscale = float(ppw) / fig_dpi
        self.canvas.figure.dpi = ppw
        self.canvas.figure.set_facecolor('#FFFFFF')
        renderer = RendererWx(self.canvas.bitmap, self.canvas.figure.dpi)
        self.canvas.figure.draw(renderer)
        self.canvas.bitmap.SetWidth(int(self.canvas.bitmap.GetWidth() * vscale))
        self.canvas.bitmap.SetHeight(int(self.canvas.bitmap.GetHeight() * vscale))
        self.canvas.draw()
        page_scale = 1.0
        if self.IsPreview():
            page_scale = float(dcw) / pgw
        top_margin = int(self.margin * pph * page_scale)
        left_margin = int(self.margin * ppw * page_scale)
        user_scale = self.width * fig_dpi * page_scale / float(grw)
        dc.SetDeviceOrigin(left_margin, top_margin)
        dc.SetUserScale(user_scale, user_scale)
        try:
            dc.DrawBitmap(self.canvas.bitmap, 0, 0)
        except:
            try:
                dc.DrawBitmap(self.canvas.bitmap, (0, 0))
            except:
                pass

        self.canvas.figure.set_facecolor(bgcolor)
        self.canvas.figure.dpi = fig_dpi
        self.canvas.draw()
        return True


Toolbar = NavigationToolbarWx
FigureManager = FigureManagerWx