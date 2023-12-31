# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\lib\yaml.pyc
# Compiled at: 2013-03-27 15:37:42
"""
.h1 Welcome to YAML!
YAML is "Yet Another Markup Language" - a markup language
which is easier to type in than XML, yet gives us a
reasonable selection of formats.

The general rule is that if a line begins with a '.',
it requires special processing. Otherwise lines
are concatenated to paragraphs, and blank lines
separate paragraphs.

If the line ".foo bar bletch" is encountered,
it immediately ends and writes out any current
paragraph.

It then looks for a parser method called 'foo';
if found, it is called with arguments (bar, bletch).

If this is not found, it assumes that 'foo' is a
paragraph style, and the text for the first line
of the paragraph is 'bar bletch'.  It would be
up to the formatter to decide whether on not 'foo'
was a valid paragraph.

Special commands understood at present are:
dot image filename
- adds the image to the document
dot beginPre Code
- begins a Preformatted object in style 'Code'
dot endPre
- ends a preformatted object.
"""
__version__ = ' $Id$ '
import sys, string
PLAIN = 1
PREFORMATTED = 2
BULLETCHAR = b'\xb7'

class BaseParser:
    """"Simplest possible parser with only the most basic options.

    This defines the line-handling abilities and basic mechanism.
    The class YAMLParser includes capabilities for a fairly rich
    story."""

    def __init__(self):
        self.reset()

    def reset(self):
        self._lineNo = 0
        self._style = 'Normal'
        self._results = []
        self._buf = []
        self._mode = PLAIN

    def parseFile(self, filename):
        data = open(filename, 'r').readlines()
        for line in data:
            self.readLine(line[:-1])

        self.endPara()
        return self._results

    def parseText(self, textBlock):
        """Parses the a possible multi-line text block"""
        lines = string.split(textBlock, '\n')
        for line in lines:
            self.readLine(line)

        self.endPara()
        return self._results

    def readLine(self, line):
        self._lineNo = self._lineNo + 1
        stripped = string.lstrip(line)
        if len(stripped) == 0:
            if self._mode == PLAIN:
                self.endPara()
            else:
                self._buf.append(line)
        elif line[0] == '.':
            self.endPara()
            words = string.split(stripped[1:])
            cmd, args = words[0], words[1:]
            if hasattr(self.__class__, cmd):
                try:
                    getattr(self, cmd)(*args)
                except TypeError as err:
                    sys.stderr.write('Parser method: %s(*%s) %s at line %d\n' % (cmd, args, err, self._lineNo))
                    raise

            else:
                self.endPara()
                words = string.split(stripped, ' ', 1)
                assert len(words) == 2, 'Style %s but no data at line %d' % (words[0], self._lineNo)
                styletag, data = words
                self._style = styletag[1:]
                self._buf.append(data)
        else:
            self._buf.append(line)

    def endPara(self):
        text = string.join(self._buf, ' ')
        if text:
            if self._mode == PREFORMATTED:
                self._results.append(('PREFORMATTED', self._style,
                 string.join(self._buf, '\n')))
            else:
                self._results.append(('PARAGRAPH', self._style, text))
        self._buf = []
        self._style = 'Normal'

    def beginPre(self, stylename):
        self._mode = PREFORMATTED
        self._style = stylename

    def endPre(self):
        self.endPara()
        self._mode = PLAIN

    def image(self, filename):
        self.endPara()
        self._results.append(('IMAGE', filename))


class Parser(BaseParser):
    """This adds a basic set of "story" components compatible with HTML & PDF.

    Images, spaces"""

    def vSpace(self, points):
        """Inserts a vertical spacer"""
        self._results.append(('VSpace', points))

    def pageBreak(self):
        """Inserts a frame break"""
        self._results.append(('PageBreak', 'blah'))

    def custom(self, moduleName, funcName):
        """Goes and gets the Python object and adds it to the story"""
        self.endPara()
        self._results.append(('Custom', moduleName, funcName))

    def nextPageTemplate(self, templateName):
        self._results.append(('NextPageTemplate', templateName))


def parseFile(filename):
    p = Parser()
    return p.parseFile(filename)


def parseText(textBlock):
    p = Parser()
    return p.parseText(textBlock)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        results = parseText(__doc__)
    else:
        results = parseFile(sys.argv[1])
    import pprint
    pprint.pprint(results)