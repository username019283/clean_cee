# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\f2py\f2py2e.pyc
# Compiled at: 2013-04-07 07:04:04
"""

f2py2e - Fortran to Python C/API generator. 2nd Edition.
         See __usage__ below.

Copyright 1999--2011 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@cens.ioc.ee>
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2005/05/06 08:31:19 $
Pearu Peterson
"""
import __version__
f2py_version = __version__.version
import sys, os, pprint, types, re
errmess = sys.stderr.write
show = pprint.pprint
import crackfortran, rules, cb_rules, auxfuncs, cfuncs, f90mod_rules
outmess = auxfuncs.outmess
try:
    from numpy import __version__ as numpy_version
except ImportError:
    numpy_version = 'N/A'

__usage__ = "Usage:\n\n1) To construct extension module sources:\n\n      f2py [<options>] <fortran files> [[[only:]||[skip:]] \\\n                                        <fortran functions> ] \\\n                                       [: <fortran files> ...]\n\n2) To compile fortran files and build extension modules:\n\n      f2py -c [<options>, <build_flib options>, <extra options>] <fortran files>\n\n3) To generate signature files:\n\n      f2py -h <filename.pyf> ...< same options as in (1) >\n\nDescription: This program generates a Python C/API file (<modulename>module.c)\n             that contains wrappers for given fortran functions so that they\n             can be called from Python. With the -c option the corresponding\n             extension modules are built.\n\nOptions:\n\n  --2d-numpy       Use numpy.f2py tool with NumPy support. [DEFAULT]\n  --2d-numeric     Use f2py2e tool with Numeric support.\n  --2d-numarray    Use f2py2e tool with Numarray support.\n  --g3-numpy       Use 3rd generation f2py from the separate f2py package.\n                   [NOT AVAILABLE YET]\n\n  -h <filename>    Write signatures of the fortran routines to file <filename>\n                   and exit. You can then edit <filename> and use it instead\n                   of <fortran files>. If <filename>==stdout then the\n                   signatures are printed to stdout.\n  <fortran functions>  Names of fortran routines for which Python C/API\n                   functions will be generated. Default is all that are found\n                   in <fortran files>.\n  <fortran files>  Paths to fortran/signature files that will be scanned for\n                   <fortran functions> in order to determine their signatures.\n  skip:            Ignore fortran functions that follow until `:'.\n  only:            Use only fortran functions that follow until `:'.\n  :                Get back to <fortran files> mode.\n\n  -m <modulename>  Name of the module; f2py generates a Python/C API\n                   file <modulename>module.c or extension module <modulename>.\n                   Default is 'untitled'.\n\n  --[no-]lower     Do [not] lower the cases in <fortran files>. By default,\n                   --lower is assumed with -h key, and --no-lower without -h key.\n\n  --build-dir <dirname>  All f2py generated files are created in <dirname>.\n                   Default is tempfile.mktemp().\n\n  --overwrite-signature  Overwrite existing signature file.\n\n  --[no-]latex-doc Create (or not) <modulename>module.tex.\n                   Default is --no-latex-doc.\n  --short-latex    Create 'incomplete' LaTeX document (without commands\n                   \\documentclass, \\tableofcontents, and \\begin{document},\n                   \\end{document}).\n\n  --[no-]rest-doc Create (or not) <modulename>module.rst.\n                   Default is --no-rest-doc.\n\n  --debug-capi     Create C/API code that reports the state of the wrappers\n                   during runtime. Useful for debugging.\n\n  --[no-]wrap-functions    Create Fortran subroutine wrappers to Fortran 77\n                   functions. --wrap-functions is default because it ensures\n                   maximum portability/compiler independence.\n\n  --include-paths <path1>:<path2>:...   Search include files from the given\n                   directories.\n\n  --help-link [..] List system resources found by system_info.py. See also\n                   --link-<resource> switch below. [..] is optional list\n                   of resources names. E.g. try 'f2py --help-link lapack_opt'.\n\n  --quiet          Run quietly.\n  --verbose        Run with extra verbosity.\n  -v               Print f2py version ID and exit.\n\n\nnumpy.distutils options (only effective with -c):\n\n  --fcompiler=         Specify Fortran compiler type by vendor\n  --compiler=          Specify C compiler type (as defined by distutils)\n\n  --help-fcompiler     List available Fortran compilers and exit\n  --f77exec=           Specify the path to F77 compiler\n  --f90exec=           Specify the path to F90 compiler\n  --f77flags=          Specify F77 compiler flags\n  --f90flags=          Specify F90 compiler flags\n  --opt=               Specify optimization flags\n  --arch=              Specify architecture specific optimization flags\n  --noopt              Compile without optimization\n  --noarch             Compile without arch-dependent optimization\n  --debug              Compile with debugging information\n\nExtra options (only effective with -c):\n\n  --link-<resource>    Link extension module with <resource> as defined\n                       by numpy.distutils/system_info.py. E.g. to link\n                       with optimized LAPACK libraries (vecLib on MacOSX,\n                       ATLAS elsewhere), use --link-lapack_opt.\n                       See also --help-link switch.\n\n  -L/path/to/lib/ -l<libname>\n  -D<define> -U<name>\n  -I/path/to/include/\n  <filename>.o <filename>.so <filename>.a\n\n  Using the following macros may be required with non-gcc Fortran\n  compilers:\n    -DPREPEND_FORTRAN -DNO_APPEND_FORTRAN -DUPPERCASE_FORTRAN\n    -DUNDERSCORE_G77\n\n  When using -DF2PY_REPORT_ATEXIT, a performance report of F2PY\n  interface is printed out at exit (platforms: Linux).\n\n  When using -DF2PY_REPORT_ON_ARRAY_COPY=<int>, a message is\n  sent to stderr whenever F2PY interface makes a copy of an\n  array. Integer <int> sets the threshold for array sizes when\n  a message should be shown.\n\nVersion:     %s\nnumpy Version: %s\nRequires:    Python 2.3 or higher.\nLicense:     NumPy license (see LICENSE.txt in the NumPy source code)\nCopyright 1999 - 2011 Pearu Peterson all rights reserved.\nhttp://cens.ioc.ee/projects/f2py2e/" % (f2py_version, numpy_version)

