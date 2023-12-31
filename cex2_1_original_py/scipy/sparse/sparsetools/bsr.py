# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\sparse\sparsetools\bsr.pyc
# Compiled at: 2013-02-16 13:27:02
from sys import version_info
if version_info >= (2, 6, 0):

    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_bsr', [dirname(__file__)])
        except ImportError:
            import _bsr
            return _bsr

        if fp is not None:
            try:
                _mod = imp.load_module('_bsr', fp, pathname, description)
            finally:
                fp.close()

            return _mod
        else:
            return


    _bsr = swig_import_helper()
    del swig_import_helper
else:
    import _bsr
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

def bsr_diagonal(*args):
    """
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax, signed char Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax, unsigned char Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax, short Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax, unsigned short Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax, int Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax, unsigned int Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax, long long Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, unsigned long long Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax, float Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax, double Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax, long double Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, npy_cfloat_wrapper Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, npy_cdouble_wrapper Yx)
    bsr_diagonal(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, npy_clongdouble_wrapper Yx)
    """
    return _bsr.bsr_diagonal(*args)


def bsr_scale_rows(*args):
    """
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax, signed char Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax, unsigned char Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax, short Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax, unsigned short Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax, int Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax, unsigned int Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax, long long Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, unsigned long long Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax, float Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax, double Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax, long double Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, npy_cfloat_wrapper Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, npy_cdouble_wrapper Xx)
    bsr_scale_rows(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, npy_clongdouble_wrapper Xx)
    """
    return _bsr.bsr_scale_rows(*args)


def bsr_scale_columns(*args):
    """
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax, signed char Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax, unsigned char Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax, short Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax, unsigned short Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax, int Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax, unsigned int Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax, long long Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, unsigned long long Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax, float Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax, double Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax, long double Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, npy_cfloat_wrapper Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, npy_cdouble_wrapper Xx)
    bsr_scale_columns(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, npy_clongdouble_wrapper Xx)
    """
    return _bsr.bsr_scale_columns(*args)


def bsr_transpose(*args):
    """
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax, int Bp, int Bj, signed char Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax, int Bp, int Bj, unsigned char Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax, int Bp, int Bj, short Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax, int Bp, int Bj, unsigned short Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax, int Bp, int Bj, int Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax, int Bp, int Bj, unsigned int Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax, int Bp, int Bj, long long Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, int Bp, int Bj, unsigned long long Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax, int Bp, int Bj, float Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax, int Bp, int Bj, double Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax, int Bp, int Bj, long double Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, int Bp, int Bj, npy_cfloat_wrapper Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, int Bp, int Bj, npy_cdouble_wrapper Bx)
    bsr_transpose(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, int Bp, int Bj, 
        npy_clongdouble_wrapper Bx)
    """
    return _bsr.bsr_transpose(*args)


def bsr_matmat_pass2(*args):
    """
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, signed char Ax, int Bp, int Bj, signed char Bx, 
        int Cp, int Cj, signed char Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, unsigned char Ax, int Bp, int Bj, unsigned char Bx, 
        int Cp, int Cj, unsigned char Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, short Ax, int Bp, int Bj, short Bx, 
        int Cp, int Cj, short Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, unsigned short Ax, int Bp, int Bj, 
        unsigned short Bx, int Cp, int Cj, unsigned short Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, int Ax, int Bp, int Bj, int Bx, int Cp, 
        int Cj, int Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, unsigned int Ax, int Bp, int Bj, unsigned int Bx, 
        int Cp, int Cj, unsigned int Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, long long Ax, int Bp, int Bj, long long Bx, 
        int Cp, int Cj, long long Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, unsigned long long Ax, int Bp, int Bj, 
        unsigned long long Bx, int Cp, int Cj, unsigned long long Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, float Ax, int Bp, int Bj, float Bx, 
        int Cp, int Cj, float Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, double Ax, int Bp, int Bj, double Bx, 
        int Cp, int Cj, double Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, long double Ax, int Bp, int Bj, long double Bx, 
        int Cp, int Cj, long double Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, npy_cfloat_wrapper Ax, int Bp, int Bj, 
        npy_cfloat_wrapper Bx, int Cp, int Cj, npy_cfloat_wrapper Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, npy_cdouble_wrapper Ax, int Bp, int Bj, 
        npy_cdouble_wrapper Bx, int Cp, int Cj, 
        npy_cdouble_wrapper Cx)
    bsr_matmat_pass2(int n_brow, int n_bcol, int R, int C, int N, int Ap, 
        int Aj, npy_clongdouble_wrapper Ax, int Bp, 
        int Bj, npy_clongdouble_wrapper Bx, int Cp, 
        int Cj, npy_clongdouble_wrapper Cx)
    """
    return _bsr.bsr_matmat_pass2(*args)


