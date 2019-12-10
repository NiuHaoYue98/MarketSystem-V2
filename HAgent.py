import numpy as np
import Agent
from Orders import Deal
import pandas as pd
import copy


class HAgent(Agent.Agent):
    eita = 0                #激活分布范围
    kappa = 0               #订单价格波动
    lamb = 0.625            #指令规模加权参数
    order_flag = False      #交易者市场中是否有订单


    def __init__(self,i):
        #初始化编号
        self.traderID = 'high' + str(i)
        #产生激活分布范围
        min_eita = 0        #最小激活值
        max_eita = 0.005      #最大激活值
        self.eita = np.random.uniform(min_eita,max_eita)
        #产生订单价格波动
        min_kappa = 0
        max_kappa = 0.01
        self.kappa = np.random.uniform(min_kappa,max_kappa)
        #产生挂单时间
        self.gamma = 1
        #计时因子：计算上一次提交订单距今的时间
        self.time = self.gamma + 1


    #生成订单
    def gen_order(self,para,Asklist,Bidlist):
        #判断是否参与市场
        if not self.judge_participate(para.true_delta):
            para.ask_scale = np.delete(para.ask_scale,0)
            para.bid_scale = np.delete(para.bid_scale,0)
            return
        self.order_flag = True
        self.order.traderID = self.traderID
        #确定订单时间及剩余时间
        self.order.time = para.t + np.random.randint(30,100)/100
        self.order.suspend_time = self.gamma
        #确定订单方向、指令规模、订单价格
        di = np.random.rand()
        if di >= 0.5:
            self.order.direction = 1
            #best_ask_price = self.gen_best_price(self.order.time,Asklist)
            best_ask_price = para.best_ask_price
            self.order.price = self.gen_best_price(self.order.time,Asklist,best_ask_price)
            self.order.scale = self.gen_order_scale(para.bid_scale)
        else:
            self.order.direction = 0
            #best_bid_price = self.gen_best_price(self.order.time,Bidlist)
            best_bid_price = para.best_bid_price
            self.order.price = self.gen_best_price(self.order.time,Bidlist,best_bid_price)
            self.order.scale = self.gen_order_scale(para.ask_scale)
            self.kappa = -self.kappa
        if self.order.scale == 0:
            return
        para.ask_scale = np.delete(para.ask_scale, 0)
        para.bid_scale = np.delete(para.bid_scale, 0)
        return self.order
        # flag = self.judge_cancle(self.order,Asklist,Bidlist)
        # if flag:
        #     return self.order

    #判断是否参与市场
    def judge_participate(self,true_delta):
        if self.order_flag:
            self.time += 1
            return False
        else:
            if self.time > self.gamma:
                self.time = 2
                if true_delta <= self.eita:
                    return False
                else:
                    return True
            else:
                self.time += 1
                return False


    #【现】产生最优价格
    def gen_best_price(self,time,orderlist,best_price):
        temp_order = orderlist[orderlist.Time < time]
        if len(temp_order) != 0:
            best_price = temp_order.iloc[0].at['Price']
        best_price = best_price * (1+self.kappa)
        best_price = round(best_price,2)
        self.kappa = abs(self.kappa)
        return best_price

    #【旧】确定订单价格
    def gen_order_price(self,best_price):
        p_t = best_price * (1+self.kappa)
        self.kappa = abs(self.kappa)
        p_t = round(p_t,2)
        return p_t

    #确定指令规模
    def gen_order_scale(self,scale_list):
        scale = scale_list[0]
        scale = round(scale,4)
        return scale

    #确定指令规模
    # def gen_order_scale(self,avg_scale,total):
    #     scale = np.random.poisson(self.lamb * avg_scale)
    #     #订单限制1
    #     min_scale = 0.001
    #     max_scale = avg_scale * total/ 4
    #
    #     while scale < min_scale :
    #         scale = np.random.poisson(self.lamb * avg_scale)
    #     if scale > max_scale:
    #         scale = max_scale
    #     #print(max_scale,scale)
    #     #【待完成】总持仓限制2
    #     scale = round(scale,2)
    #     return scale

    #确定订单价格

    #订单排序
    def sort_orders(self,AskList, BidList):
        AskList.sort_values(['Price', 'Time'], inplace=True)
        AskList.reset_index(drop=True, inplace=True)
        BidList['TimeRank'] = BidList['Time'].groupby(BidList['Price']).rank(ascending=False)
        BidList.sort_values(['Price', 'TimeRank'], ascending=False, inplace=True)
        BidList.reset_index(drop=True, inplace=True)
        BidList.drop(['TimeRank'], axis=1, inplace=True)
        return AskList, BidList

    #撤单判断
    # def judge_cancle(self,order,asklist,bidlist):
    #     return True
    # def judge_cancle(self,order,asklist,bidlist):
    #     AskList = copy.deepcopy(asklist)
    #     BidList = copy.deepcopy(bidlist)
    #     if AskList.shape[0] == 0 or BidList.shape[0] == 0:
    #         return True
    #     if order.direction == 0:
    #         AskList = AskList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
    #     else:
    #         BidList = BidList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
    #     AskList, BidList = self.sort_orders(AskList, BidList)
    #
    #     deals = pd.DataFrame(columns=['AskId', 'BidId', 'Scale', 'Price', 'Time'])
    #     trader_list = []
    #     bid_start = 0
    #     for ask_index in range(AskList.shape[0]):
    #         for bid_index in range(bid_start, BidList.shape[0]):
    #             if AskList.at[ask_index, 'Price'] <= BidList.at[bid_index, 'Price']:
    #                 # 可以成交
    #                 deal = Deal()
    #                 # 双方交易者
    #                 deal.askID = AskList.at[ask_index, 'TraderId']
    #                 deal.bidID = BidList.at[bid_index, 'TraderId']
    #                 # 成交时间
    #                 deal.time = max(AskList.at[ask_index, 'Time'], BidList.at[bid_index, 'Time'])
    #                 # 交易量
    #                 ask_scale = AskList.at[ask_index, 'Scale']
    #                 bid_scale = BidList.at[bid_index, 'Scale']
    #                 deal.scale = min(ask_scale, bid_scale)
    #                 # 成交价格
    #                 if AskList.at[ask_index, 'Time'] == deal.time:
    #                     deal.price = BidList.at[bid_index, 'Price']
    #                 elif BidList.at[bid_index, 'Time'] == deal.time:
    #                     deal.price = AskList.at[ask_index, 'Price']
    #                 else:
    #                     if ask_scale < bid_scale:
    #                         deal.price = AskList.at[ask_index, 'Price']
    #                     else:
    #                         deal.price = BidList.at[bid_index, 'Price']
    #                 deals = deals.append([{'Time': deal.time, 'AskId': deal.askID, 'BidId': deal.bidID,
    #                                        'Price': deal.price, 'Scale': deal.scale}])
    #                 # 订单簿变更
    #                 if ask_scale < bid_scale:
    #                     BidList.at[bid_index, 'Scale'] = BidList.at[bid_index, 'Scale'] - AskList.at[ask_index, 'Scale']
    #                     trader_list.append(AskList.at[ask_index, 'TraderId'])
    #                     AskList.drop(ask_index, inplace=True)
    #                 else:
    #                     AskList.at[ask_index, 'Scale'] = AskList.at[ask_index, 'Scale'] - BidList.at[bid_index, 'Scale']
    #                     trader_list.append(BidList.at[bid_index, 'TraderId'])
    #                     BidList.drop(bid_index, inplace=True)
    #                     bid_start += 1
    #                     continue
    #                 break
    #             else:
    #                 break
    #     deals['temp'] = deals['Price'] * deals['Scale']
    #     if deals.Scale.sum() == 0:
    #         return True
    #     else:
    #         market_price = deals.temp.sum() / deals.Scale.sum()
    #     deals.drop(['temp'], axis=1, inplace=True)
    #     # 更新剩余市场订单信息
    #     if order.traderID in trader_list:
    #         if order.direction == 0:
    #             temp_price = deals[deals.AskId==order.traderID]['Price'].values[0]
    #             di = -1
    #         else:
    #             temp_price = deals[deals.BidId==order.traderID]['Price'].values[0]
    #             di = 1
    #         pi = (market_price - temp_price) * di
    #         if pi < 0:
    #             print("High agent cancle the order!")
    #             return False
    #         else:
    #             return True
    #     else:
    #         return True

