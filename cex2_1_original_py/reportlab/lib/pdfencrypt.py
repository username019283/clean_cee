# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\pdfencrypt.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
import string, sys, os
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from reportlab.lib.utils import getStringIO
import tempfile
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfutils
from reportlab.platypus.flowables import Flowable
CLOBBERID = 0
CLOBBERPERMISSIONS = 0
DEBUG = 0
reserved1 = 1
reserved2 = 2
printable = 4
modifiable = 8
copypastable = 16
annotatable = 32
higherbits = 0
for i in range(6, 31):
    higherbits = higherbits | 1 << i

class StandardEncryption:
    prepared = 0

    def __init__(self, userPassword, ownerPassword=None, canPrint=1, canModify=1, canCopy=1, canAnnotate=1, strength=40):
        """
        This class defines the encryption properties to be used while creating a pdf document.
        Once initiated, a StandardEncryption object can be applied to a Canvas or a BaseDocTemplate.
        The userPassword parameter sets the user password on the encrypted pdf.
        The ownerPassword parameter sets the owner password on the encrypted pdf.
        The boolean flags canPrint, canModify, canCopy, canAnnotate determine wether a user can
        perform the corresponding actions on the pdf when only a user password has been supplied.
        If the user supplies the owner password while opening the pdf, all actions can be performed regardless
        of the flags.
        Note that the security provided by these encryption settings (and even more so for the flags) is very weak.
        """
        self.ownerPassword = ownerPassword
        self.userPassword = userPassword
        if strength == 40:
            self.revision = 2
        elif strength == 128:
            self.revision = 3
        self.canPrint = canPrint
        self.canModify = canModify
        self.canCopy = canCopy
        self.canAnnotate = canAnnotate
        self.O = self.U = self.P = self.key = None
        return

    def setAllPermissions(self, value):
        self.canPrint = self.canModify = self.canCopy = self.canAnnotate = value

    def permissionBits(self):
        p = 0
        if self.canPrint:
            p = p | printable
        if self.canModify:
            p = p | modifiable
        if self.canCopy:
            p = p | copypastable
        if self.canAnnotate:
            p = p | annotatable
        p = p | higherbits
        return p

    def encode(self, t):
        """encode a string, stream, text"""
        if not self.prepared:
            raise ValueError, 'encryption not prepared!'
        if self.objnum is None:
            raise ValueError, 'not registered in PDF object'
        return encodePDF(self.key, self.objnum, self.version, t, revision=self.revision)

    def prepare(self, document, overrideID=None):
        if DEBUG:
            print 'StandardEncryption.prepare(...) - revision %d' % self.revision
        if self.prepared:
            raise ValueError, 'encryption already prepared!'
        if overrideID:
            internalID = overrideID
        else:
            externalID = document.ID()
            internalID = document.signature.digest()
            if CLOBBERID:
                internalID = 'xxxxxxxxxxxxxxxx'
        if DEBUG:
            print 'userPassword    = %s' % self.userPassword
            print 'ownerPassword   = %s' % self.ownerPassword
            print 'internalID      = %s' % internalID
        self.P = int(self.permissionBits() - 2147483648)
        if CLOBBERPERMISSIONS:
            self.P = -44
        if DEBUG:
            print 'self.P          = %s' % repr(self.P)
        self.O = computeO(self.userPassword, self.ownerPassword, self.revision)
        if DEBUG:
            print 'self.O (as hex) = %s' % hexText(self.O)
        self.key = encryptionkey(self.userPassword, self.O, self.P, internalID, revision=self.revision)
        if DEBUG:
            print 'self.key (hex)  = %s' % hexText(self.key)
        self.U = computeU(self.key, revision=self.revision, documentId=internalID)
        if DEBUG:
            print 'self.U (as hex) = %s' % hexText(self.U)
        self.objnum = self.version = None
        self.prepared = 1
        return

    def register(self, objnum, version):
        if not self.prepared:
            raise ValueError, 'encryption not prepared!'
        self.objnum = objnum
        self.version = version

    def info(self):
        if not self.prepared:
            raise ValueError, 'encryption not prepared!'
        return StandardEncryptionDictionary(O=self.O, U=self.U, P=self.P, revision=self.revision)


