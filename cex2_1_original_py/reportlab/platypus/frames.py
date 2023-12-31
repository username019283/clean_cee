# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\platypus\frames.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = 'A frame is a container for content on a page.\n'
import logging
logger = logging.getLogger('reportlab.platypus')
_geomAttr = ('x1', 'y1', 'width', 'height', 'leftPadding', 'bottomPadding', 'rightPadding',
             'topPadding')
from reportlab import rl_config
_FUZZ = rl_config._FUZZ

class ShowBoundaryValue:

    def __init__(self, color=(0, 0, 0), width=0.1):
        self.color = color
        self.width = width

    def __nonzero__(self):
        return self.color is not None and self.width >= 0


class Frame:
    """
    A Frame is a piece of space in a document that is filled by the
    "flowables" in the story.  For example in a book like document most
    pages have the text paragraphs in one or two frames.  For generality
    a page might have several frames (for example for 3 column text or
    for text that wraps around a graphic).

    After creation a Frame is not usually manipulated directly by the
    applications program -- it is used internally by the platypus modules.

    Here is a diagramatid abstraction for the definitional part of a Frame::

                width                    x2,y2
        +---------------------------------+
        | l  top padding                r | h
        | e +-------------------------+ i | e
        | f |                         | g | i
        | t |                         | h | g
        |   |                         | t | h
        | p |                         |   | t
        | a |                         | p |
        | d |                         | a |
        |   |                         | d |
        |   +-------------------------+   |
        |    bottom padding               |
        +---------------------------------+
        (x1,y1) <-- lower left corner

    NOTE!! Frames are stateful objects.  No single frame should be used in
    two documents at the same time (especially in the presence of multithreading.
    """

    def __init__(self, x1, y1, width, height, leftPadding=6, bottomPadding=6, rightPadding=6, topPadding=6, id=None, showBoundary=0, overlapAttachedSpace=None, _debug=None):
        self.id = id
        self._debug = _debug
        self.__dict__['_x1'] = x1
        self.__dict__['_y1'] = y1
        self.__dict__['_width'] = width
        self.__dict__['_height'] = height
        self.__dict__['_leftPadding'] = leftPadding
        self.__dict__['_bottomPadding'] = bottomPadding
        self.__dict__['_rightPadding'] = rightPadding
        self.__dict__['_topPadding'] = topPadding
        self.showBoundary = showBoundary
        if overlapAttachedSpace is None:
            overlapAttachedSpace = rl_config.overlapAttachedSpace
        self._oASpace = overlapAttachedSpace
        self._geom()
        self._reset()
        return

    def __getattr__(self, a):
        if a in _geomAttr:
            return self.__dict__['_' + a]
        raise AttributeError(a)

    def __setattr__(self, a, v):
        if a in _geomAttr:
            self.__dict__['_' + a] = v
            self._geom()
        else:
            self.__dict__[a] = v

    def _saveGeom(self, **kwds):
        if not self.__dict__.setdefault('_savedGeom', {}):
            for ga in _geomAttr:
                ga = '_' + ga
                self.__dict__['_savedGeom'][ga] = self.__dict__[ga]

        for k, v in kwds.iteritems():
            setattr(self, k, v)

    def _restoreGeom(self):
        if self.__dict__.get('_savedGeom', None):
            for ga in _geomAttr:
                ga = '_' + ga
                self.__dict__[ga] = self.__dict__[ga]['_savedGeom']
                del self.__dict__['_savedGeom']

            self._geom()
        return

    def _geom(self):
        self._x2 = self._x1 + self._width
        self._y2 = self._y1 + self._height
        self._y1p = self._y1 + self._bottomPadding
        self._aW = self._x2 - self._x1 - self._leftPadding - self._rightPadding
        self._aH = self._y2 - self._y1p - self._topPadding

    def _reset(self):
        self._restoreGeom()
        self._x = self._x1 + self._leftPadding
        self._y = self._y2 - self._topPadding
        self._atTop = 1
        self._prevASpace = 0
        self._leftExtraIndent = 0.0
        self._rightExtraIndent = 0.0

    def _getAvailableWidth(self):
        return self._aW - self._leftExtraIndent - self._rightExtraIndent

    def _add(self, flowable, canv, trySplit=0):
        """ Draws the flowable at the current position.
        Returns 1 if successful, 0 if it would not fit.
        Raises a LayoutError if the object is too wide,
        or if it is too high for a totally empty frame,
        to avoid infinite loops"""
        flowable._frame = self
        flowable.canv = canv
        try:
            if getattr(flowable, 'frameAction', None):
                flowable.frameAction(self)
                return 1
            else:
                y = self._y
                p = self._y1p
                s = 0
                aW = self._getAvailableWidth()
                if not self._atTop:
                    s = flowable.getSpaceBefore()
                    if self._oASpace:
                        s = max(s - self._prevASpace, 0)
                h = y - p - s
                if h > 0:
                    w, h = flowable.wrap(aW, h)
                else:
                    return 0
                h += s
                y -= h
                if y < p - _FUZZ:
                    if not rl_config.allowTableBoundsErrors and (h > self._aH or w > aW) and not trySplit:
                        from reportlab.platypus.doctemplate import LayoutError
                        raise LayoutError('Flowable %s (%sx%s points) too large for frame (%sx%s points).' % (
                         flowable.__class__, w, h, aW, self._aH))
                    return 0
                flowable.drawOn(canv, self._x + self._leftExtraIndent, y, _sW=aW - w)
                flowable.canv = canv
                if self._debug:
                    logger.debug('drew %s' % flowable.identity())
                s = flowable.getSpaceAfter()
                y -= s
                if self._oASpace:
                    self._prevASpace = s
                if y != self._y:
                    self._atTop = 0
                self._y = y
                return 1

        finally:
            for a in ('canv', '_frame'):
                if hasattr(flowable, a):
                    delattr(flowable, a)

        return

    add = _add

    def split(self, flowable, canv):
        """Ask the flowable to split using up the available space."""
        y = self._y
        p = self._y1p
        s = 0
        if not self._atTop:
            s = flowable.getSpaceBefore()
            if self._oASpace:
                s = max(s - self._prevASpace, 0)
        flowable._frame = self
        flowable.canv = canv
        try:
            r = flowable.split(self._aW, y - p - s)
        finally:
            for a in ('canv', '_frame'):
                if hasattr(flowable, a):
                    delattr(flowable, a)

        return r

    def drawBoundary(self, canv):
        """draw the frame boundary as a rectangle (primarily for debugging)."""
        from reportlab.lib.colors import Color, CMYKColor, toColor
        sb = self.showBoundary
        ss = type(sb) in (type(''), type(()), type([])) or isinstance(sb, Color)
        w = -1
        if ss:
            c = toColor(sb, self)
            ss = c is not self
        elif isinstance(sb, ShowBoundaryValue) and sb:
            c = toColor(sb.color, self)
            w = sb.width
            ss = c is not self
        if ss:
            canv.saveState()
            canv.setStrokeColor(c)
            if w >= 0:
                canv.setLineWidth(w)
        canv.rect(self._x1, self._y1, self._x2 - self._x1, self._y2 - self._y1)
        if ss:
            canv.restoreState()

    def addFromList(self, drawlist, canv):
        """Consumes objects from the front of the list until the
        frame is full.  If it cannot fit one object, raises
        an exception."""
        if self._debug:
            logger.debug('enter Frame.addFromlist() for frame %s' % self.id)
        if self.showBoundary:
            self.drawBoundary(canv)
        while len(drawlist) > 0:
            head = drawlist[0]
            if self.add(head, canv, trySplit=0):
                del drawlist[0]
            else:
                break

    def add_generated_content(self, *C):
        self.__dict__.setdefault('_generated_content', []).extend(C)

    def _aSpaceString(self):
        return '(%s x %s%s)' % (self._getAvailableWidth(), self._aH, self._atTop and '*' or '')