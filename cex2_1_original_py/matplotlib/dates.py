# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\dates.pyc
# Compiled at: 2012-11-06 15:31:10
"""
Matplotlib provides sophisticated date plotting capabilities, standing
on the shoulders of python :mod:`datetime`, the add-on modules
:mod:`pytz` and :mod:`dateutils`.  :class:`datetime` objects are
converted to floating point numbers which represent time in days
since 0001-01-01 UTC, plus 1.  For example, 0001-01-01, 06:00 is
1.25, not 0.25.  The helper functions :func:`date2num`,
:func:`num2date` and :func:`drange` are used to facilitate easy
conversion to and from :mod:`datetime` and numeric ranges.

.. note::
   Like Python's datetime, mpl uses the Gregorian calendar for
   all conversions between dates and floating point numbers.
   This practice is not universal, and calendar differences can
   cause confusing differences between what Python and mpl
   give as the number of days since 0001-01-01 and what other
   software and databases yield.  For example, the
   `US Naval Observatory <http://www.usno.navy.mil/USNO/astronomical-applications/data-services/jul-date>`_
   uses a calendar that switches from Julian to Gregorian in
   October, 1582.  Hence, using their calculator, the number of
   days between 0001-01-01 and 2006-04-01 is 732403, whereas using
   the Gregorian calendar via the datetime module we find::

     In [31]:date(2006,4,1).toordinal() - date(1,1,1).toordinal()
     Out[31]:732401

A wide range of specific and general purpose date tick locators and
formatters are provided in this module.  See
:mod:`matplotlib.ticker` for general information on tick locators
and formatters.  These are described below.

All the matplotlib date converters, tickers and formatters are
timezone aware, and the default timezone is given by the timezone
parameter in your :file:`matplotlibrc` file.  If you leave out a
:class:`tz` timezone instance, the default from your rc file will be
assumed.  If you want to use a custom time zone, pass a
:class:`pytz.timezone` instance with the tz keyword argument to
:func:`num2date`, :func:`plot_date`, and any custom date tickers or
locators you create.  See `pytz <http://pytz.sourceforge.net>`_ for
information on :mod:`pytz` and timezone handling.

The `dateutil module <http://labix.org/python-dateutil>`_ provides
additional code to handle date ticking, making it easy to place ticks
on any kinds of dates.  See examples below.

Date tickers
------------

Most of the date tickers can locate single or multiple values.  For
example::

    # tick on mondays every week
    loc = WeekdayLocator(byweekday=MO, tz=tz)

    # tick on mondays and saturdays
    loc = WeekdayLocator(byweekday=(MO, SA))

In addition, most of the constructors take an interval argument::

    # tick on mondays every second week
    loc = WeekdayLocator(byweekday=MO, interval=2)

The rrule locator allows completely general date ticking::

    # tick every 5th easter
    rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
    loc = RRuleLocator(rule)

Here are all the date tickers:

    * :class:`MinuteLocator`: locate minutes

    * :class:`HourLocator`: locate hours

    * :class:`DayLocator`: locate specifed days of the month

    * :class:`WeekdayLocator`: Locate days of the week, eg MO, TU

    * :class:`MonthLocator`: locate months, eg 7 for july

    * :class:`YearLocator`: locate years that are multiples of base

    * :class:`RRuleLocator`: locate using a
      :class:`matplotlib.dates.rrulewrapper`.  The
      :class:`rrulewrapper` is a simple wrapper around a
      :class:`dateutils.rrule` (`dateutil
      <http://labix.org/python-dateutil>`_) which allow almost
      arbitrary date tick specifications.  See `rrule example
      <../examples/pylab_examples/date_demo_rrule.html>`_.

    * :class:`AutoDateLocator`: On autoscale, this class picks the best
      :class:`MultipleDateLocator` to set the view limits and the tick
      locations.

Date formatters
---------------

Here all all the date formatters:

    * :class:`AutoDateFormatter`: attempts to figure out the best format
      to use.  This is most useful when used with the :class:`AutoDateLocator`.

    * :class:`DateFormatter`: use :func:`strftime` format strings

    * :class:`IndexDateFormatter`: date plots with implicit *x*
      indexing.
"""
from __future__ import print_function
import re, time, math, datetime
from itertools import izip
import matplotlib, numpy as np, matplotlib.units as units, matplotlib.cbook as cbook, matplotlib.ticker as ticker
from dateutil.rrule import rrule, MO, TU, WE, TH, FR, SA, SU, YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY
from dateutil.relativedelta import relativedelta
import dateutil.parser
__all__ = ('date2num', 'num2date', 'drange', 'epoch2num', 'num2epoch', 'mx2num', 'DateFormatter',
           'IndexDateFormatter', 'AutoDateFormatter', 'DateLocator', 'RRuleLocator',
           'AutoDateLocator', 'YearLocator', 'MonthLocator', 'WeekdayLocator', 'DayLocator',
           'HourLocator', 'MinuteLocator', 'SecondLocator', 'rrule', 'MO', 'TU',
           'WE', 'TH', 'FR', 'SA', 'SU', 'YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY',
           'HOURLY', 'MINUTELY', 'SECONDLY', 'relativedelta', 'seconds', 'minutes',
           'hours', 'weeks')