def scaninputline(inputline):
    files, funcs, skipfuncs, onlyfuncs, debug = ([], [], [], [], [])
    f, f2, f3, f4, f5, f6, f7, f8, f9 = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    verbose = 1
    dolc = -1
    dolatexdoc = 0
    dorestdoc = 0
    wrapfuncs = 1
    buildpath = '.'
    include_paths = []
    signsfile, modulename = (None, None)
    options = {'buildpath': buildpath, 'coutput': None, 
       'f2py_wrapper_output': None}
    for l in inputline:
        if l == '':
            pass
        elif l == 'only:':
            f = 0
        elif l == 'skip:':
            f = -1
        elif l == ':':
            f = 1
            f4 = 0
        elif l[:8] == '--debug-':
            debug.append(l[8:])
        elif l == '--lower':
            dolc = 1
        elif l == '--build-dir':
            f6 = 1
        elif l == '--no-lower':
            dolc = 0
        elif l == '--quiet':
            verbose = 0
        elif l == '--verbose':
            verbose += 1
        elif l == '--latex-doc':
            dolatexdoc = 1
        elif l == '--no-latex-doc':
            dolatexdoc = 0
        elif l == '--rest-doc':
            dorestdoc = 1
        elif l == '--no-rest-doc':
            dorestdoc = 0
        elif l == '--wrap-functions':
            wrapfuncs = 1
        elif l == '--no-wrap-functions':
            wrapfuncs = 0
        elif l == '--short-latex':
            options['shortlatex'] = 1
        elif l == '--coutput':
            f8 = 1
        elif l == '--f2py-wrapper-output':
            f9 = 1
        elif l == '--overwrite-signature':
            options['h-overwrite'] = 1
        elif l == '-h':
            f2 = 1
        elif l == '-m':
            f3 = 1
        elif l[:2] == '-v':
            print f2py_version
            sys.exit()
        elif l == '--show-compilers':
            f5 = 1
        elif l[:8] == '-include':
            cfuncs.outneeds['userincludes'].append(l[9:-1])
            cfuncs.userincludes[l[9:-1]] = '#include ' + l[8:]
        elif l[:15] in '--include_paths':
            outmess('f2py option --include_paths is deprecated, use --include-paths instead.\n')
            f7 = 1
        elif l[:15] in '--include-paths':
            f7 = 1
        elif l[0] == '-':
            errmess('Unknown option %s\n' % `l`)
            sys.exit()
        elif f2:
            f2 = 0
            signsfile = l
        elif f3:
            f3 = 0
            modulename = l
        elif f6:
            f6 = 0
            buildpath = l
        elif f7:
            f7 = 0
            include_paths.extend(l.split(os.pathsep))
        elif f8:
            f8 = 0
            options['coutput'] = l
        elif f9:
            f9 = 0
            options['f2py_wrapper_output'] = l
        elif f == 1:
            try:
                open(l).close()
                files.append(l)
            except IOError as detail:
                errmess('IOError: %s. Skipping file "%s".\n' % (str(detail), l))

        elif f == -1:
            skipfuncs.append(l)
        elif f == 0:
            onlyfuncs.append(l)

    if not f5 and not files and not modulename:
        print __usage__
        sys.exit()
    if not os.path.isdir(buildpath):
        if not verbose:
            outmess('Creating build directory %s' % buildpath)
        os.mkdir(buildpath)
    if signsfile:
        signsfile = os.path.join(buildpath, signsfile)
    if signsfile and os.path.isfile(signsfile) and 'h-overwrite' not in options:
        errmess('Signature file "%s" exists!!! Use --overwrite-signature to overwrite.\n' % signsfile)
        sys.exit()
    options['debug'] = debug
    options['verbose'] = verbose
    if dolc == -1 and not signsfile:
        options['do-lower'] = 0
    else:
        options['do-lower'] = dolc
    if modulename:
        options['module'] = modulename
    if signsfile:
        options['signsfile'] = signsfile
    if onlyfuncs:
        options['onlyfuncs'] = onlyfuncs
    if skipfuncs:
        options['skipfuncs'] = skipfuncs
    options['dolatexdoc'] = dolatexdoc
    options['dorestdoc'] = dorestdoc
    options['wrapfuncs'] = wrapfuncs
    options['buildpath'] = buildpath
    options['include_paths'] = include_paths
    return (files, options)


