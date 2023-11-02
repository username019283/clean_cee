# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: reportlab\graphics\barcode\fourstate.pyc
# Compiled at: 2013-03-27 15:37:42
from reportlab.lib.units import inch
from common import Barcode
import string
_rm_patterns = {'0': '--||', 
   '1': "-',|", '2': "-'|,", '3': "'-,|", '4': "'-|,", 
   '5': "'',,", '6': "-,'|", '7': '-|-|', '8': "-|',", 
   '9': "',-|", 'A': "',',", 'B': "'|-,", 'C': "-,|'", 
   'D': "-|,'", 'E': '-||-', 'F': "',,'", 'G': "',|-", 
   'H': "'|,-", 'I': ",-'|", 'J': ",'-|", 'K': ",'',", 
   'L': '|--|', 'M': "|-',", 'N': "|'-,", 'O': ",-|'", 
   'P': ",','", 'Q': ",'|-", 'R': "|-,'", 'S': '|-|-', 
   'T': "|',-", 'U': ",,''", 'V': ",|-'", 'W': ",|'-", 
   'X': "|,-'", 'Y': "|,'-", 'Z': '||--', '(': "'-,'", 
   ')': "'|,|"}
_ozN_patterns = {'0': '||', 
   '1': "|'", '2': '|,', '3': "'|", '4': "''", '5': "',", 
   '6': ',|', '7': ",'", '8': ',,', '9': '.|'}
_ozC_patterns = {'A': '|||', 
   'B': "||'", 'C': '||,', 'D': "|'|", 'E': "|''", 
   'F': "|',", 'G': '|,|', 'H': "|,'", 'I': '|,,', 
   'J': "'||", 'K': "'|'", 'L': "'|,", 'M': "''|", 
   'N': "'''", 'O': "'',", 'P': "',|", 'Q': "','", 
   'R': "',,", 'S': ',||', 'T': ",|'", 'U': ',|,', 
   'V': ",'|", 'W': ",''", 'X': ",',", 'Y': ',,|', 
   'Z': ",,'", 'a': '|,.', 'b': '|.|', 'c': "|.'", 
   'd': '|.,', 'e': '|..', 'f': "'|.", 'g': "''.", 
   'h': "',.", 'i': "'.|", 'j': "'.'", 'k': "'.,", 
   'l': "'..", 'm': ',|.', 'n': ",'.", 'o': ',,.', 
   'p': ',.|', 'q': ",.'", 'r': ',.,', 's': ',..', 
   't': '.|.', 'u': ".'.", 'v': '.,.', 'w': '..|', 
   'x': "..'", 'y': '..,', 'z': '...', '0': ',,,', 
   '1': '.||', '2': ".|'", '3': '.|,', '4': ".'|", 
   '5': ".''", '6': ".',", '7': '.,|', '8': ".,'", 
   '9': '.,,', ' ': '||.', '#': "|'."}