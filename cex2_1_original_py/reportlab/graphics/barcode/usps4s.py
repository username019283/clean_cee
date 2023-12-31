# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\barcode\usps4s.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__all__ = ('USPS_4State',)
from reportlab.lib.colors import black
from common import Barcode

class USPS_4State(Barcode):
    """ USPS 4-State OneView (TM) barcode. All info from USPS-B-3200A
    """
    _widthSize = 1
    _heightSize = 1
    _fontSize = 11
    _humanReadable = 0
    tops = dict(F=(0.067, 0.115), T=(0.021, 0.04), A=(0.067, 0.115), D=(0.021, 0.04))
    bottoms = dict(F=(-0.067, -0.115), D=(-0.067, -0.115), T=(-0.021, -0.04), A=(-0.021,
                                                                                 -0.04))
    dimensions = dict(width=(0.015, 0.025), pitch=(0.0416, 0.05), hcz=(0.125, 0.125), vcz=(0.04,
                                                                                           0.04))

    def __init__(self, value='01234567094987654321', routing='', **kwd):
        self._init()
        self.tracking = value
        self.routing = routing
        self._setKeywords(**kwd)

    def _init(self):
        self._bvalue = None
        self._codewords = None
        self._characters = None
        self._barcodes = None
        return

    def scale(kind, D, s):
        V = D[kind]
        return 72 * (V[0] * (1 - s) + s * V[1])

    scale = staticmethod(scale)

    def tracking(self, tracking):
        self._init()
        self._tracking = value

    tracking = property((lambda self: self._tracking), tracking)

    def routing(self, routing):
        self._init()
        self._routing = value

    routing = property((lambda self: self._routing), routing)

    def widthSize(self, value):
        self._sized = None
        self._widthSize = value
        return

    widthSize = property((lambda self: self._widthSize), widthSize)

    def heightSize(self, value):
        self._sized = None
        self._heightSize = value
        return

    heightSize = property((lambda self: self._heightSize), heightSize)

    def fontSize(self, value):
        self._sized = None
        self._fontSize = value
        return

    fontSize = property((lambda self: self._fontSize), fontSize)

    def humanReadable(self, value):
        self._sized = None
        self._humanReadable = value
        return

    humanReadable = property((lambda self: self._humanReadable), humanReadable)

    def binary(self):
        """convert the 4 state string values to binary
        >>> print hex(USPS_4State('01234567094987654321','').binary)
        0x1122103B5C2004B1L
        >>> print hex(USPS_4State('01234567094987654321','01234').binary)
        0xD138A87BAB5CF3804B1L
        >>> print hex(USPS_4State('01234567094987654321','012345678').binary)
        0x202BDC097711204D21804B1L
        >>> print hex(USPS_4State('01234567094987654321','01234567891').binary)
        0x16907B2A24ABC16A2E5C004B1L
        """
        value = self._bvalue
        if not value:
            routing = self.routing
            n = len(routing)
            try:
                if n == 0:
                    value = 0
                elif n == 5:
                    value = int(routing) + 1
                elif n == 9:
                    value = int(routing) + 100001
                elif n == 11:
                    value = int(routing) + 1000100001
                else:
                    raise ValueError
            except:
                raise ValueError('Problem converting %s, routing code must be 0, 5, 9 or 11 digits' % routing)

            tracking = self.tracking
            svalue = tracking[0:2]
            try:
                value *= 10
                value += int(svalue[0])
                value *= 5
                value += int(svalue[1])
            except:
                raise ValueError('Problem converting %s, barcode identifier must be 2 digits' % svalue)

            i = 2
            for name, nd in (('special services', 3), ('customer identifier', 6), ('sequence number', 9)):
                j = i
                i += nd
                svalue = tracking[j:i]
                try:
                    if len(svalue) != nd:
                        raise ValueError
                    for j in xrange(nd):
                        value *= 10
                        value += int(svalue[j])

                except:
                    raise ValueError('Problem converting %s, %s must be %d digits' % (svalue, name, nd))

            self._bvalue = value
        return value

    binary = property(binary)

    def codewords(self):
        """convert binary value into codewords
        >>> print USPS_4State('01234567094987654321','01234567891').codewords)
        (673, 787, 607, 1022, 861, 19, 816, 1294, 35, 602)
        """
        value = self._codewords or self.binary
        A, J = divmod(value, 636)
        A, I = divmod(A, 1365)
        A, H = divmod(A, 1365)
        A, G = divmod(A, 1365)
        A, F = divmod(A, 1365)
        A, E = divmod(A, 1365)
        A, D = divmod(A, 1365)
        A, C = divmod(A, 1365)
        A, B = divmod(A, 1365)
        if not 0 <= A <= 658:
            raise AssertionError('improper value %s passed to _2codewords A-->%s' % (hex(long(value)), A))
            self._fcs = _crc11(value)
            if self._fcs & 1024:
                A += 659
            J *= 2
            self._codewords = tuple(map(int, (A, B, C, D, E, F, G, H, I, J)))
        return self._codewords

    codewords = property(codewords)

    def table1(self):
        self.__class__.table1 = _initNof13Table(5, 1287)
        return self.__class__.table1

    table1 = property(table1)

    def table2(self):
        self.__class__.table2 = _initNof13Table(2, 78)
        return self.__class__.table2

    table2 = property(table2)

    def characters(self):
        """ convert own codewords to characters
        >>> print ' '.join(hex(c)[2:] for c in USPS_4State('01234567094987654321','01234567891').characters)
        dcb 85c 8e4 b06 6dd 1740 17c6 1200 123f 1b2b
        """
        if not self._characters:
            codewords = self.codewords
            fcs = self._fcs
            C = []
            aC = C.append
            table1 = self.table1
            table2 = self.table2
            for i in xrange(10):
                cw = codewords[i]
                if cw <= 1286:
                    c = table1[cw]
                else:
                    c = table2[cw - 1287]
                if fcs >> i & 1:
                    c = ~c & 8191
                aC(c)

            self._characters = tuple(C)
        return self._characters

    characters = property(characters)

    def barcodes(self):
        """Get 4 state bar codes for current routing and tracking
        >>> print USPS_4State('01234567094987654321','01234567891').barcodes
        AADTFFDFTDADTAADAATFDTDDAAADDTDTTDAFADADDDTFFFDDTTTADFAAADFTDAADA
        """
        if not self._barcodes:
            C = self.characters
            B = []
            aB = B.append
            bits2bars = self._bits2bars
            for dc, db, ac, ab in self.table4:
                aB(bits2bars[(C[dc] >> db & 1) + 2 * (C[ac] >> ab & 1)])

            self._barcodes = ('').join(B)
        return self._barcodes

    barcodes = property(barcodes)
    table4 = (
     (7, 2, 4, 3), (1, 10, 0, 0), (9, 12, 2, 8), (5, 5, 6, 11),
     (8, 9, 3, 1), (0, 1, 5, 12), (2, 5, 1, 8), (4, 4, 9, 11),
     (6, 3, 8, 10), (3, 9, 7, 6), (5, 11, 1, 4), (8, 5, 2, 12),
     (9, 10, 0, 2), (7, 1, 6, 7), (3, 6, 4, 9), (0, 3, 8, 6),
     (6, 4, 2, 7), (1, 1, 9, 9), (7, 10, 5, 2), (4, 0, 3, 8),
     (6, 2, 0, 4), (8, 11, 1, 0), (9, 8, 3, 12), (2, 6, 7, 7),
     (5, 1, 4, 10), (1, 12, 6, 9), (7, 3, 8, 0), (5, 8, 9, 7),
     (4, 6, 2, 10), (3, 4, 0, 5), (8, 4, 5, 7), (7, 11, 1, 9),
     (6, 0, 9, 6), (0, 6, 4, 8), (2, 1, 3, 2), (5, 9, 8, 12),
     (4, 11, 6, 1), (9, 5, 7, 4), (3, 3, 1, 2), (0, 7, 2, 0),
     (1, 3, 4, 1), (6, 10, 3, 5), (8, 7, 9, 4), (2, 11, 5, 6),
     (0, 8, 7, 12), (4, 2, 8, 1), (5, 10, 3, 0), (9, 3, 0, 9),
     (6, 5, 2, 4), (7, 8, 1, 7), (5, 0, 4, 5), (2, 3, 0, 10),
     (6, 12, 9, 2), (3, 11, 1, 6), (8, 8, 7, 9), (5, 4, 0, 11),
     (1, 5, 2, 2), (9, 1, 4, 12), (8, 3, 6, 6), (7, 0, 3, 7),
     (4, 7, 7, 5), (0, 12, 1, 11), (2, 9, 9, 0), (6, 8, 5, 3),
     (3, 10, 8, 2))
    _bits2bars = ('T', 'D', 'A', 'F')
    horizontalClearZone = property((lambda self: self.scale('hcz', self.dimensions, self.widthScale)))
    verticalClearZone = property((lambda self: self.scale('vcz', self.dimensions, self.heightScale)))
    pitch = property((lambda self: self.scale('pitch', self.dimensions, self.widthScale)))
    barWidth = property((lambda self: self.scale('width', self.dimensions, self.widthScale)))
    barHeight = property((lambda self: self.scale('F', self.tops, self.heightScale) - self.scale('F', self.bottoms, self.heightScale)))
    widthScale = property((lambda self: min(1, max(0, self.widthSize))))
    heightScale = property((lambda self: min(1, max(0, self.heightSize))))

    def width(self):
        self.computeSize()
        return self._width

    width = property(width)

    def height(self):
        self.computeSize()
        return self._height

    height = property(height)

    def computeSize(self):
        if not getattr(self, '_sized', None):
            ws = self.widthScale
            hs = self.heightScale
            barHeight = self.barHeight
            barWidth = self.barWidth
            pitch = self.pitch
            hcz = self.horizontalClearZone
            vcz = self.verticalClearZone
            self._width = 2 * hcz + barWidth + 64 * pitch
            self._height = 2 * vcz + barHeight
            if self.humanReadable:
                self._height += self.fontSize * 1.2 + vcz
            self._sized = True
        return

    def wrap(self, aW, aH):
        self.computeSize()
        return (self.width, self.height)

    def _getBarVInfo(self, y0=0):
        vInfo = {}
        hs = self.heightScale
        for b in ('T', 'D', 'A', 'F'):
            y = self.scale(b, self.bottoms, hs) + y0
            vInfo[b] = (y, self.scale(b, self.tops, hs) + y0 - y)

        return vInfo

    def draw(self):
        self.computeSize()
        hcz = self.horizontalClearZone
        vcz = self.verticalClearZone
        bw = self.barWidth
        x = hcz
        y0 = vcz + self.barHeight * 0.5
        dw = self.pitch
        vInfo = self._getBarVInfo(y0)
        for b in self.barcodes:
            yb, hb = vInfo[b]
            self.rect(x, yb, bw, hb)
            x += dw

        self.drawHumanReadable()

    def value(self):
        tracking = self.tracking
        routing = self.routing
        routing = routing and (routing,) or ()
        return (' ').join((tracking[0:2], tracking[2:5], tracking[5:11], tracking[11:]) + routing)

    value = property(value, (lambda self, value: self.__dict__.__setitem__('tracking', value)))

    def drawHumanReadable(self):
        if self.humanReadable:
            hcz = self.horizontalClearZone
            vcz = self.verticalClearZone
            fontName = self.fontName
            fontSize = self.fontSize
            y = self.barHeight + 2 * vcz + 0.2 * fontSize
            self.annotate(hcz, y, self.value, fontName, fontSize)

    def annotate(self, x, y, text, fontName, fontSize, anchor='middle'):
        Barcode.annotate(self, x, y, text, fontName, fontSize, anchor='start')


