# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\core\arrayprint.pyc
# Compiled at: 2013-04-07 07:04:04
"""Array printing function

$Id: arrayprint.py,v 1.9 2005/09/13 13:58:44 teoliphant Exp $
"""
__all__ = [
 'array2string', 'set_printoptions', 'get_printoptions']
__docformat__ = 'restructuredtext'
import sys, numerictypes as _nt
from umath import maximum, minimum, absolute, not_equal, isnan, isinf
from multiarray import format_longfloat, datetime_as_string, datetime_data
from fromnumeric import ravel

def product(x, y):
    return x * y


_summaryEdgeItems = 3
_summaryThreshold = 1000
_float_output_precision = 8
_float_output_suppress_small = False
_line_width = 75
_nan_str = 'nan'
_inf_str = 'inf'
_formatter = None
if sys.version_info[0] >= 3:
    from functools import reduce

def set_printoptions(precision=None, threshold=None, edgeitems=None, linewidth=None, suppress=None, nanstr=None, infstr=None, formatter=None):
    """
    Set printing options.

    These options determine the way floating point numbers, arrays and
    other NumPy objects are displayed.

    Parameters
    ----------
    precision : int, optional
        Number of digits of precision for floating point output (default 8).
    threshold : int, optional
        Total number of array elements which trigger summarization
        rather than full repr (default 1000).
    edgeitems : int, optional
        Number of array items in summary at beginning and end of
        each dimension (default 3).
    linewidth : int, optional
        The number of characters per line for the purpose of inserting
        line breaks (default 75).
    suppress : bool, optional
        Whether or not suppress printing of small floating point values
        using scientific notation (default False).
    nanstr : str, optional
        String representation of floating point not-a-number (default nan).
    infstr : str, optional
        String representation of floating point infinity (default inf).
    formatter : dict of callables, optional
        If not None, the keys should indicate the type(s) that the respective
        formatting function applies to.  Callables should return a string.
        Types that are not specified (by their corresponding keys) are handled
        by the default formatters.  Individual types for which a formatter
        can be set are::

            - 'bool'
            - 'int'
            - 'timedelta' : a `numpy.timedelta64`
            - 'datetime' : a `numpy.datetime64`
            - 'float'
            - 'longfloat' : 128-bit floats
            - 'complexfloat'
            - 'longcomplexfloat' : composed of two 128-bit floats
            - 'numpy_str' : types `numpy.string_` and `numpy.unicode_`
            - 'str' : all other strings

        Other keys that can be used to set a group of types at once are::

            - 'all' : sets all types
            - 'int_kind' : sets 'int'
            - 'float_kind' : sets 'float' and 'longfloat'
            - 'complex_kind' : sets 'complexfloat' and 'longcomplexfloat'
            - 'str_kind' : sets 'str' and 'numpystr'

    See Also
    --------
    get_printoptions, set_string_function, array2string

    Notes
    -----
    `formatter` is always reset with a call to `set_printoptions`.

    Examples
    --------
    Floating point precision can be set:

    >>> np.set_printoptions(precision=4)
    >>> print np.array([1.123456789])
    [ 1.1235]

    Long arrays can be summarised:

    >>> np.set_printoptions(threshold=5)
    >>> print np.arange(10)
    [0 1 2 ..., 7 8 9]

    Small results can be suppressed:

    >>> eps = np.finfo(float).eps
    >>> x = np.arange(4.)
    >>> x**2 - (x + eps)**2
    array([ -4.9304e-32,  -4.4409e-16,   0.0000e+00,   0.0000e+00])
    >>> np.set_printoptions(suppress=True)
    >>> x**2 - (x + eps)**2
    array([-0., -0.,  0.,  0.])

    A custom formatter can be used to display array elements as desired:

    >>> np.set_printoptions(formatter={'all':lambda x: 'int: '+str(-x)})
    >>> x = np.arange(3)
    >>> x
    array([int: 0, int: -1, int: -2])
    >>> np.set_printoptions()  # formatter gets reset
    >>> x
    array([0, 1, 2])

    To put back the default options, you can use:

    >>> np.set_printoptions(edgeitems=3,infstr='inf',
    ... linewidth=75, nanstr='nan', precision=8,
    ... suppress=False, threshold=1000, formatter=None)
    """
    global _float_output_precision
    global _float_output_suppress_small
    global _formatter
    global _inf_str
    global _line_width
    global _nan_str
    global _summaryEdgeItems
    global _summaryThreshold
    if linewidth is not None:
        _line_width = linewidth
    if threshold is not None:
        _summaryThreshold = threshold
    if edgeitems is not None:
        _summaryEdgeItems = edgeitems
    if precision is not None:
        _float_output_precision = precision
    if suppress is not None:
        _float_output_suppress_small = not not suppress
    if nanstr is not None:
        _nan_str = nanstr
    if infstr is not None:
        _inf_str = infstr
    _formatter = formatter
    return


