import numpy as np
import pandas as pd
from Orders import Deal

class Market:
    NL = 100           #普通程式化交易者数量
    NH = 10             #高频交易者数量
    t = 0               #当前周期
    d_c_list = []       #图表交易者的成交量
    d_f_list = []       #基本面交易者的成交量
    s = 0.01            #最小报价单位
    delta = 0.0001      #资产基本面价格漂移参数
    sigma = 0.01        #资产基本面价格震荡标准差
    y_t = []            #资产基本面价格震荡列表

    #初始化：生成基本面价格震荡列表
    def __init__(self,r):
        self.F_list = [100, 100]  # 资产基本面价格列表
        self.P_list = [100, 100]  # 资产价格列表
        np.random.seed(r)
        self.y_t = np.random.normal(0,self.sigma,1200)

    #基本面价格生成机制
    def gen_fundamental_price(self):
        F_t_1 = self.F_list[-1]
        F_t = F_t_1 * (1+self.delta) * (1+self.y_t[self.t])
        F_t = round(F_t,2)
        self.F_list.append(F_t)

    #集合竞价匹配
    def call_auction(self,AskList,BidList,price):
        deals = pd.DataFrame(columns=['AskId', 'BidId', 'Scale', 'Price', 'Time','AskTime','BidTime','AskPrice','BidPrice','AskScale','BidScale'])
        trader_list = []
        bid_start = 0
        if AskList.shape[0] == 0 or BidList.shape[0] == 0:
            return deals, AskList, BidList,trader_list,price

        for ask_index in range(AskList.shape[0]):
            for bid_index in range(bid_start, BidList.shape[0]):
                if AskList.at[ask_index, 'Price'] <= BidList.at[bid_index, 'Price']:
                    # 可以成交
                    deal = Deal()
                    # 双方交易者
                    deal.askID = AskList.at[ask_index, 'TraderId']
                    deal.bidID = BidList.at[bid_index, 'TraderId']
                    # 成交时间
                    deal.time = max(AskList.at[ask_index, 'Time'], BidList.at[bid_index, 'Time'])
                    deal.asktime = AskList.at[ask_index, 'Time']
                    deal.bidtime = BidList.at[bid_index, 'Time']
                    # 交易量
                    ask_scale = AskList.at[ask_index, 'Scale']
                    bid_scale = BidList.at[bid_index, 'Scale']
                    deal.askscale = ask_scale
                    deal.bidscale = bid_scale
                    deal.scale = min(ask_scale, bid_scale)
                    # 成交价格
                    price = (BidList.at[bid_index, 'Price'] + AskList.at[ask_index, 'Price'])/2
                    deal.askprice = AskList.at[ask_index, 'Price']
                    deal.bidprice = BidList.at[bid_index, 'Price']
                    deals.price = price
                    deals = deals.append([{'Time': deal.time, 'AskId': deal.askID, 'BidId': deal.bidID,
                                           'Price': deal.price, 'Scale': deal.scale,'AskTime':deal.asktime,'BidTime':deal.bidtime,'AskPrice':deal.askprice,'BidPrice':deal.bidprice,'AskScale':deal.askscale,'BidScale':deal.bidscale}])
                    # 订单簿变更
                    if ask_scale < bid_scale:
                        BidList.at[bid_index, 'Scale'] = BidList.at[bid_index, 'Scale'] - AskList.at[ask_index, 'Scale']
                        trader_list.append(AskList.at[ask_index, 'TraderId'])
                        AskList.drop(ask_index, inplace=True)
                    else:
                        AskList.at[ask_index, 'Scale'] = AskList.at[ask_index, 'Scale'] - BidList.at[bid_index, 'Scale']
                        trader_list.append(BidList.at[bid_index, 'TraderId'])
                        BidList.drop(bid_index, inplace=True)
                        bid_start += 1
                        continue
                    break
                else:
                    break
        deals['Price'] = price
        # 更新剩余市场订单信息
        AskList['SuspendTime'] = AskList['SuspendTime'] - 1
        BidList['SuspendTime'] = BidList['SuspendTime'] - 1
        trader_list = trader_list + list(AskList[AskList.SuspendTime < 1].TraderId) + list(
            BidList[BidList.SuspendTime < 1].TraderId)
        AskList.reset_index(inplace=True, drop=True)
        BidList.reset_index(inplace=True, drop=True)
        return deals, AskList, BidList, trader_list, price

    # 订单排序
    def sort_orders(self,AskList, BidList):
        AskList.sort_values(['Price', 'Time'], inplace=True)
        AskList.reset_index(drop=True, inplace=True)
        BidList['TimeRank'] = BidList['Time'].groupby(BidList['Price']).rank(ascending=False)
        BidList.sort_values(['Price', 'TimeRank'], ascending=False, inplace=True)
        BidList.reset_index(drop=True, inplace=True)
        BidList.drop(['TimeRank'], axis=1, inplace=True)
        return AskList, BidList

    #等价连续竞价匹配:需要的变量是原始的订单簿和本周期内提交的订单簿,本轮的时间（调用时直接传matket.t就可以）
    def continuous_auction(self,AskList,BidList,old_price,t):
        deals = pd.DataFrame(columns=['AskId', 'BidId', 'Scale', 'Price', 'Time','AskTime','BidTime','AskPrice','BidPrice','AskScale','BidScale'])
        trader_list = []
        if AskList.shape[0] == 0 or BidList.shape[0] == 0:
            return deals, AskList, BidList,trader_list,old_price

        bid_start = 0

        #筛选出本周期之前的订单簿，并获得本轮的新提交的订单
        old_asklist = AskList[AskList.Time < t]
        old_bidlist = BidList[BidList.Time < t]
        new_asklist = AskList[AskList.Time >= t]
        new_bidlist = BidList[BidList.Time >= t]

        #按最短时间间隔开始遍历
        time_scale = np.arange(0, 1, 0.01)
        for s in time_scale:
            this_time = t+s
            #获取当前时间的订单
            temp_asklist = new_asklist[new_asklist.Time == this_time]
            temp_bidlist = new_bidlist[new_bidlist.Time == this_time]
            #加入旧订单簿中,形成总订单，接下来就可以开始匹配
            old_asklist = old_asklist.append(temp_asklist,ignore_index=True)
            old_bidlist = old_bidlist.append(temp_bidlist,ignore_index=True)
            #订单簿排序
            old_asklist,old_bidlist = self.sort_orders(old_asklist,old_bidlist)
            #开始匹配成交
            for ask_index in range(old_asklist.shape[0]):
                for bid_index in range(bid_start, old_bidlist.shape[0]):
                    if old_asklist.at[ask_index, 'Price'] <= old_bidlist.at[bid_index, 'Price']:
                        # 可以成交
                        deal = Deal()
                        # 双方交易者
                        deal.askID = old_asklist.at[ask_index, 'TraderId']
                        deal.bidID = old_bidlist.at[bid_index, 'TraderId']
                        # 成交时间
                        deal.time = max(old_asklist.at[ask_index, 'Time'], old_bidlist.at[bid_index, 'Time'])
                        deal.asktime = old_asklist.at[ask_index, 'Time']
                        deal.bidtime = old_bidlist.at[bid_index, 'Time']
                        # 交易量
                        ask_scale = old_asklist.at[ask_index, 'Scale']
                        bid_scale = old_bidlist.at[bid_index, 'Scale']
                        deal.askscale = ask_scale
                        deal.bidscale = bid_scale
                        deal.scale = min(ask_scale, bid_scale)
                        # 成交价格
                        deal.askprice = old_asklist.at[ask_index, 'Price']
                        deal.bidprice = old_bidlist.at[bid_index, 'Price']
                        if old_asklist.at[ask_index, 'Time'] == deal.time:
                            deal.price = old_bidlist.at[bid_index, 'Price']
                        elif old_bidlist.at[bid_index, 'Time'] == deal.time:
                            deal.price = old_asklist.at[ask_index, 'Price']
                        else:
                            if ask_scale < bid_scale:
                                deal.price = old_asklist.at[ask_index, 'Price']
                            else:
                                deal.price = old_bidlist.at[bid_index, 'Price']
                        price = deal.price
                        deals = deals.append([{'Time': deal.time, 'AskId': deal.askID, 'BidId': deal.bidID,
                                               'Price': deal.price, 'Scale': deal.scale,'AskTime':deal.asktime,'BidTime':deal.bidtime,'AskPrice':deal.askprice,'BidPrice':deal.bidprice,'AskScale':deal.askscale,'BidScale':deal.bidscale}])
                        # 订单簿变更
                        if ask_scale < bid_scale:
                            old_bidlist.at[bid_index, 'Scale'] = old_bidlist.at[bid_index, 'Scale'] - old_asklist.at[ask_index, 'Scale']
                            trader_list.append(old_asklist.at[ask_index, 'TraderId'])
                            old_asklist.drop(ask_index, inplace=True)
                        else:
                            old_asklist.at[ask_index, 'Scale'] = old_asklist.at[ask_index, 'Scale'] - old_bidlist.at[bid_index, 'Scale']
                            trader_list.append(old_bidlist.at[bid_index, 'TraderId'])
                            old_bidlist.drop(bid_index, inplace=True)
                            bid_start += 1
                            continue
                        break
                    else:
                        break
                else:
                    # 内层for循环break到这里，内层break代表目前不能成交，所以直接跳出循环
                    continue
                break

        #确定市场价格
        if deals.Scale.sum() == 0:
            market_price = old_price
        else:
            market_price = price
        # 更新剩余市场订单信息
        AskList['SuspendTime'] = AskList['SuspendTime'] - 1
        BidList['SuspendTime'] = BidList['SuspendTime'] - 1
        trader_list = trader_list + list(AskList[AskList.SuspendTime < 1].TraderId) + list(
            BidList[BidList.SuspendTime < 1].TraderId)
        AskList = AskList[-AskList.TraderId.isin(trader_list)]
        BidList = BidList[-BidList.TraderId.isin(trader_list)]
        AskList.reset_index(inplace=True, drop=True)
        BidList.reset_index(inplace=True, drop=True)
        return deals, AskList, BidList, trader_list, market_price