class _UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return datetime.timedelta(0)


UTC = _UTC()

def _get_rc_timezone():
    s = matplotlib.rcParams['timezone']
    if s == 'UTC':
        return UTC
    import pytz
    return pytz.timezone(s)


HOURS_PER_DAY = 24.0
MINUTES_PER_DAY = 60.0 * HOURS_PER_DAY
SECONDS_PER_DAY = 60.0 * MINUTES_PER_DAY
MUSECONDS_PER_DAY = 1000000.0 * SECONDS_PER_DAY
SEC_PER_MIN = 60
SEC_PER_HOUR = 3600
SEC_PER_DAY = SEC_PER_HOUR * 24
SEC_PER_WEEK = SEC_PER_DAY * 7
MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = (
 MO, TU, WE, TH, FR, SA, SU)
WEEKDAYS = (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY)

def _to_ordinalf(dt):
    """
    Convert :mod:`datetime` to the Gregorian date as UTC float days,
    preserving hours, minutes, seconds and microseconds.  Return value
    is a :func:`float`.
    """
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        delta = dt.tzinfo.utcoffset(dt)
        if delta is not None:
            dt -= delta
    base = float(dt.toordinal())
    if hasattr(dt, 'hour'):
        base += dt.hour / HOURS_PER_DAY + dt.minute / MINUTES_PER_DAY + dt.second / SECONDS_PER_DAY + dt.microsecond / MUSECONDS_PER_DAY
    return base


def _from_ordinalf(x, tz=None):
    """
    Convert Gregorian float of the date, preserving hours, minutes,
    seconds and microseconds.  Return value is a :class:`datetime`.
    """
    if tz is None:
        tz = _get_rc_timezone()
    ix = int(x)
    dt = datetime.datetime.fromordinal(ix)
    remainder = float(x) - ix
    hour, remainder = divmod(24 * remainder, 1)
    minute, remainder = divmod(60 * remainder, 1)
    second, remainder = divmod(60 * remainder, 1)
    microsecond = int(1000000.0 * remainder)
    if microsecond < 10:
        microsecond = 0
    dt = datetime.datetime(dt.year, dt.month, dt.day, int(hour), int(minute), int(second), microsecond, tzinfo=UTC).astimezone(tz)
    if microsecond > 999990:
        dt += datetime.timedelta(microseconds=1000000.0 - microsecond)
    return dt


class strpdate2num:
    """
    Use this class to parse date strings to matplotlib datenums when
    you know the date format string of the date you are parsing.  See
    :file:`examples/load_demo.py`.
    """

    def __init__(self, fmt):
        """ fmt: any valid strptime format is supported """
        self.fmt = fmt

    def __call__(self, s):
        """s : string to be converted
           return value: a date2num float
        """
        return date2num(datetime.datetime(*time.strptime(s, self.fmt)[:6]))


def datestr2num(d):
    """
    Convert a date string to a datenum using
    :func:`dateutil.parser.parse`.  *d* can be a single string or a
    sequence of strings.
    """
    if cbook.is_string_like(d):
        dt = dateutil.parser.parse(d)
        return date2num(dt)
    else:
        return date2num([ dateutil.parser.parse(s) for s in d ])


def date2num(d):
    """
    *d* is either a :class:`datetime` instance or a sequence of datetimes.

    Return value is a floating point number (or sequence of floats)
    which gives the number of days (fraction part represents hours,
    minutes, seconds) since 0001-01-01 00:00:00 UTC, *plus* *one*.
    The addition of one here is a historical artifact.  Also, note
    that the Gregorian calendar is assumed; this is not universal
    practice.  For details, see the module docstring.
    """
    if not cbook.iterable(d):
        return _to_ordinalf(d)
    else:
        return np.asarray([ _to_ordinalf(val) for val in d ])


def julian2num(j):
    """Convert a Julian date (or sequence) to a matplotlib date (or sequence)."""
    if cbook.iterable(j):
        j = np.asarray(j)
    return j - 1721424.5


