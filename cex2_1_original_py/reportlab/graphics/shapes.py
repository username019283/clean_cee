# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\shapes.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = 'Core of the graphics library - defines Drawing and Shapes'
import string, os, sys
from math import pi, cos, sin, tan, sqrt
from types import FloatType, IntType, ListType, TupleType, StringType, InstanceType
from pprint import pprint
from reportlab.platypus import Flowable
from reportlab.rl_config import shapeChecking, verbose, defaultGraphicsFontName as _baseGFontName, _unset_
from reportlab.lib import logger
from reportlab.lib import colors
from ..reportlab.lib.validators import *
isOpacity = NoneOr(isNumberInRange(0, 1))
from ..reportlab.lib.attrmap import *
from reportlab.lib.utils import fp_str
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.fonts import tt2ps
_baseGFontNameB = tt2ps(_baseGFontName, 1, 0)
_baseGFontNameI = tt2ps(_baseGFontName, 0, 1)
_baseGFontNameBI = tt2ps(_baseGFontName, 1, 1)

class NotImplementedError(Exception):
    pass


NON_ZERO_WINDING = 'Non-Zero Winding'
EVEN_ODD = 'Even-Odd'
STATE_DEFAULTS = {'transform': (1, 0, 0, 1, 0, 0), 
   'strokeColor': colors.black, 
   'strokeWidth': 1, 
   'strokeLineCap': 0, 
   'strokeLineJoin': 0, 
   'strokeMiterLimit': 10, 
   'strokeDashArray': None, 
   'strokeOpacity': None, 
   'fillOpacity': None, 
   'fillOverprint': False, 
   'strokeOverprint': False, 
   'overprintMask': 0, 
   'fillColor': colors.black, 
   'fontSize': 10, 
   'fontName': _baseGFontName, 
   'textAnchor': 'start'}

def nullTransform():
    return (1, 0, 0, 1, 0, 0)


def translate(dx, dy):
    return (
     1, 0, 0, 1, dx, dy)


def scale(sx, sy):
    return (
     sx, 0, 0, sy, 0, 0)


def rotate(angle):
    a = angle * pi / 180
    return (cos(a), sin(a), -sin(a), cos(a), 0, 0)


def skewX(angle):
    a = angle * pi / 180
    return (1, 0, tan(a), 1, 0, 0)


def skewY(angle):
    a = angle * pi / 180
    return (1, tan(a), 0, 1, 0, 0)


def mmult(A, B):
    """A postmultiplied by B"""
    return (
     A[0] * B[0] + A[2] * B[1],
     A[1] * B[0] + A[3] * B[1],
     A[0] * B[2] + A[2] * B[3],
     A[1] * B[2] + A[3] * B[3],
     A[0] * B[4] + A[2] * B[5] + A[4],
     A[1] * B[4] + A[3] * B[5] + A[5])


def inverse(A):
    """For A affine 2D represented as 6vec return 6vec version of A**(-1)"""
    det = float(A[0] * A[3] - A[2] * A[1])
    R = [A[3] / det, -A[1] / det, -A[2] / det, A[0] / det]
    return tuple(R + [-R[0] * A[4] - R[2] * A[5], -R[1] * A[4] - R[3] * A[5]])


def zTransformPoint(A, v):
    """Apply the homogenous part of atransformation a to vector v --> A*v"""
    return (
     A[0] * v[0] + A[2] * v[1], A[1] * v[0] + A[3] * v[1])


def transformPoint(A, v):
    """Apply transformation a to vector v --> A*v"""
    return (
     A[0] * v[0] + A[2] * v[1] + A[4], A[1] * v[0] + A[3] * v[1] + A[5])


def transformPoints(matrix, V):
    return map(transformPoint, V)


def zTransformPoints(matrix, V):
    return map((lambda x, matrix=matrix: zTransformPoint(matrix, x)), V)


def _textBoxLimits(text, font, fontSize, leading, textAnchor, boxAnchor):
    w = 0
    for t in text:
        w = max(w, stringWidth(t, font, fontSize))

    h = len(text) * leading
    yt = fontSize
    if boxAnchor[0] == 's':
        yb = -h
        yt = yt - h
    elif boxAnchor[0] == 'n':
        yb = 0
    else:
        yb = -h / 2.0
        yt = yt + yb
    if boxAnchor[-1] == 'e':
        xb = -w
        if textAnchor == 'end':
            xt = 0
        else:
            if textAnchor == 'start':
                xt = -w
            else:
                xt = -w / 2.0
    elif boxAnchor[-1] == 'w':
        xb = 0
        if textAnchor == 'end':
            xt = w
        else:
            if textAnchor == 'start':
                xt = 0
            else:
                xt = w / 2.0
    else:
        xb = -w / 2.0
        if textAnchor == 'end':
            xt = -xb
        elif textAnchor == 'start':
            xt = xb
        else:
            xt = 0
    return (
     xb, yb, w, h, xt, yt)


def _rotatedBoxLimits(x, y, w, h, angle):
    """
    Find the corner points of the rotated w x h sized box at x,y
    return the corner points and the min max points in the original space
    """
    C = zTransformPoints(rotate(angle), ((x, y), (x + w, y), (x + w, y + h), (x, y + h)))
    X = map((lambda x: x[0]), C)
    Y = map((lambda x: x[1]), C)
    return (min(X), max(X), min(Y), max(Y), C)


class _DrawTimeResizeable:
    """Addin class to provide the horribleness of _drawTimeResize"""

    def _drawTimeResize(self, w, h):
        if hasattr(self, '_canvas'):
            canvas = self._canvas
            drawing = canvas._drawing
            drawing.width, drawing.height = w, h
            if hasattr(canvas, '_drawTimeResize'):
                canvas._drawTimeResize(w, h)


class _SetKeyWordArgs:

    def __init__(self, keywords={}):
        """In general properties may be supplied to the constructor."""
        for key, value in keywords.items():
            setattr(self, key, value)


