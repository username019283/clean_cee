# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\backends\backend_ps.pyc
# Compiled at: 2012-10-30 18:11:14
"""
A PostScript backend, which can produce both PostScript .ps and .eps
"""
from __future__ import division, print_function
import glob, math, os, shutil, sys, time

def _fn_name():
    return sys._getframe(1).f_code.co_name


import io
if sys.version_info[0] < 3:
    import cStringIO
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from tempfile import mkstemp
from matplotlib import verbose, __version__, rcParams
from matplotlib._pylab_helpers import Gcf
from matplotlib.afm import AFM
from matplotlib.backend_bases import RendererBase, GraphicsContextBase, FigureManagerBase, FigureCanvasBase
from matplotlib.cbook import is_string_like, get_realpath_and_stat, is_writable_file_like, maxdict
from matplotlib.mlab import quad2cubic
from matplotlib.figure import Figure
from matplotlib.font_manager import findfont, is_opentype_cff_font
from matplotlib.ft2font import FT2Font, KERNING_DEFAULT, LOAD_NO_HINTING
from matplotlib.ttconv import convert_ttf_to_ps
from matplotlib.mathtext import MathTextParser
from matplotlib._mathtext_data import uni2type1
from matplotlib.text import Text
from matplotlib.path import Path
from matplotlib.transforms import Affine2D
from matplotlib.backends.backend_mixed import MixedModeRenderer
import numpy as np, binascii, re
try:
    set
except NameError:
    from sets import Set as set

if sys.platform.startswith('win'):
    cmd_split = '&'
else:
    cmd_split = ';'
backend_version = 'Level II'
debugPS = 0

class PsBackendHelper(object):

    def __init__(self):
        self._cached = {}

    @property
    def gs_exe(self):
        """
        excutable name of ghostscript.
        """
        try:
            return self._cached['gs_exe']
        except KeyError:
            pass

        if sys.platform == 'win32':
            gs_exe = 'gswin32c'
        else:
            gs_exe = 'gs'
        self._cached['gs_exe'] = gs_exe
        return gs_exe

    @property
    def gs_version(self):
        """
        version of ghostscript.
        """
        try:
            return self._cached['gs_version']
        except KeyError:
            pass

        from subprocess import Popen, PIPE
        pipe = Popen(self.gs_exe + ' --version', shell=True, stdout=PIPE).stdout
        if sys.version_info[0] >= 3:
            ver = pipe.read().decode('ascii')
        else:
            ver = pipe.read()
        gs_version = tuple(map(int, ver.strip().split('.')))
        self._cached['gs_version'] = gs_version
        return gs_version

    @property
    def supports_ps2write(self):
        """
        True if the installed ghostscript supports ps2write device.
        """
        return self.gs_version[0] >= 9


ps_backend_helper = PsBackendHelper()
papersize = {'letter': (8.5, 11), 'legal': (
           8.5, 14), 
   'ledger': (
            11, 17), 
   'a0': (
        33.11, 46.81), 
   'a1': (
        23.39, 33.11), 
   'a2': (
        16.54, 23.39), 
   'a3': (
        11.69, 16.54), 
   'a4': (
        8.27, 11.69), 
   'a5': (
        5.83, 8.27), 
   'a6': (
        4.13, 5.83), 
   'a7': (
        2.91, 4.13), 
   'a8': (
        2.07, 2.91), 
   'a9': (
        1.457, 2.05), 
   'a10': (
         1.02, 1.457), 
   'b0': (
        40.55, 57.32), 
   'b1': (
        28.66, 40.55), 
   'b2': (
        20.27, 28.66), 
   'b3': (
        14.33, 20.27), 
   'b4': (
        10.11, 14.33), 
   'b5': (
        7.16, 10.11), 
   'b6': (
        5.04, 7.16), 
   'b7': (
        3.58, 5.04), 
   'b8': (
        2.51, 3.58), 
   'b9': (
        1.76, 2.51), 
   'b10': (
         1.26, 1.76)}

def _get_papertype(w, h):
    keys = papersize.keys()
    keys.sort()
    keys.reverse()
    for key in keys:
        if key.startswith('l'):
            continue
        pw, ph = papersize[key]
        if w < pw and h < ph:
            return key
    else:
        return 'a0'


def _num_to_str(val):
    if is_string_like(val):
        return val
    ival = int(val)
    if val == ival:
        return str(ival)
    s = '%1.3f' % val
    s = s.rstrip('0')
    s = s.rstrip('.')
    return s


def _nums_to_str(*args):
    return (' ').join(map(_num_to_str, args))


def quote_ps_string(s):
    """Quote dangerous characters of S for use in a PostScript string constant."""
    s = s.replace('\\', '\\\\')
    s = s.replace('(', '\\(')
    s = s.replace(')', '\\)')
    s = s.replace("'", '\\251')
    s = s.replace('`', '\\301')
    s = re.sub('[^ -~\\n]', (lambda x: '\\%03o' % ord(x.group())), s)
    return s


def seq_allequal(seq1, seq2):
    """
    seq1 and seq2 are either None or sequences or arrays
    Return True if both are None or both are seqs with identical
    elements
    """
    if seq1 is None:
        return seq2 is None
    else:
        if seq2 is None:
            return False
        if len(seq1) != len(seq2):
            return False
        return np.alltrue(np.equal(seq1, seq2))


