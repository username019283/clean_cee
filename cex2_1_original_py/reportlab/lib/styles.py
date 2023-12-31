# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\styles.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = "Classes for ParagraphStyle and similar things.\n\nA style is a collection of attributes, but with some extra features\nto allow 'inheritance' from a parent, and to ensure nobody makes\nchanges after construction.\n\nParagraphStyle shows all the attributes available for formatting\nparagraphs.\n\ngetSampleStyleSheet()  returns a stylesheet you can use for initial\ndevelopment, with a few basic heading and text styles.\n"
__all__ = ('PropertySet', 'ParagraphStyle', 'LineStyle', 'ListStyle', 'StyleSheet1',
           'getSampleStyleSheet')
from reportlab.lib.colors import white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
from reportlab.rl_config import canvas_basefontname as _baseFontName
_baseFontNameB = tt2ps(_baseFontName, 1, 0)
_baseFontNameI = tt2ps(_baseFontName, 0, 1)
_baseFontNameBI = tt2ps(_baseFontName, 1, 1)

class PropertySet:
    defaults = {}

    def __init__(self, name, parent=None, **kw):
        """When initialized, it copies the class defaults;
        then takes a copy of the attributes of the parent
        if any.  All the work is done in init - styles
        should cost little to use at runtime."""
        if not 'name' not in self.defaults:
            raise AssertionError("Class Defaults may not contain a 'name' attribute")
            assert 'parent' not in self.defaults, "Class Defaults may not contain a 'parent' attribute"
            assert parent and parent.__class__ == self.__class__, 'Parent style %s must have same class as new style %s' % (parent.__class__.__name__, self.__class__.__name__)
        self.name = name
        self.parent = parent
        self.__dict__.update(self.defaults)
        self.refresh()
        self._setKwds(**kw)

    def _setKwds(self, **kw):
        for key, value in kw.items():
            self.__dict__[key] = value

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

    def refresh(self):
        """re-fetches attributes from the parent on demand;
        use if you have been hacking the styles.  This is
        used by __init__"""
        if self.parent:
            for key, value in self.parent.__dict__.items():
                if key not in ('name', 'parent'):
                    self.__dict__[key] = value

    def listAttrs(self, indent=''):
        print indent + 'name =', self.name
        print indent + 'parent =', self.parent
        keylist = self.__dict__.keys()
        keylist.sort()
        keylist.remove('name')
        keylist.remove('parent')
        for key in keylist:
            value = self.__dict__.get(key, None)
            print indent + '%s = %s' % (key, value)

        return

    def clone(self, name, parent=None, **kwds):
        r = self.__class__(name, parent)
        r.__dict__ = self.__dict__.copy()
        r.parent = parent is None and self or parent
        r._setKwds(**kwds)
        return r


class ParagraphStyle(PropertySet):
    defaults = {'fontName': _baseFontName, 
       'fontSize': 10, 
       'leading': 12, 
       'leftIndent': 0, 
       'rightIndent': 0, 
       'firstLineIndent': 0, 
       'alignment': TA_LEFT, 
       'spaceBefore': 0, 
       'spaceAfter': 0, 
       'bulletFontName': _baseFontName, 
       'bulletFontSize': 10, 
       'bulletIndent': 0, 
       'textColor': black, 
       'backColor': None, 
       'wordWrap': None, 
       'borderWidth': 0, 
       'borderPadding': 0, 
       'borderColor': None, 
       'borderRadius': None, 
       'allowWidows': 1, 
       'allowOrphans': 0, 
       'textTransform': None, 
       'endDots': None}


class LineStyle(PropertySet):
    defaults = {'width': 1, 
       'color': black}

    def prepareCanvas(self, canvas):
        """You can ask a LineStyle to set up the canvas for drawing
        the lines."""
        canvas.setLineWidth(1)


class ListStyle(PropertySet):
    defaults = dict(leftIndent=18, rightIndent=0, bulletAlign='left', bulletType='1', bulletColor=black, bulletFontName='Helvetica', bulletFontSize=12, bulletOffsetY=0, bulletDedent='auto', bulletDir='ltr', bulletFormat=None, start=None)


_stylesheet1_undefined = object()

