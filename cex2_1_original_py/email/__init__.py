# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: email\__init__.pyc
# Compiled at: 2011-03-08 09:43:14
"""A package for parsing, handling, and generating email messages."""
__version__ = '4.0.3'
__all__ = [
 'base64MIME', 
 'Charset', 
 'Encoders', 
 'Errors', 
 'Generator', 
 'Header', 
 'Iterators', 
 'Message', 
 'MIMEAudio', 
 'MIMEBase', 
 'MIMEImage', 
 'MIMEMessage', 
 'MIMEMultipart', 
 'MIMENonMultipart', 
 'MIMEText', 
 'Parser', 
 'quopriMIME', 
 'Utils', 
 'message_from_string', 
 'message_from_file', 
 'base64mime', 
 'charset', 
 'encoders', 
 'errors', 
 'generator', 
 'header', 
 'iterators', 
 'message', 
 'mime', 
 'parser', 
 'quoprimime', 
 'utils']

def message_from_string(s, *args, **kws):
    """Parse a string into a Message object model.

    Optional _class and strict are passed to the Parser constructor.
    """
    from email.parser import Parser
    return Parser(*args, **kws).parsestr(s)


def message_from_file(fp, *args, **kws):
    """Read a file and parse its contents into a Message object model.

    Optional _class and strict are passed to the Parser constructor.
    """
    from email.parser import Parser
    return Parser(*args, **kws).parse(fp)


import sys

class LazyImporter(object):

    def __init__(self, module_name):
        self.__name__ = 'email.' + module_name

    def __getattr__(self, name):
        __import__(self.__name__)
        mod = sys.modules[self.__name__]
        self.__dict__.update(mod.__dict__)
        return getattr(mod, name)


_LOWERNAMES = [
 'Charset', 
 'Encoders', 
 'Errors', 
 'FeedParser', 
 'Generator', 
 'Header', 
 'Iterators', 
 'Message', 
 'Parser', 
 'Utils', 
 'base64MIME', 
 'quopriMIME']
_MIMENAMES = [
 'Audio', 
 'Base', 
 'Image', 
 'Message', 
 'Multipart', 
 'NonMultipart', 
 'Text']
for _name in _LOWERNAMES:
    importer = LazyImporter(_name.lower())
    sys.modules['email.' + _name] = importer
    setattr(sys.modules['email'], _name, importer)

import email.mime
for _name in _MIMENAMES:
    importer = LazyImporter('mime.' + _name.lower())
    sys.modules['email.MIME' + _name] = importer
    setattr(sys.modules['email'], 'MIME' + _name, importer)
    setattr(sys.modules['email.mime'], _name, importer)