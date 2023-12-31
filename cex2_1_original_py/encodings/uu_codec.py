# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: encodings\uu_codec.pyc
# Compiled at: 2011-03-08 09:43:14
""" Python 'uu_codec' Codec - UU content transfer encoding

    Unlike most of the other codecs which target Unicode, this codec
    will return Python string objects for both encode and decode.

    Written by Marc-Andre Lemburg (mal@lemburg.com). Some details were
    adapted from uu.py which was written by Lance Ellinghouse and
    modified by Jack Jansen and Fredrik Lundh.

"""
import codecs, binascii

def uu_encode(input, errors='strict', filename='<data>', mode=438):
    """ Encodes the object input and returns a tuple (output
        object, length consumed).

        errors defines the error handling to apply. It defaults to
        'strict' handling which is the only currently supported
        error handling for this codec.

    """
    assert errors == 'strict'
    from cStringIO import StringIO
    from binascii import b2a_uu
    infile = StringIO(str(input))
    outfile = StringIO()
    read = infile.read
    write = outfile.write
    write('begin %o %s\n' % (mode & 511, filename))
    chunk = read(45)
    while chunk:
        write(b2a_uu(chunk))
        chunk = read(45)

    write(' \nend\n')
    return (
     outfile.getvalue(), len(input))


def uu_decode(input, errors='strict'):
    """ Decodes the object input and returns a tuple (output
        object, length consumed).

        input must be an object which provides the bf_getreadbuf
        buffer slot. Python strings, buffer objects and memory
        mapped files are examples of objects providing this slot.

        errors defines the error handling to apply. It defaults to
        'strict' handling which is the only currently supported
        error handling for this codec.

        Note: filename and file mode information in the input data is
        ignored.

    """
    if not errors == 'strict':
        raise AssertionError
        from cStringIO import StringIO
        from binascii import a2b_uu
        infile = StringIO(str(input))
        outfile = StringIO()
        readline = infile.readline
        write = outfile.write
        while 1:
            s = readline()
            if not s:
                raise ValueError, 'Missing "begin" line in input data'
            if s[:5] == 'begin':
                break

        while 1:
            s = readline()
            if not s or s == 'end\n':
                break
            try:
                data = a2b_uu(s)
            except binascii.Error as v:
                nbytes = ((ord(s[0]) - 32 & 63) * 4 + 5) / 3
                data = a2b_uu(s[:nbytes])

            write(data)

        raise s or ValueError, 'Truncated input data'
    return (outfile.getvalue(), len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return uu_encode(input, errors)

    def decode(self, input, errors='strict'):
        return uu_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return uu_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return uu_decode(input, self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='uu', encode=uu_encode, decode=uu_decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)