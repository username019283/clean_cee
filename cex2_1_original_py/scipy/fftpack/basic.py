# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\fftpack\basic.pyc
# Compiled at: 2013-02-16 13:27:30
"""
Discrete Fourier Transforms - basic.py
"""
from __future__ import division, print_function, absolute_import
__all__ = [
 'fft', 'ifft', 'fftn', 'ifftn', 'rfft', 'irfft', 
 'fft2', 'ifft2']
from numpy import zeros, swapaxes
import numpy
from . import _fftpack
import atexit
atexit.register(_fftpack.destroy_zfft_cache)
atexit.register(_fftpack.destroy_zfftnd_cache)
atexit.register(_fftpack.destroy_drfft_cache)
atexit.register(_fftpack.destroy_cfft_cache)
atexit.register(_fftpack.destroy_cfftnd_cache)
atexit.register(_fftpack.destroy_rfft_cache)
del atexit

def istype(arr, typeclass):
    return issubclass(arr.dtype.type, typeclass)


def _datacopied(arr, original):
    """
    Strict check for `arr` not sharing any data with `original`,
    under the assumption that arr = asarray(original)

    """
    if arr is original:
        return False
    else:
        if not isinstance(original, numpy.ndarray) and hasattr(original, '__array__'):
            return False
        return arr.base is None


def _is_safe_size(n):
    """
    Is the size of FFT such that FFTPACK can handle it in single precision
    with sufficient accuracy?

    Composite numbers of 2, 3, and 5 are accepted, as FFTPACK has those
    """
    n = int(n)
    for c in (2, 3, 5):
        while n % c == 0:
            n /= c

    return n <= 1


def _fake_crfft(x, n, *a, **kw):
    if _is_safe_size(n):
        return _fftpack.crfft(x, n, *a, **kw)
    else:
        return _fftpack.zrfft(x, n, *a, **kw).astype(numpy.complex64)


def _fake_cfft(x, n, *a, **kw):
    if _is_safe_size(n):
        return _fftpack.cfft(x, n, *a, **kw)
    else:
        return _fftpack.zfft(x, n, *a, **kw).astype(numpy.complex64)


def _fake_rfft(x, n, *a, **kw):
    if _is_safe_size(n):
        return _fftpack.rfft(x, n, *a, **kw)
    else:
        return _fftpack.drfft(x, n, *a, **kw).astype(numpy.float32)


def _fake_cfftnd(x, shape, *a, **kw):
    if numpy.all(list(map(_is_safe_size, shape))):
        return _fftpack.cfftnd(x, shape, *a, **kw)
    else:
        return _fftpack.zfftnd(x, shape, *a, **kw).astype(numpy.complex64)


_DTYPE_TO_FFT = {numpy.dtype(numpy.float32): _fake_crfft, 
   numpy.dtype(numpy.float64): _fftpack.zrfft, 
   numpy.dtype(numpy.complex64): _fake_cfft, 
   numpy.dtype(numpy.complex128): _fftpack.zfft}
_DTYPE_TO_RFFT = {numpy.dtype(numpy.float32): _fake_rfft, 
   numpy.dtype(numpy.float64): _fftpack.drfft}
_DTYPE_TO_FFTN = {numpy.dtype(numpy.complex64): _fake_cfftnd, 
   numpy.dtype(numpy.complex128): _fftpack.zfftnd, 
   numpy.dtype(numpy.float32): _fake_cfftnd, 
   numpy.dtype(numpy.float64): _fftpack.zfftnd}

def _asfarray(x):
    """Like numpy asfarray, except that it does not modify x dtype if x is
    already an array with a float dtype, and do not cast complex types to
    real."""
    if hasattr(x, 'dtype') and x.dtype.char in numpy.typecodes['AllFloat']:
        return x
    else:
        ret = numpy.asarray(x)
        if ret.dtype.char not in numpy.typecodes['AllFloat']:
            return numpy.asfarray(x)
        return ret


def _fix_shape(x, n, axis):
    """ Internal auxiliary function for _raw_fft, _raw_fftnd."""
    s = list(x.shape)
    if s[axis] > n:
        index = [
         slice(None)] * len(s)
        index[axis] = slice(0, n)
        x = x[index]
        return (
         x, False)
    else:
        index = [
         slice(None)] * len(s)
        index[axis] = slice(0, s[axis])
        s[axis] = n
        z = zeros(s, x.dtype.char)
        z[index] = x
        return (z, True)
        return


def _raw_fft(x, n, axis, direction, overwrite_x, work_function):
    """ Internal auxiliary function for fft, ifft, rfft, irfft."""
    if n is None:
        n = x.shape[axis]
    elif n != x.shape[axis]:
        x, copy_made = _fix_shape(x, n, axis)
        overwrite_x = overwrite_x or copy_made
    if axis == -1 or axis == len(x.shape) - 1:
        r = work_function(x, n, direction, overwrite_x=overwrite_x)
    else:
        x = swapaxes(x, axis, -1)
        r = work_function(x, n, direction, overwrite_x=overwrite_x)
        r = swapaxes(r, axis, -1)
    return r