def bsr_matvec(*args):
    """
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax, signed char Xx, signed char Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax, unsigned char Xx, unsigned char Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax, short Xx, short Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax, unsigned short Xx, unsigned short Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax, int Xx, int Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax, unsigned int Xx, unsigned int Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax, long long Xx, long long Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, unsigned long long Xx, 
        unsigned long long Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax, float Xx, float Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax, double Xx, double Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax, long double Xx, long double Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, npy_cfloat_wrapper Xx, 
        npy_cfloat_wrapper Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, npy_cdouble_wrapper Xx, 
        npy_cdouble_wrapper Yx)
    bsr_matvec(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, npy_clongdouble_wrapper Xx, 
        npy_clongdouble_wrapper Yx)
    """
    return _bsr.bsr_matvec(*args)


def bsr_matvecs(*args):
    """
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, signed char Ax, signed char Xx, 
        signed char Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, unsigned char Ax, unsigned char Xx, 
        unsigned char Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, short Ax, short Xx, short Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, unsigned short Ax, unsigned short Xx, 
        unsigned short Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, int Ax, int Xx, int Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, unsigned int Ax, unsigned int Xx, 
        unsigned int Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, long long Ax, long long Xx, long long Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, unsigned long long Ax, unsigned long long Xx, 
        unsigned long long Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, float Ax, float Xx, float Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, double Ax, double Xx, double Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, long double Ax, long double Xx, 
        long double Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, npy_cfloat_wrapper Ax, npy_cfloat_wrapper Xx, 
        npy_cfloat_wrapper Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, npy_cdouble_wrapper Ax, npy_cdouble_wrapper Xx, 
        npy_cdouble_wrapper Yx)
    bsr_matvecs(int n_brow, int n_bcol, int n_vecs, int R, int C, int Ap, 
        int Aj, npy_clongdouble_wrapper Ax, npy_clongdouble_wrapper Xx, 
        npy_clongdouble_wrapper Yx)
    """
    return _bsr.bsr_matvecs(*args)


def bsr_elmul_bsr(*args):
    """
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        signed char Ax, int Bp, int Bj, signed char Bx, 
        int Cp, int Cj, signed char Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned char Ax, int Bp, int Bj, unsigned char Bx, 
        int Cp, int Cj, unsigned char Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        short Ax, int Bp, int Bj, short Bx, int Cp, 
        int Cj, short Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned short Ax, int Bp, int Bj, unsigned short Bx, 
        int Cp, int Cj, unsigned short Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        int Ax, int Bp, int Bj, int Bx, int Cp, int Cj, 
        int Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned int Ax, int Bp, int Bj, unsigned int Bx, 
        int Cp, int Cj, unsigned int Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long long Ax, int Bp, int Bj, long long Bx, 
        int Cp, int Cj, long long Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, int Bp, int Bj, unsigned long long Bx, 
        int Cp, int Cj, unsigned long long Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        float Ax, int Bp, int Bj, float Bx, int Cp, 
        int Cj, float Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        double Ax, int Bp, int Bj, double Bx, int Cp, 
        int Cj, double Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long double Ax, int Bp, int Bj, long double Bx, 
        int Cp, int Cj, long double Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, int Bp, int Bj, npy_cfloat_wrapper Bx, 
        int Cp, int Cj, npy_cfloat_wrapper Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, int Bp, int Bj, npy_cdouble_wrapper Bx, 
        int Cp, int Cj, npy_cdouble_wrapper Cx)
    bsr_elmul_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, int Bp, int Bj, 
        npy_clongdouble_wrapper Bx, int Cp, int Cj, npy_clongdouble_wrapper Cx)
    """
    return _bsr.bsr_elmul_bsr(*args)


def bsr_eldiv_bsr(*args):
    """
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        signed char Ax, int Bp, int Bj, signed char Bx, 
        int Cp, int Cj, signed char Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned char Ax, int Bp, int Bj, unsigned char Bx, 
        int Cp, int Cj, unsigned char Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        short Ax, int Bp, int Bj, short Bx, int Cp, 
        int Cj, short Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned short Ax, int Bp, int Bj, unsigned short Bx, 
        int Cp, int Cj, unsigned short Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        int Ax, int Bp, int Bj, int Bx, int Cp, int Cj, 
        int Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned int Ax, int Bp, int Bj, unsigned int Bx, 
        int Cp, int Cj, unsigned int Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long long Ax, int Bp, int Bj, long long Bx, 
        int Cp, int Cj, long long Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, int Bp, int Bj, unsigned long long Bx, 
        int Cp, int Cj, unsigned long long Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        float Ax, int Bp, int Bj, float Bx, int Cp, 
        int Cj, float Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        double Ax, int Bp, int Bj, double Bx, int Cp, 
        int Cj, double Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long double Ax, int Bp, int Bj, long double Bx, 
        int Cp, int Cj, long double Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, int Bp, int Bj, npy_cfloat_wrapper Bx, 
        int Cp, int Cj, npy_cfloat_wrapper Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, int Bp, int Bj, npy_cdouble_wrapper Bx, 
        int Cp, int Cj, npy_cdouble_wrapper Cx)
    bsr_eldiv_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, int Bp, int Bj, 
        npy_clongdouble_wrapper Bx, int Cp, int Cj, npy_clongdouble_wrapper Cx)
    """
    return _bsr.bsr_eldiv_bsr(*args)


