# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\table.pyc
# Compiled at: 2012-11-06 09:32:24
"""
Place a table below the x-axis at location loc.

The table consists of a grid of cells.

The grid need not be rectangular and can have holes.

Cells are added by specifying their row and column.

For the purposes of positioning the cell at (0, 0) is
assumed to be at the top left and the cell at (max_row, max_col)
is assumed to be at bottom right.

You can add additional cells outside this range to have convenient
ways of positioning more interesting grids.

Author    : John Gill <jng@europe.renre.com>
Copyright : 2004 John Gill and John Hunter
License   : matplotlib license

"""
from __future__ import division, print_function
import warnings, artist
from artist import Artist, allow_rasterization
from patches import Rectangle
from cbook import is_string_like
from matplotlib import docstring
from text import Text
from transforms import Bbox

class Cell(Rectangle):
    """
    A cell is a Rectangle with some associated text.

    """
    PAD = 0.1

    def __init__(self, xy, width, height, edgecolor='k', facecolor='w', fill=True, text='', loc=None, fontproperties=None):
        Rectangle.__init__(self, xy, width=width, height=height, edgecolor=edgecolor, facecolor=facecolor)
        self.set_clip_on(False)
        if loc is None:
            loc = 'right'
        self._loc = loc
        self._text = Text(x=xy[0], y=xy[1], text=text, fontproperties=fontproperties)
        self._text.set_clip_on(False)
        return

    def set_transform(self, trans):
        Rectangle.set_transform(self, trans)

    def set_figure(self, fig):
        Rectangle.set_figure(self, fig)
        self._text.set_figure(fig)

    def get_text(self):
        """Return the cell Text intance"""
        return self._text

    def set_fontsize(self, size):
        self._text.set_fontsize(size)

    def get_fontsize(self):
        """Return the cell fontsize"""
        return self._text.get_fontsize()

    def auto_set_font_size(self, renderer):
        """ Shrink font size until text fits. """
        fontsize = self.get_fontsize()
        required = self.get_required_width(renderer)
        while fontsize > 1 and required > self.get_width():
            fontsize -= 1
            self.set_fontsize(fontsize)
            required = self.get_required_width(renderer)

        return fontsize

    @allow_rasterization
    def draw(self, renderer):
        if not self.get_visible():
            return
        Rectangle.draw(self, renderer)
        self._set_text_position(renderer)
        self._text.draw(renderer)

    def _set_text_position(self, renderer):
        """ Set text up so it draws in the right place.

        Currently support 'left', 'center' and 'right'
        """
        bbox = self.get_window_extent(renderer)
        l, b, w, h = bbox.bounds
        self._text.set_verticalalignment('center')
        y = b + h / 2.0
        if self._loc == 'center':
            self._text.set_horizontalalignment('center')
            x = l + w / 2.0
        elif self._loc == 'left':
            self._text.set_horizontalalignment('left')
            x = l + w * self.PAD
        else:
            self._text.set_horizontalalignment('right')
            x = l + w * (1.0 - self.PAD)
        self._text.set_position((x, y))

    def get_text_bounds(self, renderer):
        """ Get text bounds in axes co-ordinates. """
        bbox = self._text.get_window_extent(renderer)
        bboxa = bbox.inverse_transformed(self.get_data_transform())
        return bboxa.bounds

    def get_required_width(self, renderer):
        """ Get width required for this cell. """
        l, b, w, h = self.get_text_bounds(renderer)
        return w * (1.0 + 2.0 * self.PAD)

    def set_text_props(self, **kwargs):
        """update the text properties with kwargs"""
        self._text.update(kwargs)


