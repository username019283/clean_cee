# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\container.pyc
# Compiled at: 2012-11-08 06:38:04
import matplotlib.cbook as cbook

class Container(tuple):
    """
    Base class for containers.
    """

    def __repr__(self):
        return '<Container object of %d artists>' % len(self)

    def __new__(cls, *kl, **kwargs):
        return tuple.__new__(cls, kl[0])

    def __init__(self, kl, label=None):
        self.eventson = False
        self._oid = 0
        self._propobservers = {}
        self._remove_method = None
        self.set_label(label)
        return

    def set_remove_method(self, f):
        self._remove_method = f

    def remove(self):
        for c in self:
            c.remove()

        if self._remove_method:
            self._remove_method(self)

    def get_label(self):
        """
        Get the label used for this artist in the legend.
        """
        return self._label

    def set_label(self, s):
        """
        Set the label to *s* for auto legend.

        ACCEPTS: string or anything printable with '%s' conversion.
        """
        self._label = '%s' % (s,)
        self.pchanged()

    def add_callback(self, func):
        """
        Adds a callback function that will be called whenever one of
        the :class:`Artist`'s properties changes.

        Returns an *id* that is useful for removing the callback with
        :meth:`remove_callback` later.
        """
        oid = self._oid
        self._propobservers[oid] = func
        self._oid += 1
        return oid

    def remove_callback(self, oid):
        """
        Remove a callback based on its *id*.

        .. seealso::

            :meth:`add_callback`
               For adding callbacks

        """
        try:
            del self._propobservers[oid]
        except KeyError:
            pass

    def pchanged(self):
        """
        Fire an event when property changed, calling all of the
        registered callbacks.
        """
        for oid, func in self._propobservers.items():
            func(self)

    def get_children(self):
        return list(cbook.flatten(self))


class BarContainer(Container):

    def __init__(self, patches, errorbar=None, **kwargs):
        self.patches = patches
        self.errorbar = errorbar
        Container.__init__(self, patches, **kwargs)


class ErrorbarContainer(Container):

    def __init__(self, lines, has_xerr=False, has_yerr=False, **kwargs):
        self.lines = lines
        self.has_xerr = has_xerr
        self.has_yerr = has_yerr
        Container.__init__(self, lines, **kwargs)


class StemContainer(Container):

    def __init__(self, markerline_stemlines_baseline, **kwargs):
        markerline, stemlines, baseline = markerline_stemlines_baseline
        self.markerline = markerline
        self.stemlines = stemlines
        self.baseline = baseline
        Container.__init__(self, markerline_stemlines_baseline, **kwargs)