def num2julian(n):
    """Convert a matplotlib date (or sequence) to a Julian date (or sequence)."""
    if cbook.iterable(n):
        n = np.asarray(n)
    return n + 1721424.5


def num2date(x, tz=None):
    """
    *x* is a float value which gives the number of days
    (fraction part represents hours, minutes, seconds) since
    0001-01-01 00:00:00 UTC *plus* *one*.
    The addition of one here is a historical artifact.  Also, note
    that the Gregorian calendar is assumed; this is not universal
    practice.  For details, see the module docstring.

    Return value is a :class:`datetime` instance in timezone *tz* (default to
    rcparams TZ value).

    If *x* is a sequence, a sequence of :class:`datetime` objects will
    be returned.
    """
    if tz is None:
        tz = _get_rc_timezone()
    if not cbook.iterable(x):
        return _from_ordinalf(x, tz)
    else:
        return [ _from_ordinalf(val, tz) for val in x ]
        return


def drange(dstart, dend, delta):
    """
    Return a date range as float Gregorian ordinals.  *dstart* and
    *dend* are :class:`datetime` instances.  *delta* is a
    :class:`datetime.timedelta` instance.
    """
    step = delta.days + delta.seconds / SECONDS_PER_DAY + delta.microseconds / MUSECONDS_PER_DAY
    f1 = _to_ordinalf(dstart)
    f2 = _to_ordinalf(dend)
    num = int(np.ceil((f2 - f1) / step))
    dinterval_end = dstart + num * delta
    if dinterval_end >= dend:
        dinterval_end -= delta
        num -= 1
    f2 = _to_ordinalf(dinterval_end)
    return np.linspace(f1, f2, num + 1)


class DateFormatter(ticker.Formatter):
    """
    Tick location is seconds since the epoch.  Use a :func:`strftime`
    format string.

    Python only supports :mod:`datetime` :func:`strftime` formatting
    for years greater than 1900.  Thanks to Andrew Dalke, Dalke
    Scientific Software who contributed the :func:`strftime` code
    below to include dates earlier than this year.
    """
    illegal_s = re.compile('((^|[^%])(%%)*%s)')

    def __init__(self, fmt, tz=None):
        """
        *fmt* is an :func:`strftime` format string; *tz* is the
         :class:`tzinfo` instance.
        """
        if tz is None:
            tz = _get_rc_timezone()
        self.fmt = fmt
        self.tz = tz
        return

    def __call__(self, x, pos=0):
        if x == 0:
            raise ValueError('DateFormatter found a value of x=0, which is an illegal date.  This usually occurs because you have not informed the axis that it is plotting dates, eg with ax.xaxis_date()')
        dt = num2date(x, self.tz)
        return self.strftime(dt, self.fmt)

    def set_tzinfo(self, tz):
        self.tz = tz

    def _findall(self, text, substr):
        sites = []
        i = 0
        while 1:
            j = text.find(substr, i)
            if j == -1:
                break
            sites.append(j)
            i = j + 1

        return sites

    def strftime(self, dt, fmt):
        fmt = self.illegal_s.sub('\\1', fmt)
        fmt = fmt.replace('%s', 's')
        if dt.year > 1900:
            return cbook.unicode_safe(dt.strftime(fmt))
        year = dt.year
        delta = 2000 - year
        off = 6 * (delta // 100 + delta // 400)
        year = year + off
        year = year + (2000 - year) // 28 * 28
        timetuple = dt.timetuple()
        s1 = time.strftime(fmt, (year,) + timetuple[1:])
        sites1 = self._findall(s1, str(year))
        s2 = time.strftime(fmt, (year + 28,) + timetuple[1:])
        sites2 = self._findall(s2, str(year + 28))
        sites = []
        for site in sites1:
            if site in sites2:
                sites.append(site)

        s = s1
        syear = '%4d' % (dt.year,)
        for site in sites:
            s = s[:site] + syear + s[site + 4:]

        return cbook.unicode_safe(s)


class IndexDateFormatter(ticker.Formatter):
    """
    Use with :class:`~matplotlib.ticker.IndexLocator` to cycle format
    strings by index.
    """

    def __init__(self, t, fmt, tz=None):
        """
        *t* is a sequence of dates (floating point days).  *fmt* is a
        :func:`strftime` format string.
        """
        if tz is None:
            tz = _get_rc_timezone()
        self.t = t
        self.fmt = fmt
        self.tz = tz
        return

    def __call__(self, x, pos=0):
        """Return the label for time *x* at position *pos*"""
        ind = int(round(x))
        if ind >= len(self.t) or ind <= 0:
            return ''
        dt = num2date(self.t[ind], self.tz)
        return cbook.unicode_safe(dt.strftime(self.fmt))


class AutoDateFormatter(ticker.Formatter):
    """
    This class attempts to figure out the best format to use.  This is
    most useful when used with the :class:`AutoDateLocator`.

    The AutoDateFormatter has a scale dictionary that maps the scale
    of the tick (the distance in days between one major tick) and a
    format string.  The default looks like this::

        self.scaled = {
           365.0  : '%Y',
           30.    : '%b %Y',
           1.0    : '%b %d %Y',
           1./24. : '%H:%M:%D',
           }

    The algorithm picks the key in the dictionary that is >= the
    current scale and uses that format string.  You can customize this
    dictionary by doing::

      formatter = AutoDateFormatter()
      formatter.scaled[1/(24.*60.)] = '%M:%S' # only show min and sec

    """

    def __init__(self, locator, tz=None, defaultfmt='%Y-%m-%d'):
        """
        Autofmt the date labels.  The default format is the one to use
        if none of the times in scaled match
        """
        self._locator = locator
        self._tz = tz
        self.defaultfmt = defaultfmt
        self._formatter = DateFormatter(self.defaultfmt, tz)
        self.scaled = {365.0: '%Y', 
           30.0: '%b %Y', 
           1.0: '%b %d %Y', 
           1.0 / 24.0: '%H:%M:%S'}

    def __call__(self, x, pos=0):
        scale = float(self._locator._get_unit())
        fmt = self.defaultfmt
        for k in sorted(self.scaled):
            if k >= scale:
                fmt = self.scaled[k]
                break

        self._formatter = DateFormatter(fmt, self._tz)
        return self._formatter(x, pos)


class rrulewrapper:

    def __init__(self, freq, **kwargs):
        self._construct = kwargs.copy()
        self._construct['freq'] = freq
        self._rrule = rrule(**self._construct)

    def set(self, **kwargs):
        self._construct.update(kwargs)
        self._rrule = rrule(**self._construct)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self._rrule, name)


