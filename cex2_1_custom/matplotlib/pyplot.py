# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\pyplot.pyc
# Compiled at: 2012-11-08 06:38:04
"""
Provides a MATLAB-like plotting framework.

:mod:`~matplotlib.pylab` combines pyplot with numpy into a single namespace.
This is convenient for interactive work, but for programming it
is recommended that the namespaces be kept separate, e.g.::

    import numpy as np
    import matplotlib.pyplot as plt

    x = np.arange(0, 5, 0.1);
    y = np.sin(x)
    plt.plot(x, y)

"""
from __future__ import print_function
import sys, warnings, matplotlib
from matplotlib import _pylab_helpers, interactive
from matplotlib.cbook import dedent, silent_list, is_string_like, is_numlike
from matplotlib import docstring
from matplotlib.figure import Figure, figaspect
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.image import imread as _imread
from matplotlib.image import imsave as _imsave
from matplotlib import rcParams, rcParamsDefault, get_backend
from matplotlib.rcsetup import interactive_bk as _interactive_bk
from matplotlib.artist import getp, get, Artist
from matplotlib.artist import setp as _setp
from matplotlib.axes import Axes, Subplot, _string_to_bool
from matplotlib.projections import PolarAxes
from matplotlib import mlab
from matplotlib.scale import get_scale_docs, get_scale_names
from matplotlib import cm
from matplotlib.cm import get_cmap, register_cmap
import numpy as np
from matplotlib.colors import Normalize, normalize
from matplotlib.lines import Line2D
from matplotlib.text import Text, Annotation
from matplotlib.patches import Polygon, Rectangle, Circle, Arrow
from matplotlib.widgets import SubplotTool, Button, Slider, Widget
from ticker import TickHelper, Formatter, FixedFormatter, NullFormatter, FuncFormatter, FormatStrFormatter, ScalarFormatter, LogFormatter, LogFormatterExponent, LogFormatterMathtext, Locator, IndexLocator, FixedLocator, NullLocator, LinearLocator, LogLocator, AutoLocator, MultipleLocator, MaxNLocator

def _backend_selection():
    """ If rcParams['backend_fallback'] is true, check to see if the
        current backend is compatible with the current running event
        loop, and if not switches to a compatible one.
    """
    backend = rcParams['backend']
    if not rcParams['backend_fallback'] or backend not in _interactive_bk:
        return
    is_agg_backend = rcParams['backend'].endswith('Agg')
    if 'wx' in sys.modules and backend not in ('WX', 'WXAgg'):
        import wx
        if wx.App.IsMainLoopRunning():
            rcParams['backend'] = 'wx' + 'Agg' * is_agg_backend
    elif 'qt' in sys.modules and not backend == 'QtAgg':
        import qt
        if not qt.qApp.startingUp():
            rcParams['backend'] = 'qtAgg'
    elif 'PyQt4.QtCore' in sys.modules and not backend == 'Qt4Agg':
        import PyQt4.QtGui
        if not PyQt4.QtGui.qApp.startingUp():
            rcParams['backend'] = 'qt4Agg'
    elif 'gtk' in sys.modules and backend not in ('GTK', 'GTKAgg', 'GTKCairo'):
        import gobject
        if gobject.MainLoop().is_running():
            rcParams['backend'] = 'gtk' + 'Agg' * is_agg_backend
    elif 'Tkinter' in sys.modules and not backend == 'TkAgg':
        pass


_backend_selection()
from matplotlib.backends import pylab_setup
_backend_mod, new_figure_manager, draw_if_interactive, _show = pylab_setup()

@docstring.copy_dedent(Artist.findobj)
def findobj(o=None, match=None):
    if o is None:
        o = gcf()
    return o.findobj(match)


def switch_backend(newbackend):
    """
    Switch the default backend.  This feature is **experimental**, and
    is only expected to work switching to an image backend.  Eg, if
    you have a bunch of PostScript scripts that you want to run from
    an interactive ipython session, you may want to switch to the PS
    backend before running them to avoid having a bunch of GUI windows
    popup.  If you try to interactively switch from one GUI backend to
    another, you will explode.

    Calling this command will close all open windows.
    """
    global _backend_mod
    global _show
    global draw_if_interactive
    global new_figure_manager
    close('all')
    matplotlib.use(newbackend, warn=False, force=True)
    from matplotlib.backends import pylab_setup
    _backend_mod, new_figure_manager, draw_if_interactive, _show = pylab_setup()


def show(*args, **kw):
    """
    Display a figure.

    When running in ipython with its pylab mode, display all
    figures and return to the ipython prompt.

    In non-interactive mode, display all figures and block until
    the figures have been closed; in interactive mode it has no
    effect unless figures were created prior to a change from
    non-interactive to interactive mode (not recommended).  In
    that case it displays the figures but does not block.

    A single experimental keyword argument, *block*, may be
    set to True or False to override the blocking behavior
    described above.
    """
    _show(*args, **kw)


def isinteractive():
    """
    Return status of interactive mode.
    """
    return matplotlib.is_interactive()


def ioff():
    """Turn interactive mode off."""
    matplotlib.interactive(False)


def ion():
    """Turn interactive mode on."""
    matplotlib.interactive(True)


def pause(interval):
    """
    Pause for *interval* seconds.

    If there is an active figure it will be updated and displayed,
    and the gui event loop will run during the pause.

    If there is no active figure, or if a non-interactive backend
    is in use, this executes time.sleep(interval).

    This can be used for crude animation. For more complex
    animation, see :mod:`matplotlib.animation`.

    This function is experimental; its behavior may be changed
    or extended in a future release.

    """
    backend = rcParams['backend']
    if backend in _interactive_bk:
        figManager = _pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            canvas.draw()
            show(block=False)
            canvas.start_event_loop(interval)
            return
    import time
    time.sleep(interval)
    return


@docstring.copy_dedent(matplotlib.rc)
def rc(*args, **kwargs):
    matplotlib.rc(*args, **kwargs)


@docstring.copy_dedent(matplotlib.rcdefaults)
def rcdefaults():
    matplotlib.rcdefaults()
    draw_if_interactive()


def gci():
    """
    Get the current colorable artist.  Specifically, returns the
    current :class:`~matplotlib.cm.ScalarMappable` instance (image or
    patch collection), or *None* if no images or patch collections
    have been defined.  The commands :func:`~matplotlib.pyplot.imshow`
    and :func:`~matplotlib.pyplot.figimage` create
    :class:`~matplotlib.image.Image` instances, and the commands
    :func:`~matplotlib.pyplot.pcolor` and
    :func:`~matplotlib.pyplot.scatter` create
    :class:`~matplotlib.collections.Collection` instances.  The
    current image is an attribute of the current axes, or the nearest
    earlier axes in the current figure that contains an image.
    """
    return gcf()._gci()


def sci(im):
    """
    Set the current image.  This image will be the target of colormap
    commands like :func:`~matplotlib.pyplot.jet`,
    :func:`~matplotlib.pyplot.hot` or
    :func:`~matplotlib.pyplot.clim`).  The current image is an
    attribute of the current axes.
    """
    gca()._sci(im)


@docstring.copy(_setp)
def setp(*args, **kwargs):
    ret = _setp(*args, **kwargs)
    draw_if_interactive()
    return ret


def figure(num=None, figsize=None, dpi=None, facecolor=None, edgecolor=None, frameon=True, FigureClass=Figure, **kwargs):
    """
    Create a new figure.

    call signature::

      figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')

    Create a new figure and return a :class:`matplotlib.figure.Figure`
    instance.  If *num* = *None*, the figure number will be incremented and
    a new figure will be created.  The returned figure objects have a
    *number* attribute holding this number.

    If *num* is an integer, and ``figure(num)`` already exists, make it
    active and return a reference to it.  If ``figure(num)`` does not exist
    it will be created.  Numbering starts at 1, MATLAB style::

      figure(1)

    The same applies if *num* is a string. In this case *num* will be used
    as an explicit figure label::

      figure("today")

    and in windowed backends, the window title will be set to this figure
    label.

    If you are creating many figures, make sure you explicitly call "close"
    on the figures you are not using, because this will enable pylab
    to properly clean up the memory.

    Optional keyword arguments:

      =========   =======================================================
      Keyword     Description
      =========   =======================================================
      figsize     width x height in inches; defaults to rc figure.figsize
      dpi         resolution; defaults to rc figure.dpi
      facecolor   the background color; defaults to rc figure.facecolor
      edgecolor   the border color; defaults to rc figure.edgecolor
      =========   =======================================================

    rcParams defines the default values, which can be modified in the
    matplotlibrc file

    *FigureClass* is a :class:`~matplotlib.figure.Figure` or derived
    class that will be passed on to :meth:`new_figure_manager` in the
    backends which allows you to hook custom Figure classes into the
    pylab interface.  Additional kwargs will be passed on to your
    figure init function.
    """
    if figsize is None:
        figsize = rcParams['figure.figsize']
    if dpi is None:
        dpi = rcParams['figure.dpi']
    if facecolor is None:
        facecolor = rcParams['figure.facecolor']
    if edgecolor is None:
        edgecolor = rcParams['figure.edgecolor']
    allnums = get_fignums()
    next_num = max(allnums) + 1 if allnums else 1
    figLabel = ''
    if num is None:
        num = next_num
    elif is_string_like(num):
        figLabel = num
        allLabels = get_figlabels()
        if figLabel not in allLabels:
            if figLabel == 'all':
                warnings.warn("close('all') closes all existing figures")
            num = next_num
        else:
            inum = allLabels.index(figLabel)
            num = allnums[inum]
    else:
        num = int(num)
    figManager = _pylab_helpers.Gcf.get_fig_manager(num)
    if figManager is None:
        if get_backend().lower() == 'ps':
            dpi = 72
        figManager = new_figure_manager(num, figsize=figsize, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor, frameon=frameon, FigureClass=FigureClass, **kwargs)
        if figLabel:
            figManager.set_window_title(figLabel)
            figManager.canvas.figure.set_label(figLabel)

        def make_active(event):
            _pylab_helpers.Gcf.set_active(figManager)

        cid = figManager.canvas.mpl_connect('button_press_event', make_active)
        figManager._cidgcf = cid
        _pylab_helpers.Gcf.set_active(figManager)
        figManager.canvas.figure.number = num
    draw_if_interactive()
    return figManager.canvas.figure