class Table(Artist):
    """
    Create a table of cells.

    Table can have (optional) row and column headers.

    Each entry in the table can be either text or patches.

    Column widths and row heights for the table can be specifified.

    Return value is a sequence of text, line and patch instances that make
    up the table
    """
    codes = {'best': 0, 'upper right': 1, 
       'upper left': 2, 
       'lower left': 3, 
       'lower right': 4, 
       'center left': 5, 
       'center right': 6, 
       'lower center': 7, 
       'upper center': 8, 
       'center': 9, 
       'top right': 10, 
       'top left': 11, 
       'bottom left': 12, 
       'bottom right': 13, 
       'right': 14, 
       'left': 15, 
       'top': 16, 
       'bottom': 17}
    FONTSIZE = 10
    AXESPAD = 0.02

    def __init__(self, ax, loc=None, bbox=None):
        Artist.__init__(self)
        if is_string_like(loc) and loc not in self.codes:
            warnings.warn('Unrecognized location %s. Falling back on bottom; valid locations are\n%s\t' % (
             loc, ('\n\t').join(self.codes.iterkeys())))
            loc = 'bottom'
        if is_string_like(loc):
            loc = self.codes.get(loc, 1)
        self.set_figure(ax.figure)
        self._axes = ax
        self._loc = loc
        self._bbox = bbox
        self.set_transform(ax.transAxes)
        self._texts = []
        self._cells = {}
        self._autoRows = []
        self._autoColumns = []
        self._autoFontsize = True
        self._cachedRenderer = None
        return

    def add_cell(self, row, col, *args, **kwargs):
        """ Add a cell to the table. """
        xy = (0, 0)
        cell = Cell(xy, *args, **kwargs)
        cell.set_figure(self.figure)
        cell.set_transform(self.get_transform())
        cell.set_clip_on(False)
        self._cells[(row, col)] = cell

    def _approx_text_height(self):
        return self.FONTSIZE / 72.0 * self.figure.dpi / self._axes.bbox.height * 1.2

    @allow_rasterization
    def draw(self, renderer):
        if renderer is None:
            renderer = self._cachedRenderer
        if renderer is None:
            raise RuntimeError('No renderer defined')
        self._cachedRenderer = renderer
        if not self.get_visible():
            return
        else:
            renderer.open_group('table')
            self._update_positions(renderer)
            keys = self._cells.keys()
            keys.sort()
            for key in keys:
                self._cells[key].draw(renderer)

            renderer.close_group('table')
            return

    def _get_grid_bbox(self, renderer):
        """Get a bbox, in axes co-ordinates for the cells.

        Only include those in the range (0,0) to (maxRow, maxCol)"""
        boxes = [ self._cells[pos].get_window_extent(renderer) for pos in self._cells.iterkeys() if pos[0] >= 0 and pos[1] >= 0
                ]
        bbox = Bbox.union(boxes)
        return bbox.inverse_transformed(self.get_transform())

    def contains(self, mouseevent):
        """Test whether the mouse event occurred in the table.

        Returns T/F, {}
        """
        if callable(self._contains):
            return self._contains(self, mouseevent)
        else:
            if self._cachedRenderer is not None:
                boxes = [ self._cells[pos].get_window_extent(self._cachedRenderer) for pos in self._cells.iterkeys() if pos[0] >= 0 and pos[1] >= 0
                        ]
                bbox = Bbox.union(boxes)
                return (
                 bbox.contains(mouseevent.x, mouseevent.y), {})
            else:
                return (
                 False, {})

            return

    def get_children(self):
        """Return the Artists contained by the table"""
        return self._cells.values()

    get_child_artists = get_children

    def get_window_extent(self, renderer):
        """Return the bounding box of the table in window coords"""
        boxes = [ cell.get_window_extent(renderer) for cell in self._cells.values()
                ]
        return Bbox.union(boxes)

    def _do_cell_alignment(self):
        """ Calculate row heights and column widths.

        Position cells accordingly.
        """
        widths = {}
        heights = {}
        for (row, col), cell in self._cells.iteritems():
            height = heights.setdefault(row, 0.0)
            heights[row] = max(height, cell.get_height())
            width = widths.setdefault(col, 0.0)
            widths[col] = max(width, cell.get_width())

        xpos = 0
        lefts = {}
        cols = widths.keys()
        cols.sort()
        for col in cols:
            lefts[col] = xpos
            xpos += widths[col]

        ypos = 0
        bottoms = {}
        rows = heights.keys()
        rows.sort()
        rows.reverse()
        for row in rows:
            bottoms[row] = ypos
            ypos += heights[row]

        for (row, col), cell in self._cells.iteritems():
            cell.set_x(lefts[col])
            cell.set_y(bottoms[row])

    def auto_set_column_width(self, col):
        self._autoColumns.append(col)

    def _auto_set_column_width(self, col, renderer):
        """ Automagically set width for column.
        """
        cells = [ key for key in self._cells if key[1] == col ]
        width = 0
        for cell in cells:
            c = self._cells[cell]
            width = max(c.get_required_width(renderer), width)

        for cell in cells:
            self._cells[cell].set_width(width)

    def auto_set_font_size(self, value=True):
        """ Automatically set font size. """
        self._autoFontsize = value

    def _auto_set_font_size(self, renderer):
        if len(self._cells) == 0:
            return
        fontsize = self._cells.values()[0].get_fontsize()
        cells = []
        for key, cell in self._cells.iteritems():
            if key[1] in self._autoColumns:
                continue
            size = cell.auto_set_font_size(renderer)
            fontsize = min(fontsize, size)
            cells.append(cell)

        for cell in self._cells.itervalues():
            cell.set_fontsize(fontsize)

    def scale(self, xscale, yscale):
        """ Scale column widths by xscale and row heights by yscale. """
        for c in self._cells.itervalues():
            c.set_width(c.get_width() * xscale)
            c.set_height(c.get_height() * yscale)

    def set_fontsize(self, size):
        """
        Set the fontsize of the cell text

        ACCEPTS: a float in points
        """
        for cell in self._cells.itervalues():
            cell.set_fontsize(size)

    def _offset(self, ox, oy):
        """Move all the artists by ox,oy (axes coords)"""
        for c in self._cells.itervalues():
            x, y = c.get_x(), c.get_y()
            c.set_x(x + ox)
            c.set_y(y + oy)

    def _update_positions(self, renderer):
        for col in self._autoColumns:
            self._auto_set_column_width(col, renderer)

        if self._autoFontsize:
            self._auto_set_font_size(renderer)
        self._do_cell_alignment()
        bbox = self._get_grid_bbox(renderer)
        l, b, w, h = bbox.bounds
        if self._bbox is not None:
            rl, rb, rw, rh = self._bbox
            self.scale(rw / w, rh / h)
            ox = rl - l
            oy = rb - b
            self._do_cell_alignment()
        else:
            BEST, UR, UL, LL, LR, CL, CR, LC, UC, C, TR, TL, BL, BR, R, L, T, B = range(len(self.codes))
            ox = 0.5 - w / 2 - l
            oy = 0.5 - h / 2 - b
            if self._loc in (UL, LL, CL):
                ox = self.AXESPAD - l
            if self._loc in (BEST, UR, LR, R, CR):
                ox = 1 - (l + w + self.AXESPAD)
            if self._loc in (BEST, UR, UL, UC):
                oy = 1 - (b + h + self.AXESPAD)
            if self._loc in (LL, LR, LC):
                oy = self.AXESPAD - b
            if self._loc in (LC, UC, C):
                ox = 0.5 - w / 2 - l
            if self._loc in (CL, CR, C):
                oy = 0.5 - h / 2 - b
            if self._loc in (TL, BL, L):
                ox = -(l + w)
            if self._loc in (TR, BR, R):
                ox = 1.0 - l
            if self._loc in (TR, TL, T):
                oy = 1.0 - b
            if self._loc in (BL, BR, B):
                oy = -(b + h)
        self._offset(ox, oy)
        return

    def get_celld(self):
        """return a dict of cells in the table"""
        return self._cells