def callcrackfortran(files, options):
    rules.options = options
    funcs = []
    crackfortran.debug = options['debug']
    crackfortran.verbose = options['verbose']
    if 'module' in options:
        crackfortran.f77modulename = options['module']
    if 'skipfuncs' in options:
        crackfortran.skipfuncs = options['skipfuncs']
    if 'onlyfuncs' in options:
        crackfortran.onlyfuncs = options['onlyfuncs']
    crackfortran.include_paths[:] = options['include_paths']
    crackfortran.dolowercase = options['do-lower']
    postlist = crackfortran.crackfortran(files)
    if 'signsfile' in options:
        outmess('Saving signatures to file "%s"\n' % options['signsfile'])
        pyf = crackfortran.crack2fortran(postlist)
        if options['signsfile'][-6:] == 'stdout':
            sys.stdout.write(pyf)
        else:
            f = open(options['signsfile'], 'w')
            f.write(pyf)
            f.close()
    if options['coutput'] is None:
        for mod in postlist:
            mod['coutput'] = '%smodule.c' % mod['name']

    else:
        for mod in postlist:
            mod['coutput'] = options['coutput']

        if options['f2py_wrapper_output'] is None:
            for mod in postlist:
                mod['f2py_wrapper_output'] = '%s-f2pywrappers.f' % mod['name']

        else:
            for mod in postlist:
                mod['f2py_wrapper_output'] = options['f2py_wrapper_output']

    return postlist


def buildmodules(lst):
    cfuncs.buildcfuncs()
    outmess('Building modules...\n')
    modules, mnames, isusedby = [], [], {}
    for i in range(len(lst)):
        if '__user__' in lst[i]['name']:
            cb_rules.buildcallbacks(lst[i])
        else:
            if 'use' in lst[i]:
                for u in lst[i]['use'].keys():
                    if u not in isusedby:
                        isusedby[u] = []
                    isusedby[u].append(lst[i]['name'])

            modules.append(lst[i])
            mnames.append(lst[i]['name'])

    ret = {}
    for i in range(len(mnames)):
        if mnames[i] in isusedby:
            outmess('\tSkipping module "%s" which is used by %s.\n' % (mnames[i], (',').join(map((lambda s: '"%s"' % s), isusedby[mnames[i]]))))
        else:
            um = []
            if 'use' in modules[i]:
                for u in modules[i]['use'].keys():
                    if u in isusedby and u in mnames:
                        um.append(modules[mnames.index(u)])
                    else:
                        outmess('\tModule "%s" uses nonexisting "%s" which will be ignored.\n' % (mnames[i], u))

            ret[mnames[i]] = {}
            dict_append(ret[mnames[i]], rules.buildmodule(modules[i], um))

    return ret


def dict_append(d_out, d_in):
    for k, v in d_in.items():
        if k not in d_out:
            d_out[k] = []
        if type(v) is types.ListType:
            d_out[k] = d_out[k] + v
        else:
            d_out[k].append(v)


