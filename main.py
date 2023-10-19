import pandas as pd
import datetime as dt
from calibrator import get_sabr
from metric import get_metric
from strategy import get_position, back_test


def main():
    data_file = r'data/data_demo.csv'
    data = pd.read_csv(data_file)
    data['time'] = pd.to_datetime(data['time'])
    data['date'] = data['time'].dt.date
    data['rf'] = 0.02
    print('Data load success')
    train_start = dt.datetime.strptime("2021-05-01 10:00:00", "%Y-%m-%d %H:%M:%S")
    train_end = dt.datetime.strptime("2021-05-31 10:00:00", "%Y-%m-%d %H:%M:%S")
    data = data[(data['time'] >= train_start) & (data['time'] <= train_end)]
    data = data.set_index(['date', 'time', 'code'], drop=False)
    position_data = pd.DataFrame()
    print('Date Start:', train_start.date())
    print('Date end:', train_end.date())
    print('Total Compute date num:', len(data.index.levels[0]))
    for i in range(len(data.index.levels[0])-1):
        print('Computing date:', data.index.levels[0][i+1], "  num: ", i+1, "/", len(data.index.levels[0])-1)
        calib_data = data.loc[data.index.levels[0][i]]
        trade_data = data.loc[data.index.levels[0][i+1]]
        trade_data = get_sabr(calib_data, trade_data)
        trade_data = get_position(trade_data)
        position_data = pd.concat([position_data, trade_data], axis=0)
    print('Position Getting success')
    position_data.to_csv(r'data/position.csv')
    print('Start Back Test')
    portfolio = back_test(position_data)
    portfolio.to_csv(r'data/portfolio.csv')
    print(portfolio)
    get_metric(portfolio)


if __name__ == '__main__':
    portfolio= pd.read_csv(r'data/portfolio.csv')
    print(portfolio)
    get_metric(portfolio)