class RendererPS(RendererBase):
    """
    The renderer handles all the drawing primitives using a graphics
    context instance that controls the colors/styles.
    """
    fontd = maxdict(50)
    afmfontd = maxdict(50)

    def __init__(self, width, height, pswriter, imagedpi=72):
        """
        Although postscript itself is dpi independent, we need to
        imform the image code about a requested dpi to generate high
        res images and them scale them before embeddin them
        """
        RendererBase.__init__(self)
        self.width = width
        self.height = height
        self._pswriter = pswriter
        if rcParams['text.usetex']:
            self.textcnt = 0
            self.psfrag = []
        self.imagedpi = imagedpi
        self.color = None
        self.linewidth = None
        self.linejoin = None
        self.linecap = None
        self.linedash = None
        self.fontname = None
        self.fontsize = None
        self._hatches = {}
        self.image_magnification = imagedpi / 72.0
        self._clip_paths = {}
        self._path_collection_id = 0
        self.used_characters = {}
        self.mathtext_parser = MathTextParser('PS')
        self._afm_font_dir = os.path.join(rcParams['datapath'], 'fonts', 'afm')
        return

    def track_characters(self, font, s):
        """Keeps track of which characters are required from
        each font."""
        realpath, stat_key = get_realpath_and_stat(font.fname)
        used_characters = self.used_characters.setdefault(stat_key, (realpath, set()))
        used_characters[1].update([ ord(x) for x in s ])

    def merge_used_characters(self, other):
        for stat_key, (realpath, charset) in other.iteritems():
            used_characters = self.used_characters.setdefault(stat_key, (realpath, set()))
            used_characters[1].update(charset)

    def set_color(self, r, g, b, store=1):
        if (r, g, b) != self.color:
            if r == g and r == b:
                self._pswriter.write('%1.3f setgray\n' % r)
            else:
                self._pswriter.write('%1.3f %1.3f %1.3f setrgbcolor\n' % (r, g, b))
            if store:
                self.color = (r, g, b)

    def set_linewidth(self, linewidth, store=1):
        if linewidth != self.linewidth:
            self._pswriter.write('%1.3f setlinewidth\n' % linewidth)
            if store:
                self.linewidth = linewidth

    def set_linejoin(self, linejoin, store=1):
        if linejoin != self.linejoin:
            self._pswriter.write('%d setlinejoin\n' % linejoin)
            if store:
                self.linejoin = linejoin

    def set_linecap(self, linecap, store=1):
        if linecap != self.linecap:
            self._pswriter.write('%d setlinecap\n' % linecap)
            if store:
                self.linecap = linecap

    def set_linedash(self, offset, seq, store=1):
        if self.linedash is not None:
            oldo, oldseq = self.linedash
            if seq_allequal(seq, oldseq):
                return
        if seq is not None and len(seq):
            s = '[%s] %d setdash\n' % (_nums_to_str(*seq), offset)
            self._pswriter.write(s)
        else:
            self._pswriter.write('[] 0 setdash\n')
        if store:
            self.linedash = (offset, seq)
        return

    def set_font(self, fontname, fontsize, store=1):
        if rcParams['ps.useafm']:
            return
        if (
         fontname, fontsize) != (self.fontname, self.fontsize):
            out = '/%s findfont\n%1.3f scalefont\nsetfont\n' % (
             fontname, fontsize)
            self._pswriter.write(out)
            if store:
                self.fontname = fontname
            if store:
                self.fontsize = fontsize

    def create_hatch(self, hatch):
        sidelen = 72
        if hatch in self._hatches:
            return self._hatches[hatch]
        name = 'H%d' % len(self._hatches)
        self._pswriter.write('  << /PatternType 1\n     /PaintType 2\n     /TilingType 2\n     /BBox[0 0 %(sidelen)d %(sidelen)d]\n     /XStep %(sidelen)d\n     /YStep %(sidelen)d\n\n     /PaintProc {\n        pop\n        0 setlinewidth\n' % locals())
        self._pswriter.write(self._convert_path(Path.hatch(hatch), Affine2D().scale(72.0), simplify=False))
        self._pswriter.write('          stroke\n     } bind\n   >>\n   matrix\n   makepattern\n   /%(name)s exch def\n' % locals())
        self._hatches[hatch] = name
        return name

    def get_canvas_width_height(self):
        """return the canvas width and height in display coords"""
        return (
         self.width, self.height)

    def get_text_width_height_descent(self, s, prop, ismath):
        """
        get the width and height in display coords of the string s
        with FontPropertry prop

        """
        if rcParams['text.usetex']:
            texmanager = self.get_texmanager()
            fontsize = prop.get_size_in_points()
            w, h, d = texmanager.get_text_width_height_descent(s, fontsize, renderer=self)
            return (
             w, h, d)
        if ismath:
            width, height, descent, pswriter, used_characters = self.mathtext_parser.parse(s, 72, prop)
            return (
             width, height, descent)
        if rcParams['ps.useafm']:
            if ismath:
                s = s[1:-1]
            font = self._get_font_afm(prop)
            l, b, w, h, d = font.get_str_bbox_and_descent(s)
            fontsize = prop.get_size_in_points()
            scale = 0.001 * fontsize
            w *= scale
            h *= scale
            d *= scale
            return (
             w, h, d)
        font = self._get_font_ttf(prop)
        font.set_text(s, 0.0, flags=LOAD_NO_HINTING)
        w, h = font.get_width_height()
        w /= 64.0
        h /= 64.0
        d = font.get_descent()
        d /= 64.0
        return (
         w, h, d)

    def flipy(self):
        """return true if small y numbers are top for renderer"""
        return False

    def _get_font_afm(self, prop):
        key = hash(prop)
        font = self.afmfontd.get(key)
        if font is None:
            fname = findfont(prop, fontext='afm', directory=self._afm_font_dir)
            if fname is None:
                fname = findfont('Helvetica', fontext='afm', directory=self._afm_font_dir)
            font = self.afmfontd.get(fname)
            if font is None:
                with open(fname, 'rb') as (fh):
                    font = AFM(fh)
                self.afmfontd[fname] = font
            self.afmfontd[key] = font
        return font

    def _get_font_ttf(self, prop):
        key = hash(prop)
        font = self.fontd.get(key)
        if font is None:
            fname = findfont(prop)
            font = self.fontd.get(fname)
            if font is None:
                font = FT2Font(str(fname))
                self.fontd[fname] = font
            self.fontd[key] = font
        font.clear()
        size = prop.get_size_in_points()
        font.set_size(size, 72.0)
        return font

    def _rgba(self, im):
        return im.as_rgba_str()

    def _rgb(self, im):
        h, w, s = im.as_rgba_str()
        rgba = np.fromstring(s, np.uint8)
        rgba.shape = (h, w, 4)
        rgb = rgba[:, :, :3]
        return (h, w, rgb.tostring())

    def _gray(self, im, rc=0.3, gc=0.59, bc=0.11):
        rgbat = im.as_rgba_str()
        rgba = np.fromstring(rgbat[2], np.uint8)
        rgba.shape = (rgbat[0], rgbat[1], 4)
        rgba_f = rgba.astype(np.float32)
        r = rgba_f[:, :, 0]
        g = rgba_f[:, :, 1]
        b = rgba_f[:, :, 2]
        gray = (r * rc + g * gc + b * bc).astype(np.uint8)
        return (rgbat[0], rgbat[1], gray.tostring())

    def _hex_lines(self, s, chars_per_line=128):
        s = binascii.b2a_hex(s)
        nhex = len(s)
        lines = []
        for i in range(0, nhex, chars_per_line):
            limit = min(i + chars_per_line, nhex)
            lines.append(s[i:limit])

        return lines

    def get_image_magnification(self):
        """
        Get the factor by which to magnify images passed to draw_image.
        Allows a backend to have images at a different resolution to other
        artists.
        """
        return self.image_magnification

    def option_scale_image(self):
        """
        ps backend support arbitrary scaling of image.
        """
        return True

    def _get_image_h_w_bits_command(self, im):
        if im.is_grayscale:
            h, w, bits = self._gray(im)
            imagecmd = 'image'
        else:
            h, w, bits = self._rgb(im)
            imagecmd = 'false 3 colorimage'
        return (h, w, bits, imagecmd)

    def draw_image(self, gc, x, y, im, dx=None, dy=None, transform=None):
        """
        Draw the Image instance into the current axes; x is the
        distance in pixels from the left hand side of the canvas and y
        is the distance from bottom

        dx, dy is the width and height of the image.  If a transform
        (which must be an affine transform) is given, x, y, dx, dy are
        interpreted as the coordinate of the transform.
        """
        im.flipud_out()
        h, w, bits, imagecmd = self._get_image_h_w_bits_command(im)
        hexlines = ('\n').join(self._hex_lines(bits))
        if dx is None:
            xscale = w / self.image_magnification
        else:
            xscale = dx
        if dy is None:
            yscale = h / self.image_magnification
        else:
            yscale = dy
        if transform is None:
            matrix = '1 0 0 1 0 0'
        else:
            matrix = (' ').join(map(str, transform.to_values()))
        figh = self.height * 72
        bbox = gc.get_clip_rectangle()
        clippath, clippath_trans = gc.get_clip_path()
        clip = []
        if bbox is not None:
            clipx, clipy, clipw, cliph = bbox.bounds
            clip.append('%s clipbox' % _nums_to_str(clipw, cliph, clipx, clipy))
        if clippath is not None:
            id = self._get_clip_path(clippath, clippath_trans)
            clip.append('%s' % id)
        clip = ('\n').join(clip)
        ps = 'gsave\n%(clip)s\n[%(matrix)s] concat\n%(x)s %(y)s translate\n%(xscale)s %(yscale)s scale\n/DataString %(w)s string def\n%(w)s %(h)s 8 [ %(w)s 0 0 -%(h)s 0 %(h)s ]\n{\ncurrentfile DataString readhexstring pop\n} bind %(imagecmd)s\n%(hexlines)s\ngrestore\n' % locals()
        self._pswriter.write(ps)
        im.flipud_out()
        return

    def _convert_path(self, path, transform, clip=False, simplify=None):
        ps = []
        last_points = None
        if clip:
            clip = (
             0.0, 0.0, self.width * 72.0,
             self.height * 72.0)
        else:
            clip = None
        for points, code in path.iter_segments(transform, clip=clip, simplify=simplify):
            if code == Path.MOVETO:
                ps.append('%g %g m' % tuple(points))
            elif code == Path.CLOSEPOLY:
                ps.append('cl')
            elif last_points is None:
                raise ValueError('Path lacks initial MOVETO')
            elif code == Path.LINETO:
                ps.append('%g %g l' % tuple(points))
            elif code == Path.CURVE3:
                points = quad2cubic(*(list(last_points[-2:]) + list(points)))
                ps.append('%g %g %g %g %g %g c' % tuple(points[2:]))
            elif code == Path.CURVE4:
                ps.append('%g %g %g %g %g %g c' % tuple(points))
            last_points = points

        ps = ('\n').join(ps)
        return ps

    def _get_clip_path(self, clippath, clippath_transform):
        id = self._clip_paths.get((clippath, clippath_transform))
        if id is None:
            id = 'c%x' % len(self._clip_paths)
            ps_cmd = ['/%s {' % id]
            ps_cmd.append(self._convert_path(clippath, clippath_transform, simplify=False))
            ps_cmd.extend(['clip', 'newpath', '} bind def\n'])
            self._pswriter.write(('\n').join(ps_cmd))
            self._clip_paths[(clippath, clippath_transform)] = id
        return id

    def draw_path(self, gc, path, transform, rgbFace=None):
        """
        Draws a Path instance using the given affine transform.
        """
        clip = rgbFace is None and gc.get_hatch_path() is None
        simplify = path.should_simplify and clip
        ps = self._convert_path(path, transform, clip=clip, simplify=simplify)
        self._draw_ps(ps, gc, rgbFace)
        return

    def draw_markers(self, gc, marker_path, marker_trans, path, trans, rgbFace=None):
        """
        Draw the markers defined by path at each of the positions in x
        and y.  path coordinates are points, x and y coords will be
        transformed by the transform
        """
        if debugPS:
            self._pswriter.write('% draw_markers \n')
        write = self._pswriter.write
        if rgbFace:
            if rgbFace[0] == rgbFace[1] and rgbFace[0] == rgbFace[2]:
                ps_color = '%1.3f setgray' % rgbFace[0]
            else:
                ps_color = '%1.3f %1.3f %1.3f setrgbcolor' % rgbFace
        ps_cmd = ['/o {', 'gsave', 'newpath', 'translate']
        lw = gc.get_linewidth()
        stroke = lw != 0.0
        if stroke:
            ps_cmd.append('%.1f setlinewidth' % lw)
            jint = gc.get_joinstyle()
            ps_cmd.append('%d setlinejoin' % jint)
            cint = gc.get_capstyle()
            ps_cmd.append('%d setlinecap' % cint)
        ps_cmd.append(self._convert_path(marker_path, marker_trans, simplify=False))
        if rgbFace:
            if stroke:
                ps_cmd.append('gsave')
            ps_cmd.extend([ps_color, 'fill'])
            if stroke:
                ps_cmd.append('grestore')
        if stroke:
            ps_cmd.append('stroke')
        ps_cmd.extend(['grestore', '} bind def'])
        for vertices, code in path.iter_segments(trans, simplify=False):
            if len(vertices):
                x, y = vertices[-2:]
                ps_cmd.append('%g %g o' % (x, y))

        ps = ('\n').join(ps_cmd)
        self._draw_ps(ps, gc, rgbFace, fill=False, stroke=False)

    def draw_path_collection(self, gc, master_transform, paths, all_transforms, offsets, offsetTrans, facecolors, edgecolors, linewidths, linestyles, antialiaseds, urls, offset_position):
        write = self._pswriter.write
        path_codes = []
        for i, (path, transform) in enumerate(self._iter_collection_raw_paths(master_transform, paths, all_transforms)):
            name = 'p%x_%x' % (self._path_collection_id, i)
            ps_cmd = ['/%s {' % name,
             'newpath', 'translate']
            ps_cmd.append(self._convert_path(path, transform, simplify=False))
            ps_cmd.extend(['} bind def\n'])
            write(('\n').join(ps_cmd))
            path_codes.append(name)

        for xo, yo, path_id, gc0, rgbFace in self._iter_collection(gc, master_transform, all_transforms, path_codes, offsets, offsetTrans, facecolors, edgecolors, linewidths, linestyles, antialiaseds, urls, offset_position):
            ps = '%g %g %s' % (xo, yo, path_id)
            self._draw_ps(ps, gc0, rgbFace)

        self._path_collection_id += 1

    def draw_tex(self, gc, x, y, s, prop, angle, ismath='TeX!'):
        """
        draw a Text instance
        """
        w, h, bl = self.get_text_width_height_descent(s, prop, ismath)
        fontsize = prop.get_size_in_points()
        thetext = 'psmarker%d' % self.textcnt
        color = '%1.3f,%1.3f,%1.3f' % gc.get_rgb()[:3]
        fontcmd = {'sans-serif': '{\\sffamily %s}', 'monospace': '{\\ttfamily %s}'}.get(rcParams['font.family'], '{\\rmfamily %s}')
        s = fontcmd % s
        tex = '\\color[rgb]{%s} %s' % (color, s)
        corr = 0
        if rcParams['text.latex.preview']:
            pos = _nums_to_str(x - corr, y + bl)
            self.psfrag.append('\\psfrag{%s}[Bl][Bl][1][%f]{\\fontsize{%f}{%f}%s}' % (thetext, angle, fontsize, fontsize * 1.25, tex))
        else:
            pos = _nums_to_str(x - corr, y)
            self.psfrag.append('\\psfrag{%s}[bl][bl][1][%f]{\\fontsize{%f}{%f}%s}' % (thetext, angle, fontsize, fontsize * 1.25, tex))
        ps = 'gsave\n%(pos)s moveto\n(%(thetext)s)\nshow\ngrestore\n    ' % locals()
        self._pswriter.write(ps)
        self.textcnt += 1

    def draw_text(self, gc, x, y, s, prop, angle, ismath):
        """
        draw a Text instance
        """
        write = self._pswriter.write
        if debugPS:
            write('% text\n')
        if ismath == 'TeX':
            return self.tex(gc, x, y, s, prop, angle)
        else:
            if ismath:
                return self.draw_mathtext(gc, x, y, s, prop, angle)
            if rcParams['ps.useafm']:
                self.set_color(*gc.get_rgb())
                font = self._get_font_afm(prop)
                fontname = font.get_fontname()
                fontsize = prop.get_size_in_points()
                scale = 0.001 * fontsize
                thisx = 0
                thisy = font.get_str_bbox_and_descent(s)[4] * scale
                last_name = None
                lines = []
                for c in s:
                    name = uni2type1.get(ord(c), 'question')
                    try:
                        width = font.get_width_from_char_name(name)
                    except KeyError:
                        name = 'question'
                        width = font.get_width_char('?')

                    if last_name is not None:
                        kern = font.get_kern_dist_from_name(last_name, name)
                    else:
                        kern = 0
                    last_name = name
                    thisx += kern * scale
                    lines.append('%f %f m /%s glyphshow' % (thisx, thisy, name))
                    thisx += width * scale

                thetext = ('\n').join(lines)
                ps = 'gsave\n/%(fontname)s findfont\n%(fontsize)s scalefont\nsetfont\n%(x)f %(y)f translate\n%(angle)f rotate\n%(thetext)s\ngrestore\n    ' % locals()
                self._pswriter.write(ps)
            else:
                font = self._get_font_ttf(prop)
                font.set_text(s, 0, flags=LOAD_NO_HINTING)
                self.track_characters(font, s)
                self.set_color(*gc.get_rgb())
                self.set_font(font.get_sfnt()[(1, 0, 0, 6)], prop.get_size_in_points())
                cmap = font.get_charmap()
                lastgind = None
                lines = []
                thisx = 0
                thisy = font.get_descent() / 64.0
                for c in s:
                    ccode = ord(c)
                    gind = cmap.get(ccode)
                    if gind is None:
                        ccode = ord('?')
                        name = '.notdef'
                        gind = 0
                    else:
                        name = font.get_glyph_name(gind)
                    glyph = font.load_char(ccode, flags=LOAD_NO_HINTING)
                    if lastgind is not None:
                        kern = font.get_kerning(lastgind, gind, KERNING_DEFAULT)
                    else:
                        kern = 0
                    lastgind = gind
                    thisx += kern / 64.0
                    lines.append('%f %f m /%s glyphshow' % (thisx, thisy, name))
                    thisx += glyph.linearHoriAdvance / 65536.0

                thetext = ('\n').join(lines)
                ps = 'gsave\n%(x)f %(y)f translate\n%(angle)f rotate\n%(thetext)s\ngrestore\n' % locals()
                self._pswriter.write(ps)
            return

    def new_gc(self):
        return GraphicsContextPS()

    def draw_mathtext(self, gc, x, y, s, prop, angle):
        """
        Draw the math text using matplotlib.mathtext
        """
        if debugPS:
            self._pswriter.write('% mathtext\n')
        width, height, descent, pswriter, used_characters = self.mathtext_parser.parse(s, 72, prop)
        self.merge_used_characters(used_characters)
        self.set_color(*gc.get_rgb())
        thetext = pswriter.getvalue()
        ps = 'gsave\n%(x)f %(y)f translate\n%(angle)f rotate\n%(thetext)s\ngrestore\n' % locals()
        self._pswriter.write(ps)

    def draw_gouraud_triangle(self, gc, points, colors, trans):
        self.draw_gouraud_triangles(gc, points.reshape((1, 3, 2)), colors.reshape((1,
                                                                                   3,
                                                                                   4)), trans)

    def draw_gouraud_triangles(self, gc, points, colors, trans):
        assert len(points) == len(colors)
        assert points.ndim == 3
        assert points.shape[1] == 3
        assert points.shape[2] == 2
        assert colors.ndim == 3
        assert colors.shape[1] == 3
        assert colors.shape[2] == 4
        points = trans.transform(points)
        shape = points.shape
        flat_points = points.reshape((shape[0] * shape[1], 2))
        flat_colors = colors.reshape((shape[0] * shape[1], 4))
        points_min = np.min(flat_points, axis=0) - 256
        points_max = np.max(flat_points, axis=0) + 256
        factor = float(4294967295) / (points_max - points_min)
        xmin, ymin = points_min
        xmax, ymax = points_max
        streamarr = np.empty((
         shape[0] * shape[1],), dtype=[
         ('flags', 'u1'),
         (
          'points', '>u4', (2, )),
         (
          'colors', 'u1', (3, ))])
        streamarr['flags'] = 0
        streamarr['points'] = (flat_points - points_min) * factor
        streamarr['colors'] = flat_colors[:, :3] * 255.0
        stream = quote_ps_string(streamarr.tostring())
        self._pswriter.write('\ngsave\n<< /ShadingType 4\n   /ColorSpace [/DeviceRGB]\n   /BitsPerCoordinate 32\n   /BitsPerComponent 8\n   /BitsPerFlag 8\n   /AntiAlias true\n   /Decode [ %(xmin)f %(xmax)f %(ymin)f %(ymax)f 0 1 0 1 0 1 ]\n   /DataSource (%(stream)s)\n>>\nshfill\ngrestore\n' % locals())

    def _draw_ps(self, ps, gc, rgbFace, fill=True, stroke=True, command=None):
        """
        Emit the PostScript sniplet 'ps' with all the attributes from 'gc'
        applied.  'ps' must consist of PostScript commands to construct a path.

        The fill and/or stroke kwargs can be set to False if the
        'ps' string already includes filling and/or stroking, in
        which case _draw_ps is just supplying properties and
        clipping.
        """
        write = self._pswriter.write
        if debugPS and command:
            write('% ' + command + '\n')
        mightstroke = gc.shouldstroke()
        stroke = stroke and mightstroke
        fill = fill and rgbFace is not None and (len(rgbFace) <= 3 or rgbFace[3] != 0.0)
        if mightstroke:
            self.set_linewidth(gc.get_linewidth())
            jint = gc.get_joinstyle()
            self.set_linejoin(jint)
            cint = gc.get_capstyle()
            self.set_linecap(cint)
            self.set_linedash(*gc.get_dashes())
            self.set_color(*gc.get_rgb()[:3])
        write('gsave\n')
        cliprect = gc.get_clip_rectangle()
        if cliprect:
            x, y, w, h = cliprect.bounds
            write('%1.4g %1.4g %1.4g %1.4g clipbox\n' % (w, h, x, y))
        clippath, clippath_trans = gc.get_clip_path()
        if clippath:
            id = self._get_clip_path(clippath, clippath_trans)
            write('%s\n' % id)
        write(ps.strip())
        write('\n')
        if fill:
            if stroke:
                write('gsave\n')
            self.set_color(store=0, *rgbFace[:3])
            write('fill\n')
            if stroke:
                write('grestore\n')
        hatch = gc.get_hatch()
        if hatch:
            hatch_name = self.create_hatch(hatch)
            write('gsave\n')
            write('[/Pattern [/DeviceRGB]] setcolorspace %f %f %f ' % gc.get_rgb()[:3])
            write('%s setcolor fill grestore\n' % hatch_name)
        if stroke:
            write('stroke\n')
        write('grestore\n')
        return