def getRectsBounds(rectList):
    L = filter((lambda x: x is not None), rectList)
    if not L:
        return None
    else:
        xMin, yMin, xMax, yMax = L[0]
        for x1, y1, x2, y2 in L[1:]:
            if x1 < xMin:
                xMin = x1
            if x2 > xMax:
                xMax = x2
            if y1 < yMin:
                yMin = y1
            if y2 > yMax:
                yMax = y2

        return (
         xMin, yMin, xMax, yMax)


def _getBezierExtrema(y0, y1, y2, y3):
    """
    this is used to find if a curveTo path operator has extrema in its range
    The curveTo operator is defined by the points y0, y1, y2, y3

        B(t):=(1-t)^3*y0+3*(1-t)^2*t*y1+3*(1-t)*t^2*y2+t^3*y3
            :=t^3*(y3-3*y2+3*y1-y0)+t^2*(3*y2-6*y1+3*y0)+t*(3*y1-3*y0)+y0
    and is a cubic bezier curve.

    The differential is a quadratic
        t^2*(3*y3-9*y2+9*y1-3*y0)+t*(6*y2-12*y1+6*y0)+3*y1-3*y0

    The extrema must be at real roots, r, of the above which lie in 0<=r<=1

    The quadratic coefficients are
        a=3*y3-9*y2+9*y1-3*y0 b=6*y2-12*y1+6*y0 c=3*y1-3*y0
    or
        a=y3-3*y2+3*y1-y0 b=2*y2-4*y1+2*y0 c=y1-y0  (remove common factor of 3)
    or
        a=y3-3*(y2-y1)-y0 b=2*(y2-2*y1+y0) c=y1-y0

    The returned value is [y0,x1,x2,y3] where if found x1, x2 are any extremals that were found;
    there can be 0, 1 or 2 extremals
    """
    a = y3 - 3 * (y2 - y1) - y0
    b = 2 * (y2 - 2 * y1 + y0)
    c = y1 - y0
    Y = [y0]
    d = b * b - 4 * a * c
    if d >= 0:
        d = sqrt(d)
        if b < 0:
            d = -d
        q = -0.5 * (b + d)
        R = []
        try:
            R.append(q / a)
        except:
            pass

        try:
            R.append(c / q)
        except:
            pass

        b *= 1.5
        c *= 3
        for t in R:
            if 0 <= t <= 1:
                Y.append(t * (t * (t * a + b) + c) + y0)

    Y.append(y3)
    return Y


def getPathBounds(points):
    n = len(points)
    f = lambda i, p=points: p[i]
    xs = map(f, xrange(0, n, 2))
    ys = map(f, xrange(1, n, 2))
    return (min(xs), min(ys), max(xs), max(ys))


def getPointsBounds(pointList):
    """Helper function for list of points"""
    first = pointList[0]
    if type(first) in (ListType, TupleType):
        xs = map((lambda xy: xy[0]), pointList)
        ys = map((lambda xy: xy[1]), pointList)
        return (
         min(xs), min(ys), max(xs), max(ys))
    else:
        return getPathBounds(pointList)


class Shape(_SetKeyWordArgs, _DrawTimeResizeable):
    """Base class for all nodes in the tree. Nodes are simply
    packets of data to be created, stored, and ultimately
    rendered - they don't do anything active.  They provide
    convenience methods for verification but do not
    check attribiute assignments or use any clever setattr
    tricks this time."""
    _attrMap = AttrMap()

    def copy(self):
        """Return a clone of this shape."""
        raise NotImplementedError, 'No copy method implemented for %s' % self.__class__.__name__

    def getProperties(self, recur=1):
        """Interface to make it easy to extract automatic
        documentation"""
        props = {}
        for key, value in self.__dict__.items():
            if key[0:1] != '_':
                props[key] = value

        return props

    def setProperties(self, props):
        """Supports the bulk setting if properties from,
        for example, a GUI application or a config file."""
        self.__dict__.update(props)

    def dumpProperties(self, prefix=''):
        """Convenience. Lists them on standard output.  You
        may provide a prefix - mostly helps to generate code
        samples for documentation."""
        propList = self.getProperties().items()
        propList.sort()
        if prefix:
            prefix = prefix + '.'
        for name, value in propList:
            print '%s%s = %s' % (prefix, name, value)

    def verify(self):
        """If the programmer has provided the optional
        _attrMap attribute, this checks all expected
        attributes are present; no unwanted attributes
        are present; and (if a checking function is found)
        checks each attribute.  Either succeeds or raises
        an informative exception."""
        if self._attrMap is not None:
            for key in self.__dict__.keys():
                if key[0] != '_':
                    assert key in self._attrMap, 'Unexpected attribute %s found in %s' % (key, self)

            for attr, metavalue in self._attrMap.items():
                assert hasattr(self, attr), 'Missing attribute %s from %s' % (attr, self)
                value = getattr(self, attr)
                assert metavalue.validate(value), 'Invalid value %s for attribute %s in class %s' % (value, attr, self.__class__.__name__)

        return

    if shapeChecking:

        def __setattr__(self, attr, value):
            """By default we verify.  This could be off
            in some parallel base classes."""
            validateSetattr(self, attr, value)

    def getBounds(self):
        """Returns bounding rectangle of object as (x1,y1,x2,y2)"""
        raise NotImplementedError('Shapes and widgets must implement getBounds')


