# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\pdfbase\ttfonts.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = '$Id$'
__doc__ = 'TrueType font support\n\nThis defines classes to represent TrueType fonts.  They know how to calculate\ntheir own width and how to write themselves into PDF files.  They support\nsubsetting and embedding and can represent all 16-bit Unicode characters.\n\nNote on dynamic fonts\n---------------------\n\nUsually a Font in ReportLab corresponds to a fixed set of PDF objects (Font,\nFontDescriptor, Encoding).  But with dynamic font subsetting a single TTFont\nwill result in a number of Font/FontDescriptor/Encoding object sets, and the\ncontents of those will depend on the actual characters used for printing.\n\nTo support dynamic font subsetting a concept of "dynamic font" was introduced.\nDynamic Fonts have a _dynamicFont attribute set to 1.\n\nDynamic fonts have the following additional functions::\n\n    def splitString(self, text, doc):\n        \'\'\'Splits text into a number of chunks, each of which belongs to a\n        single subset.  Returns a list of tuples (subset, string).  Use\n        subset numbers with getSubsetInternalName.  Doc is used to identify\n        a document so that different documents may have different dynamically\n        constructed subsets.\'\'\'\n\n    def getSubsetInternalName(self, subset, doc):\n        \'\'\'Returns the name of a PDF Font object corresponding to a given\n        subset of this dynamic font.  Use this function instead of\n        PDFDocument.getInternalFontName.\'\'\'\n\nYou must never call PDFDocument.getInternalFontName for dynamic fonts.\n\nIf you have a traditional static font, mapping to PDF text output operators\nis simple::\n\n   \'%s 14 Tf (%s) Tj\' % (getInternalFontName(psfontname), text)\n\nIf you have a dynamic font, use this instead::\n\n   for subset, chunk in font.splitString(text, doc):\n       \'%s 14 Tf (%s) Tj\' % (font.getSubsetInternalName(subset, doc), chunk)\n\n(Tf is a font setting operator and Tj is a text ouput operator.  You should\nalso escape invalid characters in Tj argument, see TextObject._formatText.\nOh, and that 14 up there is font size.)\n\nCanvas and TextObject have special support for dynamic fonts.\n'
import string
from struct import pack, unpack, error as structError
from reportlab.lib.utils import getStringIO
from reportlab.pdfbase import pdfmetrics, pdfdoc
from reportlab import rl_config

class TTFError(pdfdoc.PDFError):
    """TrueType font exception"""
    pass


def SUBSETN(n, table=string.maketrans('0123456789', 'ABCDEFGHIJ')):
    return ('%6.6d' % n).translate(table)


from codecs import utf_8_encode, utf_8_decode, latin_1_decode
parse_utf8 = lambda x, decode=utf_8_decode: map(ord, decode(x)[0])
parse_latin1 = lambda x, decode=latin_1_decode: map(ord, decode(x)[0])

def latin1_to_utf8(text):
    """helper to convert when needed from latin input"""
    return utf_8_encode(latin_1_decode(text)[0])[0]


def makeToUnicodeCMap(fontname, subset):
    """Creates a ToUnicode CMap for a given subset.  See Adobe
    _PDF_Reference (ISBN 0-201-75839-3) for more information."""
    cmap = [
     '/CIDInit /ProcSet findresource begin', '12 dict begin', 'begincmap', '/CIDSystemInfo', '<< /Registry (%s)' % fontname, '/Ordering (%s)' % fontname, '/Supplement 0', '>> def', '/CMapName /%s def' % fontname, '/CMapType 2 def', '1 begincodespacerange', '<00> <%02X>' % (len(subset) - 1), 'endcodespacerange', '%d beginbfchar' % len(subset)] + [ '<%02X> <%04X>' % (i, v) for i, v in enumerate(subset) ] + [
     'endbfchar', 
     'endcmap', 
     'CMapName currentdict /CMap defineresource pop', 
     'end', 
     'end']
    return string.join(cmap, '\n')


def splice(stream, offset, value):
    """Splices the given value into stream at the given offset and
    returns the resulting stream (the original is unchanged)"""
    return stream[:offset] + value + stream[offset + len(value):]


def _set_ushort(stream, offset, value):
    """Writes the given unsigned short value into stream at the given
    offset and returns the resulting stream (the original is unchanged)"""
    return splice(stream, offset, pack('>H', value))


try:
    import _rl_accel
except ImportError:
    try:
        from reportlab.lib import _rl_accel
    except ImportError:
        _rl_accel = None

try:
    hex32 = _rl_accel.hex32
except:

    def hex32(i):
        return '0X%8.8X' % (long(i) & 4294967295)


try:
    add32 = _rl_accel.add32L
    calcChecksum = _rl_accel.calcChecksumL
except:

    def add32(x, y):
        """Calculate (x + y) modulo 2**32"""
        return x + y & 4294967295


    def calcChecksum(data):
        """Calculates TTF-style checksums"""
        if len(data) & 3:
            data = data + (4 - (len(data) & 3)) * '\x00'
        return sum(unpack('>%dl' % (len(data) >> 2), data)) & 4294967295