def gcf():
    """Return a reference to the current figure."""
    figManager = _pylab_helpers.Gcf.get_active()
    if figManager is not None:
        return figManager.canvas.figure
    else:
        return figure()
        return


fignum_exists = _pylab_helpers.Gcf.has_fignum

def get_fignums():
    """Return a list of existing figure numbers."""
    fignums = _pylab_helpers.Gcf.figs.keys()
    fignums.sort()
    return fignums


def get_figlabels():
    """Return a list of existing figure labels."""
    figManagers = _pylab_helpers.Gcf.get_all_fig_managers()
    figManagers.sort(key=(lambda m: m.num))
    return [ m.canvas.figure.get_label() for m in figManagers ]


def get_current_fig_manager():
    figManager = _pylab_helpers.Gcf.get_active()
    if figManager is None:
        gcf()
        figManager = _pylab_helpers.Gcf.get_active()
    return figManager


@docstring.copy_dedent(FigureCanvasBase.mpl_connect)
def connect(s, func):
    return get_current_fig_manager().canvas.mpl_connect(s, func)


@docstring.copy_dedent(FigureCanvasBase.mpl_disconnect)
def disconnect(cid):
    return get_current_fig_manager().canvas.mpl_disconnect(cid)


def close(*args):
    """
    Close a figure window.

    ``close()`` by itself closes the current figure

    ``close(h)`` where *h* is a :class:`Figure` instance, closes that figure

    ``close(num)`` closes figure number *num*

    ``close(name)`` where *name* is a string, closes figure with that label

    ``close('all')`` closes all the figure windows
    """
    if len(args) == 0:
        figManager = _pylab_helpers.Gcf.get_active()
        if figManager is None:
            return
        _pylab_helpers.Gcf.destroy(figManager.num)
    elif len(args) == 1:
        arg = args[0]
        if arg == 'all':
            _pylab_helpers.Gcf.destroy_all()
        elif isinstance(arg, int):
            _pylab_helpers.Gcf.destroy(arg)
        if is_string_like(arg):
            allLabels = get_figlabels()
            if arg in allLabels:
                num = get_fignums()[allLabels.index(arg)]
                _pylab_helpers.Gcf.destroy(num)
        else:
            if isinstance(arg, Figure):
                _pylab_helpers.Gcf.destroy_fig(arg)
            else:
                raise TypeError('Unrecognized argument type %s to close' % type(arg))
    else:
        raise TypeError('close takes 0 or 1 arguments')
    return


def clf():
    """
    Clear the current figure.
    """
    gcf().clf()
    draw_if_interactive()


def draw():
    """
    Redraw the current figure.

    This is used in interactive mode to update a figure that
    has been altered using one or more plot object method calls;
    it is not needed if figure modification is done entirely
    with pyplot functions, if a sequence of modifications ends
    with a pyplot function, or if matplotlib is in non-interactive
    mode and the sequence of modifications ends with :func:`show` or
    :func:`savefig`.

    A more object-oriented alternative, given any
    :class:`~matplotlib.figure.Figure` instance, :attr:`fig`, that
    was created using a :mod:`~matplotlib.pyplot` function, is::

        fig.canvas.draw()

    """
    get_current_fig_manager().canvas.draw()


@docstring.copy_dedent(Figure.savefig)
def savefig(*args, **kwargs):
    fig = gcf()
    return fig.savefig(*args, **kwargs)


@docstring.copy_dedent(Figure.ginput)
def ginput(*args, **kwargs):
    """
    Blocking call to interact with the figure.

    This will wait for *n* clicks from the user and return a list of the
    coordinates of each click.

    If *timeout* is negative, does not timeout.
    """
    return gcf().ginput(*args, **kwargs)


@docstring.copy_dedent(Figure.waitforbuttonpress)
def waitforbuttonpress(*args, **kwargs):
    """
    Blocking call to interact with the figure.

    This will wait for *n* key or mouse clicks from the user and
    return a list containing True's for keyboard clicks and False's
    for mouse clicks.

    If *timeout* is negative, does not timeout.
    """
    return gcf().waitforbuttonpress(*args, **kwargs)


@docstring.copy_dedent(Figure.text)
def figtext(*args, **kwargs):
    ret = gcf().text(*args, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Figure.suptitle)
def suptitle(*args, **kwargs):
    ret = gcf().suptitle(*args, **kwargs)
    draw_if_interactive()
    return ret


@docstring.Appender('Addition kwargs: hold = [True|False] overrides default hold state', '\n')
@docstring.copy_dedent(Figure.figimage)
def figimage(*args, **kwargs):
    ret = gcf().figimage(*args, **kwargs)
    draw_if_interactive()
    return ret


def figlegend(handles, labels, loc, **kwargs):
    """
    Place a legend in the figure.

    *labels*
      a sequence of strings

    *handles*
      a sequence of :class:`~matplotlib.lines.Line2D` or
      :class:`~matplotlib.patches.Patch` instances

    *loc*
      can be a string or an integer specifying the legend
      location

    A :class:`matplotlib.legend.Legend` instance is returned.

    Example::

      figlegend( (line1, line2, line3),
                 ('label1', 'label2', 'label3'),
                 'upper right' )

    .. seealso::

       :func:`~matplotlib.pyplot.legend`

    """
    l = gcf().legend(handles, labels, loc, **kwargs)
    draw_if_interactive()
    return l


def hold(b=None):
    """
    Set the hold state.  If *b* is None (default), toggle the
    hold state, else set the hold state to boolean value *b*::

      hold()      # toggle hold
      hold(True)  # hold is on
      hold(False) # hold is off

    When *hold* is *True*, subsequent plot commands will be added to
    the current axes.  When *hold* is *False*, the current axes and
    figure will be cleared on the next plot command.
    """
    fig = gcf()
    ax = fig.gca()
    fig.hold(b)
    ax.hold(b)
    b = ax.ishold()
    rc('axes', hold=b)


def ishold():
    """
    Return the hold status of the current axes.
    """
    return gca().ishold()


def over(func, *args, **kwargs):
    """
    Call a function with hold(True).

    Calls::

      func(*args, **kwargs)

    with ``hold(True)`` and then restores the hold state.
    """
    h = ishold()
    hold(True)
    func(*args, **kwargs)
    hold(h)


def axes(*args, **kwargs):
    """
    Add an axes to the figure.

    The axes is added at position *rect* specified by:

    - ``axes()`` by itself creates a default full ``subplot(111)`` window axis.

    - ``axes(rect, axisbg='w')`` where *rect* = [left, bottom, width,
      height] in normalized (0, 1) units.  *axisbg* is the background
      color for the axis, default white.

    - ``axes(h)`` where *h* is an axes instance makes *h* the current
      axis.  An :class:`~matplotlib.axes.Axes` instance is returned.

    =======   ============   ================================================
    kwarg     Accepts        Desctiption
    =======   ============   ================================================
    axisbg    color          the axes background color
    frameon   [True|False]   display the frame?
    sharex    otherax        current axes shares xaxis attribute with otherax
    sharey    otherax        current axes shares yaxis attribute with otherax
    polar     [True|False]   use a polar axes?
    =======   ============   ================================================

    Examples:

    * :file:`examples/pylab_examples/axes_demo.py` places custom axes.
    * :file:`examples/pylab_examples/shared_axis_demo.py` uses
      *sharex* and *sharey*.

    """
    nargs = len(args)
    if len(args) == 0:
        return subplot(111, **kwargs)
    if nargs > 1:
        raise TypeError('Only one non keyword arg to axes allowed')
    arg = args[0]
    if isinstance(arg, Axes):
        a = gcf().sca(arg)
    else:
        rect = arg
        a = gcf().add_axes(rect, **kwargs)
    draw_if_interactive()
    return a


def delaxes(*args):
    """
    Remove an axes from the current figure.  If *ax*
    doesn't exist, an error will be raised.

    ``delaxes()``: delete the current axes
    """
    if not len(args):
        ax = gca()
    else:
        ax = args[0]
    ret = gcf().delaxes(ax)
    draw_if_interactive()
    return ret


def sca(ax):
    """
    Set the current Axes instance to *ax*.

    The current Figure is updated to the parent of *ax*.
    """
    managers = _pylab_helpers.Gcf.get_all_fig_managers()
    for m in managers:
        if ax in m.canvas.figure.axes:
            _pylab_helpers.Gcf.set_active(m)
            m.canvas.figure.sca(ax)
            return

    raise ValueError('Axes instance argument was not found in a figure.')