class StandardEncryptionDictionary:
    __RefOnly__ = 1
    __PDFObject__ = True

    def __init__(self, O, U, P, revision):
        self.O, self.U, self.P = O, U, P
        self.revision = revision

    def format(self, document):
        from reportlab.pdfbase.pdfdoc import DummyDoc, PDFDictionary, PDFString, PDFName
        dummy = DummyDoc()
        dict = {'Filter': PDFName('Standard'), 'O': hexText(self.O), 
           'U': hexText(self.U), 
           'P': self.P}
        if self.revision == 3:
            dict['Length'] = 128
            dict['R'] = 3
            dict['V'] = 2
        else:
            dict['R'] = 2
            dict['V'] = 1
        pdfdict = PDFDictionary(dict)
        return pdfdict.format(dummy)


padding = '\n28 BF 4E 5E 4E 75 8A 41 64 00 4E 56 FF FA 01 08\n2E 2E 00 B6 D0 68 3E 80 2F 0C A9 FE 64 53 69 7A\n'
if hasattr(padding, 'join'):

    def xorKey(num, key):
        """xor's each bytes of the key with the number, which is <256"""
        if num == 0:
            return key
        from operator import xor
        return ('').join(map(chr, map(xor, len(key) * [num], map(ord, key))))


else:

    def xorKey(num, key):
        """xor's each bytes of the key with the number, which is <256"""
        from operator import xor
        out = ''
        for ch in key:
            out = out + chr(xor(num, ord(ch)))

        return out


def hexchar(x):
    return chr(string.atoi(x, 16))


def hexText(text):
    """a legitimate way to show strings in PDF"""
    out = ''
    for char in text:
        out = out + '%02X' % ord(char)

    return '<' + out + '>'


def unHexText(hexText):
    assert hexText[0] == '<', 'bad hex text'
    assert hexText[-1] == '>', 'bad hex text'
    hexText = hexText[1:-1]
    out = ''
    for i in range(int(len(hexText) / 2.0)):
        slice = hexText[i * 2:i * 2 + 2]
        char = chr(eval('0x' + slice))
        out = out + char

    return out


PadString = string.join(map(hexchar, string.split(string.strip(padding))), '')

def encryptionkey(password, OwnerKey, Permissions, FileId1, revision=2):
    password = password + PadString
    password = password[:32]
    p = Permissions
    permissionsString = ''
    for i in range(4):
        byte = p & 255
        p = p >> 8
        permissionsString = permissionsString + chr(byte % 256)

    hash = md5(password)
    hash.update(OwnerKey)
    hash.update(permissionsString)
    hash.update(FileId1)
    md5output = hash.digest()
    if revision == 2:
        key = md5output[:5]
    elif revision == 3:
        for x in range(50):
            md5output = md5(md5output).digest()

        key = md5output[:16]
    if DEBUG:
        print 'encryptionkey(%s,%s,%s,%s,%s)==>%s' % tuple(map((lambda x: hexText(str(x))), (password, OwnerKey, Permissions, FileId1, revision, key)))
    return key


def computeO(userPassword, ownerPassword, revision):
    from reportlab.lib.arciv import ArcIV
    assert revision in (2, 3), 'Unknown algorithm revision %s' % revision
    if ownerPassword in (None, ''):
        ownerPassword = userPassword
    ownerPad = ownerPassword + PadString
    ownerPad = ownerPad[0:32]
    password = userPassword + PadString
    userPad = password[:32]
    digest = md5(ownerPad).digest()
    if revision == 2:
        O = ArcIV(digest[:5]).encode(userPad)
    elif revision == 3:
        for i in range(50):
            digest = md5(digest).digest()

        digest = digest[:16]
        O = userPad
        for i in range(20):
            thisKey = xorKey(i, digest)
            O = ArcIV(thisKey).encode(O)

    if DEBUG:
        print 'computeO(%s,%s,%s)==>%s' % tuple(map((lambda x: hexText(str(x))), (userPassword, ownerPassword, revision, O)))
    return O


def computeU(encryptionkey, encodestring=PadString, revision=2, documentId=None):
    from reportlab.lib.arciv import ArcIV
    if revision == 2:
        result = ArcIV(encryptionkey).encode(encodestring)
    elif revision == 3:
        assert documentId is not None, 'Revision 3 algorithm needs the document ID!'
        h = md5(PadString)
        h.update(documentId)
        tmp = h.digest()
        tmp = ArcIV(encryptionkey).encode(tmp)
        for n in range(1, 20):
            thisKey = xorKey(n, encryptionkey)
            tmp = ArcIV(thisKey).encode(tmp)

        while len(tmp) < 32:
            tmp = tmp + '\x00'

        result = tmp
    if DEBUG:
        print 'computeU(%s,%s,%s,%s)==>%s' % tuple(map((lambda x: hexText(str(x))), (encryptionkey, encodestring, revision, documentId, result)))
    return result