def bsr_plus_bsr(*args):
    """
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        signed char Ax, int Bp, int Bj, signed char Bx, 
        int Cp, int Cj, signed char Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned char Ax, int Bp, int Bj, unsigned char Bx, 
        int Cp, int Cj, unsigned char Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        short Ax, int Bp, int Bj, short Bx, int Cp, 
        int Cj, short Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned short Ax, int Bp, int Bj, unsigned short Bx, 
        int Cp, int Cj, unsigned short Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        int Ax, int Bp, int Bj, int Bx, int Cp, int Cj, 
        int Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned int Ax, int Bp, int Bj, unsigned int Bx, 
        int Cp, int Cj, unsigned int Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long long Ax, int Bp, int Bj, long long Bx, 
        int Cp, int Cj, long long Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, int Bp, int Bj, unsigned long long Bx, 
        int Cp, int Cj, unsigned long long Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        float Ax, int Bp, int Bj, float Bx, int Cp, 
        int Cj, float Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        double Ax, int Bp, int Bj, double Bx, int Cp, 
        int Cj, double Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long double Ax, int Bp, int Bj, long double Bx, 
        int Cp, int Cj, long double Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, int Bp, int Bj, npy_cfloat_wrapper Bx, 
        int Cp, int Cj, npy_cfloat_wrapper Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, int Bp, int Bj, npy_cdouble_wrapper Bx, 
        int Cp, int Cj, npy_cdouble_wrapper Cx)
    bsr_plus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, int Bp, int Bj, 
        npy_clongdouble_wrapper Bx, int Cp, int Cj, npy_clongdouble_wrapper Cx)
    """
    return _bsr.bsr_plus_bsr(*args)


def bsr_minus_bsr(*args):
    """
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        signed char Ax, int Bp, int Bj, signed char Bx, 
        int Cp, int Cj, signed char Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned char Ax, int Bp, int Bj, unsigned char Bx, 
        int Cp, int Cj, unsigned char Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        short Ax, int Bp, int Bj, short Bx, int Cp, 
        int Cj, short Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned short Ax, int Bp, int Bj, unsigned short Bx, 
        int Cp, int Cj, unsigned short Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        int Ax, int Bp, int Bj, int Bx, int Cp, int Cj, 
        int Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned int Ax, int Bp, int Bj, unsigned int Bx, 
        int Cp, int Cj, unsigned int Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long long Ax, int Bp, int Bj, long long Bx, 
        int Cp, int Cj, long long Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        unsigned long long Ax, int Bp, int Bj, unsigned long long Bx, 
        int Cp, int Cj, unsigned long long Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        float Ax, int Bp, int Bj, float Bx, int Cp, 
        int Cj, float Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        double Ax, int Bp, int Bj, double Bx, int Cp, 
        int Cj, double Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        long double Ax, int Bp, int Bj, long double Bx, 
        int Cp, int Cj, long double Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax, int Bp, int Bj, npy_cfloat_wrapper Bx, 
        int Cp, int Cj, npy_cfloat_wrapper Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax, int Bp, int Bj, npy_cdouble_wrapper Bx, 
        int Cp, int Cj, npy_cdouble_wrapper Cx)
    bsr_minus_bsr(int n_row, int n_col, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax, int Bp, int Bj, 
        npy_clongdouble_wrapper Bx, int Cp, int Cj, npy_clongdouble_wrapper Cx)
    """
    return _bsr.bsr_minus_bsr(*args)


def bsr_sort_indices(*args):
    """
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        signed char Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned char Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        short Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned short Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        int Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned int Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long long Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        unsigned long long Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        float Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        double Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        long double Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cfloat_wrapper Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_cdouble_wrapper Ax)
    bsr_sort_indices(int n_brow, int n_bcol, int R, int C, int Ap, int Aj, 
        npy_clongdouble_wrapper Ax)
    """
    return _bsr.bsr_sort_indices(*args)