class GraphicsContextPS(GraphicsContextBase):

    def get_capstyle(self):
        return {'butt': 0, 'round': 1, 
           'projecting': 2}[GraphicsContextBase.get_capstyle(self)]

    def get_joinstyle(self):
        return {'miter': 0, 'round': 1, 
           'bevel': 2}[GraphicsContextBase.get_joinstyle(self)]

    def shouldstroke(self):
        return self.get_linewidth() > 0.0 and (len(self.get_rgb()) <= 3 or self.get_rgb()[3] != 0.0)


def new_figure_manager(num, *args, **kwargs):
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasPS(figure)
    manager = FigureManagerPS(canvas, num)
    return manager


class FigureCanvasPS(FigureCanvasBase):
    _renderer_class = RendererPS

    def draw(self):
        pass

    filetypes = {'ps': 'Postscript', 'eps': 'Encapsulated Postscript'}

    def get_default_filetype(self):
        return 'ps'

    def print_ps(self, outfile, *args, **kwargs):
        return self._print_ps(outfile, 'ps', *args, **kwargs)

    def print_eps(self, outfile, *args, **kwargs):
        return self._print_ps(outfile, 'eps', *args, **kwargs)

    def _print_ps(self, outfile, format, *args, **kwargs):
        papertype = kwargs.pop('papertype', rcParams['ps.papersize'])
        papertype = papertype.lower()
        if papertype == 'auto':
            pass
        elif papertype not in papersize:
            raise RuntimeError('%s is not a valid papertype. Use one                     of %s' % (papertype, (', ').join(papersize.iterkeys())))
        orientation = kwargs.pop('orientation', 'portrait').lower()
        if orientation == 'landscape':
            isLandscape = True
        elif orientation == 'portrait':
            isLandscape = False
        else:
            raise RuntimeError('Orientation must be "portrait" or "landscape"')
        self.figure.set_dpi(72)
        imagedpi = kwargs.pop('dpi', 72)
        facecolor = kwargs.pop('facecolor', 'w')
        edgecolor = kwargs.pop('edgecolor', 'w')
        if rcParams['text.usetex']:
            self._print_figure_tex(outfile, format, imagedpi, facecolor, edgecolor, orientation, isLandscape, papertype, **kwargs)
        else:
            self._print_figure(outfile, format, imagedpi, facecolor, edgecolor, orientation, isLandscape, papertype, **kwargs)

    def _print_figure(self, outfile, format, dpi=72, facecolor='w', edgecolor='w', orientation='portrait', isLandscape=False, papertype=None, **kwargs):
        """
        Render the figure to hardcopy.  Set the figure patch face and
        edge colors.  This is useful because some of the GUIs have a
        gray figure face color background and you'll probably want to
        override this on hardcopy

        If outfile is a string, it is interpreted as a file name.
        If the extension matches .ep* write encapsulated postscript,
        otherwise write a stand-alone PostScript file.

        If outfile is a file object, a stand-alone PostScript file is
        written into this file object.
        """
        isEPSF = format == 'eps'
        passed_in_file_object = False
        if is_string_like(outfile):
            title = outfile
        elif is_writable_file_like(outfile):
            title = None
            passed_in_file_object = True
        else:
            raise ValueError('outfile must be a path or a file-like object')
        width, height = self.figure.get_size_inches()
        if papertype == 'auto':
            if isLandscape:
                papertype = _get_papertype(height, width)
            else:
                papertype = _get_papertype(width, height)
        if isLandscape:
            paperHeight, paperWidth = papersize[papertype]
        else:
            paperWidth, paperHeight = papersize[papertype]
        if rcParams['ps.usedistiller'] and not papertype == 'auto':
            if width > paperWidth or height > paperHeight:
                if isLandscape:
                    papertype = _get_papertype(height, width)
                    paperHeight, paperWidth = papersize[papertype]
                else:
                    papertype = _get_papertype(width, height)
                    paperWidth, paperHeight = papersize[papertype]
        xo = 36.0 * (paperWidth - width)
        yo = 36.0 * (paperHeight - height)
        l, b, w, h = self.figure.bbox.bounds
        llx = xo
        lly = yo
        urx = llx + w
        ury = lly + h
        rotation = 0
        if isLandscape:
            llx, lly, urx, ury = (
             lly, llx, ury, urx)
            xo, yo = 72 * paperHeight - yo, xo
            rotation = 90
        bbox = (
         llx, lly, urx, ury)
        origfacecolor = self.figure.get_facecolor()
        origedgecolor = self.figure.get_edgecolor()
        self.figure.set_facecolor(facecolor)
        self.figure.set_edgecolor(edgecolor)
        dryrun = kwargs.get('dryrun', False)
        if dryrun:

            class NullWriter(object):

                def write(self, *kl, **kwargs):
                    pass

            self._pswriter = NullWriter()
        elif sys.version_info[0] >= 3:
            self._pswriter = io.StringIO()
        else:
            self._pswriter = cStringIO.StringIO()
        _bbox_inches_restore = kwargs.pop('bbox_inches_restore', None)
        ps_renderer = self._renderer_class(width, height, self._pswriter, imagedpi=dpi)
        renderer = MixedModeRenderer(self.figure, width, height, dpi, ps_renderer, bbox_inches_restore=_bbox_inches_restore)
        self.figure.draw(renderer)
        if dryrun:
            return
        else:
            self.figure.set_facecolor(origfacecolor)
            self.figure.set_edgecolor(origedgecolor)
            fd, tmpfile = mkstemp()
            with io.open(fd, 'wb') as (raw_fh):
                if sys.version_info[0] >= 3:
                    fh = io.TextIOWrapper(raw_fh, encoding='ascii')
                else:
                    fh = raw_fh
                if isEPSF:
                    print('%!PS-Adobe-3.0 EPSF-3.0', file=fh)
                else:
                    print('%!PS-Adobe-3.0', file=fh)
                if title:
                    print('%%Title: ' + title, file=fh)
                print('%%Creator: matplotlib version ' + __version__ + ', http://matplotlib.org/', file=fh)
                print('%%CreationDate: ' + time.ctime(time.time()), file=fh)
                print('%%Orientation: ' + orientation, file=fh)
                if not isEPSF:
                    print('%%DocumentPaperSizes: ' + papertype, file=fh)
                print('%%%%BoundingBox: %d %d %d %d' % bbox, file=fh)
                if not isEPSF:
                    print('%%Pages: 1', file=fh)
                print('%%EndComments', file=fh)
                Ndict = len(psDefs)
                print('%%BeginProlog', file=fh)
                if not rcParams['ps.useafm']:
                    Ndict += len(ps_renderer.used_characters)
                print('/mpldict %d dict def' % Ndict, file=fh)
                print('mpldict begin', file=fh)
                for d in psDefs:
                    d = d.strip()
                    for l in d.split('\n'):
                        print(l.strip(), file=fh)

                if not rcParams['ps.useafm']:
                    for font_filename, chars in ps_renderer.used_characters.itervalues():
                        if len(chars):
                            font = FT2Font(str(font_filename))
                            cmap = font.get_charmap()
                            glyph_ids = []
                            for c in chars:
                                gind = cmap.get(c) or 0
                                glyph_ids.append(gind)

                            fonttype = rcParams['ps.fonttype']
                            if len(glyph_ids) > 255:
                                fonttype = 42
                            if is_opentype_cff_font(font_filename):
                                raise RuntimeError('OpenType CFF fonts can not be saved using the internal Postscript backend at this time.\nConsider using the Cairo backend.')
                            else:
                                fh.flush()
                                convert_ttf_to_ps(font_filename, raw_fh, fonttype, glyph_ids)

                print('end', file=fh)
                print('%%EndProlog', file=fh)
                if not isEPSF:
                    print('%%Page: 1 1', file=fh)
                print('mpldict begin', file=fh)
                print('%s translate' % _nums_to_str(xo, yo), file=fh)
                if rotation:
                    print('%d rotate' % rotation, file=fh)
                print('%s clipbox' % _nums_to_str(width * 72, height * 72, 0, 0), file=fh)
                print(self._pswriter.getvalue(), file=fh)
                print('end', file=fh)
                print('showpage', file=fh)
                if not isEPSF:
                    print('%%EOF', file=fh)
            if rcParams['ps.usedistiller'] == 'ghostscript':
                gs_distill(tmpfile, isEPSF, ptype=papertype, bbox=bbox)
            elif rcParams['ps.usedistiller'] == 'xpdf':
                xpdf_distill(tmpfile, isEPSF, ptype=papertype, bbox=bbox)
            if passed_in_file_object:
                with open(tmpfile, 'rb') as (fh):
                    print(fh.read(), file=outfile)
            else:
                with open(outfile, 'w') as (fh):
                    pass
                mode = os.stat(outfile).st_mode
                shutil.move(tmpfile, outfile)
                os.chmod(outfile, mode)
            return

    def _print_figure_tex(self, outfile, format, dpi, facecolor, edgecolor, orientation, isLandscape, papertype, **kwargs):
        """
        If text.usetex is True in rc, a temporary pair of tex/eps files
        are created to allow tex to manage the text layout via the PSFrags
        package. These files are processed to yield the final ps or eps file.
        """
        isEPSF = format == 'eps'
        title = outfile
        self.figure.dpi = 72
        width, height = self.figure.get_size_inches()
        xo = 0
        yo = 0
        l, b, w, h = self.figure.bbox.bounds
        llx = xo
        lly = yo
        urx = llx + w
        ury = lly + h
        bbox = (llx, lly, urx, ury)
        origfacecolor = self.figure.get_facecolor()
        origedgecolor = self.figure.get_edgecolor()
        self.figure.set_facecolor(facecolor)
        self.figure.set_edgecolor(edgecolor)
        dryrun = kwargs.get('dryrun', False)
        if dryrun:

            class NullWriter(object):

                def write(self, *kl, **kwargs):
                    pass

            self._pswriter = NullWriter()
        elif sys.version_info[0] >= 3:
            self._pswriter = io.StringIO()
        else:
            self._pswriter = cStringIO.StringIO()
        _bbox_inches_restore = kwargs.pop('bbox_inches_restore', None)
        ps_renderer = self._renderer_class(width, height, self._pswriter, imagedpi=dpi)
        renderer = MixedModeRenderer(self.figure, width, height, dpi, ps_renderer, bbox_inches_restore=_bbox_inches_restore)
        self.figure.draw(renderer)
        if dryrun:
            return
        else:
            self.figure.set_facecolor(origfacecolor)
            self.figure.set_edgecolor(origedgecolor)
            fd, tmpfile = mkstemp()
            if sys.version_info[0] >= 3:
                fh = io.open(fd, 'w', encoding='ascii')
            else:
                fh = io.open(fd, 'wb')
            with fh:
                print('%!PS-Adobe-3.0 EPSF-3.0', file=fh)
                if title:
                    print('%%Title: ' + title, file=fh)
                print('%%Creator: matplotlib version ' + __version__ + ', http://matplotlib.org/', file=fh)
                print('%%CreationDate: ' + time.ctime(time.time()), file=fh)
                print('%%%%BoundingBox: %d %d %d %d' % bbox, file=fh)
                print('%%EndComments', file=fh)
                Ndict = len(psDefs)
                print('%%BeginProlog', file=fh)
                print('/mpldict %d dict def' % Ndict, file=fh)
                print('mpldict begin', file=fh)
                for d in psDefs:
                    d = d.strip()
                    for l in d.split('\n'):
                        print(l.strip(), file=fh)

                print('end', file=fh)
                print('%%EndProlog', file=fh)
                print('mpldict begin', file=fh)
                print('%s translate' % _nums_to_str(xo, yo), file=fh)
                print('%s clipbox' % _nums_to_str(width * 72, height * 72, 0, 0), file=fh)
                print(self._pswriter.getvalue(), file=fh)
                print('end', file=fh)
                print('showpage', file=fh)
            if isLandscape:
                isLandscape = True
                width, height = height, width
                bbox = (lly, llx, ury, urx)
            if isEPSF:
                paperWidth, paperHeight = self.figure.get_size_inches()
                if isLandscape:
                    paperWidth, paperHeight = paperHeight, paperWidth
            else:
                temp_papertype = _get_papertype(width, height)
                if papertype == 'auto':
                    papertype = temp_papertype
                    paperWidth, paperHeight = papersize[temp_papertype]
                else:
                    paperWidth, paperHeight = papersize[papertype]
                    if (width > paperWidth or height > paperHeight) and isEPSF:
                        paperWidth, paperHeight = papersize[temp_papertype]
                        verbose.report('Your figure is too big to fit on %s paper. %s     paper will be used to prevent clipping.' % (papertype, temp_papertype), 'helpful')
            texmanager = ps_renderer.get_texmanager()
            font_preamble = texmanager.get_font_preamble()
            custom_preamble = texmanager.get_custom_preamble()
            psfrag_rotated = convert_psfrags(tmpfile, ps_renderer.psfrag, font_preamble, custom_preamble, paperWidth, paperHeight, orientation)
            if rcParams['ps.usedistiller'] == 'ghostscript':
                gs_distill(tmpfile, isEPSF, ptype=papertype, bbox=bbox, rotated=psfrag_rotated)
            elif rcParams['ps.usedistiller'] == 'xpdf':
                xpdf_distill(tmpfile, isEPSF, ptype=papertype, bbox=bbox, rotated=psfrag_rotated)
            elif rcParams['text.usetex']:
                if False:
                    pass
                else:
                    gs_distill(tmpfile, isEPSF, ptype=papertype, bbox=bbox, rotated=psfrag_rotated)
            is_file = False
            if sys.version_info[0] >= 3:
                if isinstance(outfile, io.IOBase):
                    is_file = True
            elif isinstance(outfile, file):
                is_file = True
            if is_file:
                with open(tmpfile, 'rb') as (fh):
                    outfile.write(fh.read())
            else:
                with open(outfile, 'wb') as (fh):
                    pass
                mode = os.stat(outfile).st_mode
                shutil.move(tmpfile, outfile)
                os.chmod(outfile, mode)
            return


