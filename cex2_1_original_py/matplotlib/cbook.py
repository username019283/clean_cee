# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\cbook.pyc
# Compiled at: 2012-11-06 08:42:20
"""
A collection of utility functions and classes.  Many (but not all)
from the Python Cookbook -- hence the name cbook
"""
from __future__ import print_function
import datetime, errno
from functools import reduce
import glob, gzip, io, locale, os, re, subprocess, sys, threading, time, traceback, warnings
from weakref import ref, WeakKeyDictionary
import numpy as np, numpy.ma as ma
if sys.version_info[0] >= 3:
    import types
else:
    import new
if sys.version_info[0] >= 3:

    def unicode_safe(s):
        import matplotlib
        try:
            preferredencoding = locale.getpreferredencoding(matplotlib.rcParams['axes.formatter.use_locale']).strip()
            if not preferredencoding:
                preferredencoding = None
        except (ValueError, ImportError, AttributeError):
            preferredencoding = None

        if isinstance(s, bytes):
            if preferredencoding is None:
                return unicode(s)
            else:
                return unicode(s, preferredencoding)

        return s


else:

    def unicode_safe(s):
        import matplotlib
        try:
            preferredencoding = locale.getpreferredencoding(matplotlib.rcParams['axes.formatter.use_locale']).strip()
            if not preferredencoding:
                preferredencoding = None
        except (ValueError, ImportError, AttributeError):
            preferredencoding = None

        if preferredencoding is None:
            return unicode(s)
        else:
            return unicode(s, preferredencoding)
            return


class converter:
    """
    Base class for handling string -> python type with support for
    missing values
    """

    def __init__(self, missing='Null', missingval=None):
        self.missing = missing
        self.missingval = missingval

    def __call__(self, s):
        if s == self.missing:
            return self.missingval
        return s

    def is_missing(self, s):
        return not s.strip() or s == self.missing


class tostr(converter):
    """convert to string or None"""

    def __init__(self, missing='Null', missingval=''):
        converter.__init__(self, missing=missing, missingval=missingval)


class todatetime(converter):
    """convert to a datetime or None"""

    def __init__(self, fmt='%Y-%m-%d', missing='Null', missingval=None):
        """use a :func:`time.strptime` format string for conversion"""
        converter.__init__(self, missing, missingval)
        self.fmt = fmt

    def __call__(self, s):
        if self.is_missing(s):
            return self.missingval
        tup = time.strptime(s, self.fmt)
        return datetime.datetime(*tup[:6])


class todate(converter):
    """convert to a date or None"""

    def __init__(self, fmt='%Y-%m-%d', missing='Null', missingval=None):
        """use a :func:`time.strptime` format string for conversion"""
        converter.__init__(self, missing, missingval)
        self.fmt = fmt

    def __call__(self, s):
        if self.is_missing(s):
            return self.missingval
        tup = time.strptime(s, self.fmt)
        return datetime.date(*tup[:3])


class tofloat(converter):
    """convert to a float or None"""

    def __init__(self, missing='Null', missingval=None):
        converter.__init__(self, missing)
        self.missingval = missingval

    def __call__(self, s):
        if self.is_missing(s):
            return self.missingval
        return float(s)


class toint(converter):
    """convert to an int or None"""

    def __init__(self, missing='Null', missingval=None):
        converter.__init__(self, missing)

    def __call__(self, s):
        if self.is_missing(s):
            return self.missingval
        return int(s)


class _BoundMethodProxy(object):
    """
    Our own proxy object which enables weak references to bound and unbound
    methods and arbitrary callables. Pulls information about the function,
    class, and instance out of a bound method. Stores a weak reference to the
    instance to support garbage collection.

    @organization: IBM Corporation
    @copyright: Copyright (c) 2005, 2006 IBM Corporation
    @license: The BSD License

    Minor bugfixes by Michael Droettboom
    """

    def __init__(self, cb):
        try:
            try:
                self.inst = ref(cb.im_self)
            except TypeError:
                self.inst = None

            self.func = cb.im_func
            self.klass = cb.im_class
        except AttributeError:
            self.inst = None
            self.func = cb
            self.klass = None

        return

    def __getstate__(self):
        d = self.__dict__.copy()
        inst = d['inst']
        if inst is not None:
            d['inst'] = inst()
        return d

    def __setstate__(self, statedict):
        self.__dict__ = statedict
        inst = statedict['inst']
        if inst is not None:
            self.inst = ref(inst)
        return

    def __call__(self, *args, **kwargs):
        """
        Proxy for a call to the weak referenced object. Take
        arbitrary params to pass to the callable.

        Raises `ReferenceError`: When the weak reference refers to
        a dead object
        """
        if self.inst is not None and self.inst() is None:
            raise ReferenceError
        elif self.inst is not None:
            if sys.version_info[0] >= 3:
                mtd = types.MethodType(self.func, self.inst())
            else:
                mtd = new.instancemethod(self.func, self.inst(), self.klass)
        else:
            mtd = self.func
        return mtd(*args, **kwargs)

    def __eq__(self, other):
        """
        Compare the held function and instance with that held by
        another proxy.
        """
        try:
            if self.inst is None:
                return self.func == other.func and other.inst is None
            else:
                return self.func == other.func and self.inst() == other.inst()

        except Exception:
            return False

        return

    def __ne__(self, other):
        """
        Inverse of __eq__.
        """
        return not self.__eq__(other)