class Group(Shape):
    """Groups elements together.  May apply a transform
    to its contents.  Has a publicly accessible property
    'contents' which may be used to iterate over contents.
    In addition, child nodes may be given a name in which
    case they are subsequently accessible as properties."""
    _attrMap = AttrMap(transform=AttrMapValue(isTransform, desc='Coordinate transformation to apply', advancedUsage=1), contents=AttrMapValue(isListOfShapes, desc='Contained drawable elements'), strokeOverprint=AttrMapValue(isBoolean, desc='Turn on stroke overprinting'), fillOverprint=AttrMapValue(isBoolean, desc='Turn on fill overprinting', advancedUsage=1), overprintMask=AttrMapValue(isBoolean, desc='overprinting for ordinary CMYK', advancedUsage=1))

    def __init__(self, *elements, **keywords):
        """Initial lists of elements may be provided to allow
        compact definitions in literal Python code.  May or
        may not be useful."""
        self._attrMap = self._attrMap.clone()
        self.contents = []
        self.transform = (1, 0, 0, 1, 0, 0)
        for elt in elements:
            self.add(elt)

        _SetKeyWordArgs.__init__(self, keywords)

    def _addNamedNode(self, name, node):
        """if name is not None add an attribute pointing to node and add to the attrMap"""
        if name:
            if name not in self._attrMap.keys():
                self._attrMap[name] = AttrMapValue(isValidChild)
            setattr(self, name, node)

    def add(self, node, name=None):
        """Appends non-None child node to the 'contents' attribute. In addition,
        if a name is provided, it is subsequently accessible by name
        """
        if node is not None:
            assert isValidChild(node), 'Can only add Shape or UserNode objects to a Group'
            self.contents.append(node)
            self._addNamedNode(name, node)
        return

    def _nn(self, node):
        self.add(node)
        return self.contents[-1]

    def insert(self, i, n, name=None):
        """Inserts sub-node n in contents at specified location"""
        if n is not None:
            assert isValidChild(n), 'Can only insert Shape or UserNode objects in a Group'
            if i < 0:
                self.contents[i:i] = [
                 n]
            else:
                self.contents.insert(i, n)
            self._addNamedNode(name, n)
        return

    def expandUserNodes(self):
        """Return a new object which only contains primitive shapes."""
        obj = isinstance(self, Drawing) and Drawing(self.width, self.height) or Group()
        obj._attrMap = self._attrMap.clone()
        if hasattr(obj, 'transform'):
            obj.transform = self.transform[:]
        self_contents = self.contents
        a = obj.contents.append
        for child in self_contents:
            if isinstance(child, UserNode):
                newChild = child.provideNode()
            elif isinstance(child, Group):
                newChild = child.expandUserNodes()
            else:
                newChild = child.copy()
            a(newChild)

        self._copyNamedContents(obj)
        return obj

    def _explode(self):
        """ return a fully expanded object"""
        from reportlab.graphics.widgetbase import Widget
        obj = Group()
        if hasattr(obj, 'transform'):
            obj.transform = self.transform[:]
        P = self.contents[:]
        while P:
            n = P.pop(0)
            if isinstance(n, UserNode):
                P.append(n.provideNode())
            elif isinstance(n, Group):
                n = n._explode()
                if n.transform == (1, 0, 0, 1, 0, 0):
                    obj.contents.extend(n.contents)
                else:
                    obj.add(n)
            else:
                obj.add(n)

        return obj

    def _copyContents(self, obj):
        for child in self.contents:
            obj.contents.append(child)

    def _copyNamedContents(self, obj, aKeys=None, noCopy=('contents', )):
        from copy import copy
        self_contents = self.contents
        if not aKeys:
            aKeys = self._attrMap.keys()
        for k, v in self.__dict__.items():
            if v in self_contents:
                pos = self_contents.index(v)
                setattr(obj, k, obj.contents[pos])
            elif k in aKeys and k not in noCopy:
                setattr(obj, k, copy(v))

    def _copy(self, obj):
        """copies to obj"""
        obj._attrMap = self._attrMap.clone()
        self._copyContents(obj)
        self._copyNamedContents(obj)
        return obj

    def copy(self):
        """returns a copy"""
        return self._copy(self.__class__())

    def rotate(self, theta):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, rotate(theta))

    def translate(self, dx, dy):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, translate(dx, dy))

    def scale(self, sx, sy):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, scale(sx, sy))

    def skew(self, kx, ky):
        """Convenience to help you set transforms"""
        self.transform = mmult(mmult(self.transform, skewX(kx)), skewY(ky))

    def shift(self, x, y):
        """Convenience function to set the origin arbitrarily"""
        self.transform = self.transform[:-2] + (x, y)

    def asDrawing(self, width, height):
        """ Convenience function to make a drawing from a group
            After calling this the instance will be a drawing!
        """
        self.__class__ = Drawing
        self._attrMap.update(self._xtraAttrMap)
        self.width = width
        self.height = height

    def getContents(self):
        """Return the list of things to be rendered
        override to get more complicated behaviour"""
        b = getattr(self, 'background', None)
        C = self.contents
        if b and b not in C:
            C = [b] + C
        return C

    def getBounds(self):
        if self.contents:
            b = []
            for elem in self.contents:
                b.append(elem.getBounds())

            x1 = getRectsBounds(b)
            if x1 is None:
                return
            x1, y1, x2, y2 = x1
            trans = self.transform
            corners = [[x1, y1], [x1, y2], [x2, y1], [x2, y2]]
            newCorners = []
            for corner in corners:
                newCorners.append(transformPoint(trans, corner))

            return getPointsBounds(newCorners)
        else:
            return
            return


def _addObjImport(obj, I, n=None):
    """add an import of obj's class to a dictionary of imports"""
    from inspect import getmodule
    c = obj.__class__
    m = getmodule(c).__name__
    n = n or c.__name__
    if m not in I:
        I[m] = [
         n]
    elif n not in I[m]:
        I[m].append(n)


def _repr(self, I=None):
    """return a repr style string with named fixed args first, then keywords"""
    if type(self) is InstanceType:
        if self is EmptyClipPath:
            _addObjImport(self, I, 'EmptyClipPath')
            return 'EmptyClipPath'
        if I:
            _addObjImport(self, I)
        if isinstance(self, Shape):
            from inspect import getargs
            args, varargs, varkw = getargs(self.__init__.im_func.func_code)
            P = self.getProperties()
            s = self.__class__.__name__ + '('
            for n in args[1:]:
                v = P[n]
                del P[n]
                s = s + '%s,' % _repr(v, I)

            for n, v in P.items():
                v = P[n]
                s = s + '%s=%s,' % (n, _repr(v, I))

            return s[:-1] + ')'
        return repr(self)
    else:
        if type(self) is FloatType:
            return fp_str(self)
        if type(self) in (ListType, TupleType):
            s = ''
            for v in self:
                s = s + '%s,' % _repr(v, I)

            if type(self) is ListType:
                return '[%s]' % s[:-1]
            return '(%s%s)' % (s[:-1], len(self) == 1 and ',' or '')
        else:
            return repr(self)