del _rl_accel
GF_ARG_1_AND_2_ARE_WORDS = 1 << 0
GF_ARGS_ARE_XY_VALUES = 1 << 1
GF_ROUND_XY_TO_GRID = 1 << 2
GF_WE_HAVE_A_SCALE = 1 << 3
GF_RESERVED = 1 << 4
GF_MORE_COMPONENTS = 1 << 5
GF_WE_HAVE_AN_X_AND_Y_SCALE = 1 << 6
GF_WE_HAVE_A_TWO_BY_TWO = 1 << 7
GF_WE_HAVE_INSTRUCTIONS = 1 << 8
GF_USE_MY_METRICS = 1 << 9
GF_OVERLAP_COMPOUND = 1 << 10
GF_SCALED_COMPONENT_OFFSET = 1 << 11
GF_UNSCALED_COMPONENT_OFFSET = 1 << 12

def TTFOpenFile(fn):
    """Opens a TTF file possibly after searching TTFSearchPath
    returns (filename,file)
    """
    from reportlab.lib.utils import rl_isfile, open_for_read
    try:
        f = open_for_read(fn, 'rb')
        return (fn, f)
    except IOError:
        import os
        if not os.path.isabs(fn):
            for D in rl_config.TTFSearchPath:
                tfn = os.path.join(D, fn)
                if rl_isfile(tfn):
                    f = open_for_read(tfn, 'rb')
                    return (
                     tfn, f)

        raise TTFError('Can\'t open file "%s"' % fn)


class TTFontParser():
    """Basic TTF file parser"""
    ttfVersions = (65536, 1953658213, 1953784678)
    ttcVersions = (65536, 131072)
    fileKind = 'TTF'

    def __init__(self, file, validate=0, subfontIndex=0):
        """Loads and parses a TrueType font file.  file can be a filename or a
        file object.  If validate is set to a false values, skips checksum
        validation.  This can save time, especially if the font is large.
        """
        self.validate = validate
        self.readFile(file)
        isCollection = self.readHeader()
        if isCollection:
            self.readTTCHeader()
            self.getSubfont(subfontIndex)
        else:
            if self.validate:
                self.checksumFile()
            self.readTableDirectory()
            self.subfontNameX = ''

    def readTTCHeader(self):
        self.ttcVersion = self.read_ulong()
        self.fileKind = 'TTC'
        self.ttfVersions = self.ttfVersions[:-1]
        if self.ttcVersion not in self.ttcVersions:
            raise TTFError('"%s" is not a %s file: can\'t read version 0x%8.8x' % (self.filename, self.fileKind, self.ttcVersion))
        self.numSubfonts = self.read_ulong()
        self.subfontOffsets = []
        a = self.subfontOffsets.append
        for i in xrange(self.numSubfonts):
            a(self.read_ulong())

    def getSubfont(self, subfontIndex):
        if self.fileKind != 'TTC':
            raise TTFError('"%s" is not a TTC file: use this method' % (self.filename, self.fileKind))
        try:
            pos = self.subfontOffsets[subfontIndex]
        except IndexError:
            raise TTFError('TTC file "%s": bad subfontIndex %s not in [0,%d]' % (self.filename, subfontIndex, self.numSubfonts - 1))

        self.seek(pos)
        self.readHeader()
        self.readTableDirectory()
        self.subfontNameX = '-' + str(subfontIndex)

    def readTableDirectory(self):
        try:
            self.numTables = self.read_ushort()
            self.searchRange = self.read_ushort()
            self.entrySelector = self.read_ushort()
            self.rangeShift = self.read_ushort()
            self.table = {}
            self.tables = []
            for n in xrange(self.numTables):
                record = {}
                record['tag'] = self.read_tag()
                record['checksum'] = self.read_ulong()
                record['offset'] = self.read_ulong()
                record['length'] = self.read_ulong()
                self.tables.append(record)
                self.table[record['tag']] = record

        except:
            raise TTFError('Corrupt %s file "%s" cannot read Table Directory' % (self.fileKind, self.filename))

        if self.validate:
            self.checksumTables()

    def readHeader(self):
        """read the sfnt header at the current position"""
        try:
            self.version = version = self.read_ulong()
        except:
            raise TTFError('"%s" is not a %s file: can\'t read version' % (self.filename, self.fileKind))

        if version == 1330926671:
            raise TTFError('%s file "%s": postscript outlines are not supported' % (self.fileKind, self.filename))
        if version not in self.ttfVersions:
            raise TTFError('Not a TrueType font: version=0x%8.8X' % version)
        return version == self.ttfVersions[-1]

    def readFile(self, f):
        if hasattr(f, 'read'):
            self.filename = '(ttf)'
        else:
            self.filename, f = TTFOpenFile(f)
        self._ttf_data = f.read()
        self._pos = 0

    def checksumTables(self):
        for t in self.tables:
            table = self.get_chunk(t['offset'], t['length'])
            checksum = calcChecksum(table)
            if t['tag'] == 'head':
                adjustment = unpack('>l', table[8:12])[0]
                checksum = add32(checksum, -adjustment)
            xchecksum = t['checksum']
            if xchecksum != checksum:
                raise TTFError('TTF file "%s": invalid checksum %s table: %s (expected %s)' % (self.filename, hex32(checksum), t['tag'], hex32(xchecksum)))

    def checksumFile(self):
        checksum = calcChecksum(self._ttf_data)
        if 2981146554 != checksum:
            raise TTFError('TTF file "%s": invalid checksum %s (expected 0xB1B0AFBA) len: %d &3: %d' % (self.filename, hex32(checksum), len(self._ttf_data), len(self._ttf_data) & 3))

    def get_table_pos(self, tag):
        """Returns the offset and size of a given TTF table."""
        offset = self.table[tag]['offset']
        length = self.table[tag]['length']
        return (offset, length)

    def seek(self, pos):
        """Moves read pointer to a given offset in file."""
        self._pos = pos

    def skip(self, delta):
        """Skip the given number of bytes."""
        self._pos = self._pos + delta

    def seek_table(self, tag, offset_in_table=0):
        """Moves read pointer to the given offset within a given table and
        returns absolute offset of that position in the file."""
        self._pos = self.get_table_pos(tag)[0] + offset_in_table
        return self._pos

    def read_tag(self):
        """Read a 4-character tag"""
        self._pos += 4
        return self._ttf_data[self._pos - 4:self._pos]

    def read_ushort(self):
        """Reads an unsigned short"""
        self._pos += 2
        return unpack('>H', self._ttf_data[self._pos - 2:self._pos])[0]

    def read_ulong(self):
        """Reads an unsigned long"""
        self._pos += 4
        return unpack('>L', self._ttf_data[self._pos - 4:self._pos])[0]

    def read_short(self):
        """Reads a signed short"""
        self._pos += 2
        try:
            return unpack('>h', self._ttf_data[self._pos - 2:self._pos])[0]
        except structError as error:
            raise TTFError, error

    def get_ushort(self, pos):
        """Return an unsigned short at given position"""
        return unpack('>H', self._ttf_data[pos:pos + 2])[0]

    def get_ulong(self, pos):
        """Return an unsigned long at given position"""
        return unpack('>L', self._ttf_data[pos:pos + 4])[0]

    def get_chunk(self, pos, length):
        """Return a chunk of raw data at given position"""
        return self._ttf_data[pos:pos + length]

    def get_table(self, tag):
        """Return the given TTF table"""
        pos, length = self.get_table_pos(tag)
        return self._ttf_data[pos:pos + length]


