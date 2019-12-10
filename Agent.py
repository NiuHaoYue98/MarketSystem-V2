from Orders import Order
import numpy as np

class Agent:
    traderID = 0        #交易者编号
    theta = 0           #交易周期

    wealth = 0          #总财富
    c_0 = 10000         #【未定】交易者初始资金
    s_0 = 100           #【未定】交易者初始股票持有

    gamma = 5          #更新挂单时间
    order_flag = False  #交易者市场中是否有订单
    order = Order()     #订单

    #撤单订单更新
    def reset_order(self):
        self.order.traderID = 0     # 交易者编号
        self.order.direction = 0    # 订单方向 >0 1表示买单,0 表示卖单
        self.order.scale = 0        # 指令规模
        self.order.price = 0        # 指令价格
        self.order.time = 0         # 提交时间
        self.order.suspend_time = 0 # 剩余时间
        self.order.pi = 0           # 单笔订单的收益

    def __init__(self,i):
        #初始化编号
        self.traderID = 'noisy' + str(i)
        # 产生交易周期参数
        mean_theta = 2  # 交易周期均值
        min_theta = 1  # 最小交易周期
        max_theta = 4  # 最大交易周期
        while self.theta < min_theta or self.theta > max_theta :
            self.theta = int(np.random.exponential(mean_theta))
        #计时因子：计算上一次提交订单距今的时间
        self.time = np.random.uniform(2*max_theta)

    #生成订单
    def gen_order(self,market):
        #判断是否参与市场
        if not self.judge_participate():
            return
        self.order_flag = True
        self.order.traderID = self.traderID
        #确定订单价格
        self.order.price = round(np.random.normal(market.P_list[-1],1),2)
        self.order.time = market.t + np.random.randint(0,100)/100
        self.order.suspend_time = self.gamma
        #确定订单方向和指令规模
        size = int(np.random.normal(5,5))-5
        if size >= 0:
            self.order.direction = 1
        else:
            self.order.direction = 0
        if size < 1:
            size = 1
        self.order.scale = abs(size)
        return self.order

    #判断是否参与市场
    def judge_participate(self):
        if self.order_flag:
            self.time += 1
            return False
        else:
            if self.time > self.theta:
                self.time = 1
                return True
            else:
                self.time += 1
                return False