def checkU(encryptionkey, U):
    decoded = computeU(encryptionkey, U)
    if decoded != PadString:
        if len(decoded) != len(PadString):
            raise ValueError, "lengths don't match! (password failed)"
        raise ValueError, "decode of U doesn't match fixed padstring (password failed)"


def encodePDF(key, objectNumber, generationNumber, string, revision=2):
    """Encodes a string or stream"""
    newkey = key
    n = objectNumber
    for i in range(3):
        newkey = newkey + chr(n & 255)
        n = n >> 8

    n = generationNumber
    for i in range(2):
        newkey = newkey + chr(n & 255)
        n = n >> 8

    md5output = md5(newkey).digest()
    if revision == 2:
        key = md5output[:10]
    elif revision == 3:
        key = md5output
    from reportlab.lib.arciv import ArcIV
    encrypted = ArcIV(key).encode(string)
    if DEBUG:
        print 'encodePDF(%s,%s,%s,%s,%s)==>%s' % tuple(map((lambda x: hexText(str(x))), (key, objectNumber, generationNumber, string, revision, encrypted)))
    return encrypted


def test():
    enc = StandardEncryption('userpass', 'ownerpass', strength=40)
    enc.prepare(None, overrideID='xxxxxxxxxxxxxxxx')
    expectedO = '<6A835A92E99DCEA39D51CF34FDBDA42162690D2BD5F8E08E3008F91FE5B8512E>'
    expectedU = '<9997BDB61E7F288DAE6A8C4246A8F9CDCDBBC3D909D703CABA5D65A0CC6D4083>'
    expectedKey = '<A3A68B5CB1>'
    assert hexText(enc.O) == expectedO, '40 bit unexpected O value %s' % hexText(enc.O)
    assert hexText(enc.U) == expectedU, '40 bit unexpected U value %s' % hexText(enc.U)
    assert hexText(enc.key) == expectedKey, '40 bit unexpected key value %s' % hexText(enc.key)
    enc = StandardEncryption('userpass', 'ownerpass', strength=128)
    enc.prepare(None, overrideID='xxxxxxxxxxxxxxxx')
    expectedO = '<19BDBD240E0866B84C49AEEF7E2350045DB8BDAE96E039BF4E3F12DAC3427DB6>'
    expectedU = '<564747DADFF35F5F2078A2CA1705B50800000000000000000000000000000000>'
    expectedKey = '<DC1E019846B1EEABA0CDB8ED6D53B5C4>'
    assert hexText(enc.O) == expectedO, '128 bit unexpected O value %s' % hexText(enc.O)
    assert hexText(enc.U) == expectedU, '128 bit unexpected U value %s' % hexText(enc.U)
    assert hexText(enc.key) == expectedKey, '128 bit unexpected key value %s' % hexText(enc.key)
    return


def encryptCanvas(canvas, userPassword, ownerPassword=None, canPrint=1, canModify=1, canCopy=1, canAnnotate=1, strength=40):
    """Applies encryption to the document being generated"""
    enc = StandardEncryption(userPassword, ownerPassword, canPrint, canModify, canCopy, canAnnotate, strength=strength)
    canvas._doc.encrypt = enc


class EncryptionFlowable(StandardEncryption, Flowable):
    """Drop this in your Platypus story and it will set up the encryption options.

    If you do it multiple times, the last one before saving will win."""

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        encryptCanvas(self.canv, self.userPassword, self.ownerPassword, self.canPrint, self.canModify, self.canCopy, self.canAnnotate)


def encryptDocTemplate(dt, userPassword, ownerPassword=None, canPrint=1, canModify=1, canCopy=1, canAnnotate=1, strength=40):
    """For use in Platypus.  Call before build()."""
    raise Exception('Not implemented yet')


