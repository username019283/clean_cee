# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: matplotlib\mlab.pyc
# Compiled at: 2012-11-06 11:14:56
"""

Numerical python functions written for compatability with MATLAB
commands with the same names.

MATLAB compatible functions
-------------------------------

:func:`cohere`
  Coherence (normalized cross spectral density)

:func:`csd`
  Cross spectral density uing Welch's average periodogram

:func:`detrend`
  Remove the mean or best fit line from an array

:func:`find`
  Return the indices where some condition is true;
         numpy.nonzero is similar but more general.

:func:`griddata`
  interpolate irregularly distributed data to a
             regular grid.

:func:`prctile`
  find the percentiles of a sequence

:func:`prepca`
  Principal Component Analysis

:func:`psd`
  Power spectral density uing Welch's average periodogram

:func:`rk4`
  A 4th order runge kutta integrator for 1D or ND systems

:func:`specgram`
  Spectrogram (power spectral density over segments of time)

Miscellaneous functions
-------------------------

Functions that don't exist in MATLAB, but are useful anyway:

:meth:`cohere_pairs`
    Coherence over all pairs.  This is not a MATLAB function, but we
    compute coherence a lot in my lab, and we compute it for a lot of
    pairs.  This function is optimized to do this efficiently by
    caching the direct FFTs.

:meth:`rk4`
    A 4th order Runge-Kutta ODE integrator in case you ever find
    yourself stranded without scipy (and the far superior
    scipy.integrate tools)

:meth:`contiguous_regions`
    return the indices of the regions spanned by some logical mask

:meth:`cross_from_below`
    return the indices where a 1D array crosses a threshold from below

:meth:`cross_from_above`
    return the indices where a 1D array crosses a threshold from above

record array helper functions
-------------------------------

A collection of helper methods for numpyrecord arrays

.. _htmlonly:

    See :ref:`misc-examples-index`

:meth:`rec2txt`
    pretty print a record array

:meth:`rec2csv`
    store record array in CSV file

:meth:`csv2rec`
    import record array from CSV file with type inspection

:meth:`rec_append_fields`
    adds  field(s)/array(s) to record array

:meth:`rec_drop_fields`
    drop fields from record array

:meth:`rec_join`
    join two record arrays on sequence of fields

:meth:`recs_join`
    a simple join of multiple recarrays using a single column as a key

:meth:`rec_groupby`
    summarize data by groups (similar to SQL GROUP BY)

:meth:`rec_summarize`
    helper code to filter rec array fields into new fields

For the rec viewer functions(e rec2csv), there are a bunch of Format
objects you can pass into the functions that will do things like color
negative values red, set percent formatting and scaling, etc.

Example usage::

    r = csv2rec('somefile.csv', checkrows=0)

    formatd = dict(
        weight = FormatFloat(2),
        change = FormatPercent(2),
        cost   = FormatThousands(2),
        )

    rec2excel(r, 'test.xls', formatd=formatd)
    rec2csv(r, 'test.csv', formatd=formatd)
    scroll = rec2gtk(r, formatd=formatd)

    win = gtk.Window()
    win.set_size_request(600,800)
    win.add(scroll)
    win.show_all()
    gtk.main()

Deprecated functions
---------------------

The following are deprecated; please import directly from numpy (with
care--function signatures may differ):

:meth:`load`
    load ASCII file - use numpy.loadtxt

:meth:`save`
    save ASCII file - use numpy.savetxt

"""
from __future__ import division, print_function
import csv, warnings, copy, os, operator
from itertools import izip
import numpy as np
ma = np.ma
from matplotlib import verbose
import matplotlib.cbook as cbook
from matplotlib import docstring
from matplotlib.path import Path

def logspace(xmin, xmax, N):
    return np.exp(np.linspace(np.log(xmin), np.log(xmax), N))


def _norm(x):
    """return sqrt(x dot x)"""
    return np.sqrt(np.dot(x, x))


def window_hanning(x):
    """return x times the hanning window of len(x)"""
    return np.hanning(len(x)) * x


def window_none(x):
    """No window function; simply return x"""
    return x


def detrend(x, key=None):
    if key is None or key == 'constant':
        return detrend_mean(x)
    else:
        if key == 'linear':
            return detrend_linear(x)
        return


def demean(x, axis=0):
    """Return x minus its mean along the specified axis"""
    x = np.asarray(x)
    if axis == 0 or axis is None or x.ndim <= 1:
        return x - x.mean(axis)
    else:
        ind = [
         slice(None)] * x.ndim
        ind[axis] = np.newaxis
        return x - x.mean(axis)[ind]


def detrend_mean(x):
    """Return x minus the mean(x)"""
    return x - x.mean()


def detrend_none(x):
    """Return x: no detrending"""
    return x


def detrend_linear(y):
    """Return y minus best fit line; 'linear' detrending """
    x = np.arange(len(y), dtype=np.float_)
    C = np.cov(x, y, bias=1)
    b = C[(0, 1)] / C[(0, 0)]
    a = y.mean() - b * x.mean()
    return y - (b * x + a)