def gca(**kwargs):
    """
    Return the current axis instance.  This can be used to control
    axis properties either using set or the
    :class:`~matplotlib.axes.Axes` methods, for example, setting the
    xaxis range::

      plot(t,s)
      set(gca(), 'xlim', [0,10])

    or::

      plot(t,s)
      a = gca()
      a.set_xlim([0,10])

    """
    ax = gcf().gca(**kwargs)
    return ax


def subplot(*args, **kwargs):
    """
    Create a new axes (subplot).

    Creating axes with::

      subplot(numRows, numCols, plotNum)

    where *plotNum* = 1 is the first plot number and increasing *plotNums*
    fill rows first.  max(*plotNum*) == *numRows* * *numCols*

    You can leave out the commas if *numRows* <= *numCols* <=
    *plotNum* < 10, as in::

      subplot(211)    # 2 rows, 1 column, first (upper) plot

    ``subplot(111)`` is the default axis.

    New subplots that overlap old will delete the old axes.  If you do
    not want this behavior, use
    :meth:`~matplotlib.figure.Figure.add_subplot` or the
    :func:`~matplotlib.pyplot.axes` command.  Eg.::

      from pylab import *
      plot([1,2,3])  # implicitly creates subplot(111)
      subplot(211)   # overlaps, subplot(111) is killed
      plot(rand(12), rand(12))
      subplot(212, axisbg='y') # creates 2nd subplot with yellow background

    Keyword arguments:

      *axisbg*:
        The background color of the subplot, which can be any valid
        color specifier.  See :mod:`matplotlib.colors` for more
        information.

      *polar*:
        A boolean flag indicating whether the subplot plot should be
        a polar projection.  Defaults to *False*.

      *projection*:
        A string giving the name of a custom projection to be used
        for the subplot. This projection must have been previously
        registered. See :mod:`matplotlib.projections`.

    .. seealso::

        :func:`~matplotlib.pyplot.axes`
            For additional information on :func:`axes` and
            :func:`subplot` keyword arguments.

        :file:`examples/pylab_examples/polar_scatter.py`
            For an example

    **Example:**

    .. plot:: mpl_examples/pylab_examples/subplot_demo.py

    """
    if len(args) >= 3 and isinstance(args[2], bool):
        warnings.warn('The subplot index argument to subplot() appears to be a boolean. Did you intend to use subplots()?')
    fig = gcf()
    a = fig.add_subplot(*args, **kwargs)
    bbox = a.bbox
    byebye = []
    for other in fig.axes:
        if other == a:
            continue
        if bbox.fully_overlaps(other.bbox):
            byebye.append(other)

    for ax in byebye:
        delaxes(ax)

    draw_if_interactive()
    return a


def subplots(nrows=1, ncols=1, sharex=False, sharey=False, squeeze=True, subplot_kw=None, **fig_kw):
    """
    Create a figure with a set of subplots already made.

    This utility wrapper makes it convenient to create common layouts of
    subplots, including the enclosing figure object, in a single call.

    Keyword arguments:

      *nrows* : int
        Number of rows of the subplot grid.  Defaults to 1.

      *ncols* : int
        Number of columns of the subplot grid.  Defaults to 1.

      *sharex* : string or bool
        If *True*, the X axis will be shared amongst all subplots.  If
        *True* and you have multiple rows, the x tick labels on all but
        the last row of plots will have visible set to *False*
        If a string must be one of "row", "col", "all", or "none".
        "all" has the same effect as *True*, "none" has the same effect
        as *False*.
        If "row", each subplot row will share a X axis.
        If "col", each subplot column will share a X axis and the x tick
        labels on all but the last row will have visible set to *False*.

      *sharey* : string or bool
        If *True*, the Y axis will be shared amongst all subplots. If
        *True* and you have multiple columns, the y tick labels on all but
        the first column of plots will have visible set to *False*
        If a string must be one of "row", "col", "all", or "none".
        "all" has the same effect as *True*, "none" has the same effect
        as *False*.
        If "row", each subplot row will share a Y axis.
        If "col", each subplot column will share a Y axis and the y tick
        labels on all but the last row will have visible set to *False*.

      *squeeze* : bool
        If *True*, extra dimensions are squeezed out from the
        returned axis object:

        - if only one subplot is constructed (nrows=ncols=1), the
          resulting single Axis object is returned as a scalar.

        - for Nx1 or 1xN subplots, the returned object is a 1-d numpy
          object array of Axis objects are returned as numpy 1-d
          arrays.

        - for NxM subplots with N>1 and M>1 are returned as a 2d
          array.

        If *False*, no squeezing at all is done: the returned axis
        object is always a 2-d array contaning Axis instances, even if it
        ends up being 1x1.

      *subplot_kw* : dict
        Dict with keywords passed to the
        :meth:`~matplotlib.figure.Figure.add_subplot` call used to
        create each subplots.

      *fig_kw* : dict
        Dict with keywords passed to the :func:`figure` call.  Note that all
        keywords not recognized above will be automatically included here.

    Returns:

    fig, ax : tuple

      - *fig* is the :class:`matplotlib.figure.Figure` object

      - *ax* can be either a single axis object or an array of axis
        objects if more than one subplot was created.  The dimensions
        of the resulting array can be controlled with the squeeze
        keyword, see above.

    Examples::

        x = np.linspace(0, 2*np.pi, 400)
        y = np.sin(x**2)

        # Just a figure and one subplot
        f, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title('Simple plot')

        # Two subplots, unpack the output array immediately
        f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        ax1.plot(x, y)
        ax1.set_title('Sharing Y axis')
        ax2.scatter(x, y)

        # Four polar axes
        plt.subplots(2, 2, subplot_kw=dict(polar=True))

        # Share a X axis with each column of subplots
        plt.subplots(2, 2, sharex='col')

        # Share a Y axis with each row of subplots
        plt.subplots(2, 2, sharey='row')

        # Share a X and Y axis with all subplots
        plt.subplots(2, 2, sharex='all', sharey='all')
        # same as
        plt.subplots(2, 2, sharex=True, sharey=True)
    """
    if isinstance(sharex, bool):
        if sharex:
            sharex = 'all'
        else:
            sharex = 'none'
    if isinstance(sharey, bool):
        if sharey:
            sharey = 'all'
        else:
            sharey = 'none'
    share_values = [
     'all', 'row', 'col', 'none']
    if sharex not in share_values:
        if isinstance(sharex, int):
            warnings.warn("sharex argument to subplots() was an integer. Did you intend to use subplot() (without 's')?")
        raise ValueError('sharex [%s] must be one of %s' % (
         sharex, share_values))
    if sharey not in share_values:
        raise ValueError('sharey [%s] must be one of %s' % (
         sharey, share_values))
    if subplot_kw is None:
        subplot_kw = {}
    fig = figure(**fig_kw)
    nplots = nrows * ncols
    axarr = np.empty(nplots, dtype=object)
    ax0 = fig.add_subplot(nrows, ncols, 1, **subplot_kw)
    axarr[0] = ax0
    r, c = np.mgrid[:nrows, :ncols]
    r = r.flatten() * ncols
    c = c.flatten()
    lookup = {'none': np.arange(nplots), 
       'all': np.zeros(nplots, dtype=int), 
       'row': r, 
       'col': c}
    sxs = lookup[sharex]
    sys = lookup[sharey]
    for i in range(1, nplots):
        if sxs[i] == i:
            subplot_kw['sharex'] = None
        else:
            subplot_kw['sharex'] = axarr[sxs[i]]
        if sys[i] == i:
            subplot_kw['sharey'] = None
        else:
            subplot_kw['sharey'] = axarr[sys[i]]
        axarr[i] = fig.add_subplot(nrows, ncols, (i + 1), **subplot_kw)

    axarr = axarr.reshape(nrows, ncols)
    if sharex in ('col', 'all') and nrows > 1:
        for ax in axarr[:-1, :].flat:
            for label in ax.get_xticklabels():
                label.set_visible(False)

            ax.xaxis.offsetText.set_visible(False)

    if sharey in ('row', 'all') and ncols > 1:
        for ax in axarr[:, 1:].flat:
            for label in ax.get_yticklabels():
                label.set_visible(False)

            ax.yaxis.offsetText.set_visible(False)

    if squeeze:
        if nplots == 1:
            ret = (
             fig, axarr[(0, 0)])
        else:
            ret = (
             fig, axarr.squeeze())
    else:
        ret = (
         fig, axarr.reshape(nrows, ncols))
    return ret


from gridspec import GridSpec

def subplot2grid(shape, loc, rowspan=1, colspan=1, **kwargs):
    """
    Create a subplot in a grid.  The grid is specified by *shape*, at
    location of *loc*, spanning *rowspan*, *colspan* cells in each
    direction.  The index for loc is 0-based. ::

      subplot2grid(shape, loc, rowspan=1, colspan=1)

    is identical to ::

      gridspec=GridSpec(shape[0], shape[2])
      subplotspec=gridspec.new_subplotspec(loc, rowspan, colspan)
      subplot(subplotspec)
    """
    fig = gcf()
    s1, s2 = shape
    subplotspec = GridSpec(s1, s2).new_subplotspec(loc, rowspan=rowspan, colspan=colspan)
    a = fig.add_subplot(subplotspec, **kwargs)
    bbox = a.bbox
    byebye = []
    for other in fig.axes:
        if other == a:
            continue
        if bbox.fully_overlaps(other.bbox):
            byebye.append(other)

    for ax in byebye:
        delaxes(ax)

    draw_if_interactive()
    return a


