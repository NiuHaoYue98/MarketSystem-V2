import pandas as pd
from Market import Market
from HAgent import HAgent,H_Parameters
from NAgent import NAgent,N_Parameters
from Orders import Deal
import os
import sqlite3



# 订单排序
def sort_orders(AskList,BidList):
    AskList.sort_values(['Price','Time'],inplace=True)
    AskList.reset_index(drop=True,inplace=True)
    if len(BidList) != 0:
        BidList['TimeRank'] = BidList['Time'].groupby(BidList['Price']).rank(ascending=False)
    else:
        return AskList,BidList
    BidList.sort_values(['Price','TimeRank'],ascending=False,inplace=True)
    BidList.reset_index(drop=True,inplace=True)
    BidList.drop(['TimeRank'],axis=1,inplace=True)
    return AskList,BidList

# 【第一步】普通的程式化交易者提交订单
def gen_normal_orders(market,AskList,BidList):
    para = N_Parameters(market)
    for agent in normal_agents:
        order = agent.gen_order(market,para)
        if not order:
            continue
        if order.direction == 0:
            AskList = AskList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
        else:
            BidList = BidList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
    AskList,BidList = sort_orders(AskList,BidList)
    print("【Normal】The number of the Asklist and the Bidlist is ", len(AskList), len(BidList))
    return AskList,BidList

# 【第二步】高频交易者提交订单
def gen_high_orders(market,asklist,bidlist):
    AskList = pd.DataFrame(columns=['Price', 'Time', 'TraderId', 'Scale', 'SuspendTime'])
    BidList = pd.DataFrame(columns=['Price', 'Time', 'TraderId', 'Scale', 'SuspendTime'])

    #高频一些参数是所有交易者可以共用的，因此可以提前算好，然后作为一个参数包穿进去
    para = H_Parameters(market,asklist,bidlist)
    for agent in high_agents:
        order = agent.gen_order(para,asklist,bidlist)
        if not order:
            continue
        #print("There is a order from high trader!")
        if order.direction == 0:
            AskList = AskList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
        else:
            BidList = BidList.append([{'Price':order.price,'Time':order.time,'TraderId':order.traderID,'Scale':order.scale,'SuspendTime':order.suspend_time}])
    #高频的订单：后一个交易者看不到前一个交易者的订单
    print("【High】The number of the Asklist and the Bidlist is",len(AskList),len(BidList))
    asklist = asklist.append(AskList,ignore_index=True)
    bidlist = bidlist.append(BidList,ignore_index=True)
    AskList,BidList = sort_orders(asklist,bidlist)
    return AskList,BidList

