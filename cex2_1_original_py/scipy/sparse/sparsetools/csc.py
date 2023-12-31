# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\sparsetools\csc.pyc
# Compiled at: 2013-02-16 13:27:02
from sys import version_info
if version_info >= (2, 6, 0):

    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_csc', [dirname(__file__)])
        except ImportError:
            import _csc
            return _csc

        if fp is not None:
            try:
                _mod = imp.load_module('_csc', fp, pathname, description)
            finally:
                fp.close()

            return _mod
        else:
            return


    _csc = swig_import_helper()
    del swig_import_helper
else:
    import _csc
del version_info
try:
    _swig_property = property
except NameError:
    pass

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if name == 'thisown':
        return self.this.own(value)
    else:
        if name == 'this':
            if type(value).__name__ == 'SwigPyObject':
                self.__dict__[name] = value
                return
        method = class_type.__swig_setmethods__.get(name, None)
        if method:
            return method(self, value)
        if not static:
            self.__dict__[name] = value
        else:
            raise AttributeError('You cannot add attributes to %s' % self)
        return


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if name == 'thisown':
        return self.this.own()
    else:
        method = class_type.__swig_getmethods__.get(name, None)
        if method:
            return method(self)
        raise AttributeError(name)
        return


def _swig_repr(self):
    try:
        strthis = 'proxy of ' + self.this.__repr__()
    except:
        strthis = ''

    return '<%s.%s; %s >' % (self.__class__.__module__, self.__class__.__name__, strthis)


try:
    _object = object
    _newclass = 1
except AttributeError:

    class _object:
        pass


    _newclass = 0

def csc_matmat_pass1(*args):
    """
    csc_matmat_pass1(int n_row, int n_col, int Ap, int Ai, int Bp, int Bi, 
        int Cp)
    """
    return _csc.csc_matmat_pass1(*args)


def csc_diagonal(*args):
    """
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, signed char Ax, 
        signed char Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, unsigned char Ax, 
        unsigned char Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, short Ax, short Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, unsigned short Ax, 
        unsigned short Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, int Ax, int Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, unsigned int Ax, 
        unsigned int Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, long long Ax, 
        long long Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, unsigned long long Ax, 
        unsigned long long Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, float Ax, float Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, double Ax, double Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, long double Ax, 
        long double Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, npy_cfloat_wrapper Ax, 
        npy_cfloat_wrapper Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, npy_cdouble_wrapper Ax, 
        npy_cdouble_wrapper Yx)
    csc_diagonal(int n_row, int n_col, int Ap, int Aj, npy_clongdouble_wrapper Ax, 
        npy_clongdouble_wrapper Yx)
    """
    return _csc.csc_diagonal(*args)


def csc_tocsr(*args):
    """
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bj, signed char Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bj, unsigned char Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bj, short Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bj, unsigned short Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bj, int Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bj, unsigned int Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bj, long long Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bj, unsigned long long Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bj, float Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bj, double Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bj, long double Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bj, npy_cfloat_wrapper Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bj, npy_cdouble_wrapper Bx)
    csc_tocsr(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bj, npy_clongdouble_wrapper Bx)
    """
    return _csc.csc_tocsr(*args)


def csc_matmat_pass2(*args):
    """
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bi, signed char Bx, int Cp, int Ci, 
        signed char Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bi, unsigned char Bx, int Cp, 
        int Ci, unsigned char Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bi, short Bx, int Cp, int Ci, short Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bi, unsigned short Bx, int Cp, 
        int Ci, unsigned short Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bi, int Bx, int Cp, int Ci, int Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bi, unsigned int Bx, int Cp, 
        int Ci, unsigned int Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bi, long long Bx, int Cp, int Ci, 
        long long Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bi, unsigned long long Bx, 
        int Cp, int Ci, unsigned long long Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bi, float Bx, int Cp, int Ci, float Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bi, double Bx, int Cp, int Ci, double Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bi, long double Bx, int Cp, int Ci, 
        long double Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bi, npy_cfloat_wrapper Bx, 
        int Cp, int Ci, npy_cfloat_wrapper Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bi, npy_cdouble_wrapper Bx, 
        int Cp, int Ci, npy_cdouble_wrapper Cx)
    csc_matmat_pass2(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bi, npy_clongdouble_wrapper Bx, 
        int Cp, int Ci, npy_clongdouble_wrapper Cx)
    """
    return _csc.csc_matmat_pass2(*args)


