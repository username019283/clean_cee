# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\charts\doughnut.pyc
# Compiled at: 2013-04-04 12:22:40
__version__ = ' $Id$ '
__doc__ = "Doughnut chart\n\nProduces a circular chart like the doughnut charts produced by Excel.\nCan handle multiple series (which produce concentric 'rings' in the chart).\n\n"
import copy
from math import sin, cos, pi
from types import ListType, TupleType
from reportlab.lib import colors
from reportlab.lib.validators import isColor, isNumber, isListOfNumbersOrNone, isListOfNumbers, isColorOrNone, isString, isListOfStringsOrNone, OneOf, SequenceOf, isBoolean, isListOfColors, isNoneOrListOfNoneOrStrings, isNoneOrListOfNoneOrNumbers, isNumberOrNone
from ..reportlab.lib.attrmap import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Group, Drawing, Line, Rect, Polygon, Ellipse, Wedge, String, SolidShape, UserNode, STATE_DEFAULTS
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.charts.piecharts import AbstractPieChart, WedgeProperties, _addWedgeLabel, fixLabelOverlaps
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.widgets.markers import Marker

class SectorProperties(WedgeProperties):
    """This holds descriptive information about the sectors in a doughnut chart.

    It is not to be confused with the 'sector itself'; this just holds
    a recipe for how to format one, and does not allow you to hack the
    angles.  It can format a genuine Sector object for you with its
    format method.
    """
    _attrMap = AttrMap(BASE=WedgeProperties)