def encryptPdfInMemory(inputPDF, userPassword, ownerPassword=None, canPrint=1, canModify=1, canCopy=1, canAnnotate=1, strength=40):
    """accepts a PDF file 'as a byte array in memory'; return encrypted one.

    This is a high level convenience and does not touch the hard disk in any way.
    If you are encrypting the same file over and over again, it's better to use
    pageCatcher and cache the results."""
    try:
        from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory
    except ImportError:
        raise ImportError('reportlab.lib.pdfencrypt.encryptPdfInMemory failed because rlextra cannot be imported.\nSee http://developer.reportlab.com')

    bboxInfo, pickledForms = storeFormsInMemory(inputPDF, all=1, BBoxes=1)
    names = bboxInfo.keys()
    firstPageSize = bboxInfo['PageForms0'][2:]
    buf = getStringIO()
    canv = Canvas(buf, pagesize=firstPageSize)
    if CLOBBERID:
        canv._doc._ID = '[(xxxxxxxxxxxxxxxx)(xxxxxxxxxxxxxxxx)]'
    encryptCanvas(canv, userPassword, ownerPassword, canPrint, canModify, canCopy, canAnnotate, strength=strength)
    formNames = restoreFormsInMemory(pickledForms, canv)
    for formName in formNames:
        canv.doForm(formName)
        canv.showPage()

    canv.save()
    return buf.getvalue()


def encryptPdfOnDisk(inputFileName, outputFileName, userPassword, ownerPassword=None, canPrint=1, canModify=1, canCopy=1, canAnnotate=1, strength=40):
    """Creates encrypted file OUTPUTFILENAME.  Returns size in bytes."""
    inputPDF = open(inputFileName, 'rb').read()
    outputPDF = encryptPdfInMemory(inputPDF, userPassword, ownerPassword, canPrint, canModify, canCopy, canAnnotate, strength=strength)
    open(outputFileName, 'wb').write(outputPDF)
    return len(outputPDF)