def run_main(comline_list):
    """Run f2py as if string.join(comline_list,' ') is used as a command line.
    In case of using -h flag, return None.
    """
    if sys.version_info[0] >= 3:
        import imp
        imp.reload(crackfortran)
    else:
        reload(crackfortran)
    f2pydir = os.path.dirname(os.path.abspath(cfuncs.__file__))
    fobjhsrc = os.path.join(f2pydir, 'src', 'fortranobject.h')
    fobjcsrc = os.path.join(f2pydir, 'src', 'fortranobject.c')
    files, options = scaninputline(comline_list)
    auxfuncs.options = options
    postlist = callcrackfortran(files, options)
    isusedby = {}
    for i in range(len(postlist)):
        if 'use' in postlist[i]:
            for u in postlist[i]['use'].keys():
                if u not in isusedby:
                    isusedby[u] = []
                isusedby[u].append(postlist[i]['name'])

    for i in range(len(postlist)):
        if postlist[i]['block'] == 'python module' and '__user__' in postlist[i]['name']:
            if postlist[i]['name'] in isusedby:
                outmess('Skipping Makefile build for module "%s" which is used by %s\n' % (postlist[i]['name'], (',').join(map((lambda s: '"%s"' % s), isusedby[postlist[i]['name']]))))

    if 'signsfile' in options:
        if options['verbose'] > 1:
            outmess('Stopping. Edit the signature file and then run f2py on the signature file: ')
            outmess('%s %s\n' % (os.path.basename(sys.argv[0]), options['signsfile']))
        return
    for i in range(len(postlist)):
        if postlist[i]['block'] != 'python module':
            if 'python module' not in options:
                errmess('Tip: If your original code is Fortran source then you must use -m option.\n')
            raise TypeError('All blocks must be python module blocks but got %s' % `(postlist[i]['block'])`)

    auxfuncs.debugoptions = options['debug']
    f90mod_rules.options = options
    auxfuncs.wrapfuncs = options['wrapfuncs']
    ret = buildmodules(postlist)
    for mn in ret.keys():
        dict_append(ret[mn], {'csrc': fobjcsrc, 'h': fobjhsrc})

    return ret


def filter_files(prefix, suffix, files, remove_prefix=None):
    """
    Filter files by prefix and suffix.
    """
    filtered, rest = [], []
    match = re.compile(prefix + '.*' + suffix + '\\Z').match
    if remove_prefix:
        ind = len(prefix)
    else:
        ind = 0
    for file in [ x.strip() for x in files ]:
        if match(file):
            filtered.append(file[ind:])
        else:
            rest.append(file)

    return (
     filtered, rest)


def get_prefix(module):
    p = os.path.dirname(os.path.dirname(module.__file__))
    return p


