# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: _MozillaCookieJar.pyc
# Compiled at: 2011-03-08 09:43:12
"""Mozilla / Netscape cookie loading / saving."""
import re, time
from cookielib import _warn_unhandled_exception, FileCookieJar, LoadError, Cookie, MISSING_FILENAME_TEXT

class MozillaCookieJar(FileCookieJar):
    """

    WARNING: you may want to backup your browser's cookies file if you use
    this class to save cookies.  I *think* it works, but there have been
    bugs in the past!

    This class differs from CookieJar only in the format it uses to save and
    load cookies to and from a file.  This class uses the Mozilla/Netscape
    `cookies.txt' format.  lynx uses this file format, too.

    Don't expect cookies saved while the browser is running to be noticed by
    the browser (in fact, Mozilla on unix will overwrite your saved cookies if
    you change them on disk while it's running; on Windows, you probably can't
    save at all while the browser is running).

    Note that the Mozilla/Netscape format will downgrade RFC2965 cookies to
    Netscape cookies on saving.

    In particular, the cookie version and port number information is lost,
    together with information about whether or not Path, Port and Discard were
    specified by the Set-Cookie2 (or Set-Cookie) header, and whether or not the
    domain as set in the HTTP header started with a dot (yes, I'm aware some
    domains in Netscape files start with a dot and some don't -- trust me, you
    really don't want to know any more about this).

    Note that though Mozilla and Netscape use the same format, they use
    slightly different headers.  The class saves cookies using the Netscape
    header by default (Mozilla can cope with that).

    """
    magic_re = '#( Netscape)? HTTP Cookie File'
    header = '# Netscape HTTP Cookie File\n# http://www.netscape.com/newsref/std/cookie_spec.html\n# This is a generated file!  Do not edit.\n\n'

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()
        magic = f.readline()
        if not re.search(self.magic_re, magic):
            f.close()
            raise LoadError('%r does not look like a Netscape format cookies file' % filename)
        try:
            while 1:
                line = f.readline()
                if line == '':
                    break
                if line.endswith('\n'):
                    line = line[:-1]
                if line.strip().startswith(('#', '$')) or line.strip() == '':
                    continue
                domain, domain_specified, path, secure, expires, name, value = line.split('\t')
                secure = secure == 'TRUE'
                domain_specified = domain_specified == 'TRUE'
                if name == '':
                    name = value
                    value = None
                initial_dot = domain.startswith('.')
                assert domain_specified == initial_dot
                discard = False
                if expires == '':
                    expires = None
                    discard = True
                c = Cookie(0, name, value, None, False, domain, domain_specified, initial_dot, path, False, secure, expires, discard, None, None, {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except IOError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError('invalid Netscape format cookies file %r: %r' % (
             filename, line))

        return

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        f = open(filename, 'w')
        try:
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard and cookie.discard:
                    continue
                if not ignore_expires and cookie.is_expired(now):
                    continue
                if cookie.secure:
                    secure = 'TRUE'
                else:
                    secure = 'FALSE'
                if cookie.domain.startswith('.'):
                    initial_dot = 'TRUE'
                else:
                    initial_dot = 'FALSE'
                if cookie.expires is not None:
                    expires = str(cookie.expires)
                else:
                    expires = ''
                if cookie.value is None:
                    name = ''
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write(('\t').join([cookie.domain, initial_dot, cookie.path,
                 secure, expires, name, value]) + '\n')

        finally:
            f.close()

        return