def scriptInterp():
    sys_argv = sys.argv[:]
    usage = "PDFENCRYPT USAGE:\n\nPdfEncrypt encrypts your PDF files.\n\nLine mode usage:\n\n% pdfencrypt.exe pdffile [-o ownerpassword] | [owner ownerpassword],\n\t[-u userpassword] | [user userpassword],\n\t[-p 1|0] | [printable 1|0],\n\t[-m 1|0] | [modifiable 1|0],\n\t[-c 1|0] | [copypastable 1|0],\n\t[-a 1|0] | [annotatable 1|0],\n\t[-s savefilename] | [savefile savefilename],\n\t[-v 1|0] | [verbose 1|0],\n\t[-e128], [encrypt128],\n\t[-h] | [help]\n\n-o or owner set the owner password.\n-u or user set the user password.\n-p or printable set the printable attribute (must be 1 or 0).\n-m or modifiable sets the modifiable attribute (must be 1 or 0).\n-c or copypastable sets the copypastable attribute (must be 1 or 0).\n-a or annotatable sets the annotatable attribute (must be 1 or 0).\n-s or savefile sets the name for the output PDF file\n-v or verbose prints useful output to the screen.\n      (this defaults to 'pdffile_encrypted.pdf').\n'-e128' or 'encrypt128' allows you to use 128 bit encryption (in beta).\n\n-h or help prints this message.\n\nSee PdfEncryptIntro.pdf for more information.\n"
    known_modes = [
     '-o', 'owner', 
     '-u', 'user', 
     '-p', 'printable', 
     '-m', 
     'modifiable', 
     '-c', 'copypastable', 
     '-a', 'annotatable', 
     '-s', 
     'savefile', 
     '-v', 'verbose', 
     '-h', 'help', 
     '-e128', 
     'encrypt128']
    OWNER = ''
    USER = ''
    PRINTABLE = 1
    MODIFIABLE = 1
    COPYPASTABLE = 1
    ANNOTATABLE = 1
    SAVEFILE = 'encrypted.pdf'
    caller = sys_argv[0]
    argv = list(sys_argv)[1:]
    if len(argv) > 0:
        if argv[0] == '-h' or argv[0] == 'help':
            print usage
            return
        if len(argv) < 2:
            raise ValueError('Must include a filename and one or more arguments!')
        if argv[0] not in known_modes:
            infile = argv[0]
            argv = argv[1:]
            if not os.path.isfile(infile):
                raise ValueError("Can't open input file '%s'!" % infile)
        else:
            raise ValueError('First argument must be name of the PDF input file!')
        STRENGTH = 40
        if 'encrypt128' in argv:
            STRENGTH = 128
            argv.remove('encrypt128')
        if '-e128' in argv:
            STRENGTH = 128
            argv.remove('-e128')
        if '-v' in argv or 'verbose' in argv:
            if '-v' in argv:
                pos = argv.index('-v')
                arg = '-v'
            else:
                if 'verbose' in argv:
                    pos = argv.index('verbose')
                    arg = 'verbose'
                try:
                    verbose = int(argv[pos + 1])
                except:
                    verbose = 1

            argv.remove(argv[pos + 1])
            argv.remove(arg)
        else:
            from reportlab.rl_config import verbose
        arglist = (
         (
          '-o', 'OWNER', OWNER, 'Owner password'),
         (
          'owner', 'OWNER', OWNER, 'Owner password'),
         (
          '-u', 'USER', USER, 'User password'),
         (
          'user', 'USER', USER, 'User password'),
         (
          '-p', 'PRINTABLE', PRINTABLE, "'Printable'"),
         (
          'printable', 'PRINTABLE', PRINTABLE, "'Printable'"),
         (
          '-m', 'MODIFIABLE', MODIFIABLE, "'Modifiable'"),
         (
          'modifiable', 'MODIFIABLE', MODIFIABLE, "'Modifiable'"),
         (
          '-c', 'COPYPASTABLE', COPYPASTABLE, "'Copypastable'"),
         (
          'copypastable', 'COPYPASTABLE', COPYPASTABLE, "'Copypastable'"),
         (
          '-a', 'ANNOTATABLE', ANNOTATABLE, "'Annotatable'"),
         (
          'annotatable', 'ANNOTATABLE', ANNOTATABLE, "'Annotatable'"),
         (
          '-s', 'SAVEFILE', SAVEFILE, 'Output file'),
         (
          'savefile', 'SAVEFILE', SAVEFILE, 'Output file'))
        binaryrequired = ('-p', 'printable', '-m', 'modifiable', 'copypastable', '-c',
                          'annotatable', '-a')
        for thisarg in arglist:
            if thisarg[0] in argv:
                pos = argv.index(thisarg[0])
                if thisarg[0] in binaryrequired:
                    if argv[pos + 1] not in ('1', '0'):
                        raise "%s value must be either '1' or '0'!" % thisarg[1]
                try:
                    if argv[pos + 1] not in known_modes:
                        if thisarg[0] in binaryrequired:
                            exec thisarg[1] + ' = int(argv[pos+1])'
                        else:
                            exec thisarg[1] + ' = argv[pos+1]'
                        if verbose:
                            print "%s set to: '%s'." % (thisarg[3], argv[pos + 1])
                        argv.remove(argv[pos + 1])
                        argv.remove(thisarg[0])
                except:
                    raise 'Unable to set %s.' % thisarg[3]

        if verbose > 4:
            print '\ninfile:', infile
            print 'STRENGTH:', STRENGTH
            print 'SAVEFILE:', SAVEFILE
            print 'USER:', USER
            print 'OWNER:', OWNER
            print 'PRINTABLE:', PRINTABLE
            print 'MODIFIABLE:', MODIFIABLE
            print 'COPYPASTABLE:', COPYPASTABLE
            print 'ANNOTATABLE:', ANNOTATABLE
            print 'SAVEFILE:', SAVEFILE
            print 'VERBOSE:', verbose
        if SAVEFILE == 'encrypted.pdf':
            if infile[-4:] == '.pdf' or infile[-4:] == '.PDF':
                tinfile = infile[:-4]
            else:
                tinfile = infile
            SAVEFILE = tinfile + '_encrypted.pdf'
        filesize = encryptPdfOnDisk(infile, SAVEFILE, USER, OWNER, PRINTABLE, MODIFIABLE, COPYPASTABLE, ANNOTATABLE, strength=STRENGTH)
        if verbose:
            print "wrote output file '%s'(%s bytes)\n  owner password is '%s'\n  user password is '%s'" % (SAVEFILE, filesize, OWNER, USER)
        if len(argv) > 0:
            raise '\nUnrecognised arguments : %s\nknown arguments are:\n%s' % (str(argv)[1:-1], known_modes)
    else:
        print usage


def main():
    from reportlab.rl_config import verbose
    scriptInterp()


if __name__ == '__main__':
    a = filter((lambda x: x[:7] == '--debug'), sys.argv)
    if a:
        sys.argv = filter((lambda x: x[:7] != '--debug'), sys.argv)
        DEBUG = len(a)
    if '--test' in sys.argv:
        test()
    else:
        main()