def _renderGroupPy(G, pfx, I, i=0, indent='\t\t'):
    s = ''
    C = getattr(G, 'transform', None)
    if C:
        s = s + '%s%s.transform = %s\n' % (indent, pfx, _repr(C))
    C = G.contents
    for n in C:
        if isinstance(n, Group):
            npfx = 'v%d' % i
            i = i + 1
            s = s + '%s%s=%s._nn(Group())\n' % (indent, npfx, pfx)
            s = s + _renderGroupPy(n, npfx, I, i, indent)
            i = i - 1
        else:
            s = s + '%s%s.add(%s)\n' % (indent, pfx, _repr(n, I))

    return s


def _extraKW(self, pfx, **kw):
    kw.update(self.__dict__)
    R = {}
    n = len(pfx)
    for k in kw.keys():
        if k.startswith(pfx):
            R[k[n:]] = kw[k]

    return R


class Drawing(Group, Flowable):
    """Outermost container; the thing a renderer works on.
    This has no properties except a height, width and list
    of contents."""
    _saveModes = ('pdf', 'ps', 'eps', 'gif', 'png', 'jpg', 'jpeg', 'pct', 'pict', 'tiff',
                  'tif', 'py', 'bmp', 'svg', 'tiffp', 'tiffl', 'tiff1')
    _xtraAttrMap = AttrMap(width=AttrMapValue(isNumber, desc='Drawing width in points.'), height=AttrMapValue(isNumber, desc='Drawing height in points.'), canv=AttrMapValue(None), background=AttrMapValue(isValidChildOrNone, desc='Background widget for the drawing e.g. Rect(0,0,width,height)'), hAlign=AttrMapValue(OneOf('LEFT', 'RIGHT', 'CENTER', 'CENTRE'), desc='Horizontal alignment within parent document'), vAlign=AttrMapValue(OneOf('TOP', 'BOTTOM', 'CENTER', 'CENTRE'), desc='Vertical alignment within parent document'), renderScale=AttrMapValue(isNumber, desc='Global scaling for rendering'))
    _attrMap = AttrMap(BASE=Group)
    _attrMap.update(_xtraAttrMap)

    def __init__(self, width=400, height=200, *nodes, **keywords):
        self.background = None
        Group.__init__(self, *nodes, **keywords)
        self.width = width
        self.height = height
        self.hAlign = 'LEFT'
        self.vAlign = 'BOTTOM'
        self.renderScale = 1.0
        return

    def _renderPy(self):
        I = {'reportlab.graphics.shapes': ['_DrawingEditorMixin', 'Drawing', 'Group']}
        G = _renderGroupPy(self._explode(), 'self', I)
        n = 'ExplodedDrawing_' + self.__class__.__name__
        s = '#Autogenerated by ReportLab guiedit do not edit\n'
        for m, o in I.items():
            s = s + 'from %s import %s\n' % (m, string.replace(str(o)[1:-1], "'", ''))

        s = s + '\nclass %s(_DrawingEditorMixin,Drawing):\n' % n
        s = s + '\tdef __init__(self,width=%s,height=%s,*args,**kw):\n' % (self.width, self.height)
        s = s + '\t\tDrawing.__init__(self,width,height,*args,**kw)\n'
        s = s + G
        s = s + '\n\nif __name__=="__main__": #NORUNTESTS\n\t%s().save(formats=[\'pdf\'],outDir=\'.\',fnRoot=None)\n' % n
        return s

    def draw(self, showBoundary=_unset_):
        """This is used by the Platypus framework to let the document
        draw itself in a story.  It is specific to PDF and should not
        be used directly."""
        import renderPDF
        renderPDF.draw(self, self.canv, 0, 0, showBoundary=showBoundary)

    def wrap(self, availWidth, availHeight):
        width = self.width
        height = self.height
        renderScale = self.renderScale
        if renderScale != 1.0:
            width *= renderScale
            height *= renderScale
        return (
         width, height)

    def expandUserNodes(self):
        """Return a new drawing which only contains primitive shapes."""
        obj = Group.expandUserNodes(self)
        obj.width = self.width
        obj.height = self.height
        return obj

    def copy(self):
        """Returns a copy"""
        return self._copy(self.__class__(self.width, self.height))

    def asGroup(self, *args, **kw):
        return self._copy(Group(*args, **kw))

    def save(self, formats=None, verbose=None, fnRoot=None, outDir=None, title='', **kw):
        """Saves copies of self in desired location and formats.
        Multiple formats can be supported in one call

        the extra keywords can be of the form
        _renderPM_dpi=96 (which passes dpi=96 to renderPM)
        """
        genFmt = kw.pop('seqNumber', '')
        if isinstance(genFmt, int):
            genFmt = '%4d: ' % genFmt
        else:
            genFmt = ''
        genFmt += 'generating %s file %s'
        from reportlab import rl_config
        ext = ''
        if not fnRoot:
            fnRoot = getattr(self, 'fileNamePattern', self.__class__.__name__ + '%03d')
            chartId = getattr(self, 'chartId', 0)
            if hasattr(chartId, '__call__'):
                chartId = chartId(self)
            if hasattr(fnRoot, '__call__'):
                fnRoot = fnRoot(chartId)
            else:
                try:
                    fnRoot = fnRoot % chartId
                except TypeError as err:
                    if str(err).find('not all arguments converted') < 0:
                        raise

        if os.path.isabs(fnRoot):
            outDir, fnRoot = os.path.split(fnRoot)
        else:
            outDir = outDir or getattr(self, 'outDir', '.')
        outDir = outDir.rstrip().rstrip(os.sep)
        if not outDir:
            outDir = '.'
        if not os.path.isabs(outDir):
            outDir = os.path.join(getattr(self, '_override_CWD', os.path.dirname(sys.argv[0])), outDir)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        fnroot = os.path.normpath(os.path.join(outDir, fnRoot))
        plotMode = os.path.splitext(fnroot)
        if string.lower(plotMode[1][1:]) in self._saveModes:
            fnroot = plotMode[0]
        plotMode = [ x.lower() for x in formats or getattr(self, 'formats', ['pdf']) ]
        verbose = (verbose is not None and (verbose,) or (getattr(self, 'verbose', verbose),))[0]
        _saved = (logger.warnOnce.enabled, logger.infoOnce.enabled)
        logger.warnOnce.enabled = logger.infoOnce.enabled = verbose
        if 'pdf' in plotMode:
            from reportlab.graphics import renderPDF
            filename = fnroot + '.pdf'
            if verbose:
                print genFmt % ('PDF', filename)
            renderPDF.drawToFile(self, filename, title, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), **_extraKW(self, '_renderPDF_', **kw))
            ext = ext + '/.pdf'
            if sys.platform == 'mac':
                import macfs, macostools
                macfs.FSSpec(filename).SetCreatorType('CARO', 'PDF ')
                macostools.touched(filename)
        for bmFmt in ('gif', 'png', 'tif', 'jpg', 'tiff', 'pct', 'pict', 'bmp', 'tiffp',
                      'tiffl', 'tiff1'):
            if bmFmt in plotMode:
                from reportlab.graphics import renderPM
                filename = '%s.%s' % (fnroot, bmFmt)
                if verbose:
                    print genFmt % (bmFmt, filename)
                dtc = getattr(self, '_drawTimeCollector', None)
                if dtc:
                    dtcfmts = getattr(dtc, 'formats', [bmFmt])
                    if bmFmt in dtcfmts and not getattr(dtc, 'disabled', 0):
                        dtc.clear()
                    else:
                        dtc = None
                renderPM.drawToFile(self, filename, fmt=bmFmt, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), **_extraKW(self, '_renderPM_', **kw))
                ext = ext + '/.' + bmFmt
                if dtc:
                    dtc.save(filename)

        if 'eps' in plotMode:
            try:
                from rlextra.graphics import renderPS_SEP as renderPS
            except ImportError:
                from reportlab.graphics import renderPS

            filename = fnroot + '.eps'
            if verbose:
                print genFmt % ('EPS', filename)
            renderPS.drawToFile(self, filename, title=fnroot, dept=getattr(self, 'EPS_info', ['Testing'])[0], company=getattr(self, 'EPS_info', ['', 'ReportLab'])[1], preview=getattr(self, 'preview', rl_config.eps_preview), showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), ttf_embed=getattr(self, 'ttf_embed', rl_config.eps_ttf_embed), **_extraKW(self, '_renderPS_', **kw))
            ext = ext + '/.eps'
        if 'svg' in plotMode:
            from reportlab.graphics import renderSVG
            filename = fnroot + '.svg'
            if verbose:
                print genFmt % ('SVG', filename)
            renderSVG.drawToFile(self, filename, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), **_extraKW(self, '_renderSVG_', **kw))
            ext = ext + '/.svg'
        if 'ps' in plotMode:
            from reportlab.graphics import renderPS
            filename = fnroot + '.ps'
            if verbose:
                print genFmt % ('EPS', filename)
            renderPS.drawToFile(self, filename, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), **_extraKW(self, '_renderPS_', **kw))
            ext = ext + '/.ps'
        if 'py' in plotMode:
            filename = fnroot + '.py'
            if verbose:
                print genFmt % ('py', filename)
            open(filename, 'w').write(self._renderPy())
            ext = ext + '/.py'
        logger.warnOnce.enabled, logger.infoOnce.enabled = _saved
        if hasattr(self, 'saveLogger'):
            self.saveLogger(fnroot, ext)
        return ext and fnroot + ext[1:] or ''

    def asString(self, format, verbose=None, preview=0, **kw):
        """Converts to an 8 bit string in given format."""
        assert format in ('pdf', 'ps', 'eps', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'ppm',
                          'tiff', 'tif', 'py', 'pict', 'pct', 'tiffp', 'tiffl', 'tiff1'), 'Unknown file format "%s"' % format
        from reportlab import rl_config
        if format == 'pdf':
            from reportlab.graphics import renderPDF
            return renderPDF.drawToString(self)
        if format in ('gif', 'png', 'tif', 'tiff', 'jpg', 'pct', 'pict', 'bmp', 'ppm',
                      'tiffp', 'tiffl', 'tiff1'):
            from reportlab.graphics import renderPM
            return renderPM.drawToString(self, fmt=format, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary), **_extraKW(self, '_renderPM_', **kw))
        if format == 'eps':
            try:
                from rlextra.graphics import renderPS_SEP as renderPS
            except ImportError:
                from reportlab.graphics import renderPS

            return renderPS.drawToString(self, preview=preview, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary))
        if format == 'ps':
            from reportlab.graphics import renderPS
            return renderPS.drawToString(self, showBoundary=getattr(self, 'showBorder', rl_config.showBoundary))
        if format == 'py':
            return self._renderPy()

    def resized(self, kind='fit', lpad=0, rpad=0, bpad=0, tpad=0):
        """return a base class drawing which ensures all the contents fits"""
        C = self.getContents()
        oW = self.width
        oH = self.height
        drawing = Drawing(oW, oH, *C)
        xL, yL, xH, yH = drawing.getBounds()
        if kind == 'fit' or kind == 'expand' and (xL < lpad or xH > oW - rpad or yL < bpad or yH > oH - tpad):
            drawing.width = xH - xL + lpad + rpad
            drawing.height = yH - yL + tpad + bpad
            drawing.transform = (1, 0, 0, 1, lpad - xL, bpad - yL)
        elif kind == 'fitx' or kind == 'expandx' and (xL < lpad or xH > oW - rpad):
            drawing.width = xH - xL + lpad + rpad
            drawing.transform = (1, 0, 0, 1, lpad - xL, 0)
        elif kind == 'fity' or kind == 'expandy' and (yL < bpad or yH > oH - tpad):
            drawing.height = yH - yL + tpad + bpad
            drawing.transform = (1, 0, 0, 1, 0, bpad - yL)
        return drawing