def get_printoptions():
    """
    Return the current print options.

    Returns
    -------
    print_opts : dict
        Dictionary of current print options with keys

          - precision : int
          - threshold : int
          - edgeitems : int
          - linewidth : int
          - suppress : bool
          - nanstr : str
          - infstr : str
          - formatter : dict of callables

        For a full description of these options, see `set_printoptions`.

    See Also
    --------
    set_printoptions, set_string_function

    """
    d = dict(precision=_float_output_precision, threshold=_summaryThreshold, edgeitems=_summaryEdgeItems, linewidth=_line_width, suppress=_float_output_suppress_small, nanstr=_nan_str, infstr=_inf_str, formatter=_formatter)
    return d


def _leading_trailing(a):
    import numeric as _nc
    if a.ndim == 1:
        if len(a) > 2 * _summaryEdgeItems:
            b = _nc.concatenate((a[:_summaryEdgeItems],
             a[-_summaryEdgeItems:]))
        else:
            b = a
    else:
        if len(a) > 2 * _summaryEdgeItems:
            l = [ _leading_trailing(a[i]) for i in range(min(len(a), _summaryEdgeItems)) ]
            l.extend([ _leading_trailing(a[-i]) for i in range(min(len(a), _summaryEdgeItems), 0, -1)
                     ])
        else:
            l = [ _leading_trailing(a[i]) for i in range(0, len(a)) ]
        b = _nc.concatenate(tuple(l))
    return b


def _boolFormatter(x):
    if x:
        return ' True'
    else:
        return 'False'


def repr_format(x):
    return repr(x)


def _array2string(a, max_line_width, precision, suppress_small, separator=' ', prefix='', formatter=None):
    if max_line_width is None:
        max_line_width = _line_width
    if precision is None:
        precision = _float_output_precision
    if suppress_small is None:
        suppress_small = _float_output_suppress_small
    if formatter is None:
        formatter = _formatter
    if a.size > _summaryThreshold:
        summary_insert = '..., '
        data = _leading_trailing(a)
    else:
        summary_insert = ''
        data = ravel(a)
    formatdict = {'bool': _boolFormatter, 'int': IntegerFormat(data), 
       'float': FloatFormat(data, precision, suppress_small), 
       'longfloat': LongFloatFormat(precision), 
       'complexfloat': ComplexFormat(data, precision, suppress_small), 
       'longcomplexfloat': LongComplexFormat(precision), 
       'datetime': DatetimeFormat(data), 
       'timedelta': TimedeltaFormat(data), 
       'numpystr': repr_format, 
       'str': str}
    if formatter is not None:
        fkeys = [ k for k in formatter.keys() if formatter[k] is not None ]
        if 'all' in fkeys:
            for key in formatdict.keys():
                formatdict[key] = formatter['all']

        if 'int_kind' in fkeys:
            for key in ['int']:
                formatdict[key] = formatter['int_kind']

        if 'float_kind' in fkeys:
            for key in ['float', 'longfloat']:
                formatdict[key] = formatter['float_kind']

        if 'complex_kind' in fkeys:
            for key in ['complexfloat', 'longcomplexfloat']:
                formatdict[key] = formatter['complex_kind']

        if 'str_kind' in fkeys:
            for key in ['numpystr', 'str']:
                formatdict[key] = formatter['str_kind']

        for key in formatdict.keys():
            if key in fkeys:
                formatdict[key] = formatter[key]

    try:
        format_function = a._format
        msg = 'The `_format` attribute is deprecated in Numpy 2.0 and will be removed in 2.1. Use the `formatter` kw instead.'
        import warnings
        warnings.warn(msg, DeprecationWarning)
    except AttributeError:
        dtypeobj = a.dtype.type
        if issubclass(dtypeobj, _nt.bool_):
            format_function = formatdict['bool']
        else:
            if issubclass(dtypeobj, _nt.integer):
                if issubclass(dtypeobj, _nt.timedelta64):
                    format_function = formatdict['timedelta']
                else:
                    format_function = formatdict['int']
            else:
                if issubclass(dtypeobj, _nt.floating):
                    if issubclass(dtypeobj, _nt.longfloat):
                        format_function = formatdict['longfloat']
                    else:
                        format_function = formatdict['float']
                elif issubclass(dtypeobj, _nt.complexfloating):
                    if issubclass(dtypeobj, _nt.clongfloat):
                        format_function = formatdict['longcomplexfloat']
                    else:
                        format_function = formatdict['complexfloat']
        if issubclass(dtypeobj, (_nt.unicode_, _nt.string_)):
            format_function = formatdict['numpystr']
        else:
            if issubclass(dtypeobj, _nt.datetime64):
                format_function = formatdict['datetime']
            else:
                format_function = formatdict['numpystr']

    next_line_prefix = ' '
    next_line_prefix += ' ' * len(prefix)
    lst = _formatArray(a, format_function, len(a.shape), max_line_width, next_line_prefix, separator, _summaryEdgeItems, summary_insert)[:-1]
    return lst


