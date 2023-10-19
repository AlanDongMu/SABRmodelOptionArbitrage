import numpy as np
import pandas as pd
import datetime as dt


def get_data(stock_file, option_file):
    stock_data = pd.read_csv(stock_file)
    stock_data['time'] = pd.to_datetime(stock_data['time'])
    option_data = pd.read_csv(option_file)
    stock_data = stock_data.set_index('time')
    print("Data load success")

    data = pd.DataFrame()
    contract_num = (len(option_data.columns) - 1) * 0.5
    print("Total Contract Num:", int(contract_num))
    for i in range(int(contract_num)):
        contract_index = 2 * i + 1
        contract_name = option_data.columns[contract_index]
        call_put = contract_name[6]
        strike_price = float(contract_name[12:17]) / 1000
        time_index = pd.to_datetime(option_data.iloc[:, contract_index])

        contract_data = option_data.iloc[2:, contract_index:contract_index + 2].copy()
        contract_data.columns = ['time', 'mkt']
        contract_data['time'] = pd.to_datetime(contract_data['time'])
        contract_data = contract_data.set_index('time')
        lvi_index = contract_data.last_valid_index()
        contract_data = contract_data[:lvi_index]
        contract_start = contract_data.index.tolist()[0]
        contract_end = contract_data.index.tolist()[-1]
        contract_data['code'] = contract_name
        contract_data['K'] = strike_price
        contract_data['S'] = stock_data[contract_start:contract_end]['close'].values.tolist()
        contract_data['T'] = [int(t / 8) / 252 for t in range(len(contract_data), 0, -1)]
        contract_data['CorP'] = 1 if call_put == "C" else 0

        data = pd.concat([data, contract_data], axis=0)
        #print(contract_name)
        if i % 50 == 0:
            print("Contracts collected: ", i, "/", str(int(contract_num)))
    data = data.sort_index()
    data.to_csv(r'data/data.csv')


if __name__ == '__main__':
    stock_file = r"data\raw_data\stock_30min.csv"
    option_file = r"data\raw_data\option_30min.csv"
    '''
    train_start = dt.datetime.strptime("2021-05-01 10:00:00", "%Y-%m-%d %H:%M:%S")
    train_end = dt.datetime.strptime("2021-05-31 10:00:00", "%Y-%m-%d %H:%M:%S")

    train_start = dt.datetime.strptime(train_date_start, "%Y-%m-%d %H:%M:%S")
    train_end = dt.datetime.strptime(train_date_start, "%Y-%m-%d %H:%M:%S")
    test_start = dt.datetime.strptime(test_date_start, "%Y-%m-%d %H:%M:%S")
    test_end = dt.datetime.strptime(test_date_end, "%Y-%m-%d %H:%M:%S")
    '''
    get_data(stock_file, option_file)
