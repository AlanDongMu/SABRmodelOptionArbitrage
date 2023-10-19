import pandas as pd
from calculator import Greek


def get_position(data):
    threshold = 0.02
    df = data.copy()
    df['delta'] = df.apply(lambda x: Greek.delta(x["S"], x["K"], x["T"], x["rf"], x['IV'], x["CorP"]), axis=1)

    # get signal
    df['diff'] = df['IV'] - df['sabr']
    df['signal'] = 0
    df.loc[df['diff'] >= threshold, 'signal'] = -1
    df.loc[df['diff'] <= -threshold, 'signal'] = 1
    # drop out 5 day before maturity
    df.loc[df['T'] <= 5/252, 'signal'] = 0

    df['position'] = 0
    # get option buy-sell pair and current target position
    for t in df['time'].unique():

        curr = df[df['time'] == t]
        # get option position
        Call_buy_signal_num = len(curr[(curr['signal'] == 1) & (curr['CorP'] == 1)])
        Call_sell_signal_num = len(curr[(curr['signal'] == -1) & (curr['CorP'] == 1)])
        Call_signal_num = min(Call_sell_signal_num, Call_buy_signal_num)
        if Call_signal_num != 0:
            curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 1), 'position'] = -100
            Call_sell_delta = curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 1), 'position'] \
                              * curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 1), 'delta']
            Call_buy_delta = - Call_sell_delta.sum() / Call_buy_signal_num
            curr.loc[(curr['signal'] == 1) & (curr['CorP'] == 1), 'position'] = curr.loc[(curr['signal'] == 1) & (
                        curr['CorP'] == 1), 'delta'].rdiv(1) * Call_buy_delta

        Put_buy_signal_num = len(curr[(curr['signal'] == 1) & (curr['CorP'] == 0)])
        Put_sell_signal_num = len(curr[(curr['signal'] == -1) & (curr['CorP'] == 0)])
        Put_signal_num = min(Put_sell_signal_num, Put_buy_signal_num)
        if Put_signal_num != 0:
            curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 0), 'position'] = -100
            Put_sell_delta = curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 0), 'position'] \
                             * curr.loc[(curr['signal'] == -1) & (curr['CorP'] == 0), 'delta']
            Put_buy_delta = - Put_sell_delta.sum() / Put_buy_signal_num
            curr.loc[(curr['signal'] == 1) & (curr['CorP'] == 0), 'position'] = curr.loc[(curr['signal'] == 1) & (
                        curr['CorP'] == 0), 'delta'].rdiv(1) * Put_buy_delta
        df.loc[df['time'] == t, 'position'] = curr['position'].values

    return df


def back_test(data):
    df = data.copy()
    df['last_position'] = 0
    last_t = None
    portfolio = pd.DataFrame(index=df['time'].unique(), columns=['value', 'return', 'cumulate_return'])
    # value: 当前持仓价值，或套利资金占用
    # return：前一期套利收益
    # cumulative return: 累计收益
    for t in df['time'].unique():
        curr = df[df['time'] == t]
        if last_t is None:
            portfolio.loc[t, 'value'] = sum(curr['position'] * curr['mkt'])
            portfolio.loc[t, 'return'] = 0
            portfolio.loc[t, 'cumulate_return'] = 0
        else:
            past = df[df['time'] == last_t]
            past_trade_option = past[past['position'] != 0].index
            curr.loc[past_trade_option, 'last_position'] = past.loc[past_trade_option, 'position']
            past_position_value = sum(curr['last_position'] * curr['mkt'])
            portfolio.loc[t, 'return'] = past_position_value - portfolio.loc[last_t, 'value']
            portfolio.loc[t, 'value'] = sum(curr['position'] * curr['mkt'])
            portfolio.loc[t, 'cumulate_return'] = portfolio.loc[t, 'return'] + portfolio.loc[last_t, 'cumulate_return']
        last_t = t
    return portfolio