class StyleSheet1:
    """
    This may or may not be used.  The idea is to:
    
    1. slightly simplify construction of stylesheets;
    
    2. enforce rules to validate styles when added
       (e.g. we may choose to disallow having both
       'heading1' and 'Heading1' - actual rules are
       open to discussion);
       
    3. allow aliases and alternate style lookup
       mechanisms
       
    4. Have a place to hang style-manipulation
       methods (save, load, maybe support a GUI
       editor)
   
    Access is via getitem, so they can be
    compatible with plain old dictionaries.
    """

    def __init__(self):
        self.byName = {}
        self.byAlias = {}

    def __getitem__(self, key):
        try:
            return self.byAlias[key]
        except KeyError:
            try:
                return self.byName[key]
            except KeyError:
                raise KeyError("Style '%s' not found in stylesheet" % key)

    def get(self, key, default=_stylesheet1_undefined):
        try:
            return self[key]
        except KeyError:
            if default != _stylesheet1_undefined:
                return default
            raise

    def __contains__(self, key):
        return key in self.byAlias or key in self.byName

    def has_key(self, key):
        return key in self

    def add(self, style, alias=None):
        key = style.name
        if key in self.byName:
            raise KeyError("Style '%s' already defined in stylesheet" % key)
        if key in self.byAlias:
            raise KeyError("Style name '%s' is already an alias in stylesheet" % key)
        if alias:
            if alias in self.byName:
                raise KeyError("Style '%s' already defined in stylesheet" % alias)
            if alias in self.byAlias:
                raise KeyError("Alias name '%s' is already an alias in stylesheet" % alias)
        self.byName[key] = style
        if alias:
            self.byAlias[alias] = style

    def list(self):
        styles = self.byName.items()
        styles.sort()
        alii = {}
        for alias, style in self.byAlias.items():
            alii[style] = alias

        for name, style in styles:
            alias = alii.get(style, None)
            print name, alias
            style.listAttrs('    ')
            print

        return


def testStyles():
    pNormal = ParagraphStyle('Normal', None)
    pNormal.fontName = _baseFontName
    pNormal.fontSize = 12
    pNormal.leading = 14.4
    pNormal.listAttrs()
    print
    pPre = ParagraphStyle('Literal', pNormal)
    pPre.fontName = 'Courier'
    pPre.listAttrs()
    return (pNormal, pPre)


def getSampleStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='Normal', fontName=_baseFontName, fontSize=10, leading=12))
    stylesheet.add(ParagraphStyle(name='BodyText', parent=stylesheet['Normal'], spaceBefore=6))
    stylesheet.add(ParagraphStyle(name='Italic', parent=stylesheet['BodyText'], fontName=_baseFontNameI))
    stylesheet.add(ParagraphStyle(name='Heading1', parent=stylesheet['Normal'], fontName=_baseFontNameB, fontSize=18, leading=22, spaceAfter=6), alias='h1')
    stylesheet.add(ParagraphStyle(name='Title', parent=stylesheet['Normal'], fontName=_baseFontNameB, fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=6), alias='title')
    stylesheet.add(ParagraphStyle(name='Heading2', parent=stylesheet['Normal'], fontName=_baseFontNameB, fontSize=14, leading=18, spaceBefore=12, spaceAfter=6), alias='h2')
    stylesheet.add(ParagraphStyle(name='Heading3', parent=stylesheet['Normal'], fontName=_baseFontNameBI, fontSize=12, leading=14, spaceBefore=12, spaceAfter=6), alias='h3')
    stylesheet.add(ParagraphStyle(name='Heading4', parent=stylesheet['Normal'], fontName=_baseFontNameBI, fontSize=10, leading=12, spaceBefore=10, spaceAfter=4), alias='h4')
    stylesheet.add(ParagraphStyle(name='Heading5', parent=stylesheet['Normal'], fontName=_baseFontNameB, fontSize=9, leading=10.8, spaceBefore=8, spaceAfter=4), alias='h5')
    stylesheet.add(ParagraphStyle(name='Heading6', parent=stylesheet['Normal'], fontName=_baseFontNameB, fontSize=7, leading=8.4, spaceBefore=6, spaceAfter=2), alias='h6')
    stylesheet.add(ParagraphStyle(name='Bullet', parent=stylesheet['Normal'], firstLineIndent=0, spaceBefore=3), alias='bu')
    stylesheet.add(ParagraphStyle(name='Definition', parent=stylesheet['Normal'], firstLineIndent=0, leftIndent=36, bulletIndent=0, spaceBefore=6, bulletFontName=_baseFontNameBI), alias='df')
    stylesheet.add(ParagraphStyle(name='Code', parent=stylesheet['Normal'], fontName='Courier', fontSize=8, leading=8.8, firstLineIndent=0, leftIndent=36))
    return stylesheet