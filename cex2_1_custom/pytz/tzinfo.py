# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: pytz\tzinfo.pyc
# Compiled at: 2012-11-06 15:31:10
"""Base classes and helpers for building zone specific tzinfo classes"""
from datetime import datetime, timedelta, tzinfo
from bisect import bisect_right
try:
    set
except NameError:
    from sets import Set as set

import pytz
from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError
__all__ = []
_timedelta_cache = {}

def memorized_timedelta(seconds):
    """Create only one instance of each distinct timedelta"""
    try:
        return _timedelta_cache[seconds]
    except KeyError:
        delta = timedelta(seconds=seconds)
        _timedelta_cache[seconds] = delta
        return delta


_epoch = datetime.utcfromtimestamp(0)
_datetime_cache = {0: _epoch}

def memorized_datetime(seconds):
    """Create only one instance of each distinct datetime"""
    try:
        return _datetime_cache[seconds]
    except KeyError:
        dt = _epoch + timedelta(seconds=seconds)
        _datetime_cache[seconds] = dt
        return dt


_ttinfo_cache = {}

def memorized_ttinfo(*args):
    """Create only one instance of each distinct tuple"""
    try:
        return _ttinfo_cache[args]
    except KeyError:
        ttinfo = (
         memorized_timedelta(args[0]),
         memorized_timedelta(args[1]),
         args[2])
        _ttinfo_cache[args] = ttinfo
        return ttinfo


_notime = memorized_timedelta(0)

def _to_seconds(td):
    """Convert a timedelta to seconds"""
    return td.seconds + td.days * 24 * 60 * 60


class BaseTzInfo(tzinfo):
    _utcoffset = None
    _tzname = None
    zone = None

    def __str__(self):
        return self.zone


class StaticTzInfo(BaseTzInfo):
    """A timezone that has a constant offset from UTC

    These timezones are rare, as most locations have changed their
    offset at some point in their history
    """

    def fromutc(self, dt):
        """See datetime.tzinfo.fromutc"""
        if dt.tzinfo is not None and dt.tzinfo is not self:
            raise ValueError('fromutc: dt.tzinfo is not self')
        return (dt + self._utcoffset).replace(tzinfo=self)

    def utcoffset(self, dt, is_dst=None):
        """See datetime.tzinfo.utcoffset

        is_dst is ignored for StaticTzInfo, and exists only to
        retain compatibility with DstTzInfo.
        """
        return self._utcoffset

    def dst(self, dt, is_dst=None):
        """See datetime.tzinfo.dst

        is_dst is ignored for StaticTzInfo, and exists only to
        retain compatibility with DstTzInfo.
        """
        return _notime

    def tzname(self, dt, is_dst=None):
        """See datetime.tzinfo.tzname

        is_dst is ignored for StaticTzInfo, and exists only to
        retain compatibility with DstTzInfo.
        """
        return self._tzname

    def localize(self, dt, is_dst=False):
        """Convert naive time to local time"""
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        """Correct the timezone information on the given datetime.

        This is normally a no-op, as StaticTzInfo timezones never have
        ambiguous cases to correct:

        >>> from pytz import timezone
        >>> gmt = timezone('GMT')
        >>> isinstance(gmt, StaticTzInfo)
        True
        >>> dt = datetime(2011, 5, 8, 1, 2, 3, tzinfo=gmt)
        >>> gmt.normalize(dt) is dt
        True

        The supported method of converting between timezones is to use
        datetime.astimezone(). Currently normalize() also works:

        >>> la = timezone('America/Los_Angeles')
        >>> dt = la.localize(datetime(2011, 5, 7, 1, 2, 3))
        >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
        >>> gmt.normalize(dt).strftime(fmt)
        '2011-05-07 08:02:03 GMT (+0000)'
        """
        if dt.tzinfo is self:
            return dt
        else:
            if dt.tzinfo is None:
                raise ValueError('Naive time - no tzinfo set')
            return dt.astimezone(self)

    def __repr__(self):
        return '<StaticTzInfo %r>' % (self.zone,)

    def __reduce__(self):
        return (
         pytz._p, (self.zone,))