def _crc11(value):
    """
    >>> print ' '.join(hex(_crc11(USPS_4State('01234567094987654321',x).binary)) for x in ('','01234','012345678','01234567891'))
    0x51 0x65 0x606 0x751
    """
    bytes = hex(long(value))[2:-1]
    bytes = '0' * (26 - len(bytes)) + bytes
    gp = 3893
    fcs = 2047
    data = int(bytes[:2], 16) << 5
    for b in xrange(2, 8):
        if (fcs ^ data) & 1024:
            fcs = fcs << 1 ^ gp
        else:
            fcs = fcs << 1
        fcs &= 2047
        data <<= 1

    for x in xrange(2, 26, 2):
        data = int(bytes[x:x + 2], 16) << 3
        for b in xrange(8):
            if (fcs ^ data) & 1024:
                fcs = fcs << 1 ^ gp
            else:
                fcs = fcs << 1
            fcs &= 2047
            data <<= 1

    return fcs


def _ru13(i):
    """reverse unsigned 13 bit number
    >>> print _ru13(7936), _ru13(31), _ru13(47), _ru13(7808)
    31 7936 7808 47
    """
    r = 0
    for x in xrange(13):
        r <<= 1
        r |= i & 1
        i >>= 1

    return r


def _initNof13Table(N, lenT):
    """create and return table of 13 bit values with N bits on
    >>> T = _initNof13Table(5,1287)
    >>> print ' '.join('T[%d]=%d' % (i, T[i]) for i in (0,1,2,3,4,1271,1272,1284,1285,1286))
    T[0]=31 T[1]=7936 T[2]=47 T[3]=7808 T[4]=55 T[1271]=6275 T[1272]=6211 T[1284]=856 T[1285]=744 T[1286]=496
    """
    T = lenT * [None]
    l = 0
    u = lenT - 1
    for c in xrange(8192):
        bc = 0
        for b in xrange(13):
            bc += c & 1 << b != 0

        if bc != N:
            continue
        r = _ru13(c)
        if r < c:
            continue
        if r == c:
            T[u] = c
            u -= 1
        else:
            T[l] = c
            l += 1
            T[l] = r
            l += 1

    assert l == u + 1, 'u+1(%d)!=l(%d) for %d of 13 table' % (u + 1, l, N)
    return T


def _test():
    import doctest
    return doctest.testmod()


if __name__ == '__main__':
    _test()