def _convert_arrays(obj):
    import numeric as _nc
    newtup = []
    for k in obj:
        if isinstance(k, _nc.ndarray):
            k = k.tolist()
        elif isinstance(k, tuple):
            k = _convert_arrays(k)
        newtup.append(k)

    return tuple(newtup)


def array2string(a, max_line_width=None, precision=None, suppress_small=None, separator=' ', prefix='', style=repr, formatter=None):
    """
    Return a string representation of an array.

    Parameters
    ----------
    a : ndarray
        Input array.
    max_line_width : int, optional
        The maximum number of columns the string should span. Newline
        characters splits the string appropriately after array elements.
    precision : int, optional
        Floating point precision. Default is the current printing
        precision (usually 8), which can be altered using `set_printoptions`.
    suppress_small : bool, optional
        Represent very small numbers as zero. A number is "very small" if it
        is smaller than the current printing precision.
    separator : str, optional
        Inserted between elements.
    prefix : str, optional
        An array is typically printed as::

          'prefix(' + array2string(a) + ')'

        The length of the prefix string is used to align the
        output correctly.
    style : function, optional
        A function that accepts an ndarray and returns a string.  Used only
        when the shape of `a` is equal to ``()``, i.e. for 0-D arrays.
    formatter : dict of callables, optional
        If not None, the keys should indicate the type(s) that the respective
        formatting function applies to.  Callables should return a string.
        Types that are not specified (by their corresponding keys) are handled
        by the default formatters.  Individual types for which a formatter
        can be set are::

            - 'bool'
            - 'int'
            - 'timedelta' : a `numpy.timedelta64`
            - 'datetime' : a `numpy.datetime64`
            - 'float'
            - 'longfloat' : 128-bit floats
            - 'complexfloat'
            - 'longcomplexfloat' : composed of two 128-bit floats
            - 'numpy_str' : types `numpy.string_` and `numpy.unicode_`
            - 'str' : all other strings

        Other keys that can be used to set a group of types at once are::

            - 'all' : sets all types
            - 'int_kind' : sets 'int'
            - 'float_kind' : sets 'float' and 'longfloat'
            - 'complex_kind' : sets 'complexfloat' and 'longcomplexfloat'
            - 'str_kind' : sets 'str' and 'numpystr'

    Returns
    -------
    array_str : str
        String representation of the array.

    Raises
    ------
    TypeError : if a callable in `formatter` does not return a string.

    See Also
    --------
    array_str, array_repr, set_printoptions, get_printoptions

    Notes
    -----
    If a formatter is specified for a certain type, the `precision` keyword is
    ignored for that type.

    Examples
    --------
    >>> x = np.array([1e-16,1,2,3])
    >>> print np.array2string(x, precision=2, separator=',',
    ...                       suppress_small=True)
    [ 0., 1., 2., 3.]

    >>> x  = np.arange(3.)
    >>> np.array2string(x, formatter={'float_kind':lambda x: "%.2f" % x})
    '[0.00 1.00 2.00]'

    >>> x  = np.arange(3)
    >>> np.array2string(x, formatter={'int':lambda x: hex(x)})
    '[0x0L 0x1L 0x2L]'

    """
    if a.shape == ():
        x = a.item()
        try:
            lst = a._format(x)
            msg = 'The `_format` attribute is deprecated in Numpy 2.0 and will be removed in 2.1. Use the `formatter` kw instead.'
            import warnings
            warnings.warn(msg, DeprecationWarning)
        except AttributeError:
            if isinstance(x, tuple):
                x = _convert_arrays(x)
            lst = style(x)

    elif reduce(product, a.shape) == 0:
        lst = '[]'
    else:
        lst = _array2string(a, max_line_width, precision, suppress_small, separator, prefix, formatter=formatter)
    return lst


