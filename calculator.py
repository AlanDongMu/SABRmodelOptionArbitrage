import numpy as np
from scipy.stats import norm
from scipy import optimize


class Greek:  # option greeks calculator
    def __init__(self):
        self.author = "Joey Zheng"

    @staticmethod
    def bsm(S, K, T, rf, sigma, CorP=1):
        sign = 1 if CorP == 1 else -1
        d1 = (np.log(S / K) + (rf + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        P = sign * (S * norm.cdf(sign * d1) - K * norm.cdf(sign * d2) * np.exp(-rf * T))
        return P

    @staticmethod
    def delta(S, K, T, rf, sigma, CorP=1):
        d1 = (np.log(S / K) + (rf + 0.5 * sigma * sigma) * T) / (sigma * np.sqrt(T))
        return norm.cdf(d1) - (1 - CorP)

    @staticmethod
    def vega(S, K, T, rf, sigma):
        temp = np.sqrt(T)
        d1 = (np.log(S / K) + (rf + 0.5 * sigma * sigma) * T) / (sigma * temp)
        return S * norm.pdf(d1) * temp

    @staticmethod
    def calc_IV(S, K, T, rf, mkt, CorP=1):
        P_adj = mkt
        sign = 1 if CorP == 1 else -1

        def price_comp(IV):
            d1 = (np.log(S / K) + (rf + 0.5 * IV ** 2) * T) / (IV * np.sqrt(T))
            d2 = d1 - IV * np.sqrt(T)
            Pt = sign * (S * norm.cdf(sign*d1) - K * norm.cdf(sign*d2) * np.exp(-rf * T))
            return P_adj - Pt

        IV = None
        i = 0
        s = -1
        # little noise to price if calculation is unsuccessful
        while IV is None and i <= 100:
            P_adj = mkt + i * s * 0.0001
            try:
                IV = optimize.brentq(price_comp, 0.001, 1, maxiter=1000)
            except:
                IV = None
                if s > 0:
                    i += 1
                s *= -1
        return IV

    @staticmethod
    def sabr(S, K, T, rf, alpha, beta, args):
        vega, rho = args
        F = S * np.exp(rf * T)
        z = (vega / alpha) * (F * K) ** ((1 - beta) / 2) * np.log(F / K)
        X = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))
        a = ((((1 - beta) * alpha) ** 2 / (24 * (F * K) ** (1 - beta)) +
              rho * beta * vega * alpha / (4 * (F * K) ** ((1 - beta) / 2)) +
              (2 - 3 * rho ** 2) * vega ** 2 / 24) * T + 1) * alpha
        b = ((F * K) ** ((1 - beta) / 2)) * (
                1 + ((1 - beta) * np.log(F / K)) ** 2 / 24 + ((1 - beta) * np.log(F / K)) ** 4 / 1920)
        return a / b * z / X

    @staticmethod
    def dsabr_r(S, K, T, rf, alpha, beta, args):
        vega, rho = args
        F = S * np.exp(rf * T)
        z = (vega / alpha) * (F * K) ** ((1 - beta) / 2) * np.log(F / K)
        X = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))
        a = ((((1 - beta) * alpha) ** 2 / (24 * (F * K) ** (1 - beta)) +
              rho * beta * vega * alpha / (4 * (F * K) ** ((1 - beta) / 2)) +
              (2 - 3 * rho ** 2) * vega ** 2 / 24) * T + 1) * alpha
        b = ((F * K) ** ((1 - beta) / 2)) * (
                1 + ((1 - beta) * np.log(F / K)) ** 2 / 24 + ((1 - beta) * np.log(F / K)) ** 4 / 1920)
        da_r = alpha * T * (vega * beta * alpha / (4 * (F * K) ** ((1 - beta) / 2)) - rho / 4 * vega ** 2)
        dX_r = 1 / (1 - rho) - \
               (z / np.sqrt(1 - 2 * rho * z + z ** 2) - 1) / (np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho)
        return da_r / b * z / X - a / b * z * dX_r / X ** 2

    @staticmethod
    def dsabr_v(S, K, T, rf, alpha, beta, args):
        vega, rho = args
        F = S * np.exp(rf * T)
        z = (vega / alpha) * (F * K) ** ((1 - beta) / 2) * np.log(F / K)
        X = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))
        a = ((((1 - beta) * alpha) ** 2 / (24 * (F * K) ** (1 - beta)) +
              rho * beta * vega * alpha / (4 * (F * K) ** ((1 - beta) / 2)) +
              (2 - 3 * rho ** 2) * vega ** 2 / 24) * T + 1) * alpha
        b = ((F * K) ** ((1 - beta) / 2)) * (
                1 + ((1 - beta) * np.log(F / K)) ** 2 / 24 + ((1 - beta) * np.log(F / K)) ** 4 / 1920)
        da_v = alpha * T * (rho * beta * alpha / (4 * (F * K) ** ((1 - beta) / 2)) +
                            (2 - 3 * rho ** 2) * vega / 12)
        dz_v = (F * K) ** ((1 - beta) / 2) * np.log(F / K) / alpha
        return da_v / b * z / X + a / b * (dz_v / X - z * dz_v / X ** 2)