class TTFontMaker():
    """Basic TTF file generator"""

    def __init__(self):
        """Initializes the generator."""
        self.tables = {}

    def add(self, tag, data):
        """Adds a table to the TTF file."""
        if tag == 'head':
            data = splice(data, 8, '\x00\x00\x00\x00')
        self.tables[tag] = data

    def makeStream(self):
        """Finishes the generation and returns the TTF file as a string"""
        stm = getStringIO()
        write = stm.write
        numTables = len(self.tables)
        searchRange = 1
        entrySelector = 0
        while searchRange * 2 <= numTables:
            searchRange = searchRange * 2
            entrySelector = entrySelector + 1

        searchRange = searchRange * 16
        rangeShift = numTables * 16 - searchRange
        write(pack('>lHHHH', 65536, numTables, searchRange, entrySelector, rangeShift))
        tables = self.tables.items()
        tables.sort()
        offset = 12 + numTables * 16
        for tag, data in tables:
            if tag == 'head':
                head_start = offset
            checksum = calcChecksum(data)
            write(tag)
            write(pack('>LLL', checksum, offset, len(data)))
            paddedLength = len(data) + 3 & -4
            offset = offset + paddedLength

        for tag, data in tables:
            data += '\x00\x00\x00'
            write(data[:len(data) & -4])

        checksum = calcChecksum(stm.getvalue())
        checksum = add32(2981146554, -checksum)
        stm.seek(head_start + 8)
        write(pack('>L', checksum))
        return stm.getvalue()