def run_compile():
    """
    Do it all in one call!
    """
    import tempfile
    i = sys.argv.index('-c')
    del sys.argv[i]
    remove_build_dir = 0
    try:
        i = sys.argv.index('--build-dir')
    except ValueError:
        i = None

    if i is not None:
        build_dir = sys.argv[i + 1]
        del sys.argv[i + 1]
        del sys.argv[i]
    else:
        remove_build_dir = 1
        build_dir = os.path.join(tempfile.mktemp())
    sysinfo_flags = filter(re.compile('[-][-]link[-]').match, sys.argv[1:])
    sys.argv = filter((lambda a, flags=sysinfo_flags: a not in flags), sys.argv)
    if sysinfo_flags:
        sysinfo_flags = [ f[7:] for f in sysinfo_flags ]
    f2py_flags = filter(re.compile('[-][-]((no[-]|)(wrap[-]functions|lower)|debug[-]capi|quiet)|[-]include').match, sys.argv[1:])
    sys.argv = filter((lambda a, flags=f2py_flags: a not in flags), sys.argv)
    f2py_flags2 = []
    fl = 0
    for a in sys.argv[1:]:
        if a in ('only:', 'skip:'):
            fl = 1
        elif a == ':':
            fl = 0
        if fl or a == ':':
            f2py_flags2.append(a)

    if f2py_flags2 and f2py_flags2[-1] != ':':
        f2py_flags2.append(':')
    f2py_flags.extend(f2py_flags2)
    sys.argv = filter((lambda a, flags=f2py_flags2: a not in flags), sys.argv)
    flib_flags = filter(re.compile('[-][-]((f(90)?compiler([-]exec|)|compiler)=|help[-]compiler)').match, sys.argv[1:])
    sys.argv = filter((lambda a, flags=flib_flags: a not in flags), sys.argv)
    fc_flags = filter(re.compile('[-][-]((f(77|90)(flags|exec)|opt|arch)=|(debug|noopt|noarch|help[-]fcompiler))').match, sys.argv[1:])
    sys.argv = filter((lambda a, flags=fc_flags: a not in flags), sys.argv)
    del_list = []
    for s in flib_flags:
        v = '--fcompiler='
        if s[:len(v)] == v:
            from numpy.distutils import fcompiler
            fcompiler.load_all_fcompiler_classes()
            allowed_keys = fcompiler.fcompiler_class.keys()
            nv = ov = s[len(v):].lower()
            if ov not in allowed_keys:
                vmap = {}
                try:
                    nv = vmap[ov]
                except KeyError:
                    if ov not in vmap.values():
                        print 'Unknown vendor: "%s"' % s[len(v):]

                nv = ov
            i = flib_flags.index(s)
            flib_flags[i] = '--fcompiler=' + nv
            continue

    for s in del_list:
        i = flib_flags.index(s)
        del flib_flags[i]

    assert len(flib_flags) <= 2, `flib_flags`
    setup_flags = filter(re.compile('[-][-](verbose)').match, sys.argv[1:])
    sys.argv = filter((lambda a, flags=setup_flags: a not in flags), sys.argv)
    if '--quiet' in f2py_flags:
        setup_flags.append('--quiet')
    modulename = 'untitled'
    sources = sys.argv[1:]
    for optname in ['--include_paths', '--include-paths']:
        if optname in sys.argv:
            i = sys.argv.index(optname)
            f2py_flags.extend(sys.argv[i:i + 2])
            del sys.argv[i + 1]
            del sys.argv[i]
            sources = sys.argv[1:]

    if '-m' in sys.argv:
        i = sys.argv.index('-m')
        modulename = sys.argv[i + 1]
        del sys.argv[i + 1]
        del sys.argv[i]
        sources = sys.argv[1:]
    else:
        from numpy.distutils.command.build_src import get_f2py_modulename
        pyf_files, sources = filter_files('', '[.]pyf([.]src|)', sources)
        sources = pyf_files + sources
        for f in pyf_files:
            modulename = get_f2py_modulename(f)
            if modulename:
                break

        extra_objects, sources = filter_files('', '[.](o|a|so)', sources)
        include_dirs, sources = filter_files('-I', '', sources, remove_prefix=1)
        library_dirs, sources = filter_files('-L', '', sources, remove_prefix=1)
        libraries, sources = filter_files('-l', '', sources, remove_prefix=1)
        undef_macros, sources = filter_files('-U', '', sources, remove_prefix=1)
        define_macros, sources = filter_files('-D', '', sources, remove_prefix=1)
        using_numarray = 0
        using_numeric = 0
        for i in range(len(define_macros)):
            name_value = define_macros[i].split('=', 1)
            if len(name_value) == 1:
                name_value.append(None)
            if len(name_value) == 2:
                define_macros[i] = tuple(name_value)
            else:
                print 'Invalid use of -D:', name_value

    from numpy.distutils.system_info import get_info
    num_include_dir = None
    num_info = {}
    if num_info:
        include_dirs.extend(num_info.get('include_dirs', []))
    from numpy.distutils.core import setup, Extension
    ext_args = {'name': modulename, 'sources': sources, 'include_dirs': include_dirs, 
       'library_dirs': library_dirs, 
       'libraries': libraries, 
       'define_macros': define_macros, 
       'undef_macros': undef_macros, 
       'extra_objects': extra_objects, 
       'f2py_options': f2py_flags}
    if sysinfo_flags:
        from numpy.distutils.misc_util import dict_append
        for n in sysinfo_flags:
            i = get_info(n)
            if not i:
                outmess('No %s resources found in system (try `f2py --help-link`)\n' % `n`)
            dict_append(ext_args, **i)

    ext = Extension(**ext_args)
    sys.argv = [sys.argv[0]] + setup_flags
    sys.argv.extend(['build', 
     '--build-temp', 'build_dir', 
     '--build-base', 
     'build_dir', 
     '--build-platlib', '.'])
    if fc_flags:
        sys.argv.extend(['config_fc'] + fc_flags)
    if flib_flags:
        sys.argv.extend(['build_ext'] + flib_flags)
    setup(ext_modules=[ext])
    if remove_build_dir and os.path.exists(build_dir):
        import shutil
        outmess('Removing build directory %s\n' % build_dir)
        shutil.rmtree(build_dir)
    return


def main():
    if '--help-link' in sys.argv[1:]:
        sys.argv.remove('--help-link')
        from numpy.distutils.system_info import show_all
        show_all()
        return
    if '-c' in sys.argv[1:]:
        run_compile()
    else:
        run_main(sys.argv[1:])