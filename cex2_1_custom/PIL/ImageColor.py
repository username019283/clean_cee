# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PIL\ImageColor.pyc
# Compiled at: 2010-05-15 16:50:38
import Image, re, string
try:
    x = int('a', 16)
except TypeError:
    str2int = string.atoi
else:
    str2int = int

def getrgb(color):
    try:
        rgb = colormap[color]
    except KeyError:
        try:
            rgb = colormap[string.lower(color)]
        except KeyError:
            rgb = None

    if rgb:
        if isinstance(rgb, type(())):
            return rgb
        colormap[color] = rgb = getrgb(rgb)
        return rgb
    else:
        m = re.match('#\\w\\w\\w$', color)
        if m:
            return (
             str2int(color[1] * 2, 16),
             str2int(color[2] * 2, 16),
             str2int(color[3] * 2, 16))
        m = re.match('#\\w\\w\\w\\w\\w\\w$', color)
        if m:
            return (
             str2int(color[1:3], 16),
             str2int(color[3:5], 16),
             str2int(color[5:7], 16))
        m = re.match('rgb\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)$', color)
        if m:
            return (
             str2int(m.group(1)),
             str2int(m.group(2)),
             str2int(m.group(3)))
        m = re.match('rgb\\(\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*\\)$', color)
        if m:
            return (
             int(str2int(m.group(1)) * 255 / 100.0 + 0.5),
             int(str2int(m.group(2)) * 255 / 100.0 + 0.5),
             int(str2int(m.group(3)) * 255 / 100.0 + 0.5))
        m = re.match('hsl\\(\\s*(\\d+)\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*\\)$', color)
        if m:
            from colorsys import hls_to_rgb
            rgb = hls_to_rgb(float(m.group(1)) / 360.0, float(m.group(3)) / 100.0, float(m.group(2)) / 100.0)
            return (
             int(rgb[0] * 255 + 0.5),
             int(rgb[1] * 255 + 0.5),
             int(rgb[2] * 255 + 0.5))
        raise ValueError('unknown color specifier: %r' % color)
        return


def getcolor(color, mode):
    color = getrgb(color)
    if mode == 'RGB':
        return color
    if mode == 'RGBA':
        r, g, b = color
        return (
         r, g, b, 255)
    if Image.getmodebase(mode) == 'L':
        r, g, b = color
        return (r * 299 + g * 587 + b * 114) / 1000
    return color