class H_Parameters():
    agent_num = 0           #高频交易者数量
    t = 0                   #交易周期
    true_delta = 0          #判断市场参与的市场价格变动
    best_ask_price = 0      #当前市场中的最优卖价
    best_bid_price = 0      #当前市场中的最优卖价
    ask_scale = []          #卖单指令规模
    bid_scale = []          #买单指令规模
    lamb = 0.0625

    def __init__(self,market,AskList,BidList):
        self.agent_num = market.NH
        self.t = market.t
        self.true_delta = abs((market.P_list[-1] - market.P_list[-2]) / market.P_list[-2])
        # 如果某一方没有订单怎么办？
        if len(AskList) == 0:
            self.best_ask_price = market.P_list[-1]
        else:
            self.best_ask_price = AskList.iloc[0].at['Price']
        if len(BidList) == 0:
            self.best_bid_price = market.P_list[-1]
        else:
            self.best_bid_price = BidList.iloc[0].at['Price']
        ask_num = len(AskList)
        bid_num = len(BidList)
        if ask_num != 0:
            avg_ask_volumn = int(10 * self.lamb * AskList.Scale.sum() / ask_num)
        else:
            avg_ask_volumn = 3
        if bid_num != 0:
            avg_bid_volumn = int(10 * self.lamb * BidList.Scale.sum() / bid_num)
        else:
            avg_bid_volumn = 3
        ask_scale = np.random.poisson(avg_bid_volumn,self.agent_num)
        bid_scale = np.random.poisson(avg_ask_volumn,self.agent_num)
        max_ask_scale = AskList.Scale.sum() / 4
        max_bid_scale = BidList.Scale.sum() / 4

        for i in range(self.agent_num):
            if ask_scale[i] == 0:
                ask_scale[i] = 1
            if bid_scale[i] == 0:
                bid_scale[i] = 1
            if ask_scale[i] > max_ask_scale:
                ask_scale[i] = max_ask_scale
            if bid_scale[i] > max_bid_scale:
                bid_scale[i] = max_bid_scale
            self.ask_scale.append(ask_scale[i])
            self.bid_scale.append(bid_scale[i])