def csc_matvec(*args):
    """
    csc_matvec(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        signed char Xx, signed char Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        unsigned char Xx, unsigned char Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, short Ax, short Xx, 
        short Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        unsigned short Xx, unsigned short Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, int Ax, int Xx, 
        int Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        unsigned int Xx, unsigned int Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        long long Xx, long long Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        unsigned long long Xx, unsigned long long Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, float Ax, float Xx, 
        float Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, double Ax, double Xx, 
        double Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        long double Xx, long double Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        npy_cfloat_wrapper Xx, npy_cfloat_wrapper Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        npy_cdouble_wrapper Xx, npy_cdouble_wrapper Yx)
    csc_matvec(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        npy_clongdouble_wrapper Xx, npy_clongdouble_wrapper Yx)
    """
    return _csc.csc_matvec(*args)


def csc_matvecs(*args):
    """
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, signed char Ax, 
        signed char Xx, signed char Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, unsigned char Ax, 
        unsigned char Xx, unsigned char Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, short Ax, 
        short Xx, short Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, unsigned short Ax, 
        unsigned short Xx, unsigned short Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, int Ax, 
        int Xx, int Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, unsigned int Ax, 
        unsigned int Xx, unsigned int Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, long long Ax, 
        long long Xx, long long Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, unsigned long long Ax, 
        unsigned long long Xx, 
        unsigned long long Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, float Ax, 
        float Xx, float Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, double Ax, 
        double Xx, double Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, long double Ax, 
        long double Xx, long double Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        npy_cfloat_wrapper Xx, 
        npy_cfloat_wrapper Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        npy_cdouble_wrapper Xx, 
        npy_cdouble_wrapper Yx)
    csc_matvecs(int n_row, int n_col, int n_vecs, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        npy_clongdouble_wrapper Xx, 
        npy_clongdouble_wrapper Yx)
    """
    return _csc.csc_matvecs(*args)


def csc_elmul_csc(*args):
    """
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bi, signed char Bx, int Cp, int Ci, 
        signed char Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bi, unsigned char Bx, int Cp, 
        int Ci, unsigned char Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bi, short Bx, int Cp, int Ci, short Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bi, unsigned short Bx, int Cp, 
        int Ci, unsigned short Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bi, int Bx, int Cp, int Ci, int Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bi, unsigned int Bx, int Cp, 
        int Ci, unsigned int Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bi, long long Bx, int Cp, int Ci, 
        long long Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bi, unsigned long long Bx, 
        int Cp, int Ci, unsigned long long Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bi, float Bx, int Cp, int Ci, float Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bi, double Bx, int Cp, int Ci, double Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bi, long double Bx, int Cp, int Ci, 
        long double Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bi, npy_cfloat_wrapper Bx, 
        int Cp, int Ci, npy_cfloat_wrapper Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bi, npy_cdouble_wrapper Bx, 
        int Cp, int Ci, npy_cdouble_wrapper Cx)
    csc_elmul_csc(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bi, npy_clongdouble_wrapper Bx, 
        int Cp, int Ci, npy_clongdouble_wrapper Cx)
    """
    return _csc.csc_elmul_csc(*args)