class _DrawingEditorMixin:
    """This is a mixin to provide functionality for edited drawings"""

    def _add(self, obj, value, name=None, validate=None, desc=None, pos=None):
        """
        effectively setattr(obj,name,value), but takes care of things with _attrMaps etc
        """
        ivc = isValidChild(value)
        if name and hasattr(obj, '_attrMap'):
            if '_attrMap' not in obj.__dict__:
                obj._attrMap = obj._attrMap.clone()
            if ivc and validate is None:
                validate = isValidChild
            obj._attrMap[name] = AttrMapValue(validate, desc)
        if hasattr(obj, 'add') and ivc:
            if pos:
                obj.insert(pos, value, name)
            else:
                obj.add(value, name)
        elif name:
            setattr(obj, name, value)
        else:
            raise ValueError, "Can't add, need name"
        return


class LineShape(Shape):
    _attrMap = AttrMap(strokeColor=AttrMapValue(isColorOrNone), strokeWidth=AttrMapValue(isNumber), strokeLineCap=AttrMapValue(OneOf(0, 1, 2), desc='Line cap 0=butt, 1=round & 2=square'), strokeLineJoin=AttrMapValue(OneOf(0, 1, 2), desc='Line join 0=miter, 1=round & 2=bevel'), strokeMiterLimit=AttrMapValue(isNumber, desc='miter limit control miter line joins'), strokeDashArray=AttrMapValue(isListOfNumbersOrNone, desc='a sequence of numbers represents on and off, e.g. (2,1)'), strokeOpacity=AttrMapValue(isOpacity, desc='The level of transparency of the line, any real number betwen 0 and 1'), strokeOverprint=AttrMapValue(isBoolean, desc='Turn on stroke overprinting'), overprintMask=AttrMapValue(isBoolean, desc='overprinting for ordinary CMYK', advancedUsage=1))

    def __init__(self, kw):
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeWidth = 1
        self.strokeLineCap = 0
        self.strokeLineJoin = 0
        self.strokeMiterLimit = 0
        self.strokeDashArray = None
        self.strokeOpacity = None
        self.setProperties(kw)
        return


