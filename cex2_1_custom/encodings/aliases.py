# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: encodings\aliases.pyc
# Compiled at: 2011-03-08 09:43:14
""" Encoding Aliases Support

    This module is used by the encodings package search function to
    map encodings names to module names.

    Note that the search function normalizes the encoding names before
    doing the lookup, so the mapping will have to map normalized
    encoding names to module names.

    Contents:

        The following aliases dictionary contains mappings of all IANA
        character set names for which the Python core library provides
        codecs. In addition to these, a few Python specific codec
        aliases have also been added.

"""
aliases = {'646': 'ascii', 
   'ansi_x3.4_1968': 'ascii', 
   'ansi_x3_4_1968': 'ascii', 
   'ansi_x3.4_1986': 'ascii', 
   'cp367': 'ascii', 
   'csascii': 'ascii', 
   'ibm367': 'ascii', 
   'iso646_us': 'ascii', 
   'iso_646.irv_1991': 'ascii', 
   'iso_ir_6': 'ascii', 
   'us': 'ascii', 
   'us_ascii': 'ascii', 
   'base64': 'base64_codec', 
   'base_64': 'base64_codec', 
   'big5_tw': 'big5', 
   'csbig5': 'big5', 
   'big5_hkscs': 'big5hkscs', 
   'hkscs': 'big5hkscs', 
   'bz2': 'bz2_codec', 
   '037': 'cp037', 
   'csibm037': 'cp037', 
   'ebcdic_cp_ca': 'cp037', 
   'ebcdic_cp_nl': 'cp037', 
   'ebcdic_cp_us': 'cp037', 
   'ebcdic_cp_wt': 'cp037', 
   'ibm037': 'cp037', 
   'ibm039': 'cp037', 
   '1026': 'cp1026', 
   'csibm1026': 'cp1026', 
   'ibm1026': 'cp1026', 
   '1140': 'cp1140', 
   'ibm1140': 'cp1140', 
   '1250': 'cp1250', 
   'windows_1250': 'cp1250', 
   '1251': 'cp1251', 
   'windows_1251': 'cp1251', 
   '1252': 'cp1252', 
   'windows_1252': 'cp1252', 
   '1253': 'cp1253', 
   'windows_1253': 'cp1253', 
   '1254': 'cp1254', 
   'windows_1254': 'cp1254', 
   '1255': 'cp1255', 
   'windows_1255': 'cp1255', 
   '1256': 'cp1256', 
   'windows_1256': 'cp1256', 
   '1257': 'cp1257', 
   'windows_1257': 'cp1257', 
   '1258': 'cp1258', 
   'windows_1258': 'cp1258', 
   '424': 'cp424', 
   'csibm424': 'cp424', 
   'ebcdic_cp_he': 'cp424', 
   'ibm424': 'cp424', 
   '437': 'cp437', 
   'cspc8codepage437': 'cp437', 
   'ibm437': 'cp437', 
   '500': 'cp500', 
   'csibm500': 'cp500', 
   'ebcdic_cp_be': 'cp500', 
   'ebcdic_cp_ch': 'cp500', 
   'ibm500': 'cp500', 
   '775': 'cp775', 
   'cspc775baltic': 'cp775', 
   'ibm775': 'cp775', 
   '850': 'cp850', 
   'cspc850multilingual': 'cp850', 
   'ibm850': 'cp850', 
   '852': 'cp852', 
   'cspcp852': 'cp852', 
   'ibm852': 'cp852', 
   '855': 'cp855', 
   'csibm855': 'cp855', 
   'ibm855': 'cp855', 
   '857': 'cp857', 
   'csibm857': 'cp857', 
   'ibm857': 'cp857', 
   '858': 'cp858', 
   'csibm858': 'cp858', 
   'ibm858': 'cp858', 
   '860': 'cp860', 
   'csibm860': 'cp860', 
   'ibm860': 'cp860', 
   '861': 'cp861', 
   'cp_is': 'cp861', 
   'csibm861': 'cp861', 
   'ibm861': 'cp861', 
   '862': 'cp862', 
   'cspc862latinhebrew': 'cp862', 
   'ibm862': 'cp862', 
   '863': 'cp863', 
   'csibm863': 'cp863', 
   'ibm863': 'cp863', 
   '864': 'cp864', 
   'csibm864': 'cp864', 
   'ibm864': 'cp864', 
   '865': 'cp865', 
   'csibm865': 'cp865', 
   'ibm865': 'cp865', 
   '866': 'cp866', 
   'csibm866': 'cp866', 
   'ibm866': 'cp866', 
   '869': 'cp869', 
   'cp_gr': 'cp869', 
   'csibm869': 'cp869', 
   'ibm869': 'cp869', 
   '932': 'cp932', 
   'ms932': 'cp932', 
   'mskanji': 'cp932', 
   'ms_kanji': 'cp932', 
   '949': 'cp949', 
   'ms949': 'cp949', 
   'uhc': 'cp949', 
   '950': 'cp950', 
   'ms950': 'cp950', 
   'jisx0213': 'euc_jis_2004', 
   'eucjis2004': 'euc_jis_2004', 
   'euc_jis2004': 'euc_jis_2004', 
   'eucjisx0213': 'euc_jisx0213', 
   'eucjp': 'euc_jp', 
   'ujis': 'euc_jp', 
   'u_jis': 'euc_jp', 
   'euckr': 'euc_kr', 
   'korean': 'euc_kr', 
   'ksc5601': 'euc_kr', 
   'ks_c_5601': 'euc_kr', 
   'ks_c_5601_1987': 'euc_kr', 
   'ksx1001': 'euc_kr', 
   'ks_x_1001': 'euc_kr', 
   'gb18030_2000': 'gb18030', 
   'chinese': 'gb2312', 
   'csiso58gb231280': 'gb2312', 
   'euc_cn': 'gb2312', 
   'euccn': 'gb2312', 
   'eucgb2312_cn': 'gb2312', 
   'gb2312_1980': 'gb2312', 
   'gb2312_80': 'gb2312', 
   'iso_ir_58': 'gb2312', 
   '936': 'gbk', 
   'cp936': 'gbk', 
   'ms936': 'gbk', 
   'hex': 'hex_codec', 
   'roman8': 'hp_roman8', 
   'r8': 'hp_roman8', 
   'csHPRoman8': 'hp_roman8', 
   'hzgb': 'hz', 
   'hz_gb': 'hz', 
   'hz_gb_2312': 'hz', 
   'csiso2022jp': 'iso2022_jp', 
   'iso2022jp': 'iso2022_jp', 
   'iso_2022_jp': 'iso2022_jp', 
   'iso2022jp_1': 'iso2022_jp_1', 
   'iso_2022_jp_1': 'iso2022_jp_1', 
   'iso2022jp_2': 'iso2022_jp_2', 
   'iso_2022_jp_2': 'iso2022_jp_2', 
   'iso_2022_jp_2004': 'iso2022_jp_2004', 
   'iso2022jp_2004': 'iso2022_jp_2004', 
   'iso2022jp_3': 'iso2022_jp_3', 
   'iso_2022_jp_3': 'iso2022_jp_3', 
   'iso2022jp_ext': 'iso2022_jp_ext', 
   'iso_2022_jp_ext': 'iso2022_jp_ext', 
   'csiso2022kr': 'iso2022_kr', 
   'iso2022kr': 'iso2022_kr', 
   'iso_2022_kr': 'iso2022_kr', 
   'csisolatin6': 'iso8859_10', 
   'iso_8859_10': 'iso8859_10', 
   'iso_8859_10_1992': 'iso8859_10', 
   'iso_ir_157': 'iso8859_10', 
   'l6': 'iso8859_10', 
   'latin6': 'iso8859_10', 
   'thai': 'iso8859_11', 
   'iso_8859_11': 'iso8859_11', 
   'iso_8859_11_2001': 'iso8859_11', 
   'iso_8859_13': 'iso8859_13', 
   'l7': 'iso8859_13', 
   'latin7': 'iso8859_13', 
   'iso_8859_14': 'iso8859_14', 
   'iso_8859_14_1998': 'iso8859_14', 
   'iso_celtic': 'iso8859_14', 
   'iso_ir_199': 'iso8859_14', 
   'l8': 'iso8859_14', 
   'latin8': 'iso8859_14', 
   'iso_8859_15': 'iso8859_15', 
   'l9': 'iso8859_15', 
   'latin9': 'iso8859_15', 
   'iso_8859_16': 'iso8859_16', 
   'iso_8859_16_2001': 'iso8859_16', 
   'iso_ir_226': 'iso8859_16', 
   'l10': 'iso8859_16', 
   'latin10': 'iso8859_16', 
   'csisolatin2': 'iso8859_2', 
   'iso_8859_2': 'iso8859_2', 
   'iso_8859_2_1987': 'iso8859_2', 
   'iso_ir_101': 'iso8859_2', 
   'l2': 'iso8859_2', 
   'latin2': 'iso8859_2', 
   'csisolatin3': 'iso8859_3', 
   'iso_8859_3': 'iso8859_3', 
   'iso_8859_3_1988': 'iso8859_3', 
   'iso_ir_109': 'iso8859_3', 
   'l3': 'iso8859_3', 
   'latin3': 'iso8859_3', 
   'csisolatin4': 'iso8859_4', 
   'iso_8859_4': 'iso8859_4', 
   'iso_8859_4_1988': 'iso8859_4', 
   'iso_ir_110': 'iso8859_4', 
   'l4': 'iso8859_4', 
   'latin4': 'iso8859_4', 
   'csisolatincyrillic': 'iso8859_5', 
   'cyrillic': 'iso8859_5', 
   'iso_8859_5': 'iso8859_5', 
   'iso_8859_5_1988': 'iso8859_5', 
   'iso_ir_144': 'iso8859_5', 
   'arabic': 'iso8859_6', 
   'asmo_708': 'iso8859_6', 
   'csisolatinarabic': 'iso8859_6', 
   'ecma_114': 'iso8859_6', 
   'iso_8859_6': 'iso8859_6', 
   'iso_8859_6_1987': 'iso8859_6', 
   'iso_ir_127': 'iso8859_6', 
   'csisolatingreek': 'iso8859_7', 
   'ecma_118': 'iso8859_7', 
   'elot_928': 'iso8859_7', 
   'greek': 'iso8859_7', 
   'greek8': 'iso8859_7', 
   'iso_8859_7': 'iso8859_7', 
   'iso_8859_7_1987': 'iso8859_7', 
   'iso_ir_126': 'iso8859_7', 
   'csisolatinhebrew': 'iso8859_8', 
   'hebrew': 'iso8859_8', 
   'iso_8859_8': 'iso8859_8', 
   'iso_8859_8_1988': 'iso8859_8', 
   'iso_ir_138': 'iso8859_8', 
   'csisolatin5': 'iso8859_9', 
   'iso_8859_9': 'iso8859_9', 
   'iso_8859_9_1989': 'iso8859_9', 
   'iso_ir_148': 'iso8859_9', 
   'l5': 'iso8859_9', 
   'latin5': 'iso8859_9', 
   'cp1361': 'johab', 
   'ms1361': 'johab', 
   'cskoi8r': 'koi8_r', 
   '8859': 'latin_1', 
   'cp819': 'latin_1', 
   'csisolatin1': 'latin_1', 
   'ibm819': 'latin_1', 
   'iso8859': 'latin_1', 
   'iso8859_1': 'latin_1', 
   'iso_8859_1': 'latin_1', 
   'iso_8859_1_1987': 'latin_1', 
   'iso_ir_100': 'latin_1', 
   'l1': 'latin_1', 
   'latin': 'latin_1', 
   'latin1': 'latin_1', 
   'maccyrillic': 'mac_cyrillic', 
   'macgreek': 'mac_greek', 
   'maciceland': 'mac_iceland', 
   'maccentraleurope': 'mac_latin2', 
   'maclatin2': 'mac_latin2', 
   'macroman': 'mac_roman', 
   'macturkish': 'mac_turkish', 
   'dbcs': 'mbcs', 
   'csptcp154': 'ptcp154', 
   'pt154': 'ptcp154', 
   'cp154': 'ptcp154', 
   'cyrillic_asian': 'ptcp154', 
   'quopri': 'quopri_codec', 
   'quoted_printable': 'quopri_codec', 
   'quotedprintable': 'quopri_codec', 
   'rot13': 'rot_13', 
   'csshiftjis': 'shift_jis', 
   'shiftjis': 'shift_jis', 
   'sjis': 'shift_jis', 
   's_jis': 'shift_jis', 
   'shiftjis2004': 'shift_jis_2004', 
   'sjis_2004': 'shift_jis_2004', 
   's_jis_2004': 'shift_jis_2004', 
   'shiftjisx0213': 'shift_jisx0213', 
   'sjisx0213': 'shift_jisx0213', 
   's_jisx0213': 'shift_jisx0213', 
   'tis260': 'tactis', 
   'tis620': 'tis_620', 
   'tis_620_0': 'tis_620', 
   'tis_620_2529_0': 'tis_620', 
   'tis_620_2529_1': 'tis_620', 
   'iso_ir_166': 'tis_620', 
   'u16': 'utf_16', 
   'utf16': 'utf_16', 
   'unicodebigunmarked': 'utf_16_be', 
   'utf_16be': 'utf_16_be', 
   'unicodelittleunmarked': 'utf_16_le', 
   'utf_16le': 'utf_16_le', 
   'u32': 'utf_32', 
   'utf32': 'utf_32', 
   'utf_32be': 'utf_32_be', 
   'utf_32le': 'utf_32_le', 
   'u7': 'utf_7', 
   'utf7': 'utf_7', 
   'unicode_1_1_utf_7': 'utf_7', 
   'u8': 'utf_8', 
   'utf': 'utf_8', 
   'utf8': 'utf_8', 
   'utf8_ucs2': 'utf_8', 
   'utf8_ucs4': 'utf_8', 
   'uu': 'uu_codec', 
   'zip': 'zlib_codec', 
   'zlib': 'zlib_codec'}