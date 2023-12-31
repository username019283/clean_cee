# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\solvers\UkrOpt\amsg2p.pyc
# Compiled at: 2012-12-08 11:04:59
from numpy import dot, diag, ones, zeros, sqrt
from openopt.kernel.ooMisc import norm

def amsg2p(f, df, x0, epsilon, f_opt, gamma, callback=lambda x, f: False):
    f0 = f(x0)
    if f0 - f_opt <= epsilon:
        return (x0, 0)
    else:
        x, n = x0.copy(), x0.size
        df0 = df(x0)
        ndf = norm(df0)
        h, dzeta, p, B = (gamma * (f0 - f_opt) / ndf, df0 / ndf, zeros(n), diag(ones(n, 'float64')))
        k = 0
        while True:
            k += 1
            x -= h * dot(B, dzeta)
            F = f(x)
            r = callback(x, F)
            if r not in (0, False, None):
                break
            if F - f_opt <= epsilon:
                break
            DF = df(x)
            DF_dilated = dot(B.T, DF)
            nDF_dilated = norm(DF_dilated)
            dzeta_new, h = DF_dilated / nDF_dilated, gamma * (F - f_opt) / nDF_dilated
            lambda1, lambda2 = -dot(p, dzeta_new), -dot(dzeta, dzeta_new)
            c1, c2 = lambda1 > 0, lambda2 > 0
            p = (lambda1 * p + lambda2 * dzeta) / sqrt(lambda1 ** 2 + lambda2 ** 2) if c1 and c2 else dzeta if c2 and not c1 else zeros(n) if not c1 and not c2 else p
            mu = dot(p, dzeta_new)
            if -1 < mu < 0:
                S = sqrt(1 - mu ** 2)
                nu = (1 / S - 1) * dzeta_new - mu / S * p
                B += dot(dot(B, nu.reshape(n, 1)), dzeta_new.reshape(1, n))
                h /= S
                p = (p - mu * dzeta_new) / S
            else:
                p = zeros(n)
            dzeta = dzeta_new

        return (
         x, k)