class DateLocator(ticker.Locator):
    hms0d = {'byhour': 0, 'byminute': 0, 'bysecond': 0}

    def __init__(self, tz=None):
        """
        *tz* is a :class:`tzinfo` instance.
        """
        if tz is None:
            tz = _get_rc_timezone()
        self.tz = tz
        return

    def set_tzinfo(self, tz):
        self.tz = tz

    def datalim_to_dt(self):
        dmin, dmax = self.axis.get_data_interval()
        return (num2date(dmin, self.tz), num2date(dmax, self.tz))

    def viewlim_to_dt(self):
        vmin, vmax = self.axis.get_view_interval()
        return (num2date(vmin, self.tz), num2date(vmax, self.tz))

    def _get_unit(self):
        """
        Return how many days a unit of the locator is; used for
        intelligent autoscaling.
        """
        return 1

    def _get_interval(self):
        """
        Return the number of units for each tick.
        """
        return 1

    def nonsingular(self, vmin, vmax):
        unit = self._get_unit()
        interval = self._get_interval()
        if abs(vmax - vmin) < 1e-06:
            vmin -= 2 * unit * interval
            vmax += 2 * unit * interval
        return (
         vmin, vmax)


class RRuleLocator(DateLocator):

    def __init__(self, o, tz=None):
        DateLocator.__init__(self, tz)
        self.rule = o

    def __call__(self):
        try:
            dmin, dmax = self.viewlim_to_dt()
        except ValueError:
            return []

        if dmin > dmax:
            dmax, dmin = dmin, dmax
        delta = relativedelta(dmax, dmin)
        try:
            start = dmin - delta
        except ValueError:
            start = _from_ordinalf(1.0)

        try:
            stop = dmax + delta
        except ValueError:
            stop = _from_ordinalf(3652059.9999999)

        self.rule.set(dtstart=start, until=stop, count=self.MAXTICKS + 1)
        nmax, nmin = date2num((dmax, dmin))
        estimate = (nmax - nmin) / (self._get_unit() * self._get_interval())
        if estimate > self.MAXTICKS * 2:
            raise RuntimeError('RRuleLocator estimated to generate %d ticks from %s to %s: exceeds Locator.MAXTICKS * 2 (%d) ' % (estimate, dmin, dmax, self.MAXTICKS * 2))
        dates = self.rule.between(dmin, dmax, True)
        if len(dates) == 0:
            return date2num([dmin, dmax])
        return self.raise_if_exceeds(date2num(dates))

    def _get_unit(self):
        """
        Return how many days a unit of the locator is; used for
        intelligent autoscaling.
        """
        freq = self.rule._rrule._freq
        return self.get_unit_generic(freq)

    def get_unit_generic(freq):
        if freq == YEARLY:
            return 365.0
        else:
            if freq == MONTHLY:
                return 30.0
            if freq == WEEKLY:
                return 7.0
            if freq == DAILY:
                return 1.0
            if freq == HOURLY:
                return 1.0 / 24.0
            if freq == MINUTELY:
                return 1.0 / 1440
            if freq == SECONDLY:
                return 1.0 / 86400
            return -1

    get_unit_generic = staticmethod(get_unit_generic)

    def _get_interval(self):
        return self.rule._rrule._interval

    def autoscale(self):
        """
        Set the view limits to include the data range.
        """
        dmin, dmax = self.datalim_to_dt()
        if dmin > dmax:
            dmax, dmin = dmin, dmax
        delta = relativedelta(dmax, dmin)
        try:
            start = dmin - delta
        except ValueError:
            start = _from_ordinalf(1.0)

        try:
            stop = dmax + delta
        except ValueError:
            stop = _from_ordinalf(3652059.9999999)

        self.rule.set(dtstart=start, until=stop)
        dmin, dmax = self.datalim_to_dt()
        vmin = self.rule.before(dmin, True)
        if not vmin:
            vmin = dmin
        vmax = self.rule.after(dmax, True)
        if not vmax:
            vmax = dmax
        vmin = date2num(vmin)
        vmax = date2num(vmax)
        return self.nonsingular(vmin, vmax)