def csc_eldiv_csc(*args):
    """
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bi, signed char Bx, int Cp, int Ci, 
        signed char Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bi, unsigned char Bx, int Cp, 
        int Ci, unsigned char Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bi, short Bx, int Cp, int Ci, short Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bi, unsigned short Bx, int Cp, 
        int Ci, unsigned short Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bi, int Bx, int Cp, int Ci, int Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bi, unsigned int Bx, int Cp, 
        int Ci, unsigned int Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bi, long long Bx, int Cp, int Ci, 
        long long Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bi, unsigned long long Bx, 
        int Cp, int Ci, unsigned long long Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bi, float Bx, int Cp, int Ci, float Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bi, double Bx, int Cp, int Ci, double Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bi, long double Bx, int Cp, int Ci, 
        long double Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bi, npy_cfloat_wrapper Bx, 
        int Cp, int Ci, npy_cfloat_wrapper Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bi, npy_cdouble_wrapper Bx, 
        int Cp, int Ci, npy_cdouble_wrapper Cx)
    csc_eldiv_csc(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bi, npy_clongdouble_wrapper Bx, 
        int Cp, int Ci, npy_clongdouble_wrapper Cx)
    """
    return _csc.csc_eldiv_csc(*args)


def csc_plus_csc(*args):
    """
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bi, signed char Bx, int Cp, int Ci, 
        signed char Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bi, unsigned char Bx, int Cp, 
        int Ci, unsigned char Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bi, short Bx, int Cp, int Ci, short Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bi, unsigned short Bx, int Cp, 
        int Ci, unsigned short Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bi, int Bx, int Cp, int Ci, int Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bi, unsigned int Bx, int Cp, 
        int Ci, unsigned int Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bi, long long Bx, int Cp, int Ci, 
        long long Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bi, unsigned long long Bx, 
        int Cp, int Ci, unsigned long long Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bi, float Bx, int Cp, int Ci, float Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bi, double Bx, int Cp, int Ci, double Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bi, long double Bx, int Cp, int Ci, 
        long double Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bi, npy_cfloat_wrapper Bx, 
        int Cp, int Ci, npy_cfloat_wrapper Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bi, npy_cdouble_wrapper Bx, 
        int Cp, int Ci, npy_cdouble_wrapper Cx)
    csc_plus_csc(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bi, npy_clongdouble_wrapper Bx, 
        int Cp, int Ci, npy_clongdouble_wrapper Cx)
    """
    return _csc.csc_plus_csc(*args)


def csc_minus_csc(*args):
    """
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, signed char Ax, 
        int Bp, int Bi, signed char Bx, int Cp, int Ci, 
        signed char Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, unsigned char Ax, 
        int Bp, int Bi, unsigned char Bx, int Cp, 
        int Ci, unsigned char Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, short Ax, int Bp, 
        int Bi, short Bx, int Cp, int Ci, short Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, unsigned short Ax, 
        int Bp, int Bi, unsigned short Bx, int Cp, 
        int Ci, unsigned short Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, int Ax, int Bp, 
        int Bi, int Bx, int Cp, int Ci, int Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, unsigned int Ax, 
        int Bp, int Bi, unsigned int Bx, int Cp, 
        int Ci, unsigned int Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, long long Ax, 
        int Bp, int Bi, long long Bx, int Cp, int Ci, 
        long long Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, unsigned long long Ax, 
        int Bp, int Bi, unsigned long long Bx, 
        int Cp, int Ci, unsigned long long Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, float Ax, int Bp, 
        int Bi, float Bx, int Cp, int Ci, float Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, double Ax, int Bp, 
        int Bi, double Bx, int Cp, int Ci, double Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, long double Ax, 
        int Bp, int Bi, long double Bx, int Cp, int Ci, 
        long double Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, npy_cfloat_wrapper Ax, 
        int Bp, int Bi, npy_cfloat_wrapper Bx, 
        int Cp, int Ci, npy_cfloat_wrapper Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, npy_cdouble_wrapper Ax, 
        int Bp, int Bi, npy_cdouble_wrapper Bx, 
        int Cp, int Ci, npy_cdouble_wrapper Cx)
    csc_minus_csc(int n_row, int n_col, int Ap, int Ai, npy_clongdouble_wrapper Ax, 
        int Bp, int Bi, npy_clongdouble_wrapper Bx, 
        int Cp, int Ci, npy_clongdouble_wrapper Cx)
    """
    return _csc.csc_minus_csc(*args)