class CallbackRegistry:
    """
    Handle registering and disconnecting for a set of signals and
    callbacks:

        >>> def oneat(x):
        ...    print 'eat', x
        >>> def ondrink(x):
        ...    print 'drink', x

        >>> from matplotlib.cbook import CallbackRegistry
        >>> callbacks = CallbackRegistry()

        >>> id_eat = callbacks.connect('eat', oneat)
        >>> id_drink = callbacks.connect('drink', ondrink)

        >>> callbacks.process('drink', 123)
        drink 123
        >>> callbacks.process('eat', 456)
        eat 456
        >>> callbacks.process('be merry', 456) # nothing will be called
        >>> callbacks.disconnect(id_eat)
        >>> callbacks.process('eat', 456)      # nothing will be called

    In practice, one should always disconnect all callbacks when they
    are no longer needed to avoid dangling references (and thus memory
    leaks).  However, real code in matplotlib rarely does so, and due
    to its design, it is rather difficult to place this kind of code.
    To get around this, and prevent this class of memory leaks, we
    instead store weak references to bound methods only, so when the
    destination object needs to die, the CallbackRegistry won't keep
    it alive.  The Python stdlib weakref module can not create weak
    references to bound methods directly, so we need to create a proxy
    object to handle weak references to bound methods (or regular free
    functions).  This technique was shared by Peter Parente on his
    `"Mindtrove" blog
    <http://mindtrove.info/articles/python-weak-references/>`_.
    """

    def __init__(self, *args):
        if len(args):
            warnings.warn('CallbackRegistry no longer requires a list of callback types. Ignoring arguments', DeprecationWarning)
        self.callbacks = dict()
        self._cid = 0
        self._func_cid_map = {}

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.__init__()

    def connect(self, s, func):
        """
        register *func* to be called when a signal *s* is generated
        func will be called
        """
        self._func_cid_map.setdefault(s, WeakKeyDictionary())
        if func in self._func_cid_map[s]:
            return self._func_cid_map[s][func]
        self._cid += 1
        cid = self._cid
        self._func_cid_map[s][func] = cid
        self.callbacks.setdefault(s, dict())
        proxy = _BoundMethodProxy(func)
        self.callbacks[s][cid] = proxy
        return cid

    def disconnect(self, cid):
        """
        disconnect the callback registered with callback id *cid*
        """
        for eventname, callbackd in self.callbacks.items():
            try:
                del callbackd[cid]
            except KeyError:
                continue
            else:
                for key, value in self._func_cid_map.items():
                    if value == cid:
                        del self._func_cid_map[key]

                return

    def process(self, s, *args, **kwargs):
        r"""
        process signal *s*.  All of the functions registered to receive
        callbacks on *s* will be called with *\*args* and *\*\*kwargs*
        """
        if s in self.callbacks:
            for cid, proxy in self.callbacks[s].items():
                if proxy.inst is not None and proxy.inst() is None:
                    del self.callbacks[s][cid]
                else:
                    proxy(*args, **kwargs)

        return


class Scheduler(threading.Thread):
    """
    Base class for timeout and idle scheduling
    """
    idlelock = threading.Lock()
    id = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.id = Scheduler.id
        self._stopped = False
        Scheduler.id += 1
        self._stopevent = threading.Event()

    def stop(self):
        if self._stopped:
            return
        self._stopevent.set()
        self.join()
        self._stopped = True


class Timeout(Scheduler):
    """
    Schedule recurring events with a wait time in seconds
    """

    def __init__(self, wait, func):
        Scheduler.__init__(self)
        self.wait = wait
        self.func = func

    def run(self):
        while not self._stopevent.isSet():
            self._stopevent.wait(self.wait)
            Scheduler.idlelock.acquire()
            b = self.func(self)
            Scheduler.idlelock.release()
            if not b:
                break


class Idle(Scheduler):
    """
    Schedule callbacks when scheduler is idle
    """
    waittime = 0.05

    def __init__(self, func):
        Scheduler.__init__(self)
        self.func = func

    def run(self):
        while not self._stopevent.isSet():
            self._stopevent.wait(Idle.waittime)
            Scheduler.idlelock.acquire()
            b = self.func(self)
            Scheduler.idlelock.release()
            if not b:
                break


class silent_list(list):
    """
    override repr when returning a list of matplotlib artists to
    prevent long, meaningless output.  This is meant to be used for a
    homogeneous list of a given type
    """

    def __init__(self, type, seq=None):
        self.type = type
        if seq is not None:
            self.extend(seq)
        return

    def __repr__(self):
        return '<a list of %d %s objects>' % (len(self), self.type)

    def __str__(self):
        return repr(self)

    def __getstate__(self):
        return {'type': self.type, 'seq': self[:]}

    def __setstate__(self, state):
        self.type = state['type']
        self.extend(state['seq'])


def strip_math(s):
    """remove latex formatting from mathtext"""
    remove = ('\\mathdefault', '\\rm', '\\cal', '\\tt', '\\it', '\\', '{', '}')
    s = s[1:-1]
    for r in remove:
        s = s.replace(r, '')

    return s


class Bunch:
    """
    Often we want to just collect a bunch of stuff together, naming each
    item of the bunch; a dictionary's OK for that, but a small do- nothing
    class is even handier, and prettier to use.  Whenever you want to
    group a few variables::

      >>> point = Bunch(datum=2, squared=4, coord=12)
      >>> point.datum

      By: Alex Martelli
      From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
    """

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        keys = self.__dict__.iterkeys()
        return 'Bunch(%s)' % (', ').join([ '%s=%s' % (k, self.__dict__[k]) for k in keys
                                         ])


