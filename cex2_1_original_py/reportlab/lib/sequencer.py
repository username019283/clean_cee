# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\sequencer.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = 'A Sequencer class counts things. It aids numbering and formatting lists.'
__all__ = ('Sequencer getSequencer setSequencer').split()
_RN_TEMPLATES = [
 0, 1, 9, 73, 10, 2, 17, 137, 1097, 11]
_RN_LETTERS = 'IVXLCDM'

def _format_I(value):
    if value < 0 or value > 3999:
        raise ValueError, 'illegal value'
    str = ''
    base = -1
    while value:
        value, index = divmod(value, 10)
        tmp = _RN_TEMPLATES[index]
        while tmp:
            tmp, index = divmod(tmp, 8)
            str = _RN_LETTERS[index + base] + str

        base = base + 2

    return str


def _format_i(num):
    return _format_I(num).lower()


def _format_123(num):
    """The simplest formatter"""
    return str(num)


def _format_ABC(num):
    """Uppercase.  Wraps around at 26."""
    n = (num - 1) % 26
    return chr(n + 65)


def _format_abc(num):
    """Lowercase.  Wraps around at 26."""
    n = (num - 1) % 26
    return chr(n + 97)


_type2formatter = {'I': _format_I, 
   'i': _format_i, 
   '1': _format_123, 
   'A': _format_ABC, 
   'a': _format_abc}

class _Counter:
    """Private class used by Sequencer.  Each counter
    knows its format, and the IDs of anything it
    resets, as well as its value. Starts at zero
    and increments just before you get the new value,
    so that it is still 'Chapter 5' and not 'Chapter 6'
    when you print 'Figure 5.1'"""

    def __init__(self):
        self._base = 0
        self._value = self._base
        self._formatter = _format_123
        self._resets = []

    def setFormatter(self, formatFunc):
        self._formatter = formatFunc

    def reset(self, value=None):
        if value:
            self._value = value
        else:
            self._value = self._base

    def next(self):
        self._value = self._value + 1
        v = self._value
        for counter in self._resets:
            counter.reset()

        return v

    def _this(self):
        return self._value

    def nextf(self):
        """Returns next value formatted"""
        return self._formatter(self.next())

    def thisf(self):
        return self._formatter(self._this())

    def chain(self, otherCounter):
        if otherCounter not in self._resets:
            self._resets.append(otherCounter)


class Sequencer:
    """Something to make it easy to number paragraphs, sections,
    images and anything else.  The features include registering
    new string formats for sequences, and 'chains' whereby
    some counters are reset when their parents.
    It keeps track of a number of
    'counters', which are created on request:
    Usage::
    
        >>> seq = layout.Sequencer()
        >>> seq.next('Bullets')
        1
        >>> seq.next('Bullets')
        2
        >>> seq.next('Bullets')
        3
        >>> seq.reset('Bullets')
        >>> seq.next('Bullets')
        1
        >>> seq.next('Figures')
        1
        >>>
    """

    def __init__(self):
        self._counters = {}
        self._formatters = {}
        self._reset()

    def _reset(self):
        self._counters.clear()
        self._formatters.clear()
        self._formatters.update({'1': _format_123, 
           'A': _format_ABC, 
           'a': _format_abc, 
           'I': _format_I, 
           'i': _format_i})
        d = dict(_counters=self._counters, _formatters=self._formatters)
        self.__dict__.clear()
        self.__dict__.update(d)
        self._defaultCounter = None
        return

    def _getCounter(self, counter=None):
        """Creates one if not present"""
        try:
            return self._counters[counter]
        except KeyError:
            cnt = _Counter()
            self._counters[counter] = cnt
            return cnt

    def _this(self, counter=None):
        """Retrieves counter value but does not increment. For
        new counters, sets base value to 1."""
        if not counter:
            counter = self._defaultCounter
        return self._getCounter(counter)._this()

    def next(self, counter=None):
        """Retrieves the numeric value for the given counter, then
        increments it by one.  New counters start at one."""
        if not counter:
            counter = self._defaultCounter
        return self._getCounter(counter).next()

    def thisf(self, counter=None):
        if not counter:
            counter = self._defaultCounter
        return self._getCounter(counter).thisf()

    def nextf(self, counter=None):
        """Retrieves the numeric value for the given counter, then
        increments it by one.  New counters start at one."""
        if not counter:
            counter = self._defaultCounter
        return self._getCounter(counter).nextf()

    def setDefaultCounter(self, default=None):
        """Changes the key used for the default"""
        self._defaultCounter = default

    def registerFormat(self, format, func):
        """Registers a new formatting function.  The funtion
        must take a number as argument and return a string;
        fmt is a short menmonic string used to access it."""
        self._formatters[format] = func

    def setFormat(self, counter, format):
        """Specifies that the given counter should use
        the given format henceforth."""
        func = self._formatters[format]
        self._getCounter(counter).setFormatter(func)

    def reset(self, counter=None, base=0):
        if not counter:
            counter = self._defaultCounter
        self._getCounter(counter)._value = base

    def chain(self, parent, child):
        p = self._getCounter(parent)
        c = self._getCounter(child)
        p.chain(c)

    def __getitem__(self, key):
        """Allows compact notation to support the format function.
        s['key'] gets current value, s['key+'] increments."""
        if key[-1:] == '+':
            counter = key[:-1]
            return self.nextf(counter)
        else:
            return self.thisf(key)

    def format(self, template):
        """The crowning jewels - formats multi-level lists."""
        return template % self

    def dump(self):
        """Write current state to stdout for diagnostics"""
        counters = self._counters.items()
        counters.sort()
        print 'Sequencer dump:'
        for key, counter in counters:
            print '    %s: value = %d, base = %d, format example = %s' % (
             key, counter._this(), counter._base, counter.thisf())


