# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\platypus\tables.pyc
# Compiled at: 2013-03-27 15:37:42
__version__ = ' $Id$ '
__doc__ = "\nTables are created by passing the constructor a tuple of column widths, a tuple of row heights and the data in\nrow order. Drawing of the table can be controlled by using a TableStyle instance. This allows control of the\ncolor and weight of the lines (if any), and the font, alignment and padding of the text.\n\nNone values in the sequence of row heights or column widths, mean that the corresponding rows\nor columns should be automatically sized.\n\nAll the cell values should be convertible to strings; embedded newline '\\n' characters\ncause the value to wrap (ie are like a traditional linefeed).\n\nSee the test output from running this module as a script for a discussion of the method for constructing\ntables and table styles.\n"
from reportlab.platypus.flowables import Flowable, Preformatted, Spacer
from reportlab import rl_config
from reportlab.lib.styles import PropertySet, ParagraphStyle, _baseFontName
from reportlab.lib import colors
from reportlab.lib.utils import fp_str, annotateException, IdentStr, flatten
from reportlab.lib.abag import ABag as CellFrame
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.doctemplate import Indenter
from reportlab.platypus.flowables import LIIndenter
LINECAPS = {None: None, 'butt': 0, 'round': 1, 'projecting': 2, 'squared': 2}
LINEJOINS = {None: None, 'miter': 0, 'mitre': 0, 'round': 1, 'bevel': 2}

class CellStyle(PropertySet):
    fontname = _baseFontName
    fontsize = 10
    leading = 12
    leftPadding = 6
    rightPadding = 6
    topPadding = 3
    bottomPadding = 3
    firstLineIndent = 0
    color = 'black'
    alignment = 'LEFT'
    background = 'white'
    valign = 'BOTTOM'
    href = None
    destination = None

    def __init__(self, name, parent=None):
        self.name = name
        if parent is not None:
            parent.copy(self)
        return

    def copy(self, result=None):
        if result is None:
            result = CellStyle()
        for name in dir(self):
            setattr(result, name, getattr(self, name))

        return result


class TableStyle():

    def __init__(self, cmds=None, parent=None, **kw):
        commands = []
        if parent:
            commands = commands + parent.getCommands()
            self._opts = parent._opts
            for a in ('spaceBefore', 'spaceAfter'):
                if hasattr(parent, a):
                    setattr(self, a, getattr(parent, a))

        if cmds:
            commands = commands + list(cmds)
        self._cmds = commands
        self._opts = {}
        self._opts.update(kw)

    def add(self, *cmd):
        self._cmds.append(cmd)

    def __repr__(self):
        return 'TableStyle(\n%s\n) # end TableStyle' % ('  \n').join(map(repr, self._cmds))

    def getCommands(self):
        return self._cmds


def _rowLen(x):
    return not isinstance(x, (tuple, list)) and 1 or len(x)


def _calc_pc(V, avail):
    """check list V for percentage or * values
    1) absolute values go through unchanged
    2) percentages are used as weights for unconsumed space
    3) if no None values were seen '*' weights are
    set equally with unclaimed space
    otherwise * weights are assigned as None"""
    R = []
    r = R.append
    I = []
    i = I.append
    J = []
    j = J.append
    s = avail
    w = n = 0.0
    for v in V:
        if isinstance(v, basestring):
            v = v.strip()
            if not v:
                v = None
                n += 1
            elif v.endswith('%'):
                v = float(v[:-1])
                w += v
                i(len(R))
            elif v == '*':
                j(len(R))
            else:
                v = float(v)
                s -= v
        elif v is None:
            n += 1
        else:
            s -= v
        r(v)

    s = max(0.0, s)
    f = s / max(100.0, w)
    for i in I:
        R[i] *= f
        s -= R[i]

    s = max(0.0, s)
    m = len(J)
    if m:
        v = n == 0 and s / m or None
        for j in J:
            R[j] = v

    return R


def _hLine(canvLine, scp, ecp, y, hBlocks, FUZZ=rl_config._FUZZ):
    """
    Draw horizontal lines; do not draw through regions specified in hBlocks
    This also serves for vertical lines with a suitable canvLine
    """
    if hBlocks:
        hBlocks = hBlocks.get(y, None)
    if not hBlocks or scp >= hBlocks[-1][1] - FUZZ or ecp <= hBlocks[0][0] + FUZZ:
        canvLine(scp, y, ecp, y)
    else:
        i = 0
        n = len(hBlocks)
        while scp < ecp - FUZZ and i < n:
            x0, x1 = hBlocks[i]
            if x1 <= scp + FUZZ or x0 >= ecp - FUZZ:
                i += 1
                continue
            i0 = max(scp, x0)
            i1 = min(ecp, x1)
            if i0 > scp:
                canvLine(scp, y, i0, y)
            scp = i1

    if scp < ecp - FUZZ:
        canvLine(scp, y, ecp, y)
    return


def _multiLine(scp, ecp, y, canvLine, ws, count):
    offset = 0.5 * (count - 1) * ws
    y += offset
    for idx in xrange(count):
        canvLine(scp, y, ecp, y)
        y -= ws


def _convert2int(value, map, low, high, name, cmd):
    """private converter tries map(value) low<=int(value)<=high or finally an error"""
    try:
        return map[value]
    except KeyError:
        try:
            ivalue = int(value)
            if low <= ivalue <= high:
                return ivalue
        except:
            pass

    raise ValueError('Bad %s value %s in %s' % (name, value, str(cmd)))


def _endswith(obj, s):
    try:
        return obj.endswith(s)
    except:
        return 0


def spanFixDim(V0, V, spanCons, lim=None, FUZZ=rl_config._FUZZ):
    M = {}
    if not lim:
        lim = len(V0)
    for (x0, x1), v in spanCons.iteritems():
        if x0 >= lim:
            continue
        x1 += 1
        t = sum([ V[x] + M.get(x, 0) for x in xrange(x0, x1) ])
        if t >= v - FUZZ:
            continue
        X = [ x for x in xrange(x0, x1) if V0[x] is None ]
        if not X:
            continue
        v -= t
        v /= float(len(X))
        for x in X:
            M[x] = M.get(x, 0) + v

    for x, v in M.iteritems():
        V[x] += v

    return


class _ExpandedCellTuple(tuple):
    pass