def convert_psfrags(tmpfile, psfrags, font_preamble, custom_preamble, paperWidth, paperHeight, orientation):
    """
    When we want to use the LaTeX backend with postscript, we write PSFrag tags
    to a temporary postscript file, each one marking a position for LaTeX to
    render some text. convert_psfrags generates a LaTeX document containing the
    commands to convert those tags to text. LaTeX/dvips produces the postscript
    file that includes the actual text.
    """
    tmpdir = os.path.split(tmpfile)[0]
    epsfile = tmpfile + '.eps'
    shutil.move(tmpfile, epsfile)
    latexfile = tmpfile + '.tex'
    outfile = tmpfile + '.output'
    dvifile = tmpfile + '.dvi'
    psfile = tmpfile + '.ps'
    if orientation == 'landscape':
        angle = 90
    else:
        angle = 0
    if rcParams['text.latex.unicode']:
        unicode_preamble = '\\usepackage{ucs}\n\\usepackage[utf8x]{inputenc}'
    else:
        unicode_preamble = ''
    s = '\\documentclass{article}\n%s\n%s\n%s\n\\usepackage[dvips, papersize={%sin,%sin}, body={%sin,%sin}, margin={0in,0in}]{geometry}\n\\usepackage{psfrag}\n\\usepackage[dvips]{graphicx}\n\\usepackage{color}\n\\pagestyle{empty}\n\\begin{document}\n\\begin{figure}\n\\centering\n\\leavevmode\n%s\n\\includegraphics*[angle=%s]{%s}\n\\end{figure}\n\\end{document}\n' % (font_preamble, unicode_preamble, custom_preamble, paperWidth, paperHeight,
     paperWidth, paperHeight,
     ('\n').join(psfrags), angle, os.path.split(epsfile)[-1])
    with io.open(latexfile, 'wb') as (latexh):
        if rcParams['text.latex.unicode']:
            latexh.write(s.encode('utf8'))
        else:
            try:
                latexh.write(s.encode('ascii'))
            except UnicodeEncodeError:
                verbose.report("You are using unicode and latex, but have not enabled the matplotlib 'text.latex.unicode' rcParam.", 'helpful')
                raise

    if sys.platform == 'win32':
        precmd = '%s &&' % os.path.splitdrive(tmpdir)[0]
    else:
        precmd = ''
    command = '%s cd "%s" && latex -interaction=nonstopmode "%s" > "%s"' % (
     precmd, tmpdir, latexfile, outfile)
    verbose.report(command, 'debug')
    exit_status = os.system(command)
    with io.open(outfile, 'rb') as (fh):
        if exit_status:
            raise RuntimeError('LaTeX was not able to process your file:    \nHere is the full report generated by LaTeX: \n\n%s' % fh.read())
        else:
            verbose.report(fh.read(), 'debug')
    os.remove(outfile)
    command = '%s cd "%s" && dvips -q -R0 -o "%s" "%s" > "%s"' % (precmd, tmpdir,
     os.path.split(psfile)[-1], os.path.split(dvifile)[-1], outfile)
    verbose.report(command, 'debug')
    exit_status = os.system(command)
    with io.open(outfile, 'rb') as (fh):
        if exit_status:
            raise RuntimeError('dvips was not able to     process the following file:\n%s\nHere is the full report generated by dvips:     \n\n' % dvifile + fh.read())
        else:
            verbose.report(fh.read(), 'debug')
    os.remove(outfile)
    os.remove(epsfile)
    shutil.move(psfile, tmpfile)
    with open(tmpfile) as (fh):
        if 'Landscape' in fh.read(1000):
            psfrag_rotated = True
        else:
            psfrag_rotated = False
    if not debugPS:
        for fname in glob.glob(tmpfile + '.*'):
            os.remove(fname)

    return psfrag_rotated