class Line(LineShape):
    _attrMap = AttrMap(BASE=LineShape, x1=AttrMapValue(isNumber, desc=''), y1=AttrMapValue(isNumber, desc=''), x2=AttrMapValue(isNumber, desc=''), y2=AttrMapValue(isNumber, desc=''))

    def __init__(self, x1, y1, x2, y2, **kw):
        LineShape.__init__(self, kw)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def getBounds(self):
        """Returns bounding rectangle of object as (x1,y1,x2,y2)"""
        return (
         self.x1, self.y1, self.x2, self.y2)


class SolidShape(LineShape):
    _attrMap = AttrMap(BASE=LineShape, fillColor=AttrMapValue(isColorOrNone, desc='filling color of the shape, e.g. red'), fillOpacity=AttrMapValue(isOpacity, desc='the level of transparency of the color, any real number between 0 and 1'), fillOverprint=AttrMapValue(isBoolean, desc='Turn on fill overprinting'), overprintMask=AttrMapValue(isBoolean, desc='overprinting for ordinary CMYK', advancedUsage=1))

    def __init__(self, kw):
        self.fillColor = STATE_DEFAULTS['fillColor']
        self.fillOpacity = None
        LineShape.__init__(self, kw)
        return


_MOVETO, _LINETO, _CURVETO, _CLOSEPATH = range(4)
_PATH_OP_ARG_COUNT = (2, 2, 6, 0)
_PATH_OP_NAMES = ['moveTo', 'lineTo', 'curveTo', 'closePath']

def _renderPath(path, drawFuncs):
    """Helper function for renderers."""
    points = path.points
    i = 0
    hadClosePath = 0
    hadMoveTo = 0
    for op in path.operators:
        nArgs = _PATH_OP_ARG_COUNT[op]
        func = drawFuncs[op]
        j = i + nArgs
        func(*points[i:j])
        i = j
        if op == _CLOSEPATH:
            hadClosePath = hadClosePath + 1
        if op == _MOVETO:
            hadMoveTo += 1

    return hadMoveTo == hadClosePath


class Path(SolidShape):
    """Path, made up of straight lines and bezier curves."""
    _attrMap = AttrMap(BASE=SolidShape, points=AttrMapValue(isListOfNumbers), operators=AttrMapValue(isListOfNumbers), isClipPath=AttrMapValue(isBoolean))

    def __init__(self, points=None, operators=None, isClipPath=0, **kw):
        SolidShape.__init__(self, kw)
        if points is None:
            points = []
        if operators is None:
            operators = []
        assert len(points) % 2 == 0, 'Point list must have even number of elements!'
        self.points = points
        self.operators = operators
        self.isClipPath = isClipPath
        return

    def copy(self):
        new = self.__class__(self.points[:], self.operators[:])
        new.setProperties(self.getProperties())
        return new

    def moveTo(self, x, y):
        self.points.extend([x, y])
        self.operators.append(_MOVETO)

    def lineTo(self, x, y):
        self.points.extend([x, y])
        self.operators.append(_LINETO)

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self.points.extend([x1, y1, x2, y2, x3, y3])
        self.operators.append(_CURVETO)

    def closePath(self):
        self.operators.append(_CLOSEPATH)

    def getBounds(self):
        points = self.points
        try:
            X = []
            aX = X.append
            eX = X.extend
            Y = []
            aY = Y.append
            eY = Y.extend
            i = 0
            for op in self.operators:
                nArgs = _PATH_OP_ARG_COUNT[op]
                j = i + nArgs
                if nArgs == 2:
                    aX(points[i])
                    aY(points[i + 1])
                elif nArgs == 6:
                    x1, x2, x3 = points[i:j:2]
                    eX(_getBezierExtrema(X[-1], x1, x2, x3))
                    y1, y2, y3 = points[i + 1:j:2]
                    eY(_getBezierExtrema(Y[-1], y1, y2, y3))
                i = j

            return (
             min(X), min(Y), max(X), max(Y))
        except:
            return getPathBounds(points)


EmptyClipPath = Path()

