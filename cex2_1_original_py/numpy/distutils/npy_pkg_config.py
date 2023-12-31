# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\npy_pkg_config.pyc
# Compiled at: 2013-04-07 07:04:04
import sys
if sys.version_info[0] < 3:
    from ConfigParser import SafeConfigParser, NoOptionError
else:
    from configparser import ConfigParser, SafeConfigParser, NoOptionError
import re, os, shlex
__all__ = [
 'FormatError', 'PkgNotFound', 'LibraryInfo', 'VariableSet', 
 'read_config', 
 'parse_flags']
_VAR = re.compile('\\$\\{([a-zA-Z0-9_-]+)\\}')

class FormatError(IOError):
    """
    Exception thrown when there is a problem parsing a configuration file.

    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PkgNotFound(IOError):
    """Exception raised when a package can not be located."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def parse_flags(line):
    """
    Parse a line from a config file containing compile flags.

    Parameters
    ----------
    line : str
        A single line containing one or more compile flags.

    Returns
    -------
    d : dict
        Dictionary of parsed flags, split into relevant categories.
        These categories are the keys of `d`:

        * 'include_dirs'
        * 'library_dirs'
        * 'libraries'
        * 'macros'
        * 'ignored'

    """
    lexer = shlex.shlex(line)
    lexer.whitespace_split = True
    d = {'include_dirs': [], 'library_dirs': [], 'libraries': [], 'macros': [], 'ignored': []}

    def next_token(t):
        if t.startswith('-I'):
            if len(t) > 2:
                d['include_dirs'].append(t[2:])
            else:
                t = lexer.get_token()
                d['include_dirs'].append(t)
        elif t.startswith('-L'):
            if len(t) > 2:
                d['library_dirs'].append(t[2:])
            else:
                t = lexer.get_token()
                d['library_dirs'].append(t)
        elif t.startswith('-l'):
            d['libraries'].append(t[2:])
        elif t.startswith('-D'):
            d['macros'].append(t[2:])
        else:
            d['ignored'].append(t)
        return lexer.get_token()

    t = lexer.get_token()
    while t:
        t = next_token(t)

    return d


def _escape_backslash(val):
    return val.replace('\\', '\\\\')


class LibraryInfo(object):
    """
    Object containing build information about a library.

    Parameters
    ----------
    name : str
        The library name.
    description : str
        Description of the library.
    version : str
        Version string.
    sections : dict
        The sections of the configuration file for the library. The keys are
        the section headers, the values the text under each header.
    vars : class instance
        A `VariableSet` instance, which contains ``(name, value)`` pairs for
        variables defined in the configuration file for the library.
    requires : sequence, optional
        The required libraries for the library to be installed.

    Notes
    -----
    All input parameters (except "sections" which is a method) are available as
    attributes of the same name.

    """

    def __init__(self, name, description, version, sections, vars, requires=None):
        self.name = name
        self.description = description
        if requires:
            self.requires = requires
        else:
            self.requires = []
        self.version = version
        self._sections = sections
        self.vars = vars

    def sections(self):
        """
        Return the section headers of the config file.

        Parameters
        ----------
        None

        Returns
        -------
        keys : list of str
            The list of section headers.

        """
        return self._sections.keys()

    def cflags(self, section='default'):
        val = self.vars.interpolate(self._sections[section]['cflags'])
        return _escape_backslash(val)

    def libs(self, section='default'):
        val = self.vars.interpolate(self._sections[section]['libs'])
        return _escape_backslash(val)

    def __str__(self):
        m = [
         'Name: %s' % self.name]
        m.append('Description: %s' % self.description)
        if self.requires:
            m.append('Requires:')
        else:
            m.append('Requires: %s' % (',').join(self.requires))
        m.append('Version: %s' % self.version)
        return ('\n').join(m)


class VariableSet(object):
    """
    Container object for the variables defined in a config file.

    `VariableSet` can be used as a plain dictionary, with the variable names
    as keys.

    Parameters
    ----------
    d : dict
        Dict of items in the "variables" section of the configuration file.

    """

    def __init__(self, d):
        self._raw_data = dict([ (k, v) for k, v in d.items() ])
        self._re = {}
        self._re_sub = {}
        self._init_parse()

    def _init_parse(self):
        for k, v in self._raw_data.items():
            self._init_parse_var(k, v)

    def _init_parse_var(self, name, value):
        self._re[name] = re.compile('\\$\\{%s\\}' % name)
        self._re_sub[name] = value

    def interpolate(self, value):

        def _interpolate(value):
            for k in self._re.keys():
                value = self._re[k].sub(self._re_sub[k], value)

            return value

        while _VAR.search(value):
            nvalue = _interpolate(value)
            if nvalue == value:
                break
            value = nvalue

        return value

    def variables(self):
        """
        Return the list of variable names.

        Parameters
        ----------
        None

        Returns
        -------
        names : list of str
            The names of all variables in the `VariableSet` instance.

        """
        return self._raw_data.keys()

    def __getitem__(self, name):
        return self._raw_data[name]

    def __setitem__(self, name, value):
        self._raw_data[name] = value
        self._init_parse_var(name, value)


def parse_meta(config):
    if not config.has_section('meta'):
        raise FormatError('No meta section found !')
    d = {}
    for name, value in config.items('meta'):
        d[name] = value

    for k in ['name', 'description', 'version']:
        if not d.has_key(k):
            raise FormatError('Option %s (section [meta]) is mandatory, but not found' % k)

    if not d.has_key('requires'):
        d['requires'] = []
    return d