def gs_distill(tmpfile, eps=False, ptype='letter', bbox=None, rotated=False):
    """
    Use ghostscript's pswrite or epswrite device to distill a file.
    This yields smaller files without illegal encapsulated postscript
    operators. The output is low-level, converting text to outlines.
    """
    if eps:
        paper_option = '-dEPSCrop'
    else:
        paper_option = '-sPAPERSIZE=%s' % ptype
    psfile = tmpfile + '.ps'
    outfile = tmpfile + '.output'
    dpi = rcParams['ps.distiller.res']
    gs_exe = ps_backend_helper.gs_exe
    if ps_backend_helper.supports_ps2write:
        device_name = 'ps2write'
    else:
        device_name = 'pswrite'
    command = '%s -dBATCH -dNOPAUSE -r%d -sDEVICE=%s %s -sOutputFile="%s"                 "%s" > "%s"' % (gs_exe, dpi, device_name,
     paper_option, psfile, tmpfile, outfile)
    verbose.report(command, 'debug')
    exit_status = os.system(command)
    with io.open(outfile, 'rb') as (fh):
        if exit_status:
            raise RuntimeError('ghostscript was not able to process     your image.\nHere is the full report generated by ghostscript:\n\n' + fh.read())
        else:
            verbose.report(fh.read(), 'debug')
    os.remove(outfile)
    os.remove(tmpfile)
    shutil.move(psfile, tmpfile)
    if eps:
        if ps_backend_helper.supports_ps2write:
            pstoeps(tmpfile, bbox, rotated=rotated)
        else:
            pstoeps(tmpfile)