class AutoDateLocator(DateLocator):
    """
    On autoscale, this class picks the best
    :class:`MultipleDateLocator` to set the view limits and the tick
    locations.
    """

    def __init__(self, tz=None, minticks=5, maxticks=None, interval_multiples=False):
        """
        *minticks* is the minimum number of ticks desired, which is used to
        select the type of ticking (yearly, monthly, etc.).

        *maxticks* is the maximum number of ticks desired, which controls
        any interval between ticks (ticking every other, every 3, etc.).
        For really fine-grained control, this can be a dictionary mapping
        individual rrule frequency constants (YEARLY, MONTHLY, etc.)
        to their own maximum number of ticks.  This can be used to keep
        the number of ticks appropriate to the format chosen in
        class:`AutoDateFormatter`. Any frequency not specified in this
        dictionary is given a default value.

        *tz* is a :class:`tzinfo` instance.

        *interval_multiples* is a boolean that indicates whether ticks
        should be chosen to be multiple of the interval. This will lock
        ticks to 'nicer' locations. For example, this will force the
        ticks to be at hours 0,6,12,18 when hourly ticking is done at
        6 hour intervals.

        The AutoDateLocator has an interval dictionary that maps the
        frequency of the tick (a constant from dateutil.rrule) and a
        multiple allowed for that ticking.  The default looks like this::

          self.intervald = {
            YEARLY  : [1, 2, 4, 5, 10],
            MONTHLY : [1, 2, 3, 4, 6],
            DAILY   : [1, 2, 3, 7, 14],
            HOURLY  : [1, 2, 3, 4, 6, 12],
            MINUTELY: [1, 5, 10, 15, 30],
            SECONDLY: [1, 5, 10, 15, 30]
            }

        The interval is used to specify multiples that are appropriate for
        the frequency of ticking. For instance, every 7 days is sensible
        for daily ticks, but for minutes/seconds, 15 or 30 make sense.
        You can customize this dictionary by doing::

          locator = AutoDateLocator()
          locator.intervald[HOURLY] = [3] # only show every 3 hours
        """
        DateLocator.__init__(self, tz)
        self._locator = YearLocator()
        self._freq = YEARLY
        self._freqs = [YEARLY, MONTHLY, DAILY, HOURLY, MINUTELY, SECONDLY]
        self.minticks = minticks
        self.maxticks = {YEARLY: 16, MONTHLY: 12, DAILY: 11, HOURLY: 16, MINUTELY: 11, 
           SECONDLY: 11}
        if maxticks is not None:
            try:
                self.maxticks.update(maxticks)
            except TypeError:
                self.maxticks = dict(izip(self._freqs, [
                 maxticks] * len(self._freqs)))

        self.interval_multiples = interval_multiples
        self.intervald = {YEARLY: [
                  1, 2, 4, 5, 10], 
           MONTHLY: [
                   1, 2, 3, 4, 6], 
           DAILY: [
                 1, 2, 3, 7, 14], 
           HOURLY: [
                  1, 2, 3, 4, 6, 12], 
           MINUTELY: [
                    1, 5, 10, 15, 30], 
           SECONDLY: [
                    1, 5, 10, 15, 30]}
        self._byranges = [
         None, range(1, 13), range(1, 32), range(0, 24),
         range(0, 60), range(0, 60)]
        return

    def __call__(self):
        """Return the locations of the ticks"""
        self.refresh()
        return self._locator()

    def set_axis(self, axis):
        DateLocator.set_axis(self, axis)
        self._locator.set_axis(axis)

    def refresh(self):
        """Refresh internal information based on current limits."""
        dmin, dmax = self.viewlim_to_dt()
        self._locator = self.get_locator(dmin, dmax)

    def _get_unit(self):
        return RRuleLocator.get_unit_generic(self._freq)

    def autoscale(self):
        """Try to choose the view limits intelligently."""
        dmin, dmax = self.datalim_to_dt()
        self._locator = self.get_locator(dmin, dmax)
        return self._locator.autoscale()

    def get_locator(self, dmin, dmax):
        """Pick the best locator based on a distance."""
        delta = relativedelta(dmax, dmin)
        numYears = delta.years * 1.0
        numMonths = numYears * 12.0 + delta.months
        numDays = numMonths * 31.0 + delta.days
        numHours = numDays * 24.0 + delta.hours
        numMinutes = numHours * 60.0 + delta.minutes
        numSeconds = numMinutes * 60.0 + delta.seconds
        nums = [
         numYears, numMonths, numDays, numHours, numMinutes, 
         numSeconds]
        byranges = [
         None, 1, 1, 0, 0, 0]
        for i, (freq, num) in enumerate(izip(self._freqs, nums)):
            if num < self.minticks:
                byranges[i] = None
                continue
            for interval in self.intervald[freq]:
                if num <= interval * (self.maxticks[freq] - 1):
                    break
            else:
                interval = 1

            self._freq = freq
            if self._byranges[i] and self.interval_multiples:
                byranges[i] = self._byranges[i][::interval]
                interval = 1
            else:
                byranges[i] = self._byranges[i]
            break
        else:
            byranges = [
             None, 1, 1, 0, 0, 0]
            interval = 1

        unused, bymonth, bymonthday, byhour, byminute, bysecond = byranges
        del unused
        rrule = rrulewrapper(self._freq, interval=interval, dtstart=dmin, until=dmax, bymonth=bymonth, bymonthday=bymonthday, byhour=byhour, byminute=byminute, bysecond=bysecond)
        locator = RRuleLocator(rrule, self.tz)
        locator.set_axis(self.axis)
        locator.set_view_interval(*self.axis.get_view_interval())
        locator.set_data_interval(*self.axis.get_data_interval())
        return locator