class TTFontFile(TTFontParser):
    """TTF file parser and generator"""

    def __init__(self, file, charInfo=1, validate=0, subfontIndex=0):
        """Loads and parses a TrueType font file.

        file can be a filename or a file object.  If validate is set to a false
        values, skips checksum validation.  This can save time, especially if
        the font is large.  See TTFontFile.extractInfo for more information.
        """
        TTFontParser.__init__(self, file, validate=validate, subfontIndex=subfontIndex)
        self.extractInfo(charInfo)

    def extractInfo(self, charInfo=1):
        """
        Extract typographic information from the loaded font file.

        The following attributes will be set::
        
            name         PostScript font name
            flags        Font flags
            ascent       Typographic ascender in 1/1000ths of a point
            descent      Typographic descender in 1/1000ths of a point
            capHeight    Cap height in 1/1000ths of a point (0 if not available)
            bbox         Glyph bounding box [l,t,r,b] in 1/1000ths of a point
            _bbox        Glyph bounding box [l,t,r,b] in unitsPerEm
            unitsPerEm   Glyph units per em
            italicAngle  Italic angle in degrees ccw
            stemV        stem weight in 1/1000ths of a point (approximate)
        
        If charInfo is true, the following will also be set::
        
            defaultWidth   default glyph width in 1/1000ths of a point
            charWidths     dictionary of character widths for every supported UCS character
                           code
        
        This will only work if the font has a Unicode cmap (platform 3,
        encoding 1, format 4 or platform 0 any encoding format 4).  Setting
        charInfo to false avoids this requirement
        
        """
        name_offset = self.seek_table('name')
        format = self.read_ushort()
        if format != 0:
            raise TTFError, 'Unknown name table format (%d)' % format
        numRecords = self.read_ushort()
        string_data_offset = name_offset + self.read_ushort()
        names = {1: None, 2: None, 3: None, 4: None, 6: None}
        K = names.keys()
        nameCount = len(names)
        for i in xrange(numRecords):
            platformId = self.read_ushort()
            encodingId = self.read_ushort()
            languageId = self.read_ushort()
            nameId = self.read_ushort()
            length = self.read_ushort()
            offset = self.read_ushort()
            if nameId not in K:
                continue
            N = None
            if platformId == 3 and encodingId == 1 and languageId == 1033:
                opos = self._pos
                try:
                    self.seek(string_data_offset + offset)
                    if length % 2 != 0:
                        raise TTFError, 'PostScript name is UTF-16BE string of odd length'
                    length /= 2
                    N = []
                    A = N.append
                    while length > 0:
                        char = self.read_ushort()
                        A(chr(char))
                        length -= 1

                    N = ('').join(N)
                finally:
                    self._pos = opos

            elif platformId == 1 and encodingId == 0 and languageId == 0:
                N = self.get_chunk(string_data_offset + offset, length)
            if N and names[nameId] == None:
                names[nameId] = N
                nameCount -= 1
                if nameCount == 0:
                    break

        if names[6] is not None:
            psName = names[6].replace(' ', '-')
        else:
            if names[4] is not None:
                psName = names[4].replace(' ', '-')
            elif names[1] is not None:
                psName = names[1].replace(' ', '-')
            else:
                psName = None
            if not psName:
                raise TTFError, 'Could not find PostScript font name'
            for c in psName:
                oc = ord(c)
                if oc > 126 or c in ' [](){}<>/%':
                    raise TTFError, "psName=%r contains invalid character '%s' ie U+%04X" % (psName, c, ord(c))

        self.name = psName
        self.familyName = names[1] or psName
        self.styleName = names[2] or 'Regular'
        self.fullName = names[4] or psName
        self.uniqueFontID = names[3] or psName
        self.seek_table('head')
        ver_maj, ver_min = self.read_ushort(), self.read_ushort()
        if ver_maj != 1:
            raise TTFError, 'Unknown head table version %d.%04x' % (ver_maj, ver_min)
        self.fontRevision = (
         self.read_ushort(), self.read_ushort())
        self.skip(4)
        magic = self.read_ulong()
        if magic != 1594834165:
            raise TTFError, 'Invalid head table magic %04x' % magic
        self.skip(2)
        self.unitsPerEm = unitsPerEm = self.read_ushort()
        scale = lambda x, unitsPerEm=unitsPerEm: x * 1000.0 / unitsPerEm
        self.skip(16)
        xMin = self.read_short()
        yMin = self.read_short()
        xMax = self.read_short()
        yMax = self.read_short()
        self.bbox = map(scale, [xMin, yMin, xMax, yMax])
        self.skip(6)
        indexToLocFormat = self.read_ushort()
        glyphDataFormat = self.read_ushort()
        if 'OS/2' in self.table:
            self.seek_table('OS/2')
            version = self.read_ushort()
            self.skip(2)
            usWeightClass = self.read_ushort()
            self.skip(2)
            fsType = self.read_ushort()
            if fsType == 2 or fsType & 768 != 0:
                raise TTFError, 'Font does not allow subsetting/embedding (%04X)' % fsType
            self.skip(58)
            sTypoAscender = self.read_short()
            sTypoDescender = self.read_short()
            self.ascent = scale(sTypoAscender)
            self.descent = scale(sTypoDescender)
            if version > 1:
                self.skip(16)
                sCapHeight = self.read_short()
                self.capHeight = scale(sCapHeight)
            else:
                self.capHeight = self.ascent
        else:
            usWeightClass = 500
            self.ascent = scale(yMax)
            self.descent = scale(yMin)
            self.capHeight = self.ascent
        self.stemV = 50 + int((usWeightClass / 65.0) ** 2)
        self.seek_table('post')
        ver_maj, ver_min = self.read_ushort(), self.read_ushort()
        if ver_maj not in (1, 2, 3, 4):
            raise TTFError, 'Unknown post table version %d.%04x' % (ver_maj, ver_min)
        self.italicAngle = self.read_short() + self.read_ushort() / 65536.0
        self.underlinePosition = self.read_short()
        self.underlineThickness = self.read_short()
        isFixedPitch = self.read_ulong()
        self.flags = FF_SYMBOLIC
        if self.italicAngle != 0:
            self.flags = self.flags | FF_ITALIC
        if usWeightClass >= 600:
            self.flags = self.flags | FF_FORCEBOLD
        if isFixedPitch:
            self.flags = self.flags | FF_FIXED
        self.seek_table('hhea')
        ver_maj, ver_min = self.read_ushort(), self.read_ushort()
        if ver_maj != 1:
            raise TTFError, 'Unknown hhea table version %d.%04x' % (ver_maj, ver_min)
        self.skip(28)
        metricDataFormat = self.read_ushort()
        if metricDataFormat != 0:
            raise TTFError, 'Unknown horizontal metric data format (%d)' % metricDataFormat
        numberOfHMetrics = self.read_ushort()
        if numberOfHMetrics == 0:
            raise TTFError, 'Number of horizontal metrics is 0'
        self.seek_table('maxp')
        ver_maj, ver_min = self.read_ushort(), self.read_ushort()
        if ver_maj != 1:
            raise TTFError, 'Unknown maxp table version %d.%04x' % (ver_maj, ver_min)
        numGlyphs = self.read_ushort()
        if not charInfo:
            self.charToGlyph = None
            self.defaultWidth = None
            self.charWidths = None
            return
        else:
            if glyphDataFormat != 0:
                raise TTFError, 'Unknown glyph data format (%d)' % glyphDataFormat
            cmap_offset = self.seek_table('cmap')
            self.skip(2)
            cmapTableCount = self.read_ushort()
            unicode_cmap_offset = None
            for n in xrange(cmapTableCount):
                platformID = self.read_ushort()
                encodingID = self.read_ushort()
                offset = self.read_ulong()
                if platformID == 3 and encodingID == 1:
                    format = self.get_ushort(cmap_offset + offset)
                    if format == 4:
                        unicode_cmap_offset = cmap_offset + offset
                        break
                elif platformID == 0:
                    format = self.get_ushort(cmap_offset + offset)
                    if format == 4:
                        unicode_cmap_offset = cmap_offset + offset
                        break

            if unicode_cmap_offset is None:
                raise TTFError, 'Font does not have cmap for Unicode (platform 3, encoding 1, format 4 or platform 0 any encoding format 4)'
            self.seek(unicode_cmap_offset + 2)
            length = self.read_ushort()
            limit = unicode_cmap_offset + length
            self.skip(2)
            segCount = int(self.read_ushort() / 2.0)
            self.skip(6)
            endCount = map((lambda x, self=self: self.read_ushort()), xrange(segCount))
            self.skip(2)
            startCount = map((lambda x, self=self: self.read_ushort()), xrange(segCount))
            idDelta = map((lambda x, self=self: self.read_short()), xrange(segCount))
            idRangeOffset_start = self._pos
            idRangeOffset = map((lambda x, self=self: self.read_ushort()), xrange(segCount))
            glyphToChar = {}
            charToGlyph = {}
            for n in xrange(segCount):
                for unichar in xrange(startCount[n], endCount[n] + 1):
                    if idRangeOffset[n] == 0:
                        glyph = unichar + idDelta[n] & 65535
                    else:
                        offset = (unichar - startCount[n]) * 2 + idRangeOffset[n]
                        offset = idRangeOffset_start + 2 * n + offset
                        if offset >= limit:
                            glyph = 0
                        else:
                            glyph = self.get_ushort(offset)
                            if glyph != 0:
                                glyph = glyph + idDelta[n] & 65535
                    charToGlyph[unichar] = glyph
                    if glyph in glyphToChar:
                        glyphToChar[glyph].append(unichar)
                    else:
                        glyphToChar[glyph] = [
                         unichar]

            self.charToGlyph = charToGlyph
            self.seek_table('hmtx')
            aw = None
            self.charWidths = {}
            self.hmetrics = []
            for glyph in xrange(numberOfHMetrics):
                aw, lsb = self.read_ushort(), self.read_ushort()
                self.hmetrics.append((aw, lsb))
                aw = scale(aw)
                if glyph == 0:
                    self.defaultWidth = aw
                if glyph in glyphToChar:
                    for char in glyphToChar[glyph]:
                        self.charWidths[char] = aw

            for glyph in xrange(numberOfHMetrics, numGlyphs):
                lsb = self.read_ushort()
                self.hmetrics.append((aw, lsb))
                if glyph in glyphToChar:
                    for char in glyphToChar[glyph]:
                        self.charWidths[char] = aw

            self.seek_table('loca')
            self.glyphPos = []
            if indexToLocFormat == 0:
                for n in xrange(numGlyphs + 1):
                    self.glyphPos.append(self.read_ushort() << 1)

            elif indexToLocFormat == 1:
                for n in xrange(numGlyphs + 1):
                    self.glyphPos.append(self.read_ulong())

            else:
                raise TTFError, 'Unknown location table format (%d)' % indexToLocFormat
            return

    def makeSubset(self, subset):
        """Create a subset of a TrueType font"""
        output = TTFontMaker()
        glyphMap = [
         0]
        glyphSet = {0: 0}
        codeToGlyph = {}
        for code in subset:
            if code in self.charToGlyph:
                originalGlyphIdx = self.charToGlyph[code]
            else:
                originalGlyphIdx = 0
            if originalGlyphIdx not in glyphSet:
                glyphSet[originalGlyphIdx] = len(glyphMap)
                glyphMap.append(originalGlyphIdx)
            codeToGlyph[code] = glyphSet[originalGlyphIdx]

        start = self.get_table_pos('glyf')[0]
        n = 0
        while n < len(glyphMap):
            originalGlyphIdx = glyphMap[n]
            glyphPos = self.glyphPos[originalGlyphIdx]
            glyphLen = self.glyphPos[originalGlyphIdx + 1] - glyphPos
            n += 1
            if not glyphLen:
                continue
            self.seek(start + glyphPos)
            numberOfContours = self.read_short()
            if numberOfContours < 0:
                self.skip(8)
                flags = GF_MORE_COMPONENTS
                while flags & GF_MORE_COMPONENTS:
                    flags = self.read_ushort()
                    glyphIdx = self.read_ushort()
                    if glyphIdx not in glyphSet:
                        glyphSet[glyphIdx] = len(glyphMap)
                        glyphMap.append(glyphIdx)
                    if flags & GF_ARG_1_AND_2_ARE_WORDS:
                        self.skip(4)
                    else:
                        self.skip(2)
                    if flags & GF_WE_HAVE_A_SCALE:
                        self.skip(2)
                    elif flags & GF_WE_HAVE_AN_X_AND_Y_SCALE:
                        self.skip(4)
                    elif flags & GF_WE_HAVE_A_TWO_BY_TWO:
                        self.skip(8)

        numGlyphs = n = len(glyphMap)
        while n > 1 and self.hmetrics[n][0] == self.hmetrics[n - 1][0]:
            n -= 1

        numberOfHMetrics = n
        for tag in ('name', 'OS/2', 'cvt ', 'fpgm', 'prep'):
            try:
                output.add(tag, self.get_table(tag))
            except KeyError:
                pass

        post = '\x00\x03\x00\x00' + self.get_table('post')[4:16] + '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output.add('post', post)
        hhea = self.get_table('hhea')
        hhea = _set_ushort(hhea, 34, numberOfHMetrics)
        output.add('hhea', hhea)
        maxp = self.get_table('maxp')
        maxp = _set_ushort(maxp, 4, numGlyphs)
        output.add('maxp', maxp)
        entryCount = len(subset)
        length = 10 + entryCount * 2
        cmap = [0, 1, 
         1, 0, 0, 12, 
         6, length, 
         0, 
         0, 
         entryCount] + map(codeToGlyph.get, subset)
        cmap = pack(*(['>%dH' % len(cmap)] + cmap))
        output.add('cmap', cmap)
        hmtx = []
        for n in xrange(numGlyphs):
            originalGlyphIdx = glyphMap[n]
            aw, lsb = self.hmetrics[originalGlyphIdx]
            if n < numberOfHMetrics:
                hmtx.append(int(aw))
            hmtx.append(int(lsb))

        hmtx = pack(*(['>%dH' % len(hmtx)] + hmtx))
        output.add('hmtx', hmtx)
        glyphData = self.get_table('glyf')
        offsets = []
        glyf = []
        pos = 0
        for n in xrange(numGlyphs):
            offsets.append(pos)
            originalGlyphIdx = glyphMap[n]
            glyphPos = self.glyphPos[originalGlyphIdx]
            glyphLen = self.glyphPos[originalGlyphIdx + 1] - glyphPos
            data = glyphData[glyphPos:glyphPos + glyphLen]
            if glyphLen > 2 and unpack('>h', data[:2])[0] < 0:
                pos_in_glyph = 10
                flags = GF_MORE_COMPONENTS
                while flags & GF_MORE_COMPONENTS:
                    flags = unpack('>H', data[pos_in_glyph:pos_in_glyph + 2])[0]
                    glyphIdx = unpack('>H', data[pos_in_glyph + 2:pos_in_glyph + 4])[0]
                    data = _set_ushort(data, pos_in_glyph + 2, glyphSet[glyphIdx])
                    pos_in_glyph = pos_in_glyph + 4
                    if flags & GF_ARG_1_AND_2_ARE_WORDS:
                        pos_in_glyph = pos_in_glyph + 4
                    else:
                        pos_in_glyph = pos_in_glyph + 2
                    if flags & GF_WE_HAVE_A_SCALE:
                        pos_in_glyph = pos_in_glyph + 2
                    elif flags & GF_WE_HAVE_AN_X_AND_Y_SCALE:
                        pos_in_glyph = pos_in_glyph + 4
                    elif flags & GF_WE_HAVE_A_TWO_BY_TWO:
                        pos_in_glyph = pos_in_glyph + 8

            glyf.append(data)
            pos = pos + glyphLen
            if pos % 4 != 0:
                padding = 4 - pos % 4
                glyf.append('\x00' * padding)
                pos = pos + padding

        offsets.append(pos)
        output.add('glyf', string.join(glyf, ''))
        loca = []
        if pos + 1 >> 1 > 65535:
            indexToLocFormat = 1
            for offset in offsets:
                loca.append(offset)

            loca = pack(*(['>%dL' % len(loca)] + loca))
        else:
            indexToLocFormat = 0
            for offset in offsets:
                loca.append(offset >> 1)

            loca = pack(*(['>%dH' % len(loca)] + loca))
        output.add('loca', loca)
        head = self.get_table('head')
        head = _set_ushort(head, 50, indexToLocFormat)
        output.add('head', head)
        return output.makeStream()