class Doughnut(AbstractPieChart):
    _attrMap = AttrMap(x=AttrMapValue(isNumber, desc='X position of the chart within its container.'), y=AttrMapValue(isNumber, desc='Y position of the chart within its container.'), width=AttrMapValue(isNumber, desc='width of doughnut bounding box. Need not be same as width.'), height=AttrMapValue(isNumber, desc='height of doughnut bounding box.  Need not be same as height.'), data=AttrMapValue(None, desc='list of numbers defining sector sizes; need not sum to 1'), labels=AttrMapValue(isListOfStringsOrNone, desc='optional list of labels to use for each data point'), startAngle=AttrMapValue(isNumber, desc='angle of first slice; like the compass, 0 is due North'), direction=AttrMapValue(OneOf('clockwise', 'anticlockwise'), desc="'clockwise' or 'anticlockwise'"), slices=AttrMapValue(None, desc='collection of sector descriptor objects'), simpleLabels=AttrMapValue(isBoolean, desc='If true(default) use String not super duper WedgeLabel'), checkLabelOverlap=AttrMapValue(isBoolean, desc='If true check and attempt to fix\n standard label overlaps(default off)', advancedUsage=1), sideLabels=AttrMapValue(isBoolean, desc='If true attempt to make chart with labels along side and pointers', advancedUsage=1))

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1, 1]
        self.labels = None
        self.startAngle = 90
        self.direction = 'clockwise'
        self.simpleLabels = 1
        self.checkLabelOverlap = 0
        self.sideLabels = 0
        self.slices = TypedPropertyCollection(SectorProperties)
        self.slices[0].fillColor = colors.darkcyan
        self.slices[1].fillColor = colors.blueviolet
        self.slices[2].fillColor = colors.blue
        self.slices[3].fillColor = colors.cyan
        self.slices[4].fillColor = colors.pink
        self.slices[5].fillColor = colors.magenta
        self.slices[6].fillColor = colors.yellow
        return

    def demo(self):
        d = Drawing(200, 100)
        dn = Doughnut()
        dn.x = 50
        dn.y = 10
        dn.width = 100
        dn.height = 80
        dn.data = [10, 20, 30, 40, 50, 60]
        dn.labels = ['a', 'b', 'c', 'd', 'e', 'f']
        dn.slices.strokeWidth = 0.5
        dn.slices[3].popout = 10
        dn.slices[3].strokeWidth = 2
        dn.slices[3].strokeDashArray = [2, 2]
        dn.slices[3].labelRadius = 1.75
        dn.slices[3].fontColor = colors.red
        dn.slices[0].fillColor = colors.darkcyan
        dn.slices[1].fillColor = colors.blueviolet
        dn.slices[2].fillColor = colors.blue
        dn.slices[3].fillColor = colors.cyan
        dn.slices[4].fillColor = colors.aquamarine
        dn.slices[5].fillColor = colors.cadetblue
        dn.slices[6].fillColor = colors.lightcoral
        d.add(dn)
        return d

    def normalizeData(self, data=None):
        from operator import add
        sum = float(reduce(add, data, 0))
        return abs(sum) >= 1e-08 and map((lambda x, f=360.0 / sum: f * x), data) or len(data) * [0]

    def makeSectors(self):
        if type(self.data) in (ListType, TupleType) and type(self.data[0]) in (ListType, TupleType):
            normData = []
            n = []
            for l in self.data:
                t = self.normalizeData(l)
                normData.append(t)
                n.append(len(t))

            self._seriesCount = max(n)
        else:
            normData = self.normalizeData(self.data)
            n = len(normData)
            self._seriesCount = n
        checkLabelOverlap = self.checkLabelOverlap
        L = []
        L_add = L.append
        if self.labels is None:
            labels = []
            if type(n) not in (ListType, TupleType):
                labels = [
                 ''] * n
            else:
                for m in n:
                    labels = list(labels) + [''] * m

        else:
            labels = self.labels
            if type(n) not in (ListType, TupleType):
                i = n - len(labels)
                if i > 0:
                    labels = list(labels) + [''] * i
            else:
                tlab = 0
                for m in n:
                    tlab += m

            i = tlab - len(labels)
            if i > 0:
                labels = list(labels) + [''] * i
            xradius = self.width / 2.0
            yradius = self.height / 2.0
            centerx = self.x + xradius
            centery = self.y + yradius
            if self.direction == 'anticlockwise':
                whichWay = 1
            else:
                whichWay = -1
            g = Group()
            startAngle = self.startAngle
            styleCount = len(self.slices)
            if type(self.data[0]) in (ListType, TupleType):
                iradius = self.height / 5.0 / len(self.data)
                for sn, series in enumerate(normData):
                    for i, angle in enumerate(series):
                        endAngle = startAngle + angle * whichWay
                        if abs(startAngle - endAngle) < 1e-05:
                            startAngle = endAngle
                            continue
                        if startAngle < endAngle:
                            a1 = startAngle
                            a2 = endAngle
                        else:
                            a1 = endAngle
                            a2 = startAngle
                        startAngle = endAngle
                        sectorStyle = self.slices[i % styleCount]
                        cx, cy = centerx, centery
                        if sectorStyle.popout != 0:
                            averageAngle = (a1 + a2) / 2.0
                            aveAngleRadians = averageAngle * pi / 180.0
                            popdistance = sectorStyle.popout
                            cx = centerx + popdistance * cos(aveAngleRadians)
                            cy = centery + popdistance * sin(aveAngleRadians)
                        if type(n) in (ListType, TupleType):
                            theSector = Wedge(cx, cy, xradius + sn * iradius - iradius, a1, a2, yradius=yradius + sn * iradius - iradius, radius1=yradius + sn * iradius - 2 * iradius)
                        else:
                            theSector = Wedge(cx, cy, xradius, a1, a2, yradius=yradius, radius1=iradius)
                        theSector.fillColor = sectorStyle.fillColor
                        theSector.strokeColor = sectorStyle.strokeColor
                        theSector.strokeWidth = sectorStyle.strokeWidth
                        theSector.strokeDashArray = sectorStyle.strokeDashArray
                        g.add(theSector)
                        if sn == 0:
                            text = self.getSeriesName(i, '')
                            if text:
                                averageAngle = (a1 + a2) / 2.0
                                aveAngleRadians = averageAngle * pi / 180.0
                                labelRadius = sectorStyle.labelRadius
                                rx = xradius * labelRadius
                                ry = yradius * labelRadius
                                labelX = centerx + 0.5 * self.width * cos(aveAngleRadians) * labelRadius
                                labelY = centery + 0.5 * self.height * sin(aveAngleRadians) * labelRadius
                                l = _addWedgeLabel(self, text, averageAngle, labelX, labelY, sectorStyle)
                                if checkLabelOverlap:
                                    l._origdata = {'x': labelX, 'y': labelY, 'angle': averageAngle, 'rx': rx, 'ry': ry, 'cx': cx, 'cy': cy, 'bounds': l.getBounds()}
                                L_add(l)

            else:
                iradius = self.height / 5.0
                for i, angle in enumerate(normData):
                    endAngle = startAngle + angle * whichWay
                    if abs(startAngle - endAngle) < 1e-05:
                        startAngle = endAngle
                        continue
                    if startAngle < endAngle:
                        a1 = startAngle
                        a2 = endAngle
                    else:
                        a1 = endAngle
                        a2 = startAngle
                    startAngle = endAngle
                    sectorStyle = self.slices[i % styleCount]
                    cx, cy = centerx, centery
                    if sectorStyle.popout != 0:
                        averageAngle = (a1 + a2) / 2.0
                        aveAngleRadians = averageAngle * pi / 180.0
                        popdistance = sectorStyle.popout
                        cx = centerx + popdistance * cos(aveAngleRadians)
                        cy = centery + popdistance * sin(aveAngleRadians)
                    if n > 1:
                        theSector = Wedge(cx, cy, xradius, a1, a2, yradius=yradius, radius1=iradius)
                    elif n == 1:
                        theSector = Wedge(cx, cy, xradius, a1, a2, yradius=yradius, iradius=iradius)
                    theSector.fillColor = sectorStyle.fillColor
                    theSector.strokeColor = sectorStyle.strokeColor
                    theSector.strokeWidth = sectorStyle.strokeWidth
                    theSector.strokeDashArray = sectorStyle.strokeDashArray
                    g.add(theSector)
                    if labels[i] != '':
                        averageAngle = (a1 + a2) / 2.0
                        aveAngleRadians = averageAngle * pi / 180.0
                        labelRadius = sectorStyle.labelRadius
                        labelX = centerx + 0.5 * self.width * cos(aveAngleRadians) * labelRadius
                        labelY = centery + 0.5 * self.height * sin(aveAngleRadians) * labelRadius
                        rx = xradius * labelRadius
                        ry = yradius * labelRadius
                        l = _addWedgeLabel(self, labels[i], averageAngle, labelX, labelY, sectorStyle)
                        if checkLabelOverlap:
                            l._origdata = {'x': labelX, 'y': labelY, 'angle': averageAngle, 'rx': rx, 'ry': ry, 'cx': cx, 'cy': cy, 'bounds': l.getBounds()}
                        L_add(l)

            if checkLabelOverlap and L:
                fixLabelOverlaps(L)
            for l in L:
                g.add(l)

        return g

    def draw(self):
        g = Group()
        g.add(self.makeSectors())
        return g