class YearLocator(DateLocator):
    """
    Make ticks on a given day of each year that is a multiple of base.

    Examples::

      # Tick every year on Jan 1st
      locator = YearLocator()

      # Tick every 5 years on July 4th
      locator = YearLocator(5, month=7, day=4)
    """

    def __init__(self, base=1, month=1, day=1, tz=None):
        """
        Mark years that are multiple of base on a given month and day
        (default jan 1).
        """
        DateLocator.__init__(self, tz)
        self.base = ticker.Base(base)
        self.replaced = {'month': month, 'day': day, 
           'hour': 0, 
           'minute': 0, 
           'second': 0, 
           'tzinfo': tz}

    def __call__(self):
        dmin, dmax = self.viewlim_to_dt()
        ymin = self.base.le(dmin.year)
        ymax = self.base.ge(dmax.year)
        ticks = [
         dmin.replace(year=ymin, **self.replaced)]
        while 1:
            dt = ticks[-1]
            if dt.year >= ymax:
                return date2num(ticks)
            year = dt.year + self.base.get_base()
            ticks.append(dt.replace(year=year, **self.replaced))

    def autoscale(self):
        """
        Set the view limits to include the data range.
        """
        dmin, dmax = self.datalim_to_dt()
        ymin = self.base.le(dmin.year)
        ymax = self.base.ge(dmax.year)
        vmin = dmin.replace(year=ymin, **self.replaced)
        vmax = dmax.replace(year=ymax, **self.replaced)
        vmin = date2num(vmin)
        vmax = date2num(vmax)
        return self.nonsingular(vmin, vmax)


