# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\signal\wavelets.pyc
# Compiled at: 2013-02-16 13:27:32
from __future__ import division, print_function, absolute_import
import numpy as np
from numpy.dual import eig
from scipy.misc import comb
from scipy import linspace, pi, exp
from scipy.signal import convolve
__all__ = [
 'daub', 'qmf', 'cascade', 'morlet', 'ricker', 'cwt']

def daub(p):
    """
    The coefficients for the FIR low-pass filter producing Daubechies wavelets.

    p>=1 gives the order of the zero at f=1/2.
    There are 2p filter coefficients.

    Parameters
    ----------
    p : int
        Order of the zero at f=1/2, can have values from 1 to 34.

    Returns
    -------
    daub : ndarray
        Return

    """
    sqrt = np.sqrt
    if p < 1:
        raise ValueError('p must be at least 1.')
    if p == 1:
        c = 1 / sqrt(2)
        return np.array([c, c])
    if p == 2:
        f = sqrt(2) / 8
        c = sqrt(3)
        return f * np.array([1 + c, 3 + c, 3 - c, 1 - c])
    if p == 3:
        tmp = 12 * sqrt(10)
        z1 = 1.5 + sqrt(15 + tmp) / 6 - complex(0.0, 1.0) * (sqrt(15) + sqrt(tmp - 15)) / 6
        z1c = np.conj(z1)
        f = sqrt(2) / 8
        d0 = np.real((1 - z1) * (1 - z1c))
        a0 = np.real(z1 * z1c)
        a1 = 2 * np.real(z1)
        return f / d0 * np.array([a0, 3 * a0 - a1, 3 * a0 - 3 * a1 + 1,
         a0 - 3 * a1 + 3, 3 - a1, 1])
    if p < 35:
        if p < 35:
            P = [ comb(p - 1 + k, k, exact=1) for k in range(p) ][::-1]
            yj = np.roots(P)
        else:
            P = [ comb(p - 1 + k, k, exact=1) / 4.0 ** k for k in range(p)
                ][::-1]
            yj = np.roots(P) / 4
        c = np.poly1d([1, 1]) ** p
        q = np.poly1d([1])
        for k in range(p - 1):
            yval = yj[k]
            part = 2 * sqrt(yval * (yval - 1))
            const = 1 - 2 * yval
            z1 = const + part
            if abs(z1) < 1:
                z1 = const - part
            q = q * [1, -z1]

        q = c * np.real(q)
        q = q / np.sum(q) * sqrt(2)
        return q.c[::-1]
    raise ValueError('Polynomial factorization does not work well for p too large.')


def qmf(hk):
    """
    Return high-pass qmf filter from low-pass

    Parameters
    ----------
    hk : array_like
        Coefficients of high-pass filter.

    """
    N = len(hk) - 1
    asgn = [ {0: 1, 1: -1}[k % 2] for k in range(N + 1) ]
    return hk[::-1] * np.array(asgn)


def wavedec(amn, hk):
    gk = qmf(hk)
    return NotImplemented


def cascade(hk, J=7):
    """
    Return (x, phi, psi) at dyadic points ``K/2**J`` from filter coefficients.

    Parameters
    ----------
    hk : array_like
        Coefficients of low-pass filter.
    J : int, optional
        Values will be computed at grid points ``K/2**J``. Default is 7.

    Returns
    -------
    x : ndarray
        The dyadic points ``K/2**J`` for ``K=0...N * (2**J)-1`` where
        ``len(hk) = len(gk) = N+1``.
    phi : ndarray
        The scaling function ``phi(x)`` at `x`:
        ``phi(x) = sum(hk * phi(2x-k))``, where k is from 0 to N.
    psi : ndarray, optional
        The wavelet function ``psi(x)`` at `x`:
        ``phi(x) = sum(gk * phi(2x-k))``, where k is from 0 to N.
        `psi` is only returned if `gk` is not None.

    Notes
    -----
    The algorithm uses the vector cascade algorithm described by Strang and
    Nguyen in "Wavelets and Filter Banks".  It builds a dictionary of values
    and slices for quick reuse.  Then inserts vectors into final vector at the
    end.

    """
    N = len(hk) - 1
    if J > 30 - np.log2(N + 1):
        raise ValueError('Too many levels.')
    if J < 1:
        raise ValueError('Too few levels.')
    nn, kk = np.ogrid[:N, :N]
    s2 = np.sqrt(2)
    thk = np.r_[(hk, 0)]
    gk = qmf(hk)
    tgk = np.r_[(gk, 0)]
    indx1 = np.clip(2 * nn - kk, -1, N + 1)
    indx2 = np.clip(2 * nn - kk + 1, -1, N + 1)
    m = np.zeros((2, 2, N, N), 'd')
    m[(0, 0)] = np.take(thk, indx1, 0)
    m[(0, 1)] = np.take(thk, indx2, 0)
    m[(1, 0)] = np.take(tgk, indx1, 0)
    m[(1, 1)] = np.take(tgk, indx2, 0)
    m *= s2
    x = np.arange(0, N * (1 << J), dtype=np.float) / (1 << J)
    phi = 0 * x
    psi = 0 * x
    lam, v = eig(m[(0, 0)])
    ind = np.argmin(np.absolute(lam - 1))
    v = np.real(v[:, ind])
    sm = np.sum(v)
    if sm < 0:
        v = -v
        sm = -sm
    bitdic = {}
    bitdic['0'] = v / sm
    bitdic['1'] = np.dot(m[(0, 1)], bitdic['0'])
    step = 1 << J
    phi[::step] = bitdic['0']
    phi[1 << J - 1::step] = bitdic['1']
    psi[::step] = np.dot(m[(1, 0)], bitdic['0'])
    psi[1 << J - 1::step] = np.dot(m[(1, 1)], bitdic['0'])
    prevkeys = [
     '1']
    for level in range(2, J + 1):
        newkeys = [ '%d%s' % (xx, yy) for xx in [0, 1] for yy in prevkeys ]
        fac = 1 << J - level
        for key in newkeys:
            num = 0
            for pos in range(level):
                if key[pos] == '1':
                    num += 1 << level - 1 - pos

            pastphi = bitdic[key[1:]]
            ii = int(key[0])
            temp = np.dot(m[(0, ii)], pastphi)
            bitdic[key] = temp
            phi[num * fac::step] = temp
            psi[num * fac::step] = np.dot(m[(1, ii)], pastphi)

        prevkeys = newkeys

    return (x, phi, psi)