def fft(x, n=None, axis=-1, overwrite_x=0):
    """
    Return discrete Fourier transform of real or complex sequence.

    The returned complex array contains ``y(0), y(1),..., y(n-1)`` where

    ``y(j) = (x * exp(-2*pi*sqrt(-1)*j*np.arange(n)/n)).sum()``.

    Parameters
    ----------
    x : array_like
        Array to Fourier transform.
    n : int, optional
        Length of the Fourier transform.  If ``n < x.shape[axis]``, `x` is
        truncated.  If ``n > x.shape[axis]``, `x` is zero-padded. The
        default results in ``n = x.shape[axis]``.
    axis : int, optional
        Axis along which the fft's are computed; the default is over the
        last axis (i.e., ``axis=-1``).
    overwrite_x : bool, optional
        If True the contents of `x` can be destroyed; the default is False.

    Returns
    -------
    z : complex ndarray
        with the elements::

            [y(0),y(1),..,y(n/2),y(1-n/2),...,y(-1)]        if n is even
            [y(0),y(1),..,y((n-1)/2),y(-(n-1)/2),...,y(-1)]  if n is odd

        where::

            y(j) = sum[k=0..n-1] x[k] * exp(-sqrt(-1)*j*k* 2*pi/n), j = 0..n-1

        Note that ``y(-j) = y(n-j).conjugate()``.

    See Also
    --------
    ifft : Inverse FFT
    rfft : FFT of a real sequence

    Notes
    -----
    The packing of the result is "standard": If A = fft(a, n), then A[0]
    contains the zero-frequency term, A[1:n/2+1] contains the
    positive-frequency terms, and A[n/2+1:] contains the negative-frequency
    terms, in order of decreasingly negative frequency. So for an 8-point
    transform, the frequencies of the result are [ 0, 1, 2, 3, 4, -3, -2, -1].

    For n even, A[n/2] contains the sum of the positive and negative-frequency
    terms. For n even and x real, A[n/2] will always be real.

    This is most efficient for n a power of two.

    Examples
    --------
    >>> from scipy.fftpack import fft, ifft
    >>> x = np.arange(5)
    >>> np.allclose(fft(ifft(x)), x, atol=1e-15)  #within numerical accuracy.
    True

    """
    tmp = _asfarray(x)
    try:
        work_function = _DTYPE_TO_FFT[tmp.dtype]
    except KeyError:
        raise ValueError('type %s is not supported' % tmp.dtype)

    if not (istype(tmp, numpy.complex64) or istype(tmp, numpy.complex128)):
        overwrite_x = 1
    overwrite_x = overwrite_x or _datacopied(tmp, x)
    if n is None:
        n = tmp.shape[axis]
    elif n != tmp.shape[axis]:
        tmp, copy_made = _fix_shape(tmp, n, axis)
        overwrite_x = overwrite_x or copy_made
    if axis == -1 or axis == len(tmp.shape) - 1:
        return work_function(tmp, n, 1, 0, overwrite_x)
    else:
        tmp = swapaxes(tmp, axis, -1)
        tmp = work_function(tmp, n, 1, 0, overwrite_x)
        return swapaxes(tmp, axis, -1)


def ifft(x, n=None, axis=-1, overwrite_x=0):
    """
    Return discrete inverse Fourier transform of real or complex sequence.

    The returned complex array contains ``y(0), y(1),..., y(n-1)`` where

    ``y(j) = (x * exp(2*pi*sqrt(-1)*j*np.arange(n)/n)).mean()``.

    Parameters
    ----------
    x : array_like
        Transformed data to invert.
    n : int, optional
        Length of the inverse Fourier transform.  If ``n < x.shape[axis]``,
        `x` is truncated.  If ``n > x.shape[axis]``, `x` is zero-padded.
        The default results in ``n = x.shape[axis]``.
    axis : int, optional
        Axis along which the ifft's are computed; the default is over the
        last axis (i.e., ``axis=-1``).
    overwrite_x : bool, optional
        If True the contents of `x` can be destroyed; the default is False.

    """
    tmp = _asfarray(x)
    try:
        work_function = _DTYPE_TO_FFT[tmp.dtype]
    except KeyError:
        raise ValueError('type %s is not supported' % tmp.dtype)

    if not (istype(tmp, numpy.complex64) or istype(tmp, numpy.complex128)):
        overwrite_x = 1
    overwrite_x = overwrite_x or _datacopied(tmp, x)
    if n is None:
        n = tmp.shape[axis]
    elif n != tmp.shape[axis]:
        tmp, copy_made = _fix_shape(tmp, n, axis)
        overwrite_x = overwrite_x or copy_made
    if axis == -1 or axis == len(tmp.shape) - 1:
        return work_function(tmp, n, -1, 1, overwrite_x)
    else:
        tmp = swapaxes(tmp, axis, -1)
        tmp = work_function(tmp, n, -1, 1, overwrite_x)
        return swapaxes(tmp, axis, -1)


