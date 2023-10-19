import numpy as np
import pandas as pd
from scipy import optimize
from calculator import Greek


# 3. estimate 1: calibration error
def mse(args, IV, S, K, T, rf, alpha, beta):  # optimize function: minimize MSE(IV, sabr)
    res, n = 0, len(S)
    for i in range(n):
        res += (IV[i] - Greek.sabr(S[i], K[i], T[i], rf[i], alpha, beta, args)) ** 2
    return res / n


def dmse(args, IV, S, K, T, rf, alpha, beta):  # derivative of optimize function
    dmse_v, dmse_r, n = 0, 0, len(S)
    for i in range(n):
        temp = IV[i] - Greek.sabr(S[i], K[i], T[i], rf[i], alpha, beta, args)
        dmse_v -= temp * Greek.dsabr_v(S[i], K[i], T[i], rf[i], alpha, beta, args)
        dmse_r -= temp * Greek.dsabr_r(S[i], K[i], T[i], rf[i], alpha, beta, args)
    res = np.array([dmse_v, dmse_r])
    return 2 * res / n


def opt_calib(IV, S, K, T, rf, alpha, beta):
    args_ = (IV, S, K, T, rf, alpha, beta, )
    x0_, bound_ = np.array([0.5, -0.5]), ((0, None), (-1, 1))
    res = optimize.minimize(mse, x0_, args=args_, method="Powell", bounds=bound_, jac=dmse,
                            tol=1e-16, options={"maxiter": 100})
    return res


def ols(Y, X):  # perform OLS, already check with statsmodels.api.OLS
    temp = np.c_[Y, X]
    temp = temp[~np.array(np.isnan(temp).any(axis=1)).reshape(len(temp))]
    Y, X = temp[:, 0], temp[:, 1:]
    W = np.linalg.inv((X.T).dot(X)).dot(X.T).dot(Y)  # W = ([X^TX]^-1)X^TY
    Y_ = np.dot(X, W)  # Y_hat = XW
    E = Y-Y_  # residual = Y - Y_hat
    return W, Y_, E


def rolling_ols(Y, X, window=252):
    W = np.repeat(np.nan, (window-1)*X.shape[1]).reshape((window-1), X.shape[1])
    n = len(Y)
    for i in range(window, n+1, 1):
        temp_W, temp_Y, temp_E = ols(Y[i-window:i, :], X[i-window:i, :])
        W = np.concatenate((W, temp_W.T), axis=0)
    return W


def calib_alpha(data, beta):
    df = data.copy()
    F = df['S'] * np.exp(df['rf'] * df['T'])
    df['ln_F'] = np.log(F)
    df['ln_IV'] = np.log(df['IV'])

    df['diff_SK'] = np.abs(df['S'] - df['K'])
    atm_option = df[(df['diff_SK'] == df['diff_SK'].min())]
    if len(atm_option) != 1:
        atm_option = atm_option[(atm_option['T'] == atm_option['T'].min()) & (atm_option['CorP'] == 1)]
    atm_option_index = atm_option.index
    alpha = np.exp(df["ln_IV"].loc[atm_option_index] + (1 - beta) * df["ln_F"].loc[atm_option_index])
    return alpha.values


def calib_para(data, beta):
    df = data.copy()
    df["IV"] = df.apply(lambda x: Greek.calc_IV(x["S"], x["K"], x["T"], x["rf"], x["mkt"], x["CorP"]), axis=1)
    df = df[(df["IV"] >= 0.01) & (df["IV"] < 1)]

    alpha = calib_alpha(df, beta)
    IV, S, K, T, rf = df["IV"].values, df["S"].values, df["K"].values, df["T"].values, df["rf"].values

    res = opt_calib(IV, S, K, T, rf, alpha, beta)
    para = res.x
    return para


def sim_sabr(data, beta, para):
    df = data.copy()
    df["IV"] = df.apply(lambda x: Greek.calc_IV(x["S"], x["K"], x["T"], x["rf"], x["mkt"], x["CorP"]), axis=1)
    df_sabr = pd.DataFrame()
    for t in df['time'].unique():
        temp = df.loc[t]
        alpha = calib_alpha(temp, beta)
        temp['sabr'] = temp.apply(lambda x: Greek.sabr(x["S"], x["K"], x["T"], x["rf"], alpha, beta, para)[0], axis=1)
        df_sabr = pd.concat([df_sabr, temp], axis=0)

    return df_sabr


def get_sabr(calib_data, trade_data):
    beta = 0.5
    para = calib_para(calib_data, beta)
    df = sim_sabr(trade_data, beta, para)

    return df