def twinx(ax=None):
    """
    Make a second axes that shares the *x*-axis.  The new axes will
    overlay *ax* (or the current axes if *ax* is *None*).  The ticks
    for *ax2* will be placed on the right, and the *ax2* instance is
    returned.

    .. seealso::

       :file:`examples/api_examples/two_scales.py`
          For an example
    """
    if ax is None:
        ax = gca()
    ax1 = ax.twinx()
    draw_if_interactive()
    return ax1


def twiny(ax=None):
    """
    Make a second axes that shares the *y*-axis.  The new axis will
    overlay *ax* (or the current axes if *ax* is *None*).  The ticks
    for *ax2* will be placed on the top, and the *ax2* instance is
    returned.
    """
    if ax is None:
        ax = gca()
    ax1 = ax.twiny()
    draw_if_interactive()
    return ax1


def subplots_adjust(*args, **kwargs):
    """
    Tune the subplot layout.

    call signature::

      subplots_adjust(left=None, bottom=None, right=None, top=None,
                      wspace=None, hspace=None)

    The parameter meanings (and suggested defaults) are::

      left  = 0.125  # the left side of the subplots of the figure
      right = 0.9    # the right side of the subplots of the figure
      bottom = 0.1   # the bottom of the subplots of the figure
      top = 0.9      # the top of the subplots of the figure
      wspace = 0.2   # the amount of width reserved for blank space between subplots
      hspace = 0.2   # the amount of height reserved for white space between subplots

    The actual defaults are controlled by the rc file
    """
    fig = gcf()
    fig.subplots_adjust(*args, **kwargs)
    draw_if_interactive()


def subplot_tool(targetfig=None):
    """
    Launch a subplot tool window for a figure.

    A :class:`matplotlib.widgets.SubplotTool` instance is returned.
    """
    tbar = rcParams['toolbar']
    rcParams['toolbar'] = 'None'
    if targetfig is None:
        manager = get_current_fig_manager()
        targetfig = manager.canvas.figure
    else:
        for manager in _pylab_helpers.Gcf._activeQue:
            if manager.canvas.figure == targetfig:
                break
        else:
            raise RuntimeError('Could not find manager for targetfig')

    toolfig = figure(figsize=(6, 3))
    toolfig.subplots_adjust(top=0.9)
    ret = SubplotTool(targetfig, toolfig)
    rcParams['toolbar'] = tbar
    _pylab_helpers.Gcf.set_active(manager)
    return ret


def tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None):
    """
    Automatically adjust subplot parameters to give specified padding.

    Parameters:

    pad : float
        padding between the figure edge and the edges of subplots, as a fraction of the font-size.
    h_pad, w_pad : float
        padding (height/width) between edges of adjacent subplots.
        Defaults to `pad_inches`.
    rect : if rect is given, it is interpreted as a rectangle
        (left, bottom, right, top) in the normalized figure
        coordinate that the whole subplots area (including
        labels) will fit into. Default is (0, 0, 1, 1).
    """
    fig = gcf()
    fig.tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)
    draw_if_interactive()


def box(on=None):
    """
    Turn the axes box on or off.  *on* may be a boolean or a string,
    'on' or 'off'.

    If *on* is *None*, toggle state.
    """
    ax = gca()
    on = _string_to_bool(on)
    if on is None:
        on = not ax.get_frame_on()
    ax.set_frame_on(on)
    draw_if_interactive()
    return


def title(s, *args, **kwargs):
    """
    Set the title of the current axis.

    Default font override is::

      override = {'fontsize': 'medium',
                  'verticalalignment': 'baseline',
                  'horizontalalignment': 'center'}

    .. seealso::

       :func:`~matplotlib.pyplot.text`
           for information on how override and the optional args work.
    """
    l = gca().set_title(s, *args, **kwargs)
    draw_if_interactive()
    return l


def axis(*v, **kwargs):
    """
    Set or get the axis properties.::

      >>> axis()

    returns the current axes limits ``[xmin, xmax, ymin, ymax]``.::

      >>> axis(v)

    sets the min and max of the x and y axes, with
    ``v = [xmin, xmax, ymin, ymax]``.::

      >>> axis('off')

    turns off the axis lines and labels.::

      >>> axis('equal')

    changes limits of *x* or *y* axis so that equal increments of *x*
    and *y* have the same length; a circle is circular.::

      >>> axis('scaled')

    achieves the same result by changing the dimensions of the plot box instead
    of the axis data limits.::

      >>> axis('tight')

    changes *x* and *y* axis limits such that all data is shown. If
    all data is already shown, it will move it to the center of the
    figure without modifying (*xmax* - *xmin*) or (*ymax* -
    *ymin*). Note this is slightly different than in MATLAB.::

      >>> axis('image')

    is 'scaled' with the axis limits equal to the data limits.::

      >>> axis('auto')

    and::

      >>> axis('normal')

    are deprecated. They restore default behavior; axis limits are automatically
    scaled to make the data fit comfortably within the plot box.

    if ``len(*v)==0``, you can pass in *xmin*, *xmax*, *ymin*, *ymax*
    as kwargs selectively to alter just those limits without changing
    the others.

    The xmin, xmax, ymin, ymax tuple is returned

    .. seealso::

        :func:`xlim`, :func:`ylim`
           For setting the x- and y-limits individually.
    """
    ax = gca()
    v = ax.axis(*v, **kwargs)
    draw_if_interactive()
    return v


def xlabel(s, *args, **kwargs):
    """
    Set the *x* axis label of the current axis.

    Default override is::

      override = {
          'fontsize'            : 'small',
          'verticalalignment'   : 'top',
          'horizontalalignment' : 'center'
          }

    .. seealso::

        :func:`~matplotlib.pyplot.text`
            For information on how override and the optional args work
    """
    l = gca().set_xlabel(s, *args, **kwargs)
    draw_if_interactive()
    return l


def ylabel(s, *args, **kwargs):
    """
    Set the *y* axis label of the current axis.

    Defaults override is::

        override = {
           'fontsize'            : 'small',
           'verticalalignment'   : 'center',
           'horizontalalignment' : 'right',
           'rotation'='vertical' : }

    .. seealso::

        :func:`~matplotlib.pyplot.text`
            For information on how override and the optional args
            work.
    """
    l = gca().set_ylabel(s, *args, **kwargs)
    draw_if_interactive()
    return l


def xlim(*args, **kwargs):
    """
    Get or set the *x* limits of the current axes.

    ::

      xmin, xmax = xlim()   # return the current xlim
      xlim( (xmin, xmax) )  # set the xlim to xmin, xmax
      xlim( xmin, xmax )    # set the xlim to xmin, xmax

    If you do not specify args, you can pass the xmin and xmax as
    kwargs, eg.::

      xlim(xmax=3) # adjust the max leaving min unchanged
      xlim(xmin=1) # adjust the min leaving max unchanged

    Setting limits turns autoscaling off for the x-axis.

    The new axis limits are returned as a length 2 tuple.

    """
    ax = gca()
    if not args and not kwargs:
        return ax.get_xlim()
    ret = ax.set_xlim(*args, **kwargs)
    draw_if_interactive()
    return ret


def ylim(*args, **kwargs):
    """
    Get or set the *y*-limits of the current axes.

    ::

      ymin, ymax = ylim()   # return the current ylim
      ylim( (ymin, ymax) )  # set the ylim to ymin, ymax
      ylim( ymin, ymax )    # set the ylim to ymin, ymax

    If you do not specify args, you can pass the *ymin* and *ymax* as
    kwargs, eg.::

      ylim(ymax=3) # adjust the max leaving min unchanged
      ylim(ymin=1) # adjust the min leaving max unchanged

    Setting limits turns autoscaling off for the y-axis.

    The new axis limits are returned as a length 2 tuple.
    """
    ax = gca()
    if not args and not kwargs:
        return ax.get_ylim()
    ret = ax.set_ylim(*args, **kwargs)
    draw_if_interactive()
    return ret


@docstring.dedent_interpd
def xscale(*args, **kwargs):
    """
    Set the scaling of the *x*-axis.

    call signature::

      xscale(scale, **kwargs)

    The available scales are: %(scale)s

    Different keywords may be accepted, depending on the scale:

    %(scale_docs)s
    """
    ax = gca()
    ax.set_xscale(*args, **kwargs)
    draw_if_interactive()


@docstring.dedent_interpd
def yscale(*args, **kwargs):
    """
    Set the scaling of the *y*-axis.

    call signature::

      yscale(scale, **kwargs)

    The available scales are: %(scale)s

    Different keywords may be accepted, depending on the scale:

    %(scale_docs)s
    """
    ax = gca()
    ax.set_yscale(*args, **kwargs)
    draw_if_interactive()


def xticks(*args, **kwargs):
    """
    Get or set the *x*-limits of the current tick locations and labels.

    ::

      # return locs, labels where locs is an array of tick locations and
      # labels is an array of tick labels.
      locs, labels = xticks()

      # set the locations of the xticks
      xticks( arange(6) )

      # set the locations and labels of the xticks
      xticks( arange(5), ('Tom', 'Dick', 'Harry', 'Sally', 'Sue') )

    The keyword args, if any, are :class:`~matplotlib.text.Text`
    properties. For example, to rotate long labels::

      xticks( arange(12), calendar.month_name[1:13], rotation=17 )
    """
    ax = gca()
    if len(args) == 0:
        locs = ax.get_xticks()
        labels = ax.get_xticklabels()
    elif len(args) == 1:
        locs = ax.set_xticks(args[0])
        labels = ax.get_xticklabels()
    elif len(args) == 2:
        locs = ax.set_xticks(args[0])
        labels = ax.set_xticklabels(args[1], **kwargs)
    else:
        raise TypeError('Illegal number of arguments to xticks')
    if len(kwargs):
        for l in labels:
            l.update(kwargs)

    draw_if_interactive()
    return (locs, silent_list('Text xticklabel', labels))