colormap = {'aliceblue': '#f0f8ff', 
   'antiquewhite': '#faebd7', 
   'aqua': '#00ffff', 
   'aquamarine': '#7fffd4', 
   'azure': '#f0ffff', 
   'beige': '#f5f5dc', 
   'bisque': '#ffe4c4', 
   'black': '#000000', 
   'blanchedalmond': '#ffebcd', 
   'blue': '#0000ff', 
   'blueviolet': '#8a2be2', 
   'brown': '#a52a2a', 
   'burlywood': '#deb887', 
   'cadetblue': '#5f9ea0', 
   'chartreuse': '#7fff00', 
   'chocolate': '#d2691e', 
   'coral': '#ff7f50', 
   'cornflowerblue': '#6495ed', 
   'cornsilk': '#fff8dc', 
   'crimson': '#dc143c', 
   'cyan': '#00ffff', 
   'darkblue': '#00008b', 
   'darkcyan': '#008b8b', 
   'darkgoldenrod': '#b8860b', 
   'darkgray': '#a9a9a9', 
   'darkgrey': '#a9a9a9', 
   'darkgreen': '#006400', 
   'darkkhaki': '#bdb76b', 
   'darkmagenta': '#8b008b', 
   'darkolivegreen': '#556b2f', 
   'darkorange': '#ff8c00', 
   'darkorchid': '#9932cc', 
   'darkred': '#8b0000', 
   'darksalmon': '#e9967a', 
   'darkseagreen': '#8fbc8f', 
   'darkslateblue': '#483d8b', 
   'darkslategray': '#2f4f4f', 
   'darkslategrey': '#2f4f4f', 
   'darkturquoise': '#00ced1', 
   'darkviolet': '#9400d3', 
   'deeppink': '#ff1493', 
   'deepskyblue': '#00bfff', 
   'dimgray': '#696969', 
   'dimgrey': '#696969', 
   'dodgerblue': '#1e90ff', 
   'firebrick': '#b22222', 
   'floralwhite': '#fffaf0', 
   'forestgreen': '#228b22', 
   'fuchsia': '#ff00ff', 
   'gainsboro': '#dcdcdc', 
   'ghostwhite': '#f8f8ff', 
   'gold': '#ffd700', 
   'goldenrod': '#daa520', 
   'gray': '#808080', 
   'grey': '#808080', 
   'green': '#008000', 
   'greenyellow': '#adff2f', 
   'honeydew': '#f0fff0', 
   'hotpink': '#ff69b4', 
   'indianred': '#cd5c5c', 
   'indigo': '#4b0082', 
   'ivory': '#fffff0', 
   'khaki': '#f0e68c', 
   'lavender': '#e6e6fa', 
   'lavenderblush': '#fff0f5', 
   'lawngreen': '#7cfc00', 
   'lemonchiffon': '#fffacd', 
   'lightblue': '#add8e6', 
   'lightcoral': '#f08080', 
   'lightcyan': '#e0ffff', 
   'lightgoldenrodyellow': '#fafad2', 
   'lightgreen': '#90ee90', 
   'lightgray': '#d3d3d3', 
   'lightgrey': '#d3d3d3', 
   'lightpink': '#ffb6c1', 
   'lightsalmon': '#ffa07a', 
   'lightseagreen': '#20b2aa', 
   'lightskyblue': '#87cefa', 
   'lightslategray': '#778899', 
   'lightslategrey': '#778899', 
   'lightsteelblue': '#b0c4de', 
   'lightyellow': '#ffffe0', 
   'lime': '#00ff00', 
   'limegreen': '#32cd32', 
   'linen': '#faf0e6', 
   'magenta': '#ff00ff', 
   'maroon': '#800000', 
   'mediumaquamarine': '#66cdaa', 
   'mediumblue': '#0000cd', 
   'mediumorchid': '#ba55d3', 
   'mediumpurple': '#9370db', 
   'mediumseagreen': '#3cb371', 
   'mediumslateblue': '#7b68ee', 
   'mediumspringgreen': '#00fa9a', 
   'mediumturquoise': '#48d1cc', 
   'mediumvioletred': '#c71585', 
   'midnightblue': '#191970', 
   'mintcream': '#f5fffa', 
   'mistyrose': '#ffe4e1', 
   'moccasin': '#ffe4b5', 
   'navajowhite': '#ffdead', 
   'navy': '#000080', 
   'oldlace': '#fdf5e6', 
   'olive': '#808000', 
   'olivedrab': '#6b8e23', 
   'orange': '#ffa500', 
   'orangered': '#ff4500', 
   'orchid': '#da70d6', 
   'palegoldenrod': '#eee8aa', 
   'palegreen': '#98fb98', 
   'paleturquoise': '#afeeee', 
   'palevioletred': '#db7093', 
   'papayawhip': '#ffefd5', 
   'peachpuff': '#ffdab9', 
   'peru': '#cd853f', 
   'pink': '#ffc0cb', 
   'plum': '#dda0dd', 
   'powderblue': '#b0e0e6', 
   'purple': '#800080', 
   'red': '#ff0000', 
   'rosybrown': '#bc8f8f', 
   'royalblue': '#4169e1', 
   'saddlebrown': '#8b4513', 
   'salmon': '#fa8072', 
   'sandybrown': '#f4a460', 
   'seagreen': '#2e8b57', 
   'seashell': '#fff5ee', 
   'sienna': '#a0522d', 
   'silver': '#c0c0c0', 
   'skyblue': '#87ceeb', 
   'slateblue': '#6a5acd', 
   'slategray': '#708090', 
   'slategrey': '#708090', 
   'snow': '#fffafa', 
   'springgreen': '#00ff7f', 
   'steelblue': '#4682b4', 
   'tan': '#d2b48c', 
   'teal': '#008080', 
   'thistle': '#d8bfd8', 
   'tomato': '#ff6347', 
   'turquoise': '#40e0d0', 
   'violet': '#ee82ee', 
   'wheat': '#f5deb3', 
   'white': '#ffffff', 
   'whitesmoke': '#f5f5f5', 
   'yellow': '#ffff00', 
   'yellowgreen': '#9acd32'}