def unique(x):
    """Return a list of unique elements of *x*"""
    return dict([ (val, 1) for val in x ]).keys()


def iterable(obj):
    """return true if *obj* is iterable"""
    try:
        iter(obj)
    except TypeError:
        return False

    return True


def is_string_like(obj):
    """Return True if *obj* looks like a string"""
    if isinstance(obj, (str, unicode)):
        return True
    if ma.isMaskedArray(obj):
        if obj.ndim == 0 and obj.dtype.kind in 'SU':
            return True
        else:
            return False

    try:
        obj + ''
    except:
        return False

    return True


def is_sequence_of_strings(obj):
    """
    Returns true if *obj* is iterable and contains strings
    """
    if not iterable(obj):
        return False
    if is_string_like(obj):
        return False
    for o in obj:
        if not is_string_like(o):
            return False

    return True


def is_writable_file_like(obj):
    """return true if *obj* looks like a file object with a *write* method"""
    return hasattr(obj, 'write') and callable(obj.write)


def is_scalar(obj):
    """return true if *obj* is not string like and is not iterable"""
    return not is_string_like(obj) and not iterable(obj)


def is_numlike(obj):
    """return true if *obj* looks like a number"""
    try:
        obj + 1
    except:
        return False

    return True


def to_filehandle(fname, flag='rU', return_opened=False):
    """
    *fname* can be a filename or a file handle.  Support for gzipped
    files is automatic, if the filename ends in .gz.  *flag* is a
    read/write flag for :func:`file`
    """
    if is_string_like(fname):
        if fname.endswith('.gz'):
            import gzip
            flag = flag.replace('U', '')
            fh = gzip.open(fname, flag)
        elif fname.endswith('.bz2'):
            flag = flag.replace('U', '')
            import bz2
            fh = bz2.BZ2File(fname, flag)
        else:
            fh = open(fname, flag)
        opened = True
    else:
        if hasattr(fname, 'seek'):
            fh = fname
            opened = False
        else:
            raise ValueError('fname must be a string or file handle')
        if return_opened:
            return (fh, opened)
    return fh


def is_scalar_or_string(val):
    """Return whether the given object is a scalar or string like."""
    return is_string_like(val) or not iterable(val)


def get_sample_data(fname, asfileobj=True):
    """
    Return a sample data file.  *fname* is a path relative to the
    `mpl-data/sample_data` directory.  If *asfileobj* is `True`
    return a file object, otherwise just a file path.

    If the filename ends in .gz, the file is implicitly ungzipped.
    """
    root = os.path.join(os.path.dirname(__file__), 'mpl-data', 'sample_data')
    path = os.path.join(root, fname)
    if asfileobj:
        if os.path.splitext(fname)[-1].lower() in ('.csv', '.xrc', '.txt'):
            mode = 'r'
        else:
            mode = 'rb'
        base, ext = os.path.splitext(fname)
        if ext == '.gz':
            return gzip.open(path, mode)
        return open(path, mode)
    else:
        return path


def flatten(seq, scalarp=is_scalar_or_string):
    """
    Returns a generator of flattened nested containers

    For example:

        >>> from matplotlib.cbook import flatten
        >>> l = (('John', ['Hunter']), (1, 23), [[([42, (5, 23)], )]])
        >>> print list(flatten(l))
        ['John', 'Hunter', 1, 23, 42, 5, 23]

    By: Composite of Holger Krekel and Luther Blissett
    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/121294
    and Recipe 1.12 in cookbook
    """
    for item in seq:
        if scalarp(item):
            yield item
        else:
            for subitem in flatten(item, scalarp):
                yield subitem


class Sorter:
    """
    Sort by attribute or item

    Example usage::

      sort = Sorter()

      list = [(1, 2), (4, 8), (0, 3)]
      dict = [{'a': 3, 'b': 4}, {'a': 5, 'b': 2}, {'a': 0, 'b': 0},
              {'a': 9, 'b': 9}]

      sort(list)       # default sort
      sort(list, 1)    # sort by index 1
      sort(dict, 'a')  # sort a list of dicts by key 'a'

    """

    def _helper(self, data, aux, inplace):
        aux.sort()
        result = [ data[i] for junk, i in aux ]
        if inplace:
            data[:] = result
        return result

    def byItem(self, data, itemindex=None, inplace=1):
        if itemindex is None:
            if inplace:
                data.sort()
                result = data
            else:
                result = data[:]
                result.sort()
            return result
        aux = [ (data[i][itemindex], i) for i in range(len(data)) ]
        return self._helper(data, aux, inplace)
        return

    def byAttribute(self, data, attributename, inplace=1):
        aux = [ (getattr(data[i], attributename), i) for i in range(len(data)) ]
        return self._helper(data, aux, inplace)

    sort = byItem
    __call__ = byItem


class Xlator(dict):
    """
    All-in-one multiple-string-substitution class

    Example usage::

      text = "Larry Wall is the creator of Perl"
      adict = {
      "Larry Wall" : "Guido van Rossum",
      "creator" : "Benevolent Dictator for Life",
      "Perl" : "Python",
      }

      print multiple_replace(adict, text)

      xlat = Xlator(adict)
      print xlat.xlat(text)
    """

    def _make_regex(self):
        """ Build re object based on the keys of the current dictionary """
        return re.compile(('|').join(map(re.escape, self.iterkeys())))

    def __call__(self, match):
        """ Handler invoked for each regex *match* """
        return self[match.group(0)]

    def xlat(self, text):
        """ Translate *text*, returns the modified text. """
        return self._make_regex().sub(self, text)