def yticks(*args, **kwargs):
    """
    Get or set the *y*-limits of the current tick locations and labels.

    ::

      # return locs, labels where locs is an array of tick locations and
      # labels is an array of tick labels.
      locs, labels = yticks()

      # set the locations of the yticks
      yticks( arange(6) )

      # set the locations and labels of the yticks
      yticks( arange(5), ('Tom', 'Dick', 'Harry', 'Sally', 'Sue') )

    The keyword args, if any, are :class:`~matplotlib.text.Text`
    properties. For example, to rotate long labels::

      yticks( arange(12), calendar.month_name[1:13], rotation=45 )
    """
    ax = gca()
    if len(args) == 0:
        locs = ax.get_yticks()
        labels = ax.get_yticklabels()
    elif len(args) == 1:
        locs = ax.set_yticks(args[0])
        labels = ax.get_yticklabels()
    elif len(args) == 2:
        locs = ax.set_yticks(args[0])
        labels = ax.set_yticklabels(args[1], **kwargs)
    else:
        raise TypeError('Illegal number of arguments to yticks')
    if len(kwargs):
        for l in labels:
            l.update(kwargs)

    draw_if_interactive()
    return (
     locs,
     silent_list('Text yticklabel', labels))


def minorticks_on():
    """
    Display minor ticks on the current plot.

    Displaying minor ticks reduces performance; turn them off using
    minorticks_off() if drawing speed is a problem.
    """
    gca().minorticks_on()
    draw_if_interactive()


def minorticks_off():
    """
    Remove minor ticks from the current plot.
    """
    gca().minorticks_off()
    draw_if_interactive()


def rgrids(*args, **kwargs):
    """
    Get or set the radial gridlines on a polar plot.

    call signatures::

      lines, labels = rgrids()
      lines, labels = rgrids(radii, labels=None, angle=22.5, **kwargs)

    When called with no arguments, :func:`rgrid` simply returns the
    tuple (*lines*, *labels*), where *lines* is an array of radial
    gridlines (:class:`~matplotlib.lines.Line2D` instances) and
    *labels* is an array of tick labels
    (:class:`~matplotlib.text.Text` instances). When called with
    arguments, the labels will appear at the specified radial
    distances and angles.

    *labels*, if not *None*, is a len(*radii*) list of strings of the
    labels to use at each angle.

    If *labels* is None, the rformatter will be used

    Examples::

      # set the locations of the radial gridlines and labels
      lines, labels = rgrids( (0.25, 0.5, 1.0) )

      # set the locations and labels of the radial gridlines and labels
      lines, labels = rgrids( (0.25, 0.5, 1.0), ('Tom', 'Dick', 'Harry' )

    """
    ax = gca()
    if not isinstance(ax, PolarAxes):
        raise RuntimeError('rgrids only defined for polar axes')
    if len(args) == 0:
        lines = ax.yaxis.get_gridlines()
        labels = ax.yaxis.get_ticklabels()
    else:
        lines, labels = ax.set_rgrids(*args, **kwargs)
    draw_if_interactive()
    return (silent_list('Line2D rgridline', lines),
     silent_list('Text rgridlabel', labels))


def thetagrids(*args, **kwargs):
    """
    Get or set the theta locations of the gridlines in a polar plot.

    If no arguments are passed, return a tuple (*lines*, *labels*)
    where *lines* is an array of radial gridlines
    (:class:`~matplotlib.lines.Line2D` instances) and *labels* is an
    array of tick labels (:class:`~matplotlib.text.Text` instances)::

      lines, labels = thetagrids()

    Otherwise the syntax is::

      lines, labels = thetagrids(angles, labels=None, fmt='%d', frac = 1.1)

    set the angles at which to place the theta grids (these gridlines
    are equal along the theta dimension).

    *angles* is in degrees.

    *labels*, if not *None*, is a len(angles) list of strings of the
    labels to use at each angle.

    If *labels* is *None*, the labels will be ``fmt%angle``.

    *frac* is the fraction of the polar axes radius at which to place
    the label (1 is the edge). Eg. 1.05 is outside the axes and 0.95
    is inside the axes.

    Return value is a list of tuples (*lines*, *labels*):

      - *lines* are :class:`~matplotlib.lines.Line2D` instances

      - *labels* are :class:`~matplotlib.text.Text` instances.

    Note that on input, the *labels* argument is a list of strings,
    and on output it is a list of :class:`~matplotlib.text.Text`
    instances.

    Examples::

      # set the locations of the radial gridlines and labels
      lines, labels = thetagrids( range(45,360,90) )

      # set the locations and labels of the radial gridlines and labels
      lines, labels = thetagrids( range(45,360,90), ('NE', 'NW', 'SW','SE') )
    """
    ax = gca()
    if not isinstance(ax, PolarAxes):
        raise RuntimeError('rgrids only defined for polar axes')
    if len(args) == 0:
        lines = ax.xaxis.get_ticklines()
        labels = ax.xaxis.get_ticklabels()
    else:
        lines, labels = ax.set_thetagrids(*args, **kwargs)
    draw_if_interactive()
    return (silent_list('Line2D thetagridline', lines),
     silent_list('Text thetagridlabel', labels))


def plotting():
    pass


def get_plot_commands():
    """
    Get a sorted list of all of the plotting commands.
    """
    import inspect
    exclude = set(['colormaps', 'colors', 'connect', 'disconnect', 
     'get_plot_commands', 
     'get_current_fig_manager', 
     'ginput', 'plotting', 'waitforbuttonpress'])
    exclude |= set(colormaps())
    this_module = inspect.getmodule(get_plot_commands)
    commands = set()
    for name, obj in globals().items():
        if name.startswith('_') or name in exclude:
            continue
        if inspect.isfunction(obj) and inspect.getmodule(obj) is this_module:
            commands.add(name)

    commands = list(commands)
    commands.sort()
    return commands


def colors():
    """
    This is a do-nothing function to provide you with help on how
    matplotlib handles colors.

    Commands which take color arguments can use several formats to
    specify the colors.  For the basic builtin colors, you can use a
    single letter

      =====   =======
      Alias   Color
      =====   =======
      'b'     blue
      'g'     green
      'r'     red
      'c'     cyan
      'm'     magenta
      'y'     yellow
      'k'     black
      'w'     white
      =====   =======

    For a greater range of colors, you have two options.  You can
    specify the color using an html hex string, as in::

      color = '#eeefff'

    or you can pass an R,G,B tuple, where each of R,G,B are in the
    range [0,1].

    You can also use any legal html name for a color, for example::

      color = 'red'
      color = 'burlywood'
      color = 'chartreuse'

    The example below creates a subplot with a dark
    slate gray background::

       subplot(111, axisbg=(0.1843, 0.3098, 0.3098))

    Here is an example that creates a pale turqoise title::

      title('Is this the best color?', color='#afeeee')

    """
    pass


