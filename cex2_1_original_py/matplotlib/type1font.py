# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\type1font.pyc
# Compiled at: 2012-11-06 08:42:20
"""
This module contains a class representing a Type 1 font.

This version reads pfa and pfb files and splits them for embedding in
pdf files. It also supports SlantFont and ExtendFont transformations,
similarly to pdfTeX and friends. There is no support yet for
subsetting.

Usage::

   >>> font = Type1Font(filename)
   >>> clear_part, encrypted_part, finale = font.parts
   >>> slanted_font = font.transform({'slant': 0.167})
   >>> extended_font = font.transform({'extend': 1.2})

Sources:

* Adobe Technical Note #5040, Supporting Downloadable PostScript
  Language Fonts.

* Adobe Type 1 Font Format, Adobe Systems Incorporated, third printing,
  v1.1, 1993. ISBN 0-201-57044-0.
"""
from __future__ import print_function
import matplotlib.cbook as cbook, io, itertools, numpy as np, re, struct, sys
if sys.version_info[0] >= 3:

    def ord(x):
        return x


class Type1Font(object):
    """
    A class representing a Type-1 font, for use by backends.

    .. attribute:: parts

       A 3-tuple of the cleartext part, the encrypted part, and the
       finale of zeros.

    .. attribute:: prop

       A dictionary of font properties.
    """
    __slots__ = ('parts', 'prop')

    def __init__(self, input):
        """
        Initialize a Type-1 font. *input* can be either the file name of
        a pfb file or a 3-tuple of already-decoded Type-1 font parts.
        """
        if isinstance(input, tuple) and len(input) == 3:
            self.parts = input
        else:
            with open(input, 'rb') as (file):
                data = self._read(file)
            self.parts = self._split(data)
        self._parse()

    def _read(self, file):
        """
        Read the font from a file, decoding into usable parts.
        """
        rawdata = file.read()
        if not rawdata.startswith(b'\x80'):
            return rawdata
        data = ''
        while len(rawdata) > 0:
            if not rawdata.startswith(b'\x80'):
                raise RuntimeError('Broken pfb file (expected byte 128, got %d)' % ord(rawdata[0]))
            type = ord(rawdata[1])
            if type in (1, 2):
                length, = struct.unpack('<i', rawdata[2:6])
                segment = rawdata[6:6 + length]
                rawdata = rawdata[6 + length:]
            if type == 1:
                data += segment
            elif type == 2:
                data += ('').join([ ('%02x' % ord(char)).encode('ascii') for char in segment
                                  ])
            elif type == 3:
                break
            else:
                raise RuntimeError('Unknown segment type %d in pfb file' % type)

        return data

    def _split(self, data):
        """
        Split the Type 1 font into its three main parts.

        The three parts are: (1) the cleartext part, which ends in a
        eexec operator; (2) the encrypted part; (3) the fixed part,
        which contains 512 ASCII zeros possibly divided on various
        lines, a cleartomark operator, and possibly something else.
        """
        idx = data.index('eexec')
        idx += len('eexec')
        while data[idx] in ' \t\r\n':
            idx += 1

        len1 = idx
        idx = data.rindex('cleartomark') - 1
        zeros = 512
        while zeros and ord(data[idx]) in (
         ord('0'), ord('\n'), ord('\r')):
            if ord(data[idx]) == ord('0'):
                zeros -= 1
            idx -= 1

        if zeros:
            raise RuntimeError('Insufficiently many zeros in Type 1 font')
        binary = ('').join([ unichr(int(data[i:i + 2], 16)).encode('latin-1') for i in range(len1, idx, 2)
                           ])
        return (
         data[:len1], binary, data[idx:])

    _whitespace = re.compile('[\\0\\t\\r\\014\\n ]+')
    _token = re.compile('/{0,2}[^]\\0\\t\\r\\v\\n ()<>{}/%[]+')
    _comment = re.compile('%[^\\r\\n\\v]*')
    _instring = re.compile('[()\\\\]')

    @classmethod
    def _tokens(cls, text):
        """
        A PostScript tokenizer. Yield (token, value) pairs such as
        ('whitespace', '   ') or ('name', '/Foobar').
        """
        pos = 0
        while pos < len(text):
            match = cls._comment.match(text[pos:]) or cls._whitespace.match(text[pos:])
            if match:
                yield (
                 'whitespace', match.group())
                pos += match.end()
            elif text[pos] == '(':
                start = pos
                pos += 1
                depth = 1
                while depth:
                    match = cls._instring.search(text[pos:])
                    if match is None:
                        return
                    pos += match.end()
                    if match.group() == '(':
                        depth += 1
                    elif match.group() == ')':
                        depth -= 1
                    else:
                        pos += 1

                yield (
                 'string', text[start:pos])
            elif text[pos:pos + 2] in ('<<', '>>'):
                yield (
                 'delimiter', text[pos:pos + 2])
                pos += 2
            elif text[pos] == '<':
                start = pos
                pos += text[pos:].index('>')
                yield ('string', text[start:pos])
            else:
                match = cls._token.match(text[pos:])
                if match:
                    try:
                        float(match.group())
                        yield ('number', match.group())
                    except ValueError:
                        yield (
                         'name', match.group())

                    pos += match.end()
                else:
                    yield (
                     'delimiter', text[pos])
                    pos += 1

        return

    def _parse(self):
        """
        Find the values of various font properties. This limited kind
        of parsing is described in Chapter 10 "Adobe Type Manager
        Compatibility" of the Type-1 spec.
        """
        prop = {'weight': 'Regular', 'ItalicAngle': 0.0, 'isFixedPitch': False, 'UnderlinePosition': -100, 
           'UnderlineThickness': 50}
        tokenizer = self._tokens(self.parts[0])
        filtered = itertools.ifilter((lambda x: x[0] != 'whitespace'), tokenizer)
        for token, value in filtered:
            if token == 'name' and value.startswith('/'):
                key = value[1:]
                token, value = next(filtered)
                if token == 'name':
                    if value in ('true', 'false'):
                        value = value == 'true'
                    else:
                        value = value.lstrip('/')
                elif token == 'string':
                    value = value.lstrip('(').rstrip(')')
                elif token == 'number':
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                else:
                    value = None
                if key != 'FontInfo' and value is not None:
                    prop[key] = value

        if 'FontName' not in prop:
            prop['FontName'] = prop.get('FullName') or prop.get('FamilyName') or 'Unknown'
        if 'FullName' not in prop:
            prop['FullName'] = prop['FontName']
        if 'FamilyName' not in prop:
            extras = '(?i)([ -](regular|plain|italic|oblique|(semi)?bold|(ultra)?light|extra|condensed))+$'
            prop['FamilyName'] = re.sub(extras, '', prop['FullName'])
        self.prop = prop
        return

    @classmethod
    def _transformer(cls, tokens, slant, extend):

        def fontname(name):
            result = name
            if slant:
                result += '_Slant_' + str(int(1000 * slant))
            if extend != 1.0:
                result += '_Extend_' + str(int(1000 * extend))
            return result

        def italicangle(angle):
            return str(float(angle) - np.arctan(slant) / np.pi * 180)

        def fontmatrix(array):
            array = array.lstrip('[').rstrip(']').strip().split()
            array = [ float(x) for x in array ]
            oldmatrix = np.eye(3, 3)
            oldmatrix[0:3, 0] = array[::2]
            oldmatrix[0:3, 1] = array[1::2]
            modifier = np.array([[extend, 0, 0],
             [
              slant, 1, 0],
             [
              0, 0, 1]])
            newmatrix = np.dot(modifier, oldmatrix)
            array[::2] = newmatrix[0:3, 0]
            array[1::2] = newmatrix[0:3, 1]
            return '[' + (' ').join(str(x) for x in array) + ']'

        def replace(fun):

            def replacer(tokens):
                token, value = next(tokens)
                yield value
                token, value = next(tokens)
                while token == 'whitespace':
                    yield value
                    token, value = next(tokens)

                if value != '[':
                    yield fun(value)
                else:
                    array = []
                    while value != ']':
                        array += value
                        token, value = next(tokens)

                    array += value
                    yield fun(('').join(array))

            return replacer

        def suppress(tokens):
            for x in itertools.takewhile((lambda x: x[1] != 'def'), tokens):
                pass

            yield ''

        table = {'/FontName': replace(fontname), '/ItalicAngle': replace(italicangle), 
           '/FontMatrix': replace(fontmatrix), 
           '/UniqueID': suppress}
        while True:
            token, value = next(tokens)
            if token == 'name' and value in table:
                for value in table[value](itertools.chain([(token, value)], tokens)):
                    yield value

            else:
                yield value

    def transform(self, effects):
        """
        Transform the font by slanting or extending. *effects* should
        be a dict where ``effects['slant']`` is the tangent of the
        angle that the font is to be slanted to the right (so negative
        values slant to the left) and ``effects['extend']`` is the
        multiplier by which the font is to be extended (so values less
        than 1.0 condense). Returns a new :class:`Type1Font` object.
        """
        buffer = io.BytesIO()
        try:
            tokenizer = self._tokens(self.parts[0])
            for value in self._transformer(tokenizer, slant=effects.get('slant', 0.0), extend=effects.get('extend', 1.0)):
                if sys.version_info[0] >= 3 and isinstance(value, int):
                    value = chr(value).encode('latin-1')
                buffer.write(value)

            result = buffer.getvalue()
        finally:
            buffer.close()

        return Type1Font((result, self.parts[1], self.parts[2]))