def soundex(name, len=4):
    """ soundex module conforming to Odell-Russell algorithm """
    soundex_digits = '01230120022455012623010202'
    sndx = ''
    fc = ''
    for c in name.upper():
        if c.isalpha():
            if not fc:
                fc = c
            d = soundex_digits[ord(c) - ord('A')]
            if not sndx or d != sndx[-1]:
                sndx += d

    sndx = fc + sndx[1:]
    sndx = sndx.replace('0', '')
    return (sndx + len * '0')[:len]


class Null:
    """ Null objects always and reliably "do nothing." """

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __str__(self):
        return 'Null()'

    def __repr__(self):
        return 'Null()'

    def __nonzero__(self):
        return 0

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self


def mkdirs(newdir, mode=511):
    """
    make directory *newdir* recursively, and set *mode*.  Equivalent to ::

        > mkdir -p NEWDIR
        > chmod MODE NEWDIR
    """
    try:
        if not os.path.exists(newdir):
            parts = os.path.split(newdir)
            for i in range(1, len(parts) + 1):
                thispart = os.path.join(*parts[:i])
                if not os.path.exists(thispart):
                    os.makedirs(thispart, mode)

    except OSError as err:
        if err.errno != errno.EEXIST or not os.path.isdir(newdir):
            raise


class GetRealpathAndStat:

    def __init__(self):
        self._cache = {}

    def __call__(self, path):
        result = self._cache.get(path)
        if result is None:
            realpath = os.path.realpath(path)
            if sys.platform == 'win32':
                stat_key = realpath
            else:
                stat = os.stat(realpath)
                stat_key = (stat.st_ino, stat.st_dev)
            result = (
             realpath, stat_key)
            self._cache[path] = result
        return result


get_realpath_and_stat = GetRealpathAndStat()

def dict_delall(d, keys):
    """delete all of the *keys* from the :class:`dict` *d*"""
    for key in keys:
        try:
            del d[key]
        except KeyError:
            pass