def xpdf_distill(tmpfile, eps=False, ptype='letter', bbox=None, rotated=False):
    """
    Use ghostscript's ps2pdf and xpdf's/poppler's pdftops to distill a file.
    This yields smaller files without illegal encapsulated postscript
    operators. This distiller is preferred, generating high-level postscript
    output that treats text as text.
    """
    pdffile = tmpfile + '.pdf'
    psfile = tmpfile + '.ps'
    outfile = tmpfile + '.output'
    if eps:
        paper_option = '-dEPSCrop'
    else:
        paper_option = '-sPAPERSIZE=%s' % ptype
    command = 'ps2pdf -dAutoFilterColorImages=false -sColorImageFilter=FlateEncode %s "%s" "%s" > "%s"' % (
     paper_option, tmpfile, pdffile, outfile)
    if sys.platform == 'win32':
        command = command.replace('=', '#')
    verbose.report(command, 'debug')
    exit_status = os.system(command)
    with io.open(outfile, 'rb') as (fh):
        if exit_status:
            raise RuntimeError('ps2pdf was not able to process your image.\n\\Here is the report generated by ghostscript:\n\n' + fh.read())
        else:
            verbose.report(fh.read(), 'debug')
    os.remove(outfile)
    command = 'pdftops -paper match -level2 "%s" "%s" > "%s"' % (
     pdffile, psfile, outfile)
    verbose.report(command, 'debug')
    exit_status = os.system(command)
    with io.open(outfile, 'rb') as (fh):
        if exit_status:
            raise RuntimeError('pdftops was not able to process your image.\nHere is the full report generated by pdftops: \n\n' + fh.read())
        else:
            verbose.report(fh.read(), 'debug')
    os.remove(outfile)
    os.remove(tmpfile)
    shutil.move(psfile, tmpfile)
    if eps:
        pstoeps(tmpfile)
    for fname in glob.glob(tmpfile + '.*'):
        os.remove(fname)