def colormaps():
    """
    Matplotlib provides a number of colormaps, and others can be added using
    :func:`register_cmap`.  This function documents the built-in colormaps,
    and will also return a list of all registered colormaps if called.

    You can set the colormap for an image, pcolor, scatter, etc,
    using a keyword argument::

      imshow(X, cmap=cm.hot)

    or using the :func:`set_cmap` function::

      imshow(X)
      pyplot.set_cmap('hot')
      pyplot.set_cmap('jet')

    In interactive mode, :func:`set_cmap` will update the colormap post-hoc,
    allowing you to see which one works best for your data.

    All built-in colormaps can be reversed by appending ``_r``: For instance,
    ``gray_r`` is the reverse of ``gray``.

    There are several common color schemes used in visualization:

    Sequential schemes
      for unipolar data that progresses from low to high
    Diverging schemes
      for bipolar data that emphasizes positive or negative deviations from a
      central value
    Cyclic schemes
      meant for plotting values that wrap around at the
      endpoints, such as phase angle, wind direction, or time of day
    Qualitative schemes
      for nominal data that has no inherent ordering, where color is used
      only to distinguish categories

    The base colormaps are (with the exception of `spectral`) derived from
    those of the same name provided with Matlab:

      =========   =======================================================
      Colormap    Description
      =========   =======================================================
      autumn      sequential linearly-increasing shades of red-orange-yellow
      bone        sequential increasing black-white color map with
                  a tinge of blue, to emulate X-ray film
      cool        linearly-decreasing shades of cyan-magenta
      copper      sequential increasing shades of black-copper
      flag        repetitive red-white-blue-black pattern (not cyclic at
                  endpoints)
      gray        sequential linearly-increasing black-to-white
                  grayscale
      hot         sequential black-red-yellow-white, to emulate blackbody
                  radiation from an object at increasing temperatures
      hsv         cyclic red-yellow-green-cyan-blue-magenta-red, formed
                  by changing the hue component in the HSV color space
      jet         a spectral map with dark endpoints, blue-cyan-yellow-red;
                  based on a fluid-jet simulation by NCSA [#]_
      pink        sequential increasing pastel black-pink-white, meant
                  for sepia tone colorization of photographs
      prism       repetitive red-yellow-green-blue-purple-...-green pattern
                  (not cyclic at endpoints)
      spring      linearly-increasing shades of magenta-yellow
      summer      sequential linearly-increasing shades of green-yellow
      winter      linearly-increasing shades of blue-green
      spectral    black-purple-blue-green-yellow-red-white spectrum
      =========   =======================================================

    For the above list only, you can also set the colormap using the
    corresponding pylab shortcut interface function, similar to Matlab::

      imshow(X)
      hot()
      jet()

    The next set of palettes are from the `Yorick scientific visualisation
    package <http://yorick.sourceforge.net/index.php>`_, an evolution of
    the GIST package, both by David H. Munro:

      ============  =======================================================
      Colormap      Description
      ============  =======================================================
      gist_earth    mapmaker's colors from dark blue deep ocean to green
                    lowlands to brown highlands to white mountains
      gist_heat     sequential increasing black-red-orange-white, to emulate
                    blackbody radiation from an iron bar as it grows hotter
      gist_ncar     pseudo-spectral black-blue-green-yellow-red-purple-white
                    colormap from National Center for Atmospheric
                    Research [#]_
      gist_rainbow  runs through the colors in spectral order from red to
                    violet at full saturation (like *hsv* but not cyclic)
      gist_stern    "Stern special" color table from Interactive Data
                    Language software
      ============  =======================================================

    The following colormaps are based on the `ColorBrewer
    <http://colorbrewer.org>`_ color specifications and designs developed by
    Cynthia Brewer:

    ColorBrewer Diverging (luminance is highest at the midpoint, and
    decreases towards differently-colored endpoints):

      ========  ===================================
      Colormap  Description
      ========  ===================================
      BrBG      brown, white, blue-green
      PiYG      pink, white, yellow-green
      PRGn      purple, white, green
      PuOr      orange, white, purple
      RdBu      red, white, blue
      RdGy      red, white, gray
      RdYlBu    red, yellow, blue
      RdYlGn    red, yellow, green
      Spectral  red, orange, yellow, green, blue
      ========  ===================================

    ColorBrewer Sequential (luminance decreases monotonically):

      ========  ====================================
      Colormap  Description
      ========  ====================================
      Blues     white to dark blue
      BuGn      white, light blue, dark green
      BuPu      white, light blue, dark purple
      GnBu      white, light green, dark blue
      Greens    white to dark green
      Greys     white to black (not linear)
      Oranges   white, orange, dark brown
      OrRd      white, orange, dark red
      PuBu      white, light purple, dark blue
      PuBuGn    white, light purple, dark green
      PuRd      white, light purple, dark red
      Purples   white to dark purple
      RdPu      white, pink, dark purple
      Reds      white to dark red
      YlGn      light yellow, dark green
      YlGnBu    light yellow, light green, dark blue
      YlOrBr    light yellow, orange, dark brown
      YlOrRd    light yellow, orange, dark red
      ========  ====================================

    ColorBrewer Qualitative:

    (For plotting nominal data, :class:`ListedColormap` should be used,
    not :class:`LinearSegmentedColormap`.  Different sets of colors are
    recommended for different numbers of categories.  These continuous
    versions of the qualitative schemes may be removed or converted in the
    future.)

    * Accent
    * Dark2
    * Paired
    * Pastel1
    * Pastel2
    * Set1
    * Set2
    * Set3

    Other miscellaneous schemes:

      =========  =======================================================
      Colormap   Description
      =========  =======================================================
      afmhot     sequential black-orange-yellow-white blackbody
                 spectrum, commonly used in atomic force microscopy
      brg        blue-red-green
      bwr        diverging blue-white-red
      coolwarm   diverging blue-gray-red, meant to avoid issues with 3D
                 shading, color blindness, and ordering of colors [#]_
      CMRmap     "Default colormaps on color images often reproduce to
                 confusing grayscale images. The proposed colormap
                 maintains an aesthetically pleasing color image that
                 automatically reproduces to a monotonic grayscale with
                 discrete, quantifiable saturation levels." [#]_
      cubehelix  Unlike most other color schemes cubehelix was designed
                 by D.A. Green to be monotonically increasing in terms
                 of perceived brightness. Also, when printed on a black
                 and white postscript printer, the scheme results in a
                 greyscale with monotonically increasing brightness.
                 This color scheme is named cubehelix because the r,g,b
                 values produced can be visualised as a squashed helix
                 around the diagonal in the r,g,b color cube.
      gnuplot    gnuplot's traditional pm3d scheme
                 (black-blue-red-yellow)
      gnuplot2   sequential color printable as gray
                 (black-blue-violet-yellow-white)
      ocean      green-blue-white
      rainbow    spectral purple-blue-green-yellow-orange-red colormap
                 with diverging luminance
      seismic    diverging blue-white-red
      terrain    mapmaker's colors, blue-green-yellow-brown-white,
                 originally from IGOR Pro
      =========  =======================================================

    The following colormaps are redundant and may be removed in future
    versions.  It's recommended to use *gray* or *gray_r* instead, which
    produce identical output:

      =========  =======================================================
      Colormap   Description
      =========  =======================================================
      gist_gray  identical to *gray*
      gist_yarg  identical to *gray_r*
      binary     identical to *gray_r*
      =========  =======================================================

    .. rubric:: Footnotes

    .. [#] Rainbow colormaps, ``jet`` in particular, are considered a poor
      choice for scientific visualization by many researchers: `Rainbow Color
      Map (Still) Considered Harmful
      <http://www.jwave.vt.edu/%7Erkriz/Projects/create_color_table/color_07.pdf>`_

    .. [#] Resembles "BkBlAqGrYeOrReViWh200" from NCAR Command
      Language. See `Color Table Gallery
      <http://www.ncl.ucar.edu/Document/Graphics/color_table_gallery.shtml>`_

    .. [#] See `Diverging Color Maps for Scientific Visualization
      <http://www.cs.unm.edu/~kmorel/documents/ColorMaps/>`_ by Kenneth
      Moreland.

    .. [#] See `A Color Map for Effective Black-and-White Rendering of
      Color-Scale Images
      <http://www.mathworks.com/matlabcentral/fileexchange/2662-cmrmap-m>`_
      by Carey Rappaport

    """
    return sorted(cm.cmap_d.keys())


def _setup_pyplot_info_docstrings():
    """
    Generates the plotting and docstring.

    These must be done after the entire module is imported, so it is
    called from the end of this module, which is generated by
    boilerplate.py.
    """
    import re

    def pad(s, l):
        """Pad string *s* to length *l*."""
        if l < len(s):
            return s[:l]
        return s + ' ' * (l - len(s))

    commands = get_plot_commands()
    first_sentence = re.compile('(?:\\s*).+?\\.(?:\\s+|$)', flags=re.DOTALL)
    rows = []
    max_name = 0
    max_summary = 0
    for name in commands:
        doc = globals()[name].__doc__
        summary = ''
        if doc is not None:
            match = first_sentence.match(doc)
            if match is not None:
                summary = match.group(0).strip().replace('\n', ' ')
        name = '`%s`' % name
        rows.append([name, summary])
        max_name = max(max_name, len(name))
        max_summary = max(max_summary, len(summary))

    lines = []
    sep = '=' * max_name + ' ' + '=' * max_summary
    lines.append(sep)
    lines.append((' ').join([pad('Function', max_name),
     pad('Description', max_summary)]))
    lines.append(sep)
    for name, summary in rows:
        lines.append((' ').join([pad(name, max_name),
         pad(summary, max_summary)]))

    lines.append(sep)
    plotting.__doc__ = ('\n').join(lines)
    return


import matplotlib.colorbar

def colorbar(mappable=None, cax=None, ax=None, **kw):
    if mappable is None:
        mappable = gci()
        if mappable is None:
            raise RuntimeError('No mappable was found to use for colorbar creation. First define a mappable such as an image (with imshow) or a contour set (with contourf).')
    if ax is None:
        ax = gca()
    ret = gcf().colorbar(mappable, cax=cax, ax=ax, **kw)
    draw_if_interactive()
    return ret


colorbar.__doc__ = matplotlib.colorbar.colorbar_doc

def clim(vmin=None, vmax=None):
    """
    Set the color limits of the current image.

    To apply clim to all axes images do::

      clim(0, 0.5)

    If either *vmin* or *vmax* is None, the image min/max respectively
    will be used for color scaling.

    If you want to set the clim of multiple images,
    use, for example::

      for im in gca().get_images():
          im.set_clim(0, 0.05)

    """
    im = gci()
    if im is None:
        raise RuntimeError('You must first define an image, eg with imshow')
    im.set_clim(vmin, vmax)
    draw_if_interactive()
    return


def set_cmap(cmap):
    """
    Set the default colormap.  Applies to the current image if any.
    See help(colormaps) for more information.

    *cmap* must be a :class:`colors.Colormap` instance, or
    the name of a registered colormap.

    See :func:`register_cmap` and :func:`get_cmap`.
    """
    cmap = cm.get_cmap(cmap)
    rc('image', cmap=cmap.name)
    im = gci()
    if im is not None:
        im.set_cmap(cmap)
    else:
        raise RuntimeError('You must first define an image, eg with imshow')
    draw_if_interactive()
    return


@docstring.copy_dedent(_imread)
def imread(*args, **kwargs):
    return _imread(*args, **kwargs)


@docstring.copy_dedent(_imsave)
def imsave(*args, **kwargs):
    return _imsave(*args, **kwargs)