def rfft(x, n=None, axis=-1, overwrite_x=0):
    """
    Discrete Fourier transform of a real sequence.

    The returned real arrays contains::

      [y(0),Re(y(1)),Im(y(1)),...,Re(y(n/2))]              if n is even
      [y(0),Re(y(1)),Im(y(1)),...,Re(y(n/2)),Im(y(n/2))]   if n is odd

    where
    ::

      y(j) = sum[k=0..n-1] x[k] * exp(-sqrt(-1)*j*k*2*pi/n)
      j = 0..n-1

    Note that ``y(-j) == y(n-j).conjugate()``.

    Parameters
    ----------
    x : array_like, real-valued
        The data to transform.
    n : int, optional
        Defines the length of the Fourier transform.  If `n` is not specified
        (the default) then ``n = x.shape[axis]``.  If ``n < x.shape[axis]``,
        `x` is truncated, if ``n > x.shape[axis]``, `x` is zero-padded.
    axis : int, optional
        The axis along which the transform is applied.  The default is the
        last axis.
    overwrite_x : bool, optional
        If set to true, the contents of `x` can be overwritten. Default is
        False.

    See Also
    --------
    fft, irfft, scipy.fftpack.basic

    Notes
    -----
    Within numerical accuracy, ``y == rfft(irfft(y))``.

    """
    tmp = _asfarray(x)
    if not numpy.isrealobj(tmp):
        raise TypeError('1st argument must be real sequence')
    try:
        work_function = _DTYPE_TO_RFFT[tmp.dtype]
    except KeyError:
        raise ValueError('type %s is not supported' % tmp.dtype)

    overwrite_x = overwrite_x or _datacopied(tmp, x)
    return _raw_fft(tmp, n, axis, 1, overwrite_x, work_function)


def irfft(x, n=None, axis=-1, overwrite_x=0):
    """
    Return inverse discrete Fourier transform of real sequence x.

    The contents of x is interpreted as the output of the ``rfft(..)``
    function.

    Parameters
    ----------
    x : array_like
        Transformed data to invert.
    n : int, optional
        Length of the inverse Fourier transform.
        If n < x.shape[axis], x is truncated.
        If n > x.shape[axis], x is zero-padded.
        The default results in n = x.shape[axis].
    axis : int, optional
        Axis along which the ifft's are computed; the default is over
        the last axis (i.e., axis=-1).
    overwrite_x : bool, optional
        If True the contents of `x` can be destroyed; the default is False.

    Returns
    -------
    irfft : ndarray of floats
        The inverse discrete Fourier transform.

    See Also
    --------
    rfft, ifft

    Notes
    -----
    The returned real array contains::

        [y(0),y(1),...,y(n-1)]

    where for n is even::

        y(j) = 1/n (sum[k=1..n/2-1] (x[2*k-1]+sqrt(-1)*x[2*k])
                                     * exp(sqrt(-1)*j*k* 2*pi/n)
                    + c.c. + x[0] + (-1)**(j) x[n-1])

    and for n is odd::

        y(j) = 1/n (sum[k=1..(n-1)/2] (x[2*k-1]+sqrt(-1)*x[2*k])
                                     * exp(sqrt(-1)*j*k* 2*pi/n)
                    + c.c. + x[0])

    c.c. denotes complex conjugate of preceeding expression.

    For details on input parameters, see `rfft`.

    """
    tmp = _asfarray(x)
    if not numpy.isrealobj(tmp):
        raise TypeError('1st argument must be real sequence')
    try:
        work_function = _DTYPE_TO_RFFT[tmp.dtype]
    except KeyError:
        raise ValueError('type %s is not supported' % tmp.dtype)

    overwrite_x = overwrite_x or _datacopied(tmp, x)
    return _raw_fft(tmp, n, axis, -1, overwrite_x, work_function)


