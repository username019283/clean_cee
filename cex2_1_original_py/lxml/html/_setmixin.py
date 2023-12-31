# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: c:\python27\lib\site-packages\lxml-3.2.4-py2.7-win32.egg\lxml\html\_setmixin.py
# Compiled at: 2013-12-10 09:11:58


class SetMixin(object):
    """
    Mix-in for sets.  You must define __iter__, add, remove
    """

    def __len__(self):
        length = 0
        for item in self:
            length += 1

        return length

    def __contains__(self, item):
        for has_item in self:
            if item == has_item:
                return True

        return False

    def issubset(self, other):
        for item in other:
            if item not in self:
                return False

        return True

    __le__ = issubset

    def issuperset(self, other):
        for item in self:
            if item not in other:
                return False

        return True

    __ge__ = issuperset

    def union(self, other):
        return self | other

    def __or__(self, other):
        new = self.copy()
        new |= other
        return new

    def intersection(self, other):
        return self & other

    def __and__(self, other):
        new = self.copy()
        new &= other
        return new

    def difference(self, other):
        return self - other

    def __sub__(self, other):
        new = self.copy()
        new -= other
        return new

    def symmetric_difference(self, other):
        return self ^ other

    def __xor__(self, other):
        new = self.copy()
        new ^= other
        return new

    def copy(self):
        return set(self)

    def update(self, other):
        for item in other:
            self.add(item)

    def __ior__(self, other):
        self.update(other)
        return self

    def intersection_update(self, other):
        for item in self:
            if item not in other:
                self.remove(item)

    def __iand__(self, other):
        self.intersection_update(other)
        return self

    def difference_update(self, other):
        for item in other:
            if item in self:
                self.remove(item)

    def __isub__(self, other):
        self.difference_update(other)
        return self

    def symmetric_difference_update(self, other):
        for item in other:
            if item in self:
                self.remove(item)
            else:
                self.add(item)

    def __ixor__(self, other):
        self.symmetric_difference_update(other)
        return self

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def clear(self):
        for item in list(self):
            self.remove(item)