def get_bbox_header(lbrt, rotated=False):
    """
    return a postscript header stringfor the given bbox lbrt=(l, b, r, t).
    Optionally, return rotate command.
    """
    l, b, r, t = lbrt
    if rotated:
        rotate = '%.2f %.2f  translate\n90 rotate' % (l + r, 0)
    else:
        rotate = ''
    bbox_info = '%%%%BoundingBox: %d %d %d %d' % (l, b, np.ceil(r), np.ceil(t))
    hires_bbox_info = '%%%%HiResBoundingBox: %.6f %.6f %.6f %.6f' % (l, b, r, t)
    return (
     ('\n').join([bbox_info, hires_bbox_info]), rotate)


def get_bbox(tmpfile, bbox):
    """
    Use ghostscript's bbox device to find the center of the bounding box. Return
    an appropriately sized bbox centered around that point. A bit of a hack.
    """
    outfile = tmpfile + '.output'
    if sys.platform == 'win32':
        gs_exe = 'gswin32c'
    else:
        gs_exe = 'gs'
    command = '%s -dBATCH -dNOPAUSE -sDEVICE=bbox "%s"' % (
     gs_exe, tmpfile)
    verbose.report(command, 'debug')
    stdin, stdout, stderr = os.popen3(command)
    verbose.report(stdout.read(), 'debug-annoying')
    bbox_info = stderr.read()
    verbose.report(bbox_info, 'helpful')
    bbox_found = re.search('%%HiResBoundingBox: .*', bbox_info)
    if bbox_found:
        bbox_info = bbox_found.group()
    else:
        raise RuntimeError('Ghostscript was not able to extract a bounding box.Here is the Ghostscript output:\n\n%s' % bbox_info)
    l, b, r, t = [ float(i) for i in bbox_info.split()[-4:] ]
    if bbox is None:
        l, b, r, t = (
         l - 1, b - 1, r + 1, t + 1)
    else:
        x = (l + r) / 2
        y = (b + t) / 2
        dx = (bbox[2] - bbox[0]) / 2
        dy = (bbox[3] - bbox[1]) / 2
        l, b, r, t = (x - dx, y - dy, x + dx, y + dy)
    bbox_info = '%%%%BoundingBox: %d %d %d %d' % (l, b, np.ceil(r), np.ceil(t))
    hires_bbox_info = '%%%%HiResBoundingBox: %.6f %.6f %.6f %.6f' % (l, b, r, t)
    return ('\n').join([bbox_info, hires_bbox_info])