FF_FIXED = 1 << 1 - 1
FF_SERIF = 1 << 2 - 1
FF_SYMBOLIC = 1 << 3 - 1
FF_SCRIPT = 1 << 4 - 1
FF_NONSYMBOLIC = 1 << 6 - 1
FF_ITALIC = 1 << 7 - 1
FF_ALLCAP = 1 << 17 - 1
FF_SMALLCAP = 1 << 18 - 1
FF_FORCEBOLD = 1 << 19 - 1

class TTFontFace(TTFontFile, pdfmetrics.TypeFace):
    """TrueType typeface.

    Conceptually similar to a single byte typeface, but the glyphs are
    identified by UCS character codes instead of glyph names."""

    def __init__(self, filename, validate=0, subfontIndex=0):
        """Loads a TrueType font from filename."""
        pdfmetrics.TypeFace.__init__(self, None)
        TTFontFile.__init__(self, filename, validate=validate, subfontIndex=subfontIndex)
        return

    def getCharWidth(self, code):
        """Returns the width of character U+<code>"""
        return self.charWidths.get(code, self.defaultWidth)

    def addSubsetObjects(self, doc, fontname, subset):
        """Generate a TrueType font subset and add it to the PDF document.
        Returns a PDFReference to the new FontDescriptor object."""
        fontFile = pdfdoc.PDFStream()
        fontFile.content = self.makeSubset(subset)
        fontFile.dictionary['Length1'] = len(fontFile.content)
        if doc.compression:
            fontFile.filters = [
             pdfdoc.PDFZCompress]
        fontFileRef = doc.Reference(fontFile, 'fontFile:%s(%s)' % (self.filename, fontname))
        flags = self.flags & ~FF_NONSYMBOLIC
        flags = flags | FF_SYMBOLIC
        fontDescriptor = pdfdoc.PDFDictionary({'Type': '/FontDescriptor', 
           'Ascent': self.ascent, 
           'CapHeight': self.capHeight, 
           'Descent': self.descent, 
           'Flags': flags, 
           'FontBBox': pdfdoc.PDFArray(self.bbox), 
           'FontName': pdfdoc.PDFName(fontname), 
           'ItalicAngle': self.italicAngle, 
           'StemV': self.stemV, 
           'FontFile2': fontFileRef})
        return doc.Reference(fontDescriptor, 'fontDescriptor:' + fontname)