def _raw_fftnd(x, s, axes, direction, overwrite_x, work_function):
    """ Internal auxiliary function for fftnd, ifftnd."""
    if s is None:
        if axes is None:
            s = x.shape
        else:
            s = numpy.take(x.shape, axes)
    s = tuple(s)
    if axes is None:
        noaxes = True
        axes = list(range(-x.ndim, 0))
    else:
        noaxes = False
    if len(axes) != len(s):
        raise ValueError('when given, axes and shape arguments have to be of the same length')
    for dim in s:
        if dim < 1:
            raise ValueError('Invalid number of FFT data points (%d) specified.' % s)

    if noaxes:
        for i in axes:
            x, copy_made = _fix_shape(x, s[i], i)
            overwrite_x = overwrite_x or copy_made

        return work_function(x, s, direction, overwrite_x=overwrite_x)
    else:
        id = numpy.argsort(axes)
        axes = [ axes[i] for i in id ]
        s = [ s[i] for i in id ]
        for i in range(1, len(axes) + 1):
            x = numpy.swapaxes(x, axes[-i], -i)

        waxes = list(range(x.ndim - len(axes), x.ndim))
        shape = numpy.ones(x.ndim)
        shape[waxes] = s
        for i in range(len(waxes)):
            x, copy_made = _fix_shape(x, s[i], waxes[i])
            overwrite_x = overwrite_x or copy_made

        r = work_function(x, shape, direction, overwrite_x=overwrite_x)
        for i in range(len(axes), 0, -1):
            r = numpy.swapaxes(r, -i, axes[-i])

        return r


def fftn(x, shape=None, axes=None, overwrite_x=0):
    """
    Return multidimensional discrete Fourier transform.

    The returned array contains::

      y[j_1,..,j_d] = sum[k_1=0..n_1-1, ..., k_d=0..n_d-1]
         x[k_1,..,k_d] * prod[i=1..d] exp(-sqrt(-1)*2*pi/n_i * j_i * k_i)

    where d = len(x.shape) and n = x.shape.
    Note that ``y[..., -j_i, ...] = y[..., n_i-j_i, ...].conjugate()``.

    Parameters
    ----------
    x : array_like
        The (n-dimensional) array to transform.
    shape : tuple of ints, optional
        The shape of the result.  If both `shape` and `axes` (see below) are
        None, `shape` is ``x.shape``; if `shape` is None but `axes` is
        not None, then `shape` is ``scipy.take(x.shape, axes, axis=0)``.
        If ``shape[i] > x.shape[i]``, the i-th dimension is padded with zeros.
        If ``shape[i] < x.shape[i]``, the i-th dimension is truncated to
        length ``shape[i]``.
    axes : array_like of ints, optional
        The axes of `x` (`y` if `shape` is not None) along which the
        transform is applied.
    overwrite_x : bool, optional
        If True, the contents of `x` can be destroyed.  Default is False.

    Returns
    -------
    y : complex-valued n-dimensional numpy array
        The (n-dimensional) DFT of the input array.

    See Also
    --------
    ifftn

    Examples
    --------
    >>> y = (-np.arange(16), 8 - np.arange(16), np.arange(16))
    >>> np.allclose(y, fftn(ifftn(y)))
    True

    """
    return _raw_fftn_dispatch(x, shape, axes, overwrite_x, 1)


def _raw_fftn_dispatch(x, shape, axes, overwrite_x, direction):
    tmp = _asfarray(x)
    try:
        work_function = _DTYPE_TO_FFTN[tmp.dtype]
    except KeyError:
        raise ValueError('type %s is not supported' % tmp.dtype)

    if not (istype(tmp, numpy.complex64) or istype(tmp, numpy.complex128)):
        overwrite_x = 1
    overwrite_x = overwrite_x or _datacopied(tmp, x)
    return _raw_fftnd(tmp, shape, axes, direction, overwrite_x, work_function)


def ifftn(x, shape=None, axes=None, overwrite_x=0):
    """
    Return inverse multi-dimensional discrete Fourier transform of
    arbitrary type sequence x.

    The returned array contains::

      y[j_1,..,j_d] = 1/p * sum[k_1=0..n_1-1, ..., k_d=0..n_d-1]
         x[k_1,..,k_d] * prod[i=1..d] exp(sqrt(-1)*2*pi/n_i * j_i * k_i)

    where ``d = len(x.shape)``, ``n = x.shape``, and ``p = prod[i=1..d] n_i``.

    For description of parameters see `fftn`.

    See Also
    --------
    fftn : for detailed information.

    """
    return _raw_fftn_dispatch(x, shape, axes, overwrite_x, -1)


def fft2(x, shape=None, axes=(-2, -1), overwrite_x=0):
    """
    2-D discrete Fourier transform.

    Return the two-dimensional discrete Fourier transform of the 2-D argument
    `x`.

    See Also
    --------
    fftn : for detailed information.

    """
    return fftn(x, shape, axes, overwrite_x)


def ifft2(x, shape=None, axes=(-2, -1), overwrite_x=0):
    """
    2-D discrete inverse Fourier transform of real or complex sequence.

    Return inverse two-dimensional discrete Fourier transform of
    arbitrary type sequence x.

    See `ifft` for more information.

    See also
    --------
    fft2, ifft

    """
    return ifftn(x, shape, axes, overwrite_x)