# 【第四步】市场订单匹配
def gen_deals(AskList,BidList,old_price):
    deals = pd.DataFrame(columns=['AskId', 'BidId', 'Scale', 'Price', 'Time', 'AskTime', 'BidTime','AskPrice','BidPrice','AskScale','BidScale'])
    if AskList.shape[0] == 0 or BidList.shape[0] == 0:
        return deals,AskList,BidList
    trader_list = []
    bid_start = 0
    for ask_index in range(AskList.shape[0]):
        for bid_index in range(bid_start,BidList.shape[0]):
            if AskList.at[ask_index,'Price'] <= BidList.at[bid_index,'Price']:
                # 可以成交
                deal = Deal()
                #双方交易者
                deal.askID = AskList.at[ask_index, 'TraderId']
                deal.bidID = BidList.at[bid_index, 'TraderId']
                #成交时间
                deal.time = max(AskList.at[ask_index, 'Time'], BidList.at[bid_index, 'Time'])
                deal.asktime = AskList.at[ask_index, 'Time']
                deal.bidtime = BidList.at[bid_index, 'Time']
                #交易量
                ask_scale = AskList.at[ask_index,'Scale']
                bid_scale = BidList.at[bid_index,'Scale']
                deal.askscale = ask_scale
                deal.bidscale = bid_scale
                deal.scale = min(ask_scale,bid_scale)
                #成交价格
                deal.askprice = AskList.at[ask_index, 'Price']
                deal.bidprice = BidList.at[bid_index, 'Price']
                if AskList.at[ask_index, 'Time'] == deal.time:
                    deal.price = BidList.at[bid_index, 'Price']
                elif BidList.at[bid_index, 'Time'] == deal.time:
                    deal.price = AskList.at[ask_index, 'Price']
                else:
                    if ask_scale < bid_scale:
                        deal.price = AskList.at[ask_index, 'Price']
                    else:
                        deal.price = BidList.at[bid_index, 'Price']
                price = deal.price
                deals = deals.append([{'Time':deal.time,'AskId':deal.askID,'BidId':deal.bidID,'Price':deal.price,'Scale':deal.scale,'AskTime':deal.asktime,'BidTime':deal.bidtime,'AskPrice':deal.askprice,'BidPrice':deal.bidprice,'AskScale':deal.askscale,'BidScale':deal.bidscale}])
                #订单簿变更
                if ask_scale < bid_scale :
                    BidList.at[bid_index,'Scale'] = BidList.at[bid_index,'Scale'] - AskList.at[ask_index,'Scale']
                    trader_list.append(AskList.at[ask_index, 'TraderId'])
                    AskList.drop(ask_index,inplace = True)
                else:
                    AskList.at[ask_index,'Scale'] = AskList.at[ask_index,'Scale'] - BidList.at[bid_index,'Scale']
                    trader_list.append(BidList.at[bid_index, 'TraderId'])
                    BidList.drop(bid_index,inplace = True)
                    bid_start += 1
                    continue
                break
            else:
                break
    #deals['temp'] = deals['Price'] * deals['Scale']
    if deals.Scale.sum() == 0:
        market_price = old_price
    else:
        #market_price = deals.temp.sum() / deals.Scale.sum()    #表示市场价是round内价格的加权平均
        market_price = price                                    #表示市场价是round内最后成交的订单的价格
    deals.drop(['temp'],axis=1,inplace=True)
    #更新剩余市场订单信息
    AskList['SuspendTime'] = AskList['SuspendTime'] - 1
    BidList['SuspendTime'] = BidList['SuspendTime'] - 1
    trader_list = trader_list + list(AskList[AskList.SuspendTime < 1].TraderId) + list(BidList[BidList.SuspendTime < 1].TraderId)
    AskList = AskList[-AskList.TraderId.isin(trader_list)]
    BidList = BidList[-BidList.TraderId.isin(trader_list)]
    AskList.reset_index(inplace=True,drop=True)
    BidList.reset_index(inplace=True,drop=True)
    return deals,AskList,BidList,trader_list,market_price

# 【第五步】更新交易者状态
def updata_trader_stutus(trader_list,normal_agents,market):
    #更新订单状态标志、更新下一周期的策略选择
    for agent in normal_agents:
        if agent.traderID in trader_list:
            agent.order_flag = False
        agent.update_phi(market)

#创建新文件夹
def mkdir(path):
    folder = os.path.exists(path)

    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