class DstTzInfo(BaseTzInfo):
    """A timezone that has a variable offset from UTC

    The offset might change if daylight savings time comes into effect,
    or at a point in history when the region decides to change their
    timezone definition.
    """
    _utc_transition_times = None
    _transition_info = None
    zone = None
    _tzinfos = None
    _dst = None

    def __init__(self, _inf=None, _tzinfos=None):
        if _inf:
            self._tzinfos = _tzinfos
            self._utcoffset, self._dst, self._tzname = _inf
        else:
            _tzinfos = {}
            self._tzinfos = _tzinfos
            self._utcoffset, self._dst, self._tzname = self._transition_info[0]
            _tzinfos[self._transition_info[0]] = self
            for inf in self._transition_info[1:]:
                if inf not in _tzinfos:
                    _tzinfos[inf] = self.__class__(inf, _tzinfos)

    def fromutc(self, dt):
        """See datetime.tzinfo.fromutc"""
        if dt.tzinfo is not None and getattr(dt.tzinfo, '_tzinfos', None) is not self._tzinfos:
            raise ValueError('fromutc: dt.tzinfo is not self')
        dt = dt.replace(tzinfo=None)
        idx = max(0, bisect_right(self._utc_transition_times, dt) - 1)
        inf = self._transition_info[idx]
        return (dt + inf[0]).replace(tzinfo=self._tzinfos[inf])

    def normalize(self, dt):
        """Correct the timezone information on the given datetime

        If date arithmetic crosses DST boundaries, the tzinfo
        is not magically adjusted. This method normalizes the
        tzinfo to the correct one.

        To test, first we need to do some setup

        >>> from pytz import timezone
        >>> utc = timezone('UTC')
        >>> eastern = timezone('US/Eastern')
        >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'

        We next create a datetime right on an end-of-DST transition point,
        the instant when the wallclocks are wound back one hour.

        >>> utc_dt = datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc)
        >>> loc_dt = utc_dt.astimezone(eastern)
        >>> loc_dt.strftime(fmt)
        '2002-10-27 01:00:00 EST (-0500)'

        Now, if we subtract a few minutes from it, note that the timezone
        information has not changed.

        >>> before = loc_dt - timedelta(minutes=10)
        >>> before.strftime(fmt)
        '2002-10-27 00:50:00 EST (-0500)'

        But we can fix that by calling the normalize method

        >>> before = eastern.normalize(before)
        >>> before.strftime(fmt)
        '2002-10-27 01:50:00 EDT (-0400)'

        The supported method of converting between timezones is to use
        datetime.astimezone(). Currently, normalize() also works:

        >>> th = timezone('Asia/Bangkok')
        >>> am = timezone('Europe/Amsterdam')
        >>> dt = th.localize(datetime(2011, 5, 7, 1, 2, 3))
        >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
        >>> am.normalize(dt).strftime(fmt)
        '2011-05-06 20:02:03 CEST (+0200)'
        """
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        offset = dt.tzinfo._utcoffset
        dt = dt.replace(tzinfo=None)
        dt = dt - offset
        return self.fromutc(dt)

    def localize(self, dt, is_dst=False):
        """Convert naive time to local time.

        This method should be used to construct localtimes, rather
        than passing a tzinfo argument to a datetime constructor.

        is_dst is used to determine the correct timezone in the ambigous
        period at the end of daylight savings time.

        >>> from pytz import timezone
        >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
        >>> amdam = timezone('Europe/Amsterdam')
        >>> dt  = datetime(2004, 10, 31, 2, 0, 0)
        >>> loc_dt1 = amdam.localize(dt, is_dst=True)
        >>> loc_dt2 = amdam.localize(dt, is_dst=False)
        >>> loc_dt1.strftime(fmt)
        '2004-10-31 02:00:00 CEST (+0200)'
        >>> loc_dt2.strftime(fmt)
        '2004-10-31 02:00:00 CET (+0100)'
        >>> str(loc_dt2 - loc_dt1)
        '1:00:00'

        Use is_dst=None to raise an AmbiguousTimeError for ambiguous
        times at the end of daylight savings

        >>> try:
        ...     loc_dt1 = amdam.localize(dt, is_dst=None)
        ... except AmbiguousTimeError:
        ...     print('Ambiguous')
        Ambiguous

        is_dst defaults to False

        >>> amdam.localize(dt) == amdam.localize(dt, False)
        True

        is_dst is also used to determine the correct timezone in the
        wallclock times jumped over at the start of daylight savings time.

        >>> pacific = timezone('US/Pacific')
        >>> dt = datetime(2008, 3, 9, 2, 0, 0)
        >>> ploc_dt1 = pacific.localize(dt, is_dst=True)
        >>> ploc_dt2 = pacific.localize(dt, is_dst=False)
        >>> ploc_dt1.strftime(fmt)
        '2008-03-09 02:00:00 PDT (-0700)'
        >>> ploc_dt2.strftime(fmt)
        '2008-03-09 02:00:00 PST (-0800)'
        >>> str(ploc_dt2 - ploc_dt1)
        '1:00:00'

        Use is_dst=None to raise a NonExistentTimeError for these skipped
        times.

        >>> try:
        ...     loc_dt1 = pacific.localize(dt, is_dst=None)
        ... except NonExistentTimeError:
        ...     print('Non-existent')
        Non-existent
        """
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        possible_loc_dt = set()
        for delta in [timedelta(days=-1), timedelta(days=1)]:
            loc_dt = dt + delta
            idx = max(0, bisect_right(self._utc_transition_times, loc_dt) - 1)
            inf = self._transition_info[idx]
            tzinfo = self._tzinfos[inf]
            loc_dt = tzinfo.normalize(dt.replace(tzinfo=tzinfo))
            if loc_dt.replace(tzinfo=None) == dt:
                possible_loc_dt.add(loc_dt)

        if len(possible_loc_dt) == 1:
            return possible_loc_dt.pop()
        else:
            if len(possible_loc_dt) == 0:
                if is_dst is None:
                    raise NonExistentTimeError(dt)
                else:
                    if is_dst:
                        return self.localize(dt + timedelta(hours=6), is_dst=True) - timedelta(hours=6)
                    else:
                        return self.localize(dt - timedelta(hours=6), is_dst=False) + timedelta(hours=6)

            if is_dst is None:
                raise AmbiguousTimeError(dt)
            filtered_possible_loc_dt = [ p for p in possible_loc_dt if bool(p.tzinfo._dst) == is_dst
                                       ]
            if len(filtered_possible_loc_dt) == 1:
                return filtered_possible_loc_dt[0]
            if len(filtered_possible_loc_dt) == 0:
                filtered_possible_loc_dt = list(possible_loc_dt)
            sorting_keys = {}
            for local_dt in filtered_possible_loc_dt:
                key = local_dt.replace(tzinfo=None) - local_dt.tzinfo._utcoffset
                sorting_keys[key] = local_dt

            first_key = sorted(sorting_keys)[0]
            return sorting_keys[first_key]

    def utcoffset(self, dt, is_dst=None):
        """See datetime.tzinfo.utcoffset

        The is_dst parameter may be used to remove ambiguity during DST
        transitions.

        >>> from pytz import timezone
        >>> tz = timezone('America/St_Johns')
        >>> ambiguous = datetime(2009, 10, 31, 23, 30)

        >>> tz.utcoffset(ambiguous, is_dst=False)
        datetime.timedelta(-1, 73800)

        >>> tz.utcoffset(ambiguous, is_dst=True)
        datetime.timedelta(-1, 77400)

        >>> try:
        ...     tz.utcoffset(ambiguous)
        ... except AmbiguousTimeError:
        ...     print('Ambiguous')
        Ambiguous

        """
        if dt is None:
            return
        else:
            if dt.tzinfo is not self:
                dt = self.localize(dt, is_dst)
                return dt.tzinfo._utcoffset
            else:
                return self._utcoffset

            return

    def dst(self, dt, is_dst=None):
        """See datetime.tzinfo.dst

        The is_dst parameter may be used to remove ambiguity during DST
        transitions.

        >>> from pytz import timezone
        >>> tz = timezone('America/St_Johns')

        >>> normal = datetime(2009, 9, 1)

        >>> tz.dst(normal)
        datetime.timedelta(0, 3600)
        >>> tz.dst(normal, is_dst=False)
        datetime.timedelta(0, 3600)
        >>> tz.dst(normal, is_dst=True)
        datetime.timedelta(0, 3600)

        >>> ambiguous = datetime(2009, 10, 31, 23, 30)

        >>> tz.dst(ambiguous, is_dst=False)
        datetime.timedelta(0)
        >>> tz.dst(ambiguous, is_dst=True)
        datetime.timedelta(0, 3600)
        >>> try:
        ...     tz.dst(ambiguous)
        ... except AmbiguousTimeError:
        ...     print('Ambiguous')
        Ambiguous

        """
        if dt is None:
            return
        else:
            if dt.tzinfo is not self:
                dt = self.localize(dt, is_dst)
                return dt.tzinfo._dst
            else:
                return self._dst

            return

    def tzname(self, dt, is_dst=None):
        """See datetime.tzinfo.tzname

        The is_dst parameter may be used to remove ambiguity during DST
        transitions.

        >>> from pytz import timezone
        >>> tz = timezone('America/St_Johns')

        >>> normal = datetime(2009, 9, 1)

        >>> tz.tzname(normal)
        'NDT'
        >>> tz.tzname(normal, is_dst=False)
        'NDT'
        >>> tz.tzname(normal, is_dst=True)
        'NDT'

        >>> ambiguous = datetime(2009, 10, 31, 23, 30)

        >>> tz.tzname(ambiguous, is_dst=False)
        'NST'
        >>> tz.tzname(ambiguous, is_dst=True)
        'NDT'
        >>> try:
        ...     tz.tzname(ambiguous)
        ... except AmbiguousTimeError:
        ...     print('Ambiguous')
        Ambiguous
        """
        if dt is None:
            return self.zone
        else:
            if dt.tzinfo is not self:
                dt = self.localize(dt, is_dst)
                return dt.tzinfo._tzname
            else:
                return self._tzname

            return

    def __repr__(self):
        if self._dst:
            dst = 'DST'
        else:
            dst = 'STD'
        if self._utcoffset > _notime:
            return '<DstTzInfo %r %s+%s %s>' % (
             self.zone, self._tzname, self._utcoffset, dst)
        else:
            return '<DstTzInfo %r %s%s %s>' % (
             self.zone, self._tzname, self._utcoffset, dst)

    def __reduce__(self):
        return (
         pytz._p,
         (
          self.zone,
          _to_seconds(self._utcoffset),
          _to_seconds(self._dst),
          self._tzname))


def unpickler(zone, utcoffset=None, dstoffset=None, tzname=None):
    """Factory function for unpickling pytz tzinfo instances.

    This is shared for both StaticTzInfo and DstTzInfo instances, because
    database changes could cause a zones implementation to switch between
    these two base classes and we can't break pickles on a pytz version
    upgrade.
    """
    tz = pytz.timezone(zone)
    if utcoffset is None:
        return tz
    else:
        utcoffset = memorized_timedelta(utcoffset)
        dstoffset = memorized_timedelta(dstoffset)
        try:
            return tz._tzinfos[(utcoffset, dstoffset, tzname)]
        except KeyError:
            pass

        for localized_tz in tz._tzinfos.values():
            if localized_tz._utcoffset == utcoffset and localized_tz._dst == dstoffset:
                return localized_tz

        inf = (
         utcoffset, dstoffset, tzname)
        tz._tzinfos[inf] = tz.__class__(inf, tz._tzinfos)
        return tz._tzinfos[inf]