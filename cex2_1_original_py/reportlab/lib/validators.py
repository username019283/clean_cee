# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\validators.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = 'Standard verifying functions used by attrmap.'
import string, sys, codecs
from ..types import *
_SequenceTypes = (
 ListType, TupleType)
_NumberTypes = (FloatType, IntType)
from reportlab.lib import colors
if sys.hexversion < 33751040:
    True = 1
    False = 0

class Percentage(float):
    pass


class Validator:
    """base validator class"""

    def __call__(self, x):
        return self.test(x)

    def __str__(self):
        return getattr(self, '_str', self.__class__.__name__)

    def normalize(self, x):
        return x

    def normalizeTest(self, x):
        try:
            self.normalize(x)
            return True
        except:
            return False


class _isAnything(Validator):

    def test(self, x):
        return True


class _isNothing(Validator):

    def test(self, x):
        return False


class _isBoolean(Validator):
    if sys.hexversion >= 33751040:

        def test(self, x):
            if type(x) in (IntType, BooleanType):
                return x in (0, 1)
            return self.normalizeTest(x)

    else:

        def test(self, x):
            if type(x) is IntType:
                return x in (0, 1)
            return self.normalizeTest(x)

    def normalize(self, x):
        if x in (0, 1):
            return x
        else:
            try:
                S = string.upper(x)
            except:
                raise ValueError, 'Must be boolean'

            if S in ('YES', 'TRUE'):
                return True
            if S in ('NO', 'FALSE', None):
                return False
            raise ValueError, 'Must be boolean'
            return


class _isString(Validator):

    def test(self, x):
        return isinstance(x, (str, unicode))


class _isCodec(Validator):

    def test(self, x):
        if type(x) not in (StringType, UnicodeType):
            return False
        try:
            a, b, c, d = codecs.lookup(x)
            return True
        except LookupError:
            return False


class _isNumber(Validator):

    def test(self, x):
        if type(x) in _NumberTypes:
            return True
        return self.normalizeTest(x)

    def normalize(self, x):
        try:
            return float(x)
        except:
            return int(x)


class _isInt(Validator):

    def test(self, x):
        if type(x) not in (IntType, StringType):
            return False
        return self.normalizeTest(x)

    def normalize(self, x):
        return int(x)


class _isNumberOrNone(_isNumber):

    def test(self, x):
        return x is None or isNumber(x)

    def normalize(self, x):
        if x is None:
            return x
        else:
            return _isNumber.normalize(x)


class _isListOfNumbersOrNone(Validator):
    """ListOfNumbersOrNone validator class."""

    def test(self, x):
        if x is None:
            return True
        else:
            return isListOfNumbers(x)


class isNumberInRange(_isNumber):

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def test(self, x):
        try:
            n = self.normalize(x)
            if self.min <= n <= self.max:
                return True
        except ValueError:
            pass

        return False


class _isListOfShapes(Validator):
    """ListOfShapes validator class."""

    def test(self, x):
        from reportlab.graphics.shapes import Shape
        if type(x) in _SequenceTypes:
            answer = 1
            for e in x:
                if not isinstance(e, Shape):
                    answer = 0

            return answer
        return False


class _isListOfStringsOrNone(Validator):
    """ListOfStringsOrNone validator class."""

    def test(self, x):
        if x is None:
            return True
        else:
            return isListOfStrings(x)


class _isTransform(Validator):
    """Transform validator class."""

    def test(self, x):
        if type(x) in _SequenceTypes:
            if len(x) == 6:
                for element in x:
                    if not isNumber(element):
                        return False

                return True
            return False
        else:
            return False


class _isColor(Validator):
    """Color validator class."""

    def test(self, x):
        return isinstance(x, colors.Color)


class _isColorOrNone(Validator):
    """ColorOrNone validator class."""

    def test(self, x):
        if x is None:
            return True
        else:
            return isColor(x)


from reportlab.lib.normalDate import NormalDate

class _isNormalDate(Validator):

    def test(self, x):
        if isinstance(x, NormalDate):
            return True
        else:
            return x is not None and self.normalizeTest(x)

    def normalize(self, x):
        return NormalDate(x)


class _isValidChild(Validator):
    """ValidChild validator class."""

    def test(self, x):
        """Is this child allowed in a drawing or group?
        I.e. does it descend from Shape or UserNode?
        """
        from reportlab.graphics.shapes import UserNode, Shape
        return isinstance(x, UserNode) or isinstance(x, Shape)


class _isValidChildOrNone(_isValidChild):

    def test(self, x):
        return _isValidChild.test(self, x) or x is None


class _isCallable(Validator):

    def test(self, x):
        return hasattr(x, '__call__')


class OneOf(Validator):
    """Make validator functions for list of choices.

    Usage:
    f = reportlab.lib.validators.OneOf('happy','sad')
    or
    f = reportlab.lib.validators.OneOf(('happy','sad'))
    f('sad'),f('happy'), f('grumpy')
    (1,1,0)
    """

    def __init__(self, enum, *args):
        if type(enum) in [ListType, TupleType]:
            if args != ():
                raise ValueError, 'Either all singleton args or a single sequence argument'
            self._enum = tuple(enum) + args
        else:
            self._enum = (
             enum,) + args

    def test(self, x):
        return x in self._enum


