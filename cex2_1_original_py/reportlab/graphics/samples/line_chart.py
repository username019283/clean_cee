# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\samples\line_chart.pyc
# Compiled at: 2013-03-27 15:37:42
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.graphics.charts.textlabels import Label
from excelcolors import *

class LineChart(_DrawingEditorMixin, Drawing):

    def __init__(self, width=200, height=150, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self._add(self, LinePlot(), name='chart', validate=None, desc='The main chart')
        self.chart.width = 115
        self.chart.height = 80
        self.chart.x = 30
        self.chart.y = 40
        self.chart.lines[0].strokeColor = color01
        self.chart.lines[1].strokeColor = color02
        self.chart.lines[2].strokeColor = color03
        self.chart.lines[3].strokeColor = color04
        self.chart.lines[4].strokeColor = color05
        self.chart.lines[5].strokeColor = color06
        self.chart.lines[6].strokeColor = color07
        self.chart.lines[7].strokeColor = color08
        self.chart.lines[8].strokeColor = color09
        self.chart.lines[9].strokeColor = color10
        self.chart.fillColor = backgroundGrey
        self.chart.lineLabels.fontName = 'Helvetica'
        self.chart.xValueAxis.labels.fontName = 'Helvetica'
        self.chart.xValueAxis.labels.fontSize = 7
        self.chart.xValueAxis.forceZero = 0
        self.chart.data = [((0, 50), (100, 100), (200, 200), (250, 210), (300, 300), (400, 500)), ((0, 150), (100, 200), (200, 300), (250, 200), (300, 400), (400, 600))]
        self.chart.xValueAxis.avoidBoundFrac = 1
        self.chart.xValueAxis.gridEnd = 115
        self.chart.xValueAxis.tickDown = 3
        self.chart.xValueAxis.visibleGrid = 1
        self.chart.yValueAxis.tickLeft = 3
        self.chart.yValueAxis.labels.fontName = 'Helvetica'
        self.chart.yValueAxis.labels.fontSize = 7
        self._add(self, Label(), name='Title', validate=None, desc='The title at the top of the chart')
        self.Title.fontName = 'Helvetica-Bold'
        self.Title.fontSize = 7
        self.Title.x = 100
        self.Title.y = 135
        self.Title._text = 'Chart Title'
        self.Title.maxWidth = 180
        self.Title.height = 20
        self.Title.textAnchor = 'middle'
        self._add(self, Legend(), name='Legend', validate=None, desc='The legend or key for the chart')
        self.Legend.colorNamePairs = [(color01, 'Widgets'), (color02, 'Sprockets')]
        self.Legend.fontName = 'Helvetica'
        self.Legend.fontSize = 7
        self.Legend.x = 153
        self.Legend.y = 85
        self.Legend.dxTextSpace = 5
        self.Legend.dy = 5
        self.Legend.dx = 5
        self.Legend.deltay = 5
        self.Legend.alignment = 'right'
        self._add(self, Label(), name='XLabel', validate=None, desc='The label on the horizontal axis')
        self.XLabel.fontName = 'Helvetica'
        self.XLabel.fontSize = 7
        self.XLabel.x = 85
        self.XLabel.y = 10
        self.XLabel.textAnchor = 'middle'
        self.XLabel.maxWidth = 100
        self.XLabel.height = 20
        self.XLabel._text = 'X Axis'
        self._add(self, Label(), name='YLabel', validate=None, desc='The label on the vertical axis')
        self.YLabel.fontName = 'Helvetica'
        self.YLabel.fontSize = 7
        self.YLabel.x = 12
        self.YLabel.y = 80
        self.YLabel.angle = 90
        self.YLabel.textAnchor = 'middle'
        self.YLabel.maxWidth = 100
        self.YLabel.height = 20
        self.YLabel._text = 'Y Axis'
        self.chart.yValueAxis.forceZero = 1
        self.chart.xValueAxis.forceZero = 1
        self._add(self, 0, name='preview', validate=None, desc=None)
        return


if __name__ == '__main__':
    LineChart().save(formats=['pdf'], outDir=None, fnRoot='line_chart')