def _extendLine(s, line, word, max_line_len, next_line_prefix):
    if len(line.rstrip()) + len(word.rstrip()) >= max_line_len:
        s += line.rstrip() + '\n'
        line = next_line_prefix
    line += word
    return (s, line)


def _formatArray(a, format_function, rank, max_line_len, next_line_prefix, separator, edge_items, summary_insert):
    """formatArray is designed for two modes of operation:

    1. Full output

    2. Summarized output

    """
    if rank == 0:
        obj = a.item()
        if isinstance(obj, tuple):
            obj = _convert_arrays(obj)
        return str(obj)
    if summary_insert and 2 * edge_items < len(a):
        leading_items, trailing_items, summary_insert1 = edge_items, edge_items, summary_insert
    else:
        leading_items, trailing_items, summary_insert1 = 0, len(a), ''
    if rank == 1:
        s = ''
        line = next_line_prefix
        for i in xrange(leading_items):
            word = format_function(a[i]) + separator
            s, line = _extendLine(s, line, word, max_line_len, next_line_prefix)

        if summary_insert1:
            s, line = _extendLine(s, line, summary_insert1, max_line_len, next_line_prefix)
        for i in xrange(trailing_items, 1, -1):
            word = format_function(a[-i]) + separator
            s, line = _extendLine(s, line, word, max_line_len, next_line_prefix)

        word = format_function(a[-1])
        s, line = _extendLine(s, line, word, max_line_len, next_line_prefix)
        s += line + ']\n'
        s = '[' + s[len(next_line_prefix):]
    else:
        s = '['
        sep = separator.rstrip()
        for i in xrange(leading_items):
            if i > 0:
                s += next_line_prefix
            s += _formatArray(a[i], format_function, rank - 1, max_line_len, ' ' + next_line_prefix, separator, edge_items, summary_insert)
            s = s.rstrip() + sep.rstrip() + '\n' * max(rank - 1, 1)

        if summary_insert1:
            s += next_line_prefix + summary_insert1 + '\n'
        for i in xrange(trailing_items, 1, -1):
            if leading_items or i != trailing_items:
                s += next_line_prefix
            s += _formatArray(a[-i], format_function, rank - 1, max_line_len, ' ' + next_line_prefix, separator, edge_items, summary_insert)
            s = s.rstrip() + sep.rstrip() + '\n' * max(rank - 1, 1)

        if leading_items or trailing_items > 1:
            s += next_line_prefix
        s += _formatArray(a[-1], format_function, rank - 1, max_line_len, ' ' + next_line_prefix, separator, edge_items, summary_insert).rstrip() + ']\n'
    return s


class FloatFormat(object):

    def __init__(self, data, precision, suppress_small, sign=False):
        self.precision = precision
        self.suppress_small = suppress_small
        self.sign = sign
        self.exp_format = False
        self.large_exponent = False
        self.max_str_len = 0
        try:
            self.fillFormat(data)
        except (TypeError, NotImplementedError):
            pass

    def fillFormat(self, data):
        import numeric as _nc
        errstate = _nc.seterr(all='ignore')
        try:
            special = isnan(data) | isinf(data)
            valid = not_equal(data, 0) & ~special
            non_zero = absolute(data.compress(valid))
            if len(non_zero) == 0:
                max_val = 0.0
                min_val = 0.0
            else:
                max_val = maximum.reduce(non_zero)
                min_val = minimum.reduce(non_zero)
                if max_val >= 100000000.0:
                    self.exp_format = True
                if not self.suppress_small and (min_val < 0.0001 or max_val / min_val > 1000.0):
                    self.exp_format = True
        finally:
            _nc.seterr(**errstate)

        if self.exp_format:
            self.large_exponent = 0 < min_val < 1e-99 or max_val >= 1e+100
            self.max_str_len = 8 + self.precision
            if self.large_exponent:
                self.max_str_len += 1
            if self.sign:
                format = '%+'
            else:
                format = '%'
            format = format + '%d.%de' % (self.max_str_len, self.precision)
        else:
            format = '%%.%df' % (self.precision,)
            if len(non_zero):
                precision = max([ _digits(x, self.precision, format) for x in non_zero
                                ])
            else:
                precision = 0
            precision = min(self.precision, precision)
            self.max_str_len = len(str(int(max_val))) + precision + 2
            if _nc.any(special):
                self.max_str_len = max(self.max_str_len, len(_nan_str), len(_inf_str) + 1)
            if self.sign:
                format = '%#+'
            else:
                format = '%#'
            format = format + '%d.%df' % (self.max_str_len, precision)
        self.special_fmt = '%%%ds' % (self.max_str_len,)
        self.format = format

    def __call__(self, x, strip_zeros=True):
        import numeric as _nc
        err = _nc.seterr(invalid='ignore')
        try:
            if isnan(x):
                if self.sign:
                    return self.special_fmt % ('+' + _nan_str,)
                else:
                    return self.special_fmt % (_nan_str,)

            elif isinf(x):
                if x > 0:
                    if self.sign:
                        return self.special_fmt % ('+' + _inf_str,)
                    else:
                        return self.special_fmt % (_inf_str,)

                else:
                    return self.special_fmt % ('-' + _inf_str,)
        finally:
            _nc.seterr(**err)

        s = self.format % x
        if self.large_exponent:
            expsign = s[-3]
            if expsign == '+' or expsign == '-':
                s = s[1:-2] + '0' + s[-2:]
        elif self.exp_format:
            if s[-3] == '0':
                s = ' ' + s[:-3] + s[-2:]
        elif strip_zeros:
            z = s.rstrip('0')
            s = z + ' ' * (len(s) - len(z))
        return s