def morlet(M, w=5.0, s=1.0, complete=True):
    """
    Complex Morlet wavelet.

    Parameters
    ----------
    M : int
        Length of the wavelet.
    w : float
        Omega0. Default is 5
    s : float
        Scaling factor, windowed from ``-s*2*pi`` to ``+s*2*pi``. Default is 1.
    complete : bool
        Whether to use the complete or the standard version.

    Returns
    -------
    morlet : (M,) ndarray

    See Also
    --------
    scipy.signal.gausspulse

    Notes
    -----
    The standard version::

        pi**-0.25 * exp(1j*w*x) * exp(-0.5*(x**2))

    This commonly used wavelet is often referred to simply as the
    Morlet wavelet.  Note that this simplified version can cause
    admissibility problems at low values of w.

    The complete version::

        pi**-0.25 * (exp(1j*w*x) - exp(-0.5*(w**2))) * exp(-0.5*(x**2))

    The complete version of the Morlet wavelet, with a correction
    term to improve admissibility. For w greater than 5, the
    correction term is negligible.

    Note that the energy of the return wavelet is not normalised
    according to s.

    The fundamental frequency of this wavelet in Hz is given
    by ``f = 2*s*w*r / M`` where r is the sampling rate.

    """
    x = linspace(-s * 2 * pi, s * 2 * pi, M)
    output = exp(complex(0.0, 1.0) * w * x)
    if complete:
        output -= exp(-0.5 * w ** 2)
    output *= exp(-0.5 * x ** 2) * pi ** (-0.25)
    return output


def ricker(points, a):
    """
    Return a Ricker wavelet, also known as the "Mexican hat wavelet".

    It models the function:

        ``A (1 - x^2/a^2) exp(-t^2/a^2)``,

    where ``A = 2/sqrt(3a)pi^1/3``.

    Parameters
    ----------
    points : int
        Number of points in `vector`. Default is ``10 * a``.
        Will be centered around 0.
    a : scalar
        Width parameter of the wavelet.

    Returns
    -------
    vector : (N,) ndarray
        Array of length `points` in shape of ricker curve.

    Examples
    --------
    >>> from scipy import signal
    >>> import matplotlib.pyplot as plt

    >>> points = 100
    >>> a = 4.0
    >>> vec2 = signal.ricker(points, a)
    >>> print len(vec2)
    100
    >>> plt.plot(vec2)
    >>> plt.show()

    """
    A = 2 / (np.sqrt(3 * a) * np.pi ** 0.25)
    wsq = a ** 2
    vec = np.arange(0, points) - (points - 1.0) / 2
    tsq = vec ** 2
    mod = 1 - tsq / wsq
    gauss = np.exp(-tsq / (2 * wsq))
    total = A * mod * gauss
    return total


def cwt(data, wavelet, widths):
    """
    Continuous wavelet transform.

    Performs a continuous wavelet transform on `data`,
    using the `wavelet` function. A CWT performs a convolution
    with `data` using the `wavelet` function, which is characterized
    by a width parameter and length parameter.

    Parameters
    ----------
    data : (N,) ndarray
        data on which to perform the transform.
    wavelet : function
        Wavelet function, which should take 2 arguments.
        The first argument is the number of points that the returned vector
        will have (len(wavelet(width,length)) == length).
        The second is a width parameter, defining the size of the wavelet
        (e.g. standard deviation of a gaussian). See `ricker`, which
        satisfies these requirements.
    widths : (M,) sequence
        Widths to use for transform.

    Returns
    -------
    cwt: (M, N) ndarray
        Will have shape of (len(data), len(widths)).

    Notes
    -----
    >>> length = min(10 * width[ii], len(data))
    >>> cwt[ii,:] = scipy.signal.convolve(data, wavelet(width[ii],
    ...                                       length), mode='same')

    Examples
    --------
    >>> from scipy import signal
    >>> sig = np.random.rand(20) - 0.5
    >>> wavelet = signal.ricker
    >>> widths = np.arange(1, 11)
    >>> cwtmatr = signal.cwt(sig, wavelet, widths)

    """
    output = np.zeros([len(widths), len(data)])
    for ind, width in enumerate(widths):
        wavelet_data = wavelet(min(10 * width, len(data)), width)
        output[ind, :] = convolve(data, wavelet_data, mode='same')

    return output