# class H_Parameters():
#     agent_num = 0           #高频交易者数量
#     t = 0                   #交易周期
#     true_delta = 0          #判断市场参与的市场价格变动
#     best_ask_price = 0      #当前市场中的最优卖价
#     best_bid_price = 0      #当前市场中的最优卖价
#     ask_scale = []          #卖单指令规模
#     bid_scale = []          #买单指令规模
#     lamb = 0.0625
#
#     def __init__(self,market,AskList,BidList):
#         self.agent_num = market.NH
#         self.t = market.t
#         self.true_delta = abs((market.P_list[-1] - market.P_list[-2]) / market.P_list[-2])
#         # 如果某一方没有订单怎么办？
#         self.best_ask_price = AskList.iloc[0].at['Price']
#         self.best_bid_price = BidList.iloc[0].at['Price']
#         print(self.best_ask_price,self.best_bid_price)
#         ask_num = len(AskList)
#         bid_num = len(BidList)
#         if ask_num != 0:
#             avg_ask_volumn = 10000 * self.lamb * AskList.Scale.sum() / ask_num
#         else:
#             avg_ask_volumn = 0.05
#         if bid_num != 0:
#             avg_bid_volumn = 10000 * self.lamb * BidList.Scale.sum() / bid_num
#         else:
#             avg_ask_volumn = 0.05
#         ask_scale = np.divide(np.random.poisson(avg_bid_volumn,self.agent_num) ,10000)
#         bid_scale = np.divide(np.random.poisson(avg_ask_volumn,self.agent_num) ,10000)
#         max_ask_scale = AskList.Scale.sum() / 4
#         max_bid_scale = BidList.Scale.sum() / 4
#
#         for i in range(self.agent_num):
#             if ask_scale[i] > max_ask_scale:
#                 ask_scale[i] = max_ask_scale
#             if bid_scale[i] > max_bid_scale:
#                 bid_scale[i] = max_bid_scale
#             self.ask_scale.append(ask_scale[i])
#             self.bid_scale.append(bid_scale[i])