def _digits(x, precision, format):
    s = format % x
    z = s.rstrip('0')
    return precision - len(s) + len(z)


_MAXINT = sys.maxint
_MININT = -sys.maxint - 1

class IntegerFormat(object):

    def __init__(self, data):
        try:
            max_str_len = max(len(str(maximum.reduce(data))), len(str(minimum.reduce(data))))
            self.format = '%' + str(max_str_len) + 'd'
        except (TypeError, NotImplementedError):
            pass
        except ValueError:
            pass

    def __call__(self, x):
        if _MININT < x < _MAXINT:
            return self.format % x
        else:
            return '%s' % x


class LongFloatFormat(object):

    def __init__(self, precision, sign=False):
        self.precision = precision
        self.sign = sign

    def __call__(self, x):
        if isnan(x):
            if self.sign:
                return '+' + _nan_str
            else:
                return ' ' + _nan_str

        elif isinf(x):
            if x > 0:
                if self.sign:
                    return '+' + _inf_str
                else:
                    return ' ' + _inf_str

            else:
                return '-' + _inf_str
        elif x >= 0:
            if self.sign:
                return '+' + format_longfloat(x, self.precision)
            else:
                return ' ' + format_longfloat(x, self.precision)

        else:
            return format_longfloat(x, self.precision)


class LongComplexFormat(object):

    def __init__(self, precision):
        self.real_format = LongFloatFormat(precision)
        self.imag_format = LongFloatFormat(precision, sign=True)

    def __call__(self, x):
        r = self.real_format(x.real)
        i = self.imag_format(x.imag)
        return r + i + 'j'


class ComplexFormat(object):

    def __init__(self, x, precision, suppress_small):
        self.real_format = FloatFormat(x.real, precision, suppress_small)
        self.imag_format = FloatFormat(x.imag, precision, suppress_small, sign=True)

    def __call__(self, x):
        r = self.real_format(x.real, strip_zeros=False)
        i = self.imag_format(x.imag, strip_zeros=False)
        if not self.imag_format.exp_format:
            z = i.rstrip('0')
            i = z + 'j' + ' ' * (len(i) - len(z))
        else:
            i = i + 'j'
        return r + i


class DatetimeFormat(object):

    def __init__(self, x, unit=None, timezone=None, casting='same_kind'):
        if unit is None:
            if x.dtype.kind == 'M':
                unit = datetime_data(x.dtype)[0]
            else:
                unit = 's'
        if timezone is None:
            if unit in ('Y', 'M', 'W', 'D'):
                self.timezone = 'UTC'
            else:
                self.timezone = 'local'
        else:
            self.timezone = timezone
        self.unit = unit
        self.casting = casting
        return

    def __call__(self, x):
        return "'%s'" % datetime_as_string(x, unit=self.unit, timezone=self.timezone, casting=self.casting)


class TimedeltaFormat(object):

    def __init__(self, data):
        if data.dtype.kind == 'm':
            v = data.view('i8')
            max_str_len = max(len(str(maximum.reduce(v))), len(str(minimum.reduce(v))))
            self.format = '%' + str(max_str_len) + 'd'

    def __call__(self, x):
        return self.format % x.astype('i8')