def matshow(A, fignum=None, **kw):
    """
    Display an array as a matrix in a new figure window.

    The origin is set at the upper left hand corner and rows (first
    dimension of the array) are displayed horizontally.  The aspect
    ratio of the figure window is that of the array, unless this would
    make an excessively short or narrow figure.

    Tick labels for the xaxis are placed on top.

    With the exception of *fignum*, keyword arguments are passed to
    :func:`~matplotlib.pyplot.imshow`.  You may set the *origin*
    kwarg to "lower" if you want the first row in the array to be
    at the bottom instead of the top.

    *fignum*: [ None | integer | False ]
      By default, :func:`matshow` creates a new figure window with
      automatic numbering.  If *fignum* is given as an integer, the
      created figure will use this figure number.  Because of how
      :func:`matshow` tries to set the figure aspect ratio to be the
      one of the array, if you provide the number of an already
      existing figure, strange things may happen.

      If *fignum* is *False* or 0, a new figure window will **NOT** be created.
    """
    A = np.asanyarray(A)
    if fignum is False or fignum is 0:
        ax = gca()
    else:
        fig = figure(fignum, figsize=figaspect(A))
        ax = fig.add_axes([0.15, 0.09, 0.775, 0.775])
    im = ax.matshow(A, **kw)
    sci(im)
    draw_if_interactive()
    return im


def polar(*args, **kwargs):
    """
    Make a polar plot.

    call signature::

      polar(theta, r, **kwargs)

    Multiple *theta*, *r* arguments are supported, with format
    strings, as in :func:`~matplotlib.pyplot.plot`.

    """
    ax = gca(polar=True)
    ret = ax.plot(*args, **kwargs)
    draw_if_interactive()
    return ret


def plotfile(fname, cols=(0, ), plotfuncs=None, comments='#', skiprows=0, checkrows=5, delimiter=',', names=None, subplots=True, newfig=True, **kwargs):
    """
    Plot the data in in a file.

    *cols* is a sequence of column identifiers to plot.  An identifier
    is either an int or a string.  If it is an int, it indicates the
    column number.  If it is a string, it indicates the column header.
    matplotlib will make column headers lower case, replace spaces with
    underscores, and remove all illegal characters; so ``'Adj Close*'``
    will have name ``'adj_close'``.

    - If len(*cols*) == 1, only that column will be plotted on the *y* axis.

    - If len(*cols*) > 1, the first element will be an identifier for
      data for the *x* axis and the remaining elements will be the
      column indexes for multiple subplots if *subplots* is *True*
      (the default), or for lines in a single subplot if *subplots*
      is *False*.

    *plotfuncs*, if not *None*, is a dictionary mapping identifier to
    an :class:`~matplotlib.axes.Axes` plotting function as a string.
    Default is 'plot', other choices are 'semilogy', 'fill', 'bar',
    etc.  You must use the same type of identifier in the *cols*
    vector as you use in the *plotfuncs* dictionary, eg., integer
    column numbers in both or column names in both. If *subplots*
    is *False*, then including any function such as 'semilogy'
    that changes the axis scaling will set the scaling for all
    columns.

    *comments*, *skiprows*, *checkrows*, *delimiter*, and *names*
    are all passed on to :func:`matplotlib.pylab.csv2rec` to
    load the data into a record array.

    If *newfig* is *True*, the plot always will be made in a new figure;
    if *False*, it will be made in the current figure if one exists,
    else in a new figure.

    kwargs are passed on to plotting functions.

    Example usage::

      # plot the 2nd and 4th column against the 1st in two subplots
      plotfile(fname, (0,1,3))

      # plot using column names; specify an alternate plot type for volume
      plotfile(fname, ('date', 'volume', 'adj_close'),
                                    plotfuncs={'volume': 'semilogy'})

    Note: plotfile is intended as a convenience for quickly plotting
    data from flat files; it is not intended as an alternative
    interface to general plotting with pyplot or matplotlib.
    """
    if newfig:
        fig = figure()
    else:
        fig = gcf()
    if len(cols) < 1:
        raise ValueError('must have at least one column of data')
    if plotfuncs is None:
        plotfuncs = dict()
    r = mlab.csv2rec(fname, comments=comments, skiprows=skiprows, checkrows=checkrows, delimiter=delimiter, names=names)

    def getname_val(identifier):
        """return the name and column data for identifier"""
        if is_string_like(identifier):
            return (identifier, r[identifier])
        if is_numlike(identifier):
            name = r.dtype.names[int(identifier)]
            return (
             name, r[name])
        raise TypeError('identifier must be a string or integer')

    xname, x = getname_val(cols[0])
    ynamelist = []
    if len(cols) == 1:
        ax1 = fig.add_subplot(1, 1, 1)
        funcname = plotfuncs.get(cols[0], 'plot')
        func = getattr(ax1, funcname)
        func(x, **kwargs)
        ax1.set_ylabel(xname)
    else:
        N = len(cols)
        for i in range(1, N):
            if subplots:
                if i == 1:
                    ax = ax1 = fig.add_subplot(N - 1, 1, i)
                else:
                    ax = fig.add_subplot(N - 1, 1, i, sharex=ax1)
            elif i == 1:
                ax = fig.add_subplot(1, 1, 1)
            ax.grid(True)
            yname, y = getname_val(cols[i])
            ynamelist.append(yname)
            funcname = plotfuncs.get(cols[i], 'plot')
            func = getattr(ax, funcname)
            func(x, y, **kwargs)
            if subplots:
                ax.set_ylabel(yname)
            if ax.is_last_row():
                ax.set_xlabel(xname)
            else:
                ax.set_xlabel('')

    if not subplots:
        ax.legend(ynamelist, loc='best')
    if xname == 'date':
        fig.autofmt_xdate()
    draw_if_interactive()
    return


def _autogen_docstring(base):
    """Autogenerated wrappers will get their docstring from a base function
    with an addendum."""
    msg = '\n\nAdditional kwargs: hold = [True|False] overrides default hold state'
    addendum = docstring.Appender(msg, '\n\n')
    return (lambda func: addendum(docstring.copy_dedent(base)(func)))


