from Orders import Order
class Agent:
    traderID = 0        #交易者编号
    wealth = 0          #总财富
    c_0 = 10000         #【未定】交易者初始资金
    s_0 = 100           #【未定】交易者初始股票持有
    cash = 0            #现金持有量
    stock = 0           #股票持有量
    gamma = 0           #挂单时间
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