_sequencer = None

def getSequencer():
    global _sequencer
    if _sequencer is None:
        _sequencer = Sequencer()
    return _sequencer


def setSequencer(seq):
    global _sequencer
    s = _sequencer
    _sequencer = seq
    return s


def _reset():
    if _sequencer:
        _sequencer._reset()


from reportlab.rl_config import register_reset
register_reset(_reset)
del register_reset

def test():
    s = Sequencer()
    print 'Counting using default sequence: %d %d %d' % (s.next(), s.next(), s.next())
    print 'Counting Figures: Figure %d, Figure %d, Figure %d' % (
     s.next('figure'), s.next('figure'), s.next('figure'))
    print 'Back to default again: %d' % s.next()
    s.setDefaultCounter('list1')
    print 'Set default to list1: %d %d %d' % (s.next(), s.next(), s.next())
    s.setDefaultCounter()
    print 'Set default to None again: %d %d %d' % (s.next(), s.next(), s.next())
    print
    print 'Creating Appendix counter with format A, B, C...'
    s.setFormat('Appendix', 'A')
    print '    Appendix %s, Appendix %s, Appendix %s' % (
     s.nextf('Appendix'), s.nextf('Appendix'), s.nextf('Appendix'))

    def format_french(num):
        return ('un', 'deux', 'trois', 'quatre', 'cinq')[(num - 1) % 5]

    print
    print 'Defining a custom format with french words:'
    s.registerFormat('french', format_french)
    s.setFormat('FrenchList', 'french')
    print '   ',
    for i in range(1, 6):
        print s.nextf('FrenchList'),

    print
    print 'Chaining H1 and H2 - H2 goes back to one when H1 increases'
    s.chain('H1', 'H2')
    print '    H1 = %d' % s.next('H1')
    print '      H2 = %d' % s.next('H2')
    print '      H2 = %d' % s.next('H2')
    print '      H2 = %d' % s.next('H2')
    print '    H1 = %d' % s.next('H1')
    print '      H2 = %d' % s.next('H2')
    print '      H2 = %d' % s.next('H2')
    print '      H2 = %d' % s.next('H2')
    print
    print 'GetItem notation - append a plus to increment'
    print '    seq["Appendix"] = %s' % s['Appendix']
    print '    seq["Appendix+"] = %s' % s['Appendix+']
    print '    seq["Appendix+"] = %s' % s['Appendix+']
    print '    seq["Appendix"] = %s' % s['Appendix']
    print
    print 'Finally, string format notation for nested lists.  Cool!'
    print 'The expression ("Figure %(Chapter)s.%(Figure+)s" % seq) gives:'
    print '    Figure %(Chapter)s.%(Figure+)s' % s
    print '    Figure %(Chapter)s.%(Figure+)s' % s
    print '    Figure %(Chapter)s.%(Figure+)s' % s


if __name__ == '__main__':
    test()