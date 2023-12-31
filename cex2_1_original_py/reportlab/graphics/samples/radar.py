# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\samples\radar.pyc
# Compiled at: 2013-03-27 15:37:42
from reportlab.graphics.charts.legends import Legend
from excelcolors import *
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.graphics.charts.textlabels import Label

class RadarChart(_DrawingEditorMixin, Drawing):

    def __init__(self, width=200, height=150, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self._add(self, SpiderChart(), name='chart', validate=None, desc='The main chart')
        self.chart.width = 90
        self.chart.height = 90
        self.chart.x = 45
        self.chart.y = 25
        self.chart.strands[0].strokeColor = color01
        self.chart.strands[1].strokeColor = color02
        self.chart.strands[2].strokeColor = color03
        self.chart.strands[3].strokeColor = color04
        self.chart.strands[4].strokeColor = color05
        self.chart.strands[5].strokeColor = color06
        self.chart.strands[6].strokeColor = color07
        self.chart.strands[7].strokeColor = color08
        self.chart.strands[8].strokeColor = color09
        self.chart.strands[9].strokeColor = color10
        self.chart.strands[0].fillColor = None
        self.chart.strands[1].fillColor = None
        self.chart.strands[2].fillColor = None
        self.chart.strands[3].fillColor = None
        self.chart.strands[4].fillColor = None
        self.chart.strands[5].fillColor = None
        self.chart.strands[6].fillColor = None
        self.chart.strands[7].fillColor = None
        self.chart.strands[8].fillColor = None
        self.chart.strands[9].fillColor = None
        self.chart.strands.strokeWidth = 1
        self.chart.strandLabels.fontName = 'Helvetica'
        self.chart.strandLabels.fontSize = 6
        self.chart.fillColor = backgroundGrey
        self.chart.data = [(125, 180, 200), (100, 150, 180)]
        self.chart.labels = ['North', 'South', 'Central']
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
        self.chart.strands.strokeWidth = 1
        self._add(self, 0, name='preview', validate=None, desc=None)
        return


if __name__ == '__main__':
    RadarChart().save(formats=['pdf'], outDir=None, fnRoot='radar')