def getArcPoints(centerx, centery, radius, startangledegrees, endangledegrees, yradius=None, degreedelta=None, reverse=None):
    if yradius is None:
        yradius = radius
    points = []
    from math import sin, cos, pi
    degreestoradians = pi / 180.0
    startangle = startangledegrees * degreestoradians
    endangle = endangledegrees * degreestoradians
    while endangle < startangle:
        endangle = endangle + 2 * pi

    angle = float(endangle - startangle)
    a = points.append
    if angle > 0.001:
        degreedelta = min(angle, degreedelta or 1.0)
        radiansdelta = degreedelta * degreestoradians
        n = max(int(angle / radiansdelta + 0.5), 1)
        radiansdelta = angle / n
        n += 1
    else:
        n = 1
        radiansdelta = 0
    for angle in xrange(n):
        angle = startangle + angle * radiansdelta
        a((centerx + radius * cos(angle), centery + yradius * sin(angle)))

    if reverse:
        points.reverse()
    return points


class ArcPath(Path):
    """Path with an addArc method"""

    def addArc(self, centerx, centery, radius, startangledegrees, endangledegrees, yradius=None, degreedelta=None, moveTo=None, reverse=None):
        P = getArcPoints(centerx, centery, radius, startangledegrees, endangledegrees, yradius=yradius, degreedelta=degreedelta, reverse=reverse)
        if moveTo or not len(self.operators):
            self.moveTo(P[0][0], P[0][1])
            del P[0]
        for x, y in P:
            self.lineTo(x, y)


def definePath(pathSegs=[], isClipPath=0, dx=0, dy=0, **kw):
    O = []
    P = []
    for seg in pathSegs:
        if type(seg) not in [ListType, TupleType]:
            opName = seg
            args = []
        else:
            opName = seg[0]
            args = seg[1:]
        if opName not in _PATH_OP_NAMES:
            raise ValueError, 'bad operator name %s' % opName
        op = _PATH_OP_NAMES.index(opName)
        if len(args) != _PATH_OP_ARG_COUNT[op]:
            raise ValueError, '%s bad arguments %s' % (opName, str(args))
        O.append(op)
        P.extend(list(args))

    for d, o in ((dx, 0), (dy, 1)):
        for i in xrange(o, len(P), 2):
            P[i] = P[i] + d

    return Path(P, O, isClipPath, **kw)


class Rect(SolidShape):
    """Rectangle, possibly with rounded corners."""
    _attrMap = AttrMap(BASE=SolidShape, x=AttrMapValue(isNumber), y=AttrMapValue(isNumber), width=AttrMapValue(isNumber, desc='width of the object in points'), height=AttrMapValue(isNumber, desc='height of the objects in points'), rx=AttrMapValue(isNumber), ry=AttrMapValue(isNumber))

    def __init__(self, x, y, width, height, rx=0, ry=0, **kw):
        SolidShape.__init__(self, kw)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry

    def copy(self):
        new = self.__class__(self.x, self.y, self.width, self.height)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return (
         self.x, self.y, self.x + self.width, self.y + self.height)


class Image(SolidShape):
    """Bitmap image."""
    _attrMap = AttrMap(BASE=SolidShape, x=AttrMapValue(isNumber), y=AttrMapValue(isNumber), width=AttrMapValue(isNumberOrNone, desc='width of the object in points'), height=AttrMapValue(isNumberOrNone, desc='height of the objects in points'), path=AttrMapValue(None))

    def __init__(self, x, y, width, height, path, **kw):
        SolidShape.__init__(self, kw)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = path

    def copy(self):
        new = self.__class__(self.x, self.y, self.width, self.height, self.path)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return (
         self.x, self.y, self.x + self.width, self.y + self.height)


class Circle(SolidShape):
    _attrMap = AttrMap(BASE=SolidShape, cx=AttrMapValue(isNumber, desc='x of the centre'), cy=AttrMapValue(isNumber, desc='y of the centre'), r=AttrMapValue(isNumber, desc='radius in points'))

    def __init__(self, cx, cy, r, **kw):
        SolidShape.__init__(self, kw)
        self.cx = cx
        self.cy = cy
        self.r = r

    def copy(self):
        new = self.__class__(self.cx, self.cy, self.r)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return (
         self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r)


class Ellipse(SolidShape):
    _attrMap = AttrMap(BASE=SolidShape, cx=AttrMapValue(isNumber, desc='x of the centre'), cy=AttrMapValue(isNumber, desc='y of the centre'), rx=AttrMapValue(isNumber, desc='x radius'), ry=AttrMapValue(isNumber, desc='y radius'))

    def __init__(self, cx, cy, rx, ry, **kw):
        SolidShape.__init__(self, kw)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry

    def copy(self):
        new = self.__class__(self.cx, self.cy, self.rx, self.ry)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return (
         self.cx - self.rx, self.cy - self.ry, self.cx + self.rx, self.cy + self.ry)