class SequenceOf(Validator):

    def __init__(self, elemTest, name=None, emptyOK=1, NoneOK=0, lo=0, hi=2147483647):
        self._elemTest = elemTest
        self._emptyOK = emptyOK
        self._NoneOK = NoneOK
        self._lo, self._hi = lo, hi
        if name:
            self._str = name

    def test(self, x):
        if type(x) not in _SequenceTypes:
            if x is None:
                return self._NoneOK
            return False
        if x == [] or x == ():
            return self._emptyOK
        else:
            if not self._lo <= len(x) <= self._hi:
                return False
            for e in x:
                if not self._elemTest(e):
                    return False

            return True


class EitherOr(Validator):

    def __init__(self, tests, name=None):
        if type(tests) not in _SequenceTypes:
            tests = (tests,)
        self._tests = tests
        if name:
            self._str = name

    def test(self, x):
        for t in self._tests:
            if t(x):
                return True

        return False


class NoneOr(Validator):

    def __init__(self, elemTest, name=None):
        self._elemTest = elemTest
        if name:
            self._str = name

    def test(self, x):
        if x is None:
            return True
        else:
            return self._elemTest(x)


class Auto(Validator):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def test(self, x):
        return x is self.__class__ or isinstance(x, self.__class__)


class AutoOr(NoneOr):

    def test(self, x):
        return isAuto(x) or self._elemTest(x)


class isInstanceOf(Validator):

    def __init__(self, klass=None):
        self._klass = klass

    def test(self, x):
        return isinstance(x, self._klass)


class matchesPattern(Validator):
    """Matches value, or its string representation, against regex"""

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def test(self, x):
        print 'testing %s against %s' % (x, self._pattern)
        if type(x) is StringType:
            text = x
        else:
            text = str(x)
        return self._pattern.match(text) != None


class DerivedValue:
    """This is used for magic values which work themselves out.
    An example would be an "inherit" property, so that one can have

      drawing.chart.categoryAxis.labels.fontName = inherit

    and pick up the value from the top of the drawing.
    Validators will permit this provided that a value can be pulled
    in which satisfies it.  And the renderer will have special
    knowledge of these so they can evaluate themselves.
    """

    def getValue(self, renderer, attr):
        """Override this.  The renderers will pass the renderer,
        and the attribute name.  Algorithms can then backtrack up
        through all the stuff the renderer provides, including
        a correct stack of parent nodes."""
        return


class Inherit(DerivedValue):

    def __repr__(self):
        return 'inherit'

    def getValue(self, renderer, attr):
        return renderer.getStateValue(attr)


inherit = Inherit()

class NumericAlign(str):
    """for creating the numeric string value for anchors etc etc
    dp is the character to align on (the last occurrence will be used)
    dpLen is the length of characters after the dp
    """

    def __new__(cls, dp='.', dpLen=0):
        self = str.__new__(cls, 'numeric')
        self._dp = dp
        self._dpLen = dpLen
        return self


isAuto = Auto()
isBoolean = _isBoolean()
isString = _isString()
isCodec = _isCodec()
isNumber = _isNumber()
isInt = _isInt()
isNoneOrInt = NoneOr(isInt, 'isNoneOrInt')
isNumberOrNone = _isNumberOrNone()
isTextAnchor = OneOf('start', 'middle', 'end', 'boxauto')
isListOfNumbers = SequenceOf(isNumber, 'isListOfNumbers')
isListOfNumbersOrNone = _isListOfNumbersOrNone()
isListOfShapes = _isListOfShapes()
isListOfStrings = SequenceOf(isString, 'isListOfStrings')
isListOfStringsOrNone = _isListOfStringsOrNone()
isTransform = _isTransform()
isColor = _isColor()
isListOfColors = SequenceOf(isColor, 'isListOfColors')
isColorOrNone = _isColorOrNone()
isShape = isValidChild = _isValidChild()
isNoneOrShape = isValidChildOrNone = _isValidChildOrNone()
isAnything = _isAnything()
isNothing = _isNothing()
isXYCoord = SequenceOf(isNumber, lo=2, hi=2, emptyOK=0)
isBoxAnchor = OneOf('nw', 'n', 'ne', 'w', 'c', 'e', 'sw', 's', 'se', 'autox', 'autoy')
isNoneOrString = NoneOr(isString, 'NoneOrString')
isNoneOrListOfNoneOrStrings = SequenceOf(isNoneOrString, 'isNoneOrListOfNoneOrStrings', NoneOK=1)
isListOfNoneOrString = SequenceOf(isNoneOrString, 'isListOfNoneOrString', NoneOK=0)
isNoneOrListOfNoneOrNumbers = SequenceOf(isNumberOrNone, 'isNoneOrListOfNoneOrNumbers', NoneOK=1)
isCallable = _isCallable()
isNoneOrCallable = NoneOr(isCallable)
isStringOrCallable = EitherOr((isString, isCallable), 'isStringOrCallable')
isStringOrCallableOrNone = NoneOr(isStringOrCallable, 'isStringOrCallableNone')
isStringOrNone = NoneOr(isString, 'isStringOrNone')
isNormalDate = _isNormalDate()