def pstoeps(tmpfile, bbox=None, rotated=False):
    """
    Convert the postscript to encapsulated postscript.  The bbox of
    the eps file will be replaced with the given *bbox* argument. If
    None, original bbox will be used.
    """
    if bbox:
        bbox_info, rotate = get_bbox_header(bbox, rotated=rotated)
    else:
        bbox_info, rotate = (None, None)
    epsfile = tmpfile + '.eps'
    with io.open(epsfile, 'wb') as (epsh):
        write = epsh.write
        with io.open(tmpfile, 'rb') as (tmph):
            line = tmph.readline()
            while line:
                if line.startswith('%!PS'):
                    write('%!PS-Adobe-3.0 EPSF-3.0\n')
                    if bbox:
                        write(bbox_info.encode('ascii') + '\n')
                elif line.startswith('%%EndComments'):
                    write(line)
                    write('%%BeginProlog\n')
                    write('save\n')
                    write('countdictstack\n')
                    write('mark\n')
                    write('newpath\n')
                    write('/showpage {} def\n')
                    write('/setpagedevice {pop} def\n')
                    write('%%EndProlog\n')
                    write('%%Page 1 1\n')
                    if rotate:
                        write(rotate.encode('ascii') + '\n')
                    break
                elif bbox and (line.startswith('%%Bound') or line.startswith('%%HiResBound') or line.startswith('%%DocumentMedia') or line.startswith('%%Pages')):
                    pass
                else:
                    write(line)
                line = tmph.readline()

            line = tmph.readline()
            while line:
                if line.startswith('%%Trailer'):
                    write('%%Trailer\n')
                    write('cleartomark\n')
                    write('countdictstack\n')
                    write('exch sub { end } repeat\n')
                    write('restore\n')
                    if rcParams['ps.usedistiller'] == 'xpdf':
                        line = tmph.readline()
                elif line.startswith('%%PageBoundingBox'):
                    pass
                else:
                    write(line)
                line = tmph.readline()

    os.remove(tmpfile)
    shutil.move(epsfile, tmpfile)
    return


class FigureManagerPS(FigureManagerBase):
    pass


FigureManager = FigureManagerPS
psDefs = [
 '/m { moveto } bind def', 
 '/l { lineto } bind def', 
 '/r { rlineto } bind def', 
 '/c { curveto } bind def', 
 '/cl { closepath } bind def', 
 '/box {\n      m\n      1 index 0 r\n      0 exch r\n      neg 0 r\n      cl\n    } bind def', 
 '/clipbox {\n      box\n      clip\n      newpath\n    } bind def']