import numpy as np
import matplotlib.pyplot as plt


def get_win_rate(return_list):
    win_num = 0
    for i in return_list:
        win_num += 1 if i > 0 else 0
    win_rate = win_num / len(return_list)
    return win_rate


def get_max_drawdown(cumulate_return_list):

    cumulate_return = np.array(cumulate_return_list[1:])
    max_hist_return = np.zeros(len(cumulate_return))
    a = cumulate_return[0]
    for i in range(len(cumulate_return)):
        if cumulate_return[i] > a:
            a = cumulate_return[i]
        max_hist_return[i] = a
    j = np.argmax((max_hist_return-cumulate_return)/cumulate_return) # max drawdown end point
    max_draw_down = - (max_hist_return[j]-cumulate_return[j])/cumulate_return[j]
    return max_draw_down


def get_static_metric(return_list):
    return_list = np.array(return_list)
    return_std = np.std(return_list)
    return_mean = np.mean(return_list)
    return_median = np.median(return_list)
    print('收益标准差: ', return_std)
    print('收益均值: ', return_mean)
    print('收益中位数: ', return_median)
    return return_std, return_mean, return_median


def get_metric(portfolio):
    return_std, return_mean, return_median = get_static_metric(portfolio['return'])
    win_rate = get_win_rate(portfolio['return'])
    max_drawdown = get_max_drawdown(portfolio['cumulate_return'])
    with open(r'metric_result/static_result.txt', 'w') as f:
        print('收益标准差: ', return_std, file=f)
        print('收益均值: ', return_mean, file=f)
        print('收益中位数: ', return_median, file=f)
        print('胜率: ', win_rate, file=f)
        print('累计收益最大回撤率: ', max_drawdown*100, '%', file=f)

    x = portfolio.index

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.figure(1)
    plt.plot(x, portfolio['value'], label='单次套利组合持仓价值')
    plt.legend(loc="lower right")
    plt.savefig(r'metric_result/单次套利组合持仓价值.png')

    plt.figure(2)
    plt.plot(x, portfolio['return'], label='单次套利收益')
    plt.legend(loc="lower right")
    plt.savefig(r'metric_result/单次套利收益.png')

    plt.figure(3)
    plt.plot(x, portfolio['cumulate_return'], label='累计套利收益')
    plt.legend(loc="lower right")
    plt.savefig(r'metric_result/累计套利收益.png')