def _spectral_helper(x, y, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None):
    same_data = y is x
    x = np.asarray(x)
    if not same_data:
        y = np.asarray(y)
    else:
        y = x
    if len(x) < NFFT:
        n = len(x)
        x = np.resize(x, (NFFT,))
        x[n:] = 0
    if not same_data and len(y) < NFFT:
        n = len(y)
        y = np.resize(y, (NFFT,))
        y[n:] = 0
    if pad_to is None:
        pad_to = NFFT
    if scale_by_freq is None:
        scale_by_freq = True
    if sides == 'default' and np.iscomplexobj(x) or sides == 'twosided':
        numFreqs = pad_to
        scaling_factor = 1.0
    else:
        if sides in ('default', 'onesided'):
            numFreqs = pad_to // 2 + 1
            scaling_factor = 2.0
        else:
            raise ValueError("sides must be one of: 'default', 'onesided', or 'twosided'")
        if cbook.iterable(window):
            assert len(window) == NFFT
            windowVals = window
        else:
            windowVals = window(np.ones((NFFT,), x.dtype))
        step = NFFT - noverlap
        ind = np.arange(0, len(x) - NFFT + 1, step)
        n = len(ind)
        Pxy = np.zeros((numFreqs, n), np.complex_)
        for i in range(n):
            thisX = x[ind[i]:ind[i] + NFFT]
            thisX = windowVals * detrend(thisX)
            fx = np.fft.fft(thisX, n=pad_to)
            if same_data:
                fy = fx
            else:
                thisY = y[ind[i]:ind[i] + NFFT]
                thisY = windowVals * detrend(thisY)
                fy = np.fft.fft(thisY, n=pad_to)
            Pxy[:, i] = np.conjugate(fx[:numFreqs]) * fy[:numFreqs]

    Pxy /= (np.abs(windowVals) ** 2).sum()
    Pxy[1:-1] *= scaling_factor
    if scale_by_freq:
        Pxy /= Fs
    t = 1.0 / Fs * (ind + NFFT / 2.0)
    freqs = float(Fs) / pad_to * np.arange(numFreqs)
    if np.iscomplexobj(x) and sides == 'default' or sides == 'twosided':
        freqs = np.concatenate((freqs[numFreqs // 2:] - Fs, freqs[:numFreqs // 2]))
        Pxy = np.concatenate((Pxy[numFreqs // 2:, :], Pxy[:numFreqs // 2, :]), 0)
    return (Pxy, freqs, t)


docstring.interpd.update(PSD=cbook.dedent("\n    Keyword arguments:\n\n      *NFFT*: integer\n          The number of data points used in each block for the FFT.\n          Must be even; a power 2 is most efficient.  The default value is 256.\n          This should *NOT* be used to get zero padding, or the scaling of the\n          result will be incorrect. Use *pad_to* for this instead.\n\n      *Fs*: scalar\n          The sampling frequency (samples per time unit).  It is used\n          to calculate the Fourier frequencies, freqs, in cycles per time\n          unit. The default value is 2.\n\n      *detrend*: callable\n          The function applied to each segment before fft-ing,\n          designed to remove the mean or linear trend.  Unlike in\n          MATLAB, where the *detrend* parameter is a vector, in\n          matplotlib is it a function.  The :mod:`~matplotlib.pylab`\n          module defines :func:`~matplotlib.pylab.detrend_none`,\n          :func:`~matplotlib.pylab.detrend_mean`, and\n          :func:`~matplotlib.pylab.detrend_linear`, but you can use\n          a custom function as well.\n\n      *window*: callable or ndarray\n          A function or a vector of length *NFFT*. To create window\n          vectors see :func:`window_hanning`, :func:`window_none`,\n          :func:`numpy.blackman`, :func:`numpy.hamming`,\n          :func:`numpy.bartlett`, :func:`scipy.signal`,\n          :func:`scipy.signal.get_window`, etc. The default is\n          :func:`window_hanning`.  If a function is passed as the\n          argument, it must take a data segment as an argument and\n          return the windowed version of the segment.\n\n      *pad_to*: integer\n          The number of points to which the data segment is padded when\n          performing the FFT.  This can be different from *NFFT*, which\n          specifies the number of data points used.  While not increasing\n          the actual resolution of the psd (the minimum distance between\n          resolvable peaks), this can give more points in the plot,\n          allowing for more detail. This corresponds to the *n* parameter\n          in the call to fft(). The default is None, which sets *pad_to*\n          equal to *NFFT*\n\n      *sides*: [ 'default' | 'onesided' | 'twosided' ]\n          Specifies which sides of the PSD to return.  Default gives the\n          default behavior, which returns one-sided for real data and both\n          for complex data.  'onesided' forces the return of a one-sided PSD,\n          while 'twosided' forces two-sided.\n\n      *scale_by_freq*: boolean\n          Specifies whether the resulting density values should be scaled\n          by the scaling frequency, which gives density in units of Hz^-1.\n          This allows for integration over the returned frequency values.\n          The default is True for MATLAB compatibility.\n"))

@docstring.dedent_interpd
def psd(x, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None):
    """
    The power spectral density by Welch's average periodogram method.
    The vector *x* is divided into *NFFT* length blocks.  Each block
    is detrended by the function *detrend* and windowed by the function
    *window*.  *noverlap* gives the length of the overlap between blocks.
    The absolute(fft(block))**2 of each segment are averaged to compute
    *Pxx*, with a scaling to correct for power loss due to windowing.

    If len(*x*) < *NFFT*, it will be zero padded to *NFFT*.

    *x*
        Array or sequence containing the data

    %(PSD)s

      *noverlap*: integer
          The number of points of overlap between blocks.  The default value
          is 0 (no overlap).

    Returns the tuple (*Pxx*, *freqs*).

    Refs:

        Bendat & Piersol -- Random Data: Analysis and Measurement
        Procedures, John Wiley & Sons (1986)

    """
    Pxx, freqs = csd(x, x, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    return (Pxx.real, freqs)


@docstring.dedent_interpd
def csd(x, y, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None):
    """
    The cross power spectral density by Welch's average periodogram
    method.  The vectors *x* and *y* are divided into *NFFT* length
    blocks.  Each block is detrended by the function *detrend* and
    windowed by the function *window*.  *noverlap* gives the length
    of the overlap between blocks.  The product of the direct FFTs
    of *x* and *y* are averaged over each segment to compute *Pxy*,
    with a scaling to correct for power loss due to windowing.

    If len(*x*) < *NFFT* or len(*y*) < *NFFT*, they will be zero
    padded to *NFFT*.

    *x*, *y*
        Array or sequence containing the data

    %(PSD)s

      *noverlap*: integer
          The number of points of overlap between blocks.  The default value
          is 0 (no overlap).

    Returns the tuple (*Pxy*, *freqs*).

    Refs:
        Bendat & Piersol -- Random Data: Analysis and Measurement
        Procedures, John Wiley & Sons (1986)
    """
    Pxy, freqs, t = _spectral_helper(x, y, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    if len(Pxy.shape) == 2 and Pxy.shape[1] > 1:
        Pxy = Pxy.mean(axis=1)
    return (
     Pxy, freqs)


@docstring.dedent_interpd
def specgram(x, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=128, pad_to=None, sides='default', scale_by_freq=None):
    """
    Compute a spectrogram of data in *x*.  Data are split into *NFFT*
    length segments and the PSD of each section is computed.  The
    windowing function *window* is applied to each segment, and the
    amount of overlap of each segment is specified with *noverlap*.

    If *x* is real (i.e. non-complex) only the spectrum of the positive
    frequencie is returned.  If *x* is complex then the complete
    spectrum is returned.

    %(PSD)s

      *noverlap*: integer
          The number of points of overlap between blocks.  The default value
          is 128.

    Returns a tuple (*Pxx*, *freqs*, *t*):

         - *Pxx*: 2-D array, columns are the periodograms of
           successive segments

         - *freqs*: 1-D array of frequencies corresponding to the rows
           in Pxx

         - *t*: 1-D array of times corresponding to midpoints of
           segments.

    .. seealso::

        :func:`psd`
            :func:`psd` differs in the default overlap; in returning
            the mean of the segment periodograms; and in not returning
            times.
    """
    assert NFFT > noverlap
    Pxx, freqs, t = _spectral_helper(x, x, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    Pxx = Pxx.real
    return (
     Pxx, freqs, t)


_coh_error = 'Coherence is calculated by averaging over *NFFT*\nlength segments.  Your signal is too short for your choice of *NFFT*.\n'

@docstring.dedent_interpd
def cohere(x, y, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=0, pad_to=None, sides='default', scale_by_freq=None):
    r"""
    The coherence between *x* and *y*.  Coherence is the normalized
    cross spectral density:

    .. math::

        C_{xy} = \frac{|P_{xy}|^2}{P_{xx}P_{yy}}

    *x*, *y*
        Array or sequence containing the data

    %(PSD)s

      *noverlap*: integer
          The number of points of overlap between blocks.  The default value
          is 0 (no overlap).

    The return value is the tuple (*Cxy*, *f*), where *f* are the
    frequencies of the coherence vector. For cohere, scaling the
    individual densities by the sampling frequency has no effect,
    since the factors cancel out.

    .. seealso::

        :func:`psd` and :func:`csd`
            For information about the methods used to compute
            :math:`P_{xy}`, :math:`P_{xx}` and :math:`P_{yy}`.
    """
    if len(x) < 2 * NFFT:
        raise ValueError(_coh_error)
    Pxx, f = psd(x, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    Pyy, f = psd(y, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    Pxy, f = csd(x, y, NFFT, Fs, detrend, window, noverlap, pad_to, sides, scale_by_freq)
    Cxy = np.divide(np.absolute(Pxy) ** 2, Pxx * Pyy)
    Cxy.shape = (len(f),)
    return (Cxy, f)


def donothing_callback(*args):
    pass


def cohere_pairs(X, ij, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning, noverlap=0, preferSpeedOverMemory=True, progressCallback=donothing_callback, returnPxx=False):
    """
    Call signature::

      Cxy, Phase, freqs = cohere_pairs( X, ij, ...)

    Compute the coherence and phase for all pairs *ij*, in *X*.

    *X* is a *numSamples* * *numCols* array

    *ij* is a list of tuples.  Each tuple is a pair of indexes into
    the columns of X for which you want to compute coherence.  For
    example, if *X* has 64 columns, and you want to compute all
    nonredundant pairs, define *ij* as::

      ij = []
      for i in range(64):
          for j in range(i+1,64):
              ij.append( (i,j) )

    *preferSpeedOverMemory* is an optional bool. Defaults to true. If
    False, limits the caching by only making one, rather than two,
    complex cache arrays. This is useful if memory becomes critical.
    Even when *preferSpeedOverMemory* is False, :func:`cohere_pairs`
    will still give significant performace gains over calling
    :func:`cohere` for each pair, and will use subtantially less
    memory than if *preferSpeedOverMemory* is True.  In my tests with
    a 43000,64 array over all nonredundant pairs,
    *preferSpeedOverMemory* = True delivered a 33% performance boost
    on a 1.7GHZ Athlon with 512MB RAM compared with
    *preferSpeedOverMemory* = False.  But both solutions were more
    than 10x faster than naively crunching all possible pairs through
    :func:`cohere`.

    Returns::

       (Cxy, Phase, freqs)

    where:

      - *Cxy*: dictionary of (*i*, *j*) tuples -> coherence vector for
        that pair.  I.e., ``Cxy[(i,j) = cohere(X[:,i], X[:,j])``.
        Number of dictionary keys is ``len(ij)``.

      - *Phase*: dictionary of phases of the cross spectral density at
        each frequency for each pair.  Keys are (*i*, *j*).

      - *freqs*: vector of frequencies, equal in length to either the
         coherence or phase vectors for any (*i*, *j*) key.

    Eg., to make a coherence Bode plot::

          subplot(211)
          plot( freqs, Cxy[(12,19)])
          subplot(212)
          plot( freqs, Phase[(12,19)])

    For a large number of pairs, :func:`cohere_pairs` can be much more
    efficient than just calling :func:`cohere` for each pair, because
    it caches most of the intensive computations.  If :math:`N` is the
    number of pairs, this function is :math:`O(N)` for most of the
    heavy lifting, whereas calling cohere for each pair is
    :math:`O(N^2)`.  However, because of the caching, it is also more
    memory intensive, making 2 additional complex arrays with
    approximately the same number of elements as *X*.

    See :file:`test/cohere_pairs_test.py` in the src tree for an
    example script that shows that this :func:`cohere_pairs` and
    :func:`cohere` give the same results for a given pair.

    .. seealso::

        :func:`psd`
            For information about the methods used to compute
            :math:`P_{xy}`, :math:`P_{xx}` and :math:`P_{yy}`.
    """
    numRows, numCols = X.shape
    if numRows < NFFT:
        tmp = X
        X = np.zeros((NFFT, numCols), X.dtype)
        X[:numRows, :] = tmp
        del tmp
    numRows, numCols = X.shape
    allColumns = set()
    for i, j in ij:
        allColumns.add(i)
        allColumns.add(j)

    Ncols = len(allColumns)
    if np.iscomplexobj(X):
        numFreqs = NFFT
    else:
        numFreqs = NFFT // 2 + 1
    if cbook.iterable(window):
        assert len(window) == NFFT
        windowVals = window
    else:
        windowVals = window(np.ones(NFFT, X.dtype))
    ind = range(0, numRows - NFFT + 1, NFFT - noverlap)
    numSlices = len(ind)
    FFTSlices = {}
    FFTConjSlices = {}
    Pxx = {}
    slices = range(numSlices)
    normVal = np.linalg.norm(windowVals) ** 2
    for iCol in allColumns:
        progressCallback(i / Ncols, 'Cacheing FFTs')
        Slices = np.zeros((numSlices, numFreqs), dtype=np.complex_)
        for iSlice in slices:
            thisSlice = X[ind[iSlice]:ind[iSlice] + NFFT, iCol]
            thisSlice = windowVals * detrend(thisSlice)
            Slices[iSlice, :] = np.fft.fft(thisSlice)[:numFreqs]

        FFTSlices[iCol] = Slices
        if preferSpeedOverMemory:
            FFTConjSlices[iCol] = np.conjugate(Slices)
        Pxx[iCol] = np.divide(np.mean(abs(Slices) ** 2, axis=0), normVal)

    del Slices
    del ind
    del windowVals
    Cxy = {}
    Phase = {}
    count = 0
    N = len(ij)
    for i, j in ij:
        count += 1
        if count % 10 == 0:
            progressCallback(count / N, 'Computing coherences')
        if preferSpeedOverMemory:
            Pxy = FFTSlices[i] * FFTConjSlices[j]
        else:
            Pxy = FFTSlices[i] * np.conjugate(FFTSlices[j])
        if numSlices > 1:
            Pxy = np.mean(Pxy, axis=0)
        Pxy /= normVal
        Cxy[(i, j)] = abs(Pxy) ** 2 / (Pxx[i] * Pxx[j])
        Phase[(i, j)] = np.arctan2(Pxy.imag, Pxy.real)

    freqs = Fs / NFFT * np.arange(numFreqs)
    if returnPxx:
        return (Cxy, Phase, freqs, Pxx)
    else:
        return (
         Cxy, Phase, freqs)


def entropy(y, bins):
    r"""
    Return the entropy of the data in *y*.

    .. math::

      \sum p_i \log_2(p_i)

    where :math:`p_i` is the probability of observing *y* in the
    :math:`i^{th}` bin of *bins*.  *bins* can be a number of bins or a
    range of bins; see :func:`numpy.histogram`.

    Compare *S* with analytic calculation for a Gaussian::

      x = mu + sigma * randn(200000)
      Sanalytic = 0.5 * ( 1.0 + log(2*pi*sigma**2.0) )
    """
    n, bins = np.histogram(y, bins)
    n = n.astype(np.float_)
    n = np.take(n, np.nonzero(n)[0])
    p = np.divide(n, len(y))
    delta = bins[1] - bins[0]
    S = -1.0 * np.sum(p * np.log(p)) + np.log(delta)
    return S


def normpdf(x, *args):
    """Return the normal pdf evaluated at *x*; args provides *mu*, *sigma*"""
    mu, sigma = args
    return 1.0 / (np.sqrt(2 * np.pi) * sigma) * np.exp(-0.5 * (1.0 / sigma * (x - mu)) ** 2)


def levypdf(x, gamma, alpha):
    """Returm the levy pdf evaluated at *x* for params *gamma*, *alpha*"""
    N = len(x)
    if N % 2 != 0:
        raise ValueError('x must be an event length array; try\n' + 'x = np.linspace(minx, maxx, N), where N is even')
    dx = x[1] - x[0]
    f = 1 / (N * dx) * np.arange(-N / 2, N / 2, np.float_)
    ind = np.concatenate([np.arange(N / 2, N, int),
     np.arange(0, N / 2, int)])
    df = f[1] - f[0]
    cfl = np.exp(-gamma * np.absolute(2 * np.pi * f) ** alpha)
    px = np.fft.fft(np.take(cfl, ind) * df).astype(np.float_)
    return np.take(px, ind)


def find(condition):
    """Return the indices where ravel(condition) is true"""
    res, = np.nonzero(np.ravel(condition))
    return res


def longest_contiguous_ones(x):
    """
    Return the indices of the longest stretch of contiguous ones in *x*,
    assuming *x* is a vector of zeros and ones.  If there are two
    equally long stretches, pick the first.
    """
    x = np.ravel(x)
    if len(x) == 0:
        return np.array([])
    ind = (x == 0).nonzero()[0]
    if len(ind) == 0:
        return np.arange(len(x))
    if len(ind) == len(x):
        return np.array([])
    y = np.zeros((len(x) + 2,), x.dtype)
    y[1:(-1)] = x
    dif = np.diff(y)
    up = (dif == 1).nonzero()[0]
    dn = (dif == -1).nonzero()[0]
    i = (dn - up == max(dn - up)).nonzero()[0][0]
    ind = np.arange(up[i], dn[i])
    return ind


def longest_ones(x):
    """alias for longest_contiguous_ones"""
    return longest_contiguous_ones(x)


def prepca(P, frac=0):
    """

    WARNING: this function is deprecated -- please see class PCA instead

    Compute the principal components of *P*.  *P* is a (*numVars*,
    *numObs*) array.  *frac* is the minimum fraction of variance that a
    component must contain to be included.

    Return value is a tuple of the form (*Pcomponents*, *Trans*,
    *fracVar*) where:

      - *Pcomponents* : a (numVars, numObs) array

      - *Trans* : the weights matrix, ie, *Pcomponents* = *Trans* *
         *P*

      - *fracVar* : the fraction of the variance accounted for by each
         component returned

    A similar function of the same name was in the MATLAB
    R13 Neural Network Toolbox but is not found in later versions;
    its successor seems to be called "processpcs".
    """
    warnings.warn('This function is deprecated -- see class PCA instead')
    U, s, v = np.linalg.svd(P)
    varEach = s ** 2 / P.shape[1]
    totVar = varEach.sum()
    fracVar = varEach / totVar
    ind = slice((fracVar >= frac).sum())
    Trans = U[:, ind].transpose()
    Pcomponents = np.dot(Trans, P)
    return (Pcomponents, Trans, fracVar[ind])


class PCA():

    def __init__(self, a):
        """
        compute the SVD of a and store data for PCA.  Use project to
        project the data onto a reduced set of dimensions

        Inputs:

          *a*: a numobservations x numdims array

        Attrs:

          *a* a centered unit sigma version of input a

          *numrows*, *numcols*: the dimensions of a

          *mu* : a numdims array of means of a

          *sigma* : a numdims array of atandard deviation of a

          *fracs* : the proportion of variance of each of the principal components

          *Wt* : the weight vector for projecting a numdims point or array into PCA space

          *Y* : a projected into PCA space

        The factor loadings are in the Wt factor, ie the factor
        loadings for the 1st principal component are given by Wt[0]

        """
        n, m = a.shape
        if n < m:
            raise RuntimeError('we assume data in a is organized with numrows>numcols')
        self.numrows, self.numcols = n, m
        self.mu = a.mean(axis=0)
        self.sigma = a.std(axis=0)
        a = self.center(a)
        self.a = a
        U, s, Vh = np.linalg.svd(a, full_matrices=False)
        Y = np.dot(Vh, a.T).T
        vars = s ** 2 / float(len(s))
        self.fracs = vars / vars.sum()
        self.Wt = Vh
        self.Y = Y

    def project(self, x, minfrac=0.0):
        """project x onto the principle axes, dropping any axes where fraction of variance<minfrac"""
        x = np.asarray(x)
        ndims = len(x.shape)
        if x.shape[-1] != self.numcols:
            raise ValueError('Expected an array with dims[-1]==%d' % self.numcols)
        Y = np.dot(self.Wt, self.center(x).T).T
        mask = self.fracs >= minfrac
        if ndims == 2:
            Yreduced = Y[:, mask]
        else:
            Yreduced = Y[mask]
        return Yreduced

    def center(self, x):
        """center the data using the mean and sigma from training set a"""
        return (x - self.mu) / self.sigma

    @staticmethod
    def _get_colinear():
        c0 = np.array([
         0.19294738, 0.6202667, 0.45962655, 0.07608613, 0.135818, 
         0.83580842, 
         0.07218851, 0.48318321, 0.84472463, 0.18348462, 
         0.81585306, 
         0.96923926, 0.12835919, 0.35075355, 0.15807861, 
         0.837437, 
         0.10824303, 0.1723387, 0.43926494, 0.83705486])
        c1 = np.array([
         -1.17705601, -0.513883, -0.26614584, 0.88067144, 1.00474954, 
         -1.1616545, 
         0.0266109, 0.38227157, 1.80489433, 0.21472396, 
         -1.41920399, 
         -2.08158544, -0.10559009, 1.68999268, 0.34847107, 
         -0.4685737, 
         1.23980423, -0.14638744, -0.35907697, 0.22442616])
        c2 = c0 + 2 * c1
        c3 = -3 * c0 + 4 * c1
        a = np.array([c3, c0, c1, c2]).T
        return a


def prctile(x, p=(
 0.0, 25.0, 50.0, 75.0, 100.0)):
    """
    Return the percentiles of *x*.  *p* can either be a sequence of
    percentile values or a scalar.  If *p* is a sequence, the ith
    element of the return sequence is the *p*(i)-th percentile of *x*.
    If *p* is a scalar, the largest value of *x* less than or equal to
    the *p* percentage point in the sequence is returned.
    """

    def _interpolate(a, b, fraction):
        """Returns the point at the given fraction between a and b, where
        'fraction' must be between 0 and 1.
        """
        return a + (b - a) * fraction

    scalar = True
    if cbook.iterable(p):
        scalar = False
    per = np.array(p)
    values = np.array(x).ravel()
    values.sort()
    idxs = per / 100.0 * (values.shape[0] - 1)
    ai = idxs.astype(np.int)
    bi = ai + 1
    frac = idxs % 1
    cond = bi >= len(values)
    if scalar:
        if cond:
            ai -= 1
            bi -= 1
            frac += 1
    else:
        ai[cond] -= 1
        bi[cond] -= 1
        frac[cond] += 1
    return _interpolate(values[ai], values[bi], frac)


def prctile_rank(x, p):
    """
    Return the rank for each element in *x*, return the rank
    0..len(*p*).  Eg if *p* = (25, 50, 75), the return value will be a
    len(*x*) array with values in [0,1,2,3] where 0 indicates the
    value is less than the 25th percentile, 1 indicates the value is
    >= the 25th and < 50th percentile, ... and 3 indicates the value
    is above the 75th percentile cutoff.

    *p* is either an array of percentiles in [0..100] or a scalar which
    indicates how many quantiles of data you want ranked.
    """
    if not cbook.iterable(p):
        p = np.arange(100.0 / p, 100.0, 100.0 / p)
    else:
        p = np.asarray(p)
    if p.max() <= 1 or p.min() < 0 or p.max() > 100:
        raise ValueError('percentiles should be in range 0..100, not 0..1')
    ptiles = prctile(x, p)
    return np.searchsorted(ptiles, x)


def center_matrix(M, dim=0):
    """
    Return the matrix *M* with each row having zero mean and unit std.

    If *dim* = 1 operate on columns instead of rows.  (*dim* is
    opposite to the numpy axis kwarg.)
    """
    M = np.asarray(M, np.float_)
    if dim:
        M = (M - M.mean(axis=0)) / M.std(axis=0)
    else:
        M = M - M.mean(axis=1)[:, np.newaxis]
        M = M / M.std(axis=1)[:, np.newaxis]
    return M


def rk4(derivs, y0, t):
    """
    Integrate 1D or ND system of ODEs using 4-th order Runge-Kutta.
    This is a toy implementation which may be useful if you find
    yourself stranded on a system w/o scipy.  Otherwise use
    :func:`scipy.integrate`.

    *y0*
        initial state vector

    *t*
        sample times

    *derivs*
        returns the derivative of the system and has the
        signature ``dy = derivs(yi, ti)``

    Example 1 ::

        ## 2D system

        def derivs6(x,t):
            d1 =  x[0] + 2*x[1]
            d2 =  -3*x[0] + 4*x[1]
            return (d1, d2)
        dt = 0.0005
        t = arange(0.0, 2.0, dt)
        y0 = (1,2)
        yout = rk4(derivs6, y0, t)

    Example 2::

        ## 1D system
        alpha = 2
        def derivs(x,t):
            return -alpha*x + exp(-t)

        y0 = 1
        yout = rk4(derivs, y0, t)

    If you have access to scipy, you should probably be using the
    scipy.integrate tools rather than this function.
    """
    try:
        Ny = len(y0)
    except TypeError:
        yout = np.zeros((len(t),), np.float_)
    else:
        yout = np.zeros((len(t), Ny), np.float_)

    yout[0] = y0
    i = 0
    for i in np.arange(len(t) - 1):
        thist = t[i]
        dt = t[i + 1] - thist
        dt2 = dt / 2.0
        y0 = yout[i]
        k1 = np.asarray(derivs(y0, thist))
        k2 = np.asarray(derivs(y0 + dt2 * k1, thist + dt2))
        k3 = np.asarray(derivs(y0 + dt2 * k2, thist + dt2))
        k4 = np.asarray(derivs(y0 + dt * k3, thist + dt))
        yout[i + 1] = y0 + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

    return yout


def bivariate_normal(X, Y, sigmax=1.0, sigmay=1.0, mux=0.0, muy=0.0, sigmaxy=0.0):
    """
    Bivariate Gaussian distribution for equal shape *X*, *Y*.

    See `bivariate normal
    <http://mathworld.wolfram.com/BivariateNormalDistribution.html>`_
    at mathworld.
    """
    Xmu = X - mux
    Ymu = Y - muy
    rho = sigmaxy / (sigmax * sigmay)
    z = Xmu ** 2 / sigmax ** 2 + Ymu ** 2 / sigmay ** 2 - 2 * rho * Xmu * Ymu / (sigmax * sigmay)
    denom = 2 * np.pi * sigmax * sigmay * np.sqrt(1 - rho ** 2)
    return np.exp(-z / (2 * (1 - rho ** 2))) / denom


def get_xyz_where(Z, Cond):
    """
    *Z* and *Cond* are *M* x *N* matrices.  *Z* are data and *Cond* is
    a boolean matrix where some condition is satisfied.  Return value
    is (*x*, *y*, *z*) where *x* and *y* are the indices into *Z* and
    *z* are the values of *Z* at those indices.  *x*, *y*, and *z* are
    1D arrays.
    """
    X, Y = np.indices(Z.shape)
    return (X[Cond], Y[Cond], Z[Cond])


def get_sparse_matrix(M, N, frac=0.1):
    """
    Return a *M* x *N* sparse matrix with *frac* elements randomly
    filled.
    """
    data = np.zeros((M, N)) * 0.0
    for i in range(int(M * N * frac)):
        x = np.random.randint(0, M - 1)
        y = np.random.randint(0, N - 1)
        data[(x, y)] = np.random.rand()

    return data


def dist(x, y):
    """
    Return the distance between two points.
    """
    d = x - y
    return np.sqrt(np.dot(d, d))


def dist_point_to_segment(p, s0, s1):
    """
    Get the distance of a point to a segment.

      *p*, *s0*, *s1* are *xy* sequences

    This algorithm from
    http://softsurfer.com/Archive/algorithm_0102/algorithm_0102.htm#Distance%20to%20Ray%20or%20Segment
    """
    p = np.asarray(p, np.float_)
    s0 = np.asarray(s0, np.float_)
    s1 = np.asarray(s1, np.float_)
    v = s1 - s0
    w = p - s0
    c1 = np.dot(w, v)
    if c1 <= 0:
        return dist(p, s0)
    c2 = np.dot(v, v)
    if c2 <= c1:
        return dist(p, s1)
    b = c1 / c2
    pb = s0 + b * v
    return dist(p, pb)


def segments_intersect(s1, s2):
    """
    Return *True* if *s1* and *s2* intersect.
    *s1* and *s2* are defined as::

      s1: (x1, y1), (x2, y2)
      s2: (x3, y3), (x4, y4)
    """
    (x1, y1), (x2, y2) = s1
    (x3, y3), (x4, y4) = s2
    den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    n1 = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
    n2 = (x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)
    if den == 0:
        return False
    u1 = n1 / den
    u2 = n2 / den
    return 0.0 <= u1 <= 1.0 and 0.0 <= u2 <= 1.0


def fftsurr(x, detrend=detrend_none, window=window_none):
    """
    Compute an FFT phase randomized surrogate of *x*.
    """
    if cbook.iterable(window):
        x = window * detrend(x)
    else:
        x = window(detrend(x))
    z = np.fft.fft(x)
    a = 2.0 * np.pi * complex(0.0, 1.0)
    phase = a * np.random.rand(len(x))
    z = z * np.exp(phase)
    return np.fft.ifft(z).real


def liaupunov(x, fprime):
    r"""
    *x* is a very long trajectory from a map, and *fprime* returns the
    derivative of *x*.

    This function will be removed from matplotlib.

    Returns :
    .. math::

        \lambda = \frac{1}{n}\sum \ln|f^'(x_i)|

    .. seealso::

        Lyapunov Exponent
           Sec 10.5 Strogatz (1994) "Nonlinear Dynamics and Chaos".
           `Wikipedia article on Lyapunov Exponent
           <http://en.wikipedia.org/wiki/Lyapunov_exponent>`_.

    .. note::
        What the function here calculates may not be what you really want;
        *caveat emptor*.

        It also seems that this function's name is badly misspelled.
    """
    warnings.warn('This does not belong in matplotlib and will be removed', DeprecationWarning)
    return np.mean(np.log(np.absolute(fprime(x))))


class FIFOBuffer():
    """
    A FIFO queue to hold incoming *x*, *y* data in a rotating buffer
    using numpy arrays under the hood.  It is assumed that you will
    call asarrays much less frequently than you add data to the queue
    -- otherwise another data structure will be faster.

    This can be used to support plots where data is added from a real
    time feed and the plot object wants to grab data from the buffer
    and plot it to screen less freqeuently than the incoming.

    If you set the *dataLim* attr to
    :class:`~matplotlib.transforms.BBox` (eg
    :attr:`matplotlib.Axes.dataLim`), the *dataLim* will be updated as
    new data come in.

    TODO: add a grow method that will extend nmax

    .. note::

      mlab seems like the wrong place for this class.
    """

    def __init__(self, nmax):
        """
        Buffer up to *nmax* points.
        """
        self._xa = np.zeros((nmax,), np.float_)
        self._ya = np.zeros((nmax,), np.float_)
        self._xs = np.zeros((nmax,), np.float_)
        self._ys = np.zeros((nmax,), np.float_)
        self._ind = 0
        self._nmax = nmax
        self.dataLim = None
        self.callbackd = {}
        return

    def register(self, func, N):
        """
        Call *func* every time *N* events are passed; *func* signature
        is ``func(fifo)``.
        """
        self.callbackd.setdefault(N, []).append(func)

    def add(self, x, y):
        """
        Add scalar *x* and *y* to the queue.
        """
        if self.dataLim is not None:
            xy = np.asarray([(x, y)])
            self.dataLim.update_from_data_xy(xy, None)
        ind = self._ind % self._nmax
        self._xs[ind] = x
        self._ys[ind] = y
        for N, funcs in self.callbackd.iteritems():
            if self._ind % N == 0:
                for func in funcs:
                    func(self)

        self._ind += 1
        return

    def last(self):
        """
        Get the last *x*, *y* or *None*.  *None* if no data set.
        """
        if self._ind == 0:
            return (None, None)
        else:
            ind = (self._ind - 1) % self._nmax
            return (self._xs[ind], self._ys[ind])

    def asarrays(self):
        """
        Return *x* and *y* as arrays; their length will be the len of
        data added or *nmax*.
        """
        if self._ind < self._nmax:
            return (self._xs[:self._ind], self._ys[:self._ind])
        ind = self._ind % self._nmax
        self._xa[:(self._nmax - ind)] = self._xs[ind:]
        self._xa[(self._nmax - ind):] = self._xs[:ind]
        self._ya[:(self._nmax - ind)] = self._ys[ind:]
        self._ya[(self._nmax - ind):] = self._ys[:ind]
        return (
         self._xa, self._ya)

    def update_datalim_to_current(self):
        """
        Update the *datalim* in the current data in the fifo.
        """
        if self.dataLim is None:
            raise ValueError('You must first set the dataLim attr')
        x, y = self.asarrays()
        self.dataLim.update_from_data(x, y, True)
        self.dataLim.update_numerix(x, y, True)
        return


def movavg(x, n):
    """
    Compute the len(*n*) moving average of *x*.
    """
    w = np.empty((n,), dtype=np.float_)
    w[:] = 1.0 / n
    return np.convolve(x, w, mode='valid')


def save(fname, X, fmt='%.18e', delimiter=' '):
    """
    Save the data in *X* to file *fname* using *fmt* string to convert the
    data to strings.

    Deprecated.  Use numpy.savetxt.

    *fname* can be a filename or a file handle.  If the filename ends
    in '.gz', the file is automatically saved in compressed gzip
    format.  The :func:`load` function understands gzipped files
    transparently.

    Example usage::

      save('test.out', X)         # X is an array
      save('test1.out', (x,y,z))  # x,y,z equal sized 1D arrays
      save('test2.out', x)        # x is 1D
      save('test3.out', x, fmt='%1.4e')  # use exponential notation

    *delimiter* is used to separate the fields, eg. *delimiter* ','
    for comma-separated values.
    """
    warnings.warn('use numpy.savetxt', DeprecationWarning)
    if cbook.is_string_like(fname):
        if fname.endswith('.gz'):
            import gzip
            fh = gzip.open(fname, 'wb')
        else:
            fh = open(fname, 'w')
    else:
        if hasattr(fname, 'seek'):
            fh = fname
        else:
            raise ValueError('fname must be a string or file handle')
        X = np.asarray(X)
        origShape = None
        if X.ndim == 1:
            origShape = X.shape
            X.shape = (len(X), 1)
        for row in X:
            fh.write(delimiter.join([ fmt % val for val in row ]) + '\n')

    if origShape is not None:
        X.shape = origShape
    return


def load(fname, comments='#', delimiter=None, converters=None, skiprows=0, usecols=None, unpack=False, dtype=np.float_):
    """
    Load ASCII data from *fname* into an array and return the array.

    Deprecated: use numpy.loadtxt.

    The data must be regular, same number of values in every row

    *fname* can be a filename or a file handle.  Support for gzipped
    files is automatic, if the filename ends in '.gz'.

    matfile data is not supported; for that, use :mod:`scipy.io.mio`
    module.

    Example usage::

      X = load('test.dat')  # data in two columns
      t = X[:,0]
      y = X[:,1]

    Alternatively, you can do the same with "unpack"; see below::

      X = load('test.dat')    # a matrix of data
      x = load('test.dat')    # a single column of data

    - *comments*: the character used to indicate the start of a comment
      in the file

    - *delimiter* is a string-like character used to seperate values
      in the file. If *delimiter* is unspecified or *None*, any
      whitespace string is a separator.

    - *converters*, if not *None*, is a dictionary mapping column number to
      a function that will convert that column to a float (or the optional
      *dtype* if specified).  Eg, if column 0 is a date string::

        converters = {0:datestr2num}

    - *skiprows* is the number of rows from the top to skip.

    - *usecols*, if not *None*, is a sequence of integer column indexes to
      extract where 0 is the first column, eg ``usecols=[1,4,5]`` to extract
      just the 2nd, 5th and 6th columns

    - *unpack*, if *True*, will transpose the matrix allowing you to unpack
      into named arguments on the left hand side::

        t,y = load('test.dat', unpack=True) # for  two column data
        x,y,z = load('somefile.dat', usecols=[3,5,7], unpack=True)

    - *dtype*: the array will have this dtype.  default: ``numpy.float_``

    .. seealso::

        See :file:`examples/pylab_examples/load_converter.py` in the source tree
           Exercises many of these options.
    """
    warnings.warn('use numpy.loadtxt', DeprecationWarning)
    if converters is None:
        converters = {}
    fh = cbook.to_filehandle(fname)
    X = []
    if delimiter == ' ':

        def splitfunc(x):
            return x.split()

    else:

        def splitfunc(x):
            return x.split(delimiter)

    converterseq = None
    for i, line in enumerate(fh):
        if i < skiprows:
            continue
        line = line.split(comments, 1)[0].strip()
        if not len(line):
            continue
        if converterseq is None:
            converterseq = [ converters.get(j, float) for j, val in enumerate(splitfunc(line)) ]
        if usecols is not None:
            vals = splitfunc(line)
            row = [ converterseq[j](vals[j]) for j in usecols ]
        else:
            row = [ converterseq[j](val) for j, val in enumerate(splitfunc(line))
                  ]
        X.append(row)

    X = np.array(X, dtype)
    r, c = X.shape
    if r == 1 or c == 1:
        X.shape = (
         max(r, c),)
    if unpack:
        return X.transpose()
    else:
        return X
        return


import math
exp_safe_MIN = math.log(2.2250738585072014e-308)
exp_safe_MAX = 1.7976931348623157e+308

def exp_safe(x):
    """
    Compute exponentials which safely underflow to zero.

    Slow, but convenient to use. Note that numpy provides proper
    floating point exception handling with access to the underlying
    hardware.
    """
    if type(x) is np.ndarray:
        return np.exp(np.clip(x, exp_safe_MIN, exp_safe_MAX))
    else:
        return math.exp(x)


def amap(fn, *args):
    """
    amap(function, sequence[, sequence, ...]) -> array.

    Works like :func:`map`, but it returns an array.  This is just a
    convenient shorthand for ``numpy.array(map(...))``.
    """
    return np.array(map(fn, *args))


def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return np.sqrt(np.mean(np.absolute(a) ** 2))


def l1norm(a):
    """
    Return the *l1* norm of *a*, flattened out.

    Implemented as a separate function (not a call to :func:`norm` for speed).
    """
    return np.sum(np.absolute(a))


def l2norm(a):
    """
    Return the *l2* norm of *a*, flattened out.

    Implemented as a separate function (not a call to :func:`norm` for speed).
    """
    return np.sqrt(np.sum(np.absolute(a) ** 2))


def norm_flat(a, p=2):
    """
    norm(a,p=2) -> l-p norm of a.flat

    Return the l-p norm of *a*, considered as a flat array.  This is NOT a true
    matrix norm, since arrays of arbitrary rank are always flattened.

    *p* can be a number or the string 'Infinity' to get the L-infinity norm.
    """
    if p == 'Infinity':
        return np.amax(np.absolute(a))
    else:
        return np.sum(np.absolute(a) ** p) ** (1.0 / p)


def frange(xini, xfin=None, delta=None, **kw):
    """
    frange([start,] stop[, step, keywords]) -> array of floats

    Return a numpy ndarray containing a progression of floats. Similar to
    :func:`numpy.arange`, but defaults to a closed interval.

    ``frange(x0, x1)`` returns ``[x0, x0+1, x0+2, ..., x1]``; *start*
    defaults to 0, and the endpoint *is included*. This behavior is
    different from that of :func:`range` and
    :func:`numpy.arange`. This is deliberate, since :func:`frange`
    will probably be more useful for generating lists of points for
    function evaluation, and endpoints are often desired in this
    use. The usual behavior of :func:`range` can be obtained by
    setting the keyword *closed* = 0, in this case, :func:`frange`
    basically becomes :func:numpy.arange`.

    When *step* is given, it specifies the increment (or
    decrement). All arguments can be floating point numbers.

    ``frange(x0,x1,d)`` returns ``[x0,x0+d,x0+2d,...,xfin]`` where
    *xfin* <= *x1*.

    :func:`frange` can also be called with the keyword *npts*. This
    sets the number of points the list should contain (and overrides
    the value *step* might have been given). :func:`numpy.arange`
    doesn't offer this option.

    Examples::

      >>> frange(3)
      array([ 0.,  1.,  2.,  3.])
      >>> frange(3,closed=0)
      array([ 0.,  1.,  2.])
      >>> frange(1,6,2)
      array([1, 3, 5])   or 1,3,5,7, depending on floating point vagueries
      >>> frange(1,6.5,npts=5)
      array([ 1.   ,  2.375,  3.75 ,  5.125,  6.5  ])
    """
    kw.setdefault('closed', 1)
    endpoint = kw['closed'] != 0
    if xfin == None:
        xfin = xini + 0.0
        xini = 0.0
    if delta == None:
        delta = 1.0
    try:
        npts = kw['npts']
        delta = (xfin - xini) / float(npts - endpoint)
    except KeyError:
        npts = int(round((xfin - xini) / delta)) + endpoint

    return np.arange(npts) * delta + xini


def identity(n, rank=2, dtype='l', typecode=None):
    r"""
    Returns the identity matrix of shape (*n*, *n*, ..., *n*) (rank *r*).

    For ranks higher than 2, this object is simply a multi-index Kronecker
    delta::

                            /  1  if i0=i1=...=iR,
        id[i0,i1,...,iR] = -|
                            \  0  otherwise.

    Optionally a *dtype* (or typecode) may be given (it defaults to 'l').

    Since rank defaults to 2, this function behaves in the default case (when
    only *n* is given) like ``numpy.identity(n)`` -- but surprisingly, it is
    much faster.
    """
    if typecode is not None:
        dtype = typecode
    iden = np.zeros((n,) * rank, dtype)
    for i in range(n):
        idx = (
         i,) * rank
        iden[idx] = 1

    return iden


def base_repr(number, base=2, padding=0):
    """
    Return the representation of a *number* in any given *base*.
    """
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if number < base:
        return (padding - 1) * chars[0] + chars[int(number)]
    max_exponent = int(math.log(number) / math.log(base))
    max_power = long(base) ** max_exponent
    lead_digit = int(number / max_power)
    return chars[lead_digit] + base_repr(number - max_power * lead_digit, base, max(padding - 1, max_exponent))


def binary_repr(number, max_length=1025):
    """
    Return the binary representation of the input *number* as a
    string.

    This is more efficient than using :func:`base_repr` with base 2.

    Increase the value of max_length for very large numbers. Note that
    on 32-bit machines, 2**1023 is the largest integer power of 2
    which can be converted to a Python float.
    """
    shifts = map(operator.rshift, max_length * [number], range(max_length - 1, -1, -1))
    digits = map(operator.mod, shifts, max_length * [2])
    if not digits.count(1):
        return 0
    digits = digits[digits.index(1):]
    return ('').join(map(repr, digits)).replace('L', '')


def log2(x, ln2=math.log(2.0)):
    """
    Return the log(*x*) in base 2.

    This is a _slow_ function but which is guaranteed to return the correct
    integer value if the input is an integer exact power of 2.
    """
    try:
        bin_n = binary_repr(x)[1:]
    except (AssertionError, TypeError):
        return math.log(x) / ln2

    if '1' in bin_n:
        return math.log(x) / ln2
    else:
        return len(bin_n)


def ispower2(n):
    """
    Returns the log base 2 of *n* if *n* is a power of 2, zero otherwise.

    Note the potential ambiguity if *n* == 1: 2**0 == 1, interpret accordingly.
    """
    bin_n = binary_repr(n)[1:]
    if '1' in bin_n:
        return 0
    else:
        return len(bin_n)


def isvector(X):
    """
    Like the MATLAB function with the same name, returns *True*
    if the supplied numpy array or matrix *X* looks like a vector,
    meaning it has a one non-singleton axis (i.e., it can have
    multiple axes, but all must have length 1, except for one of
    them).

    If you just want to see if the array has 1 axis, use X.ndim == 1.
    """
    return np.prod(X.shape) == np.max(X.shape)


def safe_isnan(x):
    """:func:`numpy.isnan` for arbitrary types"""
    if cbook.is_string_like(x):
        return False
    else:
        try:
            b = np.isnan(x)
        except NotImplementedError:
            return False
        except TypeError:
            return False

        return b


def safe_isinf(x):
    """:func:`numpy.isinf` for arbitrary types"""
    if cbook.is_string_like(x):
        return False
    else:
        try:
            b = np.isinf(x)
        except NotImplementedError:
            return False
        except TypeError:
            return False

        return b


def rec_append_fields(rec, names, arrs, dtypes=None):
    """
    Return a new record array with field names populated with data
    from arrays in *arrs*.  If appending a single field, then *names*,
    *arrs* and *dtypes* do not have to be lists. They can just be the
    values themselves.
    """
    if not cbook.is_string_like(names) and cbook.iterable(names) and len(names) and cbook.is_string_like(names[0]):
        if len(names) != len(arrs):
            raise ValueError('number of arrays do not match number of names')
    else:
        names = [
         names]
        arrs = [arrs]
    arrs = map(np.asarray, arrs)
    if dtypes is None:
        dtypes = [ a.dtype for a in arrs ]
    else:
        if not cbook.iterable(dtypes):
            dtypes = [
             dtypes]
        if len(arrs) != len(dtypes):
            if len(dtypes) == 1:
                dtypes = dtypes * len(arrs)
            else:
                raise ValueError('dtypes must be None, a single dtype or a list')
        newdtype = np.dtype(rec.dtype.descr + zip(names, dtypes))
        newrec = np.recarray(rec.shape, dtype=newdtype)
        for field in rec.dtype.fields:
            newrec[field] = rec[field]

        for name, arr in zip(names, arrs):
            newrec[name] = arr

    return newrec


def rec_drop_fields(rec, names):
    """
    Return a new numpy record array with fields in *names* dropped.
    """
    names = set(names)
    newdtype = np.dtype([ (name, rec.dtype[name]) for name in rec.dtype.names if name not in names
                        ])
    newrec = np.recarray(rec.shape, dtype=newdtype)
    for field in newdtype.names:
        newrec[field] = rec[field]

    return newrec


def rec_keep_fields(rec, names):
    """
    Return a new numpy record array with only fields listed in names
    """
    if cbook.is_string_like(names):
        names = names.split(',')
    arrays = []
    for name in names:
        arrays.append(rec[name])

    return np.rec.fromarrays(arrays, names=names)


def rec_groupby(r, groupby, stats):
    """
    *r* is a numpy record array

    *groupby* is a sequence of record array attribute names that
    together form the grouping key.  eg ('date', 'productcode')

    *stats* is a sequence of (*attr*, *func*, *outname*) tuples which
    will call ``x = func(attr)`` and assign *x* to the record array
    output with attribute *outname*.  For example::

      stats = ( ('sales', len, 'numsales'), ('sales', np.mean, 'avgsale') )

    Return record array has *dtype* names for each attribute name in
    the the *groupby* argument, with the associated group values, and
    for each outname name in the *stats* argument, with the associated
    stat summary output.
    """
    rowd = dict()
    for i, row in enumerate(r):
        key = tuple([ row[attr] for attr in groupby ])
        rowd.setdefault(key, []).append(i)

    keys = rowd.keys()
    keys.sort()
    rows = []
    for key in keys:
        row = list(key)
        ind = rowd[key]
        thisr = r[ind]
        row.extend([ func(thisr[attr]) for attr, func, outname in stats ])
        rows.append(row)

    attrs, funcs, outnames = zip(*stats)
    names = list(groupby)
    names.extend(outnames)
    return np.rec.fromrecords(rows, names=names)


def rec_summarize(r, summaryfuncs):
    """
    *r* is a numpy record array

    *summaryfuncs* is a list of (*attr*, *func*, *outname*) tuples
    which will apply *func* to the the array *r*[attr] and assign the
    output to a new attribute name *outname*.  The returned record
    array is identical to *r*, with extra arrays for each element in
    *summaryfuncs*.

    """
    names = list(r.dtype.names)
    arrays = [ r[name] for name in names ]
    for attr, func, outname in summaryfuncs:
        names.append(outname)
        arrays.append(np.asarray(func(r[attr])))

    return np.rec.fromarrays(arrays, names=names)


def rec_join(key, r1, r2, jointype='inner', defaults=None, r1postfix='1', r2postfix='2'):
    """
    Join record arrays *r1* and *r2* on *key*; *key* is a tuple of
    field names -- if *key* is a string it is assumed to be a single
    attribute name. If *r1* and *r2* have equal values on all the keys
    in the *key* tuple, then their fields will be merged into a new
    record array containing the intersection of the fields of *r1* and
    *r2*.

    *r1* (also *r2*) must not have any duplicate keys.

    The *jointype* keyword can be 'inner', 'outer', 'leftouter'.  To
    do a rightouter join just reverse *r1* and *r2*.

    The *defaults* keyword is a dictionary filled with
    ``{column_name:default_value}`` pairs.

    The keywords *r1postfix* and *r2postfix* are postfixed to column names
    (other than keys) that are both in *r1* and *r2*.
    """
    if cbook.is_string_like(key):
        key = (
         key,)
    for name in key:
        if name not in r1.dtype.names:
            raise ValueError('r1 does not have key field %s' % name)
        if name not in r2.dtype.names:
            raise ValueError('r2 does not have key field %s' % name)

    def makekey(row):
        return tuple([ row[name] for name in key ])

    r1d = dict([ (makekey(row), i) for i, row in enumerate(r1) ])
    r2d = dict([ (makekey(row), i) for i, row in enumerate(r2) ])
    r1keys = set(r1d.keys())
    r2keys = set(r2d.keys())
    common_keys = r1keys & r2keys
    r1ind = np.array([ r1d[k] for k in common_keys ])
    r2ind = np.array([ r2d[k] for k in common_keys ])
    common_len = len(common_keys)
    left_len = right_len = 0
    if jointype == 'outer' or jointype == 'leftouter':
        left_keys = r1keys.difference(r2keys)
        left_ind = np.array([ r1d[k] for k in left_keys ])
        left_len = len(left_ind)
    if jointype == 'outer':
        right_keys = r2keys.difference(r1keys)
        right_ind = np.array([ r2d[k] for k in right_keys ])
        right_len = len(right_ind)

    def key_desc(name):
        """if name is a string key, use the larger size of r1 or r2 before merging"""
        dt1 = r1.dtype[name]
        if dt1.type != np.string_:
            return (name, dt1.descr[0][1])
        else:
            dt2 = r1.dtype[name]
            assert dt2 == dt1
            if dt1.num > dt2.num:
                return (name, dt1.descr[0][1])
            return (name, dt2.descr[0][1])

    keydesc = [ key_desc(name) for name in key ]

    def mapped_r1field(name):
        """
        The column name in *newrec* that corresponds to the column in *r1*.
        """
        if name in key or name not in r2.dtype.names:
            return name
        return name + r1postfix

    def mapped_r2field(name):
        """
        The column name in *newrec* that corresponds to the column in *r2*.
        """
        if name in key or name not in r1.dtype.names:
            return name
        return name + r2postfix

    r1desc = [ (mapped_r1field(desc[0]), desc[1]) for desc in r1.dtype.descr if desc[0] not in key ]
    r2desc = [ (mapped_r2field(desc[0]), desc[1]) for desc in r2.dtype.descr if desc[0] not in key ]
    newdtype = np.dtype(keydesc + r1desc + r2desc)
    newrec = np.recarray((common_len + left_len + right_len,), dtype=newdtype)
    if defaults is not None:
        for thiskey in defaults:
            if thiskey not in newdtype.names:
                warnings.warn('rec_join defaults key="%s" not in new dtype names "%s"' % (
                 thiskey, newdtype.names))

    for name in newdtype.names:
        dt = newdtype[name]
        if dt.kind in ('f', 'i'):
            newrec[name] = 0

    if jointype != 'inner' and defaults is not None:
        newrec_fields = newrec.dtype.fields.keys()
        for k, v in defaults.iteritems():
            if k in newrec_fields:
                newrec[k] = v

    for field in r1.dtype.names:
        newfield = mapped_r1field(field)
        if common_len:
            newrec[newfield][:common_len] = r1[field][r1ind]
        if (jointype == 'outer' or jointype == 'leftouter') and left_len:
            newrec[newfield][common_len:(common_len + left_len)] = r1[field][left_ind]

    for field in r2.dtype.names:
        newfield = mapped_r2field(field)
        if field not in key and common_len:
            newrec[newfield][:common_len] = r2[field][r2ind]
        if jointype == 'outer' and right_len:
            newrec[newfield][(-right_len):] = r2[field][right_ind]

    newrec.sort(order=key)
    return newrec


def recs_join(key, name, recs, jointype='outer', missing=0.0, postfixes=None):
    """
    Join a sequence of record arrays on single column key.

    This function only joins a single column of the multiple record arrays

    *key*
      is the column name that acts as a key

    *name*
      is the name of the column that we want to join

    *recs*
      is a list of record arrays to join

    *jointype*
      is a string 'inner' or 'outer'

    *missing*
      is what any missing field is replaced by

    *postfixes*
      if not None, a len recs sequence of postfixes

    returns a record array with columns [rowkey, name0, name1, ... namen-1].
    or if postfixes [PF0, PF1, ..., PFN-1] are supplied,
    [rowkey, namePF0, namePF1, ... namePFN-1].

    Example::

      r = recs_join("date", "close", recs=[r0, r1], missing=0.)

    """
    results = []
    aligned_iters = cbook.align_iterators(operator.attrgetter(key), *[ iter(r) for r in recs ])

    def extract(r):
        if r is None:
            return missing
        else:
            return r[name]
            return

    if jointype == 'outer':
        for rowkey, row in aligned_iters:
            results.append([rowkey] + map(extract, row))

    elif jointype == 'inner':
        for rowkey, row in aligned_iters:
            if None not in row:
                results.append([rowkey] + map(extract, row))

    if postfixes is None:
        postfixes = [ '%d' % i for i in range(len(recs)) ]
    names = (',').join([key] + [ '%s%s' % (name, postfix) for postfix in postfixes ])
    return np.rec.fromrecords(results, names=names)


def csv2rec(fname, comments='#', skiprows=0, checkrows=0, delimiter=',', converterd=None, names=None, missing='', missingd=None, use_mrecords=False):
    """
    Load data from comma/space/tab delimited file in *fname* into a
    numpy record array and return the record array.

    If *names* is *None*, a header row is required to automatically
    assign the recarray names.  The headers will be lower cased,
    spaces will be converted to underscores, and illegal attribute
    name characters removed.  If *names* is not *None*, it is a
    sequence of names to use for the column names.  In this case, it
    is assumed there is no header row.

    - *fname*: can be a filename or a file handle.  Support for gzipped
      files is automatic, if the filename ends in '.gz'

    - *comments*: the character used to indicate the start of a comment
      in the file

    - *skiprows*: is the number of rows from the top to skip

    - *checkrows*: is the number of rows to check to validate the column
      data type.  When set to zero all rows are validated.

    - *converterd*: if not *None*, is a dictionary mapping column number or
      munged column name to a converter function.

    - *names*: if not None, is a list of header names.  In this case, no
      header will be read from the file

    - *missingd* is a dictionary mapping munged column names to field values
      which signify that the field does not contain actual data and should
      be masked, e.g. '0000-00-00' or 'unused'

    - *missing*: a string whose value signals a missing field regardless of
      the column it appears in

    - *use_mrecords*: if True, return an mrecords.fromrecords record array if any of the data are missing

      If no rows are found, *None* is returned -- see :file:`examples/loadrec.py`
    """
    if converterd is None:
        converterd = dict()
    if missingd is None:
        missingd = {}
    import dateutil.parser, datetime
    fh = cbook.to_filehandle(fname)

    class FH:
        """
        For space-delimited files, we want different behavior than
        comma or tab.  Generally, we want multiple spaces to be
        treated as a single separator, whereas with comma and tab we
        want multiple commas to return multiple (empty) fields.  The
        join/strip trick below effects this.
        """

        def __init__(self, fh):
            self.fh = fh

        def close(self):
            self.fh.close()

        def seek(self, arg):
            self.fh.seek(arg)

        def fix(self, s):
            return (' ').join(s.split())

        def __next__(self):
            return self.fix(next(self.fh))

        def __iter__(self):
            for line in self.fh:
                yield self.fix(line)

    if delimiter == ' ':
        fh = FH(fh)
    reader = csv.reader(fh, delimiter=delimiter)

    def process_skiprows(reader):
        if skiprows:
            for i, row in enumerate(reader):
                if i >= skiprows - 1:
                    break

        return (
         fh, reader)

    process_skiprows(reader)

    def ismissing(name, val):
        """Should the value val in column name be masked?"""
        if val == missing or val == missingd.get(name) or val == '':
            return True
        return False

    def with_default_value(func, default):

        def newfunc(name, val):
            if ismissing(name, val):
                return default
            else:
                return func(val)

        return newfunc

    def mybool(x):
        if x == 'True':
            return True
        if x == 'False':
            return False
        raise ValueError('invalid bool')

    dateparser = dateutil.parser.parse
    mydateparser = with_default_value(dateparser, datetime.date(1, 1, 1))
    myfloat = with_default_value(float, np.nan)
    myint = with_default_value(int, -1)
    mystr = with_default_value(str, '')
    mybool = with_default_value(mybool, None)

    def mydate(x):
        d = dateparser(x)
        if d.hour > 0 or d.minute > 0 or d.second > 0:
            raise ValueError('not a date')
        return d.date()

    mydate = with_default_value(mydate, datetime.date(1, 1, 1))

    def get_func(name, item, func):
        funcmap = {mybool: myint, myint: myfloat, myfloat: mydate, mydate: mydateparser, mydateparser: mystr}
        try:
            func(name, item)
        except:
            if func == mystr:
                raise ValueError('Could not find a working conversion function')
            else:
                return get_func(name, item, funcmap[func])
        else:
            return func

    itemd = {'return': 'return_', 
       'file': 'file_', 
       'print': 'print_'}

    def get_converters(reader):
        converters = None
        for i, row in enumerate(reader):
            if i == 0:
                converters = [
                 mybool] * len(row)
            if checkrows and i > checkrows:
                break
            for j, (name, item) in enumerate(izip(names, row)):
                func = converterd.get(j)
                if func is None:
                    func = converterd.get(name)
                if func is None:
                    func = converters[j]
                    if len(item.strip()):
                        func = get_func(name, item, func)
                else:
                    func = with_default_value(func, None)
                converters[j] = func

        return converters

    needheader = names is None
    if needheader:
        for row in reader:
            if len(row) and row[0].startswith(comments):
                continue
            headers = row
            break

        delete = set("~!@#$%^&*()-=+~\\|]}[{';: /?.>,<")
        delete.add('"')
        names = []
        seen = dict()
        for i, item in enumerate(headers):
            item = item.strip().lower().replace(' ', '_')
            item = ('').join([ c for c in item if c not in delete ])
            if not len(item):
                item = 'column%d' % i
            item = itemd.get(item, item)
            cnt = seen.get(item, 0)
            if cnt > 0:
                names.append(item + '_%d' % cnt)
            else:
                names.append(item)
            seen[item] = cnt + 1

    else:
        if cbook.is_string_like(names):
            names = [ n.strip() for n in names.split(',') ]
        converters = get_converters(reader)
        if converters is None:
            raise ValueError('Could not find any valid data in CSV file')
        fh.seek(0)
        reader = csv.reader(fh, delimiter=delimiter)
        process_skiprows(reader)
        if needheader:
            while 1:
                row = next(reader)
                if len(row) and row[0].startswith(comments):
                    continue
                break

        rows = []
        rowmasks = []
        for i, row in enumerate(reader):
            if not len(row):
                continue
            if row[0].startswith(comments):
                continue
            row.extend([''] * (len(converters) - len(row)))
            rows.append([ func(name, val) for func, name, val in zip(converters, names, row) ])
            rowmasks.append([ ismissing(name, val) for name, val in zip(names, row) ])

    fh.close()
    if not len(rows):
        return
    else:
        if use_mrecords and np.any(rowmasks):
            try:
                from numpy.ma import mrecords
            except ImportError:
                raise RuntimeError('numpy 1.05 or later is required for masked array support')
            else:
                r = mrecords.fromrecords(rows, names=names, mask=rowmasks)

        else:
            r = np.rec.fromrecords(rows, names=names)
        return r


class FormatObj():

    def tostr(self, x):
        return self.toval(x)

    def toval(self, x):
        return str(x)

    def fromstr(self, s):
        return s

    def __hash__(self):
        """
        override the hash function of any of the formatters, so that we don't create duplicate excel format styles
        """
        return hash(self.__class__)


class FormatString(FormatObj):

    def tostr(self, x):
        val = repr(x)
        return val[1:-1]


class FormatFormatStr(FormatObj):

    def __init__(self, fmt):
        self.fmt = fmt

    def tostr(self, x):
        if x is None:
            return 'None'
        else:
            return self.fmt % self.toval(x)


class FormatFloat(FormatFormatStr):

    def __init__(self, precision=4, scale=1.0):
        FormatFormatStr.__init__(self, '%%1.%df' % precision)
        self.precision = precision
        self.scale = scale

    def __hash__(self):
        return hash((self.__class__, self.precision, self.scale))

    def toval(self, x):
        if x is not None:
            x = x * self.scale
        return x

    def fromstr(self, s):
        return float(s) / self.scale


class FormatInt(FormatObj):

    def tostr(self, x):
        return '%d' % int(x)

    def toval(self, x):
        return int(x)

    def fromstr(self, s):
        return int(s)


class FormatBool(FormatObj):

    def toval(self, x):
        return str(x)

    def fromstr(self, s):
        return bool(s)


class FormatPercent(FormatFloat):

    def __init__(self, precision=4):
        FormatFloat.__init__(self, precision, scale=100.0)


class FormatThousands(FormatFloat):

    def __init__(self, precision=4):
        FormatFloat.__init__(self, precision, scale=0.001)


class FormatMillions(FormatFloat):

    def __init__(self, precision=4):
        FormatFloat.__init__(self, precision, scale=1e-06)


class FormatDate(FormatObj):

    def __init__(self, fmt):
        self.fmt = fmt

    def __hash__(self):
        return hash((self.__class__, self.fmt))

    def toval(self, x):
        if x is None:
            return 'None'
        else:
            return x.strftime(self.fmt)

    def fromstr(self, x):
        import dateutil.parser
        return dateutil.parser.parse(x).date()


class FormatDatetime(FormatDate):

    def __init__(self, fmt='%Y-%m-%d %H:%M:%S'):
        FormatDate.__init__(self, fmt)

    def fromstr(self, x):
        import dateutil.parser
        return dateutil.parser.parse(x)


defaultformatd = {np.bool_: FormatBool(), 
   np.int16: FormatInt(), 
   np.int32: FormatInt(), 
   np.int64: FormatInt(), 
   np.float32: FormatFloat(), 
   np.float64: FormatFloat(), 
   np.object_: FormatObj(), 
   np.string_: FormatString()}

def get_formatd(r, formatd=None):
    """build a formatd guaranteed to have a key for every dtype name"""
    if formatd is None:
        formatd = dict()
    for i, name in enumerate(r.dtype.names):
        dt = r.dtype[name]
        format = formatd.get(name)
        if format is None:
            format = defaultformatd.get(dt.type, FormatObj())
        formatd[name] = format

    return formatd


def csvformat_factory(format):
    format = copy.deepcopy(format)
    if isinstance(format, FormatFloat):
        format.scale = 1.0
        format.fmt = '%r'
    return format


def rec2txt(r, header=None, padding=3, precision=3, fields=None):
    """
    Returns a textual representation of a record array.

    *r*: numpy recarray

    *header*: list of column headers

    *padding*: space between each column

    *precision*: number of decimal places to use for floats.
        Set to an integer to apply to all floats.  Set to a
        list of integers to apply precision individually.
        Precision for non-floats is simply ignored.

    *fields* : if not None, a list of field names to print.  fields
    can be a list of strings like ['field1', 'field2'] or a single
    comma separated string like 'field1,field2'

    Example::

      precision=[0,2,3]

    Output::

      ID    Price   Return
      ABC   12.54    0.234
      XYZ    6.32   -0.076
    """
    if fields is not None:
        r = rec_keep_fields(r, fields)
    if cbook.is_numlike(precision):
        precision = [
         precision] * len(r.dtype)

    def get_type(item, atype=int):
        tdict = {None: int, int: float, float: str}
        try:
            atype(str(item))
        except:
            return get_type(item, tdict[atype])

        return atype

    def get_justify(colname, column, precision):
        ntype = type(column[0])
        if ntype == np.str or ntype == np.str_ or ntype == np.string0 or ntype == np.string_:
            length = max(len(colname), column.itemsize)
            return (
             0, length + padding, '%s')
        if ntype == np.int or ntype == np.int16 or ntype == np.int32 or ntype == np.int64 or ntype == np.int8 or ntype == np.int_:
            length = max(len(colname), np.max(map(len, map(str, column))))
            return (
             1, length + padding, '%d')
        if ntype == np.float or ntype == np.float32 or ntype == np.float64 or hasattr(np, 'float96') and ntype == np.float96 or ntype == np.float_:
            fmt = '%.' + str(precision) + 'f'
            length = max(len(colname), np.max(map(len, map((lambda x: fmt % x), column))))
            return (
             1, length + padding, fmt)
        return (0, max(len(colname), np.max(map(len, map(str, column)))) + padding, '%s')

    if header is None:
        header = r.dtype.names
    justify_pad_prec = [ get_justify(header[i], r.__getitem__(colname), precision[i]) for i, colname in enumerate(r.dtype.names) ]
    justify_pad_prec_spacer = []
    for i in range(len(justify_pad_prec)):
        just, pad, prec = justify_pad_prec[i]
        if i == 0:
            justify_pad_prec_spacer.append((just, pad, prec, 0))
        else:
            pjust, ppad, pprec = justify_pad_prec[i - 1]
            if pjust == 0 and just == 1:
                justify_pad_prec_spacer.append((just, pad - padding, prec, 0))
            elif pjust == 1 and just == 0:
                justify_pad_prec_spacer.append((just, pad, prec, padding))
            else:
                justify_pad_prec_spacer.append((just, pad, prec, 0))

    def format(item, just_pad_prec_spacer):
        just, pad, prec, spacer = just_pad_prec_spacer
        if just == 0:
            return spacer * ' ' + str(item).ljust(pad)
        else:
            if get_type(item) == float:
                item = prec % float(item)
            elif get_type(item) == int:
                item = prec % int(item)
            return item.rjust(pad)

    textl = []
    textl.append(('').join([ format(colitem, justify_pad_prec_spacer[j]) for j, colitem in enumerate(header) ]))
    for i, row in enumerate(r):
        textl.append(('').join([ format(colitem, justify_pad_prec_spacer[j]) for j, colitem in enumerate(row) ]))
        if i == 0:
            textl[0] = textl[0].rstrip()

    text = os.linesep.join(textl)
    return text


def rec2csv(r, fname, delimiter=',', formatd=None, missing='', missingd=None, withheader=True):
    """
    Save the data from numpy recarray *r* into a
    comma-/space-/tab-delimited file.  The record array dtype names
    will be used for column headers.

    *fname*: can be a filename or a file handle.  Support for gzipped
      files is automatic, if the filename ends in '.gz'

    *withheader*: if withheader is False, do not write the attribute
      names in the first row

    for formatd type FormatFloat, we override the precision to store
    full precision floats in the CSV file

    .. seealso::

        :func:`csv2rec`
            For information about *missing* and *missingd*, which can
            be used to fill in masked values into your CSV file.
    """
    if missingd is None:
        missingd = dict()

    def with_mask(func):

        def newfunc(val, mask, mval):
            if mask:
                return mval
            else:
                return func(val)

        return newfunc

    if r.ndim != 1:
        raise ValueError('rec2csv only operates on 1 dimensional recarrays')
    formatd = get_formatd(r, formatd)
    funcs = []
    for i, name in enumerate(r.dtype.names):
        funcs.append(with_mask(csvformat_factory(formatd[name]).tostr))

    fh, opened = cbook.to_filehandle(fname, 'wb', return_opened=True)
    writer = csv.writer(fh, delimiter=delimiter)
    header = r.dtype.names
    if withheader:
        writer.writerow(header)
    mvals = []
    for name in header:
        mvals.append(missingd.get(name, missing))

    ismasked = False
    if len(r):
        row = r[0]
        ismasked = hasattr(row, '_fieldmask')
    for row in r:
        if ismasked:
            row, rowmask = row.item(), row._fieldmask.item()
        else:
            rowmask = [
             False] * len(row)
        writer.writerow([ func(val, mask, mval) for func, val, mask, mval in zip(funcs, row, rowmask, mvals)
                        ])

    if opened:
        fh.close()
    return


def griddata(x, y, z, xi, yi, interp='nn'):
    """
    ``zi = griddata(x,y,z,xi,yi)`` fits a surface of the form *z* =
    *f*(*x*, *y*) to the data in the (usually) nonuniformly spaced
    vectors (*x*, *y*, *z*).  :func:`griddata` interpolates this
    surface at the points specified by (*xi*, *yi*) to produce
    *zi*. *xi* and *yi* must describe a regular grid, can be either 1D
    or 2D, but must be monotonically increasing.

    A masked array is returned if any grid points are outside convex
    hull defined by input data (no extrapolation is done).

    If interp keyword is set to '`nn`' (default),
    uses natural neighbor interpolation based on Delaunay
    triangulation.  By default, this algorithm is provided by the
    :mod:`matplotlib.delaunay` package, written by Robert Kern.  The
    triangulation algorithm in this package is known to fail on some
    nearly pathological cases. For this reason, a separate toolkit
    (:mod:`mpl_tookits.natgrid`) has been created that provides a more
    robust algorithm fof triangulation and interpolation.  This
    toolkit is based on the NCAR natgrid library, which contains code
    that is not redistributable under a BSD-compatible license.  When
    installed, this function will use the :mod:`mpl_toolkits.natgrid`
    algorithm, otherwise it will use the built-in
    :mod:`matplotlib.delaunay` package.

    If the interp keyword is set to '`linear`', then linear interpolation
    is used instead of natural neighbor. In this case, the output grid
    is assumed to be regular with a constant grid spacing in both the x and
    y directions. For regular grids with nonconstant grid spacing, you
    must use natural neighbor interpolation.  Linear interpolation is only valid if
    :mod:`matplotlib.delaunay` package is used - :mod:`mpl_tookits.natgrid`
    only provides natural neighbor interpolation.

    The natgrid matplotlib toolkit can be downloaded from
    http://sourceforge.net/project/showfiles.php?group_id=80706&package_id=142792
    """
    try:
        from mpl_toolkits.natgrid import _natgrid, __version__
        _use_natgrid = True
    except ImportError:
        import matplotlib.delaunay as delaunay
        from matplotlib.delaunay import __version__
        _use_natgrid = False

    if not griddata._reported:
        if _use_natgrid:
            verbose.report('using natgrid version %s' % __version__)
        else:
            verbose.report('using delaunay version %s' % __version__)
        griddata._reported = True
    if xi.ndim != yi.ndim:
        raise TypeError('inputs xi and yi must have same number of dimensions (1 or 2)')
    if xi.ndim != 1 and xi.ndim != 2:
        raise TypeError('inputs xi and yi must be 1D or 2D.')
    if not len(x) == len(y) == len(z):
        raise TypeError('inputs x,y,z must all be 1D arrays of the same length')
    if hasattr(z, 'mask'):
        if z.mask.ndim:
            x = x.compress(z.mask == False)
            y = y.compress(z.mask == False)
            z = z.compressed()
    if _use_natgrid:
        if interp != 'nn':
            raise ValueError('only natural neighor interpolation allowed when using natgrid toolkit in griddata.')
        if xi.ndim == 2:
            xi = xi[0, :]
            yi = yi[:, 0]
        _natgrid.seti('ext', 0)
        _natgrid.setr('nul', np.nan)
        x = x.astype(np.float)
        y = y.astype(np.float)
        z = z.astype(np.float)
        xo = xi.astype(np.float)
        yo = yi.astype(np.float)
        if min(xo[1:] - xo[0:-1]) < 0 or min(yo[1:] - yo[0:-1]) < 0:
            raise ValueError('output grid defined by xi,yi must be monotone increasing')
        zo = np.empty((yo.shape[0], xo.shape[0]), np.float)
        _natgrid.natgridd(x, y, z, xo, yo, zo)
    else:
        if xi.ndim != yi.ndim:
            raise TypeError('inputs xi and yi must have same number of dimensions (1 or 2)')
        if xi.ndim != 1 and xi.ndim != 2:
            raise TypeError('inputs xi and yi must be 1D or 2D.')
        if xi.ndim == 1:
            xi, yi = np.meshgrid(xi, yi)
        tri = delaunay.Triangulation(x, y)
        if interp == 'nn':
            interp = tri.nn_interpolator(z)
            zo = interp(xi, yi)
        elif interp == 'linear':
            dx = xi[0, 1:] - xi[0, 0:-1]
            dy = yi[1:, 0] - yi[0:-1, 0]
            epsx = np.finfo(xi.dtype).resolution
            epsy = np.finfo(yi.dtype).resolution
            if dx.max() - dx.min() > epsx or dy.max() - dy.min() > epsy:
                raise ValueError("output grid must have constant spacing when using interp='linear'")
            interp = tri.linear_interpolator(z)
            zo = interp[yi.min():yi.max():complex(0, yi.shape[0]),
             xi.min():xi.max():complex(0, xi.shape[1])]
        else:
            raise ValueError("interp keyword must be one of 'linear' (for linear interpolation) or 'nn' (for natural neighbor interpolation). Default is 'nn'.")
    if np.any(np.isnan(zo)):
        zo = np.ma.masked_where(np.isnan(zo), zo)
    return zo


griddata._reported = False

def less_simple_linear_interpolation(x, y, xi, extrap=False):
    """
    This function provides simple (but somewhat less so than
    :func:`cbook.simple_linear_interpolation`) linear interpolation.
    :func:`simple_linear_interpolation` will give a list of point
    between a start and an end, while this does true linear
    interpolation at an arbitrary set of points.

    This is very inefficient linear interpolation meant to be used
    only for a small number of points in relatively non-intensive use
    cases.  For real linear interpolation, use scipy.
    """
    if cbook.is_scalar(xi):
        xi = [xi]
    x = np.asarray(x)
    y = np.asarray(y)
    xi = np.asarray(xi)
    s = list(y.shape)
    s[0] = len(xi)
    yi = np.tile(np.nan, s)
    for ii, xx in enumerate(xi):
        bb = x == xx
        if np.any(bb):
            jj, = np.nonzero(bb)
            yi[ii] = y[jj[0]]
        elif xx < x[0]:
            if extrap:
                yi[ii] = y[0]
        elif xx > x[-1]:
            if extrap:
                yi[ii] = y[-1]
        else:
            jj, = np.nonzero(x < xx)
            jj = max(jj)
            yi[ii] = y[jj] + (xx - x[jj]) / (x[jj + 1] - x[jj]) * (y[jj + 1] - y[jj])

    return yi


def slopes(x, y):
    """
    :func:`slopes` calculates the slope *y*'(*x*)

    The slope is estimated using the slope obtained from that of a
    parabola through any three consecutive points.

    This method should be superior to that described in the appendix
    of A CONSISTENTLY WELL BEHAVED METHOD OF INTERPOLATION by Russel
    W. Stineman (Creative Computing July 1980) in at least one aspect:

      Circles for interpolation demand a known aspect ratio between
      *x*- and *y*-values.  For many functions, however, the abscissa
      are given in different dimensions, so an aspect ratio is
      completely arbitrary.

    The parabola method gives very similar results to the circle
    method for most regular cases but behaves much better in special
    cases.

    Norbert Nemec, Institute of Theoretical Physics, University or
    Regensburg, April 2006 Norbert.Nemec at physik.uni-regensburg.de

    (inspired by a original implementation by Halldor Bjornsson,
    Icelandic Meteorological Office, March 2006 halldor at vedur.is)
    """
    x = np.asarray(x, np.float_)
    y = np.asarray(y, np.float_)
    yp = np.zeros(y.shape, np.float_)
    dx = x[1:] - x[:-1]
    dy = y[1:] - y[:-1]
    dydx = dy / dx
    yp[1:(-1)] = (dydx[:-1] * dx[1:] + dydx[1:] * dx[:-1]) / (dx[1:] + dx[:-1])
    yp[0] = 2.0 * dy[0] / dx[0] - yp[1]
    yp[-1] = 2.0 * dy[-1] / dx[-1] - yp[-2]
    return yp


def stineman_interp(xi, x, y, yp=None):
    """
    Given data vectors *x* and *y*, the slope vector *yp* and a new
    abscissa vector *xi*, the function :func:`stineman_interp` uses
    Stineman interpolation to calculate a vector *yi* corresponding to
    *xi*.

    Here's an example that generates a coarse sine curve, then
    interpolates over a finer abscissa::

      x = linspace(0,2*pi,20);  y = sin(x); yp = cos(x)
      xi = linspace(0,2*pi,40);
      yi = stineman_interp(xi,x,y,yp);
      plot(x,y,'o',xi,yi)

    The interpolation method is described in the article A
    CONSISTENTLY WELL BEHAVED METHOD OF INTERPOLATION by Russell
    W. Stineman. The article appeared in the July 1980 issue of
    Creative Computing with a note from the editor stating that while
    they were:

      not an academic journal but once in a while something serious
      and original comes in adding that this was
      "apparently a real solution" to a well known problem.

    For *yp* = *None*, the routine automatically determines the slopes
    using the :func:`slopes` routine.

    *x* is assumed to be sorted in increasing order.

    For values ``xi[j] < x[0]`` or ``xi[j] > x[-1]``, the routine
    tries an extrapolation.  The relevance of the data obtained from
    this, of course, is questionable...

    Original implementation by Halldor Bjornsson, Icelandic
    Meteorolocial Office, March 2006 halldor at vedur.is

    Completely reworked and optimized for Python by Norbert Nemec,
    Institute of Theoretical Physics, University or Regensburg, April
    2006 Norbert.Nemec at physik.uni-regensburg.de
    """
    x = np.asarray(x, np.float_)
    y = np.asarray(y, np.float_)
    assert x.shape == y.shape
    if yp is None:
        yp = slopes(x, y)
    else:
        yp = np.asarray(yp, np.float_)
    xi = np.asarray(xi, np.float_)
    yi = np.zeros(xi.shape, np.float_)
    dx = x[1:] - x[:-1]
    dy = y[1:] - y[:-1]
    s = dy / dx
    idx = np.searchsorted(x[1:-1], xi)
    sidx = s.take(idx)
    xidx = x.take(idx)
    yidx = y.take(idx)
    xidxp1 = x.take(idx + 1)
    yo = yidx + sidx * (xi - xidx)
    dy1 = (yp.take(idx) - sidx) * (xi - xidx)
    dy2 = (yp.take(idx + 1) - sidx) * (xi - xidxp1)
    dy1dy2 = dy1 * dy2
    yi = yo + dy1dy2 * np.choose(np.array(np.sign(dy1dy2), np.int32) + 1, (
     (2 * xi - xidx - xidxp1) / ((dy1 - dy2) * (xidxp1 - xidx)),
     0.0,
     1 / (dy1 + dy2)))
    return yi


def inside_poly(points, verts):
    """
    *points* is a sequence of *x*, *y* points.
    *verts* is a sequence of *x*, *y* vertices of a polygon.

    Return value is a sequence of indices into points for the points
    that are inside the polygon.
    """
    poly = Path(verts)
    return [ idx for idx, p in enumerate(points) if poly.contains_point(p) ]


def poly_below(xmin, xs, ys):
    """
    Given a sequence of *xs* and *ys*, return the vertices of a
    polygon that has a horizontal base at *xmin* and an upper bound at
    the *ys*.  *xmin* is a scalar.

    Intended for use with :meth:`matplotlib.axes.Axes.fill`, eg::

      xv, yv = poly_below(0, x, y)
      ax.fill(xv, yv)
    """
    if ma.isMaskedArray(xs) or ma.isMaskedArray(ys):
        numpy = ma
    else:
        numpy = np
    xs = numpy.asarray(xs)
    ys = numpy.asarray(ys)
    Nx = len(xs)
    Ny = len(ys)
    assert Nx == Ny
    x = xmin * numpy.ones(2 * Nx)
    y = numpy.ones(2 * Nx)
    x[:Nx] = xs
    y[:Nx] = ys
    y[Nx:] = ys[::-1]
    return (x, y)


def poly_between(x, ylower, yupper):
    """
    Given a sequence of *x*, *ylower* and *yupper*, return the polygon
    that fills the regions between them.  *ylower* or *yupper* can be
    scalar or iterable.  If they are iterable, they must be equal in
    length to *x*.

    Return value is *x*, *y* arrays for use with
    :meth:`matplotlib.axes.Axes.fill`.
    """
    if ma.isMaskedArray(ylower) or ma.isMaskedArray(yupper) or ma.isMaskedArray(x):
        numpy = ma
    else:
        numpy = np
    Nx = len(x)
    if not cbook.iterable(ylower):
        ylower = ylower * numpy.ones(Nx)
    if not cbook.iterable(yupper):
        yupper = yupper * numpy.ones(Nx)
    x = numpy.concatenate((x, x[::-1]))
    y = numpy.concatenate((yupper, ylower[::-1]))
    return (x, y)


def is_closed_polygon(X):
    """
    Tests whether first and last object in a sequence are the same.  These are
    presumably coordinates on a polygonal curve, in which case this function
    tests if that curve is closed.
    """
    return np.all(X[0] == X[-1])


def contiguous_regions(mask):
    """
    return a list of (ind0, ind1) such that mask[ind0:ind1].all() is
    True and we cover all such regions

    TODO: this is a pure python implementation which probably has a much faster numpy impl
    """
    in_region = None
    boundaries = []
    for i, val in enumerate(mask):
        if in_region is None and val:
            in_region = i
        elif in_region is not None and not val:
            boundaries.append((in_region, i))
            in_region = None

    if in_region is not None:
        boundaries.append((in_region, i + 1))
    return boundaries


def cross_from_below(x, threshold):
    """
    return the indices into *x* where *x* crosses some threshold from
    below, eg the i's where::

      x[i-1]<threshold and x[i]>=threshold

    Example code::

        import matplotlib.pyplot as plt

        t = np.arange(0.0, 2.0, 0.1)
        s = np.sin(2*np.pi*t)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, s, '-o')
        ax.axhline(0.5)
        ax.axhline(-0.5)

        ind = cross_from_below(s, 0.5)
        ax.vlines(t[ind], -1, 1)

        ind = cross_from_above(s, -0.5)
        ax.vlines(t[ind], -1, 1)

        plt.show()

    .. seealso::

        :func:`cross_from_above` and :func:`contiguous_regions`

    """
    x = np.asarray(x)
    threshold = threshold
    ind = np.nonzero((x[:-1] < threshold) & (x[1:] >= threshold))[0]
    if len(ind):
        return ind + 1
    else:
        return ind


def cross_from_above(x, threshold):
    """
    return the indices into *x* where *x* crosses some threshold from
    below, eg the i's where::

      x[i-1]>threshold and x[i]<=threshold

    .. seealso::

        :func:`cross_from_below` and :func:`contiguous_regions`

    """
    x = np.asarray(x)
    ind = np.nonzero((x[:-1] >= threshold) & (x[1:] < threshold))[0]
    if len(ind):
        return ind + 1
    else:
        return ind


def vector_lengths(X, P=2.0, axis=None):
    """
    Finds the length of a set of vectors in *n* dimensions.  This is
    like the :func:`numpy.norm` function for vectors, but has the ability to
    work over a particular axis of the supplied array or matrix.

    Computes ``(sum((x_i)^P))^(1/P)`` for each ``{x_i}`` being the
    elements of *X* along the given axis.  If *axis* is *None*,
    compute over all elements of *X*.
    """
    X = np.asarray(X)
    return np.sum(X ** P, axis=axis) ** (1.0 / P)


def distances_along_curve(X):
    """
    Computes the distance between a set of successive points in *N* dimensions.

    Where *X* is an *M* x *N* array or matrix.  The distances between
    successive rows is computed.  Distance is the standard Euclidean
    distance.
    """
    X = np.diff(X, axis=0)
    return vector_lengths(X, axis=1)


def path_length(X):
    """
    Computes the distance travelled along a polygonal curve in *N* dimensions.

    Where *X* is an *M* x *N* array or matrix.  Returns an array of
    length *M* consisting of the distance along the curve at each point
    (i.e., the rows of *X*).
    """
    X = distances_along_curve(X)
    return np.concatenate((np.zeros(1), np.cumsum(X)))


def quad2cubic(q0x, q0y, q1x, q1y, q2x, q2y):
    """
    Converts a quadratic Bezier curve to a cubic approximation.

    The inputs are the *x* and *y* coordinates of the three control
    points of a quadratic curve, and the output is a tuple of *x* and
    *y* coordinates of the four control points of the cubic curve.
    """
    c1x, c1y = q0x + 0.6666666666666666 * (q1x - q0x), q0y + 0.6666666666666666 * (q1y - q0y)
    c2x, c2y = c1x + 0.3333333333333333 * (q2x - q0x), c1y + 0.3333333333333333 * (q2y - q0y)
    return (
     q0x, q0y, c1x, c1y, c2x, c2y, q2x, q2y)


def offset_line(y, yerr):
    """
    Offsets an array *y* by +/- an error and returns a tuple (y - err, y + err).

    The error term can be:

    * A scalar. In this case, the returned tuple is obvious.
    * A vector of the same length as *y*. The quantities y +/- err are computed
      component-wise.
    * A tuple of length 2. In this case, yerr[0] is the error below *y* and
      yerr[1] is error above *y*. For example::

        from pylab import *
        x = linspace(0, 2*pi, num=100, endpoint=True)
        y = sin(x)
        y_minus, y_plus = mlab.offset_line(y, 0.1)
        plot(x, y)
        fill_between(x, ym, y2=yp)
        show()

    """
    if cbook.is_numlike(yerr) or cbook.iterable(yerr) and len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = y - yerr[0], y + yerr[1]
    else:
        raise ValueError('yerr must be scalar, 1xN or 2xN')
    return (
     ymin, ymax)