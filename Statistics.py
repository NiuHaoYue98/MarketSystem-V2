# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 21:17:24 2019

@author: apple
"""

import os
import pandas as pd


#统计高频交易者的订单成交
def count_deal(j):
    path = './Data' + str(j) + '/Deals'
    count = 0
    for fn in os.listdir(path): #fn 表示的是文件名
        count = count+1

    deal_num = []
    for i in range(1,count):
        filename = './Data' + str(j) + '/Deals/Deals' + str(i) + '.csv'
        df = pd.read_csv(filename)
        df['ask'] = df['AskId'].apply(lambda x: 1 if x[:4] == 'high' else 0)
        df['bid'] = df['BidId'].apply(lambda x: 1 if x[:4] == 'high' else 0)
        #print(df.head())
        df['total'] = df['ask'] + df['bid']
        temp = df[df.total >= 1]
        deal_num.append(len(temp))
    return deal_num

#统计高频交易者订单的提交率
def count_submit(j,total_high):
    ask_path = './Data' + str(j) + '/AskList'
    file_count = 0
    for fn in os.listdir(ask_path):
        file_count = file_count + 1

    ask_high = []   #记录高频提交卖单的序列
    bid_high = []   #记录高频提交买单的序列

    for i in range(1,file_count):
            ask_file_name = './Data' + str(j) + '/Asklist/AskList' + str(i) + '.csv'
            bid_file_name = './Data' + str(j) + '/BidList/BidList' + str(i) + '.csv'
            ask_df = pd.read_csv(ask_file_name)
            bid_df = pd.read_csv(bid_file_name)
            ask_df['ask'] = ask_df['TraderId'].apply(lambda x: 1 if x[:4] == 'high' else 0)
            bid_df['bid'] = bid_df['TraderId'].apply(lambda x: 1 if x[:4] == 'high' else 0)
            ask_high.append(ask_df['ask'].sum())
            bid_high.append(bid_df['bid'].sum())
    df = pd.DataFrame({'Round':range(1,file_count),'AskNum':ask_high,'BidNum':bid_high})
    df['SubmitSum'] = df['AskNum'] + df['BidNum']
    df['SubmitPer'] = df['SubmitSum'] / total_high
    return df

#统计交易者的财富分配
def count_wealth(MC,low_trader,high_trader,init_cash,init_stock):
    for j in range(MC):
        path = './Data' + str(j) + '/Deals'
        count = 0                   #交易轮次
        for fn in os.listdir(path): #fn 表示的是文件名
                count = count+1

        stock_low_df = pd.DataFrame({'TraderId':low_trader})
        stock_high_df = pd.DataFrame({'TraderId':high_trader})
        cash_low_df = pd.DataFrame({'TraderId':low_trader})
        cash_high_df = pd.DataFrame({'TraderId':high_trader})

        #集合竞价只有低频有财富变动
        filename = './Data' + str(j) + '/Deals/Deals' + str(0) + '.csv'
        df = pd.read_csv(filename)
        stock_low_data = [0 for i in range(len(low_trader))]
        cash_low_data = [0 for i in range(len(low_trader))]
        for index in range(df.shape[0]):
            askid = df.at[index,'AskId']
            bidid = df.at[index,'BidId']
            price = df.at[index,'Price']
            scale = df.at[index,'Scale']
            stock_low_data[int(askid[3:])] -= scale
            cash_low_data[int(askid[3:])] += scale * price
            stock_low_data[int(bidid[3:])] += scale
            cash_low_data[int(bidid[3:])] -= scale * price
            column_name = 'Round' + str(0)
            stock_low_df[column_name] = stock_low_data
            cash_low_df[column_name] = cash_low_data

        #连续竞价部分
        for i in range(1,count):
            filename = './Data' + str(j) + '/Deals/Deals' + str(i) + '.csv'
            df = pd.read_csv(filename)
            stock_low_data = [0 for i in range(len(low_trader))]
            stock_high_data = [0 for i in range(len(high_trader))]
            cash_low_data = [0 for i in range(len(low_trader))]
            cash_high_data = [0 for i in range(len(high_trader))]
            for index in range(df.shape[0]):
                askid = df.at[index,'AskId']
                bidid = df.at[index,'BidId']
                price = df.at[index,'Price']
                scale = df.at[index,'Scale']
                if askid[:4] == 'high':
                    stock_high_data[int(askid[4:])] -= scale
                    cash_high_data[int(askid[4:])] += scale * price
                else:
                    stock_low_data[int(askid[3:])] -= scale
                    cash_low_data[int(askid[3:])] += scale * price
                if bidid[:4] == 'high':
                    stock_high_data[int(bidid[4:])] += scale
                    cash_high_data[int(bidid[4:])] -= scale * price
                else:
                    stock_low_data[int(bidid[3:])] += scale
                    cash_low_data[int(bidid[3:])] -= scale * price
            column_name = 'Round' + str(i)
            stock_low_df[column_name] = stock_low_data
            stock_high_df[column_name] = stock_high_data
            cash_low_df[column_name] = cash_low_data
            cash_high_df[column_name] = cash_high_data

        stock_low_df['Final'] = init_stock
        stock_high_df['Final'] = init_stock
        cash_low_df['Final'] = init_cash
        cash_high_df['Final'] = init_cash
        for i in range(1,count):
            column_name = 'Round' + str(i)
            stock_low_df['Final'] = stock_low_df['Final'] + stock_low_df[column_name]
            stock_high_df['Final'] = stock_high_df['Final'] + stock_high_df[column_name]
            cash_low_df['Final'] += cash_low_df[column_name]
            cash_high_df['Final'] += cash_high_df[column_name]

        low_stock_file = './Data' + str(j) + '/LowStock.csv'
        stock_low_df.to_csv(low_stock_file, index=False)
        low_cash_file = './Data' + str(j) + '/LowCash.csv'
        cash_low_df.to_csv(low_cash_file,index=False)
        high_stock_file = './Data' + str(j) + '/HighStock.csv'
        stock_high_df.to_csv(high_stock_file,index=False)
        high_cash_file = './Data' + str(j) + '/HighCash.csv'
        cash_high_df.to_csv(high_cash_file,index=False)
        print(j,'财富统计完成！')

#统计交易者的财富分配
def distribution_wealth(MC,low_trader,high_trader,init_cash,init_stock):
    low_df = pd.DataFrame({'TraderId': low_trader,'InitCash':[init_cash for i in range(len(low_trader))],'InitStock':[init_stock for i in range(len(low_trader))]})
    high_df = pd.DataFrame({'TraderId': high_trader,'InitCash':[init_cash for i in range(len(high_trader))],'InitStock':[init_stock for i in range(len(high_trader))]})

    for j in range(MC):
        cash_column = 'MC' + str(j) + ' Cash'
        stock_column = 'MC' + str(j) + ' Stock'
        low_cash = pd.read_csv('./Data' + str(j) + '/LowCash.csv')
        low_df[cash_column] = low_cash['Final']
        low_stock = pd.read_csv('./Data' + str(j) + '/LowStock.csv')
        low_df[stock_column] = low_stock['Final']
        high_cash = pd.read_csv('./Data' + str(j) + '/HighCash.csv')
        high_df[cash_column] = high_cash['Final']
        high_stock = pd.read_csv('./Data' + str(j) + '/HighStock.csv')
        high_df[stock_column] = high_stock['Final']
        print(j,'财富分布统计完成！')

    low_df = low_df.append(high_df)
    low_df.to_csv('WealthDistribution.csv',index=False)

#统计闪电崩盘的发生频率
def count_crash(MC):
    data = pd.DataFrame(columns=['MC', 'Round','Present', 'Min', '30Round', 'Recover', 'Crash'])
    for j in range(MC):
        df = pd.read_csv('./Data' + str(j) + '/MarketPrice.csv')
        length = len(df)
        for i in range(length-30):
            present = df.at[i,'MarketPrice']
            last = df.at[i+30,'MarketPrice']
            min = df[i:i+30]['MarketPrice'].min()
            if last >= present:
                recover = True
                if (present - min)/min >= 0.05:
                    crash = True
                    data = data.append([
                        {'MC': j,'Round':i, 'Present': present, 'Min': min, '30Round': last, 'Recover': recover, 'Crash': crash}])
        for i in range(length-30,length):
            present = df.at[i,'MarketPrice']
            last = df.at[length-1,'MarketPrice']
            min = df[i:length-1]['MarketPrice'].min()
            if last >= present:
                recover = True
                if (present - min)/min >= 0.05:
                    crash = True
                    data = data.append([
                        {'MC': j, 'Round':i,'Present': present, 'Min': min, '30Round': last, 'Recover': recover, 'Crash': crash}])
        print(j,'闪电崩盘统计完成！')
    data.to_csv('CrashCount.csv',index=False)


if __name__ == '__main__':
    MC = 5                              #模拟次数
    total_high = 10                     #高频交易者数量
    total_low = 100                     #低频交易者数量
    init_cash = 200                     #初始现金数量
    init_stock = 2                      #初始股票数量
    low_trader = []                     #低频交易者列表
    high_trader = []                    #高频交易者列表

    for i in range(total_low):
        low_trader.append('low' + str(i))
    for i in range(total_high):
        high_trader.append('high' + str(i))

    #统计控制
    deal_count = False                  #高频交易者成交情况统计
    wealth_count = False                 #交易者财富情况统计
    wealth_distribution = False          #交易者财富变动及分布
    crash_count = True


    #高频交易者相关统计
    if deal_count:
        for j in range(MC):
            df = count_submit(j,total_high)
            print(j,'高频订单提交率统计完成',len(df))
            deal_num = count_deal(j)
            print(j,'高频订单成交率统计完成',len(deal_num))
            df['DealNum'] = deal_num
            df['DealPer'] = df['DealNum'] / df['SubmitSum']
            out_file = './Data' + str(j) + '/high_count.csv'
            df.to_csv(out_file, index=False)
            print(j,'高频统计写入文件完成！')

    #财富统计
    if wealth_count:
        count_wealth(MC,low_trader,high_trader,init_cash,init_stock)

    #财富变动及分布统计
    if wealth_distribution:
        distribution_wealth(MC,low_trader,high_trader,init_cash,init_stock)

    #闪电崩盘统计
    if crash_count:
        count_crash(MC)