@_autogen_docstring(Axes.spy)
def spy(Z, precision=0, marker=None, markersize=None, aspect='equal', hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.spy(Z, precision, marker, markersize, aspect, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    if isinstance(ret, cm.ScalarMappable):
        sci(ret)
    return ret


@_autogen_docstring(Axes.acorr)
def acorr(x, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.acorr(x, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.arrow)
def arrow(x, y, dx, dy, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.arrow(x, y, dx, dy, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.axhline)
def axhline(y=0, xmin=0, xmax=1, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.axhline(y=y, xmin=xmin, xmax=xmax, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.axhspan)
def axhspan(ymin, ymax, xmin=0, xmax=1, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.axhspan(ymin, ymax, xmin=xmin, xmax=xmax, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.axvline)
def axvline(x=0, ymin=0, ymax=1, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.axvline(x=x, ymin=ymin, ymax=ymax, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.axvspan)
def axvspan(xmin, xmax, ymin=0, ymax=1, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.axvspan(xmin, xmax, ymin=ymin, ymax=ymax, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.bar)
def bar(left, height, width=0.8, bottom=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.bar(left, height, width=width, bottom=bottom, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.barh)
def barh(bottom, width, height=0.8, left=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.barh(bottom, width, height=height, left=left, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.broken_barh)
def broken_barh(xranges, yrange, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.broken_barh(xranges, yrange, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.boxplot)
def boxplot(x, notch=False, sym='b+', vert=True, whis=1.5, positions=None, widths=None, patch_artist=False, bootstrap=None, usermedians=None, conf_intervals=None, hold=None):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.boxplot(x, notch=notch, sym=sym, vert=vert, whis=whis, positions=positions, widths=widths, patch_artist=patch_artist, bootstrap=bootstrap, usermedians=usermedians, conf_intervals=conf_intervals)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.cohere)
def cohere(x, y, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.cohere(x, y, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend, window=window, noverlap=noverlap, pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.clabel)
def clabel(CS, *args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.clabel(CS, *args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.contour)
def contour(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.contour(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    if ret._A is not None:
        sci(ret)
    return ret


@_autogen_docstring(Axes.contourf)
def contourf(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.contourf(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    if ret._A is not None:
        sci(ret)
    return ret


@_autogen_docstring(Axes.csd)
def csd(x, y, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.csd(x, y, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend, window=window, noverlap=noverlap, pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.errorbar)
def errorbar(x, y, yerr=None, xerr=None, fmt='-', ecolor=None, elinewidth=None, capsize=3, barsabove=False, lolims=False, uplims=False, xlolims=False, xuplims=False, errorevery=1, capthick=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt=fmt, ecolor=ecolor, elinewidth=elinewidth, capsize=capsize, barsabove=barsabove, lolims=lolims, uplims=uplims, xlolims=xlolims, xuplims=xuplims, errorevery=errorevery, capthick=capthick, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.fill)
def fill(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.fill(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.fill_between)
def fill_between(x, y1, y2=0, where=None, interpolate=False, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.fill_between(x, y1, y2=y2, where=where, interpolate=interpolate, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.fill_betweenx)
def fill_betweenx(y, x1, x2=0, where=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.fill_betweenx(y, x1, x2=x2, where=where, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.hexbin)
def hexbin(x, y, C=None, gridsize=100, bins=None, xscale='linear', yscale='linear', extent=None, cmap=None, norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, edgecolors='none', reduce_C_function=np.mean, mincnt=None, marginals=False, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.hexbin(x, y, C=C, gridsize=gridsize, bins=bins, xscale=xscale, yscale=yscale, extent=extent, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, linewidths=linewidths, edgecolors=edgecolors, reduce_C_function=reduce_C_function, mincnt=mincnt, marginals=marginals, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.hist)
def hist(x, bins=10, range=None, normed=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.hist(x, bins=bins, range=range, normed=normed, weights=weights, cumulative=cumulative, bottom=bottom, histtype=histtype, align=align, orientation=orientation, rwidth=rwidth, log=log, color=color, label=label, stacked=stacked, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.hist2d)
def hist2d(x, y, bins=10, range=None, normed=False, weights=None, cmin=None, cmax=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.hist2d(x, y, bins=bins, range=range, normed=normed, weights=weights, cmin=cmin, cmax=cmax, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret[-1])
    return ret


@_autogen_docstring(Axes.hlines)
def hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.hlines(y, xmin, xmax, colors=colors, linestyles=linestyles, label=label, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.imshow)
def imshow(X, cmap=None, norm=None, aspect=None, interpolation=None, alpha=None, vmin=None, vmax=None, origin=None, extent=None, shape=None, filternorm=1, filterrad=4.0, imlim=None, resample=None, url=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.imshow(X, cmap=cmap, norm=norm, aspect=aspect, interpolation=interpolation, alpha=alpha, vmin=vmin, vmax=vmax, origin=origin, extent=extent, shape=shape, filternorm=filternorm, filterrad=filterrad, imlim=imlim, resample=resample, url=url, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.loglog)
def loglog(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.loglog(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.pcolor)
def pcolor(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.pcolor(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.pcolormesh)
def pcolormesh(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.pcolormesh(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.pie)
def pie(x, explode=None, labels=None, colors=None, autopct=None, pctdistance=0.6, shadow=False, labeldistance=1.1, startangle=None, radius=None, hold=None):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.pie(x, explode=explode, labels=labels, colors=colors, autopct=autopct, pctdistance=pctdistance, shadow=shadow, labeldistance=labeldistance, startangle=startangle, radius=radius)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.plot)
def plot(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.plot(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.plot_date)
def plot_date(x, y, fmt='bo', tz=None, xdate=True, ydate=False, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.plot_date(x, y, fmt=fmt, tz=tz, xdate=xdate, ydate=ydate, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.psd)
def psd(x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.psd(x, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend, window=window, noverlap=noverlap, pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.quiver)
def quiver(*args, **kw):
    ax = gca()
    washold = ax.ishold()
    hold = kw.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.quiver(*args, **kw)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.quiverkey)
def quiverkey(*args, **kw):
    ax = gca()
    washold = ax.ishold()
    hold = kw.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.quiverkey(*args, **kw)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.scatter)
def scatter(x, y, s=20, c='b', marker='o', cmap=None, norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, faceted=True, verts=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.scatter(x, y, s=s, c=c, marker=marker, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, linewidths=linewidths, faceted=faceted, verts=verts, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.semilogx)
def semilogx(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.semilogx(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.semilogy)
def semilogy(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.semilogy(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.specgram)
def specgram(x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=128, cmap=None, xextent=None, pad_to=None, sides='default', scale_by_freq=None, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.specgram(x, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend, window=window, noverlap=noverlap, cmap=cmap, xextent=xextent, pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret[-1])
    return ret


@_autogen_docstring(Axes.stackplot)
def stackplot(x, *args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.stackplot(x, *args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.stem)
def stem(x, y, linefmt='b-', markerfmt='bo', basefmt='r-', bottom=None, label=None, hold=None):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.stem(x, y, linefmt=linefmt, markerfmt=markerfmt, basefmt=basefmt, bottom=bottom, label=label)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.step)
def step(x, y, *args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.step(x, y, *args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.streamplot)
def streamplot(x, y, u, v, density=1, linewidth=None, color=None, cmap=None, norm=None, arrowsize=1, arrowstyle='-|>', minlength=0.1, transform=None, hold=None):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.streamplot(x, y, u, v, density=density, linewidth=linewidth, color=color, cmap=cmap, norm=norm, arrowsize=arrowsize, arrowstyle=arrowstyle, minlength=minlength, transform=transform)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret.lines)
    return ret


@_autogen_docstring(Axes.tricontour)
def tricontour(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.tricontour(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    if ret._A is not None:
        sci(ret)
    return ret


@_autogen_docstring(Axes.tricontourf)
def tricontourf(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.tricontourf(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    if ret._A is not None:
        sci(ret)
    return ret


@_autogen_docstring(Axes.tripcolor)
def tripcolor(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.tripcolor(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    sci(ret)
    return ret


@_autogen_docstring(Axes.triplot)
def triplot(*args, **kwargs):
    ax = gca()
    washold = ax.ishold()
    hold = kwargs.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.triplot(*args, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.vlines)
def vlines(x, ymin, ymax, colors='k', linestyles='solid', label='', hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.vlines(x, ymin, ymax, colors=colors, linestyles=linestyles, label=label, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.xcorr)
def xcorr(x, y, normed=True, detrend=mlab.detrend_none, usevlines=True, maxlags=10, hold=None, **kwargs):
    ax = gca()
    washold = ax.ishold()
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.xcorr(x, y, normed=normed, detrend=detrend, usevlines=usevlines, maxlags=maxlags, **kwargs)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@_autogen_docstring(Axes.barbs)
def barbs(*args, **kw):
    ax = gca()
    washold = ax.ishold()
    hold = kw.pop('hold', None)
    if hold is not None:
        ax.hold(hold)
    try:
        ret = ax.barbs(*args, **kw)
        draw_if_interactive()
    finally:
        ax.hold(washold)

    return ret


@docstring.copy_dedent(Axes.cla)
def cla():
    ret = gca().cla()
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.grid)
def grid(b=None, which='major', axis='both', **kwargs):
    ret = gca().grid(b=b, which=which, axis=axis, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.legend)
def legend(*args, **kwargs):
    ret = gca().legend(*args, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.table)
def table(**kwargs):
    ret = gca().table(**kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.text)
def text(x, y, s, fontdict=None, withdash=False, **kwargs):
    ret = gca().text(x, y, s, fontdict=fontdict, withdash=withdash, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.annotate)
def annotate(*args, **kwargs):
    ret = gca().annotate(*args, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.ticklabel_format)
def ticklabel_format(**kwargs):
    ret = gca().ticklabel_format(**kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.locator_params)
def locator_params(axis='both', tight=None, **kwargs):
    ret = gca().locator_params(axis=axis, tight=tight, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.tick_params)
def tick_params(axis='both', **kwargs):
    ret = gca().tick_params(axis=axis, **kwargs)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.margins)
def margins(*args, **kw):
    ret = gca().margins(*args, **kw)
    draw_if_interactive()
    return ret


@docstring.copy_dedent(Axes.autoscale)
def autoscale(enable=True, axis='both', tight=None):
    ret = gca().autoscale(enable=enable, axis=axis, tight=tight)
    draw_if_interactive()
    return ret


def autumn():
    """
    set the default colormap to autumn and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='autumn')
    im = gci()
    if im is not None:
        im.set_cmap(cm.autumn)
    draw_if_interactive()
    return


def bone():
    """
    set the default colormap to bone and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='bone')
    im = gci()
    if im is not None:
        im.set_cmap(cm.bone)
    draw_if_interactive()
    return


def cool():
    """
    set the default colormap to cool and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='cool')
    im = gci()
    if im is not None:
        im.set_cmap(cm.cool)
    draw_if_interactive()
    return


def copper():
    """
    set the default colormap to copper and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='copper')
    im = gci()
    if im is not None:
        im.set_cmap(cm.copper)
    draw_if_interactive()
    return


def flag():
    """
    set the default colormap to flag and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='flag')
    im = gci()
    if im is not None:
        im.set_cmap(cm.flag)
    draw_if_interactive()
    return


def gray():
    """
    set the default colormap to gray and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='gray')
    im = gci()
    if im is not None:
        im.set_cmap(cm.gray)
    draw_if_interactive()
    return


def hot():
    """
    set the default colormap to hot and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='hot')
    im = gci()
    if im is not None:
        im.set_cmap(cm.hot)
    draw_if_interactive()
    return


def hsv():
    """
    set the default colormap to hsv and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='hsv')
    im = gci()
    if im is not None:
        im.set_cmap(cm.hsv)
    draw_if_interactive()
    return


def jet():
    """
    set the default colormap to jet and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='jet')
    im = gci()
    if im is not None:
        im.set_cmap(cm.jet)
    draw_if_interactive()
    return


def pink():
    """
    set the default colormap to pink and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='pink')
    im = gci()
    if im is not None:
        im.set_cmap(cm.pink)
    draw_if_interactive()
    return


def prism():
    """
    set the default colormap to prism and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='prism')
    im = gci()
    if im is not None:
        im.set_cmap(cm.prism)
    draw_if_interactive()
    return


def spring():
    """
    set the default colormap to spring and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='spring')
    im = gci()
    if im is not None:
        im.set_cmap(cm.spring)
    draw_if_interactive()
    return


def summer():
    """
    set the default colormap to summer and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='summer')
    im = gci()
    if im is not None:
        im.set_cmap(cm.summer)
    draw_if_interactive()
    return


def winter():
    """
    set the default colormap to winter and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='winter')
    im = gci()
    if im is not None:
        im.set_cmap(cm.winter)
    draw_if_interactive()
    return


def spectral():
    """
    set the default colormap to spectral and apply to current image if any.
    See help(colormaps) for more information
    """
    rc('image', cmap='spectral')
    im = gci()
    if im is not None:
        im.set_cmap(cm.spectral)
    draw_if_interactive()
    return


_setup_pyplot_info_docstrings()