class RingBuffer:
    """ class that implements a not-yet-full buffer """

    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """

        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur + 1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:] + self.data[:self.cur]

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            self.__class__ = __Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data

    def __get_item__(self, i):
        return self.data[i % len(self.data)]


def get_split_ind(seq, N):
    """
    *seq* is a list of words.  Return the index into seq such that::

        len(' '.join(seq[:ind])<=N

    .
    """
    sLen = 0
    for word, ind in zip(seq, xrange(len(seq))):
        sLen += len(word) + 1
        if sLen >= N:
            return ind

    return len(seq)


def wrap(prefix, text, cols):
    """wrap *text* with *prefix* at length *cols*"""
    pad = ' ' * len(prefix.expandtabs())
    available = cols - len(pad)
    seq = text.split(' ')
    Nseq = len(seq)
    ind = 0
    lines = []
    while ind < Nseq:
        lastInd = ind
        ind += get_split_ind(seq[ind:], available)
        lines.append(seq[lastInd:ind])

    ret = prefix + (' ').join(lines[0]) + '\n'
    for line in lines[1:]:
        ret += pad + (' ').join(line) + '\n'

    return ret


_find_dedent_regex = re.compile('(?:(?:\n\r?)|^)( *)\\S')
_dedent_regex = {}

def dedent(s):
    """
    Remove excess indentation from docstring *s*.

    Discards any leading blank lines, then removes up to n whitespace
    characters from each line, where n is the number of leading
    whitespace characters in the first line. It differs from
    textwrap.dedent in its deletion of leading blank lines and its use
    of the first non-blank line to determine the indentation.

    It is also faster in most cases.
    """
    if not s:
        return ''
    else:
        match = _find_dedent_regex.match(s)
        if match is None:
            return s
        nshift = match.end(1) - match.start(1)
        if nshift == 0:
            return s
        unindent = _dedent_regex.get(nshift, None)
        if unindent is None:
            unindent = re.compile('\n\r? {0,%d}' % nshift)
            _dedent_regex[nshift] = unindent
        result = unindent.sub('\n', s).strip()
        return result


def listFiles(root, patterns='*', recurse=1, return_folders=0):
    """
    Recursively list files

    from Parmar and Martelli in the Python Cookbook
    """
    import os.path, fnmatch
    pattern_list = patterns.split(';')
    results = []
    for dirname, dirs, files in os.walk(root):
        for name in files:
            fullname = os.path.normpath(os.path.join(dirname, name))
            if return_folders or os.path.isfile(fullname):
                for pattern in pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        results.append(fullname)
                        break

        if not recurse:
            break

    return results


def get_recursive_filelist(args):
    """
    Recurse all the files and dirs in *args* ignoring symbolic links
    and return the files as a list of strings
    """
    files = []
    for arg in args:
        if os.path.isfile(arg):
            files.append(arg)
            continue
        if os.path.isdir(arg):
            newfiles = listFiles(arg, recurse=1, return_folders=1)
            files.extend(newfiles)

    return [ f for f in files if not os.path.islink(f) ]


def pieces(seq, num=2):
    """Break up the *seq* into *num* tuples"""
    start = 0
    while 1:
        item = seq[start:start + num]
        if not len(item):
            break
        yield item
        start += num


def exception_to_str(s=None):
    sh = io.StringIO()
    if s is not None:
        print(s, file=sh)
    traceback.print_exc(file=sh)
    return sh.getvalue()


def allequal(seq):
    """
    Return *True* if all elements of *seq* compare equal.  If *seq* is
    0 or 1 length, return *True*
    """
    if len(seq) < 2:
        return True
    val = seq[0]
    for i in xrange(1, len(seq)):
        thisval = seq[i]
        if thisval != val:
            return False

    return True


def alltrue(seq):
    """
    Return *True* if all elements of *seq* evaluate to *True*.  If
    *seq* is empty, return *False*.
    """
    if not len(seq):
        return False
    for val in seq:
        if not val:
            return False

    return True


def onetrue(seq):
    """
    Return *True* if one element of *seq* is *True*.  It *seq* is
    empty, return *False*.
    """
    if not len(seq):
        return False
    for val in seq:
        if val:
            return True

    return False


def allpairs(x):
    """
    return all possible pairs in sequence *x*

    Condensed by Alex Martelli from this thread_ on c.l.python

    .. _thread: http://groups.google.com/groups?q=all+pairs+group:*python*&hl=en&lr=&ie=UTF-8&selm=mailman.4028.1096403649.5135.python-list%40python.org&rnum=1
    """
    return [ (s, f) for i, f in enumerate(x) for s in x[i + 1:] ]


class maxdict(dict):
    """
    A dictionary with a maximum size; this doesn't override all the
    relevant methods to contrain size, just setitem, so use with
    caution
    """

    def __init__(self, maxsize):
        dict.__init__(self)
        self.maxsize = maxsize
        self._killkeys = []

    def __setitem__(self, k, v):
        if k not in self:
            if len(self) >= self.maxsize:
                del self[self._killkeys[0]]
                del self._killkeys[0]
            self._killkeys.append(k)
        dict.__setitem__(self, k, v)


class Stack(object):
    """
    Implement a stack where elements can be pushed on and you can move
    back and forth.  But no pop.  Should mimic home / back / forward
    in a browser
    """

    def __init__(self, default=None):
        self.clear()
        self._default = default

    def __call__(self):
        """return the current element, or None"""
        if not len(self._elements):
            return self._default
        else:
            return self._elements[self._pos]

    def __len__(self):
        return self._elements.__len__()

    def __getitem__(self, ind):
        return self._elements.__getitem__(ind)

    def forward(self):
        """move the position forward and return the current element"""
        N = len(self._elements)
        if self._pos < N - 1:
            self._pos += 1
        return self()

    def back(self):
        """move the position back and return the current element"""
        if self._pos > 0:
            self._pos -= 1
        return self()

    def push(self, o):
        """
        push object onto stack at current position - all elements
        occurring later than the current position are discarded
        """
        self._elements = self._elements[:self._pos + 1]
        self._elements.append(o)
        self._pos = len(self._elements) - 1
        return self()

    def home(self):
        """push the first element onto the top of the stack"""
        if not len(self._elements):
            return
        self.push(self._elements[0])
        return self()

    def empty(self):
        return len(self._elements) == 0

    def clear(self):
        """empty the stack"""
        self._pos = -1
        self._elements = []

    def bubble(self, o):
        """
        raise *o* to the top of the stack and return *o*.  *o* must be
        in the stack
        """
        if o not in self._elements:
            raise ValueError('Unknown element o')
        old = self._elements[:]
        self.clear()
        bubbles = []
        for thiso in old:
            if thiso == o:
                bubbles.append(thiso)
            else:
                self.push(thiso)

        for thiso in bubbles:
            self.push(o)

        return o

    def remove(self, o):
        """remove element *o* from the stack"""
        if o not in self._elements:
            raise ValueError('Unknown element o')
        old = self._elements[:]
        self.clear()
        for thiso in old:
            if thiso == o:
                continue
            else:
                self.push(thiso)


def popall(seq):
    """empty a list"""
    for i in xrange(len(seq)):
        seq.pop()


def finddir(o, match, case=False):
    """
    return all attributes of *o* which match string in match.  if case
    is True require an exact case match.
    """
    if case:
        names = [ (name, name) for name in dir(o) if is_string_like(name) ]
    else:
        names = [ (name.lower(), name) for name in dir(o) if is_string_like(name)
                ]
        match = match.lower()
    return [ orig for name, orig in names if name.find(match) >= 0 ]


def reverse_dict(d):
    """reverse the dictionary -- may lose data if values are not unique!"""
    return dict([ (v, k) for k, v in d.iteritems() ])


def restrict_dict(d, keys):
    """
    Return a dictionary that contains those keys that appear in both
    d and keys, with values from d.
    """
    return dict([ (k, v) for k, v in d.iteritems() if k in keys ])


def report_memory(i=0):
    """return the memory consumed by process"""
    from subprocess import Popen, PIPE
    pid = os.getpid()
    if sys.platform == 'sunos5':
        a2 = Popen('ps -p %d -o osz' % pid, shell=True, stdout=PIPE).stdout.readlines()
        mem = int(a2[-1].strip())
    elif sys.platform.startswith('linux'):
        a2 = Popen('ps -p %d -o rss,sz' % pid, shell=True, stdout=PIPE).stdout.readlines()
        mem = int(a2[1].split()[1])
    elif sys.platform.startswith('darwin'):
        a2 = Popen('ps -p %d -o rss,vsz' % pid, shell=True, stdout=PIPE).stdout.readlines()
        mem = int(a2[1].split()[0])
    elif sys.platform.startswith('win'):
        try:
            a2 = Popen(['tasklist', '/nh', '/fi', 'pid eq %d' % pid], stdout=PIPE).stdout.read()
        except OSError:
            raise NotImplementedError("report_memory works on Windows only if the 'tasklist' program is found")

        mem = int(a2.strip().split()[-2].replace(',', ''))
    else:
        raise NotImplementedError("We don't have a memory monitor for %s" % sys.platform)
    return mem


_safezip_msg = 'In safezip, len(args[0])=%d but len(args[%d])=%d'

def safezip(*args):
    """make sure *args* are equal len before zipping"""
    Nx = len(args[0])
    for i, arg in enumerate(args[1:]):
        if len(arg) != Nx:
            raise ValueError(_safezip_msg % (Nx, i + 1, len(arg)))

    return zip(*args)


def issubclass_safe(x, klass):
    """return issubclass(x, klass) and return False on a TypeError"""
    try:
        return issubclass(x, klass)
    except TypeError:
        return False


def safe_masked_invalid(x):
    x = np.asanyarray(x)
    try:
        xm = np.ma.masked_invalid(x, copy=False)
        xm.shrink_mask()
    except TypeError:
        return x

    return xm


class MemoryMonitor:

    def __init__(self, nmax=20000):
        self._nmax = nmax
        self._mem = np.zeros((self._nmax,), np.int32)
        self.clear()

    def clear(self):
        self._n = 0
        self._overflow = False

    def __call__(self):
        mem = report_memory()
        if self._n < self._nmax:
            self._mem[self._n] = mem
            self._n += 1
        else:
            self._overflow = True
        return mem

    def report(self, segments=4):
        n = self._n
        segments = min(n, segments)
        dn = int(n / segments)
        ii = range(0, n, dn)
        ii[-1] = n - 1
        print()
        print('memory report: i, mem, dmem, dmem/nloops')
        print(0, self._mem[0])
        for i in range(1, len(ii)):
            di = ii[i] - ii[i - 1]
            if di == 0:
                continue
            dm = self._mem[ii[i]] - self._mem[ii[i - 1]]
            print('%5d %5d %3d %8.3f' % (ii[i], self._mem[ii[i]],
             dm, dm / float(di)))

        if self._overflow:
            print('Warning: array size was too small for the number of calls.')

    def xy(self, i0=0, isub=1):
        x = np.arange(i0, self._n, isub)
        return (x, self._mem[i0:self._n:isub])

    def plot(self, i0=0, isub=1, fig=None):
        if fig is None:
            from pylab import figure, show
            fig = figure()
        ax = fig.add_subplot(111)
        ax.plot(*self.xy(i0, isub))
        fig.canvas.draw()
        return


def print_cycles(objects, outstream=sys.stdout, show_progress=False):
    """
    *objects*
        A list of objects to find cycles in.  It is often useful to
        pass in gc.garbage to find the cycles that are preventing some
        objects from being garbage collected.

    *outstream*
        The stream for output.

    *show_progress*
        If True, print the number of objects reached as they are found.
    """
    import gc
    from types import FrameType

    def print_path(path):
        for i, step in enumerate(path):
            next = path[(i + 1) % len(path)]
            outstream.write('   %s -- ' % str(type(step)))
            if isinstance(step, dict):
                for key, val in step.iteritems():
                    if val is next:
                        outstream.write('[%s]' % repr(key))
                        break
                    if key is next:
                        outstream.write('[key] = %s' % repr(val))
                        break

            elif isinstance(step, list):
                outstream.write('[%d]' % step.index(next))
            elif isinstance(step, tuple):
                outstream.write('( tuple )')
            else:
                outstream.write(repr(step))
            outstream.write(' ->\n')

        outstream.write('\n')

    def recurse(obj, start, all, current_path):
        if show_progress:
            outstream.write('%d\r' % len(all))
        all[id(obj)] = None
        referents = gc.get_referents(obj)
        for referent in referents:
            if referent is start:
                print_path(current_path)
            elif referent is objects or isinstance(referent, FrameType):
                continue
            elif id(referent) not in all:
                recurse(referent, start, all, current_path + [obj])

        return

    for obj in objects:
        outstream.write('Examining: %r\n' % (obj,))
        recurse(obj, obj, {}, [])


class Grouper(object):
    """
    This class provides a lightweight way to group arbitrary objects
    together into disjoint sets when a full-blown graph data structure
    would be overkill.

    Objects can be joined using :meth:`join`, tested for connectedness
    using :meth:`joined`, and all disjoint sets can be retreived by
    using the object as an iterator.

    The objects being joined must be hashable and weak-referenceable.

    For example:

        >>> from matplotlib.cbook import Grouper
        >>> class Foo(object):
        ...     def __init__(self, s):
        ...         self.s = s
        ...     def __repr__(self):
        ...         return self.s
        ...
        >>> a, b, c, d, e, f = [Foo(x) for x in 'abcdef']
        >>> grp = Grouper()
        >>> grp.join(a, b)
        >>> grp.join(b, c)
        >>> grp.join(d, e)
        >>> sorted(map(tuple, grp))
        [(d, e), (a, b, c)]
        >>> grp.joined(a, b)
        True
        >>> grp.joined(a, c)
        True
        >>> grp.joined(a, d)
        False

    """

    def __init__(self, init=[]):
        mapping = self._mapping = {}
        for x in init:
            mapping[ref(x)] = [
             ref(x)]

    def __contains__(self, item):
        return ref(item) in self._mapping

    def clean(self):
        """
        Clean dead weak references from the dictionary
        """
        mapping = self._mapping
        to_drop = [ key for key in mapping if key() is None ]
        for key in to_drop:
            val = mapping.pop(key)
            val.remove(key)

        return

    def join(self, a, *args):
        """
        Join given arguments into the same set.  Accepts one or more
        arguments.
        """
        mapping = self._mapping
        set_a = mapping.setdefault(ref(a), [ref(a)])
        for arg in args:
            set_b = mapping.get(ref(arg))
            if set_b is None:
                set_a.append(ref(arg))
                mapping[ref(arg)] = set_a
            elif set_b is not set_a:
                if len(set_b) > len(set_a):
                    set_a, set_b = set_b, set_a
                set_a.extend(set_b)
                for elem in set_b:
                    mapping[elem] = set_a

        self.clean()
        return

    def joined(self, a, b):
        """
        Returns True if *a* and *b* are members of the same set.
        """
        self.clean()
        mapping = self._mapping
        try:
            return mapping[ref(a)] is mapping[ref(b)]
        except KeyError:
            return False

    def __iter__(self):
        """
        Iterate over each of the disjoint sets as a list.

        The iterator is invalid if interleaved with calls to join().
        """
        self.clean()

        class Token:
            pass

        token = Token()
        for group in self._mapping.itervalues():
            if group[-1] is not token:
                yield [ x() for x in group ]
                group.append(token)

        for group in self._mapping.itervalues():
            if group[-1] is token:
                del group[-1]

    def get_siblings(self, a):
        """
        Returns all of the items joined with *a*, including itself.
        """
        self.clean()
        siblings = self._mapping.get(ref(a), [ref(a)])
        return [ x() for x in siblings ]


def simple_linear_interpolation(a, steps):
    if steps == 1:
        return a
    steps = np.floor(steps)
    new_length = (len(a) - 1) * steps + 1
    new_shape = list(a.shape)
    new_shape[0] = new_length
    result = np.zeros(new_shape, a.dtype)
    result[0] = a[0]
    a0 = a[0:-1]
    a1 = a[1:]
    delta = (a1 - a0) / steps
    for i in range(1, int(steps)):
        result[i::steps] = delta * i + a0

    result[steps::steps] = a1
    return result


def recursive_remove(path):
    if os.path.isdir(path):
        for fname in glob.glob(os.path.join(path, '*')) + glob.glob(os.path.join(path, '.*')):
            if os.path.isdir(fname):
                recursive_remove(fname)
                os.removedirs(fname)
            else:
                os.remove(fname)

    else:
        os.remove(path)


def delete_masked_points(*args):
    """
    Find all masked and/or non-finite points in a set of arguments,
    and return the arguments with only the unmasked points remaining.

    Arguments can be in any of 5 categories:

    1) 1-D masked arrays
    2) 1-D ndarrays
    3) ndarrays with more than one dimension
    4) other non-string iterables
    5) anything else

    The first argument must be in one of the first four categories;
    any argument with a length differing from that of the first
    argument (and hence anything in category 5) then will be
    passed through unchanged.

    Masks are obtained from all arguments of the correct length
    in categories 1, 2, and 4; a point is bad if masked in a masked
    array or if it is a nan or inf.  No attempt is made to
    extract a mask from categories 2, 3, and 4 if :meth:`np.isfinite`
    does not yield a Boolean array.

    All input arguments that are not passed unchanged are returned
    as ndarrays after removing the points or rows corresponding to
    masks in any of the arguments.

    A vastly simpler version of this function was originally
    written as a helper for Axes.scatter().

    """
    if not len(args):
        return ()
    if is_string_like(args[0]) or not iterable(args[0]):
        raise ValueError('First argument must be a sequence')
    nrecs = len(args[0])
    margs = []
    seqlist = [False] * len(args)
    for i, x in enumerate(args):
        if not is_string_like(x) and iterable(x) and len(x) == nrecs:
            seqlist[i] = True
            if ma.isMA(x):
                if x.ndim > 1:
                    raise ValueError('Masked arrays must be 1-D')
            else:
                x = np.asarray(x)
        margs.append(x)

    masks = []
    for i, x in enumerate(margs):
        if seqlist[i]:
            if x.ndim > 1:
                continue
            if ma.isMA(x):
                masks.append(~ma.getmaskarray(x))
                xd = x.data
            else:
                xd = x
            try:
                mask = np.isfinite(xd)
                if isinstance(mask, np.ndarray):
                    masks.append(mask)
            except:
                pass

    if len(masks):
        mask = reduce(np.logical_and, masks)
        igood = mask.nonzero()[0]
        if len(igood) < nrecs:
            for i, x in enumerate(margs):
                if seqlist[i]:
                    margs[i] = x.take(igood, axis=0)

    for i, x in enumerate(margs):
        if seqlist[i] and ma.isMA(x):
            margs[i] = x.filled()

    return margs


def unmasked_index_ranges(mask, compressed=True):
    """
    Find index ranges where *mask* is *False*.

    *mask* will be flattened if it is not already 1-D.

    Returns Nx2 :class:`numpy.ndarray` with each row the start and stop
    indices for slices of the compressed :class:`numpy.ndarray`
    corresponding to each of *N* uninterrupted runs of unmasked
    values.  If optional argument *compressed* is *False*, it returns
    the start and stop indices into the original :class:`numpy.ndarray`,
    not the compressed :class:`numpy.ndarray`.  Returns *None* if there
    are no unmasked values.

    Example::

      y = ma.array(np.arange(5), mask = [0,0,1,0,0])
      ii = unmasked_index_ranges(ma.getmaskarray(y))
      # returns array [[0,2,] [2,4,]]

      y.compressed()[ii[1,0]:ii[1,1]]
      # returns array [3,4,]

      ii = unmasked_index_ranges(ma.getmaskarray(y), compressed=False)
      # returns array [[0, 2], [3, 5]]

      y.filled()[ii[1,0]:ii[1,1]]
      # returns array [3,4,]

    Prior to the transforms refactoring, this was used to support
    masked arrays in Line2D.

    """
    mask = mask.reshape(mask.size)
    m = np.concatenate(((1, ), mask, (1, )))
    indices = np.arange(len(mask) + 1)
    mdif = m[1:] - m[:-1]
    i0 = np.compress(mdif == -1, indices)
    i1 = np.compress(mdif == 1, indices)
    assert len(i0) == len(i1)
    if len(i1) == 0:
        return
    else:
        if not compressed:
            return np.concatenate((i0[:, np.newaxis], i1[:, np.newaxis]), axis=1)
        seglengths = i1 - i0
        breakpoints = np.cumsum(seglengths)
        ic0 = np.concatenate(((0, ), breakpoints[:-1]))
        ic1 = breakpoints
        return np.concatenate((ic0[:, np.newaxis], ic1[:, np.newaxis]), axis=1)


_linestyles = [
 ('-', 'solid'),
 ('--', 'dashed'),
 ('-.', 'dashdot'),
 (':', 'dotted')]
ls_mapper = dict(_linestyles)
ls_mapper.update([ (ls[1], ls[0]) for ls in _linestyles ])

def less_simple_linear_interpolation(x, y, xi, extrap=False):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('less_simple_linear_interpolation has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.less_simple_linear_interpolation(x, y, xi, extrap=extrap)


def vector_lengths(X, P=2.0, axis=None):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('vector_lengths has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.vector_lengths(X, P=2.0, axis=axis)


def distances_along_curve(X):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('distances_along_curve has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.distances_along_curve(X)


def path_length(X):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('path_length has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.path_length(X)


def is_closed_polygon(X):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('is_closed_polygon has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.is_closed_polygon(X)


def quad2cubic(q0x, q0y, q1x, q1y, q2x, q2y):
    """
    This function has been moved to matplotlib.mlab -- please import
    it from there
    """
    warnings.warn('quad2cubic has been moved to matplotlib.mlab -- please import it from there', DeprecationWarning)
    import matplotlib.mlab as mlab
    return mlab.quad2cubic(q0x, q0y, q1x, q1y, q2x, q2y)


def align_iterators(func, *iterables):
    """
    This generator takes a bunch of iterables that are ordered by func
    It sends out ordered tuples::

       (func(row), [rows from all iterators matching func(row)])

    It is used by :func:`matplotlib.mlab.recs_join` to join record arrays
    """

    class myiter:

        def __init__(self, it):
            self.it = it
            self.key = self.value = None
            self.iternext()
            return

        def iternext(self):
            try:
                self.value = next(self.it)
                self.key = func(self.value)
            except StopIteration:
                self.value = self.key = None

            return

        def __call__(self, key):
            retval = None
            if key == self.key:
                retval = self.value
                self.iternext()
            elif self.key and key > self.key:
                raise ValueError('Iterator has been left behind')
            return retval

    iters = [ myiter(it) for it in iterables ]
    minvals = minkey = True
    while 1:
        minvals = [ _f for _f in [ it.key for it in iters ] if _f ]
        if minvals:
            minkey = min(minvals)
            yield (minkey, [ it(minkey) for it in iters ])
        else:
            break


def is_math_text(s):
    try:
        s = unicode(s)
    except UnicodeDecodeError:
        raise ValueError('matplotlib display text must have all code points < 128 or use Unicode strings')

    dollar_count = s.count('$') - s.count('\\$')
    even_dollars = dollar_count > 0 and dollar_count % 2 == 0
    return even_dollars


class _NestedClassGetter(object):
    """
    When called with the containing class as the first argument,
    and the name of the nested class as the second argument,
    returns an instance of the nested class.
    """

    def __call__(self, containing_class, class_name):
        nested_class = getattr(containing_class, class_name)
        nested_instance = _NestedClassGetter()
        nested_instance.__class__ = nested_class
        return nested_instance


class _InstanceMethodPickler(object):
    """
    Pickle cannot handle instancemethod saving. _InstanceMethodPickler
    provides a solution to this.
    """

    def __init__(self, instancemethod):
        """Takes an instancemethod as its only argument."""
        self.parent_obj = instancemethod.im_self
        self.instancemethod_name = instancemethod.im_func.__name__

    def get_instancemethod(self):
        return getattr(self.parent_obj, self.instancemethod_name)


try:
    np.copyto
except AttributeError:
    _putmask = np.putmask
else:

    def _putmask(a, mask, values):
        return np.copyto(a, values, where=mask)


def _check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte
    string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the
    returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example::

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.::

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get('args')
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


if hasattr(subprocess, 'check_output'):
    check_output = subprocess.check_output
else:
    check_output = _check_output
if __name__ == '__main__':
    assert allequal([1, 1, 1])
    assert not allequal([1, 1, 0])
    assert allequal([])
    assert allequal(('a', 'a'))
    assert not allequal(('a', 'b'))