if __name__ == '__main__':
    MC = 20             # 蒙特卡洛重复次数
    T = 500            # 交易周期:60*6=360,没必要设置T过大
    agent_flag = False  # 控制普通程式化交易者的信息输出，默认为Fasle
    list_flag = True   # 控制每轮交易的订单簿输出，默认为Flase
    high_flag = True    #控制市场中是否有高频交易者

    for r in range(0,MC):
        # 指令簿,用于订单匹配计算
        ask_num = 0
        bid_num = 0
        AskList = pd.DataFrame(columns=['Price', 'Time', 'TraderId', 'Scale', 'SuspendTime'])
        BidList = pd.DataFrame(columns=['Price', 'Time', 'TraderId', 'Scale', 'SuspendTime'])
        #deals = pd.DataFrame(columns=['AskId', 'BidId', 'Scale', 'Price', 'Time'])


        # 初始化市场 && 交易者
        market = Market(r)
        normal_agents = [NAgent(T,i) for i in range(market.NL)]
        if agent_flag:
            Idlist = []
            Thetalist = []
            Philist0 = []
            for agent in normal_agents:
                Idlist.append(agent.traderID)
                Thetalist.append(agent.theta)
                Philist0.append(agent.phi)
            LowAgent = pd.DataFrame({'Id':Idlist,'Theta':Thetalist,'Phi0':Philist0})
        high_agents = [HAgent(i) for i in range(market.NH)]

        #记录订单簿信息
        if list_flag:
            mkdir('./Data' + str(r) + '/AskList')
            mkdir('./Data' + str(r) + '/BidList')
        #市场开盘——集合一轮集合竞价
        print(market.t)
        market.gen_fundamental_price()
        AskList, BidList = gen_normal_orders(market, AskList, BidList)

        #记录程式化交易者的信息
        if agent_flag:
            column_name = 'S' + str(market.t)
            SType = []
            for agent in normal_agents:
                SType.append(agent.strategy_type)
            LowAgent[column_name] = SType

        deals, AskList, BidList, trader_list, market_price = market.call_auction(AskList, BidList)
        if list_flag:
            askfile = './Data' + str(r) + './AskList/AskList' + str(market.t) + '.csv'
            AskList.to_csv(askfile, index=False)
            bidfile = './Data' + str(r) + './BidList/BidList' + str(market.t) + '.csv'
            BidList.to_csv(bidfile, index=False)

        market.P_list.append(market_price)
        #deals = deals.append(temp_deals, ignore_index=True)
        print('There are ', len(deals), 'deals in this round! The market Price is ', market.P_list[-1])
        updata_trader_stutus(trader_list, normal_agents, market)

        mkdir('./Data' + str(r) + '/Deals')
        dealfile = './Data' + str(r) + './Deals/Deals' + str(market.t) + '.csv'
        deals.to_csv(dealfile, index=False)

        market.t += 1

        #连续竞价
        for i in range(1,T):
            print(i)
            market.gen_fundamental_price()
            print('Fundamental Price is ', market.F_list[-1])
            # 【第一步】普通的程式化交易者提交订单
            AskList,BidList = gen_normal_orders(market,AskList,BidList)
            if agent_flag:
                #记录程式化交易者的信息
                column_name = 'S' + str(market.t)
                column_name1 = 'Phi' + str(market.t)
                SType = []
                Phi = []
                for agent in normal_agents:
                    SType.append(agent.strategy_type)
                    Phi.append(agent.phi)
                LowAgent[column_name1] = Phi
                LowAgent[column_name] = SType

            # 【第二步】高频交易者提交订单、【第三步】高频交易者主动撤单判断（撤单订单就不会提交到最终的市场中）
            AskList,BidList = gen_high_orders(market,AskList,BidList)

            if list_flag:
                askfile = './Data' + str(r) + './AskList/AskList' + str(market.t) + '.csv'
                AskList.to_csv(askfile, index=False)
                bidfile = './Data' + str(r) + './BidList/BidList' + str(market.t) + '.csv'
                BidList.to_csv(bidfile, index=False)

            # 【第四步】市场订单匹配
            #deals,AskList,BidList,trader_list,market_price = gen_deals(AskList,BidList,market.P_list[-1])
            #【选择1】 市场订单匹配选择连续竞价
            deals, AskList, BidList, trader_list, market_price = market.continuous_auction(AskList, BidList,market.P_list[-1], market.t)
            #【选择2】 市场订单匹配也选择集合竞价
            # deals, AskList, BidList, trader_list, market_price = market.call_auction(AskList, BidList)
            market.P_list.append(market_price)
            #deals = deals.append(temp_deals,ignore_index=True)
            print('There are ',len(deals) ,'deals in this round! The market Price is ',market_price)

            # 【第五步】更新交易者的状态
            updata_trader_stutus(trader_list,normal_agents,market)
            dealfile = './Data' + str(r) + '/Deals/Deals' + str(market.t) + '.csv'
            deals.to_csv(dealfile, index=False)
            market.t += 1

        print(market.F_list)
        print(market.P_list)
        market_mes = pd.DataFrame({'MarketPrice':market.P_list,'FundamentalPrice':market.F_list})
        pricefile = './Data' + str(r) + '/MarketPrice.csv'
        market_mes.to_csv(pricefile, index=False)
        if agent_flag:
            agentfile = './Data' + str(r) + './AgentMes.csv'
            LowAgent.to_csv(agentfile, index=False)