class MonthLocator(RRuleLocator):
    """
    Make ticks on occurances of each month month, eg 1, 3, 12.
    """

    def __init__(self, bymonth=None, bymonthday=1, interval=1, tz=None):
        """
        Mark every month in *bymonth*; *bymonth* can be an int or
        sequence.  Default is ``range(1,13)``, i.e. every month.

        *interval* is the interval between each iteration.  For
        example, if ``interval=2``, mark every second occurance.
        """
        if bymonth is None:
            bymonth = range(1, 13)
        o = rrulewrapper(MONTHLY, bymonth=bymonth, bymonthday=bymonthday, interval=interval, **self.hms0d)
        RRuleLocator.__init__(self, o, tz)
        return


class WeekdayLocator(RRuleLocator):
    """
    Make ticks on occurances of each weekday.
    """

    def __init__(self, byweekday=1, interval=1, tz=None):
        """
        Mark every weekday in *byweekday*; *byweekday* can be a number or
        sequence.

        Elements of *byweekday* must be one of MO, TU, WE, TH, FR, SA,
        SU, the constants from :mod:`dateutils.rrule`.

        *interval* specifies the number of weeks to skip.  For example,
        ``interval=2`` plots every second week.
        """
        o = rrulewrapper(DAILY, byweekday=byweekday, interval=interval, **self.hms0d)
        RRuleLocator.__init__(self, o, tz)


class DayLocator(RRuleLocator):
    """
    Make ticks on occurances of each day of the month.  For example,
    1, 15, 30.
    """

    def __init__(self, bymonthday=None, interval=1, tz=None):
        """
        Mark every day in *bymonthday*; *bymonthday* can be an int or
        sequence.

        Default is to tick every day of the month: ``bymonthday=range(1,32)``
        """
        if bymonthday is None:
            bymonthday = range(1, 32)
        o = rrulewrapper(DAILY, bymonthday=bymonthday, interval=interval, **self.hms0d)
        RRuleLocator.__init__(self, o, tz)
        return


class HourLocator(RRuleLocator):
    """
    Make ticks on occurances of each hour.
    """

    def __init__(self, byhour=None, interval=1, tz=None):
        """
        Mark every hour in *byhour*; *byhour* can be an int or sequence.
        Default is to tick every hour: ``byhour=range(24)``

        *interval* is the interval between each iteration.  For
        example, if ``interval=2``, mark every second occurrence.
        """
        if byhour is None:
            byhour = range(24)
        rule = rrulewrapper(HOURLY, byhour=byhour, interval=interval, byminute=0, bysecond=0)
        RRuleLocator.__init__(self, rule, tz)
        return


class MinuteLocator(RRuleLocator):
    """
    Make ticks on occurances of each minute.
    """

    def __init__(self, byminute=None, interval=1, tz=None):
        """
        Mark every minute in *byminute*; *byminute* can be an int or
        sequence.  Default is to tick every minute: ``byminute=range(60)``

        *interval* is the interval between each iteration.  For
        example, if ``interval=2``, mark every second occurrence.
        """
        if byminute is None:
            byminute = range(60)
        rule = rrulewrapper(MINUTELY, byminute=byminute, interval=interval, bysecond=0)
        RRuleLocator.__init__(self, rule, tz)
        return


class SecondLocator(RRuleLocator):
    """
    Make ticks on occurances of each second.
    """

    def __init__(self, bysecond=None, interval=1, tz=None):
        """
        Mark every second in *bysecond*; *bysecond* can be an int or
        sequence.  Default is to tick every second: ``bysecond = range(60)``

        *interval* is the interval between each iteration.  For
        example, if ``interval=2``, mark every second occurrence.

        """
        if bysecond is None:
            bysecond = range(60)
        rule = rrulewrapper(SECONDLY, bysecond=bysecond, interval=interval)
        RRuleLocator.__init__(self, rule, tz)
        return


def _close_to_dt(d1, d2, epsilon=5):
    """Assert that datetimes *d1* and *d2* are within *epsilon* microseconds."""
    delta = d2 - d1
    mus = abs(delta.days * MUSECONDS_PER_DAY + delta.seconds * 1000000.0 + delta.microseconds)
    assert mus < epsilon


def _close_to_num(o1, o2, epsilon=5):
    """Assert that float ordinals *o1* and *o2* are within *epsilon* microseconds."""
    delta = abs((o2 - o1) * MUSECONDS_PER_DAY)
    assert delta < epsilon


def epoch2num(e):
    """
    Convert an epoch or sequence of epochs to the new date format,
    that is days since 0001.
    """
    spd = 86400.0
    return 719163 + np.asarray(e) / spd


def num2epoch(d):
    """
    Convert days since 0001 to epoch.  *d* can be a number or sequence.
    """
    spd = 86400.0
    return (np.asarray(d) - 719163) * spd


