import Agent
from Orders import Order
import numpy as np
import math

class NAgent(Agent.Agent):
    theta = 0           #交易周期
    strategy_type = ''  #策略类型
    zeta = 1            #策略转化参数
    alpha_c = 0.04      #图表交易者指令规模参数
    sigma_c = 0.05      #图表交易者指令规模震荡标准差
    alpha_f = 0.04      #基本面交易者指令规模参数
    sigma_f = 0.01      #基本面交易者指令规模震荡标准差
    sigma_z = 0.01      #订单价格震荡标准差
    delta = 0.0001      #订单价格漂移参数
    phi = 0.5           #下一轮交易采用图表策略的概率
    gamma = 5          #更新挂单时间
    order_flag = False  #交易者市场中是否有订单



    def __init__(self,T,i):
        #初始化编号
        self.traderID = 'low' + str(i)
        # 产生交易周期参数
        mean_theta = 2  # 交易周期均值
        min_theta = 1  # 最小交易周期
        max_theta = 4  # 最大交易周期
        while self.theta < min_theta or self.theta > max_theta :
            self.theta = int(np.random.exponential(mean_theta))
        # 产生两种策略指令规模震荡列表
        self.epsilion_c = np.random.normal(0, self.sigma_c, T)
        self.epsilion_f = np.random.normal(0, self.sigma_f, T)
        #计时因子：计算上一次提交订单距今的时间
        self.time = np.random.uniform(2*max_theta)
        self.get_strategy_type()

    #确定当前交易者策略类型
    def get_strategy_type(self):
        r = np.random.rand()
        if r<= self.phi:
            self.strategy_type = 'c'
        else:
            self.strategy_type = 'f'

    #生成订单
    def gen_order(self,market,para):
        #判断是否参与市场
        if not self.judge_participate():
            para.price = np.delete(para.price,0)
            return
        self.order_flag = True
        #order = Order()
        self.order.traderID = self.traderID
        #self.get_strategy_type()
        #确定订单价格
        #

        # print(para.price[0])
        self.order.price = para.price[0]
        #self.order.price = self.gen_order_price(market)
        self.order.time = market.t + np.random.randint(0,100)/100
        self.order.suspend_time = self.gamma
        #确定订单方向和指令规模
        size = self.gen_order_scale(market.P_list,market.F_list,market.t)
        if size > 0:
            self.order.direction = 1
        if size < 0:
            self.order.direction = 0
        size = int(abs(size))
        if size < 1:
            size = 1
        self.order.scale = size
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

    #确定指令规模
    def gen_order_scale(self,P_list,F_list,t):
        if self.strategy_type == 'c':
            size = self.alpha_c * (P_list[-1] - P_list[-2]) + self.epsilion_c[t]
        else:
            size = self.alpha_f * (F_list[-1] - P_list[-1]) + self.epsilion_f[t]
        size = round(size,4) * 100
        return size

    #确定订单价格:需要的参数是上一周期的市场价格
    def gen_order_price(self,market):
        z_i_t = np.random.normal(0,self.sigma_z)
        p_t = market.P_list[-1] * (1+self.delta) * (1+z_i_t)
        p_t = round(p_t,4)
        return p_t

    #计算下一周期交易者的策略选择概率
    def update_phi(self,market):
        di_c = self.alpha_c * (market.P_list[-2] - market.P_list[-3]) + self.epsilion_c[market.t]
        di_f = self.alpha_f * (market.F_list[-2] - market.P_list[-3]) + self.epsilion_f[market.t]
        z_i_t = np.random.normal(0, self.sigma_z)
        p_i_t = market.P_list[-2] * (1 + self.delta) * (1 + z_i_t)
        p_i_t = round(p_i_t, 2)
        pi_c = (market.P_list[-1] - p_i_t) * di_c
        pi_f = (market.P_list[-1] - p_i_t) * di_f
        self.phi = math.exp(pi_c/self.zeta) / (math.exp(pi_c/self.zeta) + math.exp(pi_f/self.zeta))
        self.get_strategy_type()

class N_Parameters():
    agent_num = 0           #普通程式化交易者数量
    t = 0                   #交易周期
    price = 0               #订单价格
    sigma_z = 0.01          #订单价格震荡标准差
    delta = 0.0001          #订单价格漂移参数
    price = []              #订单价格序列



    def __init__(self,market):
        self.agent_num = market.NL
        self.t = market.t

        #集中产生订单价格
        z_t = np.random.normal(0,self.sigma_z,self.agent_num)
        p_t = market.P_list[-1] * (1+self.delta) * (1+z_t)
        self.price = p_t.round(2)