class Wedge(SolidShape):
    """A "slice of a pie" by default translates to a polygon moves anticlockwise
       from start angle to end angle"""
    _attrMap = AttrMap(BASE=SolidShape, centerx=AttrMapValue(isNumber, desc='x of the centre'), centery=AttrMapValue(isNumber, desc='y of the centre'), radius=AttrMapValue(isNumber, desc='radius in points'), startangledegrees=AttrMapValue(isNumber), endangledegrees=AttrMapValue(isNumber), yradius=AttrMapValue(isNumberOrNone), radius1=AttrMapValue(isNumberOrNone), yradius1=AttrMapValue(isNumberOrNone))
    degreedelta = 1

    def __init__(self, centerx, centery, radius, startangledegrees, endangledegrees, yradius=None, **kw):
        SolidShape.__init__(self, kw)
        while endangledegrees < startangledegrees:
            endangledegrees = endangledegrees + 360

        self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees = (
         centerx, centery, radius, startangledegrees, endangledegrees)
        self.yradius = yradius

    def _xtraRadii(self):
        yradius = getattr(self, 'yradius', None)
        if yradius is None:
            yradius = self.radius
        radius1 = getattr(self, 'radius1', None)
        yradius1 = getattr(self, 'yradius1', radius1)
        if radius1 is None:
            radius1 = yradius1
        return (
         yradius, radius1, yradius1)

    def asPolygon(self):
        centerx = self.centerx
        centery = self.centery
        radius = self.radius
        yradius, radius1, yradius1 = self._xtraRadii()
        startangledegrees = self.startangledegrees
        endangledegrees = self.endangledegrees
        from math import sin, cos, pi
        degreestoradians = pi / 180.0
        startangle = startangledegrees * degreestoradians
        endangle = endangledegrees * degreestoradians
        while endangle < startangle:
            endangle = endangle + 2 * pi

        angle = float(endangle - startangle)
        points = []
        if angle > 0.001:
            degreedelta = min(self.degreedelta or 1.0, angle)
            radiansdelta = degreedelta * degreestoradians
            n = max(1, int(angle / radiansdelta + 0.5))
            radiansdelta = angle / n
            n += 1
        else:
            n = 1
            radiansdelta = 0
        CA = []
        CAA = CA.append
        a = points.append
        for angle in xrange(n):
            angle = startangle + angle * radiansdelta
            CAA((cos(angle), sin(angle)))

        for c, s in CA:
            a(centerx + radius * c)
            a(centery + yradius * s)

        if (radius1 == 0 or radius1 is None) and (yradius1 == 0 or yradius1 is None):
            a(centerx)
            a(centery)
        else:
            CA.reverse()
            for c, s in CA:
                a(centerx + radius1 * c)
                a(centery + yradius1 * s)

        return Polygon(points)

    def copy(self):
        new = self.__class__(self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return self.asPolygon().getBounds()


class Polygon(SolidShape):
    """Defines a closed shape; Is implicitly
    joined back to the start for you."""
    _attrMap = AttrMap(BASE=SolidShape, points=AttrMapValue(isListOfNumbers, desc='list of numbers in the form x1, y1, x2, y2 ... xn, yn'))

    def __init__(self, points=[], **kw):
        SolidShape.__init__(self, kw)
        assert len(points) % 2 == 0, 'Point list must have even number of elements!'
        self.points = points or []

    def copy(self):
        new = self.__class__(self.points)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return getPointsBounds(self.points)


class PolyLine(LineShape):
    """Series of line segments.  Does not define a
    closed shape; never filled even if apparently joined.
    Put the numbers in the list, not two-tuples."""
    _attrMap = AttrMap(BASE=LineShape, points=AttrMapValue(isListOfNumbers, desc='list of numbers in the form x1, y1, x2, y2 ... xn, yn'))

    def __init__(self, points=[], **kw):
        LineShape.__init__(self, kw)
        points = points or []
        lenPoints = len(points)
        if lenPoints:
            if type(points[0]) in (ListType, TupleType):
                L = []
                for x, y in points:
                    L.append(x)
                    L.append(y)

                points = L
            else:
                assert len(points) % 2 == 0, 'Point list must have even number of elements!'
        self.points = points

    def copy(self):
        new = self.__class__(self.points)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        return getPointsBounds(self.points)


def numericXShift(tA, text, w, fontName, fontSize, encoding=None, pivotCharacter='.'):
    dp = getattr(tA, '_dp', pivotCharacter)
    i = text.rfind(dp)
    if i >= 0:
        dpOffs = getattr(tA, '_dpLen', 0)
        w = dpOffs + stringWidth(text[:i], fontName, fontSize, encoding)
    return w


class String(Shape):
    """Not checked against the spec, just a way to make something work.
    Can be anchored left, middle or end."""
    _attrMap = AttrMap(x=AttrMapValue(isNumber, desc='x point of anchoring'), y=AttrMapValue(isNumber, desc='y point of anchoring'), text=AttrMapValue(isString, desc='the text of the string'), fontName=AttrMapValue(None, desc='font name of the text - font is either acrobat standard or registered when using external font.'), fontSize=AttrMapValue(isNumber, desc='font size'), fillColor=AttrMapValue(isColorOrNone, desc='color of the font'), textAnchor=AttrMapValue(OneOf('start', 'middle', 'end', 'numeric'), desc='treat (x,y) as one of the options below.'), encoding=AttrMapValue(isString))
    encoding = 'utf8'

    def __init__(self, x, y, text, **kw):
        self.x = x
        self.y = y
        self.text = text
        self.textAnchor = 'start'
        self.fontName = STATE_DEFAULTS['fontName']
        self.fontSize = STATE_DEFAULTS['fontSize']
        self.fillColor = STATE_DEFAULTS['fillColor']
        self.setProperties(kw)

    def getEast(self):
        return self.x + stringWidth(self.text, self.fontName, self.fontSize, self.encoding)

    def copy(self):
        new = self.__class__(self.x, self.y, self.text)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self):
        t = self.text
        w = stringWidth(t, self.fontName, self.fontSize, self.encoding)
        tA = self.textAnchor
        x = self.x
        if tA != 'start':
            if tA == 'middle':
                x -= 0.5 * w
            else:
                if tA == 'end':
                    x -= w
                elif tA == 'numeric':
                    x -= numericXShift(tA, t, w, self.fontName, self.fontSize, self.encoding)
        return (
         x, self.y - 0.2 * self.fontSize, x + w, self.y + self.fontSize)


class UserNode(_DrawTimeResizeable):
    """A simple template for creating a new node.  The user (Python
    programmer) may subclasses this.  provideNode() must be defined to
    provide a Shape primitive when called by a renderer.  It does
    NOT inherit from Shape, as the renderer always replaces it, and
    your own classes can safely inherit from it without getting
    lots of unintended behaviour."""

    def provideNode(self):
        """Override this to create your own node. This lets widgets be
        added to drawings; they must create a shape (typically a group)
        so that the renderer can draw the custom node."""
        raise NotImplementedError, 'this method must be redefined by the user/programmer'


def test():
    r = Rect(10, 10, 200, 50)
    import pprint
    pp = pprint.pprint
    print 'a Rectangle:'
    pp(r.getProperties())
    print
    print 'verifying...',
    r.verify()
    print 'OK'
    print 'deleting rect.width'
    del r.width
    print 'verifying...',
    r.verify()


if __name__ == '__main__':
    test()