class TTEncoding():
    """Encoding for TrueType fonts (always UTF-8).

    TTEncoding does not directly participate in PDF object creation, since
    we need a number of different 8-bit encodings for every generated font
    subset.  TTFont itself cares about that."""

    def __init__(self):
        self.name = 'UTF-8'


class TTFont():
    """Represents a TrueType font.

    Its encoding is always UTF-8.

    Note: you cannot use the same TTFont object for different documents
    at the same time.

    Example of usage:

        font = ttfonts.TTFont('PostScriptFontName', '/path/to/font.ttf')
        pdfmetrics.registerFont(font)

        canvas.setFont('PostScriptFontName', size)
        canvas.drawString(x, y, "Some text encoded in UTF-8")
    """

    class State:
        namePrefix = 'F'

        def __init__(self, asciiReadable=None):
            self.assignments = {}
            self.nextCode = 0
            self.internalName = None
            self.frozen = 0
            if asciiReadable is None:
                asciiReadable = rl_config.ttfAsciiReadable
            if asciiReadable:
                subset0 = range(128)
                self.subsets = [subset0]
                for n in subset0:
                    self.assignments[n] = n

                self.nextCode = 128
            else:
                self.subsets = [
                 [
                  32] * 33]
                self.assignments[32] = 32
            return

    _multiByte = 1
    _dynamicFont = 1

    def __init__(self, name, filename, validate=0, subfontIndex=0, asciiReadable=None):
        """Loads a TrueType font from filename.

        If validate is set to a false values, skips checksum validation.  This
        can save time, especially if the font is large.
        """
        self.fontName = name
        self.face = TTFontFace(filename, validate=validate, subfontIndex=subfontIndex)
        self.encoding = TTEncoding()
        from weakref import WeakKeyDictionary
        self.state = WeakKeyDictionary()
        if asciiReadable is None:
            asciiReadable = rl_config.ttfAsciiReadable
        self._asciiReadable = asciiReadable
        return

    def _py_stringWidth(self, text, size, encoding='utf-8'):
        """Calculate text width"""
        if not isinstance(text, unicode):
            text = unicode(text, encoding or 'utf-8')
        g = self.face.charWidths.get
        dw = self.face.defaultWidth
        return 0.001 * size * sum([ g(ord(u), dw) for u in text ])

    stringWidth = _py_stringWidth

    def _assignState(self, doc, asciiReadable=None, namePrefix=None):
        """convenience function for those wishing to roll their own state properties"""
        if asciiReadable is None:
            asciiReadable = self._asciiReadable
        try:
            state = self.state[doc]
        except KeyError:
            state = self.state[doc] = TTFont.State(asciiReadable)
            if namePrefix is not None:
                state.namePrefix = namePrefix

        return state

    def splitString(self, text, doc, encoding='utf-8'):
        """Splits text into a number of chunks, each of which belongs to a
        single subset.  Returns a list of tuples (subset, string).  Use subset
        numbers with getSubsetInternalName.  Doc is needed for distinguishing
        subsets when building different documents at the same time."""
        asciiReadable = self._asciiReadable
        try:
            state = self.state[doc]
        except KeyError:
            state = self.state[doc] = TTFont.State(asciiReadable)

        curSet = -1
        cur = []
        results = []
        if not isinstance(text, unicode):
            text = unicode(text, encoding or 'utf-8')
        assignments = state.assignments
        subsets = state.subsets
        for code in map(ord, text):
            if code in assignments:
                n = assignments[code]
            else:
                if state.frozen:
                    raise pdfdoc.PDFError, 'Font %s is already frozen, cannot add new character U+%04X' % (self.fontName, code)
                n = state.nextCode
                if n & 255 == 32:
                    if n != 32:
                        subsets[n >> 8].append(32)
                    state.nextCode += 1
                    n = state.nextCode
                state.nextCode += 1
                assignments[code] = n
                if n > 32:
                    if not n & 255:
                        subsets.append([])
                    subsets[n >> 8].append(code)
                else:
                    subsets[0][n] = code
            if n >> 8 != curSet:
                if cur:
                    results.append((curSet, ('').join(map(chr, cur))))
                curSet = n >> 8
                cur = []
            cur.append(n & 255)

        if cur:
            results.append((curSet, ('').join(map(chr, cur))))
        return results

    def getSubsetInternalName(self, subset, doc):
        """Returns the name of a PDF Font object corresponding to a given
        subset of this dynamic font.  Use this function instead of
        PDFDocument.getInternalFontName."""
        try:
            state = self.state[doc]
        except KeyError:
            state = self.state[doc] = TTFont.State(self._asciiReadable)

        if subset < 0 or subset >= len(state.subsets):
            raise IndexError, 'Subset %d does not exist in font %s' % (subset, self.fontName)
        if state.internalName is None:
            state.internalName = state.namePrefix + repr(len(doc.fontMapping) + 1)
            doc.fontMapping[self.fontName] = '/' + state.internalName
            doc.delayedFonts.append(self)
        return '/%s+%d' % (state.internalName, subset)

    def addObjects(self, doc):
        """Makes  one or more PDF objects to be added to the document.  The
        caller supplies the internal name to be used (typically F1, F2, ... in
        sequence).

        This method creates a number of Font and FontDescriptor objects.  Every
        FontDescriptor is a (no more than) 256 character subset of the original
        TrueType font."""
        try:
            state = self.state[doc]
        except KeyError:
            state = self.state[doc] = TTFont.State(self._asciiReadable)

        state.frozen = 1
        for n, subset in enumerate(state.subsets):
            internalName = self.getSubsetInternalName(n, doc)[1:]
            baseFontName = '%s+%s%s' % (SUBSETN(n), self.face.name, self.face.subfontNameX)
            pdfFont = pdfdoc.PDFTrueTypeFont()
            pdfFont.__Comment__ = 'Font %s subset %d' % (self.fontName, n)
            pdfFont.Name = internalName
            pdfFont.BaseFont = baseFontName
            pdfFont.FirstChar = 0
            pdfFont.LastChar = len(subset) - 1
            widths = map(self.face.getCharWidth, subset)
            pdfFont.Widths = pdfdoc.PDFArray(widths)
            cmapStream = pdfdoc.PDFStream()
            cmapStream.content = makeToUnicodeCMap(baseFontName, subset)
            if doc.compression:
                cmapStream.filters = [
                 pdfdoc.PDFZCompress]
            pdfFont.ToUnicode = doc.Reference(cmapStream, 'toUnicodeCMap:' + baseFontName)
            pdfFont.FontDescriptor = self.face.addSubsetObjects(doc, baseFontName, subset)
            ref = doc.Reference(pdfFont, internalName)
            fontDict = doc.idToObject['BasicFonts'].dict
            fontDict[internalName] = pdfFont

        del self.state[doc]


try:
    from _rl_accel import _instanceStringWidthTTF
    import new
    TTFont.stringWidth = new.instancemethod(_instanceStringWidthTTF, None, TTFont)
except ImportError:
    pass