def parse_variables(config):
    if not config.has_section('variables'):
        raise FormatError('No variables section found !')
    d = {}
    for name, value in config.items('variables'):
        d[name] = value

    return VariableSet(d)


def parse_sections(config):
    return (
     meta_d, r)


def pkg_to_filename(pkg_name):
    return '%s.ini' % pkg_name


def parse_config(filename, dirs=None):
    if dirs:
        filenames = [ os.path.join(d, filename) for d in dirs ]
    else:
        filenames = [
         filename]
    if sys.version[:3] > '3.1':
        config = ConfigParser()
    else:
        config = SafeConfigParser()
    n = config.read(filenames)
    if not len(n) >= 1:
        raise PkgNotFound('Could not find file(s) %s' % str(filenames))
    meta = parse_meta(config)
    vars = {}
    if config.has_section('variables'):
        for name, value in config.items('variables'):
            vars[name] = _escape_backslash(value)

    secs = [ s for s in config.sections() if s not in ('meta', 'variables') ]
    sections = {}
    requires = {}
    for s in secs:
        d = {}
        if config.has_option(s, 'requires'):
            requires[s] = config.get(s, 'requires')
        for name, value in config.items(s):
            d[name] = value

        sections[s] = d

    return (meta, vars, sections, requires)


def _read_config_imp(filenames, dirs=None):

    def _read_config(f):
        meta, vars, sections, reqs = parse_config(f, dirs)
        for rname, rvalue in reqs.items():
            nmeta, nvars, nsections, nreqs = _read_config(pkg_to_filename(rvalue))
            for k, v in nvars.items():
                if not vars.has_key(k):
                    vars[k] = v

            for oname, ovalue in nsections[rname].items():
                if ovalue:
                    sections[rname][oname] += ' %s' % ovalue

        return (
         meta, vars, sections, reqs)

    meta, vars, sections, reqs = _read_config(filenames)
    if not vars.has_key('pkgdir') and vars.has_key('pkgname'):
        pkgname = vars['pkgname']
        if pkgname not in sys.modules:
            raise ValueError('You should import %s to get information on %s' % (
             pkgname, meta['name']))
        mod = sys.modules[pkgname]
        vars['pkgdir'] = _escape_backslash(os.path.dirname(mod.__file__))
    return LibraryInfo(name=meta['name'], description=meta['description'], version=meta['version'], sections=sections, vars=VariableSet(vars))


_CACHE = {}

def read_config(pkgname, dirs=None):
    """
    Return library info for a package from its configuration file.

    Parameters
    ----------
    pkgname : str
        Name of the package (should match the name of the .ini file, without
        the extension, e.g. foo for the file foo.ini).
    dirs : sequence, optional
        If given, should be a sequence of directories - usually including
        the NumPy base directory - where to look for npy-pkg-config files.

    Returns
    -------
    pkginfo : class instance
        The `LibraryInfo` instance containing the build information.

    Raises
    ------
    PkgNotFound
        If the package is not found.

    See Also
    --------
    misc_util.get_info, misc_util.get_pkg_info

    Examples
    --------
    >>> npymath_info = np.distutils.npy_pkg_config.read_config('npymath')
    >>> type(npymath_info)
    <class 'numpy.distutils.npy_pkg_config.LibraryInfo'>
    >>> print npymath_info
    Name: npymath
    Description: Portable, core math library implementing C99 standard
    Requires:
    Version: 0.1  #random

    """
    try:
        return _CACHE[pkgname]
    except KeyError:
        v = _read_config_imp(pkg_to_filename(pkgname), dirs)
        _CACHE[pkgname] = v
        return v


if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    import glob
    parser = OptionParser()
    parser.add_option('--cflags', dest='cflags', action='store_true', help='output all preprocessor and compiler flags')
    parser.add_option('--libs', dest='libs', action='store_true', help='output all linker flags')
    parser.add_option('--use-section', dest='section', help='use this section instead of default for options')
    parser.add_option('--version', dest='version', action='store_true', help='output version')
    parser.add_option('--atleast-version', dest='min_version', help='Minimal version')
    parser.add_option('--list-all', dest='list_all', action='store_true', help='Minimal version')
    parser.add_option('--define-variable', dest='define_variable', help='Replace variable with the given value')
    options, args = parser.parse_args(sys.argv)
    if len(args) < 2:
        raise ValueError('Expect package name on the command line:')
    if options.list_all:
        files = glob.glob('*.ini')
        for f in files:
            info = read_config(f)
            print '%s\t%s - %s' % (info.name, info.name, info.description)

    pkg_name = args[1]
    import os
    d = os.environ.get('NPY_PKG_CONFIG_PATH')
    if d:
        info = read_config(pkg_name, ['numpy/core/lib/npy-pkg-config', '.', d])
    else:
        info = read_config(pkg_name, ['numpy/core/lib/npy-pkg-config', '.'])
    if options.section:
        section = options.section
    else:
        section = 'default'
    if options.define_variable:
        m = re.search('([\\S]+)=([\\S]+)', options.define_variable)
        if not m:
            raise ValueError('--define-variable option should be of the form --define-variable=foo=bar')
        else:
            name = m.group(1)
            value = m.group(2)
        info.vars[name] = value
    if options.cflags:
        print info.cflags(section)
    if options.libs:
        print info.libs(section)
    if options.version:
        print info.version
    if options.min_version:
        print info.version >= options.min_version