def mx2num(mxdates):
    """
    Convert mx :class:`datetime` instance (or sequence of mx
    instances) to the new date format.
    """
    scalar = False
    if not cbook.iterable(mxdates):
        scalar = True
        mxdates = [mxdates]
    ret = epoch2num([ m.ticks() for m in mxdates ])
    if scalar:
        return ret[0]
    else:
        return ret


def date_ticker_factory(span, tz=None, numticks=5):
    """
    Create a date locator with *numticks* (approx) and a date formatter
    for *span* in days.  Return value is (locator, formatter).
    """
    if span == 0:
        span = 1 / 24.0
    minutes = span * 24 * 60
    hours = span * 24
    days = span
    weeks = span / 7.0
    months = span / 31.0
    years = span / 365.0
    if years > numticks:
        locator = YearLocator(int(years / numticks), tz=tz)
        fmt = '%Y'
    elif months > numticks:
        locator = MonthLocator(tz=tz)
        fmt = '%b %Y'
    elif weeks > numticks:
        locator = WeekdayLocator(tz=tz)
        fmt = '%a, %b %d'
    elif days > numticks:
        locator = DayLocator(interval=int(math.ceil(days / numticks)), tz=tz)
        fmt = '%b %d'
    elif hours > numticks:
        locator = HourLocator(interval=int(math.ceil(hours / numticks)), tz=tz)
        fmt = '%H:%M\n%b %d'
    elif minutes > numticks:
        locator = MinuteLocator(interval=int(math.ceil(minutes / numticks)), tz=tz)
        fmt = '%H:%M:%S'
    else:
        locator = MinuteLocator(tz=tz)
        fmt = '%H:%M:%S'
    formatter = DateFormatter(fmt, tz=tz)
    return (locator, formatter)


def seconds(s):
    """Return seconds as days."""
    return float(s) / SEC_PER_DAY


def minutes(m):
    """Return minutes as days."""
    return float(m) / MINUTES_PER_DAY


def hours(h):
    """Return hours as days."""
    return h / 24.0


def weeks(w):
    """Return weeks as days."""
    return w * 7.0


class DateConverter(units.ConversionInterface):
    """
    Converter for datetime.date and datetime.datetime data,
    or for date/time data represented as it would be converted
    by :func:`date2num`.

    The 'unit' tag for such data is None or a tzinfo instance.
    """

    @staticmethod
    def axisinfo(unit, axis):
        """
        Return the :class:`~matplotlib.units.AxisInfo` for *unit*.

        *unit* is a tzinfo instance or None.
        The *axis* argument is required but not used.
        """
        tz = unit
        majloc = AutoDateLocator(tz=tz)
        majfmt = AutoDateFormatter(majloc, tz=tz)
        datemin = datetime.date(2000, 1, 1)
        datemax = datetime.date(2010, 1, 1)
        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='', default_limits=(
         datemin, datemax))

    @staticmethod
    def convert(value, unit, axis):
        """
        If *value* is not already a number or sequence of numbers,
        convert it with :func:`date2num`.

        The *unit* and *axis* arguments are not used.
        """
        if units.ConversionInterface.is_numlike(value):
            return value
        return date2num(value)

    @staticmethod
    def default_units(x, axis):
        """Return the tzinfo instance of *x* or of its first element, or None"""
        try:
            x = x[0]
        except (TypeError, IndexError):
            pass

        try:
            return x.tzinfo
        except AttributeError:
            pass

        return


units.registry[datetime.date] = DateConverter()
units.registry[datetime.datetime] = DateConverter()
if __name__ == '__main__':
    tz = pytz.timezone('US/Pacific')
    dt = datetime.datetime(1011, 10, 9, 13, 44, 22, 101010, tzinfo=tz)
    x = date2num(dt)
    _close_to_dt(dt, num2date(x, tz))
    d1 = datetime.datetime(2000, 3, 1, tzinfo=tz)
    d2 = datetime.datetime(2000, 3, 5, tzinfo=tz)
    delta = datetime.timedelta(hours=6)
    dates = drange(d1, d2, delta)
    from _transforms import Value, Interval
    v1 = Value(date2num(d1))
    v2 = Value(date2num(d2))
    dlim = Interval(v1, v2)
    vlim = Interval(v1, v2)
    locator = DayLocator(tz=tz)
    locator.set_data_interval(dlim)
    locator.set_view_interval(vlim)
    dmin, dmax = locator.autoscale()
    vlim.set_bounds(dmin, dmax)
    ticks = locator()
    fmt = '%Y-%m-%d %H:%M:%S %Z'
    formatter = DateFormatter(fmt, tz)
    for t in dates:
        print(formatter(t))