def table(ax, cellText=None, cellColours=None, cellLoc='right', colWidths=None, rowLabels=None, rowColours=None, rowLoc='left', colLabels=None, colColours=None, colLoc='center', loc='bottom', bbox=None):
    """
    TABLE(cellText=None, cellColours=None,
          cellLoc='right', colWidths=None,
          rowLabels=None, rowColours=None, rowLoc='left',
          colLabels=None, colColours=None, colLoc='center',
          loc='bottom', bbox=None)

    Factory function to generate a Table instance.

    Thanks to John Gill for providing the class and table.
    """
    if cellText is None:
        rows = len(cellColours)
        cols = len(cellColours[0])
        cellText = [[''] * rows] * cols
    rows = len(cellText)
    cols = len(cellText[0])
    for row in cellText:
        assert len(row) == cols

    if cellColours is not None:
        if not len(cellColours) == rows:
            raise AssertionError
            for row in cellColours:
                assert len(row) == cols

        else:
            cellColours = [
             'w' * cols] * rows
        if colWidths is None:
            colWidths = [
             1.0 / cols] * cols
        rowLabelWidth = 0
        if rowLabels is None:
            if rowColours is not None:
                rowLabels = [
                 ''] * cols
                rowLabelWidth = colWidths[0]
        elif rowColours is None:
            rowColours = 'w' * rows
        assert rowLabels is not None and len(rowLabels) == rows
    offset = 0
    if colLabels is None:
        if colColours is not None:
            colLabels = [
             ''] * rows
            offset = 1
    else:
        if colColours is None:
            colColours = 'w' * cols
            offset = 1
        assert rowLabels is not None and len(rowLabels) == rows
        if cellColours is None:
            cellColours = [
             'w' * cols] * rows
        table = Table(ax, loc, bbox)
        height = table._approx_text_height()
        for row in xrange(rows):
            for col in xrange(cols):
                table.add_cell(row + offset, col, width=colWidths[col], height=height, text=cellText[row][col], facecolor=cellColours[row][col], loc=cellLoc)

    if colLabels is not None:
        for col in xrange(cols):
            table.add_cell(0, col, width=colWidths[col], height=height, text=colLabels[col], facecolor=colColours[col], loc=colLoc)

    if rowLabels is not None:
        for row in xrange(rows):
            table.add_cell(row + offset, -1, width=rowLabelWidth or 1e-15, height=height, text=rowLabels[row], facecolor=rowColours[row], loc=rowLoc)

        if rowLabelWidth == 0:
            table.auto_set_column_width(-1)
    ax.add_table(table)
    return table


docstring.interpd.update(Table=artist.kwdoc(Table))