class Table(Flowable):

    def __init__(self, data, colWidths=None, rowHeights=None, style=None, repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None, ident=None, hAlign=None, vAlign=None, normalizedData=0, cellStyles=None):
        global _emptyTableStyle
        self.ident = ident
        self.hAlign = hAlign or 'CENTER'
        self.vAlign = vAlign or 'MIDDLE'
        if not isinstance(data, (tuple, list)):
            raise ValueError('%s invalid data type' % self.identity())
        self._nrows = nrows = len(data)
        self._cellvalues = []
        _seqCW = isinstance(colWidths, (tuple, list))
        _seqRH = isinstance(rowHeights, (tuple, list))
        if nrows:
            self._ncols = ncols = max(map(_rowLen, data))
        elif colWidths and _seqCW:
            ncols = len(colWidths)
        else:
            ncols = 0
        if not emptyTableAction:
            emptyTableAction = rl_config.emptyTableAction
        self._longTableOptimize = getattr(self, '_longTableOptimize', rl_config.longTableOptimize)
        if not (nrows and ncols):
            if emptyTableAction == 'error':
                raise ValueError('%s must have at least a row and column' % self.identity())
            else:
                if emptyTableAction == 'indicate':
                    self.__class__ = Preformatted
                    if '_emptyTableStyle' not in globals().keys():
                        _emptyTableStyle = ParagraphStyle('_emptyTableStyle')
                        _emptyTableStyle.textColor = colors.red
                        _emptyTableStyle.backColor = colors.yellow
                    Preformatted.__init__(self, '%s(%d,%d)' % (self.__class__.__name__, nrows, ncols), _emptyTableStyle)
                elif emptyTableAction == 'ignore':
                    self.__class__ = Spacer
                    Spacer.__init__(self, 0, 0)
                else:
                    raise ValueError('%s bad emptyTableAction: "%s"' % (self.identity(), emptyTableAction))
                return
            if normalizedData:
                self._cellvalues = data
            else:
                self._cellvalues = data = self.normalizeData(data)
            colWidths = _seqCW or ncols * [colWidths]
        elif len(colWidths) != ncols:
            if rl_config.allowShortTableRows and isinstance(colWidths, list):
                n = len(colWidths)
                if n < ncols:
                    colWidths[n:] = (ncols - n) * [colWidths[-1]]
                else:
                    colWidths = colWidths[:ncols]
            else:
                raise ValueError('%s data error - %d columns in data but %d in column widths' % (self.identity(), ncols, len(colWidths)))
        if not _seqRH:
            rowHeights = nrows * [rowHeights]
        else:
            if len(rowHeights) != nrows:
                raise ValueError('%s data error - %d rows in data but %d in row heights' % (self.identity(), nrows, len(rowHeights)))
            for i, d in enumerate(data):
                n = len(d)
                if n != ncols:
                    if rl_config.allowShortTableRows and isinstance(d, list):
                        d[n:] = (ncols - n) * ['']
                    else:
                        raise ValueError('%s expected %d not %d columns in row %d!' % (self.identity(), ncols, n, i))

        self._rowHeights = self._argH = rowHeights
        self._colWidths = self._argW = colWidths
        if cellStyles is None:
            cellrows = []
            for i in xrange(nrows):
                cellcols = []
                for j in xrange(ncols):
                    cellcols.append(CellStyle(repr((i, j))))

                cellrows.append(cellcols)

            self._cellStyles = cellrows
        else:
            self._cellStyles = cellStyles
        self._bkgrndcmds = []
        self._linecmds = []
        self._spanCmds = []
        self._nosplitCmds = []
        self.repeatRows = repeatRows
        self.repeatCols = repeatCols
        self.splitByRow = splitByRow
        if style:
            self.setStyle(style)
        return

    def __repr__(self):
        """incomplete, but better than nothing"""
        r = getattr(self, '_rowHeights', '[unknown]')
        c = getattr(self, '_colWidths', '[unknown]')
        cv = getattr(self, '_cellvalues', '[unknown]')
        import pprint
        cv = pprint.pformat(cv)
        cv = cv.replace('\n', '\n  ')
        return '%s(\n rowHeights=%s,\n colWidths=%s,\n%s\n) # end table' % (self.__class__.__name__, r, c, cv)

    def normalizeData(self, data):
        """Takes a block of input data (list of lists etc.) and
        - coerces unicode strings to non-unicode UTF8
        - coerces nulls to ''
        -

        """

        def normCell(stuff):
            if stuff is None:
                return ''
            else:
                if isinstance(stuff, unicode):
                    return stuff.encode('utf8')
                else:
                    return stuff

                return

        outData = []
        for row in data:
            outRow = [ normCell(cell) for cell in row ]
            outData.append(outRow)

        from pprint import pprint as pp
        return outData

    def identity(self, maxLen=30):
        """Identify our selves as well as possible"""
        if self.ident:
            return self.ident
        else:
            vx = None
            nr = getattr(self, '_nrows', 'unknown')
            nc = getattr(self, '_ncols', 'unknown')
            cv = getattr(self, '_cellvalues', None)
            rh = getattr(self, '_rowHeights', None)
            if cv and 'unknown' not in (nr, nc):
                b = 0
                for i in xrange(nr):
                    for j in xrange(nc):
                        v = cv[i][j]
                        if isinstance(v, (list, tuple, Flowable)):
                            if not isinstance(v, (tuple, list)):
                                v = (v,)
                            r = ''
                            for vij in v:
                                r = vij.identity(maxLen)
                                if r and r[-4:] != '>...':
                                    break

                            if r and r[-4:] != '>...':
                                ix, jx, vx, b = (
                                 i, j, r, 1)
                        else:
                            v = v is None and '' or str(v)
                            ix, jx, vx = i, j, v
                            b = vx and isinstance(v, basestring) and 1 or 0
                            if maxLen:
                                vx = vx[:maxLen]
                        if b:
                            break

                    if b:
                        break

            if rh:
                tallest = '(tallest row %d)' % int(max(rh))
            else:
                tallest = ''
            if vx:
                vx = ' with cell(%d,%d) containing\n%s' % (ix, jx, repr(vx))
            else:
                vx = '...'
            return '<%s@0x%8.8X %s rows x %s cols%s>%s' % (self.__class__.__name__, id(self), nr, nc, tallest, vx)

    def _cellListIter(self, C, aW, aH):
        canv = getattr(self, 'canv', None)
        for c in C:
            if getattr(c, '__split_only__', None):
                for d in c.splitOn(canv, aW, aH):
                    yield d

            else:
                yield c

        return

    def _cellListProcess(self, C, aW, aH):
        if not isinstance(C, _ExpandedCellTuple):
            frame = None
            R = [].append
            for c in self._cellListIter(C, aW, aH):
                if isinstance(c, Indenter):
                    if not frame:
                        frame = CellFrame(_leftExtraIndent=0, _rightExtraIndent=0)
                    c.frameAction(frame)
                    if frame._leftExtraIndent < 1e-08 and frame._rightExtraIndent < 1e-08:
                        frame = None
                    continue
                if frame:
                    R(LIIndenter(c, leftIndent=frame._leftExtraIndent, rightIndent=frame._rightExtraIndent))
                else:
                    R(c)

            C = _ExpandedCellTuple(R.__self__)
        return C

    def _listCellGeom(self, V, w, s, W=None, H=None, aH=72000):
        if not V:
            return (0, 0)
        else:
            aW = w - s.leftPadding - s.rightPadding
            aH = aH - s.topPadding - s.bottomPadding
            t = 0
            w = 0
            canv = getattr(self, 'canv', None)
            sb0 = None
            for v in V:
                vw, vh = v.wrapOn(canv, aW, aH)
                sb = v.getSpaceBefore()
                sa = v.getSpaceAfter()
                if W is not None:
                    W.append(vw)
                if H is not None:
                    H.append(vh)
                w = max(w, vw)
                t += vh + sa + sb
                if sb0 is None:
                    sb0 = sb

            return (
             w, t - sb0 - sa)

    def _listValueWidth(self, V, aH=72000, aW=72000):
        if not V:
            return (0, 0)
        else:
            t = 0
            w = 0
            canv = getattr(self, 'canv', None)
            return max([ v.wrapOn(canv, aW, aH)[0] for v in V ])

    def _calc_width(self, availWidth, W=None):
        if getattr(self, '_width_calculated_once', None):
            return
        else:
            if not W:
                W = _calc_pc(self._argW, availWidth)
            if None in W:
                canv = getattr(self, 'canv', None)
                saved = None
                if self._spanCmds:
                    colSpanCells = self._colSpanCells
                    spanRanges = self._spanRanges
                else:
                    colSpanCells = ()
                    spanRanges = {}
                spanCons = {}
                if W is self._argW:
                    W0 = W
                    W = W[:]
                else:
                    W0 = W[:]
                V = self._cellvalues
                S = self._cellStyles
                while None in W:
                    j = W.index(None)
                    w = 0
                    for i, Vi in enumerate(V):
                        v = Vi[j]
                        s = S[i][j]
                        ji = (j, i)
                        span = spanRanges.get(ji, None)
                        if ji in colSpanCells and not span:
                            t = 0.0
                        else:
                            t = self._elementWidth(v, s)
                            if t is None:
                                raise ValueError("Flowable %s in cell(%d,%d) can't have auto width\n%s" % (v.identity(30), i, j, self.identity(30)))
                            t += s.leftPadding + s.rightPadding
                            if span:
                                c0 = span[0]
                                c1 = span[2]
                                if c0 != c1:
                                    x = (
                                     c0, c1)
                                    spanCons[x] = max(spanCons.get(x, t), t)
                                    t = 0
                        if t > w:
                            w = t

                    W[j] = w

                if spanCons:
                    try:
                        spanFixDim(W0, W, spanCons)
                    except:
                        annotateException('\nspanning problem in %s\nW0=%r W=%r\nspanCons=%r' % (self.identity(), W0, W, spanCons))

            self._colWidths = W
            width = 0
            self._colpositions = [0]
            for w in W:
                width = width + w
                self._colpositions.append(width)

            self._width = width
            self._width_calculated_once = 1
            return

    def _elementWidth(self, v, s):
        if isinstance(v, (list, tuple)):
            w = 0
            for e in v:
                ew = self._elementWidth(e, s)
                if ew is None:
                    return
                w = max(w, ew)

            return w
        if isinstance(v, Flowable) and v._fixedWidth:
            if hasattr(v, 'width') and isinstance(v.width, (int, float)):
                return v.width
            if hasattr(v, 'drawWidth') and isinstance(v.drawWidth, (int, float)):
                return v.drawWidth
        if hasattr(v, 'minWidth'):
            try:
                w = v.minWidth()
                if isinstance(w, (float, int)):
                    return w
            except AttributeError:
                pass

        if v is None:
            return 0
        else:
            try:
                v = str(v).split('\n')
            except:
                return 0

            fontName = s.fontname
            fontSize = s.fontsize
            return max([ stringWidth(x, fontName, fontSize) for x in v ])

    def _calc_height(self, availHeight, availWidth, H=None, W=None):
        H = self._argH
        if not W:
            W = _calc_pc(self._argW, availWidth)
        hmax = lim = len(H)
        longTable = self._longTableOptimize
        if None in H:
            canv = getattr(self, 'canv', None)
            saved = None
            if self._spanCmds:
                rowSpanCells = self._rowSpanCells
                colSpanCells = self._colSpanCells
                spanRanges = self._spanRanges
                colpositions = self._colpositions
            else:
                rowSpanCells = colSpanCells = ()
                spanRanges = {}
            if canv:
                saved = (canv._fontname, canv._fontsize, canv._leading)
            H0 = H
            H = H[:]
            self._rowHeights = H
            spanCons = {}
            FUZZ = rl_config._FUZZ
            while None in H:
                i = H.index(None)
                V = self._cellvalues[i]
                S = self._cellStyles[i]
                h = 0
                j = 0
                for j, (v, s, w) in enumerate(zip(V, S, W)):
                    ji = (
                     j, i)
                    span = spanRanges.get(ji, None)
                    if ji in rowSpanCells and not span:
                        continue
                    else:
                        if isinstance(v, (tuple, list, Flowable)):
                            if isinstance(v, Flowable):
                                v = (v,)
                            else:
                                v = flatten(v)
                            v = V[j] = self._cellListProcess(v, w, None)
                            if w is None and not self._canGetWidth(v):
                                raise ValueError("Flowable %s in cell(%d,%d) can't have auto width in\n%s" % (v[0].identity(30), i, j, self.identity(30)))
                            if canv:
                                canv._fontname, canv._fontsize, canv._leading = s.fontname, s.fontsize, s.leading or 1.2 * s.fontsize
                            if ji in colSpanCells:
                                if not span:
                                    continue
                                w = max(colpositions[span[2] + 1] - colpositions[span[0]], w)
                            dW, t = self._listCellGeom(v, w or self._listValueWidth(v), s)
                            if canv:
                                canv._fontname, canv._fontsize, canv._leading = saved
                            dW = dW + s.leftPadding + s.rightPadding
                            if not rl_config.allowTableBoundsErrors and dW > w:
                                from reportlab.platypus.doctemplate import LayoutError
                                raise LayoutError('Flowable %s (%sx%s points) too wide for cell(%d,%d) (%sx* points) in\n%s' % (v[0].identity(30), fp_str(dW), fp_str(t), i, j, fp_str(w), self.identity(30)))
                        else:
                            v = (v is not None and str(v) or '').split('\n')
                            t = (s.leading or 1.2 * s.fontsize) * len(v)
                        t += s.bottomPadding + s.topPadding
                        if span:
                            r0 = span[1]
                            r1 = span[3]
                            if r0 != r1:
                                x = (
                                 r0, r1)
                                spanCons[x] = max(spanCons.get(x, t), t)
                                t = 0
                    if t > h:
                        h = t

                H[i] = h
                if longTable:
                    hmax = i
                    height = sum(H[:i])
                    if height > availHeight:
                        if spanCons:
                            msr = max([ x[1] for x in spanCons.keys() ])
                            if hmax >= msr:
                                break

            if None not in H:
                hmax = lim
            if spanCons:
                try:
                    spanFixDim(H0, H, spanCons, lim=hmax)
                except:
                    annotateException('\nspanning problem in %s hmax=%s lim=%s avail=%s x %s\nH0=%r H=%r\nspanCons=%r' % (self.identity(), hmax, lim, availWidth, availHeight, H0, H, spanCons))

        height = self._height = sum(H[:hmax])
        self._rowpositions = [height]
        for h in H[:hmax]:
            height -= h
            self._rowpositions.append(height)

        assert abs(height) < 1e-08, '!!!!!%s\ninternal height error height=%r hmax=%d Sum(H[:%d])=%r\nH=%r\nrowPositions=%r' % (self.identity(), height, hmax, hmax, self._height, H[:hmax], self._rowpositions)
        self._hmax = hmax
        return

    def _calc(self, availWidth, availHeight):
        if (None in self._colWidths or '*' in self._colWidths) and self._hasVariWidthElements():
            W = self._calcPreliminaryWidths(availWidth)
        else:
            W = None
        if self._spanCmds:
            self._calcSpanRanges()
            if None in self._argH:
                self._calc_width(availWidth, W=W)
        if self._nosplitCmds:
            self._calcNoSplitRanges()
        self._calc_height(availHeight, availWidth, W=W)
        self._calc_width(availWidth, W=W)
        if self._spanCmds:
            self._calcSpanRects()
        return

    def _culprit(self):
        """Return a string describing the tallest element.
        
        Usually this is what causes tables to fail to split.  Currently
        tables are the only items to have a '_culprit' method. Doctemplate
        checks for it.
        """
        rh = self._rowHeights
        tallest = max(rh)
        rowNum = rh.index(tallest)
        return 'tallest cell %0.1f points' % tallest

    def _hasVariWidthElements(self, upToRow=None):
        """Check for flowables in table cells and warn up front.

        Allow a couple which we know are fixed size such as
        images and graphics."""
        if upToRow is None:
            upToRow = self._nrows
        for row in xrange(min(self._nrows, upToRow)):
            for col in xrange(self._ncols):
                value = self._cellvalues[row][col]
                if not self._canGetWidth(value):
                    return 1

        return 0

    def _canGetWidth(self, thing):
        """Can we work out the width quickly?"""
        if isinstance(thing, (list, tuple)):
            for elem in thing:
                if not self._canGetWidth(elem):
                    return 0

            return 1
        if isinstance(thing, Flowable):
            return thing._fixedWidth
        else:
            return 1

    def _calcPreliminaryWidths(self, availWidth):
        """Fallback algorithm for when main one fails.

        Where exact width info not given but things like
        paragraphs might be present, do a preliminary scan
        and assign some best-guess values."""
        W = list(self._argW)
        verbose = 0
        totalDefined = 0.0
        percentDefined = 0
        percentTotal = 0
        numberUndefined = 0
        numberGreedyUndefined = 0
        for w in W:
            if w is None:
                numberUndefined += 1
            elif w == '*':
                numberUndefined += 1
                numberGreedyUndefined += 1
            elif _endswith(w, '%'):
                percentDefined += 1
                percentTotal += float(w[:-1])
            else:
                assert isinstance(w, (int, float))
                totalDefined = totalDefined + w

        if verbose:
            print 'prelim width calculation.  %d columns, %d undefined width, %0.2f units remain' % (
             self._ncols, numberUndefined, availWidth - totalDefined)
        given = []
        sizeable = []
        unsizeable = []
        minimums = {}
        totalMinimum = 0
        elementWidth = self._elementWidth
        for colNo in xrange(self._ncols):
            w = W[colNo]
            if w is None or w == '*' or _endswith(w, '%'):
                siz = 1
                final = 0
                for rowNo in xrange(self._nrows):
                    value = self._cellvalues[rowNo][colNo]
                    style = self._cellStyles[rowNo][colNo]
                    pad = style.leftPadding + style.rightPadding
                    new = elementWidth(value, style)
                    if new:
                        new += pad
                    else:
                        new = pad
                    new += style.leftPadding + style.rightPadding
                    final = max(final, new)
                    siz = siz and self._canGetWidth(value)

                if siz:
                    sizeable.append(colNo)
                else:
                    unsizeable.append(colNo)
                minimums[colNo] = final
                totalMinimum += final
            else:
                given.append(colNo)

        if len(given) == self._ncols:
            return
        else:
            if verbose:
                print 'predefined width:   ', given
            if verbose:
                print 'uncomputable width: ', unsizeable
            if verbose:
                print 'computable width:   ', sizeable
            remaining = availWidth - (totalMinimum + totalDefined)
            if remaining > 0:
                definedPercentage = totalDefined / availWidth * 100
                percentTotal += definedPercentage
                if numberUndefined and percentTotal < 100:
                    undefined = numberGreedyUndefined or numberUndefined
                    defaultWeight = (100 - percentTotal) / undefined
                    percentTotal = 100
                    defaultDesired = defaultWeight / percentTotal * availWidth
                else:
                    defaultWeight = defaultDesired = 1
                desiredWidths = []
                totalDesired = 0
                effectiveRemaining = remaining
                for colNo, minimum in minimums.items():
                    w = W[colNo]
                    if _endswith(w, '%'):
                        desired = float(w[:-1]) / percentTotal * availWidth
                    elif w == '*':
                        desired = defaultDesired
                    else:
                        desired = not numberGreedyUndefined and defaultDesired or 1
                    if desired <= minimum:
                        W[colNo] = minimum
                    else:
                        desiredWidths.append((
                         desired - minimum, minimum, desired, colNo))
                        totalDesired += desired
                        effectiveRemaining += minimum

                if desiredWidths:
                    proportion = effectiveRemaining / totalDesired
                    desiredWidths.sort()
                    finalSet = []
                    for disappointment, minimum, desired, colNo in desiredWidths:
                        adjusted = proportion * desired
                        if adjusted < minimum:
                            W[colNo] = minimum
                            totalDesired -= desired
                            effectiveRemaining -= minimum
                            if totalDesired:
                                proportion = effectiveRemaining / totalDesired
                        else:
                            finalSet.append((minimum, desired, colNo))

                    for minimum, desired, colNo in finalSet:
                        adjusted = proportion * desired
                        assert adjusted >= minimum
                        W[colNo] = adjusted

            else:
                for colNo, minimum in minimums.items():
                    W[colNo] = minimum

            if verbose:
                print 'new widths are:', W
            self._argW = self._colWidths = W
            return W

    def minWidth(self):
        W = list(self._argW)
        width = 0
        elementWidth = self._elementWidth
        rowNos = xrange(self._nrows)
        values = self._cellvalues
        styles = self._cellStyles
        for colNo in xrange(len(W)):
            w = W[colNo]
            if w is None or w == '*' or _endswith(w, '%'):
                final = 0
                for rowNo in rowNos:
                    value = values[rowNo][colNo]
                    style = styles[rowNo][colNo]
                    new = elementWidth(value, style) + style.leftPadding + style.rightPadding
                    final = max(final, new)

                width += final
            else:
                width += float(w)

        return width

    def _calcSpanRanges(self):
        """Work out rects for tables which do row and column spanning.

        This creates some mappings to let the later code determine
        if a cell is part of a "spanned" range.
        self._spanRanges shows the 'coords' in integers of each
        'cell range', or None if it was clobbered:
        (col, row) -> (col0, row0, col1, row1)

        Any cell not in the key is not part of a spanned region
        """
        self._spanRanges = spanRanges = {}
        for x in xrange(self._ncols):
            for y in xrange(self._nrows):
                spanRanges[(x, y)] = (
                 x, y, x, y)

        self._colSpanCells = []
        self._rowSpanCells = []
        csa = self._colSpanCells.append
        rsa = self._rowSpanCells.append
        for cmd, start, stop in self._spanCmds:
            x0, y0 = start
            x1, y1 = stop
            if x0 < 0:
                x0 = x0 + self._ncols
            if x1 < 0:
                x1 = x1 + self._ncols
            if y0 < 0:
                y0 = y0 + self._nrows
            if y1 < 0:
                y1 = y1 + self._nrows
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            if x0 != x1 or y0 != y1:
                if x0 != x1:
                    for y in xrange(y0, y1 + 1):
                        for x in xrange(x0, x1 + 1):
                            csa((x, y))

                if y0 != y1:
                    for y in xrange(y0, y1 + 1):
                        for x in xrange(x0, x1 + 1):
                            rsa((x, y))

                for y in xrange(y0, y1 + 1):
                    for x in xrange(x0, x1 + 1):
                        spanRanges[(x, y)] = None

                spanRanges[(x0, y0)] = (
                 x0, y0, x1, y1)

        return

    def _calcNoSplitRanges(self):
        """
        This creates some mappings to let the later code determine
        if a cell is part of a "nosplit" range.
        self._nosplitRanges shows the 'coords' in integers of each
        'cell range', or None if it was clobbered:
        (col, row) -> (col0, row0, col1, row1)

        Any cell not in the key is not part of a spanned region
        """
        self._nosplitRanges = nosplitRanges = {}
        for x in xrange(self._ncols):
            for y in xrange(self._nrows):
                nosplitRanges[(x, y)] = (
                 x, y, x, y)

        self._colNoSplitCells = []
        self._rowNoSplitCells = []
        csa = self._colNoSplitCells.append
        rsa = self._rowNoSplitCells.append
        for cmd, start, stop in self._nosplitCmds:
            x0, y0 = start
            x1, y1 = stop
            if x0 < 0:
                x0 = x0 + self._ncols
            if x1 < 0:
                x1 = x1 + self._ncols
            if y0 < 0:
                y0 = y0 + self._nrows
            if y1 < 0:
                y1 = y1 + self._nrows
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            if x0 != x1 or y0 != y1:
                if x0 != x1:
                    for y in xrange(y0, y1 + 1):
                        for x in xrange(x0, x1 + 1):
                            csa((x, y))

                if y0 != y1:
                    for y in xrange(y0, y1 + 1):
                        for x in xrange(x0, x1 + 1):
                            rsa((x, y))

                for y in xrange(y0, y1 + 1):
                    for x in xrange(x0, x1 + 1):
                        nosplitRanges[(x, y)] = None

                nosplitRanges[(x0, y0)] = (
                 x0, y0, x1, y1)

        return

    def _calcSpanRects(self):
        """Work out rects for tables which do row and column spanning.

        Based on self._spanRanges, which is already known,
        and the widths which were given or previously calculated,
        self._spanRects shows the real coords for drawing:
            
            (col, row) -> (x, y, width, height)

        for each cell.  Any cell which 'does not exist' as another
        has spanned over it will get a None entry on the right
        """
        spanRects = getattr(self, '_spanRects', {})
        hmax = getattr(self, '_hmax', None)
        longTable = self._longTableOptimize
        if spanRects and (longTable and hmax == self._hmax_spanRects or not longTable):
            return
        colpositions = self._colpositions
        rowpositions = self._rowpositions
        vBlocks = {}
        hBlocks = {}
        rlim = len(rowpositions) - 1
        for coord, value in self._spanRanges.iteritems():
            if value is None:
                spanRects[coord] = None
            else:
                col0, row0, col1, row1 = value
                if row1 >= rlim:
                    continue
                col, row = coord
                if col1 - col0 > 0:
                    for _ in xrange(col0 + 1, col1 + 1):
                        vBlocks.setdefault(colpositions[_], []).append((rowpositions[row1 + 1], rowpositions[row0]))

                if row1 - row0 > 0:
                    for _ in xrange(row0 + 1, row1 + 1):
                        hBlocks.setdefault(rowpositions[_], []).append((colpositions[col0], colpositions[col1 + 1]))

                x = colpositions[col0]
                y = rowpositions[row1 + 1]
                width = colpositions[col1 + 1] - x
                height = rowpositions[row0] - y
                spanRects[coord] = (x, y, width, height)

        for _ in (hBlocks, vBlocks):
            for value in _.values():
                value.sort()

        self._spanRects = spanRects
        self._vBlocks = vBlocks
        self._hBlocks = hBlocks
        self._hmax_spanRects = hmax
        return

    def setStyle(self, tblstyle):
        if not isinstance(tblstyle, TableStyle):
            tblstyle = TableStyle(tblstyle)
        for cmd in tblstyle.getCommands():
            self._addCommand(cmd)

        for k, v in tblstyle._opts.items():
            setattr(self, k, v)

        for a in ('spaceBefore', 'spaceAfter'):
            if not hasattr(self, a) and hasattr(tblstyle, a):
                setattr(self, a, getattr(tblstyle, a))

    def _addCommand(self, cmd):
        if cmd[0] in ('BACKGROUND', 'ROWBACKGROUNDS', 'COLBACKGROUNDS'):
            self._bkgrndcmds.append(cmd)
        elif cmd[0] == 'SPAN':
            self._spanCmds.append(cmd)
        elif cmd[0] == 'NOSPLIT':
            self._nosplitCmds.append(cmd)
        elif _isLineCommand(cmd):
            cmd = list(cmd)
            if len(cmd) < 5:
                raise ValueError('bad line command ' + str(cmd))
            if len(cmd) < 6:
                cmd.append(1)
            else:
                cap = _convert2int(cmd[5], LINECAPS, 0, 2, 'cap', cmd)
                cmd[5] = cap
            if len(cmd) < 7:
                cmd.append(None)
            if len(cmd) < 8:
                cmd.append(1)
            else:
                join = _convert2int(cmd[7], LINEJOINS, 0, 2, 'join', cmd)
                cmd[7] = join
            if len(cmd) < 9:
                cmd.append(1)
            else:
                lineCount = cmd[8]
                if lineCount is None:
                    lineCount = 1
                    cmd[8] = lineCount
                assert lineCount >= 1
            if len(cmd) < 10:
                cmd.append(cmd[3])
            else:
                space = cmd[9]
                if space is None:
                    space = cmd[3]
                    cmd[9] = space
            assert len(cmd) == 10
            self._linecmds.append(tuple(cmd))
        else:
            (op, (sc, sr), (ec, er)), values = cmd[:3], cmd[3:]
            if sc < 0:
                sc = sc + self._ncols
            if ec < 0:
                ec = ec + self._ncols
            if sr < 0:
                sr = sr + self._nrows
            if er < 0:
                er = er + self._nrows
            for i in xrange(sr, er + 1):
                for j in xrange(sc, ec + 1):
                    _setCellStyle(self._cellStyles, i, j, op, values)

        return

    def _drawLines(self):
        ccap, cdash, cjoin = (None, None, None)
        self.canv.saveState()
        for op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space in self._linecmds:
            if isinstance(sr, basestring) and sr.startswith('split'):
                continue
            if sc < 0:
                sc = sc + self._ncols
            if ec < 0:
                ec = ec + self._ncols
            if sr < 0:
                sr = sr + self._nrows
            if er < 0:
                er = er + self._nrows
            if cap != None and ccap != cap:
                self.canv.setLineCap(cap)
                ccap = cap
            if dash is None or dash == []:
                if cdash is not None:
                    self.canv.setDash()
                    cdash = None
            elif dash != cdash:
                self.canv.setDash(dash)
                cdash = dash
            if join is not None and cjoin != join:
                self.canv.setLineJoin(join)
                cjoin = join
            getattr(self, _LineOpMap.get(op, '_drawUnknown'))((sc, sr), (ec, er), weight, color, count, space)

        self.canv.restoreState()
        self._curcolor = None
        return

    def _drawUnknown(self, start, end, weight, color, count, space):
        import sys
        op = sys._getframe(1).f_locals['op']
        raise ValueError("Unknown line command '%s'" % op)

    def _drawGrid(self, start, end, weight, color, count, space):
        self._drawBox(start, end, weight, color, count, space)
        self._drawInnerGrid(start, end, weight, color, count, space)

    def _drawBox(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        self._drawHLines((sc, sr), (ec, sr), weight, color, count, space)
        self._drawHLines((sc, er + 1), (ec, er + 1), weight, color, count, space)
        self._drawVLines((sc, sr), (sc, er), weight, color, count, space)
        self._drawVLines((ec + 1, sr), (ec + 1, er), weight, color, count, space)

    def _drawInnerGrid(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        self._drawHLines((sc, sr + 1), (ec, er), weight, color, count, space)
        self._drawVLines((sc + 1, sr), (ec, er), weight, color, count, space)

    def _prepLine(self, weight, color):
        if color != self._curcolor:
            self.canv.setStrokeColor(color)
            self._curcolor = color
        if weight != self._curweight:
            self.canv.setLineWidth(weight)
            self._curweight = weight

    def _drawHLines(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        ecp = self._colpositions[sc:ec + 2]
        rp = self._rowpositions[sr:er + 1]
        if len(ecp) <= 1 or len(rp) < 1:
            return
        self._prepLine(weight, color)
        scp = ecp[0]
        ecp = ecp[-1]
        hBlocks = getattr(self, '_hBlocks', {})
        canvLine = self.canv.line
        if count == 1:
            for y in rp:
                _hLine(canvLine, scp, ecp, y, hBlocks)

        else:
            lf = lambda x0, y0, x1, y1, canvLine=canvLine, ws=weight + space, count=count: _multiLine(x0, x1, y0, canvLine, ws, count)
            for y in rp:
                _hLine(lf, scp, ecp, y, hBlocks)

    def _drawHLinesB(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        self._drawHLines((sc, sr + 1), (ec, er + 1), weight, color, count, space)

    def _drawVLines(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        erp = self._rowpositions[sr:er + 2]
        cp = self._colpositions[sc:ec + 1]
        if len(erp) <= 1 or len(cp) < 1:
            return
        self._prepLine(weight, color)
        srp = erp[0]
        erp = erp[-1]
        vBlocks = getattr(self, '_vBlocks', {})
        canvLine = lambda y0, x0, y1, x1, _line=self.canv.line: _line(x0, y0, x1, y1)
        if count == 1:
            for x in cp:
                _hLine(canvLine, erp, srp, x, vBlocks)

        else:
            lf = lambda x0, y0, x1, y1, canvLine=canvLine, ws=weight + space, count=count: _multiLine(x0, x1, y0, canvLine, ws, count)
            for x in cp:
                _hLine(lf, erp, srp, x, vBlocks)

    def _drawVLinesA(self, start, end, weight, color, count, space):
        sc, sr = start
        ec, er = end
        self._drawVLines((sc + 1, sr), (ec + 1, er), weight, color, count, space)

    def wrap(self, availWidth, availHeight):
        self._calc(availWidth, availHeight)
        self.availWidth = availWidth
        return (self._width, self._height)

    def onSplit(self, T, byRow=1):
        """
        This method will be called when the Table is split.
        Special purpose tables can override to do special stuff.
        """
        pass

    def _cr_0(self, n, cmds):
        for c in cmds:
            c = tuple(c)
            (sc, sr), (ec, er) = c[1:3]
            if sr >= n:
                continue
            if er >= n:
                er = n - 1
            self._addCommand((c[0],) + ((sc, sr), (ec, er)) + c[3:])

    def _cr_1_1(self, n, repeatRows, cmds):
        for c in cmds:
            c = tuple(c)
            (sc, sr), (ec, er) = c[1:3]
            if sr in ('splitfirst', 'splitlast'):
                self._addCommand(c)
            else:
                if sr >= 0 and sr >= repeatRows and sr < n and er >= 0 and er < n:
                    continue
                if sr >= repeatRows and sr < n:
                    sr = repeatRows
                elif sr >= repeatRows and sr >= n:
                    sr = sr + repeatRows - n
                if er >= repeatRows and er < n:
                    er = repeatRows
                elif er >= repeatRows and er >= n:
                    er = er + repeatRows - n
                self._addCommand((c[0],) + ((sc, sr), (ec, er)) + c[3:])

    def _cr_1_0(self, n, cmds):
        for c in cmds:
            c = tuple(c)
            (sc, sr), (ec, er) = c[1:3]
            if sr in ('splitfirst', 'splitlast'):
                self._addCommand(c)
            else:
                if er >= 0 and er < n:
                    continue
                if sr >= 0 and sr < n:
                    sr = 0
                if sr >= n:
                    sr = sr - n
                if er >= n:
                    er = er - n
                self._addCommand((c[0],) + ((sc, sr), (ec, er)) + c[3:])

    def _splitRows(self, availHeight):
        n = self._getFirstPossibleSplitRowPosition(availHeight)
        if n <= self.repeatRows:
            return []
        lim = len(self._rowHeights)
        if n == lim:
            return [self]
        repeatRows = self.repeatRows
        repeatCols = self.repeatCols
        splitByRow = self.splitByRow
        data = self._cellvalues
        ident = self.ident
        if ident:
            ident = IdentStr(ident)
        R0 = self.__class__(data[:n], colWidths=self._colWidths, rowHeights=self._argH[:n], repeatRows=repeatRows, repeatCols=repeatCols, splitByRow=splitByRow, normalizedData=1, cellStyles=self._cellStyles[:n], ident=ident)
        A = []
        for op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space in self._linecmds:
            if isinstance(sr, basestring) and sr.startswith('split'):
                A.append((op, (sc, sr), (ec, sr), weight, color, cap, dash, join, count, space))
                if sr == 'splitlast':
                    sr = er = n - 1
                elif sr == 'splitfirst':
                    sr = n
                    er = n
            if sc < 0:
                sc = sc + self._ncols
            if ec < 0:
                ec = ec + self._ncols
            if sr < 0:
                sr = sr + self._nrows
            if er < 0:
                er = er + self._nrows
            if op in ('BOX', 'OUTLINE', 'GRID'):
                if sr < n and er >= n:
                    A.append(('LINEABOVE', (sc, sr), (ec, sr), weight, color, cap, dash, join, count, space))
                    A.append(('LINEBEFORE', (sc, sr), (sc, er), weight, color, cap, dash, join, count, space))
                    A.append(('LINEAFTER', (ec, sr), (ec, er), weight, color, cap, dash, join, count, space))
                    A.append(('LINEBELOW', (sc, er), (ec, er), weight, color, cap, dash, join, count, space))
                    if op == 'GRID':
                        A.append(('LINEBELOW', (sc, n - 1), (ec, n - 1), weight, color, cap, dash, join, count, space))
                        A.append(('LINEABOVE', (sc, n), (ec, n), weight, color, cap, dash, join, count, space))
                        A.append(('INNERGRID', (sc, sr), (ec, er), weight, color, cap, dash, join, count, space))
                else:
                    A.append((op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space))
            elif op in ('INNERGRID', 'LINEABOVE'):
                if sr < n and er >= n:
                    A.append(('LINEBELOW', (sc, n - 1), (ec, n - 1), weight, color, cap, dash, join, count, space))
                    A.append(('LINEABOVE', (sc, n), (ec, n), weight, color, cap, dash, join, count, space))
                A.append((op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space))
            elif op == 'LINEBELOW':
                if sr < n and er >= n - 1:
                    A.append(('LINEABOVE', (sc, n), (ec, n), weight, color, cap, dash, join, count, space))
                A.append((op, (sc, sr), (ec, er), weight, color))
            elif op == 'LINEABOVE':
                if sr <= n and er >= n:
                    A.append(('LINEBELOW', (sc, n - 1), (ec, n - 1), weight, color, cap, dash, join, count, space))
                A.append((op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space))
            else:
                A.append((op, (sc, sr), (ec, er), weight, color, cap, dash, join, count, space))

        R0._cr_0(n, A)
        R0._cr_0(n, self._bkgrndcmds)
        R0._cr_0(n, self._spanCmds)
        R0._cr_0(n, self._nosplitCmds)
        if ident:
            ident = IdentStr(ident)
        if repeatRows:
            R1 = self.__class__(data[:repeatRows] + data[n:], colWidths=self._colWidths, rowHeights=self._argH[:repeatRows] + self._argH[n:], repeatRows=repeatRows, repeatCols=repeatCols, splitByRow=splitByRow, normalizedData=1, cellStyles=self._cellStyles[:repeatRows] + self._cellStyles[n:], ident=ident)
            R1._cr_1_1(n, repeatRows, A)
            R1._cr_1_1(n, repeatRows, self._bkgrndcmds)
            R1._cr_1_1(n, repeatRows, self._spanCmds)
            R1._cr_1_1(n, repeatRows, self._nosplitCmds)
        else:
            R1 = self.__class__(data[n:], colWidths=self._colWidths, rowHeights=self._argH[n:], repeatRows=repeatRows, repeatCols=repeatCols, splitByRow=splitByRow, normalizedData=1, cellStyles=self._cellStyles[n:], ident=ident)
            R1._cr_1_0(n, A)
            R1._cr_1_0(n, self._bkgrndcmds)
            R1._cr_1_0(n, self._spanCmds)
            R1._cr_1_0(n, self._nosplitCmds)
        R0.hAlign = R1.hAlign = self.hAlign
        R0.vAlign = R1.vAlign = self.vAlign
        self.onSplit(R0)
        self.onSplit(R1)
        return [R0, R1]

    def _getRowImpossible(impossible, cells, ranges):
        for xy in cells:
            r = ranges[xy]
            if r != None:
                y1, y2 = r[1], r[3]
                if y1 != y2:
                    ymin = min(y1, y2)
                    ymax = max(y1, y2)
                    y = ymin + 1
                    while 1:
                        if y > ymax:
                            break
                        impossible[y] = None
                        y += 1

        return

    _getRowImpossible = staticmethod(_getRowImpossible)

    def _getFirstPossibleSplitRowPosition(self, availHeight):
        impossible = {}
        if self._spanCmds:
            self._getRowImpossible(impossible, self._rowSpanCells, self._spanRanges)
        if self._nosplitCmds:
            self._getRowImpossible(impossible, self._rowNoSplitCells, self._nosplitRanges)
        h = 0
        n = 1
        split_at = 0
        for rh in self._rowHeights:
            if h + rh > availHeight:
                break
            if n not in impossible:
                split_at = n
            h = h + rh
            n = n + 1

        return split_at

    def split(self, availWidth, availHeight):
        self._calc(availWidth, availHeight)
        if self.splitByRow:
            if not rl_config.allowTableBoundsErrors and self._width > availWidth:
                return []
            return self._splitRows(availHeight)
        raise NotImplementedError

    def draw(self):
        self._curweight = self._curcolor = self._curcellstyle = None
        self._drawBkgrnd()
        if not self._spanCmds:
            for row, rowstyle, rowpos, rowheight in zip(self._cellvalues, self._cellStyles, self._rowpositions[1:], self._rowHeights):
                for cellval, cellstyle, colpos, colwidth in zip(row, rowstyle, self._colpositions[:-1], self._colWidths):
                    self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))

        else:
            for rowNo in xrange(self._nrows):
                for colNo in xrange(self._ncols):
                    cellRect = self._spanRects[(colNo, rowNo)]
                    if cellRect is not None:
                        x, y, width, height = cellRect
                        cellval = self._cellvalues[rowNo][colNo]
                        cellstyle = self._cellStyles[rowNo][colNo]
                        self._drawCell(cellval, cellstyle, (x, y), (width, height))

        self._drawLines()
        return

    def _drawBkgrnd(self):
        nrows = self._nrows
        ncols = self._ncols
        canv = self.canv
        colpositions = self._colpositions
        rowpositions = self._rowpositions
        rowHeights = self._rowHeights
        colWidths = self._colWidths
        spanRects = getattr(self, '_spanRects', None)
        for cmd, (sc, sr), (ec, er), arg in self._bkgrndcmds:
            if sc < 0:
                sc = sc + ncols
            if ec < 0:
                ec = ec + ncols
            if sr < 0:
                sr = sr + nrows
            if er < 0:
                er = er + nrows
            x0 = colpositions[sc]
            y0 = rowpositions[sr]
            x1 = colpositions[min(ec + 1, ncols)]
            y1 = rowpositions[min(er + 1, nrows)]
            w, h = x1 - x0, y1 - y0
            if hasattr(arg, '__call__'):
                arg(self, canv, x0, y0, w, h)
            elif cmd == 'ROWBACKGROUNDS':
                colorCycle = map(colors.toColorOrNone, arg)
                count = len(colorCycle)
                rowCount = er - sr + 1
                for i in xrange(rowCount):
                    color = colorCycle[i % count]
                    h = rowHeights[sr + i]
                    if color:
                        canv.setFillColor(color)
                        canv.rect(x0, y0, w, -h, stroke=0, fill=1)
                    y0 = y0 - h

            elif cmd == 'COLBACKGROUNDS':
                colorCycle = map(colors.toColorOrNone, arg)
                count = len(colorCycle)
                colCount = ec - sc + 1
                for i in xrange(colCount):
                    color = colorCycle[i % count]
                    w = colWidths[sc + i]
                    if color:
                        canv.setFillColor(color)
                        canv.rect(x0, y0, w, h, stroke=0, fill=1)
                    x0 = x0 + w

            else:
                color = colors.toColorOrNone(arg)
                if color:
                    if ec == sc and er == sr and spanRects:
                        xywh = spanRects.get((sc, sr))
                        if xywh:
                            x0, y0, w, h = xywh
                    canv.setFillColor(color)
                    canv.rect(x0, y0, w, h, stroke=0, fill=1)

        return

    def _drawCell(self, cellval, cellstyle, pos, size):
        colpos, rowpos = pos
        colwidth, rowheight = size
        if self._curcellstyle is not cellstyle:
            cur = self._curcellstyle
            if cur is None or cellstyle.color != cur.color:
                self.canv.setFillColor(cellstyle.color)
            if cur is None or cellstyle.leading != cur.leading or cellstyle.fontname != cur.fontname or cellstyle.fontsize != cur.fontsize:
                self.canv.setFont(cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
            self._curcellstyle = cellstyle
        just = cellstyle.alignment
        valign = cellstyle.valign
        if isinstance(cellval, (tuple, list, Flowable)):
            if not isinstance(cellval, (tuple, list)):
                cellval = (cellval,)
            W = []
            H = []
            w, h = self._listCellGeom(cellval, colwidth, cellstyle, W=W, H=H, aH=rowheight)
            if valign == 'TOP':
                y = rowpos + rowheight - cellstyle.topPadding
            elif valign == 'BOTTOM':
                y = rowpos + cellstyle.bottomPadding + h
            else:
                y = rowpos + (rowheight + cellstyle.bottomPadding - cellstyle.topPadding + h) / 2.0
            if cellval:
                y += cellval[0].getSpaceBefore()
            for v, w, h in zip(cellval, W, H):
                if just == 'LEFT':
                    x = colpos + cellstyle.leftPadding
                elif just == 'RIGHT':
                    x = colpos + colwidth - cellstyle.rightPadding - w
                elif just in ('CENTRE', 'CENTER'):
                    x = colpos + (colwidth + cellstyle.leftPadding - cellstyle.rightPadding - w) / 2.0
                else:
                    raise ValueError('Invalid justification %s' % just)
                y -= v.getSpaceBefore()
                y -= h
                v.drawOn(self.canv, x, y)
                y -= v.getSpaceAfter()

        else:
            if just == 'LEFT':
                draw = self.canv.drawString
                x = colpos + cellstyle.leftPadding
            elif just in ('CENTRE', 'CENTER'):
                draw = self.canv.drawCentredString
                x = colpos + (colwidth + cellstyle.leftPadding - cellstyle.rightPadding) * 0.5
            elif just == 'RIGHT':
                draw = self.canv.drawRightString
                x = colpos + colwidth - cellstyle.rightPadding
            elif just == 'DECIMAL':
                draw = self.canv.drawAlignedString
                x = colpos + colwidth - cellstyle.rightPadding
            else:
                raise ValueError('Invalid justification %s' % just)
            vals = str(cellval).split('\n')
            n = len(vals)
            leading = cellstyle.leading
            fontsize = cellstyle.fontsize
            if valign == 'BOTTOM':
                y = rowpos + cellstyle.bottomPadding + n * leading - fontsize
            elif valign == 'TOP':
                y = rowpos + rowheight - cellstyle.topPadding - fontsize
            elif valign == 'MIDDLE':
                y = rowpos + (cellstyle.bottomPadding + rowheight - cellstyle.topPadding + n * leading) / 2.0 - fontsize
            else:
                raise ValueError("Bad valign: '%s'" % str(valign))
            for v in vals:
                draw(x, y, v)
                y -= leading

        onDraw = getattr(cellval, 'onDraw', None)
        if onDraw:
            onDraw(self.canv, cellval.kind, cellval.label)
        if cellstyle.href:
            self.canv.linkURL(cellstyle.href, (colpos, rowpos, colpos + colwidth, rowpos + rowheight), relative=1)
        if cellstyle.destination:
            self.canv.linkRect('', cellstyle.destination, Rect=(colpos, rowpos, colpos + colwidth, rowpos + rowheight), relative=1)
        return


_LineOpMap = {'GRID': '_drawGrid', 'BOX': '_drawBox', 
   'OUTLINE': '_drawBox', 
   'INNERGRID': '_drawInnerGrid', 
   'LINEBELOW': '_drawHLinesB', 
   'LINEABOVE': '_drawHLines', 
   'LINEBEFORE': '_drawVLines', 
   'LINEAFTER': '_drawVLinesA'}

class LongTable(Table):
    """Henning von Bargen's changes will be active"""
    _longTableOptimize = 1


LINECOMMANDS = _LineOpMap.keys()

def _isLineCommand(cmd):
    return cmd[0] in LINECOMMANDS


def _setCellStyle(cellStyles, i, j, op, values):
    new = cellStyles[i][j]
    if op == 'FONT':
        n = len(values)
        new.fontname = values[0]
        if n > 1:
            new.fontsize = values[1]
            if n > 2:
                new.leading = values[2]
            else:
                new.leading = new.fontsize * 1.2
    elif op in ('FONTNAME', 'FACE'):
        new.fontname = values[0]
    elif op in ('SIZE', 'FONTSIZE'):
        new.fontsize = values[0]
    elif op == 'LEADING':
        new.leading = values[0]
    elif op == 'TEXTCOLOR':
        new.color = colors.toColor(values[0], colors.Color(0, 0, 0))
    elif op in ('ALIGN', 'ALIGNMENT'):
        new.alignment = values[0]
    elif op == 'VALIGN':
        new.valign = values[0]
    elif op == 'LEFTPADDING':
        new.leftPadding = values[0]
    elif op == 'RIGHTPADDING':
        new.rightPadding = values[0]
    elif op == 'TOPPADDING':
        new.topPadding = values[0]
    elif op == 'BOTTOMPADDING':
        new.bottomPadding = values[0]
    elif op == 'HREF':
        new.href = values[0]
    elif op == 'DESTINATION':
        new.destination = values[0]


GRID_STYLE = TableStyle([
 (
  'GRID', (0, 0), (-1, -1), 0.25, colors.black),
 (
  'ALIGN', (1, 1), (-1, -1), 'RIGHT')])
BOX_STYLE = TableStyle([
 (
  'BOX', (0, 0), (-1, -1), 0.5, colors.black),
 (
  'ALIGN', (1, 1), (-1, -1), 'RIGHT')])
LABELED_GRID_STYLE = TableStyle([
 (
  'INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
 (
  'BOX', (0, 0), (-1, -1), 2, colors.black),
 (
  'LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
 (
  'LINEAFTER', (0, 0), (0, -1), 2, colors.black),
 (
  'ALIGN', (1, 1), (-1, -1), 'RIGHT')])
COLORED_GRID_STYLE = TableStyle([
 (
  'INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
 (
  'BOX', (0, 0), (-1, -1), 2, colors.red),
 (
  'LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
 (
  'LINEAFTER', (0, 0), (0, -1), 2, colors.black),
 (
  'ALIGN', (1, 1), (-1, -1), 'RIGHT')])
LIST_STYLE = TableStyle([
 (
  'LINEABOVE', (0, 0), (-1, 0), 2, colors.green),
 (
  'LINEABOVE', (0, 1), (-1, -1), 0.25, colors.black),
 (
  'LINEBELOW', (0, -1), (-1, -1), 2, colors.green),
 (
  'ALIGN', (1, 1), (-1, -1), 'RIGHT')])
if __name__ == '__main__':
    from tests.test_platypus_tables import old_tables_test
    old_tables_test()