def sample1():
    """Make up something from the individual Sectors"""
    d = Drawing(400, 400)
    g = Group()
    s1 = Wedge(centerx=200, centery=200, radius=150, startangledegrees=0, endangledegrees=120, radius1=100)
    s1.fillColor = colors.red
    s1.strokeColor = None
    d.add(s1)
    s2 = Wedge(centerx=200, centery=200, radius=150, startangledegrees=120, endangledegrees=240, radius1=100)
    s2.fillColor = colors.green
    s2.strokeColor = None
    d.add(s2)
    s3 = Wedge(centerx=200, centery=200, radius=150, startangledegrees=240, endangledegrees=260, radius1=100)
    s3.fillColor = colors.blue
    s3.strokeColor = None
    d.add(s3)
    s4 = Wedge(centerx=200, centery=200, radius=150, startangledegrees=260, endangledegrees=360, radius1=100)
    s4.fillColor = colors.gray
    s4.strokeColor = None
    d.add(s4)
    return d


def sample2():
    """Make a simple demo"""
    d = Drawing(400, 400)
    dn = Doughnut()
    dn.x = 50
    dn.y = 50
    dn.width = 300
    dn.height = 300
    dn.data = [10, 20, 30, 40, 50, 60]
    d.add(dn)
    return d


def sample3():
    """Make a more complex demo"""
    d = Drawing(400, 400)
    dn = Doughnut()
    dn.x = 50
    dn.y = 50
    dn.width = 300
    dn.height = 300
    dn.data = [[10, 20, 30, 40, 50, 60], [10, 20, 30, 40]]
    dn.labels = ['a', 'b', 'c', 'd', 'e', 'f']
    d.add(dn)
    return d


def sample4():
    """Make a more complex demo with Label Overlap fixing"""
    d = Drawing(400, 400)
    dn = Doughnut()
    dn.x = 50
    dn.y = 50
    dn.width = 300
    dn.height = 300
    dn.data = [[10, 20, 30, 40, 50, 60], [10, 20, 30, 40]]
    dn.labels = ['a', 'b', 'c', 'd', 'e', 'f']
    dn.checkLabelOverlap = True
    d.add(dn)
    return d


if __name__ == '__main__':
    from reportlab.graphics.renderPDF import drawToFile
    d = sample1()
    drawToFile(d, 'doughnut1.pdf')
    d = sample2()
    drawToFile(d, 'doughnut2.pdf')
    d = sample3()
    drawToFile(d, 'doughnut3.pdf')